"""Sync orchestration service — coordinates live connector runs.

ARCH:BackgroundSyncPosture
ARCH:ConnectorToIntakeHandoff
ARCH:ConnectorSyncStateTracking
ARCH:ConnectorPrinciple.ReadFirst

Single entry point for triggering a live sync on a connected account.
Resolves context, selects the correct connector, refreshes tokens if
needed, fetches/normalizes, persists via IntakeHandoffService, and
updates sync state.

Supports both on-demand manual sync and future scheduled sync.
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass
from typing import Optional

from sqlalchemy.orm import Session

from app.config import get_settings
from app.connectors.context import ConnectorContextResolver
from app.connectors.contracts import (
    ConnectorExecutionContext,
    FetchResult,
    SyncCheckpoint,
)
from app.connectors.intake import IntakeHandoffService, ConnectorDispatchResult
from app.connectors.sync import SyncStateManager
from app.connectors.token_manager import TokenManager
from app.models.source import ConnectedAccount

logger = logging.getLogger(__name__)


# ── Result ───────────────────────────────────────────────────────────


@dataclass
class SyncResult:
    """Result of a sync operation on a single connected account."""

    account_id: uuid.UUID
    provider_type: str
    connector_type: str
    success: bool = False
    items_fetched: int = 0
    dispatch_result: Optional[ConnectorDispatchResult] = None
    error: Optional[str] = None
    duration_ms: float = 0.0


# ── Connector Registry ───────────────────────────────────────────────


def _get_connector_for_account(account: ConnectedAccount):
    """Select the correct connector(s) based on provider_type.

    Returns a list of (connector_instance, connector_type) tuples.
    A single account may need multiple connectors (e.g., Google → gmail + calendar).
    """
    connectors = []

    if account.provider_type == "google":
        from app.connectors.google.gmail import GmailConnector
        from app.connectors.google.calendar import GoogleCalendarConnector
        connectors.append(GmailConnector())
        connectors.append(GoogleCalendarConnector())

    elif account.provider_type in ("microsoft", "microsoft_365"):
        from app.connectors.microsoft.mail import MicrosoftMailConnector
        from app.connectors.microsoft.calendar import MicrosoftCalendarConnector
        connectors.append(MicrosoftMailConnector())
        connectors.append(MicrosoftCalendarConnector())

    return connectors


# ── Sync Orchestration ───────────────────────────────────────────────


def sync_account(
    session: Session,
    account_id: uuid.UUID,
) -> list[SyncResult]:
    """Run a full sync on a connected account.

    ARCH:BackgroundSyncPosture
    ARCH:ConnectorToIntakeHandoff

    Steps:
    1. Resolve account context
    2. Refresh tokens if expired
    3. For each relevant connector type:
       a. Build FetchResult via fetch_and_normalize()
       b. Persist via IntakeHandoffService
       c. Dispatch to intake graph for triage
       d. Update sync state
    4. Return results

    Args:
        session: SQLAlchemy session.
        account_id: The connected account to sync.

    Returns:
        List of SyncResult, one per connector type synced.
    """
    settings = get_settings()
    token_manager = TokenManager(session, settings.token_encryption_key)
    context_resolver = ConnectorContextResolver(session)
    sync_manager = SyncStateManager(session)
    intake_service = IntakeHandoffService(session)

    results: list[SyncResult] = []

    # Load account
    account = session.get(ConnectedAccount, account_id)
    if account is None:
        return [SyncResult(
            account_id=account_id,
            provider_type="unknown",
            connector_type="unknown",
            error=f"Account {account_id} not found",
        )]

    if account.status != "active":
        return [SyncResult(
            account_id=account_id,
            provider_type=account.provider_type,
            connector_type="unknown",
            error=f"Account is not active (status={account.status})",
        )]

    # Refresh tokens if needed
    try:
        _ensure_fresh_tokens(session, account, token_manager, settings)
    except Exception as exc:
        error_msg = f"Token refresh failed: {exc}"
        logger.error("sync_account: %s for account %s", error_msg, account_id)
        sync_manager.record_failure(account_id, error_msg)
        session.commit()
        return [SyncResult(
            account_id=account_id,
            provider_type=account.provider_type,
            connector_type="all",
            error=error_msg,
        )]

    # Get connectors for this account type
    connectors = _get_connector_for_account(account)
    if not connectors:
        return [SyncResult(
            account_id=account_id,
            provider_type=account.provider_type,
            connector_type="unknown",
            error=f"No connectors registered for provider {account.provider_type}",
        )]

    # Resolve execution context
    try:
        context = context_resolver.resolve(account_id)
    except Exception as exc:
        error_msg = f"Context resolution failed: {exc}"
        logger.error("sync_account: %s", error_msg)
        sync_manager.record_failure(account_id, error_msg)
        session.commit()
        return [SyncResult(
            account_id=account_id,
            provider_type=account.provider_type,
            connector_type="all",
            error=error_msg,
        )]

    # Inject decrypted tokens into context sync_metadata for connector use
    tokens = token_manager.get_tokens(account_id)
    if tokens:
        context.sync_metadata = {
            **(context.sync_metadata or {}),
            "_access_token": tokens.get("access_token"),
            "_refresh_token": tokens.get("refresh_token"),
        }

    # Run each connector
    for connector in connectors:
        result = _run_single_connector(
            session=session,
            connector=connector,
            context=context,
            account_id=account_id,
            intake_service=intake_service,
            sync_manager=sync_manager,
        )
        results.append(result)

    session.commit()
    return results


def _ensure_fresh_tokens(
    session: Session,
    account: ConnectedAccount,
    token_manager: TokenManager,
    settings,
) -> None:
    """Refresh access token if it has expired.

    ARCH:TokenRevocationHandling
    """
    if not token_manager.is_expired(account.id):
        return

    tokens = token_manager.get_tokens(account.id)
    if not tokens or not tokens.get("refresh_token"):
        raise ValueError("No refresh token available — reauthorization required")

    logger.info("Refreshing expired token for account %s", account.id)

    if account.provider_type == "google":
        from app.connectors.oauth_providers import GoogleOAuthProvider
        provider = GoogleOAuthProvider(settings)
        new_tokens = provider.refresh_access_token(tokens["refresh_token"])
    elif account.provider_type in ("microsoft", "microsoft_365"):
        from app.connectors.oauth_providers import MicrosoftOAuthProvider
        provider = MicrosoftOAuthProvider(settings)
        new_tokens = provider.refresh_access_token(tokens["refresh_token"])
    else:
        raise ValueError(f"Unknown provider type for refresh: {account.provider_type}")

    token_manager.store_tokens(account.id, new_tokens)
    session.flush()


def _run_single_connector(
    *,
    session: Session,
    connector,
    context: ConnectorExecutionContext,
    account_id: uuid.UUID,
    intake_service: IntakeHandoffService,
    sync_manager: SyncStateManager,
) -> SyncResult:
    """Run a single connector fetch, persist, dispatch, and sync-state update."""
    start = time.monotonic()
    result = SyncResult(
        account_id=account_id,
        provider_type=connector.provider_type,
        connector_type=connector.connector_type,
    )

    try:
        # Fetch and normalize
        fetch_result: FetchResult = connector.fetch_and_normalize(context)

        total_items = (
            len(fetch_result.messages)
            + len(fetch_result.threads)
            + len(fetch_result.events)
            + len(fetch_result.signals)
        )
        result.items_fetched = total_items

        if total_items > 0:
            # Persist and dispatch through intake graph
            dispatch_result = intake_service.persist_and_dispatch(context, fetch_result)
            result.dispatch_result = dispatch_result

        # Update sync state
        checkpoint = SyncCheckpoint(
            connected_account_id=account_id,
            status="success",
            items_fetched=total_items,
            sync_cursor=fetch_result.checkpoint.sync_cursor if fetch_result.checkpoint else None,
        )
        sync_manager.apply_checkpoint(checkpoint)

        result.success = True
        logger.info(
            "sync: %s/%s fetched %d items for account %s",
            connector.provider_type,
            connector.connector_type,
            total_items,
            account_id,
        )

    except NotImplementedError:
        # Connector not yet wired for live fetch — not a failure
        result.error = f"{connector.connector_type} live fetch not yet implemented"
        logger.info("sync: %s", result.error)
        result.success = True  # Not a failure, just not implemented

    except Exception as exc:
        result.error = str(exc)
        logger.exception(
            "sync: %s/%s failed for account %s: %s",
            connector.provider_type,
            connector.connector_type,
            account_id,
            exc,
        )
        sync_manager.record_failure(account_id, f"{connector.connector_type}: {exc}")

    result.duration_ms = (time.monotonic() - start) * 1000
    return result



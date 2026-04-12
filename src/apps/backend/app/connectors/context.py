"""Connector execution context resolution.

ARCH:ConnectedAccountModel
ARCH:AccountProfileConnectorSupport
ARCH:AccountProvenanceModel
ARCH:ConnectorPrinciple.MultiAccountFirstClass

This module resolves the correct ConnectedAccount and optional AccountProfile
into a ConnectorExecutionContext for a connector run. This is where
multi-account support becomes operational, not just modeled.
"""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.connectors.contracts import ConnectorExecutionContext
from app.models.source import ConnectedAccount, AccountProfile


class AccountNotFoundError(Exception):
    """Raised when a connected account cannot be found."""

    def __init__(self, account_id: uuid.UUID) -> None:
        self.account_id = account_id
        super().__init__(f"Connected account not found: {account_id}")


class AccountInactiveError(Exception):
    """Raised when a connected account exists but is not active."""

    def __init__(self, account_id: uuid.UUID, status: str) -> None:
        self.account_id = account_id
        self.status = status
        super().__init__(
            f"Connected account {account_id} is not active (status={status})"
        )


class ProfileNotFoundError(Exception):
    """Raised when a requested account profile cannot be found."""

    def __init__(self, profile_id: uuid.UUID, account_id: uuid.UUID) -> None:
        self.profile_id = profile_id
        self.account_id = account_id
        super().__init__(
            f"Account profile {profile_id} not found under account {account_id}"
        )


class ConnectorContextResolver:
    """Resolves ConnectedAccount + optional AccountProfile into execution context.

    This is the gateway between the domain model and the connector runtime.
    It enforces that connector execution always starts from a real, active
    account record and that profile context is resolved explicitly.

    ARCH:ConnectorPrinciple.MultiAccountFirstClass
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def resolve(
        self,
        account_id: uuid.UUID,
        profile_id: Optional[uuid.UUID] = None,
    ) -> ConnectorExecutionContext:
        """Resolve execution context from account ID and optional profile ID.

        Args:
            account_id: The connected account to resolve.
            profile_id: Optional specific profile under the account.

        Returns:
            A fully resolved ConnectorExecutionContext.

        Raises:
            AccountNotFoundError: Account does not exist.
            AccountInactiveError: Account exists but is not active.
            ProfileNotFoundError: Profile not found under the given account.
        """
        account = self._session.get(ConnectedAccount, account_id)
        if account is None:
            raise AccountNotFoundError(account_id)

        if account.status != "active":
            raise AccountInactiveError(account_id, account.status)

        # Build base context from account
        context = ConnectorExecutionContext(
            connected_account_id=account.id,
            provider_type=account.provider_type,
            account_label=account.account_label,
            account_address=account.account_address,
            tenant_context=account.tenant_context,
            sync_metadata=account.sync_metadata,
        )

        # Resolve profile if requested
        if profile_id is not None:
            profile = self._session.get(AccountProfile, profile_id)
            if profile is None or profile.account_id != account.id:
                raise ProfileNotFoundError(profile_id, account_id)
            context.profile_id = profile.id
            context.profile_type = profile.profile_type
            context.profile_label = profile.profile_label

        return context

    def resolve_all_profiles(
        self, account_id: uuid.UUID
    ) -> list[ConnectorExecutionContext]:
        """Resolve execution contexts for ALL profiles under an account.

        Useful when a connector needs to iterate over all profiles
        (e.g., all calendars under a Google account).

        Returns:
            List of ConnectorExecutionContext, one per profile.
            Empty list if the account has no profiles.
        """
        # First resolve the base account (validates existence and status)
        base_context = self.resolve(account_id)

        profiles = (
            self._session.execute(
                select(AccountProfile).where(
                    AccountProfile.account_id == account_id
                )
            )
            .scalars()
            .all()
        )

        if not profiles:
            return [base_context]

        contexts = []
        for profile in profiles:
            ctx = ConnectorExecutionContext(
                connected_account_id=base_context.connected_account_id,
                provider_type=base_context.provider_type,
                account_label=base_context.account_label,
                account_address=base_context.account_address,
                tenant_context=base_context.tenant_context,
                sync_metadata=base_context.sync_metadata,
                profile_id=profile.id,
                profile_type=profile.profile_type,
                profile_label=profile.profile_label,
            )
            contexts.append(ctx)

        return contexts

    def list_active_accounts(
        self,
        provider_type: Optional[str] = None,
    ) -> list[ConnectedAccount]:
        """List all active connected accounts, optionally filtered by provider.

        Args:
            provider_type: Optional filter (e.g. 'google', 'microsoft_365').

        Returns:
            List of active ConnectedAccount records.
        """
        stmt = select(ConnectedAccount).where(
            ConnectedAccount.status == "active"
        )
        if provider_type is not None:
            stmt = stmt.where(ConnectedAccount.provider_type == provider_type)
        return list(self._session.execute(stmt).scalars().all())


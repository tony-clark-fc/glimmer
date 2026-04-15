"""Connector management API routes — OAuth flows, account management, sync.

ARCH:ConnectorIsolation
ARCH:OAuthAndTokenStorage
ARCH:ConnectedAccountConsentModel
ARCH:MultiAccountTokenIsolation
ARCH:SecretExposurePrevention
ARCH:ConnectorPrinciple.ReadFirst

Thin API surface for connector lifecycle management:
- Connected account CRUD
- Google and Microsoft OAuth flows
- Manual sync triggers
- Sync status visibility

Token data is NEVER exposed in API responses.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings, Settings
from app.db import get_db
from app.models.source import ConnectedAccount

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/connectors", tags=["connectors"])


# ── Pydantic Contracts ───────────────────────────────────────────────


class ConnectedAccountResponse(BaseModel):
    """Response model for a connected account — never exposes tokens."""
    model_config = {"from_attributes": True}

    id: uuid.UUID
    provider_type: str
    account_label: str
    account_address: Optional[str] = None
    tenant_context: Optional[str] = None
    purpose_label: Optional[str] = None
    status: str
    created_at: datetime
    # Sync status (from sync_metadata, safe to expose)
    last_sync_at: Optional[str] = None
    last_sync_status: Optional[str] = None
    last_sync_items: Optional[int] = None
    last_error: Optional[str] = None
    has_credentials: bool = False

    @classmethod
    def from_account(cls, account: ConnectedAccount) -> "ConnectedAccountResponse":
        sync = account.sync_metadata or {}
        auth = account.auth_metadata or {}
        return cls(
            id=account.id,
            provider_type=account.provider_type,
            account_label=account.account_label,
            account_address=account.account_address,
            tenant_context=account.tenant_context,
            purpose_label=account.purpose_label,
            status=account.status,
            created_at=account.created_at,
            last_sync_at=sync.get("last_sync_at"),
            last_sync_status=sync.get("last_sync_status"),
            last_sync_items=sync.get("last_sync_items_fetched"),
            last_error=sync.get("last_error_summary"),
            has_credentials=bool(auth.get("encrypted_tokens")),
        )


class ConnectedAccountCreate(BaseModel):
    """Request body for manually creating a connected account."""
    provider_type: str = Field(..., description="google or microsoft")
    account_label: str = Field(..., min_length=1, max_length=255)
    account_address: Optional[str] = None
    tenant_context: Optional[str] = None
    purpose_label: Optional[str] = None


class AuthUrlResponse(BaseModel):
    """Response containing an OAuth authorization URL."""
    auth_url: str
    state: str
    provider: str


class SyncTriggerResponse(BaseModel):
    """Response from a manual sync trigger."""
    account_id: uuid.UUID
    results: list[dict] = []
    overall_success: bool = False


class ConnectorStatusResponse(BaseModel):
    """Overall connector status summary."""
    google_configured: bool = False
    microsoft_configured: bool = False
    accounts: list[ConnectedAccountResponse] = []
    total_accounts: int = 0
    active_accounts: int = 0


# ── In-memory OAuth state store (simple for MVP) ────────────────────
# In production, use signed JWTs or a short-lived DB table.
_oauth_states: dict[str, dict] = {}


# ── Account Management ───────────────────────────────────────────────


@router.get("/accounts", response_model=list[ConnectedAccountResponse])
def list_accounts(db: Session = Depends(get_db)) -> list[ConnectedAccountResponse]:
    """List all connected accounts.

    ARCH:ConnectedAccountConsentModel
    ARCH:SecretExposurePrevention — no token data in response.
    """
    accounts = db.execute(
        select(ConnectedAccount).order_by(ConnectedAccount.created_at.desc())
    ).scalars().all()
    return [ConnectedAccountResponse.from_account(a) for a in accounts]


@router.post("/accounts", response_model=ConnectedAccountResponse, status_code=201)
def create_account(
    body: ConnectedAccountCreate,
    db: Session = Depends(get_db),
) -> ConnectedAccountResponse:
    """Manually create a connected account record.

    ARCH:ConnectedAccountConsentModel
    """
    if body.provider_type not in ("google", "microsoft", "microsoft_365"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported provider type: {body.provider_type}",
        )

    account = ConnectedAccount(
        provider_type=body.provider_type,
        account_label=body.account_label,
        account_address=body.account_address,
        tenant_context=body.tenant_context,
        purpose_label=body.purpose_label,
        status="pending",  # Not active until OAuth completes
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return ConnectedAccountResponse.from_account(account)


@router.delete("/accounts/{account_id}", status_code=204)
def delete_account(
    account_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> None:
    """Disconnect and deactivate a connected account.

    ARCH:TokenRevocationHandling
    Clears stored tokens and marks the account as revoked.
    """
    account = db.get(ConnectedAccount, account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    # Clear tokens
    from app.connectors.token_manager import TokenManager
    settings = get_settings()
    token_mgr = TokenManager(db, settings.token_encryption_key)
    token_mgr.clear_tokens(account_id)

    account.status = "revoked"
    db.commit()


# ── Google OAuth ─────────────────────────────────────────────────────


@router.get("/google/auth-url", response_model=AuthUrlResponse)
def get_google_auth_url(
    settings: Settings = Depends(get_settings),
) -> AuthUrlResponse:
    """Generate a Google OAuth authorization URL.

    ARCH:OAuthAndTokenStorage
    ARCH:GoogleScopeMinimization
    """
    if not settings.google_oauth_configured:
        raise HTTPException(
            status_code=503,
            detail="Google OAuth not configured. Set GLIMMER_GOOGLE_OAUTH_CLIENT_ID and GLIMMER_GOOGLE_OAUTH_CLIENT_SECRET.",
        )

    from app.connectors.oauth_providers import GoogleOAuthProvider

    provider = GoogleOAuthProvider(settings)
    state = str(uuid.uuid4())
    auth_url, returned_state = provider.get_authorization_url(state)

    _oauth_states[returned_state] = {
        "provider": "google",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    return AuthUrlResponse(
        auth_url=auth_url,
        state=returned_state,
        provider="google",
    )


@router.get("/google/callback")
def google_oauth_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """Handle Google OAuth callback — exchange code for tokens.

    ARCH:OAuthAndTokenStorage
    ARCH:ConnectedAccountConsentModel
    ARCH:SecretExposurePrevention
    """
    # Validate state
    stored = _oauth_states.pop(state, None)
    if stored is None or stored.get("provider") != "google":
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    from app.connectors.oauth_providers import GoogleOAuthProvider
    from app.connectors.token_manager import TokenManager

    provider = GoogleOAuthProvider(settings)

    try:
        tokens = provider.exchange_code(code, state=state)
    except Exception as exc:
        logger.error("Google OAuth token exchange failed: %s", exc)
        raise HTTPException(status_code=400, detail=f"Token exchange failed: {exc}")

    # Get user info to identify the account
    try:
        user_info = provider.get_user_info(tokens["access_token"])
    except Exception as exc:
        logger.error("Google user info fetch failed: %s", exc)
        user_info = {"email": "unknown@google.com"}

    email = user_info.get("email", "unknown@google.com")

    # Check if account already exists
    existing = db.execute(
        select(ConnectedAccount).where(
            ConnectedAccount.provider_type == "google",
            ConnectedAccount.account_address == email,
        )
    ).scalars().first()

    if existing:
        account = existing
        account.status = "active"
    else:
        account = ConnectedAccount(
            provider_type="google",
            account_label=f"Google – {email}",
            account_address=email,
            status="active",
        )
        db.add(account)
        db.flush()

    # Store encrypted tokens
    token_mgr = TokenManager(db, settings.token_encryption_key)
    token_mgr.store_tokens(account.id, tokens)

    db.commit()

    # Redirect to frontend settings page
    frontend_url = settings.cors_origin_list[0] if settings.cors_origin_list else "http://localhost:3000"
    return RedirectResponse(
        url=f"{frontend_url}/settings/connectors?connected=google&account={email}",
        status_code=302,
    )


# ── Microsoft OAuth ──────────────────────────────────────────────────


@router.get("/microsoft/auth-url", response_model=AuthUrlResponse)
def get_microsoft_auth_url(
    settings: Settings = Depends(get_settings),
) -> AuthUrlResponse:
    """Generate a Microsoft OAuth authorization URL.

    ARCH:OAuthAndTokenStorage
    ARCH:MicrosoftScopeMinimization
    """
    if not settings.microsoft_oauth_configured:
        raise HTTPException(
            status_code=503,
            detail="Microsoft OAuth not configured. Set GLIMMER_MICROSOFT_OAUTH_CLIENT_ID and GLIMMER_MICROSOFT_OAUTH_CLIENT_SECRET.",
        )

    from app.connectors.oauth_providers import MicrosoftOAuthProvider

    provider = MicrosoftOAuthProvider(settings)
    state = str(uuid.uuid4())
    auth_url, returned_state = provider.get_authorization_url(state)

    _oauth_states[returned_state] = {
        "provider": "microsoft",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    return AuthUrlResponse(
        auth_url=auth_url,
        state=returned_state,
        provider="microsoft",
    )


@router.get("/microsoft/callback")
def microsoft_oauth_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """Handle Microsoft OAuth callback — exchange code for tokens.

    ARCH:OAuthAndTokenStorage
    ARCH:ConnectedAccountConsentModel
    ARCH:MicrosoftTenantMailboxContext
    """
    stored = _oauth_states.pop(state, None)
    if stored is None or stored.get("provider") != "microsoft":
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    from app.connectors.oauth_providers import MicrosoftOAuthProvider
    from app.connectors.token_manager import TokenManager

    provider = MicrosoftOAuthProvider(settings)

    try:
        tokens = provider.exchange_code(code, state=state)
    except Exception as exc:
        logger.error("Microsoft OAuth token exchange failed: %s", exc)
        raise HTTPException(status_code=400, detail=f"Token exchange failed: {exc}")

    # Get user info
    try:
        user_info = provider.get_user_info(tokens["access_token"])
    except Exception as exc:
        logger.error("Microsoft user info fetch failed: %s", exc)
        user_info = {"email": "unknown@microsoft.com"}

    email = user_info.get("email", "unknown@microsoft.com")
    display_name = user_info.get("display_name", email)
    tenant_id = user_info.get("tenant_id")

    # Check if account already exists
    existing = db.execute(
        select(ConnectedAccount).where(
            ConnectedAccount.provider_type.in_(["microsoft", "microsoft_365"]),
            ConnectedAccount.account_address == email,
        )
    ).scalars().first()

    if existing:
        account = existing
        account.status = "active"
        if tenant_id:
            account.tenant_context = tenant_id
    else:
        account = ConnectedAccount(
            provider_type="microsoft",
            account_label=f"Microsoft – {display_name}",
            account_address=email,
            tenant_context=tenant_id,
            status="active",
        )
        db.add(account)
        db.flush()

    # Store encrypted tokens
    token_mgr = TokenManager(db, settings.token_encryption_key)
    token_mgr.store_tokens(account.id, tokens)

    db.commit()

    frontend_url = settings.cors_origin_list[0] if settings.cors_origin_list else "http://localhost:3000"
    return RedirectResponse(
        url=f"{frontend_url}/settings/connectors?connected=microsoft&account={email}",
        status_code=302,
    )


# ── Sync ─────────────────────────────────────────────────────────────


@router.post("/sync/{account_id}", response_model=SyncTriggerResponse)
def trigger_sync(
    account_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> SyncTriggerResponse:
    """Manually trigger a sync for a connected account.

    ARCH:BackgroundSyncPosture
    ARCH:ConnectorPrinciple.ReadFirst
    """
    from app.services.sync_orchestration import sync_account

    results = sync_account(db, account_id)

    return SyncTriggerResponse(
        account_id=account_id,
        results=[
            {
                "connector_type": r.connector_type,
                "success": r.success,
                "items_fetched": r.items_fetched,
                "error": r.error,
                "duration_ms": round(r.duration_ms, 1),
            }
            for r in results
        ],
        overall_success=all(r.success for r in results),
    )


# ── Status ───────────────────────────────────────────────────────────


@router.get("/status", response_model=ConnectorStatusResponse)
def get_connector_status(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> ConnectorStatusResponse:
    """Get overall connector status.

    Returns configuration state and account summaries.
    """
    accounts = db.execute(
        select(ConnectedAccount).order_by(ConnectedAccount.created_at.desc())
    ).scalars().all()

    account_responses = [ConnectedAccountResponse.from_account(a) for a in accounts]
    active_count = sum(1 for a in accounts if a.status == "active")

    return ConnectorStatusResponse(
        google_configured=settings.google_oauth_configured,
        microsoft_configured=settings.microsoft_oauth_configured,
        accounts=account_responses,
        total_accounts=len(accounts),
        active_accounts=active_count,
    )





"""OAuth provider helpers for Google and Microsoft.

ARCH:OAuthAndTokenStorage
ARCH:ConnectedAccountConsentModel
ARCH:GoogleScopeMinimization
ARCH:MicrosoftScopeMinimization
ARCH:LeastPrivilegeModel

Stateless provider helpers that generate OAuth authorization URLs and
exchange authorization codes for tokens. These are used by the connector
API routes and stay within the connector layer boundary.
"""

from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any

from app.config import Settings

logger = logging.getLogger(__name__)

# In-memory storage for MSAL auth code flows (state → flow dict).
# Short-lived; cleaned up on exchange_code call.
_ms_auth_flows: dict[str, dict] = {}

# In-memory storage for Google OAuth flows (state → Flow object).
# Required to preserve the PKCE code_verifier across the redirect.
_google_auth_flows: dict[str, Any] = {}


# ── Google OAuth Provider ────────────────────────────────────────────


class GoogleOAuthProvider:
    """Google OAuth 2.0 provider for Gmail and Calendar access.

    ARCH:GoogleScopeMinimization — requests only read-only scopes.
    ARCH:ConnectorPrinciple.ReadFirst
    """

    def __init__(self, settings: Settings) -> None:
        self._client_id = settings.google_oauth_client_id
        self._client_secret = settings.google_oauth_client_secret
        self._redirect_uri = settings.google_oauth_redirect_uri
        self._scopes = settings.google_oauth_scope_list

    def _make_flow(self):
        """Create a new google_auth_oauthlib Flow."""
        from google_auth_oauthlib.flow import Flow

        flow = Flow.from_client_config(
            client_config={
                "web": {
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self._redirect_uri],
                }
            },
            scopes=self._scopes,
        )
        flow.redirect_uri = self._redirect_uri
        return flow

    def get_authorization_url(self, state: str | None = None) -> tuple[str, str]:
        """Generate Google OAuth consent URL.

        Args:
            state: Optional CSRF state. If None, a random one is generated.

        Returns:
            Tuple of (authorization_url, state).
        """
        if state is None:
            state = str(uuid.uuid4())

        flow = self._make_flow()

        authorization_url, returned_state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
            state=state,
        )

        # Store the flow so exchange_code can reuse it (preserves PKCE code_verifier)
        _google_auth_flows[returned_state] = flow

        return authorization_url, returned_state

    def exchange_code(self, code: str, state: str | None = None) -> dict[str, Any]:
        """Exchange an authorization code for OAuth tokens.

        Args:
            code: The authorization code from the callback.
            state: The state from the callback (used to retrieve the stored Flow with PKCE verifier).

        Returns:
            Token dict with access_token, refresh_token, expires_at_iso, scopes.
        """
        # Retrieve the stored flow (has the PKCE code_verifier)
        flow = _google_auth_flows.pop(state, None) if state else None

        if flow is None:
            # Fallback: create a new flow (will fail if Google requires PKCE)
            flow = self._make_flow()

        flow.fetch_token(code=code)
        credentials = flow.credentials

        expires_at = None
        if credentials.expiry:
            expires_at = credentials.expiry.replace(tzinfo=timezone.utc).isoformat()

        return {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_type": "Bearer",
            "expires_at_iso": expires_at,
            "scopes": list(credentials.scopes) if credentials.scopes else self._scopes,
            "id_token": getattr(credentials, "id_token", None),
        }

    def refresh_access_token(self, refresh_token: str) -> dict[str, Any]:
        """Refresh an access token using a refresh token.

        Args:
            refresh_token: The OAuth refresh token.

        Returns:
            Updated token dict.
        """
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials

        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self._client_id,
            client_secret=self._client_secret,
            scopes=self._scopes,
        )
        credentials.refresh(Request())

        expires_at = None
        if credentials.expiry:
            expires_at = credentials.expiry.replace(tzinfo=timezone.utc).isoformat()

        return {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token or refresh_token,
            "token_type": "Bearer",
            "expires_at_iso": expires_at,
            "scopes": list(credentials.scopes) if credentials.scopes else self._scopes,
        }

    def get_user_info(self, access_token: str) -> dict[str, Any]:
        """Fetch the authenticated user's email address.

        Used after OAuth exchange to identify which account was connected.
        """
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials

        credentials = Credentials(token=access_token)
        service = build("gmail", "v1", credentials=credentials)
        profile = service.users().getProfile(userId="me").execute()

        return {
            "email": profile.get("emailAddress"),
            "messages_total": profile.get("messagesTotal"),
            "threads_total": profile.get("threadsTotal"),
        }


# ── Microsoft OAuth Provider ─────────────────────────────────────────


class MicrosoftOAuthProvider:
    """Microsoft OAuth 2.0 provider for Graph API (Mail + Calendar).

    ARCH:MicrosoftScopeMinimization — requests only read-only scopes.
    ARCH:ConnectorPrinciple.ReadFirst
    """

    AUTHORITY_BASE = "https://login.microsoftonline.com"

    def __init__(self, settings: Settings) -> None:
        self._client_id = settings.microsoft_oauth_client_id
        self._client_secret = settings.microsoft_oauth_client_secret
        self._redirect_uri = settings.microsoft_oauth_redirect_uri
        self._tenant_id = settings.microsoft_oauth_tenant_id
        self._scopes = settings.microsoft_oauth_scope_list
        self._authority = f"{self.AUTHORITY_BASE}/{self._tenant_id}"

    def _get_msal_app(self):
        """Create an MSAL ConfidentialClientApplication."""
        import msal

        return msal.ConfidentialClientApplication(
            client_id=self._client_id,
            client_credential=self._client_secret,
            authority=self._authority,
        )

    def get_authorization_url(self, state: str | None = None) -> tuple[str, str]:
        """Generate Microsoft OAuth consent URL.

        Args:
            state: Optional CSRF state. If None, a random one is generated.

        Returns:
            Tuple of (authorization_url, state).
        """
        if state is None:
            state = str(uuid.uuid4())

        app = self._get_msal_app()
        flow = app.initiate_auth_code_flow(
            scopes=self._scopes,
            redirect_uri=self._redirect_uri,
            state=state,
        )

        # Store the flow dict for later use in exchange_code
        _ms_auth_flows[state] = flow

        auth_url = flow.get("auth_uri", "")
        return auth_url, state

    def exchange_code(self, code: str, state: str | None = None) -> dict[str, Any]:
        """Exchange an authorization code for OAuth tokens.

        Args:
            code: The authorization code from the callback.
            state: The state parameter from the callback (needed to retrieve the flow).

        Returns:
            Token dict with access_token, refresh_token, expires_at_iso, scopes.
        """
        app = self._get_msal_app()

        # Try to find the stored flow for this state
        flow = _ms_auth_flows.pop(state, None) if state else None

        if flow:
            # Use the newer auth code flow API
            result = app.acquire_token_by_auth_code_flow(
                auth_code_flow=flow,
                auth_response={"code": code, "state": state},
            )
        else:
            # Fallback: direct token request via requests
            import requests as req

            token_url = f"{self._authority}/oauth2/v2.0/token"
            data = {
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "code": code,
                "redirect_uri": self._redirect_uri,
                "grant_type": "authorization_code",
                "scope": " ".join(self._scopes),
            }
            resp = req.post(token_url, data=data)
            result = resp.json()

        if "error" in result:
            error_desc = result.get("error_description", result.get("error"))
            raise ValueError(f"Microsoft token exchange failed: {error_desc}")

        expires_in = result.get("expires_in", 3600)
        expires_at = datetime.fromtimestamp(
            time.time() + expires_in, tz=timezone.utc
        ).isoformat()

        return {
            "access_token": result.get("access_token"),
            "refresh_token": result.get("refresh_token"),
            "token_type": result.get("token_type", "Bearer"),
            "expires_at_iso": expires_at,
            "scopes": result.get("scope", "").split() if isinstance(result.get("scope"), str) else self._scopes,
            "id_token": result.get("id_token"),
            "id_token_claims": result.get("id_token_claims"),
        }

    def refresh_access_token(self, refresh_token: str) -> dict[str, Any]:
        """Refresh an access token using a refresh token.

        Args:
            refresh_token: The OAuth refresh token.

        Returns:
            Updated token dict.
        """
        app = self._get_msal_app()
        # MSAL doesn't have a direct refresh-by-token method without accounts.
        # Use the acquire_token_by_refresh_token (private) or build a manual request.
        # For robustness, use requests directly.
        import requests

        token_url = f"{self._authority}/oauth2/v2.0/token"
        data = {
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
            "scope": " ".join(self._scopes),
        }
        resp = requests.post(token_url, data=data)
        result = resp.json()

        if "error" in result:
            error_desc = result.get("error_description", result.get("error"))
            raise ValueError(f"Microsoft token refresh failed: {error_desc}")

        expires_in = result.get("expires_in", 3600)
        expires_at = datetime.fromtimestamp(
            time.time() + expires_in, tz=timezone.utc
        ).isoformat()

        return {
            "access_token": result.get("access_token"),
            "refresh_token": result.get("refresh_token", refresh_token),
            "token_type": result.get("token_type", "Bearer"),
            "expires_at_iso": expires_at,
            "scopes": result.get("scope", "").split() if isinstance(result.get("scope"), str) else self._scopes,
        }

    def get_user_info(self, access_token: str) -> dict[str, Any]:
        """Fetch the authenticated user's profile from Microsoft Graph.

        Used after OAuth exchange to identify which account was connected.
        """
        import httpx

        headers = {"Authorization": f"Bearer {access_token}"}
        response = httpx.get("https://graph.microsoft.com/v1.0/me", headers=headers)
        response.raise_for_status()
        data = response.json()

        return {
            "email": data.get("mail") or data.get("userPrincipalName"),
            "display_name": data.get("displayName"),
            "tenant_id": data.get("@odata.context", "").split("'")[1] if "'" in data.get("@odata.context", "") else None,
        }





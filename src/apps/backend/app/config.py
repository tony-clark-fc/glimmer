"""Glimmer backend settings — local-first configuration.

Configuration is loaded from environment variables with sensible local
development defaults.  The app must start cleanly with *no* .env file
present; production-sensitive values (secrets, tokens) must fail loudly
if missing rather than falling back to a dangerous default.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Root configuration for the Glimmer backend."""

    model_config = SettingsConfigDict(
        env_prefix="GLIMMER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────
    app_name: str = "Glimmer"
    debug: bool = False

    # ── Network ──────────────────────────────────────────────────
    # Bind to 0.0.0.0 to allow access from other devices on the
    # local network or over VPN.  Use 127.0.0.1 to restrict to
    # localhost only.
    host: str = "0.0.0.0"
    port: int = 8000

    # Comma-separated list of allowed CORS origins.  Defaults cover
    # common local-dev and LAN access patterns.  Add your VPN or
    # Tailscale hostname as needed.
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # ── Database ─────────────────────────────────────────────────
    database_url: str = "postgresql+psycopg://localhost:5432/glimmer_dev"

    # ── Test database (used only by test harness) ────────────────
    test_database_url: str = "postgresql+psycopg://localhost:5432/glimmer_test"

    # ── Telegram Operator Alerts ──────────────────────────────────
    # Bot token for internal system health alerts (not user-facing).
    # If empty, Telegram alerts are silently skipped.
    telegram_bot_token: str = ""
    telegram_operator_chat_id: str = ""

    # ── Google OAuth ──────────────────────────────────────────────
    # ARCH:GoogleScopeMinimization — read-only scopes only.
    google_oauth_client_id: str = ""
    google_oauth_client_secret: str = ""
    google_oauth_redirect_uri: str = "http://localhost:8000/connectors/google/callback"
    google_oauth_scopes: str = (
        "https://www.googleapis.com/auth/gmail.readonly,"
        "https://www.googleapis.com/auth/calendar.readonly"
    )

    # ── Microsoft OAuth ───────────────────────────────────────────
    # ARCH:MicrosoftScopeMinimization — read-only scopes only.
    microsoft_oauth_client_id: str = ""
    microsoft_oauth_client_secret: str = ""
    microsoft_oauth_redirect_uri: str = "http://localhost:8000/connectors/microsoft/callback"
    microsoft_oauth_tenant_id: str = "common"
    microsoft_oauth_scopes: str = "Mail.Read,Calendars.Read,User.Read"

    # ── Token Encryption ──────────────────────────────────────────
    # Fernet key for encrypting OAuth tokens at rest.
    # Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    token_encryption_key: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse the comma-separated CORS origins string into a list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def google_oauth_scope_list(self) -> list[str]:
        """Parse Google OAuth scopes into a list."""
        return [s.strip() for s in self.google_oauth_scopes.split(",") if s.strip()]

    @property
    def microsoft_oauth_scope_list(self) -> list[str]:
        """Parse Microsoft OAuth scopes into a list."""
        return [s.strip() for s in self.microsoft_oauth_scopes.split(",") if s.strip()]

    @property
    def google_oauth_configured(self) -> bool:
        """Return True if Google OAuth credentials are set."""
        return bool(self.google_oauth_client_id and self.google_oauth_client_secret)

    @property
    def microsoft_oauth_configured(self) -> bool:
        """Return True if Microsoft OAuth credentials are set."""
        return bool(self.microsoft_oauth_client_id and self.microsoft_oauth_client_secret)


def get_settings() -> Settings:
    """Return a cached Settings instance (Pydantic handles caching via env)."""
    return Settings()


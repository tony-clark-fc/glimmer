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

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse the comma-separated CORS origins string into a list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


def get_settings() -> Settings:
    """Return a cached Settings instance (Pydantic handles caching via env)."""
    return Settings()


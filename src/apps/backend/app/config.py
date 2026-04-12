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

    # ── Database ─────────────────────────────────────────────────
    database_url: str = "postgresql+psycopg://localhost:5432/glimmer_dev"

    # ── Test database (used only by test harness) ────────────────
    test_database_url: str = "postgresql+psycopg://localhost:5432/glimmer_test"


def get_settings() -> Settings:
    """Return a cached Settings instance (Pydantic handles caching via env)."""
    return Settings()


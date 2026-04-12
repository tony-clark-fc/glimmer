"""Smoke tests — Workstream A foundational proof.

TEST:Smoke.BackendStarts
TEST:Smoke.DatabaseConnectivity
TEST:Foundation.Config.LocalFirstDefaultsResolve
TEST:Foundation.Backend.StructureRespectsBoundaryShape
"""

from __future__ import annotations

import importlib

from fastapi.testclient import TestClient
from sqlalchemy import text


# ── TEST:Smoke.BackendStarts ─────────────────────────────────────────
def test_backend_starts(client: TestClient) -> None:
    """The FastAPI application boots and the health endpoint responds."""
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["app_name"] == "Glimmer"


# ── TEST:Smoke.DatabaseConnectivity ──────────────────────────────────
def test_database_connectivity(client: TestClient) -> None:
    """The health endpoint reports database connectivity as ok."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["database"] == "ok"


def test_database_session_works(db_session) -> None:
    """A raw SQL query succeeds against the test database."""
    result = db_session.execute(text("SELECT 1 AS val"))
    assert result.scalar() == 1


# ── TEST:Foundation.Config.LocalFirstDefaultsResolve ─────────────────
def test_local_first_defaults_resolve() -> None:
    """Settings resolve with sensible local defaults, no .env required."""
    from app.config import Settings

    settings = Settings()
    assert settings.app_name == "Glimmer"
    assert "localhost" in settings.database_url or "127.0.0.1" in settings.database_url
    assert settings.debug is False


# ── TEST:Foundation.Backend.StructureRespectsBoundaryShape ───────────
def test_backend_package_structure_exists() -> None:
    """Core backend packages are importable and follow boundary shape."""
    # app package
    app = importlib.import_module("app")
    assert app is not None

    # config
    config = importlib.import_module("app.config")
    assert hasattr(config, "Settings")
    assert hasattr(config, "get_settings")

    # db
    db = importlib.import_module("app.db")
    assert hasattr(db, "get_engine")

    # api layer
    api = importlib.import_module("app.api")
    assert api is not None

    # health route
    health = importlib.import_module("app.api.health")
    assert hasattr(health, "router")

    # models base
    models = importlib.import_module("app.models")
    assert hasattr(models, "Base")




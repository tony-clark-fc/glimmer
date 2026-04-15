"""API tests for the /operator endpoints.

TEST:API.Operator.CreateReadUpdate
TEST:API.Operator.SingleOperatorConstraint

Proves the PrimaryOperator API surface is correct and enforces
the single-operator MVP constraint.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.operator import PrimaryOperator


@pytest.fixture(autouse=True)
def _clean_operators(db_session: Session):
    """Ensure the operators table is empty before and after each test."""
    db_session.query(PrimaryOperator).delete()
    db_session.commit()
    yield
    db_session.query(PrimaryOperator).delete()
    db_session.commit()


# ── Helper: build a test client that uses the test DB session ────

@pytest.fixture()
def api_client(db_session: Session):
    """TestClient wired to the test database via dependency override."""
    from app.main import create_app
    from app.db import get_db

    app = create_app()

    def _override_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_db

    with TestClient(app) as c:
        yield c


# ── GET /operator ────────────────────────────────────────────────


class TestGetOperator:
    """Test GET /operator."""

    def test_returns_404_when_none(self, api_client: TestClient):
        resp = api_client.get("/operator")
        assert resp.status_code == 404
        assert "No operator configured" in resp.json()["detail"]

    def test_returns_operator_after_create(self, api_client: TestClient):
        api_client.post("/operator", json={"display_name": "Tony"})
        resp = api_client.get("/operator")
        assert resp.status_code == 200
        body = resp.json()
        assert body["display_name"] == "Tony"
        assert body["id"] is not None


# ── POST /operator ───────────────────────────────────────────────


class TestCreateOperator:
    """Test POST /operator."""

    def test_create_minimal(self, api_client: TestClient):
        resp = api_client.post("/operator", json={"display_name": "Tony"})
        assert resp.status_code == 201
        body = resp.json()
        assert body["display_name"] == "Tony"
        assert body["preferred_timezone"] is None

    def test_create_with_preferences(self, api_client: TestClient):
        resp = api_client.post(
            "/operator",
            json={
                "display_name": "Tony",
                "preferred_timezone": "Europe/London",
                "preferred_language": "en-GB",
                "channel_preferences": {"telegram_enabled": True},
            },
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["preferred_timezone"] == "Europe/London"
        assert body["preferred_language"] == "en-GB"
        assert body["channel_preferences"]["telegram_enabled"] is True

    def test_create_rejects_duplicate(self, api_client: TestClient):
        api_client.post("/operator", json={"display_name": "Tony"})
        resp = api_client.post("/operator", json={"display_name": "Duplicate"})
        assert resp.status_code == 409
        assert "already exists" in resp.json()["detail"]

    def test_create_rejects_empty_name(self, api_client: TestClient):
        resp = api_client.post("/operator", json={"display_name": ""})
        assert resp.status_code == 422  # validation error


# ── PATCH /operator ──────────────────────────────────────────────


class TestUpdateOperator:
    """Test PATCH /operator."""

    def test_update_returns_404_when_none(self, api_client: TestClient):
        resp = api_client.patch("/operator", json={"display_name": "Tony"})
        assert resp.status_code == 404

    def test_update_single_field(self, api_client: TestClient):
        api_client.post("/operator", json={"display_name": "Tony"})
        resp = api_client.patch(
            "/operator",
            json={"preferred_timezone": "America/New_York"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["display_name"] == "Tony"  # unchanged
        assert body["preferred_timezone"] == "America/New_York"

    def test_update_display_name(self, api_client: TestClient):
        api_client.post("/operator", json={"display_name": "Tony"})
        resp = api_client.patch("/operator", json={"display_name": "Tony S"})
        assert resp.status_code == 200
        assert resp.json()["display_name"] == "Tony S"

    def test_update_preserves_unset_fields(self, api_client: TestClient):
        api_client.post(
            "/operator",
            json={
                "display_name": "Tony",
                "preferred_timezone": "Europe/London",
                "preferred_language": "en-GB",
            },
        )
        api_client.patch(
            "/operator",
            json={"preferred_timezone": "US/Eastern"},
        )
        resp = api_client.get("/operator")
        body = resp.json()
        assert body["preferred_timezone"] == "US/Eastern"
        assert body["preferred_language"] == "en-GB"  # not clobbered


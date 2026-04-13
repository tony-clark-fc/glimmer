"""API tests for persona selection endpoint — Workstream E persona rendering.

TEST:UI.Persona.FallbackAndContextSelectionWorks (API backing)
TEST:UI.Persona.RenderingRemainsSubordinateToOperationalContent (structural)
"""

from __future__ import annotations

import pytest
from sqlalchemy import text

from app.db import get_session
from app.models.persona import PersonaAsset, PersonaClassification


# ── Fixtures ─────────────────────────────────────────────────────

_CLEANUP_TABLES = [
    "persona_selection_events",
    "persona_classifications",
    "persona_assets",
]


@pytest.fixture(autouse=True)
def _clean_tables(client):
    """Ensure persona tables are clean before and after each test."""
    session = get_session()
    for table in _CLEANUP_TABLES:
        session.execute(text(f"DELETE FROM {table}"))
    session.commit()
    session.close()
    yield
    session = get_session()
    for table in _CLEANUP_TABLES:
        session.execute(text(f"DELETE FROM {table}"))
    session.commit()
    session.close()


# ── Helpers ──────────────────────────────────────────────────────


def _seed_asset(
    label: str = "Default Glimmer",
    asset_path: str = "/assets/persona/default.png",
    is_default: bool = False,
    classifications: list[tuple[str, str]] | None = None,
) -> PersonaAsset:
    session = get_session()
    asset = PersonaAsset(
        label=label,
        asset_path=asset_path,
        asset_type="avatar",
        is_default=is_default,
    )
    session.add(asset)
    session.flush()
    if classifications:
        for ctype, cvalue in classifications:
            c = PersonaClassification(
                asset_id=asset.id,
                classification_type=ctype,
                classification_value=cvalue,
            )
            session.add(c)
    session.commit()
    session.refresh(asset)
    return asset


# ── Tests ────────────────────────────────────────────────────────


class TestPersonaSelection:
    """TEST:UI.Persona.FallbackAndContextSelectionWorks — API backing."""

    def test_select_returns_null_when_no_assets(self, client) -> None:
        resp = client.get("/persona/select")
        assert resp.status_code == 200
        data = resp.json()
        assert data["asset"] is None
        assert data["fallback_used"] is True
        assert "No active persona assets" in data["selection_reason"]

    def test_select_returns_default_when_no_context(self, client) -> None:
        _seed_asset(label="Default", is_default=True)
        resp = client.get("/persona/select")
        assert resp.status_code == 200
        data = resp.json()
        assert data["asset"] is not None
        assert data["asset"]["label"] == "Default"
        assert data["asset"]["is_default"] is True
        assert data["fallback_used"] is True
        assert "no context specified" in data["selection_reason"].lower()

    def test_select_returns_context_match(self, client) -> None:
        _seed_asset(
            label="Executive Focus",
            classifications=[
                ("suitability", "focused"),
                ("suitability", "executive"),
            ],
        )
        _seed_asset(label="Default", is_default=True)

        resp = client.get("/persona/select?context=briefing")
        assert resp.status_code == 200
        data = resp.json()
        assert data["asset"] is not None
        assert data["asset"]["label"] == "Executive Focus"
        assert data["fallback_used"] is False
        assert "briefing" in data["selection_reason"]

    def test_select_falls_back_to_default_on_unknown_context(self, client) -> None:
        _seed_asset(label="Default Avatar", is_default=True)
        resp = client.get("/persona/select?context=unknown_mode")
        assert resp.status_code == 200
        data = resp.json()
        assert data["asset"] is not None
        assert data["asset"]["label"] == "Default Avatar"
        assert data["fallback_used"] is True

    def test_select_falls_back_to_default_when_context_has_no_match(
        self, client
    ) -> None:
        _seed_asset(
            label="Voice Only",
            classifications=[("suitability", "conversational")],
        )
        _seed_asset(label="Default", is_default=True)

        # Request context=triage, which looks for "focused"/"executive"
        resp = client.get("/persona/select?context=triage")
        assert resp.status_code == 200
        data = resp.json()
        assert data["asset"]["label"] == "Default"
        assert data["fallback_used"] is True

    def test_select_for_drafting_context(self, client) -> None:
        _seed_asset(
            label="Drafting Pro",
            classifications=[("suitability", "drafting")],
        )
        resp = client.get("/persona/select?context=draft")
        assert resp.status_code == 200
        data = resp.json()
        assert data["asset"]["label"] == "Drafting Pro"
        assert data["fallback_used"] is False

    def test_select_for_today_context(self, client) -> None:
        _seed_asset(
            label="Morning Briefer",
            classifications=[("suitability", "briefing")],
        )
        resp = client.get("/persona/select?context=today")
        assert resp.status_code == 200
        data = resp.json()
        assert data["asset"]["label"] == "Morning Briefer"
        assert data["fallback_used"] is False


class TestPersonaAssetList:
    """List all active persona assets."""

    def test_list_returns_empty_when_none(self, client) -> None:
        resp = client.get("/persona/assets")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_returns_active_assets(self, client) -> None:
        _seed_asset(label="Asset A", is_default=True)
        _seed_asset(label="Asset B")

        resp = client.get("/persona/assets")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        labels = {a["label"] for a in data}
        assert labels == {"Asset A", "Asset B"}

    def test_list_includes_classifications(self, client) -> None:
        _seed_asset(
            label="Classified",
            classifications=[
                ("mood", "focused"),
                ("tone", "professional"),
            ],
        )
        resp = client.get("/persona/assets")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        classifs = data[0]["classifications"]
        assert len(classifs) == 2
        types = {c["classification_type"] for c in classifs}
        assert types == {"mood", "tone"}


class TestPersonaResponseShape:
    """Verify response contract shape for frontend consumption."""

    def test_selection_response_has_required_fields(self, client) -> None:
        _seed_asset(label="Test", is_default=True)
        resp = client.get("/persona/select")
        data = resp.json()
        assert "asset" in data
        assert "selection_reason" in data
        assert "fallback_used" in data
        asset = data["asset"]
        assert "id" in asset
        assert "label" in asset
        assert "asset_path" in asset
        assert "asset_type" in asset
        assert "is_default" in asset
        assert "classifications" in asset


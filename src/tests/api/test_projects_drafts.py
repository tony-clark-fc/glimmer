"""API tests for projects and drafts endpoints — Workstream E backend surfaces.

TEST:UI.PortfolioView.ComparesProjectAttentionDemand (API backing)
TEST:UI.ProjectWorkspace.ShowsSynthesisNotJustChronology (API backing)
TEST:UI.DraftWorkspace.ShowsContextAndVariants (API backing)
TEST:Drafting.Variants.MultipleVariantsRemainLinked (API backing)
TEST:Drafting.NoAutoSend.BoundaryPreserved (structural: no send endpoint)
"""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import text

from app.db import get_session
from app.models.portfolio import Project
from app.models.execution import WorkItem, BlockerRecord, WaitingOnRecord
from app.models.interpretation import ExtractedAction
from app.models.drafting import Draft, DraftVariant


# ── Fixtures ─────────────────────────────────────────────────────

_CLEANUP_TABLES = [
    "draft_variants",
    "drafts",
    "extracted_actions",
    "waiting_on_records",
    "blocker_records",
    "work_items",
    "projects",
]


@pytest.fixture(autouse=True)
def _clean_tables(client):
    """Ensure tables are clean before and after each test."""
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


def _seed_project(name: str = "Alpha Project", **kwargs) -> Project:
    session = get_session()
    p = Project(name=name, status="active", **kwargs)
    session.add(p)
    session.commit()
    session.refresh(p)
    return p


def _seed_work_item(project_id: uuid.UUID, title: str, status: str = "open") -> WorkItem:
    session = get_session()
    wi = WorkItem(project_id=project_id, title=title, status=status)
    session.add(wi)
    session.commit()
    session.refresh(wi)
    return wi


def _seed_blocker(project_id: uuid.UUID, summary: str) -> BlockerRecord:
    session = get_session()
    b = BlockerRecord(project_id=project_id, summary=summary, status="active")
    session.add(b)
    session.commit()
    session.refresh(b)
    return b


def _seed_draft(body: str = "Hello — draft response", **kwargs) -> Draft:
    session = get_session()
    d = Draft(body_content=body, status="draft", **kwargs)
    session.add(d)
    session.commit()
    session.refresh(d)
    return d


def _seed_variant(draft_id: uuid.UUID, label: str, body: str) -> DraftVariant:
    session = get_session()
    v = DraftVariant(draft_id=draft_id, variant_label=label, body_content=body)
    session.add(v)
    session.commit()
    session.refresh(v)
    return v


# ── Projects API ─────────────────────────────────────────────────


class TestProjectsList:
    def test_list_projects_empty(self, client) -> None:
        resp = client.get("/projects")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_projects_with_data(self, client) -> None:
        p = _seed_project("Alpha")
        _seed_work_item(p.id, "Fix login bug", status="open")
        _seed_work_item(p.id, "Done thing", status="completed")
        _seed_blocker(p.id, "Waiting for creds")

        resp = client.get("/projects")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        proj = data[0]
        assert proj["name"] == "Alpha"
        assert proj["open_items"] == 1  # only open ones
        assert proj["active_blockers"] == 1


class TestProjectDetail:
    def test_get_project_detail(self, client) -> None:
        p = _seed_project("Beta", objective="Ship the MVP", short_summary="A cool project")
        _seed_work_item(p.id, "Design review")
        _seed_blocker(p.id, "Need API keys")

        resp = client.get(f"/projects/{p.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Beta"
        assert data["objective"] == "Ship the MVP"
        assert len(data["open_items"]) == 1
        assert len(data["blockers"]) == 1

    def test_get_project_not_found(self, client) -> None:
        resp = client.get(f"/projects/{uuid.uuid4()}")
        assert resp.status_code == 404


# ── Drafts API ───────────────────────────────────────────────────


class TestDraftsList:
    def test_list_drafts_empty(self, client) -> None:
        resp = client.get("/drafts")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_drafts_with_data(self, client) -> None:
        _seed_draft("Please review the attached", intent_label="Follow-up")

        resp = client.get("/drafts")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["body_content"] == "Please review the attached"
        assert data[0]["intent_label"] == "Follow-up"


class TestDraftDetail:
    def test_get_draft_with_variants(self, client) -> None:
        """TEST:Drafting.Variants.MultipleVariantsRemainLinked"""
        d = _seed_draft("Base draft", intent_label="Reply")
        _seed_variant(d.id, "concise", "Short version")
        _seed_variant(d.id, "warm", "Friendly version")

        resp = client.get(f"/drafts/{d.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["body_content"] == "Base draft"
        assert len(data["variants"]) == 2
        labels = {v["variant_label"] for v in data["variants"]}
        assert labels == {"concise", "warm"}

    def test_get_draft_not_found(self, client) -> None:
        resp = client.get(f"/drafts/{uuid.uuid4()}")
        assert resp.status_code == 404


class TestNoAutoSendBoundary:
    """TEST:Drafting.NoAutoSend.BoundaryPreserved — no send endpoint.

    Verify there is no POST/PUT endpoint that could be confused with
    sending a draft. The API must remain review-only.
    """

    def test_no_send_endpoint_exists(self, client) -> None:
        d = _seed_draft("Test draft")
        # Try obvious send-like paths — all should 404 or 405
        for method in ("post", "put", "patch"):
            resp = getattr(client, method)(
                f"/drafts/{d.id}/send",
                json={},
            )
            assert resp.status_code in (404, 405), (
                f"Unexpected {resp.status_code} for {method.upper()} /drafts/{{id}}/send — "
                "no send endpoint should exist"
            )

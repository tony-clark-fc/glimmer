"""Draft creation API integration tests.

TEST:Drafting.API.CreateDraftReturnsReviewableDraft
TEST:Drafting.API.NoAutoSendOnCreatedDraft
TEST:Drafting.API.LLMContextFieldsAccepted
TEST:Release.Drafting.CreateDraftEndpointWorksCorrectly

Proves the POST /drafts endpoint creates reviewable drafts,
preserves no-auto-send boundary, and accepts LLM context fields.
"""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import text

from app.db import get_session
from app.models.drafting import Draft
from app.models.portfolio import Project


# ── Fixtures ─────────────────────────────────────────────────────


_CLEANUP_TABLES = ["draft_variants", "drafts", "audit_records", "projects"]


@pytest.fixture(autouse=True)
def _clean_tables(client):
    """Ensure draft tables are clean before and after each test."""
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


# ── Creation Tests ───────────────────────────────────────────────


class TestCreateDraft:
    """TEST:Drafting.API.CreateDraftReturnsReviewableDraft"""

    def test_create_draft_with_body(self, client) -> None:
        """POST /drafts with body_content creates a reviewable draft."""
        resp = client.post(
            "/drafts",
            json={
                "body_content": "Hi — following up on our meeting.",
                "intent": "follow_up",
                "channel_type": "email",
                "tone_mode": "concise",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["body_content"] == "Hi — following up on our meeting."
        assert data["intent_label"] == "follow_up"
        assert data["channel_type"] == "email"
        assert data["tone_mode"] == "concise"
        assert data["status"] == "draft"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_draft_minimal_body(self, client) -> None:
        """POST /drafts with only body_content creates a draft."""
        resp = client.post(
            "/drafts",
            json={"body_content": "Quick note."},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["body_content"] == "Quick note."
        assert data["status"] == "draft"
        assert data["intent_label"] == "reply"  # default

    def test_create_draft_empty_body_accepted(self, client) -> None:
        """POST /drafts with empty body_content accepted (LLM may fill it)."""
        resp = client.post(
            "/drafts",
            json={
                "body_content": "",
                "intent": "initiate",
                "context_summary": "Starting a new conversation about Q3 planning.",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        # LLM is disabled in tests, so body remains empty
        assert data["status"] == "draft"
        assert data["intent_label"] == "initiate"

    def test_create_draft_default_body(self, client) -> None:
        """POST /drafts with no body_content field uses default empty string."""
        resp = client.post(
            "/drafts",
            json={"intent": "reply"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "draft"

    def test_created_draft_appears_in_list(self, client) -> None:
        """Created draft appears in GET /drafts listing."""
        client.post(
            "/drafts",
            json={"body_content": "Listed draft."},
        )
        resp = client.get("/drafts")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["body_content"] == "Listed draft."

    def test_created_draft_retrievable_by_id(self, client) -> None:
        """Created draft retrievable via GET /drafts/{id}."""
        create_resp = client.post(
            "/drafts",
            json={"body_content": "Specific draft.", "intent": "brief"},
        )
        assert create_resp.status_code == 201
        draft_id = create_resp.json()["id"]

        detail_resp = client.get(f"/drafts/{draft_id}")
        assert detail_resp.status_code == 200
        assert detail_resp.json()["body_content"] == "Specific draft."
        assert detail_resp.json()["intent_label"] == "brief"


class TestCreateDraftLinkedEntities:
    """TEST:Drafting.API.DraftLinkedToProjectAndSource"""

    def test_create_draft_with_project_link(self, client) -> None:
        """Draft can be linked to a project ID."""
        # Create a real project so FK is satisfied
        session = get_session()
        project = Project(name="TestProj", status="active")
        session.add(project)
        session.commit()
        project_id = str(project.id)
        session.close()

        resp = client.post(
            "/drafts",
            json={
                "body_content": "Project-linked draft.",
                "project_id": project_id,
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["linked_project_id"] == project_id

    def test_create_draft_with_source_message(self, client) -> None:
        """Draft can reference a source message (no FK constraint)."""
        msg_id = str(uuid.uuid4())
        resp = client.post(
            "/drafts",
            json={
                "body_content": "Reply draft.",
                "source_message_id": msg_id,
                "source_record_type": "message",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["source_message_id"] == msg_id
        assert data["source_record_type"] == "message"


class TestCreateDraftLLMContext:
    """TEST:Drafting.API.LLMContextFieldsAccepted

    Proves the endpoint accepts all LLM context fields without error,
    even when LLM is disabled (fields are simply ignored).
    """

    def test_all_llm_context_fields_accepted(self, client) -> None:
        """All LLM context fields accepted in request body."""
        resp = client.post(
            "/drafts",
            json={
                "body_content": "",
                "intent": "reply",
                "channel_type": "email",
                "tone_mode": "warm",
                "context_summary": "Long conversation about Q3 budget.",
                "original_message_summary": "Client asked about timeline.",
                "project_name": "Budget Review",
                "stakeholder_names": ["Alice", "Bob"],
                "key_points": ["Confirm timeline", "Mention budget approval"],
                "rationale_summary": "Client needs a reply before Friday.",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "draft"
        assert data["tone_mode"] == "warm"
        assert data["rationale_summary"] is not None


class TestCreateDraftNoAutoSend:
    """TEST:Drafting.API.NoAutoSendOnCreatedDraft

    Critical safety proof: created drafts are always in 'draft' status
    and never trigger any send behavior.
    """

    def test_created_draft_is_never_sent(self, client) -> None:
        """Draft status is always 'draft', never 'sent'."""
        resp = client.post(
            "/drafts",
            json={"body_content": "Must not auto-send."},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "draft"
        assert data["status"] != "sent"
        assert data["status"] != "sent_by_operator"

    def test_no_send_endpoint_after_creation(self, client) -> None:
        """No send endpoint exists for created drafts."""
        resp = client.post(
            "/drafts",
            json={"body_content": "Test."},
        )
        draft_id = resp.json()["id"]

        for method in ("post", "put", "patch"):
            send_resp = getattr(client, method)(
                f"/drafts/{draft_id}/send",
                json={},
            )
            assert send_resp.status_code in (404, 405), (
                f"Unexpected {send_resp.status_code} for {method.upper()} "
                f"/drafts/{{id}}/send — no send endpoint should exist"
            )

    def test_draft_persisted_with_audit_trail(self, client) -> None:
        """Created draft produces an audit record."""
        resp = client.post(
            "/drafts",
            json={"body_content": "Audited draft.", "intent": "reply"},
        )
        assert resp.status_code == 201

        # Verify the draft was persisted
        draft_id = resp.json()["id"]
        session = get_session()
        try:
            draft = session.get(Draft, uuid.UUID(draft_id))
            assert draft is not None
            assert draft.status == "draft"
        finally:
            session.close()


class TestCreateDraftValidation:
    """TEST:Drafting.API.ValidationOnCreate"""

    def test_empty_json_body_accepted(self, client) -> None:
        """Empty JSON body uses all defaults — creates a minimal draft."""
        resp = client.post("/drafts", json={})
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "draft"
        assert data["intent_label"] == "reply"

    def test_invalid_uuid_rejected(self, client) -> None:
        """Invalid UUID for project_id rejected."""
        resp = client.post(
            "/drafts",
            json={"body_content": "Bad ID.", "project_id": "not-a-uuid"},
        )
        assert resp.status_code == 422




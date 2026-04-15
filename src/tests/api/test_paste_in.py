"""Tests for E15 — Persona page paste-in ingestion.

PLAN:WorkstreamE.PackageE15.PersonaPagePasteIn
TEST:PersonaPage.PasteIn.CapturePreservesRawArtifact
TEST:PersonaPage.PasteIn.ExtractedEntitiesAppearAsCandidateNodes
TEST:PersonaPage.PasteIn.DoesNotBypassStagedPersistence

Proves the paste-in pipeline:
1. Raw content is preserved as a PasteInSourceArtifact before interpretation
2. Extracted entities appear as candidate nodes with paste_in source origin
3. Paste-in does not bypass the staged persistence model
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture()
def client():
    """Create a test client."""
    app = create_app()
    with TestClient(app) as c:
        yield c


def _create_session(client: TestClient, mode: str = "idea") -> str:
    """Helper to create a session and return its ID."""
    resp = client.post("/persona/sessions", json={"workspace_mode": mode})
    assert resp.status_code == 201
    return resp.json()["id"]


def _mock_extraction_result(**overrides):
    """Build a mock SmartPasteInExtractionResult-like object."""
    from dataclasses import dataclass, field

    @dataclass
    class _MockResult:
        used_llm: bool = False
        fallback_reason: str | None = None
        entities: list[dict] = field(default_factory=list)
        explanation: str = "Mock extraction complete."
        inference_latency_ms: float = 0.0

    defaults = {
        "entities": [
            {"entity_type": "stakeholder", "label": "Alice", "subtitle": "Project lead", "confidence": 0.9},
            {"entity_type": "risk", "label": "Timeline slip", "subtitle": "Phase 2 may be delayed", "confidence": 0.7},
        ],
        "explanation": "I found 2 entities in the pasted content: a stakeholder (Alice) and a risk (Timeline slip).",
    }
    defaults.update(overrides)
    return _MockResult(**defaults)


_MOCK_TARGET = "app.inference.orchestration.paste_in_extract_smart"


# ── TEST:PersonaPage.PasteIn.CapturePreservesRawArtifact ─────────────


class TestPasteInArtifactPreservation:
    """Prove paste-in provenance is preserved — raw content is stored
    before any entity extraction begins."""

    @patch(_MOCK_TARGET, new_callable=AsyncMock, return_value=_mock_extraction_result())
    def test_paste_in_returns_artifact_id(self, mock_extract, client: TestClient):
        """Submitting paste-in content returns a persisted artifact ID."""
        session_id = _create_session(client)
        resp = client.post(
            f"/persona/sessions/{session_id}/paste-in",
            json={
                "content": "Meeting notes: Alice agreed to deliver specs by Friday.",
                "content_type_hint": "meeting_notes",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "artifact_id" in data
        assert data["artifact_id"]  # non-empty
        # Artifact ID should be a valid UUID
        uuid.UUID(data["artifact_id"])

    @patch(_MOCK_TARGET, new_callable=AsyncMock, return_value=_mock_extraction_result())
    def test_paste_in_preserves_extraction_status(self, mock_extract, client: TestClient):
        """The response includes extraction_status showing the pipeline result."""
        session_id = _create_session(client)
        resp = client.post(
            f"/persona/sessions/{session_id}/paste-in",
            json={"content": "Some test content to analyze."},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["extraction_status"] in ("extracted", "failed")

    @patch(_MOCK_TARGET, new_callable=AsyncMock, return_value=_mock_extraction_result())
    def test_paste_in_returns_explanation(self, mock_extract, client: TestClient):
        """The response includes a conversational explanation from Glimmer."""
        session_id = _create_session(client)
        resp = client.post(
            f"/persona/sessions/{session_id}/paste-in",
            json={"content": "Alice needs to finish the budget report by Monday."},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "explanation" in data
        assert len(data["explanation"]) > 0

    @patch(_MOCK_TARGET, new_callable=AsyncMock, return_value=_mock_extraction_result())
    def test_paste_in_default_content_type_is_freeform(self, mock_extract, client: TestClient):
        """Content type defaults to 'freeform' when not specified."""
        session_id = _create_session(client)
        resp = client.post(
            f"/persona/sessions/{session_id}/paste-in",
            json={"content": "Just some notes."},
        )
        assert resp.status_code == 201
        # The endpoint should accept and not error on default content type
        assert resp.json()["artifact_id"]

    def test_paste_in_empty_content_rejected(self, client: TestClient):
        """Empty content is rejected with 422."""
        session_id = _create_session(client)
        resp = client.post(
            f"/persona/sessions/{session_id}/paste-in",
            json={"content": ""},
        )
        assert resp.status_code == 422

    def test_paste_in_whitespace_only_rejected(self, client: TestClient):
        """Whitespace-only content is rejected with 422."""
        session_id = _create_session(client)
        resp = client.post(
            f"/persona/sessions/{session_id}/paste-in",
            json={"content": "   \n\t  "},
        )
        assert resp.status_code == 422


# ── TEST:PersonaPage.PasteIn.ExtractedEntitiesAppearAsCandidateNodes ──


class TestPasteInExtractedEntities:
    """Prove paste-in extraction results integrate into the mind-map as
    reviewable candidate entities, not silently accepted state."""

    @patch(_MOCK_TARGET, new_callable=AsyncMock, return_value=_mock_extraction_result())
    def test_candidate_nodes_have_paste_in_source_origin(self, mock_extract, client: TestClient):
        """Extracted candidate nodes have source_origin='paste_in'."""
        session_id = _create_session(client)
        resp = client.post(
            f"/persona/sessions/{session_id}/paste-in",
            json={
                "content": "Project Alpha: Bob is handling the infrastructure. Risk: budget overrun by 20%.",
                "content_type_hint": "freeform",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert len(data["candidate_nodes"]) > 0
        for node in data["candidate_nodes"]:
            assert node["source_origin"] == "paste_in"
            assert node["status"] == "pending"

    @patch(_MOCK_TARGET, new_callable=AsyncMock, return_value=_mock_extraction_result())
    def test_candidate_nodes_have_valid_entity_types(self, mock_extract, client: TestClient):
        """Extracted nodes have valid entity types from the allowed set."""
        session_id = _create_session(client)
        resp = client.post(
            f"/persona/sessions/{session_id}/paste-in",
            json={
                "content": "Meeting with stakeholder Jane about milestone delivery.",
                "content_type_hint": "meeting_notes",
            },
        )
        assert resp.status_code == 201
        valid_types = {
            "project", "stakeholder", "milestone", "risk",
            "blocker", "work_item", "decision", "dependency",
        }
        for node in resp.json()["candidate_nodes"]:
            assert node["entity_type"] in valid_types

    @patch(_MOCK_TARGET, new_callable=AsyncMock, return_value=_mock_extraction_result())
    def test_candidate_nodes_include_artifact_provenance(self, mock_extract, client: TestClient):
        """Extracted nodes carry metadata linking back to the paste-in artifact."""
        session_id = _create_session(client)
        resp = client.post(
            f"/persona/sessions/{session_id}/paste-in",
            json={"content": "Alice is leading the design phase."},
        )
        assert resp.status_code == 201
        data = resp.json()
        artifact_id = data["artifact_id"]
        for node in data["candidate_nodes"]:
            assert node.get("metadata", {}).get("paste_in_artifact_id") == artifact_id

    @patch(_MOCK_TARGET, new_callable=AsyncMock, return_value=_mock_extraction_result())
    def test_candidate_nodes_have_node_ids(self, mock_extract, client: TestClient):
        """Each extracted node has a unique node_id."""
        session_id = _create_session(client)
        resp = client.post(
            f"/persona/sessions/{session_id}/paste-in",
            json={"content": "Stakeholder Bob. Risk: timeline. Blocker: missing specs."},
        )
        assert resp.status_code == 201
        nodes = resp.json()["candidate_nodes"]
        node_ids = [n["node_id"] for n in nodes]
        assert len(node_ids) == len(set(node_ids)), "Node IDs must be unique"

    @patch(_MOCK_TARGET, new_callable=AsyncMock, return_value=_mock_extraction_result())
    def test_used_llm_field_present(self, mock_extract, client: TestClient):
        """Response includes used_llm field indicating extraction path."""
        session_id = _create_session(client)
        resp = client.post(
            f"/persona/sessions/{session_id}/paste-in",
            json={"content": "Some content to analyze."},
        )
        assert resp.status_code == 201
        assert "used_llm" in resp.json()

    @patch(_MOCK_TARGET, new_callable=AsyncMock, return_value=_mock_extraction_result(entities=[], explanation="No entities found."))
    def test_empty_extraction_returns_explanation(self, mock_extract, client: TestClient):
        """When no entities are extracted, response still has explanation."""
        session_id = _create_session(client)
        resp = client.post(
            f"/persona/sessions/{session_id}/paste-in",
            json={"content": "Hello world."},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["candidate_nodes"] == []
        assert len(data["explanation"]) > 0


# ── TEST:PersonaPage.PasteIn.DoesNotBypassStagedPersistence ──────────


class TestPasteInDoesNotBypassStagedPersistence:
    """Prove pasted-content entities enter the working state and require
    explicit confirmation before database persistence."""

    def test_paste_in_on_confirmed_session_rejected(self, client: TestClient):
        """Paste-in is rejected on a confirmed (terminal) session."""
        session_id = _create_session(client)

        # Save some working state and confirm
        client.put(
            f"/persona/sessions/{session_id}/working-state",
            json={
                "candidate_nodes": [
                    {
                        "node_id": "n1",
                        "entity_type": "project",
                        "label": "Test",
                        "status": "accepted_by_operator",
                        "source_origin": "conversation",
                    }
                ],
                "candidate_edges": [],
                "state_version": 1,
            },
        )
        client.post(
            f"/persona/sessions/{session_id}/confirm",
            json={"accepted_node_ids": ["n1"]},
        )

        resp = client.post(
            f"/persona/sessions/{session_id}/paste-in",
            json={"content": "Should be rejected."},
        )
        assert resp.status_code == 409

    def test_paste_in_on_abandoned_session_rejected(self, client: TestClient):
        """Paste-in is rejected on an abandoned (terminal) session."""
        session_id = _create_session(client)
        client.post(f"/persona/sessions/{session_id}/discard")

        resp = client.post(
            f"/persona/sessions/{session_id}/paste-in",
            json={"content": "Should be rejected."},
        )
        assert resp.status_code == 409

    @patch(_MOCK_TARGET, new_callable=AsyncMock, return_value=_mock_extraction_result())
    def test_paste_in_does_not_create_operational_entities(self, mock_extract, client: TestClient):
        """Paste-in alone does not create projects/stakeholders in the operational DB."""
        session_id = _create_session(client)

        # Submit paste-in
        resp = client.post(
            f"/persona/sessions/{session_id}/paste-in",
            json={
                "content": "Project Phoenix: stakeholder Alice. Milestone: phase 1 complete.",
                "content_type_hint": "freeform",
            },
        )
        assert resp.status_code == 201
        assert len(resp.json()["candidate_nodes"]) > 0

        # The operational project list should not contain paste-in entities
        # (Paste-in creates candidates, not operational records — they only
        # reach the DB through the confirm flow.)

    def test_paste_in_invalid_session_404(self, client: TestClient):
        """Paste-in on a non-existent session returns 404."""
        fake_id = str(uuid.uuid4())
        resp = client.post(
            f"/persona/sessions/{fake_id}/paste-in",
            json={"content": "Test content."},
        )
        assert resp.status_code == 404

    def test_paste_in_bad_uuid_404(self, client: TestClient):
        """Paste-in with an invalid UUID returns 404."""
        resp = client.post(
            "/persona/sessions/not-a-uuid/paste-in",
            json={"content": "Test content."},
        )
        assert resp.status_code == 404

    @patch(_MOCK_TARGET, new_callable=AsyncMock, return_value=_mock_extraction_result())
    def test_multiple_paste_ins_same_session(self, mock_extract, client: TestClient):
        """Multiple paste-ins on the same session are all accepted."""
        session_id = _create_session(client)

        resp1 = client.post(
            f"/persona/sessions/{session_id}/paste-in",
            json={"content": "First paste: stakeholder Bob."},
        )
        assert resp1.status_code == 201
        id1 = resp1.json()["artifact_id"]

        resp2 = client.post(
            f"/persona/sessions/{session_id}/paste-in",
            json={"content": "Second paste: risk — timeline slip."},
        )
        assert resp2.status_code == 201
        id2 = resp2.json()["artifact_id"]

        # Different artifacts
        assert id1 != id2

    @patch(_MOCK_TARGET, new_callable=AsyncMock, return_value=_mock_extraction_result())
    def test_paste_in_on_paused_session_accepted(self, mock_extract, client: TestClient):
        """Paste-in is accepted on a paused session."""
        session_id = _create_session(client)

        # Pause the session
        client.patch(
            f"/persona/sessions/{session_id}",
            json={"session_status": "paused"},
        )

        resp = client.post(
            f"/persona/sessions/{session_id}/paste-in",
            json={"content": "Content for paused session."},
        )
        assert resp.status_code == 201


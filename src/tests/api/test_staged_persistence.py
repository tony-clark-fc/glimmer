"""Tests for E14 — Persona page staged persistence and confirm flow.

PLAN:WorkstreamE.PackageE14.PersonaPageStagedPersistence
TEST:PersonaPage.StagedPersistence.ConfirmSaveCommitsAllEntities
TEST:PersonaPage.StagedPersistence.DiscardDoesNotPersist
TEST:PersonaPage.MindMap.WorkingStateVisuallyDistinct
"""

from __future__ import annotations

import pytest

from app.main import create_app
from fastapi.testclient import TestClient


@pytest.fixture()
def client():
    """Create a test client."""
    app = create_app()
    with TestClient(app) as c:
        yield c


def _create_session(client: TestClient) -> str:
    """Helper to create a session and return its ID."""
    resp = client.post("/persona/sessions", json={"workspace_mode": "idea"})
    assert resp.status_code == 201
    return resp.json()["id"]


class TestWorkingStateSaveAndRetrieve:
    """Test the working state save/backup and retrieval cycle."""

    def test_save_working_state_creates_backup(self, client: TestClient):
        session_id = _create_session(client)
        payload = {
            "candidate_nodes": [
                {
                    "node_id": "node-1",
                    "entity_type": "project",
                    "label": "Test Project",
                    "subtitle": "A test",
                    "status": "pending",
                    "source_origin": "conversation",
                },
            ],
            "candidate_edges": [],
            "state_version": 1,
        }
        resp = client.put(
            f"/persona/sessions/{session_id}/working-state", json=payload
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["session_id"] == session_id
        assert len(data["candidate_nodes"]) == 1
        assert data["state_version"] == 1

    def test_get_working_state_returns_empty_when_none(self, client: TestClient):
        session_id = _create_session(client)
        resp = client.get(f"/persona/sessions/{session_id}/working-state")
        assert resp.status_code == 200
        data = resp.json()
        assert data["candidate_nodes"] == []
        assert data["state_version"] == 0

    def test_get_working_state_returns_saved_data(self, client: TestClient):
        session_id = _create_session(client)
        nodes = [
            {
                "node_id": "n1",
                "entity_type": "stakeholder",
                "label": "Alice",
                "status": "pending",
                "source_origin": "conversation",
            },
            {
                "node_id": "n2",
                "entity_type": "risk",
                "label": "Budget overrun",
                "status": "accepted_by_operator",
                "source_origin": "conversation",
            },
        ]
        edges = [
            {
                "edge_id": "e1",
                "source_node_id": "n1",
                "target_node_id": "n2",
                "relation": "linked_to",
            },
        ]
        client.put(
            f"/persona/sessions/{session_id}/working-state",
            json={
                "candidate_nodes": nodes,
                "candidate_edges": edges,
                "state_version": 3,
            },
        )
        resp = client.get(f"/persona/sessions/{session_id}/working-state")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["candidate_nodes"]) == 2
        assert len(data["candidate_edges"]) == 1
        assert data["state_version"] == 3

    def test_save_updates_existing_working_state(self, client: TestClient):
        session_id = _create_session(client)
        # First save
        client.put(
            f"/persona/sessions/{session_id}/working-state",
            json={
                "candidate_nodes": [
                    {"node_id": "n1", "entity_type": "project", "label": "V1", "status": "pending", "source_origin": "conversation"},
                ],
                "candidate_edges": [],
                "state_version": 1,
            },
        )
        # Second save with updated data
        resp = client.put(
            f"/persona/sessions/{session_id}/working-state",
            json={
                "candidate_nodes": [
                    {"node_id": "n1", "entity_type": "project", "label": "V2", "status": "accepted_by_operator", "source_origin": "conversation"},
                    {"node_id": "n2", "entity_type": "milestone", "label": "M1", "status": "pending", "source_origin": "conversation"},
                ],
                "candidate_edges": [],
                "state_version": 2,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["candidate_nodes"]) == 2
        assert data["state_version"] == 2
        assert data["candidate_nodes"][0]["label"] == "V2"

    def test_save_rejected_on_confirmed_session(self, client: TestClient):
        session_id = _create_session(client)
        # Save working state with accepted node
        client.put(
            f"/persona/sessions/{session_id}/working-state",
            json={
                "candidate_nodes": [
                    {"node_id": "n1", "entity_type": "project", "label": "P", "status": "accepted_by_operator", "source_origin": "conversation"},
                ],
                "candidate_edges": [],
                "state_version": 1,
            },
        )
        # Confirm the session
        client.post(
            f"/persona/sessions/{session_id}/confirm",
            json={"accepted_node_ids": ["n1"]},
        )
        # Try to save again
        resp = client.put(
            f"/persona/sessions/{session_id}/working-state",
            json={"candidate_nodes": [], "candidate_edges": [], "state_version": 2},
        )
        assert resp.status_code == 409

    def test_save_rejected_on_abandoned_session(self, client: TestClient):
        session_id = _create_session(client)
        # Discard the session
        client.post(f"/persona/sessions/{session_id}/discard")
        # Try to save
        resp = client.put(
            f"/persona/sessions/{session_id}/working-state",
            json={"candidate_nodes": [], "candidate_edges": [], "state_version": 1},
        )
        assert resp.status_code == 409


class TestConfirmWorkingState:
    """Test the Confirm & Save batch commit.

    TEST:PersonaPage.StagedPersistence.ConfirmSaveCommitsAllEntities
    """

    def test_confirm_persists_accepted_project(self, client: TestClient):
        session_id = _create_session(client)
        client.put(
            f"/persona/sessions/{session_id}/working-state",
            json={
                "candidate_nodes": [
                    {"node_id": "p1", "entity_type": "project", "label": "New App", "subtitle": "Mobile app", "status": "accepted_by_operator", "source_origin": "conversation"},
                ],
                "candidate_edges": [],
                "state_version": 1,
            },
        )
        resp = client.post(
            f"/persona/sessions/{session_id}/confirm",
            json={"accepted_node_ids": ["p1"]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["persisted_count"] == 1
        assert data["session_status"] == "confirmed"
        assert data["persisted_entities"][0]["entity_type"] == "project"
        assert data["persisted_entities"][0]["label"] == "New App"

    def test_confirm_persists_multiple_entity_types(self, client: TestClient):
        session_id = _create_session(client)
        client.put(
            f"/persona/sessions/{session_id}/working-state",
            json={
                "candidate_nodes": [
                    {"node_id": "p1", "entity_type": "project", "label": "My Project", "status": "accepted_by_operator", "source_origin": "conversation"},
                    {"node_id": "s1", "entity_type": "stakeholder", "label": "Bob", "status": "accepted_by_operator", "source_origin": "conversation"},
                    {"node_id": "r1", "entity_type": "risk", "label": "Delay risk", "status": "accepted_by_operator", "source_origin": "conversation"},
                    {"node_id": "w1", "entity_type": "work_item", "label": "Build API", "status": "accepted_by_operator", "source_origin": "conversation"},
                    {"node_id": "d1", "entity_type": "decision", "label": "Use Python", "status": "accepted_by_operator", "source_origin": "conversation"},
                ],
                "candidate_edges": [],
                "state_version": 1,
            },
        )
        resp = client.post(
            f"/persona/sessions/{session_id}/confirm",
            json={"accepted_node_ids": ["p1", "s1", "r1", "w1", "d1"]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["persisted_count"] == 5
        types = {e["entity_type"] for e in data["persisted_entities"]}
        assert types == {"project", "stakeholder", "risk", "work_item", "decision"}

    def test_confirm_only_persists_accepted_ids(self, client: TestClient):
        """Only nodes listed in accepted_node_ids are persisted — pending and
        discarded nodes are excluded."""
        session_id = _create_session(client)
        client.put(
            f"/persona/sessions/{session_id}/working-state",
            json={
                "candidate_nodes": [
                    {"node_id": "p1", "entity_type": "project", "label": "Accepted", "status": "accepted_by_operator", "source_origin": "conversation"},
                    {"node_id": "p2", "entity_type": "project", "label": "Pending", "status": "pending", "source_origin": "conversation"},
                    {"node_id": "p3", "entity_type": "project", "label": "Discarded", "status": "discarded_by_operator", "source_origin": "conversation"},
                ],
                "candidate_edges": [],
                "state_version": 1,
            },
        )
        resp = client.post(
            f"/persona/sessions/{session_id}/confirm",
            json={"accepted_node_ids": ["p1"]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["persisted_count"] == 1
        assert data["persisted_entities"][0]["label"] == "Accepted"

    def test_confirm_transitions_session_to_confirmed(self, client: TestClient):
        session_id = _create_session(client)
        client.put(
            f"/persona/sessions/{session_id}/working-state",
            json={
                "candidate_nodes": [
                    {"node_id": "p1", "entity_type": "project", "label": "Parent Project", "status": "accepted_by_operator", "source_origin": "conversation"},
                    {"node_id": "n1", "entity_type": "blocker", "label": "B", "status": "accepted_by_operator", "source_origin": "conversation"},
                ],
                "candidate_edges": [],
                "state_version": 1,
            },
        )
        client.post(
            f"/persona/sessions/{session_id}/confirm",
            json={"accepted_node_ids": ["p1", "n1"]},
        )
        # Get session and verify status
        resp = client.get(f"/persona/sessions/{session_id}")
        assert resp.json()["session_status"] == "confirmed"

    def test_confirm_fails_without_working_state(self, client: TestClient):
        session_id = _create_session(client)
        resp = client.post(
            f"/persona/sessions/{session_id}/confirm",
            json={"accepted_node_ids": ["n1"]},
        )
        assert resp.status_code == 422

    def test_confirm_fails_with_no_accepted_nodes(self, client: TestClient):
        session_id = _create_session(client)
        client.put(
            f"/persona/sessions/{session_id}/working-state",
            json={
                "candidate_nodes": [
                    {"node_id": "n1", "entity_type": "project", "label": "P", "status": "pending", "source_origin": "conversation"},
                ],
                "candidate_edges": [],
                "state_version": 1,
            },
        )
        # Try to confirm with IDs that don't match saved nodes
        resp = client.post(
            f"/persona/sessions/{session_id}/confirm",
            json={"accepted_node_ids": ["nonexistent"]},
        )
        assert resp.status_code == 422

    def test_confirm_rejected_on_already_confirmed(self, client: TestClient):
        session_id = _create_session(client)
        client.put(
            f"/persona/sessions/{session_id}/working-state",
            json={
                "candidate_nodes": [
                    {"node_id": "n1", "entity_type": "project", "label": "P", "status": "accepted_by_operator", "source_origin": "conversation"},
                ],
                "candidate_edges": [],
                "state_version": 1,
            },
        )
        client.post(
            f"/persona/sessions/{session_id}/confirm",
            json={"accepted_node_ids": ["n1"]},
        )
        # Try to confirm again
        resp = client.post(
            f"/persona/sessions/{session_id}/confirm",
            json={"accepted_node_ids": ["n1"]},
        )
        assert resp.status_code == 409


class TestDiscardWorkingState:
    """Test the discard flow — nothing persisted.

    TEST:PersonaPage.StagedPersistence.DiscardDoesNotPersist
    """

    def test_discard_transitions_to_abandoned(self, client: TestClient):
        session_id = _create_session(client)
        client.put(
            f"/persona/sessions/{session_id}/working-state",
            json={
                "candidate_nodes": [
                    {"node_id": "n1", "entity_type": "project", "label": "P", "status": "pending", "source_origin": "conversation"},
                ],
                "candidate_edges": [],
                "state_version": 1,
            },
        )
        resp = client.post(f"/persona/sessions/{session_id}/discard")
        assert resp.status_code == 200
        data = resp.json()
        assert data["discarded"] is True
        assert data["session_status"] == "abandoned"

    def test_discard_deletes_working_state(self, client: TestClient):
        session_id = _create_session(client)
        client.put(
            f"/persona/sessions/{session_id}/working-state",
            json={
                "candidate_nodes": [
                    {"node_id": "n1", "entity_type": "project", "label": "P", "status": "pending", "source_origin": "conversation"},
                ],
                "candidate_edges": [],
                "state_version": 1,
            },
        )
        client.post(f"/persona/sessions/{session_id}/discard")
        # Working state should be gone
        resp = client.get(f"/persona/sessions/{session_id}/working-state")
        # Session is abandoned — get still works but returns empty
        assert resp.status_code == 200
        assert resp.json()["candidate_nodes"] == []

    def test_discard_without_working_state_still_works(self, client: TestClient):
        session_id = _create_session(client)
        resp = client.post(f"/persona/sessions/{session_id}/discard")
        assert resp.status_code == 200
        assert resp.json()["discarded"] is True

    def test_discard_rejected_on_already_confirmed(self, client: TestClient):
        session_id = _create_session(client)
        client.put(
            f"/persona/sessions/{session_id}/working-state",
            json={
                "candidate_nodes": [
                    {"node_id": "n1", "entity_type": "project", "label": "P", "status": "accepted_by_operator", "source_origin": "conversation"},
                ],
                "candidate_edges": [],
                "state_version": 1,
            },
        )
        client.post(
            f"/persona/sessions/{session_id}/confirm",
            json={"accepted_node_ids": ["n1"]},
        )
        resp = client.post(f"/persona/sessions/{session_id}/discard")
        assert resp.status_code == 409

    def test_discard_rejected_on_already_abandoned(self, client: TestClient):
        session_id = _create_session(client)
        client.post(f"/persona/sessions/{session_id}/discard")
        resp = client.post(f"/persona/sessions/{session_id}/discard")
        assert resp.status_code == 409


class TestWorkingStateEdgeCases:
    """Additional edge case tests for the working state flow."""

    def test_invalid_session_id_returns_404(self, client: TestClient):
        resp = client.get("/persona/sessions/not-a-uuid/working-state")
        assert resp.status_code == 404

    def test_confirm_with_blocker_and_milestone(self, client: TestClient):
        session_id = _create_session(client)
        client.put(
            f"/persona/sessions/{session_id}/working-state",
            json={
                "candidate_nodes": [
                    {"node_id": "p1", "entity_type": "project", "label": "Parent Project", "status": "accepted_by_operator", "source_origin": "conversation"},
                    {"node_id": "b1", "entity_type": "blocker", "label": "Design incomplete", "status": "accepted_by_operator", "source_origin": "conversation"},
                    {"node_id": "m1", "entity_type": "milestone", "label": "Beta launch", "subtitle": "June 2026", "status": "accepted_by_operator", "source_origin": "conversation"},
                ],
                "candidate_edges": [],
                "state_version": 1,
            },
        )
        resp = client.post(
            f"/persona/sessions/{session_id}/confirm",
            json={"accepted_node_ids": ["p1", "b1", "m1"]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["persisted_count"] == 3
        types = {e["entity_type"] for e in data["persisted_entities"]}
        assert "blocker" in types
        assert "milestone" in types
        assert "project" in types




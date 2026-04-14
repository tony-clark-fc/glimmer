"""API tests for voice session endpoints — WF1-WF5.

TEST:Voice.Session.BootstrapBindsCorrectOperatorAndSession (API)
TEST:Voice.Session.TranscriptBecomesStructuredSignal (API)
TEST:ChannelSession.SummariesPersistWithTraceableOrigin (API)
TEST:Voice.Session.SpokenBriefingIsBoundedAndRelevant (API)
"""

from __future__ import annotations

import pytest
from sqlalchemy import text

from app.db import get_session


# ── Fixtures ─────────────────────────────────────────────────────

_CLEANUP_TABLES = [
    "briefing_artifacts",
    "focus_packs",
    "imported_signals",
    "voice_session_states",
    "channel_sessions",
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


# ── Tests ────────────────────────────────────────────────────────


class TestVoiceSessionAPI:
    """Voice session lifecycle through the REST API."""

    def test_create_session(self, client) -> None:
        resp = client.post("/voice/sessions", json={})
        assert resp.status_code == 200
        data = resp.json()
        assert "session_id" in data
        assert "channel_session_id" in data
        assert data["status"] == "in_progress"

    def test_get_session(self, client) -> None:
        create_resp = client.post("/voice/sessions", json={})
        session_id = create_resp.json()["session_id"]

        resp = client.get(f"/voice/sessions/{session_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["session_id"] == session_id
        assert data["status"] == "in_progress"
        assert data["utterance_count"] == 0

    def test_get_nonexistent_session_returns_404(self, client) -> None:
        import uuid
        resp = client.get(f"/voice/sessions/{uuid.uuid4()}")
        assert resp.status_code == 404

    def test_submit_utterance(self, client) -> None:
        create_resp = client.post("/voice/sessions", json={})
        session_id = create_resp.json()["session_id"]

        resp = client.post(
            f"/voice/sessions/{session_id}/utterances",
            json={"text": "What's my top priority?"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["signal_id"] != ""
        assert data["route_target"] == "triage"
        assert data["auto_send_blocked"] is True

    def test_submit_utterance_to_nonexistent_session(self, client) -> None:
        import uuid
        resp = client.post(
            f"/voice/sessions/{uuid.uuid4()}/utterances",
            json={"text": "Hello"},
        )
        assert resp.status_code == 404

    def test_end_session(self, client) -> None:
        create_resp = client.post("/voice/sessions", json={})
        session_id = create_resp.json()["session_id"]

        # Submit an utterance first
        client.post(
            f"/voice/sessions/{session_id}/utterances",
            json={"text": "Let me review project Alpha"},
        )

        # End the session
        resp = client.post(f"/voice/sessions/{session_id}/end")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "completed"

    def test_end_session_creates_summary(self, client) -> None:
        create_resp = client.post("/voice/sessions", json={})
        session_id = create_resp.json()["session_id"]

        client.post(
            f"/voice/sessions/{session_id}/utterances",
            json={"text": "Check project deadlines"},
        )
        client.post(f"/voice/sessions/{session_id}/end")

        # Get session detail — should have summary
        resp = client.get(f"/voice/sessions/{session_id}")
        data = resp.json()
        assert data["status"] == "completed"
        assert data["summary"] is not None

    def test_utterance_to_completed_session_fails(self, client) -> None:
        create_resp = client.post("/voice/sessions", json={})
        session_id = create_resp.json()["session_id"]

        # End the session
        client.post(f"/voice/sessions/{session_id}/end")

        # Try to submit utterance — should fail
        resp = client.post(
            f"/voice/sessions/{session_id}/utterances",
            json={"text": "Too late"},
        )
        assert resp.status_code == 400

    def test_multiple_utterances_increment_count(self, client) -> None:
        create_resp = client.post("/voice/sessions", json={})
        session_id = create_resp.json()["session_id"]

        for text in ["First", "Second", "Third"]:
            client.post(
                f"/voice/sessions/{session_id}/utterances",
                json={"text": text},
            )

        resp = client.get(f"/voice/sessions/{session_id}")
        data = resp.json()
        assert data["utterance_count"] == 3

    def test_auto_send_always_blocked(self, client) -> None:
        """TEST:Drafting.NoAutoSend.BoundaryPreserved — voice channel."""
        create_resp = client.post("/voice/sessions", json={})
        session_id = create_resp.json()["session_id"]

        resp = client.post(
            f"/voice/sessions/{session_id}/utterances",
            json={"text": "Send a message to the team right now"},
        )
        data = resp.json()
        # Even explicit "send" requests must have auto_send_blocked
        assert data["auto_send_blocked"] is True


class TestSpokenBriefingAPI:
    """WF5 — Spoken briefing API tests.

    TEST:Voice.Session.SpokenBriefingIsBoundedAndRelevant (API)
    """

    def test_briefing_returns_empty_when_no_focus_pack(self, client) -> None:
        """Briefing endpoint returns graceful empty state."""
        create_resp = client.post("/voice/sessions", json={})
        session_id = create_resp.json()["session_id"]

        resp = client.post(f"/voice/sessions/{session_id}/briefing")
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_empty"] is True
        assert data["auto_send_blocked"] is True
        assert "briefing_text" in data

    def test_briefing_with_focus_pack_data(self, client) -> None:
        """Briefing with real focus pack returns meaningful content."""
        # Seed a focus pack via the database
        from app.db import get_session as _get_session
        from app.models.drafting import FocusPack

        session = _get_session()
        fp = FocusPack(
            top_actions={"items": [
                {"title": "Review Q2 forecast", "rationale": "Due Friday"},
                {"title": "Approve vendor contract", "rationale": "Overdue"},
            ]},
            high_risk_items={"items": [
                {"summary": "Supply chain delay", "severity": "high"},
            ]},
        )
        session.add(fp)
        session.commit()
        session.close()

        create_resp = client.post("/voice/sessions", json={})
        session_id = create_resp.json()["session_id"]

        resp = client.post(f"/voice/sessions/{session_id}/briefing")
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_empty"] is False
        assert data["auto_send_blocked"] is True
        assert data["section_count"] >= 2
        assert data["briefing_artifact_id"] is not None
        assert "Review Q2 forecast" in data["briefing_text"]

    def test_briefing_for_nonexistent_session_returns_404(self, client) -> None:
        import uuid
        resp = client.post(f"/voice/sessions/{uuid.uuid4()}/briefing")
        assert resp.status_code == 404

    def test_briefing_always_blocks_auto_send(self, client) -> None:
        """Briefing responses must always have auto_send_blocked."""
        create_resp = client.post("/voice/sessions", json={})
        session_id = create_resp.json()["session_id"]

        resp = client.post(f"/voice/sessions/{session_id}/briefing")
        data = resp.json()
        assert data["auto_send_blocked"] is True

    def test_context_endpoint_returns_session_state(self, client) -> None:
        """GET /voice/sessions/{id}/context returns session orientation."""
        create_resp = client.post("/voice/sessions", json={})
        session_id = create_resp.json()["session_id"]

        # Submit some utterances to build state
        client.post(
            f"/voice/sessions/{session_id}/utterances",
            json={"text": "Let's talk about project deadlines"},
        )

        resp = client.get(f"/voice/sessions/{session_id}/context")
        assert resp.status_code == 200
        data = resp.json()
        assert "context_text" in data
        assert data["auto_send_blocked"] is True

    def test_context_for_nonexistent_session_returns_404(self, client) -> None:
        import uuid
        resp = client.get(f"/voice/sessions/{uuid.uuid4()}/context")
        assert resp.status_code == 404


class TestVoiceHandoffAPI:
    """WF7/WF8 — Voice handoff API tests.

    TEST:Voice.Session.HandoffCreatesWorkspaceVisibleContinuation (API)
    TEST:Security.NoAutoSend.GlobalBoundaryPreserved (API — voice handoff)
    """

    def test_handoff_creates_record(self, client) -> None:
        create_resp = client.post("/voice/sessions", json={})
        session_id = create_resp.json()["session_id"]

        resp = client.post(f"/voice/sessions/{session_id}/handoff")
        assert resp.status_code == 200
        data = resp.json()
        assert data["source_channel"] == "voice"
        assert data["auto_send_blocked"] is True
        assert "handoff_id" in data
        assert data["workspace_target"] == "/review"

    def test_handoff_for_nonexistent_session_returns_404(self, client) -> None:
        import uuid
        resp = client.post(f"/voice/sessions/{uuid.uuid4()}/handoff")
        assert resp.status_code == 404

    def test_handoff_always_blocks_auto_send(self, client) -> None:
        create_resp = client.post("/voice/sessions", json={})
        session_id = create_resp.json()["session_id"]

        resp = client.post(f"/voice/sessions/{session_id}/handoff")
        data = resp.json()
        assert data["auto_send_blocked"] is True

    def test_handoff_preserves_channel_session_id(self, client) -> None:
        create_resp = client.post("/voice/sessions", json={})
        channel_session_id = create_resp.json()["channel_session_id"]
        session_id = create_resp.json()["session_id"]

        resp = client.post(f"/voice/sessions/{session_id}/handoff")
        data = resp.json()
        assert data["channel_session_id"] == channel_session_id


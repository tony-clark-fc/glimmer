"""Persona page conversation session API tests.

PLAN:WorkstreamE.PackageE12.PersonaPageConversationUi
TEST:PersonaPage.Conversation.ChatRendersAndAcceptsInput
TEST:PersonaPage.Conversation.SessionLifecycleManaged

Tests:
- Session creation returns 201 with correct structure
- Get session returns session with message history
- Send message returns Glimmer reply
- Session lifecycle transitions work correctly
- Invalid session IDs return 404
- Terminal sessions cannot accept messages
- Empty messages are rejected
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import text

from app.db import get_session


# ── Fixtures ─────────────────────────────────────────────────────

_CLEANUP_TABLES = [
    "persona_page_messages",
    "persona_page_sessions",
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


# ── Mock for persona_chat_smart ───────────────────────────────────

def _mock_chat_result():
    """Create a mock SmartConversationResult."""
    from app.inference.orchestration import SmartConversationResult
    return SmartConversationResult(
        used_llm=False,
        fallback_reason="test mock",
        reply_content="This is a test response from Glimmer.",
        inference_latency_ms=0.0,
        model="mock",
    )


# ── Session Creation ──────────────────────────────────────────────

class TestCreateSession:
    def test_create_session_returns_201(self, client):
        resp = client.post("/persona/sessions", json={"workspace_mode": "idea"})
        assert resp.status_code == 201
        data = resp.json()
        assert "id" in data
        assert data["session_status"] == "active"
        assert data["workspace_mode"] == "idea"
        assert data["messages"] == []

    def test_create_session_default_mode(self, client):
        resp = client.post("/persona/sessions", json={})
        assert resp.status_code == 201
        data = resp.json()
        assert data["workspace_mode"] == "update"

    def test_create_session_has_timestamps(self, client):
        resp = client.post("/persona/sessions", json={})
        data = resp.json()
        assert data["created_at"]
        assert data["updated_at"]


# ── Get Session ───────────────────────────────────────────────────

class TestGetSession:
    def test_get_session_returns_session(self, client):
        create_resp = client.post("/persona/sessions", json={"workspace_mode": "plan"})
        session_id = create_resp.json()["id"]

        resp = client.get(f"/persona/sessions/{session_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == session_id
        assert data["session_status"] == "active"
        assert data["workspace_mode"] == "plan"

    def test_get_nonexistent_session_404(self, client):
        fake_id = str(uuid.uuid4())
        resp = client.get(f"/persona/sessions/{fake_id}")
        assert resp.status_code == 404

    def test_get_invalid_uuid_404(self, client):
        resp = client.get("/persona/sessions/not-a-uuid")
        assert resp.status_code == 404


# ── Send Message ──────────────────────────────────────────────────

class TestSendMessage:
    @patch(
        "app.inference.orchestration.persona_chat_smart",
        new_callable=AsyncMock,
    )
    def test_send_message_returns_reply(self, mock_chat, client):
        mock_chat.return_value = _mock_chat_result()

        create_resp = client.post("/persona/sessions", json={})
        session_id = create_resp.json()["id"]

        resp = client.post(
            f"/persona/sessions/{session_id}/messages",
            json={"content": "Hello Glimmer!"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["role"] == "glimmer"
        assert data["content"] == "This is a test response from Glimmer."
        assert data["ordering"] == 2  # user message is 1, glimmer is 2

    @patch(
        "app.inference.orchestration.persona_chat_smart",
        new_callable=AsyncMock,
    )
    def test_send_message_persists_history(self, mock_chat, client):
        mock_chat.return_value = _mock_chat_result()

        create_resp = client.post("/persona/sessions", json={})
        session_id = create_resp.json()["id"]

        client.post(
            f"/persona/sessions/{session_id}/messages",
            json={"content": "First message"},
        )

        # Get session — should have 2 messages (user + glimmer)
        resp = client.get(f"/persona/sessions/{session_id}")
        messages = resp.json()["messages"]
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "First message"
        assert messages[1]["role"] == "glimmer"

    @patch(
        "app.inference.orchestration.persona_chat_smart",
        new_callable=AsyncMock,
    )
    def test_send_message_includes_inference_metadata(self, mock_chat, client):
        mock_chat.return_value = _mock_chat_result()

        create_resp = client.post("/persona/sessions", json={})
        session_id = create_resp.json()["id"]

        resp = client.post(
            f"/persona/sessions/{session_id}/messages",
            json={"content": "Test"},
        )
        data = resp.json()
        assert data["inference_metadata"] is not None
        assert data["inference_metadata"]["used_llm"] is False
        assert data["inference_metadata"]["fallback_reason"] == "test mock"

    def test_send_message_empty_rejected(self, client):
        create_resp = client.post("/persona/sessions", json={})
        session_id = create_resp.json()["id"]

        resp = client.post(
            f"/persona/sessions/{session_id}/messages",
            json={"content": "   "},
        )
        assert resp.status_code == 422

    def test_send_message_nonexistent_session_404(self, client):
        fake_id = str(uuid.uuid4())
        resp = client.post(
            f"/persona/sessions/{fake_id}/messages",
            json={"content": "Hello"},
        )
        assert resp.status_code == 404

    @patch(
        "app.inference.orchestration.persona_chat_smart",
        new_callable=AsyncMock,
    )
    def test_send_message_updates_workspace_mode(self, mock_chat, client):
        mock_chat.return_value = _mock_chat_result()

        create_resp = client.post("/persona/sessions", json={"workspace_mode": "update"})
        session_id = create_resp.json()["id"]

        client.post(
            f"/persona/sessions/{session_id}/messages",
            json={"content": "Switch to idea mode", "workspace_mode": "idea"},
        )

        resp = client.get(f"/persona/sessions/{session_id}")
        assert resp.json()["workspace_mode"] == "idea"


# ── Session Lifecycle ─────────────────────────────────────────────

class TestSessionLifecycle:
    def test_pause_active_session(self, client):
        create_resp = client.post("/persona/sessions", json={})
        session_id = create_resp.json()["id"]

        resp = client.patch(
            f"/persona/sessions/{session_id}",
            json={"session_status": "paused"},
        )
        assert resp.status_code == 200
        assert resp.json()["session_status"] == "paused"

    def test_resume_paused_session(self, client):
        create_resp = client.post("/persona/sessions", json={})
        session_id = create_resp.json()["id"]

        client.patch(
            f"/persona/sessions/{session_id}",
            json={"session_status": "paused"},
        )
        resp = client.patch(
            f"/persona/sessions/{session_id}",
            json={"session_status": "active"},
        )
        assert resp.status_code == 200
        assert resp.json()["session_status"] == "active"

    def test_confirm_active_session(self, client):
        create_resp = client.post("/persona/sessions", json={})
        session_id = create_resp.json()["id"]

        resp = client.patch(
            f"/persona/sessions/{session_id}",
            json={"session_status": "confirmed"},
        )
        assert resp.status_code == 200
        assert resp.json()["session_status"] == "confirmed"

    def test_abandon_active_session(self, client):
        create_resp = client.post("/persona/sessions", json={})
        session_id = create_resp.json()["id"]

        resp = client.patch(
            f"/persona/sessions/{session_id}",
            json={"session_status": "abandoned"},
        )
        assert resp.status_code == 200
        assert resp.json()["session_status"] == "abandoned"

    def test_confirmed_is_terminal(self, client):
        create_resp = client.post("/persona/sessions", json={})
        session_id = create_resp.json()["id"]

        client.patch(
            f"/persona/sessions/{session_id}",
            json={"session_status": "confirmed"},
        )
        resp = client.patch(
            f"/persona/sessions/{session_id}",
            json={"session_status": "active"},
        )
        assert resp.status_code == 409

    def test_abandoned_is_terminal(self, client):
        create_resp = client.post("/persona/sessions", json={})
        session_id = create_resp.json()["id"]

        client.patch(
            f"/persona/sessions/{session_id}",
            json={"session_status": "abandoned"},
        )
        resp = client.patch(
            f"/persona/sessions/{session_id}",
            json={"session_status": "active"},
        )
        assert resp.status_code == 409

    @patch(
        "app.inference.orchestration.persona_chat_smart",
        new_callable=AsyncMock,
    )
    def test_confirmed_session_rejects_messages(self, mock_chat, client):
        mock_chat.return_value = _mock_chat_result()

        create_resp = client.post("/persona/sessions", json={})
        session_id = create_resp.json()["id"]

        client.patch(
            f"/persona/sessions/{session_id}",
            json={"session_status": "confirmed"},
        )
        resp = client.post(
            f"/persona/sessions/{session_id}/messages",
            json={"content": "Hello"},
        )
        assert resp.status_code == 409

    @patch(
        "app.inference.orchestration.persona_chat_smart",
        new_callable=AsyncMock,
    )
    def test_paused_session_accepts_message_and_reactivates(self, mock_chat, client):
        mock_chat.return_value = _mock_chat_result()

        create_resp = client.post("/persona/sessions", json={})
        session_id = create_resp.json()["id"]

        client.patch(
            f"/persona/sessions/{session_id}",
            json={"session_status": "paused"},
        )

        resp = client.post(
            f"/persona/sessions/{session_id}/messages",
            json={"content": "I'm back"},
        )
        assert resp.status_code == 200

        # Session should now be active again
        session = client.get(f"/persona/sessions/{session_id}")
        assert session.json()["session_status"] == "active"

    def test_invalid_status_rejected(self, client):
        create_resp = client.post("/persona/sessions", json={})
        session_id = create_resp.json()["id"]

        resp = client.patch(
            f"/persona/sessions/{session_id}",
            json={"session_status": "invalid_status"},
        )
        assert resp.status_code == 422

    def test_update_nonexistent_session_404(self, client):
        fake_id = str(uuid.uuid4())
        resp = client.patch(
            f"/persona/sessions/{fake_id}",
            json={"session_status": "paused"},
        )
        assert resp.status_code == 404


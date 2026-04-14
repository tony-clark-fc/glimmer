"""API tests for Telegram companion endpoints — WF6.

TEST:Telegram.Companion.WhatMattersNowReturnsBoundedSummary (API)
TEST:Telegram.Companion.HandoffToWorkspaceOccursWhenNeeded (API)
TEST:Security.NoAutoSend.GlobalBoundaryPreserved (API — Telegram)
"""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import text

from app.db import get_session


# ── Fixtures ─────────────────────────────────────────────────────

_CLEANUP_TABLES = [
    "briefing_artifacts",
    "focus_packs",
    "imported_signals",
    "telegram_conversation_states",
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


class TestTelegramSessionAPI:
    """Telegram session lifecycle through the REST API."""

    def test_create_session(self, client) -> None:
        resp = client.post(
            "/telegram/sessions",
            json={"telegram_chat_id": "12345"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["telegram_chat_id"] == "12345"
        assert "session_id" in data
        assert "channel_session_id" in data
        assert data["message_count"] == 0

    def test_get_session(self, client) -> None:
        create_resp = client.post(
            "/telegram/sessions",
            json={"telegram_chat_id": "12345"},
        )
        session_id = create_resp.json()["session_id"]

        resp = client.get(f"/telegram/sessions/{session_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["session_id"] == session_id
        assert data["telegram_chat_id"] == "12345"

    def test_get_nonexistent_session_returns_404(self, client) -> None:
        resp = client.get(f"/telegram/sessions/{uuid.uuid4()}")
        assert resp.status_code == 404

    def test_reuse_existing_session(self, client) -> None:
        resp1 = client.post(
            "/telegram/sessions",
            json={"telegram_chat_id": "77777"},
        )
        resp2 = client.post(
            "/telegram/sessions",
            json={"telegram_chat_id": "77777"},
        )
        assert resp1.json()["session_id"] == resp2.json()["session_id"]


class TestTelegramMessageAPI:
    """Telegram message processing through the REST API."""

    def test_process_message(self, client) -> None:
        create_resp = client.post(
            "/telegram/sessions",
            json={"telegram_chat_id": "12345"},
        )
        session_id = create_resp.json()["session_id"]

        resp = client.post(
            f"/telegram/sessions/{session_id}/messages",
            json={"text": "What's my top priority?"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["signal_id"] is not None
        assert data["route_target"] == "triage"
        assert data["auto_send_blocked"] is True
        assert data["handoff_needed"] is False

    def test_message_triggers_handoff(self, client) -> None:
        """TEST:Telegram.Companion.HandoffToWorkspaceOccursWhenNeeded"""
        create_resp = client.post(
            "/telegram/sessions",
            json={"telegram_chat_id": "12345"},
        )
        session_id = create_resp.json()["session_id"]

        resp = client.post(
            f"/telegram/sessions/{session_id}/messages",
            json={"text": "I need to review the draft in detail"},
        )
        data = resp.json()
        assert data["handoff_needed"] is True
        assert data["handoff_url"] is not None
        assert "/review" in data["handoff_url"]
        assert data["auto_send_blocked"] is True

    def test_message_to_nonexistent_session_returns_404(self, client) -> None:
        resp = client.post(
            f"/telegram/sessions/{uuid.uuid4()}/messages",
            json={"text": "Hello"},
        )
        assert resp.status_code == 404

    def test_auto_send_always_blocked(self, client) -> None:
        """TEST:Security.NoAutoSend.GlobalBoundaryPreserved — Telegram API."""
        create_resp = client.post(
            "/telegram/sessions",
            json={"telegram_chat_id": "12345"},
        )
        session_id = create_resp.json()["session_id"]

        resp = client.post(
            f"/telegram/sessions/{session_id}/messages",
            json={"text": "Send the team an update right now"},
        )
        data = resp.json()
        assert data["auto_send_blocked"] is True


class TestTelegramWhatMattersNowAPI:
    """What Matters Now summary through the REST API."""

    def test_what_matters_now_empty(self, client) -> None:
        create_resp = client.post(
            "/telegram/sessions",
            json={"telegram_chat_id": "12345"},
        )
        session_id = create_resp.json()["session_id"]

        resp = client.post(
            f"/telegram/sessions/{session_id}/what-matters-now"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_empty"] is True
        assert data["auto_send_blocked"] is True

    def test_what_matters_now_with_data(self, client) -> None:
        """TEST:Telegram.Companion.WhatMattersNowReturnsBoundedSummary"""
        from app.db import get_session as _get_session
        from app.models.drafting import FocusPack

        session = _get_session()
        fp = FocusPack(
            top_actions={"items": [
                {"title": "Review Q2 forecast", "rationale": "Due Friday"},
            ]},
        )
        session.add(fp)
        session.commit()
        session.close()

        create_resp = client.post(
            "/telegram/sessions",
            json={"telegram_chat_id": "12345"},
        )
        session_id = create_resp.json()["session_id"]

        resp = client.post(
            f"/telegram/sessions/{session_id}/what-matters-now"
        )
        data = resp.json()
        assert data["is_empty"] is False
        assert data["auto_send_blocked"] is True
        assert "Review Q2 forecast" in data["summary_text"]

    def test_what_matters_now_nonexistent_returns_404(self, client) -> None:
        resp = client.post(
            f"/telegram/sessions/{uuid.uuid4()}/what-matters-now"
        )
        assert resp.status_code == 404


class TestTelegramHandoffAPI:
    """WF7/WF8 — Telegram handoff API tests.

    TEST:Telegram.Companion.HandoffToWorkspaceOccursWhenNeeded (API)
    TEST:Security.NoAutoSend.GlobalBoundaryPreserved (API — Telegram handoff)
    """

    def test_handoff_creates_record(self, client) -> None:
        create_resp = client.post(
            "/telegram/sessions",
            json={"telegram_chat_id": "api-handoff-1"},
        )
        session_id = create_resp.json()["session_id"]

        resp = client.post(f"/telegram/sessions/{session_id}/handoff")
        assert resp.status_code == 200
        data = resp.json()
        assert data["source_channel"] == "telegram"
        assert data["auto_send_blocked"] is True
        assert "handoff_id" in data
        assert data["workspace_target"] == "/review"

    def test_handoff_for_nonexistent_session_returns_404(self, client) -> None:
        resp = client.post(
            f"/telegram/sessions/{uuid.uuid4()}/handoff"
        )
        assert resp.status_code == 404

    def test_handoff_always_blocks_auto_send(self, client) -> None:
        create_resp = client.post(
            "/telegram/sessions",
            json={"telegram_chat_id": "api-handoff-2"},
        )
        session_id = create_resp.json()["session_id"]

        resp = client.post(f"/telegram/sessions/{session_id}/handoff")
        data = resp.json()
        assert data["auto_send_blocked"] is True


class TestPendingHandoffsAPI:
    """WF7 — Pending handoffs retrieval through the REST API.

    TEST:Telegram.Companion.ReviewNeededStateSurfacesInWorkspace (API)
    """

    def test_pending_handoffs_empty(self, client) -> None:
        resp = client.get("/telegram/handoffs/pending")
        assert resp.status_code == 200
        data = resp.json()
        assert data == []

    def test_pending_handoffs_after_voice_handoff(self, client) -> None:
        create_resp = client.post("/voice/sessions", json={})
        session_id = create_resp.json()["session_id"]
        client.post(f"/voice/sessions/{session_id}/handoff")

        resp = client.get("/telegram/handoffs/pending")
        data = resp.json()
        assert len(data) == 1
        assert data[0]["source_channel"] == "voice"
        assert data[0]["auto_send_blocked"] is True

    def test_pending_handoffs_after_telegram_handoff(self, client) -> None:
        create_resp = client.post(
            "/telegram/sessions",
            json={"telegram_chat_id": "api-pending-1"},
        )
        session_id = create_resp.json()["session_id"]
        client.post(f"/telegram/sessions/{session_id}/handoff")

        resp = client.get("/telegram/handoffs/pending")
        data = resp.json()
        assert len(data) == 1
        assert data[0]["source_channel"] == "telegram"

    def test_pending_handoffs_mixed_channels(self, client) -> None:
        v_resp = client.post("/voice/sessions", json={})
        v_id = v_resp.json()["session_id"]
        client.post(f"/voice/sessions/{v_id}/handoff")

        t_resp = client.post(
            "/telegram/sessions",
            json={"telegram_chat_id": "api-pending-2"},
        )
        t_id = t_resp.json()["session_id"]
        client.post(f"/telegram/sessions/{t_id}/handoff")

        resp = client.get("/telegram/handoffs/pending")
        data = resp.json()
        assert len(data) == 2
        channels = {r["source_channel"] for r in data}
        assert channels == {"voice", "telegram"}
        for r in data:
            assert r["auto_send_blocked"] is True


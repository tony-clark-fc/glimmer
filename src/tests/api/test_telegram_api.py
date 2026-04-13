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


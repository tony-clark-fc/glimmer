"""Telegram companion integration tests — WF6.

TEST:Telegram.Companion.WhatMattersNowReturnsBoundedSummary
TEST:Telegram.Companion.HandoffToWorkspaceOccursWhenNeeded
TEST:VoiceAndTelegram.SharedCoreFlowParityPreserved
TEST:Security.NoAutoSend.GlobalBoundaryPreserved

Proves that Telegram companion interaction is:
- bounded (not a second control room)
- review-safe (auto_send_blocked, handoff when needed)
- grounded in shared core (routes through IntakeGraph)
- session-aware (ChannelSession + TelegramConversationState)
"""

from __future__ import annotations

import uuid

from app.models.channel import ChannelSession, TelegramConversationState
from app.models.source import ImportedSignal
from app.models.drafting import FocusPack
from app.services.telegram import (
    bootstrap_telegram_session,
    normalize_telegram_message,
    update_telegram_context,
    generate_what_matters_now,
    detect_handoff_needed,
    generate_handoff_response,
    route_telegram_to_core,
    MAX_TELEGRAM_RESPONSE_LENGTH,
)


# ── Session Bootstrap Tests ──────────────────────────────────────


class TestTelegramSessionBootstrap:
    """TEST:Telegram.Companion.WhatMattersNowReturnsBoundedSummary — session foundation."""

    def test_bootstrap_creates_channel_session(self, db_session) -> None:
        cs, ts = bootstrap_telegram_session(
            db_session, telegram_chat_id="12345"
        )
        assert cs is not None
        assert cs.channel_type == "telegram"
        assert cs.session_state == "active"
        assert cs.channel_identity == "telegram_12345"

    def test_bootstrap_creates_telegram_state(self, db_session) -> None:
        cs, ts = bootstrap_telegram_session(
            db_session, telegram_chat_id="12345"
        )
        assert ts is not None
        assert ts.telegram_chat_id == "12345"
        assert ts.channel_session_id == cs.id

    def test_bootstrap_binds_operator(self, db_session) -> None:
        from app.models.operator import PrimaryOperator

        op = PrimaryOperator(display_name="Test Operator")
        db_session.add(op)
        db_session.flush()

        cs, ts = bootstrap_telegram_session(
            db_session, telegram_chat_id="12345", operator_id=op.id
        )
        assert cs.operator_id == op.id

    def test_bootstrap_reuses_existing_active_session(self, db_session) -> None:
        cs1, ts1 = bootstrap_telegram_session(
            db_session, telegram_chat_id="99999"
        )
        cs2, ts2 = bootstrap_telegram_session(
            db_session, telegram_chat_id="99999"
        )
        assert ts1.id == ts2.id
        assert cs1.id == cs2.id

    def test_bootstrap_initializes_state_data(self, db_session) -> None:
        cs, ts = bootstrap_telegram_session(
            db_session, telegram_chat_id="12345"
        )
        assert ts.state_data is not None
        assert ts.state_data["message_count"] == 0
        assert ts.state_data["topics_discussed"] == []


# ── Message Normalization Tests ──────────────────────────────────


class TestTelegramMessageNormalization:
    """TEST:Telegram.Companion.WhatMattersNowReturnsBoundedSummary — signal creation."""

    def test_message_creates_imported_signal(self, db_session) -> None:
        cs, ts = bootstrap_telegram_session(
            db_session, telegram_chat_id="12345"
        )
        signal_id = normalize_telegram_message(
            db_session,
            channel_session_id=cs.id,
            telegram_chat_id="12345",
            text="What matters today?",
        )
        assert signal_id is not None
        signal = db_session.get(ImportedSignal, signal_id)
        assert signal is not None
        assert signal.signal_type == "telegram_import"
        assert signal.content == "What matters today?"

    def test_signal_has_telegram_provenance(self, db_session) -> None:
        cs, ts = bootstrap_telegram_session(
            db_session, telegram_chat_id="12345"
        )
        signal_id = normalize_telegram_message(
            db_session,
            channel_session_id=cs.id,
            telegram_chat_id="12345",
            text="Check project status",
            telegram_message_id="msg_42",
        )
        signal = db_session.get(ImportedSignal, signal_id)
        assert signal.raw_metadata["telegram_chat_id"] == "12345"
        assert signal.raw_metadata["telegram_message_id"] == "msg_42"
        assert signal.raw_metadata["provider"] == "telegram"
        assert signal.source_label == "telegram:12345"

    def test_empty_message_returns_none(self, db_session) -> None:
        cs, ts = bootstrap_telegram_session(
            db_session, telegram_chat_id="12345"
        )
        signal_id = normalize_telegram_message(
            db_session,
            channel_session_id=cs.id,
            telegram_chat_id="12345",
            text="   ",
        )
        assert signal_id is None


# ── Session Context Update Tests ─────────────────────────────────


class TestTelegramContextUpdate:
    """TEST:Telegram.Companion.WhatMattersNowReturnsBoundedSummary — session state."""

    def test_update_increments_message_count(self, db_session) -> None:
        cs, ts = bootstrap_telegram_session(
            db_session, telegram_chat_id="12345"
        )
        update_telegram_context(
            db_session, telegram_state_id=ts.id, message_text="Hello"
        )
        assert ts.state_data["message_count"] == 1

        update_telegram_context(
            db_session, telegram_state_id=ts.id, message_text="Again"
        )
        assert ts.state_data["message_count"] == 2

    def test_update_sets_topic(self, db_session) -> None:
        cs, ts = bootstrap_telegram_session(
            db_session, telegram_chat_id="12345"
        )
        update_telegram_context(
            db_session, telegram_state_id=ts.id, current_topic="deadlines"
        )
        assert ts.current_topic == "deadlines"
        assert "deadlines" in ts.state_data["topics_discussed"]

    def test_topics_are_bounded(self, db_session) -> None:
        cs, ts = bootstrap_telegram_session(
            db_session, telegram_chat_id="12345"
        )
        for i in range(10):
            update_telegram_context(
                db_session,
                telegram_state_id=ts.id,
                current_topic=f"topic_{i}",
            )
        assert len(ts.state_data["topics_discussed"]) <= 5

    def test_nonexistent_state_raises(self, db_session) -> None:
        import pytest
        with pytest.raises(ValueError):
            update_telegram_context(
                db_session,
                telegram_state_id=uuid.uuid4(),
            )


# ── "What Matters Now" Tests ─────────────────────────────────────


class TestWhatMattersNow:
    """TEST:Telegram.Companion.WhatMattersNowReturnsBoundedSummary"""

    def test_returns_empty_when_no_focus_pack(self, db_session) -> None:
        result = generate_what_matters_now(db_session)
        assert result["is_empty"] is True
        assert result["auto_send_blocked"] is True
        assert len(result["summary_text"]) > 0

    def test_returns_bounded_summary_with_data(self, db_session) -> None:
        fp = FocusPack(
            top_actions={"items": [
                {"title": "Review contracts", "rationale": "Due tomorrow"},
            ]},
        )
        db_session.add(fp)
        db_session.flush()

        result = generate_what_matters_now(db_session)
        assert result["is_empty"] is False
        assert result["auto_send_blocked"] is True
        assert len(result["summary_text"]) <= MAX_TELEGRAM_RESPONSE_LENGTH
        assert "Review contracts" in result["summary_text"]

    def test_summary_is_shorter_than_voice_briefing(self, db_session) -> None:
        """Telegram responses should be more concise than voice briefings."""
        from app.services.briefing import MAX_BRIEFING_LENGTH

        assert MAX_TELEGRAM_RESPONSE_LENGTH < MAX_BRIEFING_LENGTH


# ── Handoff Detection Tests ──────────────────────────────────────


class TestHandoffDetection:
    """TEST:Telegram.Companion.HandoffToWorkspaceOccursWhenNeeded"""

    def test_detects_review_trigger(self) -> None:
        needed, reason = detect_handoff_needed("I need to review the draft")
        assert needed is True
        assert "review" in reason.lower()

    def test_detects_approve_trigger(self) -> None:
        needed, reason = detect_handoff_needed("Can I approve this action?")
        assert needed is True

    def test_detects_compare_trigger(self) -> None:
        needed, reason = detect_handoff_needed("Compare the two drafts")
        assert needed is True

    def test_no_handoff_for_simple_query(self) -> None:
        needed, reason = detect_handoff_needed("What matters today?")
        assert needed is False
        assert reason == ""

    def test_no_handoff_for_note_capture(self) -> None:
        needed, reason = detect_handoff_needed("Note: call supplier tomorrow")
        assert needed is False

    def test_handoff_response_includes_workspace_url(self) -> None:
        result = generate_handoff_response(
            reason="Review needed",
            channel_session_id=uuid.uuid4(),
        )
        assert result["handoff_needed"] is True
        assert "/review" in result["workspace_url"]
        assert result["auto_send_blocked"] is True


# ── Telegram-to-Core Routing Tests ───────────────────────────────


class TestTelegramRouting:
    """TEST:VoiceAndTelegram.SharedCoreFlowParityPreserved — Telegram path."""

    def test_telegram_routes_through_intake_graph(self, db_session) -> None:
        cs, ts = bootstrap_telegram_session(
            db_session, telegram_chat_id="12345"
        )
        signal_id = normalize_telegram_message(
            db_session,
            channel_session_id=cs.id,
            telegram_chat_id="12345",
            text="What needs my attention?",
        )

        result = route_telegram_to_core(
            signal_id=signal_id,
            channel_session_id=cs.id,
        )
        assert result["route_target"] == "triage"
        assert result["auto_send_blocked"] is True

    def test_telegram_routing_always_blocks_auto_send(self, db_session) -> None:
        """TEST:Security.NoAutoSend.GlobalBoundaryPreserved — Telegram channel."""
        cs, ts = bootstrap_telegram_session(
            db_session, telegram_chat_id="12345"
        )
        signal_id = normalize_telegram_message(
            db_session,
            channel_session_id=cs.id,
            telegram_chat_id="12345",
            text="Send an update to the team now",
        )

        result = route_telegram_to_core(
            signal_id=signal_id,
            channel_session_id=cs.id,
        )
        # Even explicit "send" requests must not bypass auto_send_blocked
        assert result["auto_send_blocked"] is True



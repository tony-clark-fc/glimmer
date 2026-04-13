"""Cross-surface handoff and safety parity tests — WF7/WF8.

TEST:Voice.Session.HandoffCreatesWorkspaceVisibleContinuation
TEST:Telegram.Companion.HandoffToWorkspaceOccursWhenNeeded
TEST:Telegram.Companion.ReviewNeededStateSurfacesInWorkspace
TEST:Security.NoAutoSend.GlobalBoundaryPreserved
TEST:Security.ReviewGate.ExternalImpactRequiresApproval
TEST:VoiceAndTelegram.SharedCoreFlowParityPreserved

Proves:
- Voice and Telegram handoffs create workspace-visible artifacts
- Handoffs preserve context and provenance
- auto_send_blocked is enforced across all channels
- Review gates are never silently bypassed
"""

from __future__ import annotations

import uuid

from app.models.channel import ChannelSession, TelegramConversationState
from app.models.drafting import BriefingArtifact
from app.services.voice import bootstrap_voice_session
from app.services.telegram import bootstrap_telegram_session
from app.services.handoff import (
    create_handoff_from_voice,
    create_handoff_from_telegram,
    get_pending_handoffs,
    verify_auto_send_blocked,
    verify_review_gate_preserved,
    HandoffRecord,
)


# ── Voice Handoff Tests ──────────────────────────────────────────


class TestVoiceHandoff:
    """TEST:Voice.Session.HandoffCreatesWorkspaceVisibleContinuation"""

    def test_handoff_creates_artifact(self, db_session) -> None:
        cs, vs = bootstrap_voice_session(db_session)
        handoff = create_handoff_from_voice(
            db_session,
            channel_session_id=cs.id,
            reason="Needs workspace review",
        )
        assert handoff.handoff_id is not None
        assert handoff.source_channel == "voice"
        assert handoff.auto_send_blocked is True

        artifact = db_session.get(BriefingArtifact, handoff.handoff_id)
        assert artifact is not None
        assert artifact.briefing_type == "channel_handoff"
        assert "voice" in artifact.content.lower()

    def test_handoff_preserves_context(self, db_session) -> None:
        cs, vs = bootstrap_voice_session(db_session)
        handoff = create_handoff_from_voice(
            db_session,
            channel_session_id=cs.id,
            reason="Complex review",
            current_topic="budget analysis",
            unresolved_prompts=["What about Q3?", "Compare to last year"],
            referenced_project_ids=["proj-1", "proj-2"],
        )
        assert "budget analysis" in handoff.context_summary
        assert len(handoff.pending_items) == 2
        assert handoff.workspace_target == "/review"

    def test_handoff_updates_channel_session(self, db_session) -> None:
        cs, vs = bootstrap_voice_session(db_session)
        handoff = create_handoff_from_voice(
            db_session,
            channel_session_id=cs.id,
            reason="Needs review",
        )
        db_session.refresh(cs)
        assert cs.session_metadata.get("handoff_created") is True
        assert cs.session_metadata.get("handoff_artifact_id") == str(handoff.handoff_id)

    def test_handoff_to_dict_serializable(self, db_session) -> None:
        cs, vs = bootstrap_voice_session(db_session)
        handoff = create_handoff_from_voice(
            db_session,
            channel_session_id=cs.id,
            reason="Test",
        )
        d = handoff.to_dict()
        assert d["source_channel"] == "voice"
        assert d["auto_send_blocked"] is True
        assert "handoff_id" in d


# ── Telegram Handoff Tests ───────────────────────────────────────


class TestTelegramHandoff:
    """TEST:Telegram.Companion.HandoffToWorkspaceOccursWhenNeeded"""

    def test_telegram_handoff_creates_artifact(self, db_session) -> None:
        cs, ts = bootstrap_telegram_session(
            db_session, telegram_chat_id="54321"
        )
        handoff = create_handoff_from_telegram(
            db_session,
            channel_session_id=cs.id,
            telegram_chat_id="54321",
            reason="Review required",
        )
        assert handoff.handoff_id is not None
        assert handoff.source_channel == "telegram"

        artifact = db_session.get(BriefingArtifact, handoff.handoff_id)
        assert artifact is not None
        assert artifact.briefing_type == "channel_handoff"
        assert "54321" in artifact.content

    def test_telegram_handoff_preserves_context(self, db_session) -> None:
        cs, ts = bootstrap_telegram_session(
            db_session, telegram_chat_id="54321"
        )
        handoff = create_handoff_from_telegram(
            db_session,
            channel_session_id=cs.id,
            telegram_chat_id="54321",
            reason="Draft comparison needed",
            current_topic="contract review",
            message_count=7,
        )
        assert "contract review" in handoff.context_summary
        assert "7 messages" in handoff.context_summary

    def test_telegram_handoff_updates_channel_session(self, db_session) -> None:
        cs, ts = bootstrap_telegram_session(
            db_session, telegram_chat_id="54321"
        )
        handoff = create_handoff_from_telegram(
            db_session,
            channel_session_id=cs.id,
            telegram_chat_id="54321",
            reason="Review",
        )
        db_session.refresh(cs)
        assert cs.session_metadata.get("handoff_created") is True


# ── Pending Handoffs Retrieval Tests ─────────────────────────────


class TestPendingHandoffs:
    """TEST:Telegram.Companion.ReviewNeededStateSurfacesInWorkspace"""

    def test_pending_handoffs_empty(self, db_session) -> None:
        records = get_pending_handoffs(db_session)
        assert records == []

    def test_pending_handoffs_returns_voice_handoff(self, db_session) -> None:
        cs, vs = bootstrap_voice_session(db_session)
        create_handoff_from_voice(
            db_session,
            channel_session_id=cs.id,
            reason="Voice review needed",
        )
        records = get_pending_handoffs(db_session)
        assert len(records) == 1
        assert records[0].source_channel == "voice"

    def test_pending_handoffs_returns_telegram_handoff(self, db_session) -> None:
        cs, ts = bootstrap_telegram_session(
            db_session, telegram_chat_id="54321"
        )
        create_handoff_from_telegram(
            db_session,
            channel_session_id=cs.id,
            telegram_chat_id="54321",
            reason="Telegram review needed",
        )
        records = get_pending_handoffs(db_session)
        assert len(records) == 1
        assert records[0].source_channel == "telegram"

    def test_pending_handoffs_mixed_channels(self, db_session) -> None:
        cs1, vs = bootstrap_voice_session(db_session)
        create_handoff_from_voice(
            db_session,
            channel_session_id=cs1.id,
            reason="Voice review",
        )
        cs2, ts = bootstrap_telegram_session(
            db_session, telegram_chat_id="54321"
        )
        create_handoff_from_telegram(
            db_session,
            channel_session_id=cs2.id,
            telegram_chat_id="54321",
            reason="Telegram review",
        )
        records = get_pending_handoffs(db_session)
        assert len(records) == 2
        channels = {r.source_channel for r in records}
        assert channels == {"voice", "telegram"}


# ── Safety Parity Tests ─────────────────────────────────────────


class TestSafetyParity:
    """TEST:Security.NoAutoSend.GlobalBoundaryPreserved
    TEST:Security.ReviewGate.ExternalImpactRequiresApproval"""

    def test_auto_send_blocked_verification_passes(self) -> None:
        assert verify_auto_send_blocked({"auto_send_blocked": True}) is True

    def test_auto_send_blocked_verification_fails_when_missing(self) -> None:
        assert verify_auto_send_blocked({}) is False

    def test_auto_send_blocked_verification_fails_when_false(self) -> None:
        assert verify_auto_send_blocked({"auto_send_blocked": False}) is False

    def test_review_gate_preserved_when_path_exists(self) -> None:
        assert verify_review_gate_preserved(
            needs_review=True, has_review_path=True
        ) is True

    def test_review_gate_fails_when_no_path(self) -> None:
        assert verify_review_gate_preserved(
            needs_review=True, has_review_path=False
        ) is False

    def test_review_gate_ok_when_no_review_needed(self) -> None:
        assert verify_review_gate_preserved(
            needs_review=False, has_review_path=False
        ) is True

    def test_voice_handoff_always_blocks_auto_send(self, db_session) -> None:
        cs, vs = bootstrap_voice_session(db_session)
        handoff = create_handoff_from_voice(
            db_session,
            channel_session_id=cs.id,
            reason="Test",
        )
        assert handoff.auto_send_blocked is True

    def test_telegram_handoff_always_blocks_auto_send(self, db_session) -> None:
        cs, ts = bootstrap_telegram_session(
            db_session, telegram_chat_id="54321"
        )
        handoff = create_handoff_from_telegram(
            db_session,
            channel_session_id=cs.id,
            telegram_chat_id="54321",
            reason="Test",
        )
        assert handoff.auto_send_blocked is True

    def test_all_handoff_records_block_auto_send(self, db_session) -> None:
        """Global safety: every handoff must have auto_send_blocked."""
        cs1, vs = bootstrap_voice_session(db_session)
        create_handoff_from_voice(
            db_session, channel_session_id=cs1.id, reason="V",
        )
        cs2, ts = bootstrap_telegram_session(
            db_session, telegram_chat_id="54321"
        )
        create_handoff_from_telegram(
            db_session,
            channel_session_id=cs2.id,
            telegram_chat_id="54321",
            reason="T",
        )
        records = get_pending_handoffs(db_session)
        for r in records:
            assert r.auto_send_blocked is True


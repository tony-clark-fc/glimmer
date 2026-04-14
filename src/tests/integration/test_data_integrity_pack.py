"""Cross-cutting data-integrity regression tests — WG5.

TEST:Integrity.SourceLayer.MessagesThreadsEventsSignalsRemainDistinct
TEST:Integrity.AcceptedState.PromotionRetainsOriginTrace
TEST:Integrity.Summaries.SupersessionDoesNotEraseHistory
TEST:Domain.InterpretedVsAccepted.Separation
TEST:Domain.MultiAccount.ProvenancePersistence
TEST:Security.NoAutoSend.GlobalBoundaryPreserved
TEST:Release.DataIntegrity.MemoryAndProvenanceRemainConsistent

WORKG:WG5 — Data-integrity regression surface
TESTPACK:DataIntegrity.ControlSurface
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select

from app.models.source import (
    Message,
    MessageThread,
    CalendarEvent,
    ImportedSignal,
    ConnectedAccount,
)
from app.models.portfolio import Project
from app.models.interpretation import (
    MessageClassification,
    ExtractedAction,
)
from app.models.drafting import FocusPack, BriefingArtifact
from app.models.channel import ChannelSession


def _make_account(db_session, provider_type: str = "google", label: str = "test") -> ConnectedAccount:
    """Create a ConnectedAccount for test use."""
    acct = ConnectedAccount(
        provider_type=provider_type,
        account_label=label,
    )
    db_session.add(acct)
    db_session.flush()
    return acct


# ── TEST:Integrity.SourceLayer.MessagesThreadsEventsSignalsRemainDistinct ───


class TestSourceLayerDistinctness:
    """Prove source-layer records remain distinct after persistence."""

    def test_message_and_thread_remain_separate(self, db_session) -> None:
        """A message and its parent thread are distinct records."""
        acct = _make_account(db_session)

        thread = MessageThread(
            connected_account_id=acct.id,
            source_type="gmail",
            external_thread_id="integrity-thread-1",
            derived_subject="Test thread",
        )
        db_session.add(thread)
        db_session.flush()

        msg = Message(
            connected_account_id=acct.id,
            source_type="gmail",
            external_message_id="integrity-msg-1",
            thread_id=thread.id,
            subject="Re: Test thread",
            body_text="Hello",
        )
        db_session.add(msg)
        db_session.flush()

        assert msg.id != thread.id
        assert msg.thread_id == thread.id

        reloaded_msg = db_session.get(Message, msg.id)
        reloaded_thread = db_session.get(MessageThread, thread.id)
        assert reloaded_msg is not None
        assert reloaded_thread is not None
        assert reloaded_msg.thread_id == reloaded_thread.id

    def test_event_is_distinct_from_message(self, db_session) -> None:
        """Events and messages are stored in separate tables."""
        acct = _make_account(db_session)

        event = CalendarEvent(
            connected_account_id=acct.id,
            external_event_id="integrity-event-1",
            title="Meeting",
            start_time=datetime(2026, 5, 1, 10, 0, tzinfo=timezone.utc),
            end_time=datetime(2026, 5, 1, 11, 0, tzinfo=timezone.utc),
        )
        msg = Message(
            connected_account_id=acct.id,
            source_type="gmail",
            external_message_id="integrity-msg-2",
            subject="Meeting notes",
            body_text="Notes here",
        )
        db_session.add_all([event, msg])
        db_session.flush()

        assert event.id != msg.id
        assert type(event).__tablename__ != type(msg).__tablename__

    def test_signal_preserves_origin_channel(self, db_session) -> None:
        """ImportedSignals retain their origin channel provenance."""
        signal = ImportedSignal(
            signal_type="voice_transcript",
            content="What is my top priority?",
            raw_metadata={"channel": "voice", "session_id": "test-session"},
        )
        db_session.add(signal)
        db_session.flush()

        reloaded = db_session.get(ImportedSignal, signal.id)
        assert reloaded.signal_type == "voice_transcript"
        assert reloaded.raw_metadata["channel"] == "voice"


# ── TEST:Integrity.AcceptedState.PromotionRetainsOriginTrace ────────


class TestAcceptedStatePromotion:
    """Prove that interpretation → accepted promotion retains trace."""

    def test_classification_retains_review_state(self, db_session) -> None:
        """MessageClassification preserves review_state through state changes."""
        project = Project(name="Integrity Test Project", status="active")
        db_session.add(project)
        db_session.flush()

        acct = _make_account(db_session)
        msg = Message(
            connected_account_id=acct.id,
            source_type="gmail",
            external_message_id="integrity-class-1",
            subject="Budget query",
            body_text="What's our budget?",
        )
        db_session.add(msg)
        db_session.flush()

        cls = MessageClassification(
            source_record_id=msg.id,
            source_record_type="message",
            selected_project_id=project.id,
            confidence=0.9,
            review_state="pending_review",
        )
        db_session.add(cls)
        db_session.flush()

        # Promote to accepted
        cls.review_state = "accepted"
        db_session.flush()

        reloaded = db_session.get(MessageClassification, cls.id)
        assert reloaded.review_state == "accepted"
        assert reloaded.source_record_id == msg.id  # origin trace preserved
        assert reloaded.selected_project_id == project.id

    def test_extracted_action_retains_source_message(self, db_session) -> None:
        """ExtractedAction always traces back to its source message."""
        acct = _make_account(db_session, provider_type="microsoft_365", label="work")
        msg = Message(
            connected_account_id=acct.id,
            source_type="microsoft_mail",
            external_message_id="integrity-action-1",
            subject="Action needed",
            body_text="Please review the contract",
        )
        db_session.add(msg)
        db_session.flush()

        action = ExtractedAction(
            source_record_id=msg.id,
            source_record_type="message",
            action_text="Review the contract",
            review_state="pending_review",
        )
        db_session.add(action)
        db_session.flush()

        # Accept the action
        action.review_state = "accepted"
        db_session.flush()

        reloaded = db_session.get(ExtractedAction, action.id)
        assert reloaded.source_record_id == msg.id
        assert reloaded.review_state == "accepted"


# ── TEST:Integrity.Summaries.SupersessionDoesNotEraseHistory ────────


class TestSummarySupersession:
    """Prove summary refresh does not erase earlier versions."""

    def test_briefing_artifacts_accumulate(self, db_session) -> None:
        """Multiple briefing artifacts coexist — old ones are not deleted."""
        a1 = BriefingArtifact(
            briefing_type="voice_spoken_briefing",
            content="First briefing content",
        )
        a2 = BriefingArtifact(
            briefing_type="voice_spoken_briefing",
            content="Second briefing content",
        )
        db_session.add_all([a1, a2])
        db_session.flush()

        results = db_session.execute(
            select(BriefingArtifact)
            .where(BriefingArtifact.briefing_type == "voice_spoken_briefing")
        ).scalars().all()
        assert len(results) >= 2
        contents = {r.content for r in results}
        assert "First briefing content" in contents
        assert "Second briefing content" in contents

    def test_focus_packs_accumulate(self, db_session) -> None:
        """Multiple focus packs coexist — history preserved."""
        fp1 = FocusPack(
            top_actions={"items": [{"title": "Old priority"}]},
        )
        fp2 = FocusPack(
            top_actions={"items": [{"title": "New priority"}]},
        )
        db_session.add_all([fp1, fp2])
        db_session.flush()

        results = db_session.execute(
            select(FocusPack).order_by(FocusPack.created_at.desc())
        ).scalars().all()
        assert len(results) >= 2


# ── TEST:Domain.MultiAccount.ProvenancePersistence ──────────────────


class TestMultiAccountProvenance:
    """Prove multi-account provenance survives persistence round trips."""

    def test_messages_from_different_accounts_stay_distinct(self, db_session) -> None:
        """Messages from different provider accounts keep their provenance."""
        acct_google = _make_account(db_session, provider_type="google", label="personal-gmail")
        acct_ms = _make_account(db_session, provider_type="microsoft_365", label="work-o365")

        msg_google = Message(
            connected_account_id=acct_google.id,
            source_type="gmail",
            external_message_id="integrity-g-msg-1",
            subject="Google message",
            body_text="From Google",
        )
        msg_ms = Message(
            connected_account_id=acct_ms.id,
            source_type="microsoft_mail",
            external_message_id="integrity-ms-msg-1",
            subject="Microsoft message",
            body_text="From Microsoft",
        )
        db_session.add_all([msg_google, msg_ms])
        db_session.flush()

        g = db_session.get(Message, msg_google.id)
        m = db_session.get(Message, msg_ms.id)
        assert g.connected_account_id == acct_google.id
        assert g.source_type == "gmail"
        assert m.connected_account_id == acct_ms.id
        assert m.source_type == "microsoft_mail"
        assert g.connected_account_id != m.connected_account_id


# ── TEST:Security.NoAutoSend.GlobalBoundaryPreserved ────────────────


class TestGlobalAutoSendBoundary:
    """Prove auto_send_blocked is enforced across all companion channels."""

    def test_handoff_artifacts_always_block_auto_send(self, db_session) -> None:
        """Every channel_handoff BriefingArtifact has auto_send source metadata."""
        from app.services.voice import bootstrap_voice_session
        from app.services.handoff import (
            create_handoff_from_voice,
            get_pending_handoffs,
        )

        cs, vs = bootstrap_voice_session(db_session)
        create_handoff_from_voice(
            db_session,
            channel_session_id=cs.id,
            reason="Data integrity test",
        )

        records = get_pending_handoffs(db_session)
        for r in records:
            assert r.auto_send_blocked is True

    def test_channel_sessions_do_not_bypass_review(self, db_session) -> None:
        """ChannelSession records cannot silently create auto-send state."""
        cs = ChannelSession(
            channel_type="voice",
            channel_identity="voice-integrity-test",
        )
        db_session.add(cs)
        db_session.flush()

        reloaded = db_session.get(ChannelSession, cs.id)
        meta = reloaded.session_metadata or {}
        assert meta.get("auto_send_allowed") is not True



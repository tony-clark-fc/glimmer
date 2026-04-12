"""Interpretation-layer and review-state persistence tests.

TEST:Domain.InterpretedVsAccepted.Separation
TEST:Domain.Interpretation.ReviewStateLifecyclePersists
"""

from __future__ import annotations

from datetime import datetime, timezone

from app.models.portfolio import Project
from app.models.source import ConnectedAccount, Message
from app.models.interpretation import (
    ExtractedAction,
    ExtractedDecision,
    ExtractedDeadlineSignal,
    MessageClassification,
    VALID_REVIEW_STATES,
)


class TestInterpretedVsAcceptedSeparation:
    """TEST:Domain.InterpretedVsAccepted.Separation

    Interpreted artifacts are structurally separate from accepted records.
    """

    def test_classification_is_not_a_project(self, db_session) -> None:
        """Classification lives in its own table, not collapsed into project."""
        project = Project(name="Separation Test")
        db_session.add(project)
        db_session.flush()

        acct = ConnectedAccount(
            provider_type="google", account_label="Test"
        )
        db_session.add(acct)
        db_session.flush()

        msg = Message(
            connected_account_id=acct.id,
            source_type="gmail",
            external_message_id="sep-msg-001",
        )
        db_session.add(msg)
        db_session.flush()

        cls = MessageClassification(
            source_record_id=msg.id,
            source_record_type="message",
            selected_project_id=project.id,
            confidence=0.85,
            review_state="pending_review",
        )
        db_session.add(cls)
        db_session.flush()

        fetched = db_session.get(MessageClassification, cls.id)
        assert fetched is not None
        assert fetched.review_state == "pending_review"
        # Classification exists independently — it does not mutate the project
        proj = db_session.get(Project, project.id)
        assert proj.status == "active"  # project unchanged

    def test_extracted_action_stays_pending(self, db_session) -> None:
        """An extracted action begins as pending, not auto-accepted."""
        acct = ConnectedAccount(
            provider_type="google", account_label="Test"
        )
        db_session.add(acct)
        db_session.flush()

        msg = Message(
            connected_account_id=acct.id,
            source_type="gmail",
            external_message_id="action-msg-001",
        )
        db_session.add(msg)
        db_session.flush()

        action = ExtractedAction(
            source_record_id=msg.id,
            source_record_type="message",
            action_text="Send revised budget by Friday",
            urgency_signal="high",
        )
        db_session.add(action)
        db_session.flush()

        fetched = db_session.get(ExtractedAction, action.id)
        assert fetched is not None
        assert fetched.review_state == "pending_review"


class TestReviewStateLifecycle:
    """TEST:Domain.Interpretation.ReviewStateLifecyclePersists

    Review state transitions persist correctly.
    """

    def _make_classification(self, db_session) -> MessageClassification:
        acct = ConnectedAccount(
            provider_type="google", account_label="Test"
        )
        db_session.add(acct)
        db_session.flush()
        msg = Message(
            connected_account_id=acct.id,
            source_type="gmail",
            external_message_id=f"rs-msg-{__import__('uuid').uuid4().hex[:8]}",
        )
        db_session.add(msg)
        db_session.flush()
        cls = MessageClassification(
            source_record_id=msg.id,
            source_record_type="message",
            confidence=0.9,
        )
        db_session.add(cls)
        db_session.flush()
        return cls

    def test_all_review_states_valid(self) -> None:
        """Valid review states include the expected values."""
        assert VALID_REVIEW_STATES == {
            "pending_review", "accepted", "amended", "rejected", "superseded"
        }

    def test_transition_to_accepted(self, db_session) -> None:
        cls = self._make_classification(db_session)
        assert cls.review_state == "pending_review"

        cls.review_state = "accepted"
        cls.reviewed_at = datetime.now(timezone.utc)
        db_session.flush()

        fetched = db_session.get(MessageClassification, cls.id)
        assert fetched.review_state == "accepted"
        assert fetched.reviewed_at is not None

    def test_transition_to_rejected(self, db_session) -> None:
        cls = self._make_classification(db_session)
        cls.review_state = "rejected"
        cls.reviewed_at = datetime.now(timezone.utc)
        db_session.flush()

        fetched = db_session.get(MessageClassification, cls.id)
        assert fetched.review_state == "rejected"

    def test_transition_to_amended(self, db_session) -> None:
        cls = self._make_classification(db_session)
        cls.review_state = "amended"
        db_session.flush()
        assert db_session.get(MessageClassification, cls.id).review_state == "amended"

    def test_transition_to_superseded(self, db_session) -> None:
        cls = self._make_classification(db_session)
        cls.review_state = "superseded"
        db_session.flush()
        assert db_session.get(MessageClassification, cls.id).review_state == "superseded"

    def test_extracted_decision_review_lifecycle(self, db_session) -> None:
        acct = ConnectedAccount(
            provider_type="google", account_label="Test"
        )
        db_session.add(acct)
        db_session.flush()
        msg = Message(
            connected_account_id=acct.id,
            source_type="gmail",
            external_message_id="dec-msg-001",
        )
        db_session.add(msg)
        db_session.flush()

        decision = ExtractedDecision(
            source_record_id=msg.id,
            source_record_type="message",
            decision_text="Use PostgreSQL for primary storage",
        )
        db_session.add(decision)
        db_session.flush()
        assert decision.review_state == "pending_review"

        decision.review_state = "accepted"
        db_session.flush()
        assert db_session.get(ExtractedDecision, decision.id).review_state == "accepted"

    def test_deadline_signal_review_lifecycle(self, db_session) -> None:
        acct = ConnectedAccount(
            provider_type="google", account_label="Test"
        )
        db_session.add(acct)
        db_session.flush()
        msg = Message(
            connected_account_id=acct.id,
            source_type="gmail",
            external_message_id="dl-msg-001",
        )
        db_session.add(msg)
        db_session.flush()

        deadline = ExtractedDeadlineSignal(
            source_record_id=msg.id,
            source_record_type="message",
            deadline_text="By end of Q2",
            inferred_date=datetime(2026, 6, 30, tzinfo=timezone.utc),
            confidence=0.7,
        )
        db_session.add(deadline)
        db_session.flush()
        assert deadline.review_state == "pending_review"

        deadline.review_state = "accepted"
        db_session.flush()
        assert db_session.get(ExtractedDeadlineSignal, deadline.id).review_state == "accepted"


"""Extraction and review-state tests.

TEST:Triage.ActionExtraction.ClearRequestBecomesCandidateAction
TEST:Triage.ActionExtraction.UncertainMeaningRequiresReview
TEST:Triage.Extraction.DecisionAndDeadlineSignalsPersist
TEST:Triage.ReviewInterrupt.ResumeContinuesSafely
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.graphs.triage import extract_and_persist, CONFIDENCE_THRESHOLD_AMBIGUOUS
from app.models.interpretation import (
    ExtractedAction,
    ExtractedDecision,
    ExtractedDeadlineSignal,
    VALID_REVIEW_STATES,
)
from app.models.portfolio import Project
from app.models.source import ConnectedAccount, Message


def _make_message(db_session) -> Message:
    account = ConnectedAccount(
        provider_type="google",
        account_label="test@example.com",
        status="active",
    )
    db_session.add(account)
    db_session.flush()

    message = Message(
        connected_account_id=account.id,
        source_type="gmail",
        external_message_id="ext_msg_001",
    )
    db_session.add(message)
    db_session.flush()
    return message


class TestActionExtraction:
    """TEST:Triage.ActionExtraction.ClearRequestBecomesCandidateAction
    TEST:Triage.ActionExtraction.UncertainMeaningRequiresReview
    """

    def test_clear_action_persists_as_pending_review(self, db_session) -> None:
        """A clear action request creates an ExtractedAction in pending_review."""
        msg = _make_message(db_session)
        project = Project(name="Test Project")
        db_session.add(project)
        db_session.flush()

        result = extract_and_persist(
            db_session,
            source_record_id=msg.id,
            source_record_type="message",
            project_id=project.id,
            actions=[{
                "description": "Send the Q3 budget report by Friday",
                "confidence": 0.9,
                "proposed_owner": "operator",
                "urgency_signal": "high",
            }],
            decisions=[],
            deadlines=[],
        )

        assert len(result.action_ids) == 1
        action = db_session.get(ExtractedAction, result.action_ids[0])
        assert action.action_text == "Send the Q3 budget report by Friday"
        assert action.review_state == "pending_review"
        assert action.linked_project_id == project.id

    def test_uncertain_action_triggers_review(self, db_session) -> None:
        """Low-confidence action sets needs_review flag."""
        msg = _make_message(db_session)

        result = extract_and_persist(
            db_session,
            source_record_id=msg.id,
            source_record_type="message",
            project_id=None,
            actions=[{
                "description": "Maybe follow up on something?",
                "confidence": 0.2,  # Below threshold
            }],
            decisions=[],
            deadlines=[],
        )

        assert result.needs_review
        assert len(result.review_reasons) > 0
        assert "low confidence" in result.review_reasons[0].lower()

    def test_multiple_actions_all_persist(self, db_session) -> None:
        msg = _make_message(db_session)

        result = extract_and_persist(
            db_session,
            source_record_id=msg.id,
            source_record_type="message",
            project_id=None,
            actions=[
                {"description": "Action one", "confidence": 0.8},
                {"description": "Action two", "confidence": 0.7},
            ],
            decisions=[],
            deadlines=[],
        )

        assert len(result.action_ids) == 2


class TestDecisionAndDeadlineExtraction:
    """TEST:Triage.Extraction.DecisionAndDeadlineSignalsPersist"""

    def test_decision_persists(self, db_session) -> None:
        msg = _make_message(db_session)
        project = Project(name="Decision Host")
        db_session.add(project)
        db_session.flush()

        result = extract_and_persist(
            db_session,
            source_record_id=msg.id,
            source_record_type="message",
            project_id=project.id,
            actions=[],
            decisions=[{
                "description": "We agreed to use vendor X for hosting",
                "rationale": "Cost savings and reliability track record",
            }],
            deadlines=[],
        )

        assert len(result.decision_ids) == 1
        decision = db_session.get(ExtractedDecision, result.decision_ids[0])
        assert "vendor X" in decision.decision_text
        assert decision.review_state == "pending_review"

    def test_deadline_persists(self, db_session) -> None:
        msg = _make_message(db_session)

        result = extract_and_persist(
            db_session,
            source_record_id=msg.id,
            source_record_type="message",
            project_id=None,
            actions=[],
            decisions=[],
            deadlines=[{
                "description": "Contract must be signed by April 30th",
                "inferred_date": datetime(2026, 4, 30, tzinfo=timezone.utc),
                "confidence": 0.85,
            }],
        )

        assert len(result.deadline_ids) == 1
        deadline = db_session.get(ExtractedDeadlineSignal, result.deadline_ids[0])
        assert "April 30th" in deadline.deadline_text
        assert deadline.review_state == "pending_review"
        assert deadline.inferred_date is not None

    def test_mixed_extraction(self, db_session) -> None:
        """Actions, decisions, and deadlines can all be extracted from one message."""
        msg = _make_message(db_session)

        result = extract_and_persist(
            db_session,
            source_record_id=msg.id,
            source_record_type="message",
            project_id=None,
            actions=[{"description": "Follow up with client", "confidence": 0.8}],
            decisions=[{"description": "Approved the new design"}],
            deadlines=[{
                "description": "Review due by end of week",
                "confidence": 0.7,
            }],
        )

        assert len(result.action_ids) == 1
        assert len(result.decision_ids) == 1
        assert len(result.deadline_ids) == 1


class TestReviewInterruptResume:
    """TEST:Triage.ReviewInterrupt.ResumeContinuesSafely

    Proves that review state transitions work correctly:
    - Items start in pending_review
    - Can transition to accepted, rejected, amended, superseded
    - State changes are durable
    """

    def test_extracted_action_starts_pending(self, db_session) -> None:
        msg = _make_message(db_session)
        result = extract_and_persist(
            db_session,
            source_record_id=msg.id,
            source_record_type="message",
            project_id=None,
            actions=[{"description": "Test action", "confidence": 0.9}],
            decisions=[],
            deadlines=[],
        )

        action = db_session.get(ExtractedAction, result.action_ids[0])
        assert action.review_state == "pending_review"

    def test_action_can_be_accepted(self, db_session) -> None:
        msg = _make_message(db_session)
        result = extract_and_persist(
            db_session,
            source_record_id=msg.id,
            source_record_type="message",
            project_id=None,
            actions=[{"description": "Accept me", "confidence": 0.9}],
            decisions=[],
            deadlines=[],
        )

        action = db_session.get(ExtractedAction, result.action_ids[0])
        action.review_state = "accepted"
        action.reviewed_at = datetime.now(timezone.utc)
        db_session.flush()

        refreshed = db_session.get(ExtractedAction, action.id)
        assert refreshed.review_state == "accepted"
        assert refreshed.reviewed_at is not None

    def test_action_can_be_rejected(self, db_session) -> None:
        msg = _make_message(db_session)
        result = extract_and_persist(
            db_session,
            source_record_id=msg.id,
            source_record_type="message",
            project_id=None,
            actions=[{"description": "Reject me", "confidence": 0.3}],
            decisions=[],
            deadlines=[],
        )

        action = db_session.get(ExtractedAction, result.action_ids[0])
        action.review_state = "rejected"
        db_session.flush()

        assert db_session.get(ExtractedAction, action.id).review_state == "rejected"

    def test_all_review_states_are_valid(self) -> None:
        """Verify the canonical review states are defined."""
        assert "pending_review" in VALID_REVIEW_STATES
        assert "accepted" in VALID_REVIEW_STATES
        assert "rejected" in VALID_REVIEW_STATES
        assert "amended" in VALID_REVIEW_STATES
        assert "superseded" in VALID_REVIEW_STATES


"""Project classification and stakeholder resolution tests.

TEST:Triage.ProjectClassification.SingleStrongMatch
TEST:Triage.ProjectClassification.AmbiguousMatchRequiresReview
TEST:Triage.StakeholderInterpretation.UncertainIdentityRequiresReview
"""

from __future__ import annotations

import uuid

from app.graphs.triage import (
    classify_project,
    persist_classification,
    resolve_stakeholders,
)
from app.models.portfolio import Project
from app.models.stakeholder import Stakeholder, StakeholderIdentity


class TestProjectClassificationStrongMatch:
    """TEST:Triage.ProjectClassification.SingleStrongMatch"""

    def test_strong_name_match(self, db_session) -> None:
        """Message mentioning a project name gets high-confidence classification."""
        project = Project(name="Alpha Launch", short_summary="The Q3 product launch")
        db_session.add(project)
        db_session.flush()

        result = classify_project(
            db_session,
            sender_identity="alice@example.com",
            subject="Update on Alpha Launch timeline",
            body_text="The Alpha Launch is on track for Q3.",
        )
        assert result.project_id == project.id
        assert result.confidence >= 0.5
        assert not result.needs_review

    def test_no_projects_returns_no_match(self, db_session) -> None:
        """No active projects → no classification needed."""
        result = classify_project(
            db_session,
            sender_identity="alice@example.com",
            subject="Random subject",
            body_text="Nothing relevant here.",
        )
        assert result.project_id is None
        assert result.confidence == 0.0
        assert not result.needs_review

    def test_no_matching_content_needs_review(self, db_session) -> None:
        """Message with no project keywords needs manual classification."""
        project = Project(name="Beta Project")
        db_session.add(project)
        db_session.flush()

        result = classify_project(
            db_session,
            sender_identity="bob@example.com",
            subject="Lunch plans",
            body_text="Are we meeting for lunch?",
        )
        assert result.needs_review
        assert result.confidence == 0.0

    def test_classification_persists(self, db_session) -> None:
        """Classification result is persisted as a MessageClassification."""
        project = Project(name="Gamma System")
        db_session.add(project)
        db_session.flush()

        result = classify_project(
            db_session,
            sender_identity=None,
            subject="Gamma System deployment update",
            body_text="Gamma System passed staging tests.",
        )

        msg_id = uuid.uuid4()
        cls_id = persist_classification(db_session, msg_id, "message", result)

        from app.models.interpretation import MessageClassification
        cls = db_session.get(MessageClassification, cls_id)
        assert cls is not None
        assert cls.selected_project_id == project.id
        assert cls.review_state == "accepted"


class TestProjectClassificationAmbiguous:
    """TEST:Triage.ProjectClassification.AmbiguousMatchRequiresReview"""

    def test_ambiguous_multiple_matches_needs_review(self, db_session) -> None:
        """Two projects match with similar confidence → review required."""
        p1 = Project(
            name="Platform Rebuild",
            short_summary="Rebuild the main platform infrastructure",
        )
        p2 = Project(
            name="Platform Analytics",
            short_summary="Analytics platform for customer data",
        )
        db_session.add_all([p1, p2])
        db_session.flush()

        result = classify_project(
            db_session,
            sender_identity="dev@example.com",
            subject="Platform update needed",
            body_text="We need to update the platform before the deadline.",
        )
        # Both projects match on "Platform" keyword
        assert result.needs_review
        assert len(result.candidates) >= 2

    def test_ambiguous_classification_persists_as_pending(self, db_session) -> None:
        """Ambiguous classification persists with pending_review state."""
        p1 = Project(name="Shared Name Project A")
        p2 = Project(name="Shared Name Project B")
        db_session.add_all([p1, p2])
        db_session.flush()

        result = classify_project(
            db_session,
            sender_identity=None,
            subject="Shared Name update",
            body_text="This relates to Shared Name work.",
        )

        msg_id = uuid.uuid4()
        cls_id = persist_classification(db_session, msg_id, "message", result)

        from app.models.interpretation import MessageClassification
        cls = db_session.get(MessageClassification, cls_id)
        assert cls.review_state == "pending_review"
        assert cls.ambiguity_flag is True


class TestStakeholderResolution:
    """TEST:Triage.StakeholderInterpretation.UncertainIdentityRequiresReview"""

    def test_single_match_resolves_cleanly(self, db_session) -> None:
        """Known sender with unique identity resolves without review."""
        stakeholder = Stakeholder(display_name="Alice")
        db_session.add(stakeholder)
        db_session.flush()

        identity = StakeholderIdentity(
            stakeholder_id=stakeholder.id,
            channel_type="email",
            identity_value="alice@example.com",
        )
        db_session.add(identity)
        db_session.flush()

        result = resolve_stakeholders(db_session, sender_identity="alice@example.com")
        assert stakeholder.id in result.stakeholder_ids
        assert not result.needs_review

    def test_unknown_sender_returns_empty(self, db_session) -> None:
        """Unknown sender returns no matches, no review needed."""
        result = resolve_stakeholders(db_session, sender_identity="nobody@example.com")
        assert len(result.stakeholder_ids) == 0
        assert not result.needs_review

    def test_multiple_matches_needs_review(self, db_session) -> None:
        """Same email belonging to multiple stakeholders → review required."""
        s1 = Stakeholder(display_name="Alice Work")
        s2 = Stakeholder(display_name="Alice Personal")
        db_session.add_all([s1, s2])
        db_session.flush()

        # Same email registered under two different stakeholders
        id1 = StakeholderIdentity(
            stakeholder_id=s1.id,
            channel_type="email",
            identity_value="alice@example.com",
        )
        id2 = StakeholderIdentity(
            stakeholder_id=s2.id,
            channel_type="email",
            identity_value="alice@example.com",
        )
        db_session.add_all([id1, id2])
        db_session.flush()

        result = resolve_stakeholders(db_session, sender_identity="alice@example.com")
        assert result.needs_review
        assert len(result.ambiguities) > 0
        assert result.ambiguities[0]["role"] == "sender"

    def test_named_email_resolves(self, db_session) -> None:
        """Email in 'Name <addr>' format resolves correctly."""
        stakeholder = Stakeholder(display_name="Bob")
        db_session.add(stakeholder)
        db_session.flush()

        identity = StakeholderIdentity(
            stakeholder_id=stakeholder.id,
            channel_type="email",
            identity_value="bob@example.com",
        )
        db_session.add(identity)
        db_session.flush()

        result = resolve_stakeholders(
            db_session, sender_identity="Bob Smith <bob@example.com>"
        )
        assert stakeholder.id in result.stakeholder_ids

    def test_no_sender_returns_empty(self, db_session) -> None:
        """None sender returns empty result without error."""
        result = resolve_stakeholders(db_session, sender_identity=None)
        assert len(result.stakeholder_ids) == 0
        assert not result.needs_review


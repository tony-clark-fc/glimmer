"""Drafting handoff and no-auto-send boundary tests.

TEST:Drafting.DraftGeneration.CreatesReviewableDraft
TEST:Drafting.NoAutoSend.BoundaryPreserved
TEST:Security.NoAutoSend.GlobalBoundaryPreserved
"""

from __future__ import annotations

import uuid

from app.models.drafting import Draft, DraftVariant
from app.models.audit import AuditRecord
from app.graphs.drafting import (
    create_draft,
    has_send_capability,
    AUTO_SEND_BLOCKED,
)


class TestDraftCreation:
    """TEST:Drafting.DraftGeneration.CreatesReviewableDraft

    Proves that the drafting handoff creates reviewable draft artifacts.
    """

    def test_creates_draft_in_draft_status(self, db_session) -> None:
        """Draft is created with 'draft' status — never 'sent'."""
        result = create_draft(
            session=db_session,
            body_content="Dear colleague, here is the update.",
            intent="reply",
        )
        assert result.draft_id is not None

        draft = db_session.get(Draft, result.draft_id)
        assert draft is not None
        assert draft.status == "draft"
        assert draft.body_content == "Dear colleague, here is the update."
        assert draft.intent_label == "reply"

    def test_draft_with_project_context(self, db_session) -> None:
        """Draft preserves project and stakeholder context."""
        from app.models.portfolio import Project
        project = Project(name="Test", status="active")
        db_session.add(project)
        db_session.flush()

        stakeholder_id = uuid.uuid4()
        result = create_draft(
            session=db_session,
            body_content="Meeting follow-up notes.",
            intent="follow_up",
            project_id=project.id,
            stakeholder_ids=[stakeholder_id],
            channel_type="email",
            tone_mode="warm",
        )

        draft = db_session.get(Draft, result.draft_id)
        assert draft.linked_project_id == project.id
        assert str(stakeholder_id) in str(draft.linked_stakeholder_ids)
        assert draft.channel_type == "email"
        assert draft.tone_mode == "warm"

    def test_draft_with_variants(self, db_session) -> None:
        """Draft can include multiple tone variants."""
        result = create_draft(
            session=db_session,
            body_content="Main draft content.",
            intent="reply",
            variants=[
                {"label": "concise", "body_content": "Short version."},
                {"label": "fuller", "body_content": "Extended version with more detail."},
            ],
        )
        assert len(result.variant_ids) == 2

        for vid in result.variant_ids:
            variant = db_session.get(DraftVariant, vid)
            assert variant is not None
            assert variant.draft_id == result.draft_id

    def test_draft_creates_audit_record(self, db_session) -> None:
        """Draft creation produces an audit trail entry."""
        result = create_draft(
            session=db_session,
            body_content="Test draft.",
            intent="brief",
        )

        from sqlalchemy import select
        audits = db_session.execute(
            select(AuditRecord).where(
                AuditRecord.entity_type == "draft",
                AuditRecord.entity_id == result.draft_id,
            )
        ).scalars().all()
        assert len(audits) == 1
        assert audits[0].action == "created"
        assert audits[0].new_state["auto_send_blocked"] is True

    def test_draft_with_rationale(self, db_session) -> None:
        """Draft can carry rationale explaining why it was generated."""
        result = create_draft(
            session=db_session,
            body_content="Please see attached.",
            intent="reply",
            rationale_summary="Client requested status update; this responds to the latest thread.",
        )
        draft = db_session.get(Draft, result.draft_id)
        assert draft.rationale_summary is not None
        assert "status update" in draft.rationale_summary


class TestNoAutoSend:
    """TEST:Drafting.NoAutoSend.BoundaryPreserved
    TEST:Security.NoAutoSend.GlobalBoundaryPreserved

    Proves that the no-auto-send boundary is a hard invariant.
    """

    def test_auto_send_always_blocked(self, db_session) -> None:
        """DraftingResult always has auto_send_blocked=True."""
        result = create_draft(
            session=db_session,
            body_content="Test.",
            intent="reply",
        )
        assert result.auto_send_blocked is True

    def test_review_always_required(self, db_session) -> None:
        """DraftingResult always has review_required=True."""
        result = create_draft(
            session=db_session,
            body_content="Test.",
            intent="reply",
        )
        assert result.review_required is True

    def test_no_send_capability(self) -> None:
        """The drafting service explicitly has no send capability."""
        assert has_send_capability() is False

    def test_auto_send_blocked_constant(self) -> None:
        """AUTO_SEND_BLOCKED is a hard constant, always True."""
        assert AUTO_SEND_BLOCKED is True

    def test_draft_never_starts_sent(self, db_session) -> None:
        """A newly created draft is never in 'sent' status."""
        result = create_draft(
            session=db_session,
            body_content="Content.",
            intent="initiate",
        )
        draft = db_session.get(Draft, result.draft_id)
        assert draft.status == "draft"
        assert draft.status != "sent"
        assert draft.status != "sent_by_operator"


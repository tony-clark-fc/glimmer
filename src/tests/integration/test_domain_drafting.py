"""Drafting, briefing, and focus artifact persistence tests.

TEST:Domain.Drafting.DraftsAndVariantsPersistWithIntent
TEST:Domain.Briefings.FocusAndBriefingArtifactsPersist
"""

from __future__ import annotations

from app.models.portfolio import Project
from app.models.drafting import (
    BriefingArtifact,
    Draft,
    DraftVariant,
    FocusPack,
)


class TestDraftsAndVariants:
    """TEST:Domain.Drafting.DraftsAndVariantsPersistWithIntent"""

    def test_draft_persists_with_intent(self, db_session) -> None:
        project = Project(name="Draft Host")
        db_session.add(project)
        db_session.flush()

        draft = Draft(
            linked_project_id=project.id,
            channel_type="email",
            tone_mode="concise",
            body_content="Hi Alice, here's the updated timeline...",
            rationale_summary="Responding to Alice's request for updated timeline",
            intent_label="timeline_update_reply",
        )
        db_session.add(draft)
        db_session.flush()

        fetched = db_session.get(Draft, draft.id)
        assert fetched is not None
        assert fetched.intent_label == "timeline_update_reply"
        assert fetched.tone_mode == "concise"
        assert fetched.status == "draft"

    def test_draft_has_multiple_variants(self, db_session) -> None:
        draft = Draft(
            body_content="Base draft content",
            channel_type="email",
        )
        db_session.add(draft)
        db_session.flush()

        v1 = DraftVariant(
            draft_id=draft.id,
            variant_label="concise",
            body_content="Short version of the reply.",
        )
        v2 = DraftVariant(
            draft_id=draft.id,
            variant_label="warmer",
            body_content="A friendlier, more detailed version...",
        )
        v3 = DraftVariant(
            draft_id=draft.id,
            variant_label="executive",
            body_content="Executive summary style.",
        )
        db_session.add_all([v1, v2, v3])
        db_session.flush()

        db_session.refresh(draft)
        assert len(draft.variants) == 3
        labels = {v.variant_label for v in draft.variants}
        assert labels == {"concise", "warmer", "executive"}

    def test_draft_version_number_persists(self, db_session) -> None:
        draft = Draft(
            body_content="First version",
            version_number=1,
        )
        db_session.add(draft)
        db_session.flush()

        draft.body_content = "Revised version"
        draft.version_number = 2
        db_session.flush()

        fetched = db_session.get(Draft, draft.id)
        assert fetched.version_number == 2

    def test_draft_linked_stakeholder_ids(self, db_session) -> None:
        draft = Draft(
            body_content="Reply to multiple people",
            linked_stakeholder_ids={"stakeholders": ["id-aaa", "id-bbb"]},
        )
        db_session.add(draft)
        db_session.flush()

        fetched = db_session.get(Draft, draft.id)
        assert "id-aaa" in fetched.linked_stakeholder_ids["stakeholders"]


class TestBriefingsAndFocusPacks:
    """TEST:Domain.Briefings.FocusAndBriefingArtifactsPersist"""

    def test_briefing_artifact_persists(self, db_session) -> None:
        project = Project(name="Briefing Host")
        db_session.add(project)
        db_session.flush()

        ba = BriefingArtifact(
            linked_project_id=project.id,
            briefing_type="daily_focus",
            content="Top 3 priorities for today...",
            source_scope_metadata={"date_range": "2026-04-13"},
        )
        db_session.add(ba)
        db_session.flush()

        fetched = db_session.get(BriefingArtifact, ba.id)
        assert fetched is not None
        assert fetched.briefing_type == "daily_focus"
        assert fetched.source_scope_metadata["date_range"] == "2026-04-13"

    def test_meeting_prep_briefing(self, db_session) -> None:
        ba = BriefingArtifact(
            briefing_type="meeting_prep",
            content="Prep notes for the design review...",
        )
        db_session.add(ba)
        db_session.flush()

        fetched = db_session.get(BriefingArtifact, ba.id)
        assert fetched.briefing_type == "meeting_prep"

    def test_focus_pack_persists(self, db_session) -> None:
        fp = FocusPack(
            top_actions=[
                {"title": "Reply to Alice", "urgency": "high"},
                {"title": "Review contract", "urgency": "medium"},
            ],
            high_risk_items=[{"summary": "OAuth token expiry"}],
            waiting_on_items=[{"whom": "Bob", "what": "API spec"}],
            reply_debt_summary="3 unanswered emails from this week",
            calendar_pressure_summary="2 meetings before noon tomorrow",
        )
        db_session.add(fp)
        db_session.flush()

        fetched = db_session.get(FocusPack, fp.id)
        assert fetched is not None
        assert len(fetched.top_actions) == 2
        assert fetched.high_risk_items[0]["summary"] == "OAuth token expiry"
        assert "3 unanswered" in fetched.reply_debt_summary


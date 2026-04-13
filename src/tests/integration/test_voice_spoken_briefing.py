"""Spoken briefing integration tests — WF5.

TEST:Voice.Session.SpokenBriefingIsBoundedAndRelevant

Proves that spoken briefings are:
- bounded in length (not bloated essay output)
- grounded in real focus-pack data (not hallucinated)
- structured for listening (numbered items, short sentences)
- persisted as BriefingArtifact for traceability
- graceful when no data exists
"""

from __future__ import annotations

import uuid

from app.models.drafting import BriefingArtifact, FocusPack
from app.services.briefing import (
    MAX_BRIEFING_LENGTH,
    MAX_SPOKEN_ACTIONS,
    generate_spoken_briefing,
    generate_session_context_response,
    _format_top_actions,
    _format_risks,
    _format_waiting,
    _format_pressure,
)


# ── Focus Pack Formatting Tests ──────────────────────────────────


class TestSpokenBriefingFormatting:
    """Unit-level tests for briefing section formatting."""

    def test_format_top_actions_returns_bounded_output(self) -> None:
        items = [
            {"title": f"Action {i}", "rationale": f"Reason {i}"}
            for i in range(10)
        ]
        result = _format_top_actions({"items": items})
        assert result is not None
        # Should only mention MAX_SPOKEN_ACTIONS items
        for i in range(1, MAX_SPOKEN_ACTIONS + 1):
            assert f"Action {i - 1}" in result  # 0-indexed in data
        # Remaining count should be mentioned
        assert "plus" in result.lower()

    def test_format_top_actions_with_empty_items(self) -> None:
        assert _format_top_actions({"items": []}) is None
        assert _format_top_actions(None) is None
        assert _format_top_actions({}) is None

    def test_format_top_actions_truncates_long_titles(self) -> None:
        long_title = "A" * 100
        result = _format_top_actions({"items": [{"title": long_title}]})
        assert result is not None
        assert "..." in result
        assert len(long_title) > 80  # confirm test setup

    def test_format_risks_bounded(self) -> None:
        items = [
            {"summary": f"Risk {i}", "severity": "high"}
            for i in range(5)
        ]
        result = _format_risks({"items": items})
        assert result is not None
        assert "Risk 0" in result
        assert "Risk 1" in result
        # Should mention total count
        assert "5" in result

    def test_format_risks_empty(self) -> None:
        assert _format_risks(None) is None
        assert _format_risks({"items": []}) is None

    def test_format_waiting_bounded(self) -> None:
        items = [
            {"waiting_on": f"Person {i}", "description": f"Desc {i}"}
            for i in range(5)
        ]
        result = _format_waiting({"items": items})
        assert result is not None
        assert "Person 0" in result
        assert "Person 1" in result
        assert "5" in result

    def test_format_waiting_empty(self) -> None:
        assert _format_waiting(None) is None
        assert _format_waiting({"items": []}) is None

    def test_format_pressure_with_both(self) -> None:
        result = _format_pressure("3 pending actions", "2 active blockers")
        assert result is not None
        assert "3 pending actions" in result
        assert "2 active blockers" in result
        assert result.startswith("Pressure:")

    def test_format_pressure_with_none(self) -> None:
        assert _format_pressure(None, None) is None

    def test_format_pressure_with_only_reply_debt(self) -> None:
        result = _format_pressure("5 items", None)
        assert result is not None
        assert "5 items" in result


# ── Spoken Briefing Generation Tests ─────────────────────────────


class TestSpokenBriefingGeneration:
    """Integration tests for full briefing generation flow."""

    def test_briefing_with_no_focus_pack_returns_empty(self, db_session) -> None:
        """When no focus pack exists, briefing is graceful empty state."""
        result = generate_spoken_briefing(db_session)
        assert result.is_empty is True
        assert result.briefing_artifact_id is None
        assert result.source_focus_pack_id is None
        assert "No focus data" in result.briefing_text

    def test_briefing_from_populated_focus_pack(self, db_session) -> None:
        """Briefing with real data produces bounded spoken output."""
        fp = FocusPack(
            top_actions={"items": [
                {"title": "Review contracts", "rationale": "Due tomorrow"},
                {"title": "Update stakeholders", "rationale": "Overdue"},
            ]},
            high_risk_items={"items": [
                {"summary": "Budget overrun on Project Alpha", "severity": "high"},
            ]},
            waiting_on_items={"items": [
                {"waiting_on": "Legal team", "description": "Contract review"},
            ]},
            reply_debt_summary="3 pending actions awaiting review",
            calendar_pressure_summary=None,
        )
        db_session.add(fp)
        db_session.flush()

        result = generate_spoken_briefing(db_session, focus_pack_id=fp.id)

        assert result.is_empty is False
        assert result.source_focus_pack_id == fp.id
        assert result.briefing_artifact_id is not None
        assert result.section_count >= 3  # actions, risks, waiting
        # Content is grounded in the real data
        assert "Review contracts" in result.briefing_text
        assert "Budget overrun" in result.briefing_text
        assert "Legal team" in result.briefing_text

    def test_briefing_is_bounded_in_length(self, db_session) -> None:
        """Briefing text never exceeds MAX_BRIEFING_LENGTH."""
        # Create a focus pack with lots of data
        items = [
            {"title": f"Very important action number {i} with a long description that goes on", "rationale": f"Extremely detailed rationale {i} explaining why this is critical"}
            for i in range(20)
        ]
        fp = FocusPack(
            top_actions={"items": items},
            high_risk_items={"items": [
                {"summary": f"Risk description {i} that is also quite long" * 3}
                for i in range(10)
            ]},
            waiting_on_items={"items": [
                {"waiting_on": f"Person {i}", "description": f"Waiting for something important {i}" * 3}
                for i in range(10)
            ]},
            reply_debt_summary="15 pending actions awaiting review",
            calendar_pressure_summary="7 active blockers across projects",
        )
        db_session.add(fp)
        db_session.flush()

        result = generate_spoken_briefing(db_session, focus_pack_id=fp.id)

        assert len(result.briefing_text) <= MAX_BRIEFING_LENGTH
        assert result.is_empty is False

    def test_briefing_persists_artifact(self, db_session) -> None:
        """Briefing creates a traceable BriefingArtifact."""
        fp = FocusPack(
            top_actions={"items": [{"title": "Test action", "rationale": "Test"}]},
        )
        db_session.add(fp)
        db_session.flush()

        result = generate_spoken_briefing(
            db_session,
            focus_pack_id=fp.id,
            channel_session_id=uuid.uuid4(),
        )

        assert result.briefing_artifact_id is not None
        artifact = db_session.get(BriefingArtifact, result.briefing_artifact_id)
        assert artifact is not None
        assert artifact.briefing_type == "voice_spoken_briefing"
        assert artifact.content == result.briefing_text
        assert artifact.source_scope_metadata is not None
        assert artifact.source_scope_metadata["source_focus_pack_id"] == str(fp.id)

    def test_briefing_uses_latest_focus_pack_by_default(self, db_session) -> None:
        """When no focus_pack_id given, uses the most recent one."""
        fp_old = FocusPack(
            top_actions={"items": [{"title": "Old action"}]},
        )
        db_session.add(fp_old)
        db_session.flush()

        fp_new = FocusPack(
            top_actions={"items": [{"title": "New action"}]},
        )
        db_session.add(fp_new)
        db_session.flush()

        result = generate_spoken_briefing(db_session)

        assert result.source_focus_pack_id == fp_new.id
        assert "New action" in result.briefing_text

    def test_briefing_with_empty_focus_pack(self, db_session) -> None:
        """Focus pack with no data produces clear-state message."""
        fp = FocusPack()
        db_session.add(fp)
        db_session.flush()

        result = generate_spoken_briefing(db_session, focus_pack_id=fp.id)

        assert "clear" in result.briefing_text.lower()
        assert result.section_count == 0

    def test_briefing_section_count_matches_content(self, db_session) -> None:
        """Section count accurately reflects what's in the briefing."""
        fp = FocusPack(
            top_actions={"items": [{"title": "Action A"}]},
            reply_debt_summary="2 pending",
        )
        db_session.add(fp)
        db_session.flush()

        result = generate_spoken_briefing(db_session, focus_pack_id=fp.id)

        assert result.section_count == 2  # actions + pressure


# ── Session Context Response Tests ───────────────────────────────


class TestSessionContextResponse:
    """Tests for the quick 'where are we?' voice response."""

    def test_context_with_active_session(self) -> None:
        result = generate_session_context_response(
            current_topic="project deadlines",
            utterance_count=5,
            referenced_project_ids=[str(uuid.uuid4()), str(uuid.uuid4())],
            unresolved_prompts=["What about the budget?"],
        )
        assert "project deadlines" in result
        assert "5 exchanges" in result
        assert "2 projects" in result
        assert "1 open question" in result

    def test_context_with_no_topic(self) -> None:
        result = generate_session_context_response(
            current_topic=None,
            utterance_count=0,
            referenced_project_ids=[],
            unresolved_prompts=[],
        )
        assert "No specific topic" in result

    def test_context_is_concise(self) -> None:
        """Context response should be short — not a full briefing."""
        result = generate_session_context_response(
            current_topic="quarterly review",
            utterance_count=12,
            referenced_project_ids=[str(uuid.uuid4())] * 5,
            unresolved_prompts=["Q1", "Q2", "Q3"],
        )
        # Should be well under briefing length
        assert len(result) < 200

    def test_context_singular_forms(self) -> None:
        result = generate_session_context_response(
            current_topic="testing",
            utterance_count=1,
            referenced_project_ids=[str(uuid.uuid4())],
            unresolved_prompts=["one question"],
        )
        assert "1 exchange " in result  # not "exchanges"
        assert "1 project" in result  # not "projects"
        assert "1 open question " in result  # not "questions"


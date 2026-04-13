"""Work-breakdown and next-step advisory tests.

TEST:Planner.WorkBreakdown.SuggestsNextStepWithoutSilentRestructure
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from app.models.portfolio import Project
from app.models.execution import WorkItem, BlockerRecord, WaitingOnRecord
from app.models.interpretation import ExtractedAction
from app.graphs.planner import suggest_next_steps


class TestWorkBreakdownAdvisory:
    """TEST:Planner.WorkBreakdown.SuggestsNextStepWithoutSilentRestructure

    Proves that next-step suggestions are advisory and do not
    silently restructure the project model.
    """

    def test_no_project_returns_empty(self, db_session) -> None:
        """Nonexistent project returns no suggestions."""
        result = suggest_next_steps(db_session, uuid.uuid4())
        assert result == []

    def test_blocker_suggests_resolution(self, db_session) -> None:
        """Active blockers generate resolution suggestions."""
        project = Project(name="Test", status="active")
        db_session.add(project)
        db_session.flush()

        blocker = BlockerRecord(
            project_id=project.id,
            summary="Missing API credentials",
            status="active",
        )
        db_session.add(blocker)
        db_session.flush()

        result = suggest_next_steps(db_session, project.id)
        assert len(result) >= 1
        assert any("blocker" in s.suggestion.lower() for s in result)
        assert all(not s.is_restructuring for s in result)

    def test_overdue_items_suggested(self, db_session) -> None:
        """Overdue work items appear in suggestions."""
        project = Project(name="Test", status="active")
        db_session.add(project)
        db_session.flush()

        wi = WorkItem(
            project_id=project.id,
            title="Submit proposal",
            status="open",
            due_date=datetime.now(timezone.utc) - timedelta(days=1),
        )
        db_session.add(wi)
        db_session.flush()

        result = suggest_next_steps(db_session, project.id)
        assert len(result) >= 1
        assert any("overdue" in s.suggestion.lower() for s in result)

    def test_pending_actions_batch_review(self, db_session) -> None:
        """Many pending actions suggest batch review."""
        project = Project(name="Test", status="active")
        db_session.add(project)
        db_session.flush()

        for i in range(5):
            action = ExtractedAction(
                source_record_id=uuid.uuid4(),
                source_record_type="message",
                linked_project_id=project.id,
                action_text=f"Action {i}",
                review_state="pending_review",
            )
            db_session.add(action)
        db_session.flush()

        result = suggest_next_steps(db_session, project.id)
        assert len(result) >= 1
        assert any("pending" in s.suggestion.lower() for s in result)

    def test_overdue_waiting_on_suggests_follow_up(self, db_session) -> None:
        """Overdue waiting-on items suggest follow-up."""
        project = Project(name="Test", status="active")
        db_session.add(project)
        db_session.flush()

        wo = WaitingOnRecord(
            project_id=project.id,
            waiting_on_whom="Design team",
            description="Awaiting mockups",
            expected_by=datetime.now(timezone.utc) - timedelta(days=2),
            status="waiting",
        )
        db_session.add(wo)
        db_session.flush()

        result = suggest_next_steps(db_session, project.id)
        assert len(result) >= 1
        assert any("follow up" in s.suggestion.lower() for s in result)

    def test_empty_project_suggests_general_progress(self, db_session) -> None:
        """Project with no items suggests reviewing goals."""
        project = Project(name="Test", status="active")
        db_session.add(project)
        db_session.flush()

        result = suggest_next_steps(db_session, project.id)
        assert len(result) >= 1
        assert all(not s.is_restructuring for s in result)

    def test_suggestions_never_restructure(self, db_session) -> None:
        """No suggestion from the deterministic layer proposes restructuring."""
        project = Project(name="Test", status="active")
        db_session.add(project)
        db_session.flush()

        # Add various items to trigger different paths
        wi = WorkItem(
            project_id=project.id,
            title="Work item",
            status="open",
            due_date=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        blocker = BlockerRecord(
            project_id=project.id,
            summary="Blocked",
            status="active",
        )
        db_session.add_all([wi, blocker])
        db_session.flush()

        result = suggest_next_steps(db_session, project.id)
        assert all(not s.is_restructuring for s in result)

    def test_suggestions_have_rationale(self, db_session) -> None:
        """Every suggestion includes a rationale explanation."""
        project = Project(name="Test", status="active")
        db_session.add(project)
        db_session.flush()

        wi = WorkItem(
            project_id=project.id,
            title="Task",
            status="open",
        )
        db_session.add(wi)
        db_session.flush()

        result = suggest_next_steps(db_session, project.id)
        assert all(s.rationale != "" for s in result)


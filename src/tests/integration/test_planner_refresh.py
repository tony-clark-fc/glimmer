"""Project-memory refresh trigger tests.

TEST:Planner.ProjectMemoryRefresh.TriggerIsTraceable
"""

from __future__ import annotations

import uuid

from app.models.portfolio import Project
from app.models.execution import WorkItem
from app.models.interpretation import ExtractedAction
from app.models.summary import ProjectSummary, RefreshEvent
from app.models.audit import AuditRecord
from app.graphs.refresh import trigger_project_refresh


class TestProjectMemoryRefresh:
    """TEST:Planner.ProjectMemoryRefresh.TriggerIsTraceable

    Proves that project-memory refresh is triggered and traceable,
    with visible lineage and audit trail.
    """

    def test_refresh_creates_summary(self, db_session) -> None:
        """Refresh generates a new project summary."""
        project = Project(name="Alpha", status="active", objective="Build widgets")
        db_session.add(project)
        db_session.flush()

        result = trigger_project_refresh(db_session, project.id)
        assert result.status == "completed"
        assert result.summary_id is not None

        summary = db_session.get(ProjectSummary, result.summary_id)
        assert summary is not None
        assert "Alpha" in summary.summary_text
        assert summary.is_current is True

    def test_refresh_creates_refresh_event(self, db_session) -> None:
        """Refresh creates a traceable RefreshEvent record."""
        project = Project(name="Beta", status="active")
        db_session.add(project)
        db_session.flush()

        result = trigger_project_refresh(db_session, project.id, trigger_type="post_triage")
        event = db_session.get(RefreshEvent, result.refresh_event_id)
        assert event is not None
        assert event.status == "completed"
        assert event.refresh_type == "post_triage"
        assert event.completed_at is not None

    def test_refresh_creates_audit_record(self, db_session) -> None:
        """Refresh creates an audit record for traceability."""
        project = Project(name="Gamma", status="active")
        db_session.add(project)
        db_session.flush()

        result = trigger_project_refresh(db_session, project.id, triggered_by="system")

        from sqlalchemy import select
        audits = db_session.execute(
            select(AuditRecord).where(
                AuditRecord.entity_type == "project_summary",
                AuditRecord.entity_id == result.summary_id,
            )
        ).scalars().all()
        assert len(audits) == 1
        assert audits[0].action == "created"
        assert audits[0].actor == "system"
        assert "refresh_event_id" in audits[0].context_metadata

    def test_refresh_supersedes_previous_summary(self, db_session) -> None:
        """A second refresh supersedes the first and preserves lineage."""
        project = Project(name="Delta", status="active")
        db_session.add(project)
        db_session.flush()

        r1 = trigger_project_refresh(db_session, project.id)
        db_session.flush()
        r2 = trigger_project_refresh(db_session, project.id)
        db_session.flush()

        s1 = db_session.get(ProjectSummary, r1.summary_id)
        s2 = db_session.get(ProjectSummary, r2.summary_id)

        assert s1.is_current is False
        assert s2.is_current is True
        assert s2.supersedes_id == s1.id
        assert s2.version_marker == s1.version_marker + 1

    def test_refresh_includes_state_signals(self, db_session) -> None:
        """Summary text includes current work items and actions."""
        project = Project(name="Epsilon", status="active", objective="Ship v1")
        db_session.add(project)
        db_session.flush()

        wi = WorkItem(project_id=project.id, title="Deploy staging", status="open")
        action = ExtractedAction(
            source_record_id=uuid.uuid4(),
            source_record_type="message",
            linked_project_id=project.id,
            action_text="Review PR",
            review_state="pending_review",
        )
        db_session.add_all([wi, action])
        db_session.flush()

        result = trigger_project_refresh(db_session, project.id)
        summary = db_session.get(ProjectSummary, result.summary_id)
        assert "Deploy staging" in summary.summary_text
        assert "pending actions" in summary.summary_text.lower()

    def test_refresh_for_nonexistent_project_fails_gracefully(self, db_session) -> None:
        """Refresh for missing project creates a failed event, not an exception."""
        result = trigger_project_refresh(db_session, uuid.uuid4())
        assert result.status == "failed"
        assert result.summary_id is None

        event = db_session.get(RefreshEvent, result.refresh_event_id)
        assert event.status == "failed"

    def test_triggered_by_is_preserved(self, db_session) -> None:
        """The triggered_by actor is preserved in the refresh event."""
        project = Project(name="Zeta", status="active")
        db_session.add(project)
        db_session.flush()

        result = trigger_project_refresh(
            db_session, project.id, triggered_by="planner_graph"
        )
        event = db_session.get(RefreshEvent, result.refresh_event_id)
        assert event.triggered_by == "planner_graph"


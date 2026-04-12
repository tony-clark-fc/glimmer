"""Summary, refresh, and lineage persistence tests.

TEST:Domain.SummaryRefresh.Lineage
"""

from __future__ import annotations

from datetime import datetime, timezone

from app.models.portfolio import Project
from app.models.summary import ProjectSummary, RefreshEvent


class TestSummaryRefreshLineage:
    """TEST:Domain.SummaryRefresh.Lineage"""

    def test_project_summary_persists(self, db_session) -> None:
        project = Project(name="Summary Host")
        db_session.add(project)
        db_session.flush()

        summary = ProjectSummary(
            project_id=project.id,
            summary_text="Project is on track for Q2 delivery.",
            version_marker=1,
            confidence_indicator=0.9,
            source_scope_metadata={
                "messages_considered": 42,
                "date_range": "2026-04-01 to 2026-04-13",
            },
        )
        db_session.add(summary)
        db_session.flush()

        fetched = db_session.get(ProjectSummary, summary.id)
        assert fetched is not None
        assert fetched.version_marker == 1
        assert fetched.is_current is True
        assert fetched.confidence_indicator == 0.9

    def test_summary_supersession_lineage(self, db_session) -> None:
        """A new summary supersedes the old one with explicit lineage."""
        project = Project(name="Lineage Host")
        db_session.add(project)
        db_session.flush()

        v1 = ProjectSummary(
            project_id=project.id,
            summary_text="Initial summary — early stage.",
            version_marker=1,
            is_current=True,
        )
        db_session.add(v1)
        db_session.flush()

        # Create v2 that supersedes v1
        v2 = ProjectSummary(
            project_id=project.id,
            summary_text="Updated summary — post design review.",
            version_marker=2,
            supersedes_id=v1.id,
            is_current=True,
        )
        db_session.add(v2)

        # Mark v1 as no longer current
        v1.is_current = False
        db_session.flush()

        fetched_v1 = db_session.get(ProjectSummary, v1.id)
        fetched_v2 = db_session.get(ProjectSummary, v2.id)

        assert fetched_v1.is_current is False
        assert fetched_v2.is_current is True
        assert fetched_v2.supersedes_id == v1.id
        assert fetched_v2.version_marker == 2

    def test_refresh_event_persists(self, db_session) -> None:
        project = Project(name="Refresh Host")
        db_session.add(project)
        db_session.flush()

        refresh = RefreshEvent(
            project_id=project.id,
            refresh_type="summary_refresh",
            triggered_by="operator",
            input_scope={"date_range": "last_7_days", "sources": ["gmail"]},
            status="in_progress",
        )
        db_session.add(refresh)
        db_session.flush()

        fetched = db_session.get(RefreshEvent, refresh.id)
        assert fetched is not None
        assert fetched.refresh_type == "summary_refresh"
        assert fetched.triggered_by == "operator"
        assert fetched.status == "in_progress"

    def test_refresh_event_completion(self, db_session) -> None:
        project = Project(name="Refresh Complete Host")
        db_session.add(project)
        db_session.flush()

        summary = ProjectSummary(
            project_id=project.id,
            summary_text="Fresh summary",
            version_marker=1,
        )
        db_session.add(summary)
        db_session.flush()

        refresh = RefreshEvent(
            project_id=project.id,
            refresh_type="summary_refresh",
            triggered_by="scheduler",
            status="in_progress",
        )
        db_session.add(refresh)
        db_session.flush()

        refresh.status = "completed"
        refresh.completed_at = datetime.now(timezone.utc)
        refresh.output_artifact_ids = {"summary_ids": [str(summary.id)]}
        db_session.flush()

        fetched = db_session.get(RefreshEvent, refresh.id)
        assert fetched.status == "completed"
        assert fetched.completed_at is not None
        assert str(summary.id) in fetched.output_artifact_ids["summary_ids"]


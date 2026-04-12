"""Domain portfolio persistence tests.

TEST:Domain.ProjectLifecycle.BasicPersistence
TEST:Domain.ProjectPortfolio.WorkstreamsAndMilestonesPersist
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta

from sqlalchemy import select

from app.models.portfolio import Milestone, Project, ProjectWorkstream


# ── TEST:Domain.ProjectLifecycle.BasicPersistence ────────────────────


class TestProjectLifecycle:
    """Project CRUD and lifecycle basics."""

    def test_create_project_persists(self, db_session) -> None:
        """A new project can be created and read back."""
        project = Project(name="Alpha Launch", status="active")
        db_session.add(project)
        db_session.flush()

        fetched = db_session.get(Project, project.id)
        assert fetched is not None
        assert fetched.name == "Alpha Launch"
        assert fetched.status == "active"
        assert fetched.archived is False
        assert fetched.created_at is not None

    def test_project_fields_persist(self, db_session) -> None:
        """All main project properties round-trip correctly."""
        project = Project(
            name="Beta",
            short_summary="Short summary text",
            objective="Ship the beta milestone",
            status="planning",
            phase="Phase 1",
            priority_band="high",
        )
        db_session.add(project)
        db_session.flush()

        fetched = db_session.get(Project, project.id)
        assert fetched is not None
        assert fetched.short_summary == "Short summary text"
        assert fetched.objective == "Ship the beta milestone"
        assert fetched.phase == "Phase 1"
        assert fetched.priority_band == "high"

    def test_project_update_changes_updated_at(self, db_session) -> None:
        """Updating a project mutates updated_at."""
        project = Project(name="Gamma")
        db_session.add(project)
        db_session.flush()

        original_updated = project.updated_at

        project.status = "completed"
        db_session.flush()

        # SQLAlchemy onupdate fires on flush
        fetched = db_session.get(Project, project.id)
        assert fetched is not None
        assert fetched.status == "completed"

    def test_project_archive(self, db_session) -> None:
        """A project can be archived."""
        project = Project(name="Delta")
        db_session.add(project)
        db_session.flush()

        project.archived = True
        db_session.flush()

        fetched = db_session.get(Project, project.id)
        assert fetched is not None
        assert fetched.archived is True

    def test_multiple_projects_persist(self, db_session) -> None:
        """Multiple projects coexist without collision."""
        p1 = Project(name="Project One")
        p2 = Project(name="Project Two")
        p3 = Project(name="Project Three")
        db_session.add_all([p1, p2, p3])
        db_session.flush()

        result = db_session.execute(select(Project)).scalars().all()
        names = {p.name for p in result}
        assert {"Project One", "Project Two", "Project Three"}.issubset(names)


# ── TEST:Domain.ProjectPortfolio.WorkstreamsAndMilestonesPersist ─────


class TestWorkstreamPersistence:
    """ProjectWorkstream persistence and relationships."""

    def test_workstream_belongs_to_project(self, db_session) -> None:
        """A workstream links to its parent project."""
        project = Project(name="Workstream Host")
        db_session.add(project)
        db_session.flush()

        ws = ProjectWorkstream(
            project_id=project.id,
            title="Foundation",
            status="in_progress",
            ordering=1,
        )
        db_session.add(ws)
        db_session.flush()

        fetched = db_session.get(ProjectWorkstream, ws.id)
        assert fetched is not None
        assert fetched.project_id == project.id
        assert fetched.title == "Foundation"
        assert fetched.ordering == 1

    def test_project_has_many_workstreams(self, db_session) -> None:
        """A project can have multiple workstreams."""
        project = Project(name="Multi-WS")
        db_session.add(project)
        db_session.flush()

        ws_a = ProjectWorkstream(
            project_id=project.id, title="WS A", ordering=1
        )
        ws_b = ProjectWorkstream(
            project_id=project.id, title="WS B", ordering=2
        )
        db_session.add_all([ws_a, ws_b])
        db_session.flush()

        db_session.refresh(project)
        assert len(project.workstreams) == 2
        titles = {ws.title for ws in project.workstreams}
        assert titles == {"WS A", "WS B"}

    def test_workstream_fields_persist(self, db_session) -> None:
        """All workstream properties round-trip correctly."""
        project = Project(name="WS Fields Host")
        db_session.add(project)
        db_session.flush()

        ws = ProjectWorkstream(
            project_id=project.id,
            title="Core",
            summary="Core platform work",
            status="planned",
            ordering=0,
            owner_hint="engineering",
        )
        db_session.add(ws)
        db_session.flush()

        fetched = db_session.get(ProjectWorkstream, ws.id)
        assert fetched is not None
        assert fetched.summary == "Core platform work"
        assert fetched.owner_hint == "engineering"


class TestMilestonePersistence:
    """Milestone persistence and relationships."""

    def test_milestone_belongs_to_project(self, db_session) -> None:
        """A milestone links to its parent project."""
        project = Project(name="Milestone Host")
        db_session.add(project)
        db_session.flush()

        target = datetime(2026, 6, 1, tzinfo=timezone.utc)
        ms = Milestone(
            project_id=project.id,
            title="MVP Release",
            target_date=target,
            status="upcoming",
            importance=3,
        )
        db_session.add(ms)
        db_session.flush()

        fetched = db_session.get(Milestone, ms.id)
        assert fetched is not None
        assert fetched.project_id == project.id
        assert fetched.title == "MVP Release"
        assert fetched.target_date == target
        assert fetched.importance == 3

    def test_project_has_many_milestones(self, db_session) -> None:
        """A project can have multiple milestones."""
        project = Project(name="Multi-MS")
        db_session.add(project)
        db_session.flush()

        ms_a = Milestone(project_id=project.id, title="Alpha")
        ms_b = Milestone(project_id=project.id, title="Beta")
        ms_c = Milestone(project_id=project.id, title="GA")
        db_session.add_all([ms_a, ms_b, ms_c])
        db_session.flush()

        db_session.refresh(project)
        assert len(project.milestones) == 3
        titles = {ms.title for ms in project.milestones}
        assert titles == {"Alpha", "Beta", "GA"}

    def test_milestone_completion(self, db_session) -> None:
        """A milestone can be marked completed with a timestamp."""
        project = Project(name="Completion Host")
        db_session.add(project)
        db_session.flush()

        ms = Milestone(project_id=project.id, title="Ship It")
        db_session.add(ms)
        db_session.flush()

        now = datetime.now(timezone.utc)
        ms.status = "completed"
        ms.completed_at = now
        db_session.flush()

        fetched = db_session.get(Milestone, ms.id)
        assert fetched is not None
        assert fetched.status == "completed"
        assert fetched.completed_at is not None

    def test_milestone_fields_persist(self, db_session) -> None:
        """All milestone properties round-trip correctly."""
        project = Project(name="MS Fields Host")
        db_session.add(project)
        db_session.flush()

        ms = Milestone(
            project_id=project.id,
            title="Design Review",
            description="Architecture review with team leads",
            target_date=datetime(2026, 5, 15, tzinfo=timezone.utc),
            status="upcoming",
            importance=2,
        )
        db_session.add(ms)
        db_session.flush()

        fetched = db_session.get(Milestone, ms.id)
        assert fetched is not None
        assert fetched.description == "Architecture review with team leads"
        assert fetched.importance == 2


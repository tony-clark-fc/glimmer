"""Accepted operational artifact persistence tests.

TEST:Domain.Execution.AcceptedArtifactsPersistSeparately
"""

from __future__ import annotations

from datetime import datetime, timezone

from app.models.portfolio import Project, ProjectWorkstream
from app.models.execution import (
    BlockerRecord,
    DecisionRecord,
    RiskRecord,
    WaitingOnRecord,
    WorkItem,
)


class TestAcceptedArtifactsPersistSeparately:
    """TEST:Domain.Execution.AcceptedArtifactsPersistSeparately"""

    def _make_project(self, db_session) -> Project:
        p = Project(name="Execution Test Project")
        db_session.add(p)
        db_session.flush()
        return p

    def test_work_item_persists(self, db_session) -> None:
        project = self._make_project(db_session)
        wi = WorkItem(
            project_id=project.id,
            title="Implement OAuth flow",
            description="Set up Google OAuth consent",
            item_type="task",
            status="open",
            due_date=datetime(2026, 5, 1, tzinfo=timezone.utc),
            owner_hint="backend-team",
            source_provenance={"extracted_action_id": "abc-123"},
            priority_indicators={"urgency": "high", "impact": "critical"},
        )
        db_session.add(wi)
        db_session.flush()

        fetched = db_session.get(WorkItem, wi.id)
        assert fetched is not None
        assert fetched.title == "Implement OAuth flow"
        assert fetched.source_provenance["extracted_action_id"] == "abc-123"
        assert fetched.priority_indicators["urgency"] == "high"

    def test_work_item_links_to_workstream(self, db_session) -> None:
        project = self._make_project(db_session)
        ws = ProjectWorkstream(
            project_id=project.id, title="Foundation"
        )
        db_session.add(ws)
        db_session.flush()

        wi = WorkItem(
            project_id=project.id,
            workstream_id=ws.id,
            title="Database setup",
        )
        db_session.add(wi)
        db_session.flush()

        fetched = db_session.get(WorkItem, wi.id)
        assert fetched.workstream_id == ws.id

    def test_decision_record_persists(self, db_session) -> None:
        project = self._make_project(db_session)
        dr = DecisionRecord(
            project_id=project.id,
            title="Use PostgreSQL",
            decision_text="We will use PostgreSQL as primary storage.",
            rationale="Best fit for structured + retrieval needs.",
            decided_at=datetime(2026, 4, 1, tzinfo=timezone.utc),
        )
        db_session.add(dr)
        db_session.flush()

        fetched = db_session.get(DecisionRecord, dr.id)
        assert fetched is not None
        assert fetched.title == "Use PostgreSQL"

    def test_risk_record_persists(self, db_session) -> None:
        project = self._make_project(db_session)
        rr = RiskRecord(
            project_id=project.id,
            summary="OAuth token refresh may fail silently",
            severity_signal="high",
            likelihood_signal="medium",
            mitigation_notes="Add health-check endpoint for token status",
        )
        db_session.add(rr)
        db_session.flush()

        fetched = db_session.get(RiskRecord, rr.id)
        assert fetched is not None
        assert fetched.severity_signal == "high"

    def test_blocker_record_persists(self, db_session) -> None:
        project = self._make_project(db_session)
        br = BlockerRecord(
            project_id=project.id,
            summary="Waiting for API credentials from IT",
            blocking_what="Connector integration testing",
            owner_hint="IT team",
        )
        db_session.add(br)
        db_session.flush()

        fetched = db_session.get(BlockerRecord, br.id)
        assert fetched is not None
        assert "API credentials" in fetched.summary

    def test_waiting_on_record_persists(self, db_session) -> None:
        project = self._make_project(db_session)
        wr = WaitingOnRecord(
            project_id=project.id,
            waiting_on_whom="Alice Chen (Acme Corp)",
            description="Revised contract terms",
            expected_by=datetime(2026, 5, 15, tzinfo=timezone.utc),
        )
        db_session.add(wr)
        db_session.flush()

        fetched = db_session.get(WaitingOnRecord, wr.id)
        assert fetched is not None
        assert fetched.waiting_on_whom == "Alice Chen (Acme Corp)"
        assert fetched.status == "waiting"

    def test_multiple_artifact_types_coexist(self, db_session) -> None:
        """Multiple accepted artifact types coexist under one project."""
        project = self._make_project(db_session)

        wi = WorkItem(project_id=project.id, title="Task A")
        dr = DecisionRecord(
            project_id=project.id,
            title="Decision A",
            decision_text="We decided A",
        )
        rr = RiskRecord(project_id=project.id, summary="Risk A")
        br = BlockerRecord(project_id=project.id, summary="Blocker A")
        wr = WaitingOnRecord(
            project_id=project.id,
            waiting_on_whom="Bob",
            description="Waiting for docs",
        )
        db_session.add_all([wi, dr, rr, br, wr])
        db_session.flush()

        # All have distinct IDs and persist independently
        assert all(
            db_session.get(type(obj), obj.id) is not None
            for obj in [wi, dr, rr, br, wr]
        )


"""Audit and trace persistence tests.

TEST:Domain.Audit.MeaningfulStateMutation
"""

from __future__ import annotations

import uuid

from app.models.portfolio import Project
from app.models.audit import AuditRecord


class TestAuditMeaningfulStateMutation:
    """TEST:Domain.Audit.MeaningfulStateMutation"""

    def test_audit_record_persists(self, db_session) -> None:
        project = Project(name="Audit Host")
        db_session.add(project)
        db_session.flush()

        audit = AuditRecord(
            entity_type="project",
            entity_id=project.id,
            action="created",
            actor="operator",
            change_summary="Project 'Audit Host' created",
            new_state={"name": "Audit Host", "status": "active"},
        )
        db_session.add(audit)
        db_session.flush()

        fetched = db_session.get(AuditRecord, audit.id)
        assert fetched is not None
        assert fetched.entity_type == "project"
        assert fetched.action == "created"
        assert fetched.actor == "operator"

    def test_audit_records_state_change(self, db_session) -> None:
        """Audit captures both previous and new state."""
        project = Project(name="State Change Host")
        db_session.add(project)
        db_session.flush()

        audit = AuditRecord(
            entity_type="project",
            entity_id=project.id,
            action="updated",
            actor="operator",
            change_summary="Status changed from active to completed",
            previous_state={"status": "active"},
            new_state={"status": "completed"},
        )
        db_session.add(audit)
        db_session.flush()

        fetched = db_session.get(AuditRecord, audit.id)
        assert fetched.previous_state["status"] == "active"
        assert fetched.new_state["status"] == "completed"

    def test_audit_promotion_from_interpreted_to_accepted(self, db_session) -> None:
        """Audit captures promotion of interpreted artifact to accepted state."""
        audit = AuditRecord(
            entity_type="extracted_action",
            entity_id=uuid.uuid4(),
            action="promoted",
            actor="operator",
            change_summary="Extracted action promoted to work item",
            previous_state={"review_state": "pending_review"},
            new_state={"review_state": "accepted"},
            context_metadata={
                "promoted_to": "work_item",
                "work_item_id": str(uuid.uuid4()),
            },
        )
        db_session.add(audit)
        db_session.flush()

        fetched = db_session.get(AuditRecord, audit.id)
        assert fetched.action == "promoted"
        assert fetched.context_metadata["promoted_to"] == "work_item"

    def test_audit_by_system_actor(self, db_session) -> None:
        """System/graph actions are also auditable."""
        audit = AuditRecord(
            entity_type="project_summary",
            entity_id=uuid.uuid4(),
            action="created",
            actor="graph:summary_refresh_node",
            change_summary="Auto-generated project summary v3",
            context_metadata={"graph_run_id": "run-abc-123"},
        )
        db_session.add(audit)
        db_session.flush()

        fetched = db_session.get(AuditRecord, audit.id)
        assert fetched.actor == "graph:summary_refresh_node"
        assert fetched.context_metadata["graph_run_id"] == "run-abc-123"

    def test_multiple_audits_for_same_entity(self, db_session) -> None:
        """Multiple audit records can exist for the same entity."""
        entity_id = uuid.uuid4()

        a1 = AuditRecord(
            entity_type="work_item",
            entity_id=entity_id,
            action="created",
            actor="operator",
        )
        a2 = AuditRecord(
            entity_type="work_item",
            entity_id=entity_id,
            action="updated",
            actor="operator",
            change_summary="Status changed to in_progress",
        )
        a3 = AuditRecord(
            entity_type="work_item",
            entity_id=entity_id,
            action="updated",
            actor="operator",
            change_summary="Status changed to done",
        )
        db_session.add_all([a1, a2, a3])
        db_session.flush()

        from sqlalchemy import select
        result = db_session.execute(
            select(AuditRecord).where(AuditRecord.entity_id == entity_id)
        ).scalars().all()
        assert len(result) == 3
        actions = [r.action for r in result]
        assert actions.count("created") == 1
        assert actions.count("updated") == 2


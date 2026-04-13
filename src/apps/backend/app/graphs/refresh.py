"""Project-memory refresh trigger service.

ARCH:ProjectMemoryRefresh
ARCH:ProjectMemoryRefreshPipeline
ARCH:SummaryRefreshTriggers
ARCH:AuditAndTraceLayer

Triggers traceable project-summary refresh when meaningful
new state arrives. Refresh is visible and auditable —
not a hidden background mutation.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.summary import ProjectSummary, RefreshEvent
from app.models.audit import AuditRecord
from app.models.portfolio import Project
from app.models.execution import WorkItem
from app.models.interpretation import ExtractedAction


# ── Refresh Result ───────────────────────────────────────────────────


class RefreshResult:
    """Result of a project-memory refresh cycle."""

    def __init__(
        self,
        refresh_event_id: uuid.UUID,
        summary_id: Optional[uuid.UUID],
        status: str,
        trigger_type: str,
    ):
        self.refresh_event_id = refresh_event_id
        self.summary_id = summary_id
        self.status = status
        self.trigger_type = trigger_type


# ── Refresh Trigger ──────────────────────────────────────────────────


def trigger_project_refresh(
    session: Session,
    project_id: uuid.UUID,
    triggered_by: str = "system",
    trigger_type: str = "post_triage",
) -> RefreshResult:
    """Trigger a traceable project-memory refresh.

    ARCH:ProjectMemoryRefresh — visible refresh with lineage.
    ARCH:AuditAndTraceLayer — mutation creates audit record.

    Steps:
    1. Create a RefreshEvent to track the cycle
    2. Gather current project state signals
    3. Generate new ProjectSummary (supersedes previous)
    4. Mark old summary as non-current
    5. Audit the refresh
    6. Complete the RefreshEvent
    """
    project = session.get(Project, project_id)
    if not project:
        # Create a failed refresh event for traceability
        # Use project_id=None since the project doesn't exist (FK constraint)
        event = RefreshEvent(
            project_id=None,
            refresh_type=trigger_type,
            triggered_by=triggered_by,
            status="failed",
            input_scope={"error": "Project not found", "requested_project_id": str(project_id)},
        )
        session.add(event)
        session.flush()
        return RefreshResult(
            refresh_event_id=event.id,
            summary_id=None,
            status="failed",
            trigger_type=trigger_type,
        )

    # Create refresh event
    event = RefreshEvent(
        project_id=project_id,
        refresh_type=trigger_type,
        triggered_by=triggered_by,
        status="in_progress",
    )
    session.add(event)
    session.flush()

    # Gather current state signals for summary generation
    open_items = session.execute(
        select(WorkItem).where(
            WorkItem.project_id == project_id,
            WorkItem.status.in_(["open", "in_progress"]),
        )
    ).scalars().all()

    pending_actions = session.execute(
        select(ExtractedAction).where(
            ExtractedAction.linked_project_id == project_id,
            ExtractedAction.review_state == "pending_review",
        )
    ).scalars().all()

    # Build summary text from current state
    summary_parts: list[str] = []
    summary_parts.append(f"Project: {project.name}")
    if project.objective:
        summary_parts.append(f"Objective: {project.objective}")
    if project.status:
        summary_parts.append(f"Status: {project.status}")
    if open_items:
        summary_parts.append(f"Open work items: {len(open_items)}")
        for wi in open_items[:3]:
            summary_parts.append(f"  - {wi.title}")
    if pending_actions:
        summary_parts.append(f"Pending actions awaiting review: {len(pending_actions)}")

    summary_text = "\n".join(summary_parts)

    # Find previous current summary for supersession
    prev_summary = session.execute(
        select(ProjectSummary).where(
            ProjectSummary.project_id == project_id,
            ProjectSummary.is_current == True,  # noqa: E712
        )
    ).scalars().first()

    prev_version = prev_summary.version_marker if prev_summary else 0
    prev_id = prev_summary.id if prev_summary else None

    # Mark old summary as non-current
    if prev_summary:
        prev_summary.is_current = False

    # Create new summary with lineage
    new_summary = ProjectSummary(
        project_id=project_id,
        summary_text=summary_text,
        source_scope_metadata={
            "open_work_items": len(open_items),
            "pending_actions": len(pending_actions),
            "trigger_type": trigger_type,
            "triggered_by": triggered_by,
        },
        version_marker=prev_version + 1,
        supersedes_id=prev_id,
        is_current=True,
    )
    session.add(new_summary)
    session.flush()

    # Update refresh event
    event.status = "completed"
    event.completed_at = datetime.now(timezone.utc)
    event.output_artifact_ids = {"summary_id": str(new_summary.id)}
    event.input_scope = {
        "open_work_items": len(open_items),
        "pending_actions": len(pending_actions),
    }

    # Create audit record for traceability
    audit = AuditRecord(
        entity_type="project_summary",
        entity_id=new_summary.id,
        action="created",
        actor=triggered_by,
        change_summary=f"Project summary refreshed (v{new_summary.version_marker}) via {trigger_type}",
        previous_state={"superseded_summary_id": str(prev_id)} if prev_id else None,
        new_state={"summary_id": str(new_summary.id), "version": new_summary.version_marker},
        context_metadata={"refresh_event_id": str(event.id)},
    )
    session.add(audit)
    session.flush()

    return RefreshResult(
        refresh_event_id=event.id,
        summary_id=new_summary.id,
        status="completed",
        trigger_type=trigger_type,
    )



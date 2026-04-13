"""Projects API routes — portfolio and project workspace surfaces.

ARCH:ProjectStateModel
ARCH:PortfolioViewArchitecture
ARCH:ProjectWorkspaceArchitecture

Thin API surface for project listing and detail retrieval.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_session
from app.models.portfolio import Project
from app.models.execution import WorkItem, BlockerRecord, WaitingOnRecord
from app.models.interpretation import ExtractedAction

router = APIRouter(prefix="/projects", tags=["projects"])


# ── Pydantic contracts ───────────────────────────────────────────


class ProjectSummaryResponse(BaseModel):
    """Lightweight project summary for portfolio view."""
    model_config = {"from_attributes": True}

    id: uuid.UUID
    name: str
    status: str
    objective: Optional[str] = None
    short_summary: Optional[str] = None
    open_items: int = 0
    active_blockers: int = 0
    pending_actions: int = 0
    created_at: datetime


class ProjectDetailResponse(BaseModel):
    """Detailed project info for project workspace."""
    model_config = {"from_attributes": True}

    id: uuid.UUID
    name: str
    status: str
    objective: Optional[str] = None
    short_summary: Optional[str] = None
    phase: Optional[str] = None
    priority_band: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    open_items: list[dict] = []
    blockers: list[dict] = []
    waiting_on: list[dict] = []
    pending_actions: list[dict] = []


# ── Dependency ───────────────────────────────────────────────────


def _get_db():
    session = get_session()
    try:
        yield session
    finally:
        session.close()


# ── Routes ───────────────────────────────────────────────────────


@router.get("", response_model=list[ProjectSummaryResponse])
def list_projects(db: Session = Depends(_get_db)) -> list[ProjectSummaryResponse]:
    """List all projects with attention-demand signals.

    ARCH:PortfolioViewArchitecture
    """
    projects = db.execute(
        select(Project).order_by(Project.created_at.desc())
    ).scalars().all()

    results = []
    for p in projects:
        open_count = db.execute(
            select(func.count()).select_from(WorkItem).where(
                WorkItem.project_id == p.id,
                WorkItem.status.in_(["open", "in_progress"]),
            )
        ).scalar() or 0

        blocker_count = db.execute(
            select(func.count()).select_from(BlockerRecord).where(
                BlockerRecord.project_id == p.id,
                BlockerRecord.status == "active",
            )
        ).scalar() or 0

        pending_count = db.execute(
            select(func.count()).select_from(ExtractedAction).where(
                ExtractedAction.linked_project_id == p.id,
                ExtractedAction.review_state == "pending_review",
            )
        ).scalar() or 0

        results.append(ProjectSummaryResponse(
            id=p.id,
            name=p.name,
            status=p.status,
            objective=p.objective,
            short_summary=p.short_summary,
            open_items=open_count,
            active_blockers=blocker_count,
            pending_actions=pending_count,
            created_at=p.created_at,
        ))

    return results


@router.get("/{project_id}", response_model=ProjectDetailResponse)
def get_project(
    project_id: uuid.UUID,
    db: Session = Depends(_get_db),
) -> ProjectDetailResponse:
    """Get detailed project context for project workspace.

    ARCH:ProjectWorkspaceArchitecture
    """
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    open_items = db.execute(
        select(WorkItem).where(
            WorkItem.project_id == project_id,
            WorkItem.status.in_(["open", "in_progress"]),
        )
    ).scalars().all()

    blockers = db.execute(
        select(BlockerRecord).where(
            BlockerRecord.project_id == project_id,
            BlockerRecord.status == "active",
        )
    ).scalars().all()

    waiting = db.execute(
        select(WaitingOnRecord).where(
            WaitingOnRecord.project_id == project_id,
            WaitingOnRecord.status == "waiting",
        )
    ).scalars().all()

    pending = db.execute(
        select(ExtractedAction).where(
            ExtractedAction.linked_project_id == project_id,
            ExtractedAction.review_state == "pending_review",
        )
    ).scalars().all()

    return ProjectDetailResponse(
        id=project.id,
        name=project.name,
        status=project.status,
        objective=project.objective,
        short_summary=project.short_summary,
        phase=project.phase,
        priority_band=project.priority_band,
        created_at=project.created_at,
        updated_at=project.updated_at,
        open_items=[
            {"id": str(wi.id), "title": wi.title, "status": wi.status,
             "due_date": wi.due_date.isoformat() if wi.due_date else None}
            for wi in open_items
        ],
        blockers=[
            {"id": str(b.id), "summary": b.summary}
            for b in blockers
        ],
        waiting_on=[
            {"id": str(w.id), "waiting_on": w.waiting_on_whom, "description": w.description}
            for w in waiting
        ],
        pending_actions=[
            {"id": str(a.id), "action_text": a.action_text, "urgency": a.urgency_signal}
            for a in pending
        ],
    )




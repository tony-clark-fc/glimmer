"""Research and expert advice API routes.

ARCH:ResearchToolBoundary
ARCH:ExpertAdviceCapability
ARCH:ExpertAdviceReviewBoundary

Thin API surface for triggering research escalations, expert advice,
viewing results, and reviewing research/advice outputs. Routes are thin;
business logic stays in graphs/research.py.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_session
from app.models.research import (
    ExpertAdviceExchange,
    ResearchFinding,
    ResearchRun,
    ResearchSourceReference,
    ResearchSummaryArtifact,
)
from app.graphs.research import determine_escalation_mode

router = APIRouter(prefix="/research", tags=["research"])


# ── Pydantic contracts ───────────────────────────────────────────


class EscalationRequest(BaseModel):
    """Request to trigger a research escalation."""
    prompt: str = Field(..., min_length=1, description="The task or question")
    mode: Optional[str] = Field(
        None, description="Explicit mode: 'research' or 'advice'. Auto-detected if omitted."
    )
    gemini_mode: str = Field(
        default="Pro", description="Gemini mode for expert advice: Fast, Thinking, Pro"
    )
    project_id: Optional[uuid.UUID] = Field(None, description="Linked project")
    document_name: Optional[str] = Field(
        None, description="Document name for deep research"
    )


class EscalationResponse(BaseModel):
    """Response from a research escalation."""
    escalation_mode: str
    status: str
    research_run_id: Optional[uuid.UUID] = None
    expert_advice_exchange_id: Optional[uuid.UUID] = None
    document_url: Optional[str] = None
    response_text: Optional[str] = None
    error_message: Optional[str] = None


class RoutingPreviewResponse(BaseModel):
    """Preview of how a prompt would be routed."""
    prompt_preview: str
    determined_mode: str


class ReviewActionRequest(BaseModel):
    """Request to review (accept/reject) a research or advice result."""
    action: str = Field(
        ..., description="Review action: 'accepted' or 'rejected'"
    )


class ResearchRunResponse(BaseModel):
    """Response model for a research run."""
    model_config = {"from_attributes": True}

    id: uuid.UUID
    invocation_origin: str
    project_id: Optional[uuid.UUID] = None
    research_query: str
    document_name: Optional[str] = None
    status: str
    document_url: Optional[str] = None
    error_message: Optional[str] = None
    summary_review_state: Optional[str] = None
    findings_count: int = 0
    sources_count: int = 0
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ResearchFindingResponse(BaseModel):
    """Response model for a research finding."""
    model_config = {"from_attributes": True}

    id: uuid.UUID
    finding_type: str
    content: str
    confidence_signal: Optional[str] = None
    source_url: Optional[str] = None
    ordering: Optional[int] = None
    created_at: datetime


class ResearchSourceReferenceResponse(BaseModel):
    """Response model for a research source reference."""
    model_config = {"from_attributes": True}

    id: uuid.UUID
    source_url: Optional[str] = None
    source_title: Optional[str] = None
    source_description: Optional[str] = None
    relevance_notes: Optional[str] = None
    created_at: datetime


class ResearchSummaryResponse(BaseModel):
    """Response model for a research summary artifact."""
    model_config = {"from_attributes": True}

    id: uuid.UUID
    summary_text: str
    review_state: str
    created_at: datetime


class ResearchRunDetailResponse(ResearchRunResponse):
    """Detailed response for a single research run including findings, sources, and summary."""
    findings: list[ResearchFindingResponse] = []
    sources: list[ResearchSourceReferenceResponse] = []
    summary: Optional[ResearchSummaryResponse] = None


class ExpertAdviceExchangeResponse(BaseModel):
    """Response model for an expert advice exchange."""
    model_config = {"from_attributes": True}

    id: uuid.UUID
    invocation_origin: str
    project_id: Optional[uuid.UUID] = None
    prompt: str
    gemini_mode: str
    response_text: Optional[str] = None
    duration_ms: Optional[int] = None
    status: str
    review_state: str
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


# ── Dependency ───────────────────────────────────────────────────


def _get_db():
    """Yield a database session for request lifecycle."""
    session = get_session()
    try:
        yield session
    finally:
        session.close()


# ── Routing Preview ──────────────────────────────────────────────


@router.post("/preview-routing", response_model=RoutingPreviewResponse)
def preview_routing(body: EscalationRequest) -> RoutingPreviewResponse:
    """Preview how a prompt would be routed without executing.

    TEST:ExpertAdvice.Routing.EscalationDistinguishesResearchFromAdvice
    """
    mode = determine_escalation_mode(body.prompt, explicit_mode=body.mode)
    return RoutingPreviewResponse(
        prompt_preview=body.prompt[:100],
        determined_mode=mode,
    )


# ── Research Runs ────────────────────────────────────────────────


@router.get("/runs", response_model=list[ResearchRunResponse])
def list_research_runs(
    limit: int = 20,
    db: Session = Depends(_get_db),
) -> list[ResearchRunResponse]:
    """List recent research runs with summary counts."""
    runs = db.execute(
        select(ResearchRun)
        .order_by(ResearchRun.created_at.desc())
        .limit(limit)
    ).scalars().all()

    result = []
    for r in runs:
        findings_count = db.execute(
            select(func.count(ResearchFinding.id)).where(
                ResearchFinding.research_run_id == r.id
            )
        ).scalar() or 0
        sources_count = db.execute(
            select(func.count(ResearchSourceReference.id)).where(
                ResearchSourceReference.research_run_id == r.id
            )
        ).scalar() or 0
        summary = db.execute(
            select(ResearchSummaryArtifact).where(
                ResearchSummaryArtifact.research_run_id == r.id
            )
        ).scalar()
        result.append(ResearchRunResponse(
            id=r.id,
            invocation_origin=r.invocation_origin,
            project_id=r.project_id,
            research_query=r.research_query,
            document_name=r.document_name,
            status=r.status,
            document_url=r.document_url,
            error_message=r.error_message,
            summary_review_state=summary.review_state if summary else None,
            findings_count=findings_count,
            sources_count=sources_count,
            created_at=r.created_at,
            started_at=r.started_at,
            completed_at=r.completed_at,
        ))
    return result


@router.get("/runs/{run_id}", response_model=ResearchRunDetailResponse)
def get_research_run(
    run_id: uuid.UUID,
    db: Session = Depends(_get_db),
) -> ResearchRunDetailResponse:
    """Get a specific research run with full detail: findings, sources, summary."""
    run = db.get(ResearchRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Research run not found")

    findings = db.execute(
        select(ResearchFinding)
        .where(ResearchFinding.research_run_id == run_id)
        .order_by(ResearchFinding.ordering, ResearchFinding.created_at)
    ).scalars().all()

    sources = db.execute(
        select(ResearchSourceReference)
        .where(ResearchSourceReference.research_run_id == run_id)
        .order_by(ResearchSourceReference.created_at)
    ).scalars().all()

    summary_row = db.execute(
        select(ResearchSummaryArtifact).where(
            ResearchSummaryArtifact.research_run_id == run_id
        )
    ).scalar()

    return ResearchRunDetailResponse(
        id=run.id,
        invocation_origin=run.invocation_origin,
        project_id=run.project_id,
        research_query=run.research_query,
        document_name=run.document_name,
        status=run.status,
        document_url=run.document_url,
        error_message=run.error_message,
        summary_review_state=summary_row.review_state if summary_row else None,
        findings_count=len(findings),
        sources_count=len(sources),
        created_at=run.created_at,
        started_at=run.started_at,
        completed_at=run.completed_at,
        findings=[ResearchFindingResponse.model_validate(f) for f in findings],
        sources=[ResearchSourceReferenceResponse.model_validate(s) for s in sources],
        summary=ResearchSummaryResponse.model_validate(summary_row) if summary_row else None,
    )


# ── Research Run Summary Review ──────────────────────────────────


@router.patch("/runs/{run_id}/summary/review")
def review_research_summary(
    run_id: uuid.UUID,
    body: ReviewActionRequest,
    db: Session = Depends(_get_db),
) -> dict:
    """Accept or reject a research run's summary artifact.

    ARCH:ExpertAdviceReviewBoundary
    TEST:Research.Output.ResultsReenterWorkflowSafely
    """
    if body.action not in ("accepted", "rejected"):
        raise HTTPException(status_code=400, detail="action must be 'accepted' or 'rejected'")

    summary = db.execute(
        select(ResearchSummaryArtifact).where(
            ResearchSummaryArtifact.research_run_id == run_id
        )
    ).scalar()
    if not summary:
        raise HTTPException(status_code=404, detail="Research run or summary not found")

    summary.review_state = body.action
    db.commit()
    return {"id": str(summary.id), "review_state": summary.review_state}


# ── Expert Advice Exchanges ──────────────────────────────────────


@router.get("/exchanges", response_model=list[ExpertAdviceExchangeResponse])
def list_exchanges(
    limit: int = 20,
    db: Session = Depends(_get_db),
) -> list[ExpertAdviceExchangeResponse]:
    """List recent expert advice exchanges."""
    exchanges = db.execute(
        select(ExpertAdviceExchange)
        .order_by(ExpertAdviceExchange.created_at.desc())
        .limit(limit)
    ).scalars().all()
    return [ExpertAdviceExchangeResponse.model_validate(e) for e in exchanges]


@router.get(
    "/exchanges/{exchange_id}",
    response_model=ExpertAdviceExchangeResponse,
)
def get_exchange(
    exchange_id: uuid.UUID,
    db: Session = Depends(_get_db),
) -> ExpertAdviceExchangeResponse:
    """Get a specific expert advice exchange."""
    exchange = db.get(ExpertAdviceExchange, exchange_id)
    if not exchange:
        raise HTTPException(status_code=404, detail="Exchange not found")
    return ExpertAdviceExchangeResponse.model_validate(exchange)


# ── Expert Advice Exchange Review ────────────────────────────────


@router.patch("/exchanges/{exchange_id}/review")
def review_exchange(
    exchange_id: uuid.UUID,
    body: ReviewActionRequest,
    db: Session = Depends(_get_db),
) -> dict:
    """Accept or reject an expert advice exchange response.

    ARCH:ExpertAdviceReviewBoundary
    TEST:ExpertAdvice.Output.ResponseEntersAsInterpretedCandidate
    """
    if body.action not in ("accepted", "rejected"):
        raise HTTPException(status_code=400, detail="action must be 'accepted' or 'rejected'")

    exchange = db.get(ExpertAdviceExchange, exchange_id)
    if not exchange:
        raise HTTPException(status_code=404, detail="Exchange not found")

    exchange.review_state = body.action
    db.commit()
    return {"id": str(exchange.id), "review_state": exchange.review_state}



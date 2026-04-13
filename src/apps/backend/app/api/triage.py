"""Triage and priority API routes — review actions, focus packs, priority views.

ARCH:TriageViewArchitecture
ARCH:TodayViewArchitecture
ARCH:ReviewQueueArchitecture
ARCH:ReviewGateArchitecture
ARCH:NoAutoSendPolicy

Thin API surface for triage review, focus-pack retrieval, and
priority guidance. Routes are thin; business logic stays in
services/graphs layers.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_session
from app.models.interpretation import (
    MessageClassification,
    ExtractedAction,
    VALID_REVIEW_STATES,
)
from app.models.drafting import FocusPack
from app.graphs.planner import generate_focus_pack, suggest_next_steps


router = APIRouter(prefix="/triage", tags=["triage"])


# ── Pydantic contracts ───────────────────────────────────────────


class ReviewActionRequest(BaseModel):
    """Request body for a review action on an interpreted artifact."""
    action: str = Field(..., description="Review action: accepted, rejected, amended")
    amended_text: Optional[str] = Field(None, description="Amended text if action is 'amended'")


class ClassificationResponse(BaseModel):
    """Response model for a message classification."""
    model_config = {"from_attributes": True}

    id: uuid.UUID
    source_record_id: uuid.UUID
    source_record_type: str
    selected_project_id: Optional[uuid.UUID] = None
    confidence: Optional[float] = None
    ambiguity_flag: bool = False
    classification_rationale: Optional[str] = None
    review_state: str
    created_at: datetime


class ExtractedActionResponse(BaseModel):
    """Response model for an extracted action."""
    model_config = {"from_attributes": True}

    id: uuid.UUID
    source_record_id: uuid.UUID
    source_record_type: str
    linked_project_id: Optional[uuid.UUID] = None
    action_text: str
    urgency_signal: Optional[str] = None
    review_state: str
    created_at: datetime


class FocusPackResponse(BaseModel):
    """Response model for a focus pack."""
    model_config = {"from_attributes": True}

    id: uuid.UUID
    generated_at: datetime
    top_actions: Optional[dict] = None
    high_risk_items: Optional[dict] = None
    waiting_on_items: Optional[dict] = None
    reply_debt_summary: Optional[str] = None
    calendar_pressure_summary: Optional[str] = None


class NextStepResponse(BaseModel):
    """Response model for a next-step suggestion."""
    project_id: uuid.UUID
    suggestion: str
    rationale: str
    is_restructuring: bool = False


class PriorityItemResponse(BaseModel):
    """Response model for a priority item."""
    item_id: str
    item_type: str
    project_id: Optional[str] = None
    priority_score: float
    rationale: str
    title: str


class GenerateFocusPackRequest(BaseModel):
    """Request body for focus pack generation."""
    project_ids: Optional[list[uuid.UUID]] = None
    trigger_type: str = "on_demand"


class ReviewQueueResponse(BaseModel):
    """Response model for the review queue."""
    classifications: list[ClassificationResponse] = []
    actions: list[ExtractedActionResponse] = []
    total_pending: int = 0


# ── Dependency ───────────────────────────────────────────────────


def _get_db():
    """Yield a database session for request lifecycle."""
    session = get_session()
    try:
        yield session
    finally:
        session.close()


# ── Review Queue ─────────────────────────────────────────────────


@router.get("/review-queue", response_model=ReviewQueueResponse)
def get_review_queue(db: Session = Depends(_get_db)) -> ReviewQueueResponse:
    """Get all items pending review.

    ARCH:ReviewQueueArchitecture
    TEST:ApplicationSurface.TriageAndPriorityEndpointsSupportReviewActions
    """
    classifications = db.execute(
        select(MessageClassification).where(
            MessageClassification.review_state == "pending_review"
        ).order_by(MessageClassification.created_at.desc())
    ).scalars().all()

    actions = db.execute(
        select(ExtractedAction).where(
            ExtractedAction.review_state == "pending_review"
        ).order_by(ExtractedAction.created_at.desc())
    ).scalars().all()

    return ReviewQueueResponse(
        classifications=[ClassificationResponse.model_validate(c) for c in classifications],
        actions=[ExtractedActionResponse.model_validate(a) for a in actions],
        total_pending=len(classifications) + len(actions),
    )


# ── Review Actions ───────────────────────────────────────────────


@router.patch(
    "/classifications/{classification_id}/review",
    response_model=ClassificationResponse,
)
def review_classification(
    classification_id: uuid.UUID,
    body: ReviewActionRequest,
    db: Session = Depends(_get_db),
) -> ClassificationResponse:
    """Apply a review action to a classification.

    ARCH:ReviewGateArchitecture — operator review actions.
    TEST:ApplicationSurface.TriageAndPriorityEndpointsSupportReviewActions
    """
    classification = db.get(MessageClassification, classification_id)
    if not classification:
        raise HTTPException(status_code=404, detail="Classification not found")

    if body.action not in ("accepted", "rejected", "amended"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid review action: {body.action}. Must be accepted, rejected, or amended",
        )

    if classification.review_state != "pending_review":
        raise HTTPException(
            status_code=409,
            detail=f"Classification already reviewed: {classification.review_state}",
        )

    classification.review_state = body.action
    classification.reviewed_at = datetime.now(timezone.utc)

    if body.action == "amended" and body.amended_text:
        classification.classification_rationale = body.amended_text

    db.commit()
    db.refresh(classification)
    return ClassificationResponse.model_validate(classification)


@router.patch(
    "/actions/{action_id}/review",
    response_model=ExtractedActionResponse,
)
def review_action(
    action_id: uuid.UUID,
    body: ReviewActionRequest,
    db: Session = Depends(_get_db),
) -> ExtractedActionResponse:
    """Apply a review action to an extracted action.

    ARCH:ReviewGateArchitecture — operator review actions.
    TEST:Security.ReviewGate.ExternalImpactRequiresApproval
    """
    action = db.get(ExtractedAction, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")

    if body.action not in ("accepted", "rejected", "amended"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid review action: {body.action}",
        )

    if action.review_state != "pending_review":
        raise HTTPException(
            status_code=409,
            detail=f"Action already reviewed: {action.review_state}",
        )

    action.review_state = body.action
    action.reviewed_at = datetime.now(timezone.utc)

    if body.action == "amended" and body.amended_text:
        action.action_text = body.amended_text

    db.commit()
    db.refresh(action)
    return ExtractedActionResponse.model_validate(action)


# ── Focus Pack ───────────────────────────────────────────────────


@router.post("/focus-pack", response_model=FocusPackResponse, status_code=201)
def create_focus_pack(
    body: GenerateFocusPackRequest,
    db: Session = Depends(_get_db),
) -> FocusPackResponse:
    """Generate a new focus pack from current operational state.

    ARCH:PlannerGraph
    ARCH:FocusPackModel
    TEST:Planner.PriorityRationale.VisibleInApplicationSurface
    """
    result = generate_focus_pack(
        session=db,
        project_ids=body.project_ids,
        trigger_type=body.trigger_type,
    )
    db.commit()

    focus = db.get(FocusPack, result.focus_pack_id)
    return FocusPackResponse.model_validate(focus)


@router.get("/focus-pack/latest", response_model=FocusPackResponse)
def get_latest_focus_pack(
    db: Session = Depends(_get_db),
) -> FocusPackResponse:
    """Get the most recent focus pack.

    ARCH:TodayViewArchitecture
    """
    focus = db.execute(
        select(FocusPack).order_by(FocusPack.created_at.desc())
    ).scalars().first()

    if not focus:
        raise HTTPException(status_code=404, detail="No focus pack available")

    return FocusPackResponse.model_validate(focus)


# ── Next Steps ───────────────────────────────────────────────────


@router.get(
    "/projects/{project_id}/next-steps",
    response_model=list[NextStepResponse],
)
def get_next_steps(
    project_id: uuid.UUID,
    db: Session = Depends(_get_db),
) -> list[NextStepResponse]:
    """Get advisory next-step suggestions for a project.

    ARCH:PlannerGraphReviewGate — advisory only.
    TEST:Planner.WorkBreakdown.SuggestsNextStepWithoutSilentRestructure
    """
    suggestions = suggest_next_steps(session=db, project_id=project_id)
    return [
        NextStepResponse(
            project_id=s.project_id,
            suggestion=s.suggestion,
            rationale=s.rationale,
            is_restructuring=s.is_restructuring,
        )
        for s in suggestions
    ]



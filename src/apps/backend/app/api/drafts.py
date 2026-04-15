"""Drafts API routes — draft creation, listing, and detail retrieval.

ARCH:DraftWorkspaceArchitecture
ARCH:DraftModel
ARCH:NoAutoSendPolicy
ARCH:DraftingGraphNoAutoSend

Thin API surface for draft creation, listing, and variant retrieval.
Drafts are always review-only — no send capability exposed.

When creating a draft with an empty body_content, the LLM generates
the body from the provided context (when enabled).  The no-auto-send
boundary is preserved regardless of which path produces the body.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.drafting import Draft, DraftVariant

router = APIRouter(prefix="/drafts", tags=["drafts"])


# ── Pydantic contracts ───────────────────────────────────────────


class CreateDraftRequest(BaseModel):
    """Request body for creating a new draft.

    When body_content is empty or omitted, the LLM generates the body
    from the provided context fields (when LLM drafting is enabled).
    """
    body_content: str = Field("", description="Draft body text (empty to request LLM generation)")
    intent: str = Field("reply", description="Intent: reply, follow_up, initiate, brief")
    source_message_id: Optional[uuid.UUID] = Field(None, description="Source message this draft responds to")
    source_record_type: Optional[str] = Field(None, description="Source record type")
    project_id: Optional[uuid.UUID] = Field(None, description="Linked project")
    stakeholder_ids: Optional[list[uuid.UUID]] = Field(None, description="Linked stakeholder IDs")
    channel_type: Optional[str] = Field(None, description="Channel: email, telegram")
    tone_mode: Optional[str] = Field(None, description="Tone: concise, warm, firm, executive")
    rationale_summary: Optional[str] = Field(None, description="Why this draft is being created")
    # LLM context fields — used when body_content is empty
    context_summary: Optional[str] = Field(None, description="Summary of the conversation context for LLM")
    original_message_summary: Optional[str] = Field(None, description="Summary of the message being replied to")
    project_name: Optional[str] = Field(None, description="Project name for LLM context")
    stakeholder_names: Optional[list[str]] = Field(None, description="Stakeholder names for LLM context")
    key_points: Optional[list[str]] = Field(None, description="Key points the draft should cover")


class DraftVariantResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    variant_label: str
    body_content: str
    created_at: datetime


class DraftListResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    intent_label: Optional[str] = None
    channel_type: Optional[str] = None
    tone_mode: Optional[str] = None
    status: str
    body_content: str
    rationale_summary: Optional[str] = None
    linked_project_id: Optional[uuid.UUID] = None
    created_at: datetime


class DraftDetailResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    intent_label: Optional[str] = None
    channel_type: Optional[str] = None
    tone_mode: Optional[str] = None
    status: str
    body_content: str
    rationale_summary: Optional[str] = None
    linked_project_id: Optional[uuid.UUID] = None
    linked_stakeholder_ids: Optional[dict] = None
    source_message_id: Optional[uuid.UUID] = None
    source_record_type: Optional[str] = None
    version_number: int = 1
    created_at: datetime
    updated_at: datetime
    variants: list[DraftVariantResponse] = []




# ── Routes ───────────────────────────────────────────────────────


@router.post("", response_model=DraftDetailResponse, status_code=201)
def create_draft_endpoint(
    body: CreateDraftRequest,
    db: Session = Depends(get_db),
) -> DraftDetailResponse:
    """Create a new draft, optionally with LLM-generated body.

    ARCH:DraftingGraphNoAutoSend — auto_send is ALWAYS blocked.
    ARCH:ReviewGateArchitecture — drafts are ALWAYS review-required.
    ARCH:NoAutoSendPolicy — this creates a draft, NOT a sent message.
    TEST:Drafting.API.CreateDraftReturnsReviewableDraft

    When body_content is empty, the LLM generates body text from the
    provided context (context_summary, original_message_summary, etc.).
    If LLM is disabled or fails, an empty body is persisted — the
    operator can edit it in the workspace.
    """
    from app.graphs.drafting import create_draft_enhanced

    result = create_draft_enhanced(
        db,
        body_content=body.body_content,
        intent=body.intent,
        source_message_id=body.source_message_id,
        source_record_type=body.source_record_type,
        project_id=body.project_id,
        stakeholder_ids=body.stakeholder_ids,
        channel_type=body.channel_type,
        tone_mode=body.tone_mode,
        rationale_summary=body.rationale_summary,
        context_summary=body.context_summary,
        original_message_summary=body.original_message_summary,
        project_name=body.project_name,
        stakeholder_names=body.stakeholder_names,
        key_points=body.key_points,
    )
    db.commit()

    # Load the persisted draft with variants for the response
    draft = db.get(Draft, result.draft_id)
    variants = db.execute(
        select(DraftVariant).where(DraftVariant.draft_id == result.draft_id)
    ).scalars().all()

    detail = DraftDetailResponse.model_validate(draft)
    detail.variants = [DraftVariantResponse.model_validate(v) for v in variants]
    return detail


@router.get("", response_model=list[DraftListResponse])
def list_drafts(db: Session = Depends(get_db)) -> list[DraftListResponse]:
    """List all drafts, most recent first.

    ARCH:DraftWorkspaceArchitecture
    """
    drafts = db.execute(
        select(Draft).order_by(Draft.created_at.desc())
    ).scalars().all()

    return [DraftListResponse.model_validate(d) for d in drafts]


@router.get("/{draft_id}", response_model=DraftDetailResponse)
def get_draft(
    draft_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> DraftDetailResponse:
    """Get a draft with its variants.

    ARCH:DraftWorkspaceArchitecture
    """
    draft = db.get(Draft, draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    variants = db.execute(
        select(DraftVariant).where(DraftVariant.draft_id == draft_id)
    ).scalars().all()

    detail = DraftDetailResponse.model_validate(draft)
    detail.variants = [DraftVariantResponse.model_validate(v) for v in variants]
    return detail



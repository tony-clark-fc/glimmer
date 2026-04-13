"""Drafts API routes — draft listing and detail retrieval.

ARCH:DraftWorkspaceArchitecture
ARCH:DraftModel
ARCH:NoAutoSendPolicy

Thin API surface for draft listing and variant retrieval.
Drafts are always review-only — no send capability exposed.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_session
from app.models.drafting import Draft, DraftVariant

router = APIRouter(prefix="/drafts", tags=["drafts"])


# ── Pydantic contracts ───────────────────────────────────────────


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


# ── Dependency ───────────────────────────────────────────────────


def _get_db():
    session = get_session()
    try:
        yield session
    finally:
        session.close()


# ── Routes ───────────────────────────────────────────────────────


@router.get("", response_model=list[DraftListResponse])
def list_drafts(db: Session = Depends(_get_db)) -> list[DraftListResponse]:
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
    db: Session = Depends(_get_db),
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



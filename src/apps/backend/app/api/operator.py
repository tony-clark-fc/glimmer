"""Operator API routes — thin CRUD surface for PrimaryOperator.

ARCH:PrimaryOperatorModel

Routes are thin; business logic belongs in services/domain layers.
"""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.operator import PrimaryOperator

router = APIRouter(prefix="/operator", tags=["operator"])


# ── Pydantic contracts ───────────────────────────────────────────


class OperatorCreate(BaseModel):
    """Request body for creating the primary operator."""

    display_name: str = Field(..., min_length=1, max_length=255)
    preferred_timezone: Optional[str] = None
    preferred_working_hours: Optional[str] = None
    preferred_language: Optional[str] = None
    tone_preferences: Optional[str] = None
    channel_preferences: Optional[dict] = None
    summary_preferences: Optional[dict] = None
    escalation_preferences: Optional[dict] = None


class OperatorUpdate(BaseModel):
    """Request body for updating operator preferences."""

    display_name: Optional[str] = Field(None, min_length=1, max_length=255)
    preferred_timezone: Optional[str] = None
    preferred_working_hours: Optional[str] = None
    preferred_language: Optional[str] = None
    tone_preferences: Optional[str] = None
    channel_preferences: Optional[dict] = None
    summary_preferences: Optional[dict] = None
    escalation_preferences: Optional[dict] = None


class OperatorResponse(BaseModel):
    """Response body representing the primary operator."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    display_name: str
    preferred_timezone: Optional[str] = None
    preferred_working_hours: Optional[str] = None
    preferred_language: Optional[str] = None
    tone_preferences: Optional[str] = None
    channel_preferences: Optional[dict] = None
    summary_preferences: Optional[dict] = None
    escalation_preferences: Optional[dict] = None




# ── Routes ───────────────────────────────────────────────────────


@router.get("", response_model=OperatorResponse)
def get_operator(db: Session = Depends(get_db)) -> OperatorResponse:
    """Return the primary operator.

    MVP assumes a single operator.  Returns 404 if none exists yet.
    """
    op = db.query(PrimaryOperator).first()
    if op is None:
        raise HTTPException(status_code=404, detail="No operator configured")
    return OperatorResponse.model_validate(op)


@router.post("", response_model=OperatorResponse, status_code=201)
def create_operator(
    body: OperatorCreate,
    db: Session = Depends(get_db),
) -> OperatorResponse:
    """Create the primary operator.

    MVP allows only one operator.  Returns 409 if one already exists.
    """
    existing = db.query(PrimaryOperator).first()
    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="Primary operator already exists",
        )
    op = PrimaryOperator(**body.model_dump(exclude_unset=True))
    db.add(op)
    db.commit()
    db.refresh(op)
    return OperatorResponse.model_validate(op)


@router.patch("", response_model=OperatorResponse)
def update_operator(
    body: OperatorUpdate,
    db: Session = Depends(get_db),
) -> OperatorResponse:
    """Update operator preferences.

    Only supplied fields are updated.  Returns 404 if none exists.
    """
    op = db.query(PrimaryOperator).first()
    if op is None:
        raise HTTPException(status_code=404, detail="No operator configured")

    updates = body.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(op, field, value)

    db.commit()
    db.refresh(op)
    return OperatorResponse.model_validate(op)


"""Persona asset API — context-aware selection with fallback.

ARCH:VisualPersonaSelection
ARCH:VisualPersonaRenderingRules
REQ:VisualPersonaSupport
REQ:ContextAwareVisualPresentation

Serves managed persona assets for frontend rendering.
Selection is driven by classification labels and interaction context.
Falls back to the default asset if no specific match exists.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db import get_session
from app.models.persona import PersonaAsset, PersonaClassification

router = APIRouter(prefix="/persona", tags=["persona"])


# ── Response contracts ────────────────────────────────────────────

class PersonaClassificationResponse(BaseModel):
    classification_type: str
    classification_value: str


class PersonaAssetResponse(BaseModel):
    id: str
    label: str
    asset_path: str
    asset_type: str
    is_default: bool
    classifications: list[PersonaClassificationResponse]


class PersonaSelectionResponse(BaseModel):
    """Response for context-aware persona selection."""
    asset: PersonaAssetResponse | None
    selection_reason: str
    fallback_used: bool


# ── Selection logic ───────────────────────────────────────────────

# Mapping from interaction context to classification suitability values
CONTEXT_SUITABILITY_MAP: dict[str, list[str]] = {
    "briefing": ["briefing", "focused", "executive"],
    "today": ["briefing", "focused", "executive"],
    "drafting": ["drafting", "professional", "warm"],
    "draft": ["drafting", "professional", "warm"],
    "voice": ["supportive", "warm", "conversational"],
    "triage": ["focused", "executive"],
    "review": ["focused", "professional"],
}


def _select_persona_for_context(
    db: Session,
    context: str | None,
) -> tuple[PersonaAsset | None, str, bool]:
    """Select a persona asset for the given interaction context.

    Returns (asset, reason, fallback_used).
    """
    # If context is provided, try to find a matching active asset
    if context:
        suitability_values = CONTEXT_SUITABILITY_MAP.get(context, [])
        if suitability_values:
            stmt = (
                select(PersonaAsset)
                .join(PersonaAsset.classifications)
                .where(
                    PersonaAsset.is_active == True,  # noqa: E712
                    PersonaClassification.classification_value.in_(
                        suitability_values
                    ),
                )
                .options(selectinload(PersonaAsset.classifications))
                .limit(1)
            )
            asset = db.execute(stmt).scalar_one_or_none()
            if asset is not None:
                return (
                    asset,
                    f"Selected for context '{context}' based on classification match",
                    False,
                )

    # Fall back to default active asset
    default_stmt = (
        select(PersonaAsset)
        .where(
            PersonaAsset.is_active == True,  # noqa: E712
            PersonaAsset.is_default == True,  # noqa: E712
        )
        .options(selectinload(PersonaAsset.classifications))
        .limit(1)
    )
    default_asset = db.execute(default_stmt).scalar_one_or_none()
    if default_asset is not None:
        reason = (
            f"Fallback to default — no context-specific match for '{context}'"
            if context
            else "Default persona asset (no context specified)"
        )
        return (default_asset, reason, True)

    # No active assets at all — fall back to any active asset
    any_stmt = (
        select(PersonaAsset)
        .where(PersonaAsset.is_active == True)  # noqa: E712
        .options(selectinload(PersonaAsset.classifications))
        .limit(1)
    )
    any_asset = db.execute(any_stmt).scalar_one_or_none()
    if any_asset is not None:
        return (any_asset, "Fallback to first active asset — no default configured", True)

    return (None, "No active persona assets available", True)


def _asset_to_response(asset: PersonaAsset) -> PersonaAssetResponse:
    return PersonaAssetResponse(
        id=str(asset.id),
        label=asset.label,
        asset_path=asset.asset_path,
        asset_type=asset.asset_type,
        is_default=asset.is_default,
        classifications=[
            PersonaClassificationResponse(
                classification_type=c.classification_type,
                classification_value=c.classification_value,
            )
            for c in asset.classifications
        ],
    )


# ── Routes ────────────────────────────────────────────────────────

@router.get("/select")
def select_persona(
    context: Optional[str] = None,
    db: Session = Depends(get_session),
) -> PersonaSelectionResponse:
    """Select a persona asset for a given interaction context.

    If no context is provided, returns the default persona.
    If no matching persona exists, falls back to default, then any active asset.
    If no active assets exist at all, returns asset=null.
    """
    asset, reason, fallback_used = _select_persona_for_context(db, context)
    return PersonaSelectionResponse(
        asset=_asset_to_response(asset) if asset else None,
        selection_reason=reason,
        fallback_used=fallback_used,
    )


@router.get("/assets")
def list_persona_assets(
    db: Session = Depends(get_session),
) -> list[PersonaAssetResponse]:
    """List all active persona assets."""
    stmt = (
        select(PersonaAsset)
        .where(PersonaAsset.is_active == True)  # noqa: E712
        .options(selectinload(PersonaAsset.classifications))
        .order_by(PersonaAsset.label)
    )
    assets = db.execute(stmt).scalars().all()
    return [_asset_to_response(a) for a in assets]



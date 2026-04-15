"""Contextual "Ask Glimmer" API — cross-surface element-scoped interaction.

PLAN:WorkstreamE.PackageE16.ContextualAskGlimmer
ARCH:ContextualAskGlimmerInteraction
REQ:ContextualAskGlimmer
REQ:HumanApprovalBoundaries

Provides a single endpoint for the operator to ask Glimmer a contextual
question about any data element visible on any workspace surface.

Responses include a review_required flag — if the response implies an
externally meaningful action, it must enter the standard review flow.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

from app.inference.orchestration import contextual_ask_smart

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ask", tags=["ask-glimmer"])


# ── Request/Response contracts ────────────────────────────────────────


class ContextualAskRequest(BaseModel):
    """Request body for a contextual Ask Glimmer interaction."""

    element_type: str
    element_id: str
    element_context: dict[str, Any] = {}
    surface: str
    question: str

    @field_validator("question")
    @classmethod
    def question_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Question must not be empty.")
        return v.strip()

    @field_validator("element_type")
    @classmethod
    def element_type_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Element type must not be empty.")
        return v.strip()

    @field_validator("surface")
    @classmethod
    def surface_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Surface must not be empty.")
        return v.strip()


class ContextualAskResponse(BaseModel):
    """Response body from a contextual Ask Glimmer interaction."""

    reply: str
    review_required: bool
    review_reason: str | None = None
    used_llm: bool
    inference_latency_ms: float = 0.0


# ── Endpoint ──────────────────────────────────────────────────────────


@router.post("/contextual", response_model=ContextualAskResponse, status_code=200)
async def ask_glimmer_contextual(request: ContextualAskRequest) -> ContextualAskResponse:
    """Ask Glimmer a question about a specific workspace data element.

    ARCH:ContextualAskGlimmerInteraction
    ARCH:ReviewGateArchitecture — review_required flag preserved in response.

    The request includes the element type, its context data, the workspace
    surface, and the operator's question. The response includes the answer
    and a review_required flag for review-gate compliance.
    """
    try:
        result = await contextual_ask_smart(
            element_type=request.element_type,
            element_id=request.element_id,
            element_context=request.element_context,
            surface=request.surface,
            question=request.question,
        )

        return ContextualAskResponse(
            reply=result.reply_content,
            review_required=result.review_required,
            review_reason=result.review_reason,
            used_llm=result.used_llm,
            inference_latency_ms=result.inference_latency_ms,
        )

    except Exception as exc:
        logger.error("Contextual ask failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to process contextual question.",
        ) from exc


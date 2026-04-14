"""LLM-enhanced orchestration — wires LLM tasks into existing graph flows.

PLAN:WorkstreamI.PackageI8.OrchestrationWiring
TEST:LLM.Orchestration.TriagePipelineUsesLLMWhenAvailable
TEST:LLM.Orchestration.FallbackChainWorksCleanly
TEST:LLM.Safety.ReviewGatesNotWeakened
TEST:LLM.Safety.ProvenanceNotFlattened
TEST:LLM.Safety.NoAutoSendNotWeakened

Provides fallback-aware orchestration functions that:
1. Try LLM inference first
2. Fall back to deterministic logic on failure
3. Preserve all safety boundaries (review gates, no-auto-send, provenance)
4. Track which path was used for operational visibility

These functions are the integration point between the inference layer
and the existing graph services. They do NOT replace the graph services —
they wrap them with LLM-first-then-fallback behavior.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from typing import Optional

from sqlalchemy.orm import Session

from app.inference.base import InferenceError
from app.inference.config import InferenceSettings
from app.inference.openai_compat import OpenAICompatibleProvider
from app.inference.tasks.classification import (
    LLMClassificationResult,
    classify_project_llm,
)
from app.inference.tasks.extraction import (
    LLMExtractionResult,
    extract_from_message_llm,
)
from app.inference.tasks.prioritization import (
    LLMPrioritizationResult,
    enhance_prioritization_llm,
)
from app.inference.tasks.drafting import (
    LLMDraftResult,
    generate_draft_llm,
)
from app.inference.tasks.briefing import (
    LLMBriefingResult,
    generate_briefing_llm,
)

# Import existing deterministic services for fallback
from app.graphs.triage import (
    ClassificationResult,
    classify_project,
    ExtractionResult,
    extract_and_persist,
)

logger = logging.getLogger(__name__)


# ── Provider Singleton ───────────────────────────────────────────────

_provider: OpenAICompatibleProvider | None = None


def get_inference_provider(
    settings: InferenceSettings | None = None,
) -> OpenAICompatibleProvider:
    """Get or create the inference provider singleton.

    Uses default settings (LM Studio at 127.0.0.1:1234) unless overridden.
    """
    global _provider
    if _provider is None or settings is not None:
        _provider = OpenAICompatibleProvider(settings or InferenceSettings())
    return _provider


def set_inference_provider(provider: OpenAICompatibleProvider | None) -> None:
    """Override the provider (for testing or reconfiguration)."""
    global _provider
    _provider = provider


# ── Fallback Result Wrapper ──────────────────────────────────────────


@dataclass
class FallbackResult:
    """Wrapper indicating which path produced the result.

    TEST:LLM.Orchestration.FallbackChainWorksCleanly
    """

    used_llm: bool
    fallback_reason: str | None = None


# ── Classification with Fallback ─────────────────────────────────────


@dataclass
class SmartClassificationResult(FallbackResult):
    """Classification result with LLM/fallback tracking."""

    project_id: Optional[uuid.UUID] = None
    confidence: float = 0.0
    rationale: str = ""
    candidates: list = None  # type: ignore[assignment]
    needs_review: bool = False
    review_reason: Optional[str] = None
    inference_latency_ms: float = 0.0

    def __post_init__(self):
        if self.candidates is None:
            self.candidates = []


async def classify_project_smart(
    session: Session,
    sender_identity: Optional[str],
    subject: Optional[str],
    body_text: Optional[str],
    source_account_label: Optional[str] = None,
    *,
    provider: OpenAICompatibleProvider | None = None,
) -> SmartClassificationResult:
    """Classify a message with LLM-first, deterministic-fallback.

    TEST:LLM.Orchestration.TriagePipelineUsesLLMWhenAvailable
    TEST:LLM.Orchestration.FallbackChainWorksCleanly
    TEST:LLM.Safety.ReviewGatesNotWeakened

    Steps:
    1. Try LLM classification
    2. On failure, fall back to deterministic classify_project()
    3. Preserve review gates regardless of path
    """
    provider = provider or get_inference_provider()

    # Build project list from DB for the LLM prompt
    from app.models.portfolio import Project
    from sqlalchemy import select

    projects_orm = session.execute(
        select(Project).where(Project.status == "active")
    ).scalars().all()

    projects_for_llm = [
        {
            "id": str(p.id),
            "name": p.name,
            "objective": p.objective or "",
            "short_summary": p.short_summary or "",
        }
        for p in projects_orm
    ]

    project_id_map = {p.name: p.id for p in projects_orm if p.name}

    # Try LLM first
    try:
        llm_result: LLMClassificationResult = await classify_project_llm(
            provider,
            projects=projects_for_llm,
            sender=sender_identity,
            subject=subject,
            body=body_text,
            source_account=source_account_label,
            project_id_map=project_id_map,
        )

        return SmartClassificationResult(
            used_llm=True,
            project_id=llm_result.project_id,
            confidence=llm_result.confidence,
            rationale=llm_result.rationale,
            candidates=llm_result.candidates,
            needs_review=llm_result.needs_review,
            review_reason=llm_result.review_reason,
            inference_latency_ms=llm_result.inference_latency_ms,
        )

    except InferenceError as exc:
        logger.info(
            "LLM classification failed, falling back to deterministic: %s", exc
        )

        # Deterministic fallback
        det_result: ClassificationResult = classify_project(
            session,
            sender_identity,
            subject,
            body_text,
            source_account_label,
        )

        return SmartClassificationResult(
            used_llm=False,
            fallback_reason=str(exc),
            project_id=det_result.project_id,
            confidence=det_result.confidence,
            rationale=det_result.rationale,
            candidates=det_result.candidates,
            needs_review=det_result.needs_review,
            review_reason=det_result.review_reason,
        )


# ── Extraction with Fallback ─────────────────────────────────────────


async def extract_from_message_smart(
    sender: Optional[str],
    subject: Optional[str],
    body: Optional[str],
    project_name: Optional[str] = None,
    project_objective: Optional[str] = None,
    *,
    provider: OpenAICompatibleProvider | None = None,
) -> LLMExtractionResult:
    """Extract items with LLM-first, empty-fallback.

    On LLM failure, returns an empty extraction result.
    The caller can then apply heuristic extraction if desired.
    """
    provider = provider or get_inference_provider()

    try:
        return await extract_from_message_llm(
            provider,
            sender=sender,
            subject=subject,
            body=body,
            project_name=project_name,
            project_objective=project_objective,
        )
    except InferenceError as exc:
        logger.info(
            "LLM extraction failed, returning empty result: %s", exc
        )
        return LLMExtractionResult(
            used_llm=False,
        )


# ── Draft Generation with Fallback ──────────────────────────────────


async def generate_draft_smart(
    *,
    intent: str = "reply",
    channel_type: str = "email",
    tone_mode: str = "concise",
    context_summary: str | None = None,
    original_message_summary: str | None = None,
    project_name: str | None = None,
    stakeholder_names: list[str] | None = None,
    key_points: list[str] | None = None,
    variant_count: int = 0,
    provider: OpenAICompatibleProvider | None = None,
) -> LLMDraftResult:
    """Generate a draft with LLM-first, empty-fallback.

    ARCH:DraftingGraphNoAutoSend — auto_send is ALWAYS blocked.

    On LLM failure, returns a result with empty body_content.
    The caller must check and handle the empty case.
    """
    provider = provider or get_inference_provider()

    try:
        result = await generate_draft_llm(
            provider,
            intent=intent,
            channel_type=channel_type,
            tone_mode=tone_mode,
            context_summary=context_summary,
            original_message_summary=original_message_summary,
            project_name=project_name,
            stakeholder_names=stakeholder_names,
            key_points=key_points,
            variant_count=variant_count,
        )
        # SAFETY: enforce no-auto-send even if somehow bypassed
        assert result.auto_send_blocked is True
        return result

    except InferenceError as exc:
        logger.info(
            "LLM drafting failed, returning empty draft: %s", exc
        )
        return LLMDraftResult(
            body_content="",
            auto_send_blocked=True,
            used_llm=False,
        )


# ── Briefing with Fallback ───────────────────────────────────────────


async def generate_briefing_smart(
    *,
    top_actions: list[dict] | None = None,
    high_risk_items: list[dict] | None = None,
    waiting_on_items: list[dict] | None = None,
    reply_debt_summary: str | None = None,
    calendar_pressure_summary: str | None = None,
    project_names: list[str] | None = None,
    provider: OpenAICompatibleProvider | None = None,
) -> LLMBriefingResult:
    """Generate a briefing with LLM-first, empty-fallback.

    On LLM failure, returns an empty result. The caller should
    fall back to the template-based generate_spoken_briefing().
    """
    provider = provider or get_inference_provider()

    try:
        return await generate_briefing_llm(
            provider,
            top_actions=top_actions,
            high_risk_items=high_risk_items,
            waiting_on_items=waiting_on_items,
            reply_debt_summary=reply_debt_summary,
            calendar_pressure_summary=calendar_pressure_summary,
            project_names=project_names,
        )
    except InferenceError as exc:
        logger.info(
            "LLM briefing failed, returning empty result: %s", exc
        )
        return LLMBriefingResult(used_llm=False)


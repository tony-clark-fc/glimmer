"""LLM-powered project classification task.

PLAN:WorkstreamI.PackageI3.LLMClassification
TEST:LLM.Classification.ProducesValidClassificationResult
TEST:LLM.Classification.ConfidenceAndRationalePresent
TEST:LLM.Classification.LowConfidenceTriggersReviewGate
TEST:LLM.Classification.FallsBackToDeterministicWhenUnavailable

Replaces keyword-based classification with LLM inference.
Falls back to the deterministic baseline when the provider is unavailable.

The classification result is an INTERPRETED CANDIDATE — it enters
pending_review state and is never silently accepted as truth.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass

from app.inference.base import InferenceError, InferenceResult
from app.inference.context_builder import (
    assemble_messages,
    build_message_context,
    build_project_context,
)
from app.inference.openai_compat import OpenAICompatibleProvider
from app.inference.prompts.classification import (
    SYSTEM_PROMPT,
    build_user_prompt,
)
from app.inference.response_parser import parse_llm_response

logger = logging.getLogger(__name__)


# ── Classification Result ────────────────────────────────────────────

CONFIDENCE_REVIEW_THRESHOLD = 0.5


@dataclass
class LLMClassificationResult:
    """Result of LLM-powered classification.

    This is an interpreted candidate — it enters pending_review state.
    The operator must accept or override the classification.
    """

    project_id: uuid.UUID | None
    project_name: str | None
    confidence: float
    rationale: str
    candidates: list[dict]
    needs_review: bool
    review_reason: str | None
    used_llm: bool
    inference_latency_ms: float = 0.0
    raw_llm_response: str | None = None


# ── Main Classification Function ─────────────────────────────────────


async def classify_project_llm(
    provider: OpenAICompatibleProvider,
    *,
    projects: list[dict],
    sender: str | None,
    subject: str | None,
    body: str | None,
    source_account: str | None = None,
    project_id_map: dict[str, uuid.UUID] | None = None,
) -> LLMClassificationResult:
    """Classify a message to a project using the LLM.

    Args:
        provider: The inference provider to use.
        projects: List of project dicts with id, name, objective, short_summary.
        sender: Sender identity string.
        subject: Message subject.
        body: Message body text.
        source_account: Account label the message arrived on.
        project_id_map: Optional mapping of project name → UUID for ID resolution.

    Returns:
        LLMClassificationResult with the LLM's classification.

    Raises:
        InferenceError: If the provider fails (caller should fall back to deterministic).

    TEST:LLM.Classification.ProducesValidClassificationResult
    TEST:LLM.Classification.ConfidenceAndRationalePresent
    """
    # Build prompt context (with token budget management)
    project_ctx = build_project_context(projects)
    msg_ctx = build_message_context(sender, subject, body)

    user_prompt = build_user_prompt(
        projects=project_ctx,
        sender=msg_ctx["sender"],
        subject=msg_ctx["subject"],
        body=msg_ctx["body"],
        source_account=source_account,
    )

    messages = assemble_messages(SYSTEM_PROMPT, user_prompt)

    # Call the LLM
    result: InferenceResult = await provider.chat_completion(
        messages=messages,
        temperature=0.1,  # Low temperature for consistent classification
        max_tokens=1000,  # Generous budget — model can be verbose with rationale
    )

    # Parse the response
    parsed = parse_llm_response(
        result.content,
        required_fields=["confidence", "rationale"],
    )

    if not parsed.success:
        logger.warning(
            "LLM classification parse failed: %s (raw: %s)",
            parsed.error,
            result.content[:200],
        )
        raise InferenceError(
            f"Failed to parse classification response: {parsed.error}",
            provider="llm_classification",
            detail=result.content[:500],
        )

    data = parsed.data
    assert data is not None  # Guaranteed by parsed.success

    # Resolve project ID from name if we have a mapping
    resolved_project_id: uuid.UUID | None = None
    project_name = data.get("project_name")
    project_id_str = data.get("project_id")

    if project_id_str and project_id_str != "null":
        try:
            resolved_project_id = uuid.UUID(project_id_str)
        except ValueError:
            pass

    if resolved_project_id is None and project_name and project_id_map:
        resolved_project_id = project_id_map.get(project_name)

    # Determine review need
    confidence = float(data.get("confidence", 0.0))
    needs_review = data.get("needs_review", confidence < CONFIDENCE_REVIEW_THRESHOLD)
    review_reason = data.get("review_reason")

    if confidence < CONFIDENCE_REVIEW_THRESHOLD and not needs_review:
        needs_review = True
        review_reason = review_reason or "Low confidence — operator review recommended"

    candidates = data.get("candidates", [])

    return LLMClassificationResult(
        project_id=resolved_project_id,
        project_name=project_name,
        confidence=confidence,
        rationale=data.get("rationale", ""),
        candidates=candidates,
        needs_review=needs_review,
        review_reason=review_reason,
        used_llm=True,
        inference_latency_ms=result.latency_ms,
        raw_llm_response=result.content,
    )



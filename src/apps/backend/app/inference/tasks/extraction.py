"""LLM-powered action/decision/deadline extraction task.

PLAN:WorkstreamI.PackageI4.LLMExtraction
TEST:LLM.Extraction.ProducesValidStructuredActions
TEST:LLM.Extraction.ConfidencePerExtractionPresent
TEST:LLM.Extraction.NoHallucinationFromEmptyContent
TEST:LLM.Extraction.FallsBackWhenUnavailable
TEST:LLM.Extraction.OutputCompatibleWithPersistenceLayer

Extracts structured actions, decisions, and deadlines from message content
using LLM inference. Falls back to empty extraction when the provider is
unavailable (the caller can then use heuristic extraction if desired).

All extracted items are INTERPRETED CANDIDATES — they enter pending_review
state and are never silently accepted as truth.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from app.inference.base import InferenceError, InferenceResult
from app.inference.context_builder import assemble_messages, build_message_context
from app.inference.openai_compat import OpenAICompatibleProvider
from app.inference.prompts.extraction import SYSTEM_PROMPT, build_user_prompt
from app.inference.response_parser import parse_llm_response

logger = logging.getLogger(__name__)


# ── Extraction Result ────────────────────────────────────────────────


@dataclass
class LLMExtractionResult:
    """Result of LLM-powered extraction.

    All items are interpreted candidates — they enter pending_review state.
    Compatible with the persistence layer's extract_and_persist() function.
    """

    actions: list[dict] = field(default_factory=list)
    decisions: list[dict] = field(default_factory=list)
    deadlines: list[dict] = field(default_factory=list)
    used_llm: bool = False
    inference_latency_ms: float = 0.0
    raw_llm_response: str | None = None

    @property
    def total_items(self) -> int:
        return len(self.actions) + len(self.decisions) + len(self.deadlines)

    @property
    def is_empty(self) -> bool:
        return self.total_items == 0


# ── Main Extraction Function ─────────────────────────────────────────


async def extract_from_message_llm(
    provider: OpenAICompatibleProvider,
    *,
    sender: str | None,
    subject: str | None,
    body: str | None,
    project_name: str | None = None,
    project_objective: str | None = None,
) -> LLMExtractionResult:
    """Extract actions, decisions, and deadlines from a message using the LLM.

    Args:
        provider: The inference provider to use.
        sender: Sender identity string.
        subject: Message subject.
        body: Message body text.
        project_name: Name of the classified project (if known).
        project_objective: Objective of the classified project.

    Returns:
        LLMExtractionResult with extracted items.

    Raises:
        InferenceError: If the provider fails (caller should fall back).

    TEST:LLM.Extraction.ProducesValidStructuredActions
    TEST:LLM.Extraction.ConfidencePerExtractionPresent
    """
    msg_ctx = build_message_context(sender, subject, body)

    user_prompt = build_user_prompt(
        sender=msg_ctx["sender"],
        subject=msg_ctx["subject"],
        body=msg_ctx["body"],
        project_name=project_name,
        project_objective=project_objective,
    )

    messages = assemble_messages(SYSTEM_PROMPT, user_prompt)

    result: InferenceResult = await provider.chat_completion(
        messages=messages,
        temperature=0.1,
        max_tokens=1500,  # Extraction can produce longer output than classification
    )

    parsed = parse_llm_response(
        result.content,
        required_fields=["actions", "decisions", "deadlines"],
    )

    if not parsed.success:
        logger.warning(
            "LLM extraction parse failed: %s (raw: %s)",
            parsed.error,
            result.content[:200],
        )
        raise InferenceError(
            f"Failed to parse extraction response: {parsed.error}",
            provider="llm_extraction",
            detail=result.content[:500],
        )

    data = parsed.data
    assert data is not None

    # Normalize and validate extracted items
    actions = _normalize_actions(data.get("actions", []))
    decisions = _normalize_decisions(data.get("decisions", []))
    deadlines = _normalize_deadlines(data.get("deadlines", []))

    return LLMExtractionResult(
        actions=actions,
        decisions=decisions,
        deadlines=deadlines,
        used_llm=True,
        inference_latency_ms=result.latency_ms,
        raw_llm_response=result.content,
    )


# ── Normalization Helpers ────────────────────────────────────────────


def _normalize_actions(raw_actions: list) -> list[dict]:
    """Normalize action items to the persistence-compatible format."""
    normalized: list[dict] = []
    for item in raw_actions:
        if not isinstance(item, dict):
            continue
        description = item.get("description", "").strip()
        if not description:
            continue
        normalized.append({
            "description": description,
            "proposed_owner": item.get("proposed_owner"),
            "due_date_signal": item.get("due_date_signal"),
            "urgency_signal": item.get("urgency_signal"),
            "confidence": _clamp_confidence(item.get("confidence", 0.5)),
        })
    return normalized


def _normalize_decisions(raw_decisions: list) -> list[dict]:
    """Normalize decision items to the persistence-compatible format."""
    normalized: list[dict] = []
    for item in raw_decisions:
        if not isinstance(item, dict):
            continue
        description = item.get("description", "").strip()
        if not description:
            continue
        normalized.append({
            "description": description,
            "rationale": item.get("rationale"),
            "confidence": _clamp_confidence(item.get("confidence", 0.5)),
        })
    return normalized


def _normalize_deadlines(raw_deadlines: list) -> list[dict]:
    """Normalize deadline items to the persistence-compatible format."""
    normalized: list[dict] = []
    for item in raw_deadlines:
        if not isinstance(item, dict):
            continue
        description = item.get("description", "").strip()
        if not description:
            continue
        normalized.append({
            "description": description,
            "inferred_date": item.get("inferred_date"),
            "confidence": _clamp_confidence(item.get("confidence", 0.5)),
        })
    return normalized


def _clamp_confidence(value) -> float:
    """Clamp a confidence value to [0.0, 1.0]."""
    try:
        v = float(value)
        return max(0.0, min(1.0, v))
    except (TypeError, ValueError):
        return 0.5


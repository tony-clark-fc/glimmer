"""LLM-enhanced prioritization — narrative rationale and next-step suggestions.

PLAN:WorkstreamI.PackageI5.LLMPrioritization
TEST:LLM.Prioritization.ProducesNarrativeRationale
TEST:LLM.Prioritization.NextStepSuggestionsAreContextual
TEST:LLM.Prioritization.FallsBackToDeterministicScoring

Enhances deterministic priority scoring with LLM-generated narrative
rationale and contextual next-step suggestions.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from app.inference.base import InferenceError, InferenceResult
from app.inference.context_builder import assemble_messages
from app.inference.openai_compat import OpenAICompatibleProvider
from app.inference.prompts.prioritization import SYSTEM_PROMPT, build_user_prompt
from app.inference.response_parser import parse_llm_response

logger = logging.getLogger(__name__)


@dataclass
class LLMPrioritizationResult:
    """Result of LLM-enhanced prioritization."""

    narrative: str = ""
    enhanced_items: list[dict] = field(default_factory=list)
    overall_suggestions: list[str] = field(default_factory=list)
    used_llm: bool = False
    inference_latency_ms: float = 0.0
    raw_llm_response: str | None = None


async def enhance_prioritization_llm(
    provider: OpenAICompatibleProvider,
    *,
    priority_items: list[dict],
    active_projects: list[dict] | None = None,
    reply_debt_summary: str | None = None,
    calendar_pressure_summary: str | None = None,
) -> LLMPrioritizationResult:
    """Enhance deterministic priority scoring with LLM narrative.

    Raises:
        InferenceError: If the provider fails (caller should use deterministic output).
    """
    user_prompt = build_user_prompt(
        priority_items=priority_items,
        active_projects=active_projects,
        reply_debt_summary=reply_debt_summary,
        calendar_pressure_summary=calendar_pressure_summary,
    )

    messages = assemble_messages(SYSTEM_PROMPT, user_prompt)

    result: InferenceResult = await provider.chat_completion(
        messages=messages,
        temperature=0.3,  # Slightly higher for natural language
        max_tokens=1000,
    )

    parsed = parse_llm_response(
        result.content,
        required_fields=["narrative"],
    )

    if not parsed.success:
        logger.warning(
            "LLM prioritization parse failed: %s", parsed.error,
        )
        raise InferenceError(
            f"Failed to parse prioritization response: {parsed.error}",
            provider="llm_prioritization",
            detail=result.content[:500],
        )

    data = parsed.data
    assert data is not None

    return LLMPrioritizationResult(
        narrative=data.get("narrative", ""),
        enhanced_items=data.get("enhanced_items", []),
        overall_suggestions=data.get("overall_suggestions", []),
        used_llm=True,
        inference_latency_ms=result.latency_ms,
        raw_llm_response=result.content,
    )


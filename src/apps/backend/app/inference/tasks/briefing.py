"""LLM-enhanced briefing generation task.

PLAN:WorkstreamI.PackageI7.LLMBriefing
TEST:LLM.Briefing.ProducesNaturalSpokenOutput
TEST:LLM.Briefing.GroundedInFocusPackData
TEST:LLM.Briefing.LengthBoundRespected
TEST:LLM.Briefing.FallsBackWhenUnavailable

Generates natural-language spoken briefings from focus-pack data
using LLM inference. Falls back to the template-based briefing
when the provider is unavailable.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from app.inference.base import InferenceError, InferenceResult
from app.inference.context_builder import assemble_messages
from app.inference.openai_compat import OpenAICompatibleProvider
from app.inference.prompts.briefing import SYSTEM_PROMPT, build_user_prompt
from app.inference.response_parser import parse_llm_response

logger = logging.getLogger(__name__)

MAX_BRIEFING_LENGTH = 600


@dataclass
class LLMBriefingResult:
    """Result of LLM-enhanced briefing generation."""

    briefing_text: str = ""
    section_count: int = 0
    sections_used: list[str] = field(default_factory=list)
    items_mentioned: int = 0
    used_llm: bool = False
    inference_latency_ms: float = 0.0
    raw_llm_response: str | None = None

    @property
    def is_empty(self) -> bool:
        return not self.briefing_text.strip()


async def generate_briefing_llm(
    provider: OpenAICompatibleProvider,
    *,
    top_actions: list[dict] | None = None,
    high_risk_items: list[dict] | None = None,
    waiting_on_items: list[dict] | None = None,
    reply_debt_summary: str | None = None,
    calendar_pressure_summary: str | None = None,
    project_names: list[str] | None = None,
) -> LLMBriefingResult:
    """Generate a spoken briefing using the LLM.

    Raises:
        InferenceError: If the provider fails (caller should use template briefing).
    """
    user_prompt = build_user_prompt(
        top_actions=top_actions,
        high_risk_items=high_risk_items,
        waiting_on_items=waiting_on_items,
        reply_debt_summary=reply_debt_summary,
        calendar_pressure_summary=calendar_pressure_summary,
        project_names=project_names,
    )

    messages = assemble_messages(SYSTEM_PROMPT, user_prompt)

    result: InferenceResult = await provider.chat_completion(
        messages=messages,
        temperature=0.3,
        max_tokens=800,
    )

    parsed = parse_llm_response(
        result.content,
        required_fields=["briefing_text"],
    )

    if not parsed.success:
        logger.warning("LLM briefing parse failed: %s", parsed.error)
        raise InferenceError(
            f"Failed to parse briefing response: {parsed.error}",
            provider="llm_briefing",
            detail=result.content[:500],
        )

    data = parsed.data
    assert data is not None

    briefing_text = data.get("briefing_text", "")

    # Enforce length bound — the model should respect the 600 char limit
    # but we enforce it as a safety net
    if len(briefing_text) > MAX_BRIEFING_LENGTH:
        briefing_text = briefing_text[:MAX_BRIEFING_LENGTH - 3] + "..."
        logger.info("Briefing truncated to %d chars", MAX_BRIEFING_LENGTH)

    return LLMBriefingResult(
        briefing_text=briefing_text,
        section_count=data.get("section_count", 0),
        sections_used=data.get("sections_used", []),
        items_mentioned=data.get("items_mentioned", 0),
        used_llm=True,
        inference_latency_ms=result.latency_ms,
        raw_llm_response=result.content,
    )


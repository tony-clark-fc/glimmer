"""LLM-powered draft generation task.

PLAN:WorkstreamI.PackageI6.LLMDrafting
TEST:LLM.Drafting.GeneratesContextualDraft
TEST:LLM.Drafting.ToneModeRespected
TEST:LLM.Drafting.StakeholderAwarenessPresent
TEST:LLM.Drafting.NoAutoSendBoundaryPreserved
TEST:LLM.Drafting.FallsBackWhenUnavailable

Generates communication drafts using LLM inference.
CRITICAL: Drafts are ALWAYS review-required. auto_send is NEVER permitted.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from app.inference.base import InferenceError, InferenceResult
from app.inference.context_builder import assemble_messages
from app.inference.openai_compat import OpenAICompatibleProvider
from app.inference.prompts.drafting import SYSTEM_PROMPT, build_user_prompt
from app.inference.response_parser import parse_llm_response

logger = logging.getLogger(__name__)


@dataclass
class LLMDraftResult:
    """Result of LLM-powered draft generation.

    CRITICAL: auto_send_blocked is ALWAYS True. This is a hard product boundary.
    """

    body_content: str = ""
    subject_suggestion: str | None = None
    rationale_summary: str = ""
    variants: list[dict] = field(default_factory=list)
    auto_send_blocked: bool = True  # HARD INVARIANT — never False
    used_llm: bool = False
    inference_latency_ms: float = 0.0
    raw_llm_response: str | None = None


async def generate_draft_llm(
    provider: OpenAICompatibleProvider,
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
) -> LLMDraftResult:
    """Generate a communication draft using the LLM.

    ARCH:DraftingGraphNoAutoSend — auto_send is ALWAYS blocked.

    Raises:
        InferenceError: If the provider fails (caller should fall back).
    """
    user_prompt = build_user_prompt(
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

    messages = assemble_messages(SYSTEM_PROMPT, user_prompt)

    result: InferenceResult = await provider.chat_completion(
        messages=messages,
        temperature=0.4,  # Some creativity for natural drafting
        max_tokens=1500,
    )

    parsed = parse_llm_response(
        result.content,
        required_fields=["body_content"],
    )

    if not parsed.success:
        logger.warning("LLM drafting parse failed: %s", parsed.error)
        raise InferenceError(
            f"Failed to parse drafting response: {parsed.error}",
            provider="llm_drafting",
            detail=result.content[:500],
        )

    data = parsed.data
    assert data is not None

    variants = []
    for v in data.get("variants", []):
        if isinstance(v, dict) and v.get("body_content"):
            variants.append({
                "label": v.get("label", "alternate"),
                "body_content": v["body_content"],
            })

    return LLMDraftResult(
        body_content=data.get("body_content", ""),
        subject_suggestion=data.get("subject_suggestion"),
        rationale_summary=data.get("rationale_summary", ""),
        variants=variants,
        auto_send_blocked=True,  # HARD INVARIANT
        used_llm=True,
        inference_latency_ms=result.latency_ms,
        raw_llm_response=result.content,
    )


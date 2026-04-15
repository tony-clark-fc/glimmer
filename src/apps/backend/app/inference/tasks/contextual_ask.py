"""LLM-enhanced contextual "Ask Glimmer" task.

PLAN:WorkstreamE.PackageE16.ContextualAskGlimmer
ARCH:ContextualAskGlimmerInteraction
TEST:UI.AskGlimmer.ResponseRespectsReviewGates

Generates contextual responses when the operator asks a question
about a specific data element on any workspace surface.

The response includes a review_required flag — derived from the
[REVIEW_REQUIRED] marker the model emits when its answer implies
an externally meaningful action.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from app.inference.base import InferenceError, InferenceResult
from app.inference.context_builder import assemble_messages
from app.inference.openai_compat import OpenAICompatibleProvider
from app.inference.prompts.contextual_ask import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)

REVIEW_MARKER = "[REVIEW_REQUIRED]"


@dataclass
class LLMContextualAskResult:
    """Result of a contextual Ask Glimmer interaction."""

    reply_content: str = ""
    review_required: bool = False
    review_reason: str | None = None
    used_llm: bool = False
    inference_latency_ms: float = 0.0
    model: str = ""
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None

    @property
    def is_empty(self) -> bool:
        return not self.reply_content.strip()


def _extract_review_flag(raw_content: str) -> tuple[str, bool, str | None]:
    """Strip the [REVIEW_REQUIRED] marker and return (clean_content, flag, reason)."""
    if REVIEW_MARKER in raw_content:
        clean = raw_content.replace(REVIEW_MARKER, "").strip()
        return clean, True, "Response implies an externally meaningful action that requires operator approval."
    return raw_content.strip(), False, None


async def generate_contextual_ask_llm(
    provider: OpenAICompatibleProvider,
    *,
    element_type: str,
    element_id: str,
    element_context: dict,
    surface: str,
    question: str,
    project_summaries: list[dict] | None = None,
) -> LLMContextualAskResult:
    """Generate a contextual response using the LLM.

    Args:
        provider: The inference provider.
        element_type: Type of the data element.
        element_id: Element identifier.
        element_context: Serialized element data.
        surface: Workspace surface name.
        question: The operator's question.
        project_summaries: Active project data for grounding.

    Returns:
        LLMContextualAskResult with the reply and review flag.

    Raises:
        InferenceError: If the provider fails.
    """
    user_prompt = build_user_prompt(
        element_type=element_type,
        element_id=element_id,
        element_context=element_context,
        surface=surface,
        question=question,
        project_summaries=project_summaries,
    )

    messages = assemble_messages(SYSTEM_PROMPT, user_prompt)

    result: InferenceResult = await provider.chat_completion(
        messages=messages,
        temperature=0.6,
        max_tokens=800,
    )

    raw_content = (result.content or "").strip()

    if not raw_content:
        logger.warning("LLM contextual ask returned empty content")
        raise InferenceError(
            "LLM returned empty response for contextual ask",
            provider="llm_contextual_ask",
        )

    reply_content, review_required, review_reason = _extract_review_flag(raw_content)

    return LLMContextualAskResult(
        reply_content=reply_content,
        review_required=review_required,
        review_reason=review_reason,
        used_llm=True,
        inference_latency_ms=result.latency_ms,
        model=result.model,
        prompt_tokens=result.prompt_tokens,
        completion_tokens=result.completion_tokens,
        total_tokens=result.total_tokens,
    )


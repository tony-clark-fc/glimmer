"""LLM-enhanced persona-page conversation task.

PLAN:WorkstreamE.PackageE12.PersonaPageConversationUi
ARCH:PersonaPage.ConversationModel
TEST:PersonaPage.Conversation.ChatRendersAndAcceptsInput

Generates conversational replies for the Glimmer persona page.
Unlike other LLM tasks, conversation output is plain text (not JSON)
because it flows directly into the chat stream.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from app.inference.base import InferenceError, InferenceResult
from app.inference.context_builder import assemble_messages
from app.inference.openai_compat import OpenAICompatibleProvider
from app.inference.prompts.conversation import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)


@dataclass
class LLMConversationResult:
    """Result of a persona-page conversation turn."""

    reply_content: str = ""
    used_llm: bool = False
    inference_latency_ms: float = 0.0
    model: str = ""
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None

    @property
    def is_empty(self) -> bool:
        return not self.reply_content.strip()


async def generate_conversation_reply_llm(
    provider: OpenAICompatibleProvider,
    *,
    operator_message: str,
    workspace_mode: str = "update",
    message_history: list[dict] | None = None,
    project_summaries: list[dict] | None = None,
    portfolio_health: dict | None = None,
) -> LLMConversationResult:
    """Generate a conversation reply using the LLM.

    Args:
        provider: The inference provider.
        operator_message: The operator's latest message.
        workspace_mode: Active workspace mode.
        message_history: Recent prior conversation messages.
        project_summaries: Active project data for grounding.
        portfolio_health: Portfolio health snapshot.

    Returns:
        LLMConversationResult with the reply text.

    Raises:
        InferenceError: If the provider fails.
    """
    user_prompt = build_user_prompt(
        operator_message=operator_message,
        workspace_mode=workspace_mode,
        message_history=message_history,
        project_summaries=project_summaries,
        portfolio_health=portfolio_health,
    )

    messages = assemble_messages(SYSTEM_PROMPT, user_prompt)

    result: InferenceResult = await provider.chat_completion(
        messages=messages,
        temperature=0.7,
        max_tokens=1000,
    )

    reply_content = (result.content or "").strip()

    if not reply_content:
        logger.warning("LLM conversation returned empty content")
        raise InferenceError(
            "LLM returned empty response for conversation",
            provider="llm_conversation",
        )

    return LLMConversationResult(
        reply_content=reply_content,
        used_llm=True,
        inference_latency_ms=result.latency_ms,
        model=result.model,
        prompt_tokens=result.prompt_tokens,
        completion_tokens=result.completion_tokens,
        total_tokens=result.total_tokens,
    )


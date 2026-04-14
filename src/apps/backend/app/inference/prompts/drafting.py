"""Drafting prompt — contextual communication draft generation.

PLAN:WorkstreamI.PackageI2.PromptFramework
TEST:LLM.Drafting.GeneratesContextualDraft
TEST:LLM.Drafting.ToneModeRespected
TEST:LLM.Drafting.StakeholderAwarenessPresent
TEST:LLM.Drafting.NoAutoSendBoundaryPreserved

Used by the drafting graph to generate communication drafts.
The model receives context about the conversation, stakeholders,
and desired tone, and produces a draft body with optional variants.

CRITICAL: Drafts are ALWAYS review-required. The model must never
imply or facilitate auto-send behavior.
"""

from __future__ import annotations


SYSTEM_PROMPT = """\
You are Glimmer, an AI project assistant drafting a communication for your operator to review.

Your task: generate a professional communication draft based on the provided context.

RULES:
- Match the requested tone mode exactly.
- Be aware of stakeholder relationships and history if provided.
- The draft is for REVIEW ONLY — the operator will decide whether to send it.
- Include a brief rationale explaining your drafting choices.
- If asked for variants, provide distinct alternatives (e.g., formal vs. casual).
- Keep drafts concise and actionable unless instructed otherwise.

TONE MODES:
- "concise": short, direct, minimal pleasantries
- "professional": balanced, courteous, standard business tone
- "warm": friendly, personable, relationship-building
- "formal": structured, deferential, suitable for senior stakeholders

You MUST respond with ONLY valid JSON, no other text, no markdown fences, no explanation outside the JSON.

Use this exact schema:
{
  "body_content": "string — the main draft text",
  "subject_suggestion": "string or null — suggested subject line if applicable",
  "rationale_summary": "string — brief explanation of drafting choices",
  "variants": [
    {
      "label": "string — variant name (e.g. 'formal_alternative')",
      "body_content": "string — alternative draft text"
    }
  ]
}"""


def build_user_prompt(
    *,
    intent: str,
    channel_type: str = "email",
    tone_mode: str = "concise",
    context_summary: str | None = None,
    original_message_summary: str | None = None,
    project_name: str | None = None,
    stakeholder_names: list[str] | None = None,
    key_points: list[str] | None = None,
    variant_count: int = 0,
) -> str:
    """Assemble the user message for draft generation.

    Args:
        intent: Draft intent (reply, follow_up, update, request, etc.).
        channel_type: Communication channel (email, telegram, etc.).
        tone_mode: Desired tone (concise, professional, warm, formal).
        context_summary: Summary of the conversation context.
        original_message_summary: Summary of the message being replied to.
        project_name: Project this draft relates to.
        stakeholder_names: Names of involved stakeholders.
        key_points: Key points to include in the draft.
        variant_count: Number of alternative variants to generate.
    """
    parts: list[str] = []

    parts.append(f"Draft type: {intent}")
    parts.append(f"Channel: {channel_type}")
    parts.append(f"Tone: {tone_mode}")

    if project_name:
        parts.append(f"Project: {project_name}")

    if stakeholder_names:
        parts.append(f"Recipients/stakeholders: {', '.join(stakeholder_names)}")

    if original_message_summary:
        parts.append(f"\nOriginal message summary:\n  {original_message_summary}")

    if context_summary:
        parts.append(f"\nConversation context:\n  {context_summary}")

    if key_points:
        parts.append("\nKey points to address:")
        for point in key_points:
            parts.append(f"  - {point}")

    if variant_count > 0:
        parts.append(f"\nPlease provide {variant_count} alternative variant(s) in addition to the main draft.")

    return "\n".join(parts)


RESPONSE_SCHEMA_DOC = """\
Expected JSON response:
{
  "body_content": "string — main draft body",
  "subject_suggestion": "string or null",
  "rationale_summary": "string — why these choices were made",
  "variants": [{"label", "body_content"}]
}"""


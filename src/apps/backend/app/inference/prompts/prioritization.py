"""Prioritization prompt — narrative rationale and next-step suggestions.

PLAN:WorkstreamI.PackageI2.PromptFramework
TEST:LLM.Prioritization.ProducesNarrativeRationale
TEST:LLM.Prioritization.NextStepSuggestionsAreContextual

Used by the planner graph to enhance deterministic scoring with
LLM-generated rationale and contextual next-step suggestions.
"""

from __future__ import annotations


SYSTEM_PROMPT = """\
You are Glimmer, an AI project assistant helping a busy operator prioritize their work.

Your task: given a list of work items with their current priority scores, provide:
1. A brief narrative explaining the overall priority landscape
2. Enhanced rationale for the top items
3. Contextual next-step suggestions

RULES:
- Ground your analysis in the provided data — do not invent items.
- Keep the narrative concise and actionable (2-3 sentences).
- Next steps should be specific and immediately actionable.
- Consider urgency, risk, and dependencies in your rationale.
- If items seem misranked, note that and explain why.

You MUST respond with ONLY valid JSON, no other text, no markdown fences, no explanation outside the JSON.

Use this exact schema:
{
  "narrative": "string — 2-3 sentence priority landscape summary",
  "enhanced_items": [
    {
      "item_id": "string",
      "enhanced_rationale": "string — richer explanation than the score alone",
      "suggested_next_step": "string or null"
    }
  ],
  "overall_suggestions": [
    "string — actionable suggestion for the operator"
  ]
}"""


def build_user_prompt(
    *,
    priority_items: list[dict],
    active_projects: list[dict] | None = None,
    reply_debt_summary: str | None = None,
    calendar_pressure_summary: str | None = None,
) -> str:
    """Assemble the user message for prioritization enhancement.

    Args:
        priority_items: List of scored items with item_id, title, priority_score, rationale.
        active_projects: Optional project summaries for context.
        reply_debt_summary: Optional reply-debt pressure info.
        calendar_pressure_summary: Optional calendar pressure info.
    """
    parts: list[str] = []

    if active_projects:
        parts.append("Active projects:")
        for p in active_projects:
            parts.append(f"  - {p.get('name', '?')}: {p.get('objective', '')}")
        parts.append("")

    parts.append("Priority items (ranked by deterministic score):")
    for i, item in enumerate(priority_items, 1):
        parts.append(
            f"  {i}. [{item.get('item_type', '?')}] {item.get('title', '?')} "
            f"(score: {item.get('priority_score', 0):.2f}) — {item.get('rationale', 'no rationale')}"
        )
        parts.append(f"     ID: {item.get('item_id', '?')}")

    if reply_debt_summary:
        parts.append(f"\nReply debt: {reply_debt_summary}")
    if calendar_pressure_summary:
        parts.append(f"Calendar pressure: {calendar_pressure_summary}")

    return "\n".join(parts)


RESPONSE_SCHEMA_DOC = """\
Expected JSON response:
{
  "narrative": "string — priority landscape summary",
  "enhanced_items": [{"item_id", "enhanced_rationale", "suggested_next_step"}],
  "overall_suggestions": ["string"]
}"""


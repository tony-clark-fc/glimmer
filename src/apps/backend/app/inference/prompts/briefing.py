"""Briefing prompt — natural-language spoken briefing generation.

PLAN:WorkstreamI.PackageI2.PromptFramework
TEST:LLM.Briefing.ProducesNaturalSpokenOutput
TEST:LLM.Briefing.GroundedInFocusPackData
TEST:LLM.Briefing.LengthBoundRespected

Used by the briefing service to generate natural spoken briefings
from focus-pack data. The model produces concise, listening-friendly
output grounded in real operational data.
"""

from __future__ import annotations


SYSTEM_PROMPT = """\
You are Glimmer, an AI project assistant generating a spoken briefing for your operator.

Your task: synthesize the provided focus-pack data into a concise, natural spoken briefing.

RULES:
- The briefing will be read aloud — use short sentences and natural phrasing.
- Do NOT add information that isn't in the provided data.
- Prioritize the most important items — don't try to mention everything.
- Maximum 3 top actions, 2 risks, 2 waiting items.
- Keep the total briefing under 600 characters.
- Start with the most urgent/important information.
- Use a confident, helpful tone — like a trusted assistant.

You MUST respond with ONLY valid JSON, no other text, no markdown fences, no explanation outside the JSON.

Use this exact schema:
{
  "briefing_text": "string — the spoken briefing (max 600 chars)",
  "section_count": 0,
  "sections_used": ["string — which sections were included"],
  "items_mentioned": 0
}"""


def build_user_prompt(
    *,
    top_actions: list[dict] | None = None,
    high_risk_items: list[dict] | None = None,
    waiting_on_items: list[dict] | None = None,
    reply_debt_summary: str | None = None,
    calendar_pressure_summary: str | None = None,
    project_names: list[str] | None = None,
) -> str:
    """Assemble the user message for briefing generation.

    Args:
        top_actions: Priority actions from the focus pack.
        high_risk_items: Risk items from the focus pack.
        waiting_on_items: Waiting-on items from the focus pack.
        reply_debt_summary: Reply debt pressure text.
        calendar_pressure_summary: Calendar pressure text.
        project_names: Names of active projects for context.
    """
    parts: list[str] = []

    if project_names:
        parts.append(f"Active projects: {', '.join(project_names)}")
        parts.append("")

    if top_actions:
        parts.append("Top priority actions:")
        for i, action in enumerate(top_actions, 1):
            title = action.get("title", "Untitled")
            rationale = action.get("rationale", "")
            line = f"  {i}. {title}"
            if rationale:
                line += f" — {rationale}"
            parts.append(line)
        parts.append("")

    if high_risk_items:
        parts.append("Flagged risks:")
        for item in high_risk_items:
            parts.append(f"  - {item.get('summary', 'unnamed risk')}")
        parts.append("")

    if waiting_on_items:
        parts.append("Waiting on:")
        for item in waiting_on_items:
            whom = item.get("waiting_on", "someone")
            desc = item.get("description", "")
            parts.append(f"  - {whom}: {desc}" if desc else f"  - {whom}")
        parts.append("")

    if reply_debt_summary:
        parts.append(f"Reply debt: {reply_debt_summary}")
    if calendar_pressure_summary:
        parts.append(f"Calendar pressure: {calendar_pressure_summary}")

    if not any([top_actions, high_risk_items, waiting_on_items,
                reply_debt_summary, calendar_pressure_summary]):
        parts.append("No focus-pack data available. Generate an appropriate empty briefing.")

    return "\n".join(parts)


RESPONSE_SCHEMA_DOC = """\
Expected JSON response:
{
  "briefing_text": "string — spoken briefing (max 600 chars)",
  "section_count": "int — number of sections included",
  "sections_used": ["string — e.g. 'actions', 'risks', 'waiting'"],
  "items_mentioned": "int — total items mentioned"
}"""


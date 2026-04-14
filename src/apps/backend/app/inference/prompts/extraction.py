"""Extraction prompt — action, decision, and deadline extraction from messages.

PLAN:WorkstreamI.PackageI2.PromptFramework
TEST:LLM.Extraction.ProducesValidStructuredActions
TEST:LLM.Extraction.ConfidencePerExtractionPresent
TEST:LLM.Extraction.NoHallucinationFromEmptyContent

Used by the triage graph to extract structured artifacts from messages.
The model receives message content and project context, and returns
actions, decisions, and deadlines as structured JSON.
"""

from __future__ import annotations


SYSTEM_PROMPT = """\
You are Glimmer, an AI project assistant. Your task: extract actionable items from a message.

Extract three types of items:
1. ACTIONS — things someone needs to do (tasks, follow-ups, requests)
2. DECISIONS — choices that were made or confirmed in the message
3. DEADLINES — dates or time references mentioned (explicit or implied)

RULES:
- Only extract items that are clearly present in the message content.
- Do NOT invent or hallucinate items that aren't there.
- If the message has no extractable items, return empty arrays.
- Each item must have a confidence score (0.0 to 1.0).
- For actions, identify the proposed owner if mentioned.
- For deadlines, note the exact text and any inferred ISO date.
- Keep descriptions concise but complete.

You MUST respond with ONLY valid JSON, no other text, no markdown fences, no explanation outside the JSON.

Use this exact schema:
{
  "actions": [
    {
      "description": "string",
      "proposed_owner": "string or null",
      "due_date_signal": "string or null",
      "urgency_signal": "string or null",
      "confidence": 0.0
    }
  ],
  "decisions": [
    {
      "description": "string",
      "rationale": "string or null",
      "confidence": 0.0
    }
  ],
  "deadlines": [
    {
      "description": "string",
      "inferred_date": "ISO date string or null",
      "confidence": 0.0
    }
  ]
}"""


def build_user_prompt(
    *,
    sender: str | None,
    subject: str | None,
    body: str | None,
    project_name: str | None = None,
    project_objective: str | None = None,
) -> str:
    """Assemble the user message for extraction.

    Args:
        sender: Sender identity.
        subject: Message subject.
        body: Message body text.
        project_name: Name of the classified project (if known).
        project_objective: Objective of the classified project.
    """
    parts: list[str] = []

    if project_name:
        parts.append(f"Project context: {project_name}")
        if project_objective:
            parts.append(f"  Objective: {project_objective}")
        parts.append("")

    parts.append("Message to analyze:")
    if sender:
        parts.append(f"  From: {sender}")
    if subject:
        parts.append(f"  Subject: {subject}")
    if body:
        parts.append(f"  Body: {body}")
    else:
        parts.append("  Body: (empty)")

    return "\n".join(parts)


RESPONSE_SCHEMA_DOC = """\
Expected JSON response:
{
  "actions": [{"description", "proposed_owner", "due_date_signal", "urgency_signal", "confidence"}],
  "decisions": [{"description", "rationale", "confidence"}],
  "deadlines": [{"description", "inferred_date", "confidence"}]
}"""


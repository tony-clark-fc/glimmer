"""Classification prompt — project classification from message context.

PLAN:WorkstreamI.PackageI2.PromptFramework
TEST:LLM.Classification.ProducesValidClassificationResult
TEST:LLM.Classification.ConfidenceAndRationalePresent

Used by the triage graph to classify which project a message belongs to.
The model receives the active project list and message metadata,
and returns a JSON classification with confidence and rationale.
"""

from __future__ import annotations


SYSTEM_PROMPT = """\
You are Glimmer, an AI project assistant for a busy operator managing multiple live projects.

Your task: given a message and a list of active projects, classify which project the message most likely relates to.

RULES:
- Choose the single best-matching project, or "none" if no project matches.
- Provide a confidence score between 0.0 and 1.0.
- Provide a brief rationale (1-2 sentences max).
- If multiple projects are plausible, list them as candidates with individual scores.
- If confidence is below 0.5, mark needs_review as true.
- Be conservative: do not force a match when the message is genuinely unrelated.
- Keep your JSON response COMPACT — no unnecessary whitespace or verbose explanations.

You MUST respond with ONLY valid JSON, no other text, no markdown fences, no explanation outside the JSON.

Use this exact schema:
{"project_name": "string or null", "project_id": "string or null", "confidence": 0.0, "rationale": "string", "needs_review": false, "review_reason": "string or null", "candidates": [{"project_id": "string", "project_name": "string", "score": 0.0, "reason": "string"}]}"""


def build_user_prompt(
    *,
    projects: list[dict],
    sender: str | None,
    subject: str | None,
    body: str | None,
    source_account: str | None = None,
) -> str:
    """Assemble the user message for classification.

    Args:
        projects: List of dicts with id, name, objective, short_summary.
        sender: Sender identity string.
        subject: Message subject.
        body: Message body text.
        source_account: Account label the message arrived on.
    """
    parts: list[str] = []

    # Project list
    parts.append("Active projects:")
    if not projects:
        parts.append("  (none)")
    for i, p in enumerate(projects, 1):
        line = f"  {i}. {p.get('name', 'Unnamed')}"
        if p.get("objective"):
            line += f" — {p['objective']}"
        if p.get("short_summary"):
            line += f" ({p['short_summary']})"
        line += f" [id: {p.get('id', '?')}]"
        parts.append(line)

    parts.append("")
    parts.append("Message to classify:")
    if sender:
        parts.append(f"  From: {sender}")
    if source_account:
        parts.append(f"  Account: {source_account}")
    if subject:
        parts.append(f"  Subject: {subject}")
    if body:
        parts.append(f"  Body: {body}")

    return "\n".join(parts)


RESPONSE_SCHEMA_DOC = """\
Expected JSON response:
{
  "project_name": "string or null — name of the matched project",
  "project_id": "string or null — UUID of the matched project",
  "confidence": "float 0.0-1.0 — classification confidence",
  "rationale": "string — explanation of why this project was chosen",
  "needs_review": "bool — true if confidence is low or ambiguous",
  "review_reason": "string or null — why review is needed",
  "candidates": [
    {
      "project_id": "string",
      "project_name": "string",
      "score": "float 0.0-1.0",
      "reason": "string"
    }
  ]
}"""


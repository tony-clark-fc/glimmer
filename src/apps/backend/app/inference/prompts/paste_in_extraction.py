"""Paste-in entity extraction prompt — structured entity extraction from pasted content.

PLAN:WorkstreamE.PackageE15.PersonaPagePasteIn
ARCH:PersonaPage.PasteInPipeline
REQ:PersonaPagePasteInIngestion

System and user prompts for extracting candidate entities from content the
operator pastes into the Glimmer persona page. Output is structured JSON
that maps directly to MindMapCandidateNode entries.

All extracted entities are INTERPRETED CANDIDATES — they enter the working
state as pending and require explicit operator review before persistence.
"""

from __future__ import annotations


SYSTEM_PROMPT = """\
You are Glimmer, an AI project chief-of-staff. The operator has pasted \
some content into the workspace for analysis.

Your job is to extract structured project entities from the pasted text. \
Return a JSON object with two keys:

1. "entities" — an array of extracted entities. Each entity has:
   - "entity_type": one of "project", "stakeholder", "milestone", "risk", \
"blocker", "work_item", "decision", "dependency"
   - "label": a short, clear name for the entity (max 80 chars)
   - "subtitle": optional detail or description (max 200 chars)
   - "confidence": how confident you are this is a real entity (0.0–1.0)

2. "explanation" — a concise conversational summary (2–4 sentences) \
explaining what you found in the pasted content and why. Written in first \
person as Glimmer.

RULES:
- Extract only entities that are clearly present or strongly implied.
- Do NOT invent entities not supported by the text.
- Prefer specific labels over vague ones.
- If the text contains very little extractable structure, return an empty \
entities array and explain why.
- Do not extract the same entity twice.
- Keep the explanation friendly and concise.

Respond ONLY with valid JSON, no markdown fences, no extra text."""


def build_user_prompt(
    *,
    raw_content: str,
    content_type_hint: str = "freeform",
    project_summaries: list[dict] | None = None,
) -> str:
    """Build the user prompt for paste-in entity extraction.

    Args:
        raw_content: The raw pasted text from the operator.
        content_type_hint: What kind of content this is.
        project_summaries: Active project context for grounding.
    """
    parts: list[str] = []

    parts.append(f"[Content type: {content_type_hint}]")
    parts.append("")

    if project_summaries:
        parts.append("Active projects for context:")
        for p in project_summaries[:8]:
            name = p.get("name", "Unnamed")
            obj = p.get("objective", "")
            line = f"  - {name}"
            if obj:
                line += f": {obj}"
            parts.append(line)
        parts.append("")

    # Truncate very long content to stay within token limits
    content = raw_content[:8000] if len(raw_content) > 8000 else raw_content
    parts.append("Pasted content:")
    parts.append("---")
    parts.append(content)
    parts.append("---")

    return "\n".join(parts)


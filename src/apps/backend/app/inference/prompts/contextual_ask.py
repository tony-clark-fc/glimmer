"""Contextual "Ask Glimmer" prompt — cross-surface element-scoped interaction.

PLAN:WorkstreamE.PackageE16.ContextualAskGlimmer
ARCH:ContextualAskGlimmerInteraction
REQ:ContextualAskGlimmer

System and user prompts for the contextual Ask Glimmer popover.
The model responds to operator questions about a specific data element
visible on one of the workspace surfaces.

Responses follow review-gate discipline: the model must flag when its
answer implies an externally meaningful action (draft, send, schedule).
"""

from __future__ import annotations

import json


SYSTEM_PROMPT = """\
You are Glimmer, a sharp, organised, and tactful AI project chief-of-staff.

The operator is asking you a question about a specific data element \
they can see on their workspace. You have the element's type, context data, \
and the surface they're viewing.

RULES:
- Be concise and directly helpful — answer about the specific element.
- Ground your answer in the element context provided.
- If you don't have enough information, say so honestly.
- Never make up data about projects, stakeholders, or deadlines.
- Never claim to have taken external actions (sent messages, etc.).
- You can suggest actions but you cannot execute them.
- Stay warm but professional. Avoid filler.

REVIEW-GATE RULE:
If the operator's question implies an externally meaningful action \
(e.g. "draft a follow-up", "send this to…", "schedule a meeting", \
"create a task for…", "update the calendar"), you MUST include the \
exact marker [REVIEW_REQUIRED] at the very end of your response. \
This tells the system the response implies an action that needs \
operator approval before execution.

Do NOT include [REVIEW_REQUIRED] for informational questions, \
explanations, summaries, or advice that doesn't imply external action.

Respond in plain text (not JSON, not markdown fences). \
Keep responses under 300 words."""


def build_user_prompt(
    *,
    element_type: str,
    element_id: str,
    element_context: dict,
    surface: str,
    question: str,
    project_summaries: list[dict] | None = None,
) -> str:
    """Assemble the user prompt with element context.

    Args:
        element_type: Type of the data element (project, action_item, risk, etc.).
        element_id: Unique identifier of the element.
        element_context: Serialized data from the element.
        surface: Workspace surface the operator is viewing.
        question: The operator's question about this element.
        project_summaries: Active project summaries for broader context.
    """
    parts: list[str] = []

    parts.append(f"[Surface: {surface}]")
    parts.append(f"[Element type: {element_type}]")
    parts.append(f"[Element ID: {element_id}]")
    parts.append("")

    # Element context — serialized compactly
    if element_context:
        context_str = json.dumps(element_context, indent=None, default=str)
        # Truncate if very long to fit token budget
        if len(context_str) > 2000:
            context_str = context_str[:2000] + "…"
        parts.append(f"Element data: {context_str}")
        parts.append("")

    if project_summaries:
        parts.append("Active projects for reference:")
        for p in project_summaries[:5]:
            name = p.get("name", "Unnamed")
            line = f"  - {name}"
            obj = p.get("objective", "")
            if obj:
                line += f": {obj}"
            parts.append(line)
        parts.append("")

    parts.append(f"Operator's question: {question}")

    return "\n".join(parts)


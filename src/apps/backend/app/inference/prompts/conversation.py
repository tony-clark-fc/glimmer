"""Conversation prompt — persona-page chat completion.

PLAN:WorkstreamE.PackageE12.PersonaPageConversationUi
ARCH:PersonaPage.ConversationModel
REQ:GlimmerPersonaPage

System and user prompts for the persona-page conversational interface.
The model acts as Glimmer — the operator's project chief-of-staff — and
responds naturally while staying grounded in the operator's portfolio.

No auto-send, no autonomous external actions.
"""

from __future__ import annotations


SYSTEM_PROMPT = """\
You are Glimmer, a sharp, organised, and tactful AI project chief-of-staff.

You are chatting with your operator on the Glimmer persona page. \
Your role is to help them manage their projects, triage new information, \
plan work, and stay on top of priorities.

RULES:
- Be concise and helpful — like a trusted senior EA, not a chatbot.
- Ground your answers in the provided project/portfolio context.
- If you don't have enough information, say so honestly.
- Never make up data about projects, stakeholders, or deadlines.
- Never claim to have sent messages, emails, or calendar invitations.
- You can suggest actions but you cannot execute external actions.
- Stay warm but professional. Avoid filler.
- Match the current workspace mode (provided below) in your focus:
  • idea: help brainstorm, explore concepts, extract project elements
  • plan: discuss milestones, tasks, timelines, dependencies
  • report: summarise recent activity and what's changed
  • debrief: listen to what the operator did, extract actions/updates
  • update: highlight new inbox items and what needs attention

Respond in plain text (not JSON, not markdown fences). \
Keep responses under 500 words."""


def build_user_prompt(
    *,
    operator_message: str,
    workspace_mode: str = "update",
    message_history: list[dict] | None = None,
    project_summaries: list[dict] | None = None,
    portfolio_health: dict | None = None,
) -> str:
    """Assemble the user prompt with conversation context.

    Args:
        operator_message: The current message from the operator.
        workspace_mode: Active workspace mode (idea/plan/report/debrief/update).
        message_history: Recent prior messages [{role, content}].
        project_summaries: Active project summaries for context.
        portfolio_health: Current portfolio health metrics.
    """
    parts: list[str] = []

    parts.append(f"[Workspace mode: {workspace_mode}]")
    parts.append("")

    if portfolio_health:
        health_lines = []
        if portfolio_health.get("active_projects"):
            health_lines.append(f"{portfolio_health['active_projects']} active projects")
        if portfolio_health.get("active_blockers"):
            health_lines.append(f"{portfolio_health['active_blockers']} blockers")
        if portfolio_health.get("overdue_items"):
            health_lines.append(f"{portfolio_health['overdue_items']} overdue items")
        if health_lines:
            parts.append(f"Portfolio snapshot: {', '.join(health_lines)}")
            parts.append("")

    if project_summaries:
        parts.append("Active projects:")
        for p in project_summaries[:8]:  # Limit to avoid token overflow
            name = p.get("name", "Unnamed")
            obj = p.get("objective", "")
            line = f"  - {name}"
            if obj:
                line += f": {obj}"
            parts.append(line)
        parts.append("")

    if message_history:
        parts.append("Recent conversation:")
        # Include last 10 messages for context window management
        for msg in message_history[-10:]:
            role_label = "Operator" if msg.get("role") == "user" else "Glimmer"
            parts.append(f"  {role_label}: {msg['content']}")
        parts.append("")

    parts.append(f"Operator's message: {operator_message}")

    return "\n".join(parts)


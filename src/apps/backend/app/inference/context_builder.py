"""Context builder — assembles domain objects into prompt-ready context.

PLAN:WorkstreamI.PackageI2.PromptFramework
TEST:LLM.Prompts.ContextBuilderAssemblesRelevantContext
TEST:LLM.Prompts.TokenBudgetRespected

Converts SQLAlchemy domain objects into prompt-ready dictionaries,
manages token budgets, and handles truncation when context exceeds
the available window.

Token estimation uses a simple chars/4 heuristic — sufficient for
budget management without requiring a tokenizer dependency.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# ── Token Estimation ─────────────────────────────────────────────────

# Simple heuristic: ~4 characters per token on average for English text.
# This is conservative (real tokenizers are closer to 3.5-4.5) but safe
# for budget management — we'd rather leave headroom than overflow.
CHARS_PER_TOKEN = 4


def estimate_tokens(text: str) -> int:
    """Estimate the token count of a text string.

    Uses chars/4 heuristic — sufficient for budget management.
    """
    if not text:
        return 0
    return max(1, len(text) // CHARS_PER_TOKEN)


def truncate_to_token_budget(text: str, max_tokens: int) -> str:
    """Truncate text to fit within a token budget.

    Truncates at word boundaries when possible to avoid mid-word cuts.
    """
    if estimate_tokens(text) <= max_tokens:
        return text

    max_chars = max_tokens * CHARS_PER_TOKEN
    truncated = text[:max_chars]

    # Try to truncate at a word boundary
    last_space = truncated.rfind(" ")
    if last_space > max_chars * 0.8:  # Don't cut too aggressively
        truncated = truncated[:last_space]

    return truncated + "..."


# ── Token Budget ─────────────────────────────────────────────────────

# Default token budget allocation for a typical task.
# Total context window: 52,000 tokens (Gemma 4 31B in LM Studio)
# We reserve generous headroom.

@dataclass
class TokenBudget:
    """Token budget allocation for a prompt."""

    system_prompt: int = 500
    project_context: int = 2000
    message_content: int = 2000
    stakeholder_context: int = 500
    response_space: int = 2000
    total_window: int = 52000

    @property
    def available_for_content(self) -> int:
        """Tokens available for dynamic content (projects + message + stakeholders)."""
        return self.total_window - self.system_prompt - self.response_space

    def remaining_after(self, used_tokens: int) -> int:
        """Tokens remaining after some have been used."""
        return max(0, self.available_for_content - used_tokens)


DEFAULT_BUDGET = TokenBudget()


# ── Project Context Builder ──────────────────────────────────────────


def build_project_context(
    projects: list,
    max_tokens: int = DEFAULT_BUDGET.project_context,
) -> list[dict]:
    """Convert project domain objects to prompt-ready dictionaries.

    Truncates individual project summaries to fit the token budget.
    Projects should have: id, name, objective, short_summary, status.

    Args:
        projects: List of Project model instances or dicts.
        max_tokens: Maximum tokens for the entire project context.

    Returns:
        List of dictionaries suitable for prompt templates.
    """
    result: list[dict] = []
    tokens_used = 0

    for project in projects:
        # Handle both ORM objects and dicts
        if isinstance(project, dict):
            p = project
        else:
            p = {
                "id": str(getattr(project, "id", "")),
                "name": getattr(project, "name", ""),
                "objective": getattr(project, "objective", ""),
                "short_summary": getattr(project, "short_summary", ""),
                "status": getattr(project, "status", ""),
            }

        # Estimate tokens for this project entry
        entry_text = f"{p.get('name', '')} {p.get('objective', '')} {p.get('short_summary', '')}"
        entry_tokens = estimate_tokens(entry_text)

        if tokens_used + entry_tokens > max_tokens:
            # Truncate the summary to fit
            remaining = max_tokens - tokens_used
            if remaining < 20:
                break  # Not enough room for a meaningful entry
            if p.get("short_summary"):
                p["short_summary"] = truncate_to_token_budget(
                    p["short_summary"], remaining - 10  # Reserve for name/objective
                )

        result.append(p)
        tokens_used += entry_tokens

    return result


# ── Message Context Builder ──────────────────────────────────────────


def build_message_context(
    sender: str | None,
    subject: str | None,
    body: str | None,
    max_tokens: int = DEFAULT_BUDGET.message_content,
) -> dict:
    """Build message context within token budget.

    Truncates body text if it exceeds the budget — subject and sender
    are kept intact as they're typically short.

    Returns:
        Dictionary with sender, subject, body (possibly truncated).
    """
    # Subject and sender are usually short, keep them intact
    overhead_tokens = estimate_tokens(f"{sender or ''} {subject or ''}")
    body_budget = max_tokens - overhead_tokens

    truncated_body = body
    if body and estimate_tokens(body) > body_budget:
        truncated_body = truncate_to_token_budget(body, body_budget)
        logger.info(
            "Message body truncated from %d to %d estimated tokens",
            estimate_tokens(body),
            estimate_tokens(truncated_body),
        )

    return {
        "sender": sender,
        "subject": subject,
        "body": truncated_body,
    }


# ── Stakeholder Context Builder ──────────────────────────────────────


def build_stakeholder_context(
    stakeholders: list,
    max_tokens: int = DEFAULT_BUDGET.stakeholder_context,
) -> list[str]:
    """Build stakeholder names/identities within token budget.

    Args:
        stakeholders: List of Stakeholder model instances or dicts.
        max_tokens: Maximum tokens for stakeholder context.

    Returns:
        List of stakeholder name strings.
    """
    names: list[str] = []
    tokens_used = 0

    for stakeholder in stakeholders:
        if isinstance(stakeholder, dict):
            name = stakeholder.get("display_name") or stakeholder.get("name", "Unknown")
        else:
            name = getattr(stakeholder, "display_name", None) or getattr(stakeholder, "name", "Unknown")

        entry_tokens = estimate_tokens(name)
        if tokens_used + entry_tokens > max_tokens:
            break

        names.append(name)
        tokens_used += entry_tokens

    return names


# ── Full Prompt Assembly ─────────────────────────────────────────────


def assemble_messages(
    system_prompt: str,
    user_prompt: str,
) -> list[dict[str, str]]:
    """Assemble system and user prompts into the messages format.

    Returns:
        List of message dicts in OpenAI chat format.
    """
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def estimate_prompt_tokens(
    system_prompt: str,
    user_prompt: str,
) -> int:
    """Estimate total token usage for a prompt pair."""
    return estimate_tokens(system_prompt) + estimate_tokens(user_prompt)


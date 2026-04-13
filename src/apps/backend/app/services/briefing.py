"""Spoken briefing generation — listening-friendly output from focus/priority data.

ARCH:VoiceInteractionArchitecture
ARCH:VoiceLayeringStrategy
ARCH:BriefingSurfaceArchitecture
REQ:PreparedBriefings
REQ:Explainability

Formats focus-pack, priority, and project-context data into concise
spoken briefings suitable for voice delivery. Spoken output is shorter,
more structured, and more direct than screen text.

WF5 — Spoken briefing and bounded response behavior.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.drafting import BriefingArtifact, FocusPack


# ── Constants ────────────────────────────────────────────────────────

# Maximum items to mention in a spoken briefing to keep it listenable
MAX_SPOKEN_ACTIONS = 3
MAX_SPOKEN_RISKS = 2
MAX_SPOKEN_WAITING = 2

# Maximum character length for a spoken briefing
MAX_BRIEFING_LENGTH = 800


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ── Spoken Briefing Result ───────────────────────────────────────────


class SpokenBriefingResult:
    """Result of spoken briefing generation.

    TEST:Voice.Session.SpokenBriefingIsBoundedAndRelevant
    """

    def __init__(
        self,
        briefing_text: str,
        briefing_artifact_id: uuid.UUID | None,
        section_count: int,
        is_empty: bool,
        source_focus_pack_id: uuid.UUID | None,
    ):
        self.briefing_text = briefing_text
        self.briefing_artifact_id = briefing_artifact_id
        self.section_count = section_count
        self.is_empty = is_empty
        self.source_focus_pack_id = source_focus_pack_id


# ── Focus Pack Formatting ────────────────────────────────────────────


def _format_top_actions(top_actions: dict | None) -> str | None:
    """Format top actions for spoken delivery."""
    if not top_actions:
        return None
    items = top_actions.get("items", [])
    if not items:
        return None

    bounded = items[:MAX_SPOKEN_ACTIONS]
    lines = []
    for i, item in enumerate(bounded, 1):
        title = item.get("title", "Untitled item")
        # Truncate long titles for speech
        if len(title) > 80:
            title = title[:77] + "..."
        rationale = item.get("rationale", "")
        if rationale:
            lines.append(f"{i}. {title} — {rationale}")
        else:
            lines.append(f"{i}. {title}")

    remaining = len(items) - len(bounded)
    header = "Your top priorities"
    if remaining > 0:
        header += f" (plus {remaining} more)"

    return f"{header}: {'; '.join(lines)}."


def _format_risks(high_risk_items: dict | None) -> str | None:
    """Format high-risk items for spoken delivery."""
    if not high_risk_items:
        return None
    items = high_risk_items.get("items", [])
    if not items:
        return None

    bounded = items[:MAX_SPOKEN_RISKS]
    parts = []
    for item in bounded:
        summary = item.get("summary", "unnamed risk")
        if len(summary) > 60:
            summary = summary[:57] + "..."
        parts.append(summary)

    remaining = len(items) - len(bounded)
    count_text = f"{len(items)} risk item{'s' if len(items) != 1 else ''}"
    if remaining > 0:
        return f"{count_text} flagged, including: {'; '.join(parts)}."
    return f"Risk{'s' if len(items) != 1 else ''} flagged: {'; '.join(parts)}."


def _format_waiting(waiting_on_items: dict | None) -> str | None:
    """Format waiting-on items for spoken delivery."""
    if not waiting_on_items:
        return None
    items = waiting_on_items.get("items", [])
    if not items:
        return None

    bounded = items[:MAX_SPOKEN_WAITING]
    parts = []
    for item in bounded:
        whom = item.get("waiting_on", "someone")
        desc = item.get("description", "")
        if desc:
            short_desc = desc[:50] + "..." if len(desc) > 50 else desc
            parts.append(f"{whom} on {short_desc}")
        else:
            parts.append(whom)

    remaining = len(items) - len(bounded)
    if remaining > 0:
        return f"Waiting on {len(items)} responses, including: {'; '.join(parts)}."
    return f"Waiting on: {'; '.join(parts)}."


def _format_pressure(
    reply_debt: str | None,
    calendar_pressure: str | None,
) -> str | None:
    """Format pressure indicators for spoken delivery."""
    parts = []
    if reply_debt:
        parts.append(reply_debt)
    if calendar_pressure:
        parts.append(calendar_pressure)
    if not parts:
        return None
    return "Pressure: " + ". ".join(parts) + "."


# ── Main Briefing Generation ─────────────────────────────────────────


def generate_spoken_briefing(
    db: Session,
    *,
    focus_pack_id: uuid.UUID | None = None,
    project_ids: list[uuid.UUID] | None = None,
    channel_session_id: uuid.UUID | None = None,
) -> SpokenBriefingResult:
    """Generate a bounded spoken briefing from focus-pack data.

    TEST:Voice.Session.SpokenBriefingIsBoundedAndRelevant

    If focus_pack_id is given, uses that specific focus pack.
    Otherwise, uses the most recent focus pack (optionally filtered
    by project_ids in its source scope).

    The briefing is:
    - concise (bounded to MAX_BRIEFING_LENGTH)
    - structured for listening (numbered items, short sentences)
    - grounded in real focus-pack data (not hallucinated)
    - persisted as a BriefingArtifact for traceability
    """
    # Resolve focus pack
    focus_pack = _resolve_focus_pack(db, focus_pack_id)

    if focus_pack is None:
        return SpokenBriefingResult(
            briefing_text="No focus data available yet. Connect accounts and run a planning cycle to generate your first briefing.",
            briefing_artifact_id=None,
            section_count=0,
            is_empty=True,
            source_focus_pack_id=None,
        )

    # Build spoken sections from focus pack data
    sections: list[str] = []

    actions_text = _format_top_actions(focus_pack.top_actions)
    if actions_text:
        sections.append(actions_text)

    risks_text = _format_risks(focus_pack.high_risk_items)
    if risks_text:
        sections.append(risks_text)

    waiting_text = _format_waiting(focus_pack.waiting_on_items)
    if waiting_text:
        sections.append(waiting_text)

    pressure_text = _format_pressure(
        focus_pack.reply_debt_summary,
        focus_pack.calendar_pressure_summary,
    )
    if pressure_text:
        sections.append(pressure_text)

    if not sections:
        briefing_text = "Everything looks clear right now. No urgent actions, risks, or waiting items."
        is_empty = True
    else:
        briefing_text = " ".join(sections)
        is_empty = False

    # Enforce length bound
    if len(briefing_text) > MAX_BRIEFING_LENGTH:
        briefing_text = briefing_text[: MAX_BRIEFING_LENGTH - 3] + "..."

    # Persist as BriefingArtifact
    artifact = BriefingArtifact(
        briefing_type="voice_spoken_briefing",
        content=briefing_text,
        source_scope_metadata={
            "source_focus_pack_id": str(focus_pack.id),
            "channel_session_id": str(channel_session_id) if channel_session_id else None,
            "project_ids": [str(p) for p in (project_ids or [])],
            "section_count": len(sections),
        },
    )
    db.add(artifact)
    db.flush()

    return SpokenBriefingResult(
        briefing_text=briefing_text,
        briefing_artifact_id=artifact.id,
        section_count=len(sections),
        is_empty=is_empty,
        source_focus_pack_id=focus_pack.id,
    )


def _resolve_focus_pack(
    db: Session,
    focus_pack_id: uuid.UUID | None,
) -> FocusPack | None:
    """Resolve the focus pack to use for briefing generation."""
    if focus_pack_id:
        return db.get(FocusPack, focus_pack_id)

    # Get the most recent focus pack
    result = db.execute(
        select(FocusPack).order_by(FocusPack.generated_at.desc()).limit(1)
    ).scalar_one_or_none()
    return result


# ── Session-Context Spoken Response ──────────────────────────────────


def generate_session_context_response(
    *,
    current_topic: str | None,
    utterance_count: int,
    referenced_project_ids: list[str],
    unresolved_prompts: list[str],
) -> str:
    """Generate a bounded spoken context summary for the current session.

    This is not a full briefing — it's a short orientation response
    when the operator asks "where are we?" during a voice session.

    TEST:Voice.Session.SpokenBriefingIsBoundedAndRelevant
    """
    parts: list[str] = []

    if current_topic:
        parts.append(f"We're discussing {current_topic}.")
    else:
        parts.append("No specific topic set for this session.")

    if utterance_count > 0:
        parts.append(f"{utterance_count} exchange{'s' if utterance_count != 1 else ''} so far.")

    if referenced_project_ids:
        count = len(referenced_project_ids)
        parts.append(f"Touching {count} project{'s' if count != 1 else ''}.")

    if unresolved_prompts:
        count = len(unresolved_prompts)
        parts.append(f"{count} open question{'s' if count != 1 else ''} remaining.")

    return " ".join(parts)



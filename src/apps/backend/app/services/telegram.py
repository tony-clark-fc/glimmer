"""Telegram companion service — bounded mobile interaction support.

ARCH:TelegramCompanionChannel
ARCH:TelegramCompanionUx
ARCH:TelegramCompanionInteractionStyle
ARCH:ChannelSessionModel
REQ:TelegramMobilePresence
REQ:HumanApprovalBoundaries

Services for Telegram companion session lifecycle. Telegram is a
bounded companion surface — not a second control room.

Supported interactions:
- "what matters now?" → bounded focus summary
- note/action capture → ImportedSignal with telegram provenance
- handoff to workspace when richer review is needed

WF6 — Telegram bounded companion interaction.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.channel import ChannelSession, TelegramConversationState
from app.models.source import ImportedSignal
from app.services.briefing import generate_spoken_briefing


def _genuuid() -> uuid.UUID:
    return uuid.uuid4()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ── Constants ────────────────────────────────────────────────────────

# Maximum length for a Telegram companion response
MAX_TELEGRAM_RESPONSE_LENGTH = 500

# Interactions that should trigger a workspace handoff
HANDOFF_TRIGGERS = [
    "review",
    "approve",
    "compare",
    "draft comparison",
    "detailed",
    "full context",
    "show me everything",
]


# ── Session Bootstrap ────────────────────────────────────────────────


def bootstrap_telegram_session(
    db: Session,
    *,
    telegram_chat_id: str,
    operator_id: uuid.UUID | None = None,
) -> tuple[ChannelSession, TelegramConversationState]:
    """Create a ChannelSession + TelegramConversationState for a Telegram chat.

    TEST:Telegram.Companion.WhatMattersNowReturnsBoundedSummary

    If an active session already exists for this chat_id, returns it.
    Otherwise creates a new one.
    """
    # Check for existing active session
    existing = db.execute(
        select(TelegramConversationState).where(
            TelegramConversationState.telegram_chat_id == telegram_chat_id,
        )
    ).scalar_one_or_none()

    if existing:
        channel_session = db.get(ChannelSession, existing.channel_session_id)
        if channel_session and channel_session.session_state == "active":
            # Update last interaction
            channel_session.last_interaction_at = _utcnow()
            db.flush()
            return channel_session, existing

    # Create new session
    channel_session = ChannelSession(
        operator_id=operator_id,
        channel_type="telegram",
        channel_identity=f"telegram_{telegram_chat_id}",
        session_state="active",
        last_interaction_at=_utcnow(),
        session_metadata={
            "telegram_chat_id": telegram_chat_id,
        },
    )
    db.add(channel_session)
    db.flush()

    telegram_state = TelegramConversationState(
        channel_session_id=channel_session.id,
        telegram_chat_id=telegram_chat_id,
        state_data={
            "message_count": 0,
            "topics_discussed": [],
        },
    )
    db.add(telegram_state)
    db.flush()

    return channel_session, telegram_state


# ── Message Normalization ────────────────────────────────────────────


def normalize_telegram_message(
    db: Session,
    *,
    channel_session_id: uuid.UUID,
    telegram_chat_id: str,
    text: str,
    telegram_message_id: str | None = None,
) -> uuid.UUID | None:
    """Normalize a Telegram message into an ImportedSignal.

    TEST:Telegram.Companion.WhatMattersNowReturnsBoundedSummary

    Returns the ImportedSignal ID, or None if text is empty.
    """
    if not text.strip():
        return None

    signal = ImportedSignal(
        signal_type="telegram_import",
        source_label=f"telegram:{telegram_chat_id}",
        content=text.strip(),
        raw_metadata={
            "channel_session_id": str(channel_session_id),
            "telegram_chat_id": telegram_chat_id,
            "telegram_message_id": telegram_message_id,
            "provider": "telegram",
        },
    )
    db.add(signal)
    db.flush()
    return signal.id


# ── Session State Update ─────────────────────────────────────────────


def update_telegram_context(
    db: Session,
    *,
    telegram_state_id: uuid.UUID,
    current_topic: str | None = None,
    message_text: str | None = None,
) -> TelegramConversationState:
    """Update Telegram session state with bounded context.

    TEST:Telegram.Companion.WhatMattersNowReturnsBoundedSummary
    """
    state = db.get(TelegramConversationState, telegram_state_id)
    if state is None:
        raise ValueError(f"TelegramConversationState {telegram_state_id} not found")

    if current_topic is not None:
        state.current_topic = current_topic

    state_data = dict(state.state_data or {})
    state_data["message_count"] = state_data.get("message_count", 0) + 1

    if current_topic:
        topics = state_data.get("topics_discussed", [])
        if current_topic not in topics:
            topics.append(current_topic)
            state_data["topics_discussed"] = topics[-5:]  # bounded

    state.state_data = state_data
    db.flush()
    return state


# ── "What Matters Now" Summary ───────────────────────────────────────


def generate_what_matters_now(
    db: Session,
    *,
    channel_session_id: uuid.UUID | None = None,
) -> dict:
    """Generate a bounded "what matters now" summary for Telegram.

    TEST:Telegram.Companion.WhatMattersNowReturnsBoundedSummary

    Uses the same focus-pack data as the voice briefing but formats
    it even more concisely for mobile Telegram delivery.
    """
    result = generate_spoken_briefing(
        db,
        channel_session_id=channel_session_id,
    )

    # Further condense for Telegram
    briefing_text = result.briefing_text
    if len(briefing_text) > MAX_TELEGRAM_RESPONSE_LENGTH:
        briefing_text = briefing_text[:MAX_TELEGRAM_RESPONSE_LENGTH - 3] + "..."

    return {
        "summary_text": briefing_text,
        "section_count": result.section_count,
        "is_empty": result.is_empty,
        "auto_send_blocked": True,  # Hard rule — always
    }


# ── Handoff Detection ────────────────────────────────────────────────


def detect_handoff_needed(message_text: str) -> tuple[bool, str]:
    """Determine if a Telegram message needs workspace handoff.

    TEST:Telegram.Companion.HandoffToWorkspaceOccursWhenNeeded

    Returns (needs_handoff, reason).
    """
    lower = message_text.lower()
    for trigger in HANDOFF_TRIGGERS:
        if trigger in lower:
            return True, f"Interaction requires workspace: '{trigger}' detected"
    return False, ""


def generate_handoff_response(
    *,
    reason: str,
    channel_session_id: uuid.UUID,
    workspace_base_url: str = "http://localhost:3000",
) -> dict:
    """Generate a handoff response directing the operator to the workspace.

    TEST:Telegram.Companion.HandoffToWorkspaceOccursWhenNeeded

    Includes a workspace link and context for what needs review.
    """
    return {
        "handoff_needed": True,
        "reason": reason,
        "workspace_url": f"{workspace_base_url}/review",
        "channel_session_id": str(channel_session_id),
        "message": f"This needs the full workspace. {reason} — open Glimmer to continue.",
        "auto_send_blocked": True,  # Hard rule — always
    }


# ── Telegram Route-to-Core ───────────────────────────────────────────


def route_telegram_to_core(
    *,
    signal_id: uuid.UUID,
    channel_session_id: uuid.UUID,
) -> dict:
    """Route a Telegram-derived signal into the shared IntakeGraph.

    TEST:VoiceAndTelegram.SharedCoreFlowParityPreserved

    Same shared core as voice — not a separate Telegram logic path.
    """
    from app.graphs.intake import get_intake_graph

    compiled = get_intake_graph()

    intake_state = {
        "source_record_ids": [signal_id],
        "record_type": "imported_signal",
        "provider_type": "telegram",
        "channel": "telegram",
        "workflow_id": str(uuid.uuid4()),
        "initiated_at": _utcnow().isoformat(),
    }

    result = compiled.invoke(intake_state)
    return {
        "route_target": result.get("route_target", "triage"),
        "route_reason": result.get("route_reason", "Telegram signal routed to triage"),
        "workflow_id": result.get("workflow_id", ""),
        "auto_send_blocked": True,  # Hard rule — always
    }


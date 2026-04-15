"""Telegram companion API — bounded mobile interaction endpoints.

ARCH:TelegramCompanionChannel
ARCH:TelegramCompanionUx
REQ:TelegramMobilePresence
REQ:HumanApprovalBoundaries

REST endpoints for Telegram companion interaction. Telegram is a
bounded companion surface — quick check-ins, brief questions,
note capture, and handoff to the main workspace.

WF6 — Telegram bounded companion interaction.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.channel import TelegramConversationState
from app.services.telegram import (
    bootstrap_telegram_session,
    normalize_telegram_message,
    update_telegram_context,
    generate_what_matters_now,
    detect_handoff_needed,
    generate_handoff_response,
    route_telegram_to_core,
)
from app.services.handoff import create_handoff_from_telegram, get_pending_handoffs

router = APIRouter(prefix="/telegram", tags=["telegram"])


# ── Request/Response contracts ────────────────────────────────────


class TelegramSessionCreateRequest(BaseModel):
    """Request to create or resume a Telegram session."""
    telegram_chat_id: str
    operator_id: Optional[str] = None


class TelegramSessionResponse(BaseModel):
    """Response for a Telegram session."""
    session_id: str
    channel_session_id: str
    telegram_chat_id: str
    message_count: int


class TelegramMessageRequest(BaseModel):
    """Request to process a Telegram message."""
    text: str
    telegram_message_id: Optional[str] = None


class TelegramMessageResponse(BaseModel):
    """Response for a processed Telegram message."""
    signal_id: Optional[str]
    route_target: str
    route_reason: str
    handoff_needed: bool
    handoff_url: Optional[str]
    auto_send_blocked: bool


class TelegramSummaryResponse(BaseModel):
    """Response for a 'what matters now' summary."""
    summary_text: str
    section_count: int
    is_empty: bool
    auto_send_blocked: bool


# ── Routes ────────────────────────────────────────────────────────


@router.post("/sessions")
def create_telegram_session(
    req: TelegramSessionCreateRequest,
    db: Session = Depends(get_db),
) -> TelegramSessionResponse:
    """Create or resume a Telegram companion session.

    TEST:Telegram.Companion.WhatMattersNowReturnsBoundedSummary
    """
    import uuid

    operator_id = uuid.UUID(req.operator_id) if req.operator_id else None

    channel_session, telegram_state = bootstrap_telegram_session(
        db,
        telegram_chat_id=req.telegram_chat_id,
        operator_id=operator_id,
    )
    db.commit()

    state_data = telegram_state.state_data or {}
    return TelegramSessionResponse(
        session_id=str(telegram_state.id),
        channel_session_id=str(channel_session.id),
        telegram_chat_id=req.telegram_chat_id,
        message_count=state_data.get("message_count", 0),
    )


@router.get("/sessions/{session_id}")
def get_telegram_session(
    session_id: str,
    db: Session = Depends(get_db),
) -> TelegramSessionResponse:
    """Get the current state of a Telegram session."""
    import uuid

    telegram_state = db.get(TelegramConversationState, uuid.UUID(session_id))
    if telegram_state is None:
        raise HTTPException(status_code=404, detail="Telegram session not found")

    state_data = telegram_state.state_data or {}
    return TelegramSessionResponse(
        session_id=str(telegram_state.id),
        channel_session_id=str(telegram_state.channel_session_id),
        telegram_chat_id=telegram_state.telegram_chat_id,
        message_count=state_data.get("message_count", 0),
    )


@router.post("/sessions/{session_id}/messages")
def process_telegram_message(
    session_id: str,
    req: TelegramMessageRequest,
    db: Session = Depends(get_db),
) -> TelegramMessageResponse:
    """Process an incoming Telegram message.

    TEST:Telegram.Companion.HandoffToWorkspaceOccursWhenNeeded
    TEST:VoiceAndTelegram.SharedCoreFlowParityPreserved
    """
    import uuid

    telegram_state = db.get(TelegramConversationState, uuid.UUID(session_id))
    if telegram_state is None:
        raise HTTPException(status_code=404, detail="Telegram session not found")

    # Check if handoff is needed before processing
    handoff_needed, handoff_reason = detect_handoff_needed(req.text)

    # Normalize the message into an ImportedSignal
    signal_id = normalize_telegram_message(
        db,
        channel_session_id=telegram_state.channel_session_id,
        telegram_chat_id=telegram_state.telegram_chat_id,
        text=req.text,
        telegram_message_id=req.telegram_message_id,
    )

    # Update session context
    update_telegram_context(
        db,
        telegram_state_id=telegram_state.id,
        message_text=req.text,
    )

    # Route to shared core
    if signal_id:
        routing = route_telegram_to_core(
            signal_id=signal_id,
            channel_session_id=telegram_state.channel_session_id,
        )
    else:
        routing = {
            "route_target": "none",
            "route_reason": "Empty message — nothing to route",
            "auto_send_blocked": True,
        }

    db.commit()

    handoff_url = None
    if handoff_needed:
        handoff = generate_handoff_response(
            reason=handoff_reason,
            channel_session_id=telegram_state.channel_session_id,
        )
        handoff_url = handoff["workspace_url"]

    return TelegramMessageResponse(
        signal_id=str(signal_id) if signal_id else None,
        route_target=routing["route_target"],
        route_reason=routing["route_reason"],
        handoff_needed=handoff_needed,
        handoff_url=handoff_url,
        auto_send_blocked=True,  # Hard rule — always
    )


@router.post("/sessions/{session_id}/what-matters-now")
def what_matters_now(
    session_id: str,
    db: Session = Depends(get_db),
) -> TelegramSummaryResponse:
    """Get a bounded 'what matters now' summary for Telegram.

    TEST:Telegram.Companion.WhatMattersNowReturnsBoundedSummary
    """
    import uuid

    telegram_state = db.get(TelegramConversationState, uuid.UUID(session_id))
    if telegram_state is None:
        raise HTTPException(status_code=404, detail="Telegram session not found")

    result = generate_what_matters_now(
        db,
        channel_session_id=telegram_state.channel_session_id,
    )

    return TelegramSummaryResponse(
        summary_text=result["summary_text"],
        section_count=result["section_count"],
        is_empty=result["is_empty"],
        auto_send_blocked=result["auto_send_blocked"],
    )


@router.post("/sessions/{session_id}/handoff")
def create_telegram_handoff(
    session_id: str,
    db: Session = Depends(get_db),
) -> dict:
    """Create a workspace-visible handoff from a Telegram session.

    TEST:Telegram.Companion.HandoffToWorkspaceOccursWhenNeeded
    TEST:Voice.Session.HandoffCreatesWorkspaceVisibleContinuation
    """
    import uuid

    telegram_state = db.get(TelegramConversationState, uuid.UUID(session_id))
    if telegram_state is None:
        raise HTTPException(status_code=404, detail="Telegram session not found")

    state_data = telegram_state.state_data or {}

    handoff = create_handoff_from_telegram(
        db,
        channel_session_id=telegram_state.channel_session_id,
        telegram_chat_id=telegram_state.telegram_chat_id,
        reason="Telegram session handoff to workspace",
        current_topic=telegram_state.current_topic,
        message_count=state_data.get("message_count", 0),
    )
    db.commit()

    return handoff.to_dict()


@router.get("/handoffs/pending")
def list_pending_handoffs(
    db: Session = Depends(get_db),
) -> list[dict]:
    """List all pending handoffs from companion channels.

    TEST:Telegram.Companion.ReviewNeededStateSurfacesInWorkspace
    """
    records = get_pending_handoffs(db)
    return [r.to_dict() for r in records]


"""Voice session API — bootstrap, utterances, and session lifecycle.

ARCH:VoiceInteractionArchitecture
ARCH:VoiceSessionGraph
REQ:VoiceInteraction
REQ:HumanApprovalBoundaries

REST endpoints for voice session management. Per-utterance POST model
for WF1-WF4 testability. WebSocket streaming can be added later for
real-time voice (WF5+).
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.channel import ChannelSession, VoiceSessionState
from app.services.voice import (
    bootstrap_voice_session,
    normalize_utterances,
    update_session_context,
    create_session_summary,
    route_voice_to_core,
)
from app.services.briefing import (
    generate_spoken_briefing,
    generate_session_context_response,
)
from app.services.handoff import create_handoff_from_voice

router = APIRouter(prefix="/voice", tags=["voice"])


# ── Request/Response contracts ────────────────────────────────────


class VoiceSessionCreateRequest(BaseModel):
    """Request to create a new voice session."""
    operator_id: Optional[str] = None
    project_context_ids: list[str] = []


class VoiceSessionResponse(BaseModel):
    """Response for a voice session."""
    session_id: str
    channel_session_id: str
    status: str


class VoiceUtteranceRequest(BaseModel):
    """Request to submit a voice utterance."""
    text: str
    timestamp: Optional[str] = None
    metadata: Optional[dict] = None


class VoiceUtteranceResponse(BaseModel):
    """Response for a submitted utterance."""
    signal_id: str
    route_target: str
    route_reason: str
    auto_send_blocked: bool


class SpokenBriefingResponse(BaseModel):
    """Response for a spoken briefing request."""
    briefing_text: str
    briefing_artifact_id: Optional[str]
    section_count: int
    is_empty: bool
    auto_send_blocked: bool


class VoiceSessionDetailResponse(BaseModel):
    """Detail response for a voice session."""
    session_id: str
    channel_session_id: str
    status: str
    current_topic: Optional[str]
    utterance_count: int
    summary: Optional[str]
    referenced_project_ids: list[str]


# ── Routes ────────────────────────────────────────────────────────


@router.post("/sessions")
def create_voice_session(
    req: VoiceSessionCreateRequest,
    db: Session = Depends(get_db),
) -> VoiceSessionResponse:
    """Create a new voice session.

    TEST:Voice.Session.BootstrapBindsCorrectOperatorAndSession
    """
    import uuid

    operator_id = uuid.UUID(req.operator_id) if req.operator_id else None
    project_ids = [uuid.UUID(p) for p in req.project_context_ids]

    channel_session, voice_state = bootstrap_voice_session(
        db,
        operator_id=operator_id,
        project_context_ids=project_ids,
    )
    db.commit()

    return VoiceSessionResponse(
        session_id=str(voice_state.id),
        channel_session_id=str(channel_session.id),
        status=voice_state.session_status,
    )


@router.get("/sessions/{session_id}")
def get_voice_session(
    session_id: str,
    db: Session = Depends(get_db),
) -> VoiceSessionDetailResponse:
    """Get the current state of a voice session."""
    import uuid

    voice_state = db.get(VoiceSessionState, uuid.UUID(session_id))
    if voice_state is None:
        raise HTTPException(status_code=404, detail="Voice session not found")

    state_data = voice_state.state_data or {}
    return VoiceSessionDetailResponse(
        session_id=str(voice_state.id),
        channel_session_id=str(voice_state.channel_session_id),
        status=voice_state.session_status,
        current_topic=state_data.get("current_topic"),
        utterance_count=state_data.get("utterance_count", 0),
        summary=voice_state.summary_content,
        referenced_project_ids=state_data.get("referenced_project_ids", []),
    )


@router.post("/sessions/{session_id}/utterances")
def submit_utterance(
    session_id: str,
    req: VoiceUtteranceRequest,
    db: Session = Depends(get_db),
) -> VoiceUtteranceResponse:
    """Submit a voice utterance for normalization and routing.

    TEST:Voice.Session.TranscriptBecomesStructuredSignal
    TEST:VoiceAndTelegram.SharedCoreFlowParityPreserved
    """
    import uuid

    voice_state = db.get(VoiceSessionState, uuid.UUID(session_id))
    if voice_state is None:
        raise HTTPException(status_code=404, detail="Voice session not found")

    if voice_state.session_status != "in_progress":
        raise HTTPException(status_code=400, detail="Session is not active")

    # WF2: Normalize utterance into ImportedSignal
    signal_ids = normalize_utterances(
        db,
        channel_session_id=voice_state.channel_session_id,
        transcript_segments=[{
            "text": req.text,
            "timestamp": req.timestamp,
            "metadata": req.metadata,
        }],
    )

    # WF3: Update continuity context
    update_session_context(
        db,
        voice_state_id=voice_state.id,
    )

    # Append transcript to the voice state
    existing_transcript = voice_state.transcript_content or ""
    voice_state.transcript_content = (
        f"{existing_transcript}\n{req.text}".strip()
        if existing_transcript
        else req.text
    )
    db.flush()

    # WF4: Route to shared core
    routing = route_voice_to_core(
        signal_ids=signal_ids,
        channel_session_id=voice_state.channel_session_id,
    )

    db.commit()

    return VoiceUtteranceResponse(
        signal_id=str(signal_ids[0]) if signal_ids else "",
        route_target=routing["route_target"],
        route_reason=routing["route_reason"],
        auto_send_blocked=routing["auto_send_blocked"],
    )


@router.post("/sessions/{session_id}/end")
def end_voice_session(
    session_id: str,
    db: Session = Depends(get_db),
) -> VoiceSessionResponse:
    """End a voice session, creating a summary.

    TEST:ChannelSession.SummariesPersistWithTraceableOrigin
    """
    import uuid

    voice_state = db.get(VoiceSessionState, uuid.UUID(session_id))
    if voice_state is None:
        raise HTTPException(status_code=404, detail="Voice session not found")

    voice_state = create_session_summary(db, voice_state_id=voice_state.id)
    db.commit()

    return VoiceSessionResponse(
        session_id=str(voice_state.id),
        channel_session_id=str(voice_state.channel_session_id),
        status=voice_state.session_status,
    )


@router.post("/sessions/{session_id}/briefing")
def request_spoken_briefing(
    session_id: str,
    db: Session = Depends(get_db),
) -> SpokenBriefingResponse:
    """Generate a spoken briefing for a voice session.

    TEST:Voice.Session.SpokenBriefingIsBoundedAndRelevant

    Uses the most recent focus pack to produce a listening-friendly
    briefing bounded in length and content. The briefing is persisted
    as a BriefingArtifact for traceability.
    """
    import uuid

    voice_state = db.get(VoiceSessionState, uuid.UUID(session_id))
    if voice_state is None:
        raise HTTPException(status_code=404, detail="Voice session not found")

    state_data = voice_state.state_data or {}
    project_ids = [
        uuid.UUID(pid)
        for pid in state_data.get("referenced_project_ids", [])
    ]

    result = generate_spoken_briefing(
        db,
        project_ids=project_ids if project_ids else None,
        channel_session_id=voice_state.channel_session_id,
    )
    db.commit()

    return SpokenBriefingResponse(
        briefing_text=result.briefing_text,
        briefing_artifact_id=str(result.briefing_artifact_id) if result.briefing_artifact_id else None,
        section_count=result.section_count,
        is_empty=result.is_empty,
        auto_send_blocked=True,  # Hard rule — always
    )


@router.get("/sessions/{session_id}/context")
def get_session_context_summary(
    session_id: str,
    db: Session = Depends(get_db),
) -> dict:
    """Get a spoken context summary for the current session state.

    TEST:Voice.Session.SpokenBriefingIsBoundedAndRelevant

    Quick "where are we?" response for voice sessions.
    """
    import uuid

    voice_state = db.get(VoiceSessionState, uuid.UUID(session_id))
    if voice_state is None:
        raise HTTPException(status_code=404, detail="Voice session not found")

    state_data = voice_state.state_data or {}

    context_text = generate_session_context_response(
        current_topic=state_data.get("current_topic"),
        utterance_count=state_data.get("utterance_count", 0),
        referenced_project_ids=state_data.get("referenced_project_ids", []),
        unresolved_prompts=state_data.get("unresolved_prompts", []),
    )

    return {
        "context_text": context_text,
        "session_id": session_id,
        "auto_send_blocked": True,
    }


@router.post("/sessions/{session_id}/handoff")
def create_voice_handoff(
    session_id: str,
    db: Session = Depends(get_db),
) -> dict:
    """Create a workspace-visible handoff from a voice session.

    TEST:Voice.Session.HandoffCreatesWorkspaceVisibleContinuation

    Persists a handoff artifact so the operator can continue
    in the main workspace with context preserved.
    """
    import uuid

    voice_state = db.get(VoiceSessionState, uuid.UUID(session_id))
    if voice_state is None:
        raise HTTPException(status_code=404, detail="Voice session not found")

    state_data = voice_state.state_data or {}

    handoff = create_handoff_from_voice(
        db,
        channel_session_id=voice_state.channel_session_id,
        reason="Voice session handoff to workspace",
        current_topic=state_data.get("current_topic"),
        unresolved_prompts=state_data.get("unresolved_prompts", []),
        referenced_project_ids=state_data.get("referenced_project_ids", []),
    )
    db.commit()

    return handoff.to_dict()

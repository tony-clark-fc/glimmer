"""Voice session services — transcript normalization, continuity, routing.

ARCH:VoiceInteractionArchitecture
ARCH:VoiceSessionGraph
ARCH:VoiceToStructuredOutputPath

Services for voice session lifecycle. These are called by graph nodes
and API handlers. They are the testable business-logic layer.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.channel import ChannelSession, VoiceSessionState
from app.models.source import ImportedSignal


def _genuuid() -> uuid.UUID:
    return uuid.uuid4()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ── WF1: Session bootstrap ───────────────────────────────────────


def bootstrap_voice_session(
    db: Session,
    *,
    operator_id: uuid.UUID | None = None,
    project_context_ids: list[uuid.UUID] | None = None,
) -> tuple[ChannelSession, VoiceSessionState]:
    """Create a ChannelSession + VoiceSessionState for a new voice interaction.

    TEST:Voice.Session.BootstrapBindsCorrectOperatorAndSession

    Returns the (channel_session, voice_state) pair.
    """
    channel_session = ChannelSession(
        operator_id=operator_id,
        channel_type="voice",
        channel_identity=f"voice_{uuid.uuid4().hex[:12]}",
        session_state="active",
        last_interaction_at=_utcnow(),
        session_metadata={
            "project_context_ids": [str(p) for p in (project_context_ids or [])],
        },
    )
    db.add(channel_session)
    db.flush()

    voice_state = VoiceSessionState(
        channel_session_id=channel_session.id,
        session_status="in_progress",
        state_data={
            "referenced_project_ids": [str(p) for p in (project_context_ids or [])],
            "current_topic": None,
            "unresolved_prompts": [],
            "utterance_count": 0,
        },
    )
    db.add(voice_state)
    db.flush()

    return channel_session, voice_state


# ── WF2: Transcript normalization ────────────────────────────────


def normalize_utterances(
    db: Session,
    *,
    channel_session_id: uuid.UUID,
    transcript_segments: list[dict],
) -> list[uuid.UUID]:
    """Convert voice transcript segments into ImportedSignal records.

    TEST:Voice.Session.TranscriptBecomesStructuredSignal

    Each segment becomes an ImportedSignal with signal_type="voice_transcript"
    and provenance metadata linking back to the channel session.

    Segments: [{text: str, timestamp?: str, index?: int, metadata?: dict}]
    Returns list of ImportedSignal IDs.
    """
    signal_ids: list[uuid.UUID] = []

    for i, segment in enumerate(transcript_segments):
        text = segment.get("text", "").strip()
        if not text:
            continue

        signal = ImportedSignal(
            signal_type="voice_transcript",
            source_label=f"voice_session:{channel_session_id}",
            content=text,
            raw_metadata={
                "channel_session_id": str(channel_session_id),
                "utterance_index": segment.get("index", i),
                "timestamp": segment.get("timestamp"),
                "segment_metadata": segment.get("metadata"),
            },
        )
        db.add(signal)
        db.flush()
        signal_ids.append(signal.id)

    return signal_ids


# ── WF3: Session continuity ──────────────────────────────────────

# Maximum number of recent topics to retain for bounded continuity
MAX_RECENT_TOPICS = 5
MAX_UNRESOLVED_PROMPTS = 10


def update_session_context(
    db: Session,
    *,
    voice_state_id: uuid.UUID,
    current_topic: str | None = None,
    referenced_project_ids: list[uuid.UUID] | None = None,
    unresolved_prompts: list[str] | None = None,
    summary_content: str | None = None,
) -> VoiceSessionState:
    """Update the voice session state with bounded continuity context.

    TEST:Voice.Session.ContinuityPreservedWithinSession

    Continuity is bounded — topic history is capped, prompts are capped,
    and referenced projects are a set, not an unbounded list.
    """
    voice_state = db.get(VoiceSessionState, voice_state_id)
    if voice_state is None:
        raise ValueError(f"VoiceSessionState {voice_state_id} not found")

    state_data = dict(voice_state.state_data or {})

    if current_topic is not None:
        state_data["current_topic"] = current_topic
        # Maintain bounded recent topics list
        recent_topics = state_data.get("recent_topics", [])
        recent_topics.append(current_topic)
        state_data["recent_topics"] = recent_topics[-MAX_RECENT_TOPICS:]

    if referenced_project_ids is not None:
        # Merge, don't replace — but keep as a set
        existing = set(state_data.get("referenced_project_ids", []))
        existing.update(str(p) for p in referenced_project_ids)
        state_data["referenced_project_ids"] = sorted(existing)

    if unresolved_prompts is not None:
        state_data["unresolved_prompts"] = unresolved_prompts[:MAX_UNRESOLVED_PROMPTS]

    utterance_count = state_data.get("utterance_count", 0) + 1
    state_data["utterance_count"] = utterance_count

    voice_state.state_data = state_data
    if summary_content is not None:
        voice_state.summary_content = summary_content

    db.flush()
    return voice_state


def create_session_summary(
    db: Session,
    *,
    voice_state_id: uuid.UUID,
) -> VoiceSessionState:
    """Generate a session summary and mark the session as completed.

    TEST:ChannelSession.SummariesPersistWithTraceableOrigin
    """
    voice_state = db.get(VoiceSessionState, voice_state_id)
    if voice_state is None:
        raise ValueError(f"VoiceSessionState {voice_state_id} not found")

    state_data = dict(voice_state.state_data or {})

    # Build a deterministic summary from session state
    topic = state_data.get("current_topic", "general")
    utterance_count = state_data.get("utterance_count", 0)
    project_ids = state_data.get("referenced_project_ids", [])
    unresolved = state_data.get("unresolved_prompts", [])

    summary_parts = [f"Voice session covering topic: {topic}."]
    summary_parts.append(f"Utterances processed: {utterance_count}.")
    if project_ids:
        summary_parts.append(f"Referenced {len(project_ids)} project(s).")
    if unresolved:
        summary_parts.append(
            f"Unresolved prompts remaining: {len(unresolved)}."
        )

    voice_state.summary_content = " ".join(summary_parts)
    voice_state.session_status = "completed"
    voice_state.ended_at = _utcnow()
    db.flush()

    # Also update the parent channel session
    channel_session = db.get(ChannelSession, voice_state.channel_session_id)
    if channel_session:
        channel_session.session_state = "completed"
        channel_session.last_interaction_at = _utcnow()
        db.flush()

    return voice_state


# ── WF4: Voice-to-core routing ───────────────────────────────────


def route_voice_to_core(
    *,
    signal_ids: list[uuid.UUID],
    channel_session_id: uuid.UUID,
) -> dict:
    """Route voice-derived signals into the shared IntakeGraph.

    TEST:VoiceAndTelegram.SharedCoreFlowParityPreserved
    TEST:Voice.Session.ReviewGatePreservedForMeaningfulActions

    Constructs an IntakeState and invokes the compiled IntakeGraph.
    Returns the routing result as a dict.
    """
    from app.graphs.intake import get_intake_graph

    compiled = get_intake_graph()

    intake_state = {
        "source_record_ids": signal_ids,
        "record_type": "imported_signal",
        "provider_type": "voice",
        "channel": "voice",
        "workflow_id": str(uuid.uuid4()),
        "initiated_at": _utcnow().isoformat(),
    }

    result = compiled.invoke(intake_state)
    return {
        "route_target": result.get("route_target", "triage"),
        "route_reason": result.get("route_reason", "Voice signal routed to triage"),
        "workflow_id": result.get("workflow_id", ""),
        "needs_review": False,  # Determined by downstream triage
        "auto_send_blocked": True,  # Hard rule — always
    }



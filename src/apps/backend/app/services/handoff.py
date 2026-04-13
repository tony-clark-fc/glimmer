"""Cross-surface handoff service — workspace-visible continuation.

ARCH:ChannelHandoffUx
ARCH:CrossSurfaceContinuity
ARCH:ReviewGateArchitecture
REQ:StateContinuity
REQ:HumanApprovalBoundaries

Creates workspace-visible continuation records when voice or Telegram
sessions need to hand off to the main workspace for richer review.

WF7 — Cross-surface handoff into the workspace.
WF8 — Approval and safety parity across channels.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.channel import ChannelSession
from app.models.drafting import BriefingArtifact


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ── Handoff Record ───────────────────────────────────────────────────


class HandoffRecord:
    """A cross-surface handoff from a companion channel into the workspace.

    TEST:Voice.Session.HandoffCreatesWorkspaceVisibleContinuation

    Not a database model (yet) — stored as a BriefingArtifact with
    briefing_type="channel_handoff" for traceability.
    """

    def __init__(
        self,
        handoff_id: uuid.UUID,
        source_channel: str,
        channel_session_id: uuid.UUID,
        reason: str,
        context_summary: str,
        pending_items: list[str],
        workspace_target: str,
        auto_send_blocked: bool = True,
    ):
        self.handoff_id = handoff_id
        self.source_channel = source_channel
        self.channel_session_id = channel_session_id
        self.reason = reason
        self.context_summary = context_summary
        self.pending_items = pending_items
        self.workspace_target = workspace_target
        self.auto_send_blocked = auto_send_blocked

    def to_dict(self) -> dict:
        return {
            "handoff_id": str(self.handoff_id),
            "source_channel": self.source_channel,
            "channel_session_id": str(self.channel_session_id),
            "reason": self.reason,
            "context_summary": self.context_summary,
            "pending_items": self.pending_items,
            "workspace_target": self.workspace_target,
            "auto_send_blocked": self.auto_send_blocked,
        }


# ── Handoff Creation ─────────────────────────────────────────────────


def create_handoff_from_voice(
    db: Session,
    *,
    channel_session_id: uuid.UUID,
    reason: str,
    current_topic: str | None = None,
    unresolved_prompts: list[str] | None = None,
    referenced_project_ids: list[str] | None = None,
) -> HandoffRecord:
    """Create a workspace-visible handoff from a voice session.

    TEST:Voice.Session.HandoffCreatesWorkspaceVisibleContinuation

    Persists a BriefingArtifact(briefing_type="channel_handoff") so the
    handoff is traceable and visible in the main workspace.
    """
    context_parts = []
    if current_topic:
        context_parts.append(f"Topic: {current_topic}")
    if referenced_project_ids:
        context_parts.append(f"Projects referenced: {len(referenced_project_ids)}")
    context_summary = ". ".join(context_parts) if context_parts else "Voice session handoff"

    pending = list(unresolved_prompts or [])

    # Persist as BriefingArtifact for workspace visibility
    artifact = BriefingArtifact(
        briefing_type="channel_handoff",
        content=f"Handoff from voice: {reason}. {context_summary}",
        source_scope_metadata={
            "source_channel": "voice",
            "channel_session_id": str(channel_session_id),
            "reason": reason,
            "current_topic": current_topic,
            "unresolved_prompts": pending,
            "referenced_project_ids": referenced_project_ids or [],
        },
    )
    db.add(artifact)
    db.flush()

    # Update channel session to reflect handoff
    channel_session = db.get(ChannelSession, channel_session_id)
    if channel_session:
        channel_session.session_metadata = {
            **(channel_session.session_metadata or {}),
            "handoff_created": True,
            "handoff_artifact_id": str(artifact.id),
            "handoff_reason": reason,
        }
        db.flush()

    return HandoffRecord(
        handoff_id=artifact.id,
        source_channel="voice",
        channel_session_id=channel_session_id,
        reason=reason,
        context_summary=context_summary,
        pending_items=pending,
        workspace_target="/review",
        auto_send_blocked=True,
    )


def create_handoff_from_telegram(
    db: Session,
    *,
    channel_session_id: uuid.UUID,
    telegram_chat_id: str,
    reason: str,
    current_topic: str | None = None,
    message_count: int = 0,
) -> HandoffRecord:
    """Create a workspace-visible handoff from a Telegram session.

    TEST:Telegram.Companion.HandoffToWorkspaceOccursWhenNeeded

    Persists a BriefingArtifact(briefing_type="channel_handoff") for
    workspace visibility.
    """
    context_parts = []
    if current_topic:
        context_parts.append(f"Topic: {current_topic}")
    if message_count > 0:
        context_parts.append(f"{message_count} messages in session")
    context_summary = ". ".join(context_parts) if context_parts else "Telegram session handoff"

    artifact = BriefingArtifact(
        briefing_type="channel_handoff",
        content=f"Handoff from Telegram ({telegram_chat_id}): {reason}. {context_summary}",
        source_scope_metadata={
            "source_channel": "telegram",
            "channel_session_id": str(channel_session_id),
            "telegram_chat_id": telegram_chat_id,
            "reason": reason,
            "current_topic": current_topic,
            "message_count": message_count,
        },
    )
    db.add(artifact)
    db.flush()

    # Update channel session
    channel_session = db.get(ChannelSession, channel_session_id)
    if channel_session:
        channel_session.session_metadata = {
            **(channel_session.session_metadata or {}),
            "handoff_created": True,
            "handoff_artifact_id": str(artifact.id),
            "handoff_reason": reason,
        }
        db.flush()

    return HandoffRecord(
        handoff_id=artifact.id,
        source_channel="telegram",
        channel_session_id=channel_session_id,
        reason=reason,
        context_summary=context_summary,
        pending_items=[],
        workspace_target="/review",
        auto_send_blocked=True,
    )


# ── Handoff Retrieval ────────────────────────────────────────────────


def get_pending_handoffs(db: Session) -> list[HandoffRecord]:
    """Retrieve all pending handoff records (BriefingArtifacts of type channel_handoff).

    TEST:Telegram.Companion.ReviewNeededStateSurfacesInWorkspace

    Returns handoff records that are visible in the workspace review surface.
    """
    artifacts = db.execute(
        select(BriefingArtifact)
        .where(BriefingArtifact.briefing_type == "channel_handoff")
        .order_by(BriefingArtifact.created_at.desc())
    ).scalars().all()

    records = []
    for a in artifacts:
        meta = a.source_scope_metadata or {}
        records.append(HandoffRecord(
            handoff_id=a.id,
            source_channel=meta.get("source_channel", "unknown"),
            channel_session_id=uuid.UUID(meta["channel_session_id"]) if meta.get("channel_session_id") else uuid.uuid4(),
            reason=meta.get("reason", ""),
            context_summary=a.content,
            pending_items=meta.get("unresolved_prompts", []),
            workspace_target="/review",
            auto_send_blocked=True,
        ))
    return records


# ── Safety Parity Checks ────────────────────────────────────────────


def verify_auto_send_blocked(routing_result: dict) -> bool:
    """Verify that auto_send_blocked is True in any routing result.

    TEST:Security.NoAutoSend.GlobalBoundaryPreserved

    This is a safety assertion — it should never return False in the MVP.
    """
    return routing_result.get("auto_send_blocked", False) is True


def verify_review_gate_preserved(
    *,
    needs_review: bool,
    has_review_path: bool,
) -> bool:
    """Verify that review gates are preserved across channels.

    TEST:Security.ReviewGate.ExternalImpactRequiresApproval

    If review is needed, there must be a path to review.
    """
    if needs_review and not has_review_path:
        return False
    return True


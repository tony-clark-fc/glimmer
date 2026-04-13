"""Drafting handoff service — creates reviewable drafts from assistant core.

ARCH:DraftingGraph
ARCH:DraftingGraphNoAutoSend
ARCH:NoAutoSendPolicy

This service creates Draft artifacts from triage/planner context.
Drafts are ALWAYS reviewable — auto_send is always blocked.

Draft creation is allowed. Autonomous sending is NOT.
"""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.models.drafting import Draft, DraftVariant
from app.models.audit import AuditRecord


# ── Drafting Result ──────────────────────────────────────────────────


class DraftingResult:
    """Result of draft creation — always review-required."""

    def __init__(
        self,
        draft_id: uuid.UUID,
        variant_ids: list[uuid.UUID],
        auto_send_blocked: bool,
        review_required: bool,
    ):
        self.draft_id = draft_id
        self.variant_ids = variant_ids
        # Hard invariants — these must ALWAYS be True
        self.auto_send_blocked = auto_send_blocked
        self.review_required = review_required


# ── Auto-Send Guard ──────────────────────────────────────────────────


AUTO_SEND_BLOCKED = True  # Hard constant — never set to False

NO_AUTO_SEND_ASSERTION = (
    "Glimmer drafting service enforces no-auto-send boundary. "
    "Drafts are always review-required."
)


# ── Draft Creation ───────────────────────────────────────────────────


def create_draft(
    session: Session,
    body_content: str,
    intent: str = "reply",
    source_message_id: Optional[uuid.UUID] = None,
    source_record_type: Optional[str] = None,
    project_id: Optional[uuid.UUID] = None,
    stakeholder_ids: Optional[list[uuid.UUID]] = None,
    channel_type: Optional[str] = None,
    tone_mode: Optional[str] = None,
    rationale_summary: Optional[str] = None,
    variants: Optional[list[dict]] = None,
) -> DraftingResult:
    """Create a reviewable draft artifact.

    ARCH:DraftingGraphNoAutoSend — auto_send is ALWAYS blocked.
    ARCH:ReviewGateArchitecture — drafts are ALWAYS review-required.

    The draft starts in 'draft' status and must be explicitly
    reviewed by the operator before any external action.
    """
    assert AUTO_SEND_BLOCKED, NO_AUTO_SEND_ASSERTION

    draft = Draft(
        source_message_id=source_message_id,
        source_record_type=source_record_type,
        linked_project_id=project_id,
        linked_stakeholder_ids=(
            {"stakeholder_ids": [str(sid) for sid in stakeholder_ids]}
            if stakeholder_ids
            else None
        ),
        channel_type=channel_type or "email",
        tone_mode=tone_mode or "concise",
        body_content=body_content,
        rationale_summary=rationale_summary,
        status="draft",  # Never starts as 'sent'
        intent_label=intent,
    )
    session.add(draft)
    session.flush()

    variant_ids: list[uuid.UUID] = []
    if variants:
        for v in variants:
            variant = DraftVariant(
                draft_id=draft.id,
                variant_label=v.get("label", "alternate"),
                body_content=v.get("body_content", ""),
            )
            session.add(variant)
            session.flush()
            variant_ids.append(variant.id)

    # Audit the draft creation
    audit = AuditRecord(
        entity_type="draft",
        entity_id=draft.id,
        action="created",
        actor="system",
        change_summary=f"Draft created with intent '{intent}' — review required",
        new_state={
            "draft_id": str(draft.id),
            "status": "draft",
            "auto_send_blocked": True,
            "intent": intent,
        },
    )
    session.add(audit)
    session.flush()

    return DraftingResult(
        draft_id=draft.id,
        variant_ids=variant_ids,
        auto_send_blocked=AUTO_SEND_BLOCKED,
        review_required=True,
    )


def has_send_capability() -> bool:
    """Check if the drafting service has send capability.

    ARCH:NoAutoSendPolicy — always returns False.
    This is a hard product boundary, not a feature toggle.
    """
    return False



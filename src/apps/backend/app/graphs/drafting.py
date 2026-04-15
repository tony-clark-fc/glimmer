"""Drafting handoff service — creates reviewable drafts from assistant core.

ARCH:DraftingGraph
ARCH:DraftingGraphNoAutoSend
ARCH:NoAutoSendPolicy
PLAN:WorkstreamI.PackageI8.OrchestrationWiring

This service creates Draft artifacts from triage/planner context.
Drafts are ALWAYS reviewable — auto_send is always blocked.

Draft creation is allowed. Autonomous sending is NOT.

When the LLM is available and enabled, create_draft_enhanced() can
generate body_content from context when the caller does not provide
pre-written content.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.models.drafting import Draft, DraftVariant
from app.models.audit import AuditRecord

logger = logging.getLogger(__name__)


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


# ── LLM-Enhanced Draft Creation ──────────────────────────────────────


def create_draft_enhanced(
    session: Session,
    *,
    body_content: str = "",
    intent: str = "reply",
    source_message_id: Optional[uuid.UUID] = None,
    source_record_type: Optional[str] = None,
    project_id: Optional[uuid.UUID] = None,
    stakeholder_ids: Optional[list[uuid.UUID]] = None,
    channel_type: Optional[str] = None,
    tone_mode: Optional[str] = None,
    rationale_summary: Optional[str] = None,
    variants: Optional[list[dict]] = None,
    context_summary: Optional[str] = None,
    original_message_summary: Optional[str] = None,
    project_name: Optional[str] = None,
    stakeholder_names: Optional[list[str]] = None,
    key_points: Optional[list[str]] = None,
) -> DraftingResult:
    """Create a draft, using LLM to generate body_content when not provided.

    PLAN:WorkstreamI.PackageI8.OrchestrationWiring
    ARCH:DraftingGraphNoAutoSend — auto_send is ALWAYS blocked.
    TEST:LLM.Drafting.GeneratesContextualDraft

    If body_content is empty/blank and LLM drafting is enabled, uses the
    LLM to generate the draft body from the provided context.  Falls
    back to empty body_content on LLM failure (caller sees the empty
    body and can act accordingly).

    The no-auto-send boundary is preserved regardless of which path
    generates the body_content.
    """
    if not body_content.strip():
        body_content = _try_llm_draft(
            intent=intent,
            channel_type=channel_type or "email",
            tone_mode=tone_mode or "concise",
            context_summary=context_summary,
            original_message_summary=original_message_summary,
            project_name=project_name,
            stakeholder_names=stakeholder_names,
            key_points=key_points,
        ) or ""
        if body_content:
            # LLM also generates a rationale when it produces the body
            rationale_summary = rationale_summary or "Draft body generated by LLM"

    return create_draft(
        session,
        body_content=body_content,
        intent=intent,
        source_message_id=source_message_id,
        source_record_type=source_record_type,
        project_id=project_id,
        stakeholder_ids=stakeholder_ids,
        channel_type=channel_type,
        tone_mode=tone_mode,
        rationale_summary=rationale_summary,
        variants=variants,
    )


def _try_llm_draft(
    *,
    intent: str,
    channel_type: str,
    tone_mode: str,
    context_summary: Optional[str],
    original_message_summary: Optional[str],
    project_name: Optional[str],
    stakeholder_names: Optional[list[str]],
    key_points: Optional[list[str]],
) -> Optional[str]:
    """Attempt LLM draft generation.  Returns body text or None."""
    from app.inference.config import InferenceSettings

    settings = InferenceSettings()
    if not settings.llm_drafting_enabled:
        return None

    try:
        from app.inference.orchestration import generate_draft_smart

        result = asyncio.run(generate_draft_smart(
            intent=intent,
            channel_type=channel_type,
            tone_mode=tone_mode,
            context_summary=context_summary,
            original_message_summary=original_message_summary,
            project_name=project_name,
            stakeholder_names=stakeholder_names,
            key_points=key_points,
        ))

        # Hard safety check — must never bypass no-auto-send
        assert result.auto_send_blocked is True, NO_AUTO_SEND_ASSERTION

        if result.used_llm and result.body_content:
            logger.info(
                "Draft body generated by LLM (%d chars, tone=%s)",
                len(result.body_content),
                tone_mode,
            )
            return result.body_content

        return None

    except Exception as exc:
        logger.info("LLM draft generation skipped: %s", exc)
        return None



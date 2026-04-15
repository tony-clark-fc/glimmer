"""Persona asset API — context-aware selection, mood, and conversation sessions.

ARCH:VisualPersonaSelection
ARCH:VisualPersonaRenderingRules
ARCH:PersonaPage.ConversationModel
ARCH:PersonaPageSessionModel
REQ:VisualPersonaSupport
REQ:ContextAwareVisualPresentation
REQ:GlimmerPersonaPage

Serves managed persona assets for frontend rendering.
Selection is driven by classification labels and interaction context.
Falls back to the default asset if no specific match exists.
Mood endpoint derives Glimmer's emotional state from portfolio health.
Conversation session endpoints manage persona-page chat lifecycle.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models.persona import PersonaAsset, PersonaClassification
from app.models.portfolio import Project, Milestone
from app.models.execution import WorkItem, BlockerRecord, RiskRecord, DecisionRecord
from app.models.channel import ChannelSession, PersonaPageSession, PersonaPageMessage, MindMapWorkingState
from app.models.stakeholder import Stakeholder

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/persona", tags=["persona"])


# ── Response contracts ────────────────────────────────────────────

class PersonaClassificationResponse(BaseModel):
    classification_type: str
    classification_value: str


class PersonaAssetResponse(BaseModel):
    id: str
    label: str
    asset_path: str
    asset_type: str
    is_default: bool
    classifications: list[PersonaClassificationResponse]


class PersonaSelectionResponse(BaseModel):
    """Response for context-aware persona selection."""
    asset: PersonaAssetResponse | None
    selection_reason: str
    fallback_used: bool


class GlimmerMoodResponse(BaseModel):
    """Glimmer's current mood based on portfolio health."""
    mood: str  # bau, happy, grumpy, thinking, worried
    reason: str
    portfolio_health: dict


# ── Selection logic ───────────────────────────────────────────────

# Mapping from interaction context to classification suitability values
CONTEXT_SUITABILITY_MAP: dict[str, list[str]] = {
    "briefing": ["briefing", "focused", "executive"],
    "today": ["briefing", "focused", "executive"],
    "drafting": ["drafting", "professional", "warm"],
    "draft": ["drafting", "professional", "warm"],
    "voice": ["supportive", "warm", "conversational"],
    "triage": ["focused", "executive"],
    "review": ["focused", "professional"],
}


def _select_persona_for_context(
    db: Session,
    context: str | None,
) -> tuple[PersonaAsset | None, str, bool]:
    """Select a persona asset for the given interaction context.

    Returns (asset, reason, fallback_used).
    """
    # If context is provided, try to find a matching active asset
    if context:
        suitability_values = CONTEXT_SUITABILITY_MAP.get(context, [])
        if suitability_values:
            stmt = (
                select(PersonaAsset)
                .join(PersonaAsset.classifications)
                .where(
                    PersonaAsset.is_active == True,  # noqa: E712
                    PersonaClassification.classification_value.in_(
                        suitability_values
                    ),
                )
                .options(selectinload(PersonaAsset.classifications))
                .limit(1)
            )
            asset = db.execute(stmt).scalar_one_or_none()
            if asset is not None:
                return (
                    asset,
                    f"Selected for context '{context}' based on classification match",
                    False,
                )

    # Fall back to default active asset
    default_stmt = (
        select(PersonaAsset)
        .where(
            PersonaAsset.is_active == True,  # noqa: E712
            PersonaAsset.is_default == True,  # noqa: E712
        )
        .options(selectinload(PersonaAsset.classifications))
        .limit(1)
    )
    default_asset = db.execute(default_stmt).scalar_one_or_none()
    if default_asset is not None:
        reason = (
            f"Fallback to default — no context-specific match for '{context}'"
            if context
            else "Default persona asset (no context specified)"
        )
        return (default_asset, reason, True)

    # No active assets at all — fall back to any active asset
    any_stmt = (
        select(PersonaAsset)
        .where(PersonaAsset.is_active == True)  # noqa: E712
        .options(selectinload(PersonaAsset.classifications))
        .limit(1)
    )
    any_asset = db.execute(any_stmt).scalar_one_or_none()
    if any_asset is not None:
        return (any_asset, "Fallback to first active asset — no default configured", True)

    return (None, "No active persona assets available", True)


def _asset_to_response(asset: PersonaAsset) -> PersonaAssetResponse:
    return PersonaAssetResponse(
        id=str(asset.id),
        label=asset.label,
        asset_path=asset.asset_path,
        asset_type=asset.asset_type,
        is_default=asset.is_default,
        classifications=[
            PersonaClassificationResponse(
                classification_type=c.classification_type,
                classification_value=c.classification_value,
            )
            for c in asset.classifications
        ],
    )


# ── Routes ────────────────────────────────────────────────────────

@router.get("/select")
def select_persona(
    context: Optional[str] = None,
    db: Session = Depends(get_db),
) -> PersonaSelectionResponse:
    """Select a persona asset for a given interaction context.

    If no context is provided, returns the default persona.
    If no matching persona exists, falls back to default, then any active asset.
    If no active assets exist at all, returns asset=null.
    """
    asset, reason, fallback_used = _select_persona_for_context(db, context)
    return PersonaSelectionResponse(
        asset=_asset_to_response(asset) if asset else None,
        selection_reason=reason,
        fallback_used=fallback_used,
    )


@router.get("/assets")
def list_persona_assets(
    db: Session = Depends(get_db),
) -> list[PersonaAssetResponse]:
    """List all active persona assets."""
    stmt = (
        select(PersonaAsset)
        .where(PersonaAsset.is_active == True)  # noqa: E712
        .options(selectinload(PersonaAsset.classifications))
        .order_by(PersonaAsset.label)
    )
    assets = db.execute(stmt).scalars().all()
    return [_asset_to_response(a) for a in assets]


# ── Mood determination ────────────────────────────────────────────

MOOD_IMAGE_COUNTS: dict[str, int] = {
    "bau": 9,       # 00-08
    "grumpy": 3,     # 00-02
    "happy": 3,      # 00-02
    "thinking": 3,   # 00-02
    "worried": 4,    # 00-03
}


def _determine_mood(db: Session) -> tuple[str, str, dict]:
    """Derive Glimmer's mood from portfolio health signals.

    Returns (mood, reason, health_dict).
    """
    project_count = db.execute(
        select(func.count()).select_from(Project).where(
            Project.archived == False,  # noqa: E712
        )
    ).scalar() or 0

    blocker_count = db.execute(
        select(func.count()).select_from(BlockerRecord).where(
            BlockerRecord.status == "active",
        )
    ).scalar() or 0

    overdue_count = 0
    try:
        overdue_count = db.execute(
            select(func.count()).select_from(WorkItem).where(
                WorkItem.status.in_(["open", "in_progress"]),
                WorkItem.due_date < datetime.now(timezone.utc),
            )
        ).scalar() or 0
    except Exception:
        pass

    risk_count = 0
    try:
        risk_count = db.execute(
            select(func.count()).select_from(RiskRecord).where(
                RiskRecord.severity_signal == "high",
                RiskRecord.status == "active",
            )
        ).scalar() or 0
    except Exception:
        pass

    health = {
        "active_projects": project_count,
        "active_blockers": blocker_count,
        "overdue_items": overdue_count,
        "high_risks": risk_count,
    }

    # Mood rules
    if blocker_count == 0 and overdue_count == 0 and risk_count == 0 and project_count > 0:
        return "happy", "All clear — no blockers, no overdue items, no high risks", health
    if risk_count >= 3 or (blocker_count >= 3 and overdue_count >= 3):
        return "worried", f"{risk_count} high risks, {blocker_count} blockers, {overdue_count} overdue", health
    if overdue_count >= 3:
        return "grumpy", f"{overdue_count} overdue items need attention", health
    if blocker_count >= 2 or risk_count >= 1:
        return "worried", f"{blocker_count} active blockers, {risk_count} high risks", health

    return "bau", "Business as usual — things are ticking along", health


@router.get("/mood")
def get_mood(
    db: Session = Depends(get_db),
) -> GlimmerMoodResponse:
    """Get Glimmer's current mood based on portfolio health.

    REQ:GlimmerPersonaPage — mood determines which avatar image set to use.
    """
    mood, reason, health = _determine_mood(db)
    return GlimmerMoodResponse(
        mood=mood,
        reason=reason,
        portfolio_health=health,
    )


# ── Conversation session contracts ────────────────────────────────

class PersonaMessageResponse(BaseModel):
    """A single conversation message."""
    id: str
    role: str
    content: str
    ordering: int
    workspace_mode: str | None
    inference_metadata: dict | None
    created_at: str


class PersonaSessionResponse(BaseModel):
    """A persona-page conversation session."""
    id: str
    session_status: str
    workspace_mode: str | None
    summary_intent: str | None
    created_at: str
    updated_at: str
    messages: list[PersonaMessageResponse]


class CreateSessionRequest(BaseModel):
    """Request to create a new persona-page session."""
    workspace_mode: str | None = "update"


class SendMessageRequest(BaseModel):
    """Request to send a message in a persona-page session."""
    content: str
    workspace_mode: str | None = None


class UpdateSessionRequest(BaseModel):
    """Request to update session status."""
    session_status: str  # paused, confirmed, abandoned


# ── Conversation session helpers ──────────────────────────────────

VALID_SESSION_STATUSES = {"active", "paused", "confirmed", "abandoned"}
VALID_TRANSITIONS = {
    "active": {"paused", "confirmed", "abandoned"},
    "paused": {"active", "abandoned"},
    # confirmed and abandoned are terminal
}


def _message_to_response(msg: PersonaPageMessage) -> PersonaMessageResponse:
    return PersonaMessageResponse(
        id=str(msg.id),
        role=msg.role,
        content=msg.content,
        ordering=msg.ordering,
        workspace_mode=msg.workspace_mode,
        inference_metadata=msg.inference_metadata,
        created_at=msg.created_at.isoformat() if msg.created_at else "",
    )


def _session_to_response(session: PersonaPageSession) -> PersonaSessionResponse:
    return PersonaSessionResponse(
        id=str(session.id),
        session_status=session.session_status,
        workspace_mode=session.workspace_mode,
        summary_intent=session.summary_intent,
        created_at=session.created_at.isoformat() if session.created_at else "",
        updated_at=session.updated_at.isoformat() if session.updated_at else "",
        messages=[_message_to_response(m) for m in session.messages],
    )


def _get_project_summaries(db: Session) -> list[dict]:
    """Get active project summaries for LLM context."""
    projects = db.execute(
        select(Project).where(
            Project.archived == False,  # noqa: E712
            Project.status != "archived",
        )
    ).scalars().all()
    return [
        {
            "id": str(p.id),
            "name": p.name,
            "objective": p.objective or "",
            "short_summary": p.short_summary or "",
        }
        for p in projects
    ]


def _get_portfolio_health(db: Session) -> dict:
    """Get portfolio health snapshot for LLM context."""
    project_count = db.execute(
        select(func.count()).select_from(Project).where(
            Project.archived == False,  # noqa: E712
        )
    ).scalar() or 0

    blocker_count = db.execute(
        select(func.count()).select_from(BlockerRecord).where(
            BlockerRecord.status == "active",
        )
    ).scalar() or 0

    overdue_count = 0
    try:
        overdue_count = db.execute(
            select(func.count()).select_from(WorkItem).where(
                WorkItem.status.in_(["open", "in_progress"]),
                WorkItem.due_date < datetime.now(timezone.utc),
            )
        ).scalar() or 0
    except Exception:
        pass

    return {
        "active_projects": project_count,
        "active_blockers": blocker_count,
        "overdue_items": overdue_count,
    }


# ── Conversation session routes ───────────────────────────────────

@router.post("/sessions", response_model=PersonaSessionResponse, status_code=201)
def create_session(
    request: CreateSessionRequest,
    db: Session = Depends(get_db),
) -> PersonaSessionResponse:
    """Create a new persona-page conversation session.

    ARCH:PersonaPageSessionModel — creates ChannelSession + PersonaPageSession pair.
    """
    channel_session = ChannelSession(
        channel_type="web",
        session_state="active",
        last_interaction_at=datetime.now(timezone.utc),
    )
    db.add(channel_session)
    db.flush()

    persona_session = PersonaPageSession(
        channel_session_id=channel_session.id,
        session_status="active",
        workspace_mode=request.workspace_mode,
    )
    db.add(persona_session)
    db.commit()
    db.refresh(persona_session)

    return _session_to_response(persona_session)


@router.get("/sessions/{session_id}", response_model=PersonaSessionResponse)
def get_session(
    session_id: str,
    db: Session = Depends(get_db),
) -> PersonaSessionResponse:
    """Get a persona-page session with its message history."""
    import uuid as _uuid
    try:
        sid = _uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found")

    session = db.execute(
        select(PersonaPageSession)
        .where(PersonaPageSession.id == sid)
        .options(selectinload(PersonaPageSession.messages))
    ).scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return _session_to_response(session)


@router.post("/sessions/{session_id}/messages", response_model=PersonaMessageResponse)
async def send_message(
    session_id: str,
    request: SendMessageRequest,
    db: Session = Depends(get_db),
) -> PersonaMessageResponse:
    """Send a message in a persona-page session and get Glimmer's reply.

    ARCH:PersonaPage.ConversationModel
    ARCH:PersonaPage.OrchestrationRelationship

    Persists the operator's message, calls the LLM, persists and returns Glimmer's reply.
    """
    import uuid as _uuid
    try:
        sid = _uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found")

    session = db.execute(
        select(PersonaPageSession)
        .where(PersonaPageSession.id == sid)
        .options(selectinload(PersonaPageSession.messages))
    ).scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.session_status not in ("active", "paused"):
        raise HTTPException(
            status_code=409,
            detail=f"Session is {session.session_status} — cannot send messages",
        )

    # Re-activate paused session
    if session.session_status == "paused":
        session.session_status = "active"

    content = request.content.strip()
    if not content:
        raise HTTPException(status_code=422, detail="Message content cannot be empty")

    workspace_mode = request.workspace_mode or session.workspace_mode or "update"
    if request.workspace_mode:
        session.workspace_mode = request.workspace_mode

    # Determine ordering
    next_order = len(session.messages) + 1

    # Persist user message
    user_msg = PersonaPageMessage(
        session_id=session.id,
        role="user",
        content=content,
        ordering=next_order,
        workspace_mode=workspace_mode,
    )
    db.add(user_msg)
    db.flush()

    # Build message history for LLM context
    message_history = [
        {"role": m.role, "content": m.content}
        for m in session.messages
    ]

    # Get portfolio context
    project_summaries = _get_project_summaries(db)
    portfolio_health = _get_portfolio_health(db)

    # Call orchestration
    from app.inference.orchestration import persona_chat_smart

    result = await persona_chat_smart(
        operator_message=content,
        workspace_mode=workspace_mode,
        message_history=message_history,
        project_summaries=project_summaries,
        portfolio_health=portfolio_health,
    )

    # Persist Glimmer's reply
    glimmer_msg = PersonaPageMessage(
        session_id=session.id,
        role="glimmer",
        content=result.reply_content,
        ordering=next_order + 1,
        workspace_mode=workspace_mode,
        inference_metadata={
            "used_llm": result.used_llm,
            "fallback_reason": result.fallback_reason,
            "inference_latency_ms": result.inference_latency_ms,
            "model": result.model,
            "prompt_tokens": result.prompt_tokens,
            "completion_tokens": result.completion_tokens,
            "total_tokens": result.total_tokens,
        },
    )
    db.add(glimmer_msg)

    # Update session timestamps
    session.updated_at = datetime.now(timezone.utc)

    # Update channel session
    channel_session = db.get(ChannelSession, session.channel_session_id)
    if channel_session:
        channel_session.last_interaction_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(glimmer_msg)

    return _message_to_response(glimmer_msg)


@router.patch("/sessions/{session_id}", response_model=PersonaSessionResponse)
def update_session(
    session_id: str,
    request: UpdateSessionRequest,
    db: Session = Depends(get_db),
) -> PersonaSessionResponse:
    """Update a persona-page session status.

    ARCH:PersonaPageSessionModel — enforces valid lifecycle transitions.
    """
    import uuid as _uuid
    try:
        sid = _uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found")

    session = db.execute(
        select(PersonaPageSession)
        .where(PersonaPageSession.id == sid)
        .options(selectinload(PersonaPageSession.messages))
    ).scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    new_status = request.session_status
    if new_status not in VALID_SESSION_STATUSES:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid session status: {new_status}",
        )

    allowed = VALID_TRANSITIONS.get(session.session_status, set())
    if new_status not in allowed:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot transition from {session.session_status} to {new_status}",
        )

    session.session_status = new_status
    if new_status == "confirmed":
        session.confirmed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(session)

    return _session_to_response(session)


# ── Working state contracts ───────────────────────────────────────


class CandidateNodePayload(BaseModel):
    """A single candidate node in the working state."""
    node_id: str
    entity_type: str
    label: str
    subtitle: str | None = None
    status: str = "pending"  # pending, accepted_by_operator, discarded_by_operator
    source_origin: str = "conversation"  # conversation, paste_in, operator_created
    metadata: dict | None = None
    position_x: float | None = None
    position_y: float | None = None


class CandidateEdgePayload(BaseModel):
    """A single candidate edge in the working state."""
    edge_id: str
    source_node_id: str
    target_node_id: str
    relation: str  # owns, depends_on, blocks, involves, linked_to
    label: str | None = None


class SaveWorkingStateRequest(BaseModel):
    """Request to save/backup the mind-map working state."""
    candidate_nodes: list[CandidateNodePayload]
    candidate_edges: list[CandidateEdgePayload]
    state_version: int = 1


class WorkingStateResponse(BaseModel):
    """Response for the working state of a session."""
    session_id: str
    candidate_nodes: list[dict]
    candidate_edges: list[dict]
    state_version: int
    updated_at: str


class ConfirmWorkingStateRequest(BaseModel):
    """Request to confirm the working state and persist accepted entities.

    Only nodes with status="accepted_by_operator" will be persisted.
    """
    accepted_node_ids: list[str]


class ConfirmWorkingStateResponse(BaseModel):
    """Response for the confirm & save operation."""
    session_id: str
    persisted_count: int
    persisted_entities: list[dict]
    session_status: str


class DiscardWorkingStateResponse(BaseModel):
    """Response for the discard operation."""
    session_id: str
    discarded: bool
    session_status: str


# ── Working state helpers ─────────────────────────────────────────


def _resolve_session(session_id: str, db: Session) -> PersonaPageSession:
    """Resolve a session by ID, raising 404 if not found."""
    import uuid as _uuid
    try:
        sid = _uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found")

    session = db.execute(
        select(PersonaPageSession)
        .where(PersonaPageSession.id == sid)
        .options(
            selectinload(PersonaPageSession.messages),
            selectinload(PersonaPageSession.working_state),
        )
    ).scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return session


# ── Working state routes ──────────────────────────────────────────


@router.put(
    "/sessions/{session_id}/working-state",
    response_model=WorkingStateResponse,
)
def save_working_state(
    session_id: str,
    request: SaveWorkingStateRequest,
    db: Session = Depends(get_db),
) -> WorkingStateResponse:
    """Save or update the mind-map working state for session backup.

    ARCH:MindMapWorkingStateModel
    ARCH:PersonaPage.StagedPersistence

    This is a session-scoped backup. Nothing is persisted to the operational
    database until the operator explicitly confirms via the confirm endpoint.
    """
    session = _resolve_session(session_id, db)

    if session.session_status in ("confirmed", "abandoned"):
        raise HTTPException(
            status_code=409,
            detail=f"Session is {session.session_status} — cannot modify working state",
        )

    nodes_data = [n.model_dump() for n in request.candidate_nodes]
    edges_data = [e.model_dump() for e in request.candidate_edges]

    if session.working_state:
        ws = session.working_state
        ws.candidate_nodes = nodes_data
        ws.candidate_edges = edges_data
        ws.state_version = request.state_version
    else:
        ws = MindMapWorkingState(
            session_id=session.id,
            candidate_nodes=nodes_data,
            candidate_edges=edges_data,
            state_version=request.state_version,
        )
        db.add(ws)

    db.commit()
    db.refresh(ws)

    return WorkingStateResponse(
        session_id=str(session.id),
        candidate_nodes=ws.candidate_nodes or [],
        candidate_edges=ws.candidate_edges or [],
        state_version=ws.state_version,
        updated_at=ws.updated_at.isoformat() if ws.updated_at else "",
    )


@router.get(
    "/sessions/{session_id}/working-state",
    response_model=WorkingStateResponse,
)
def get_working_state(
    session_id: str,
    db: Session = Depends(get_db),
) -> WorkingStateResponse:
    """Retrieve the saved working state for session resumption.

    ARCH:MindMapWorkingStateModel
    """
    session = _resolve_session(session_id, db)

    if not session.working_state:
        return WorkingStateResponse(
            session_id=str(session.id),
            candidate_nodes=[],
            candidate_edges=[],
            state_version=0,
            updated_at="",
        )

    ws = session.working_state
    return WorkingStateResponse(
        session_id=str(session.id),
        candidate_nodes=ws.candidate_nodes or [],
        candidate_edges=ws.candidate_edges or [],
        state_version=ws.state_version,
        updated_at=ws.updated_at.isoformat() if ws.updated_at else "",
    )


@router.post(
    "/sessions/{session_id}/confirm",
    response_model=ConfirmWorkingStateResponse,
)
def confirm_working_state(
    session_id: str,
    request: ConfirmWorkingStateRequest,
    db: Session = Depends(get_db),
) -> ConfirmWorkingStateResponse:
    """Confirm & Save — persist accepted working-state entities in one batch.

    ARCH:PersonaPage.StagedPersistence
    ARCH:StateOwnershipBoundaries
    REQ:PersonaPageStagedPersistence

    Only nodes whose IDs appear in accepted_node_ids are persisted.
    The session transitions to "confirmed" status.

    This is a coordinated batch commit — all accepted entities are persisted
    in a single transaction. If any entity fails, none are persisted.
    """
    session = _resolve_session(session_id, db)

    if session.session_status not in ("active", "paused"):
        raise HTTPException(
            status_code=409,
            detail=f"Session is {session.session_status} — cannot confirm",
        )

    if not session.working_state or not session.working_state.candidate_nodes:
        raise HTTPException(
            status_code=422,
            detail="No working state to confirm — save working state first",
        )

    ws = session.working_state
    nodes = ws.candidate_nodes or []
    accepted_ids = set(request.accepted_node_ids)

    # Filter to only the accepted nodes
    accepted_nodes = [n for n in nodes if n.get("node_id") in accepted_ids]

    if not accepted_nodes:
        raise HTTPException(
            status_code=422,
            detail="No accepted nodes found in working state",
        )

    # Persist accepted entities to the operational database.
    # Two-pass approach: projects and stakeholders first (no project_id required),
    # then subsidiary entities that require a project_id linkage.
    persisted = []
    created_project_id: uuid.UUID | None = None

    import uuid as _uuid

    # Pass 1: Create projects and stakeholders
    for node in accepted_nodes:
        entity_type = node.get("entity_type", "")
        label = node.get("label", "")
        meta = node.get("metadata") or {}

        if entity_type == "project":
            project = Project(
                name=label,
                objective=meta.get("objective", ""),
                short_summary=node.get("subtitle", ""),
                status="active",
            )
            db.add(project)
            db.flush()
            if created_project_id is None:
                created_project_id = project.id
            persisted.append({
                "entity_type": "project",
                "entity_id": str(project.id),
                "label": label,
            })
        elif entity_type == "stakeholder":
            stakeholder = Stakeholder(
                display_name=label,
                role_title=node.get("subtitle"),
            )
            db.add(stakeholder)
            db.flush()
            persisted.append({
                "entity_type": "stakeholder",
                "entity_id": str(stakeholder.id),
                "label": label,
            })

    # If no project was created in this batch, find the first active project
    # to link subsidiary entities to
    if created_project_id is None:
        first_project = db.execute(
            select(Project).where(
                Project.archived == False,  # noqa: E712
            ).limit(1)
        ).scalar_one_or_none()
        if first_project:
            created_project_id = first_project.id

    # Pass 2: Create subsidiary entities (need project_id)
    for node in accepted_nodes:
        entity_type = node.get("entity_type", "")
        label = node.get("label", "")
        meta = node.get("metadata") or {}
        # Resolve project_id: explicit from metadata, or auto-linked
        node_project_id = meta.get("project_id")
        if node_project_id:
            try:
                node_project_id = _uuid.UUID(str(node_project_id))
            except ValueError:
                node_project_id = created_project_id
        else:
            node_project_id = created_project_id

        if entity_type == "milestone":
            milestone = Milestone(
                title=label,
                description=node.get("subtitle", ""),
                project_id=node_project_id,
            )
            db.add(milestone)
            db.flush()
            persisted.append({
                "entity_type": "milestone",
                "entity_id": str(milestone.id),
                "label": label,
            })
        elif entity_type == "risk":
            risk = RiskRecord(
                summary=label,
                severity_signal=meta.get("severity", "medium"),
                status="active",
                project_id=node_project_id,
            )
            db.add(risk)
            db.flush()
            persisted.append({
                "entity_type": "risk",
                "entity_id": str(risk.id),
                "label": label,
            })
        elif entity_type == "blocker":
            blocker = BlockerRecord(
                summary=label,
                status="active",
                project_id=node_project_id,
            )
            db.add(blocker)
            db.flush()
            persisted.append({
                "entity_type": "blocker",
                "entity_id": str(blocker.id),
                "label": label,
            })
        elif entity_type == "work_item":
            work_item = WorkItem(
                title=label,
                description=node.get("subtitle", ""),
                status="open",
                project_id=node_project_id,
            )
            db.add(work_item)
            db.flush()
            persisted.append({
                "entity_type": "work_item",
                "entity_id": str(work_item.id),
                "label": label,
            })
        elif entity_type == "decision":
            decision = DecisionRecord(
                title=label,
                decision_text=label,
                rationale=node.get("subtitle", ""),
                status="active",
                project_id=node_project_id,
            )
            db.add(decision)
            db.flush()
            persisted.append({
                "entity_type": "decision",
                "entity_id": str(decision.id),
                "label": label,
            })
        elif entity_type not in ("project", "stakeholder"):
            # Unknown entity type — skip but log
            logger.warning(
                "Skipping unknown entity type %r for node %r",
                entity_type,
                node.get("node_id"),
            )

    # Transition session to confirmed
    session.session_status = "confirmed"
    session.confirmed_at = datetime.now(timezone.utc)

    db.commit()

    return ConfirmWorkingStateResponse(
        session_id=str(session.id),
        persisted_count=len(persisted),
        persisted_entities=persisted,
        session_status="confirmed",
    )


@router.post(
    "/sessions/{session_id}/discard",
    response_model=DiscardWorkingStateResponse,
)
def discard_working_state(
    session_id: str,
    db: Session = Depends(get_db),
) -> DiscardWorkingStateResponse:
    """Discard the working state without persisting any entities.

    ARCH:PersonaPage.StagedPersistence
    ARCH:StateOwnershipBoundaries

    The session transitions to "abandoned" status. The working state
    record is deleted. No entities reach the operational database.
    """
    session = _resolve_session(session_id, db)

    if session.session_status in ("confirmed", "abandoned"):
        raise HTTPException(
            status_code=409,
            detail=f"Session is already {session.session_status}",
        )

    # Delete working state if it exists
    if session.working_state:
        db.delete(session.working_state)

    session.session_status = "abandoned"
    db.commit()

    return DiscardWorkingStateResponse(
        session_id=str(session.id),
        discarded=True,
        session_status="abandoned",
    )



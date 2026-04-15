"""Shared graph state contracts for all Glimmer workflows.

ARCH:GraphState.WorkflowContext
ARCH:GraphState.DomainReferences
ARCH:GraphState.ReviewState
ARCH:GraphState.ContinuationMetadata
ARCH:GraphState.ConfidenceSignals

These TypedDict-based state shapes define the information that flows
through LangGraph graphs. State is reference-based — it holds IDs to
persisted domain entities, not full payloads.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Annotated, Any, Literal, Optional

from langgraph.graph import add_messages
from typing_extensions import TypedDict


# ── Intake Graph State ───────────────────────────────────────────────


class IntakeState(TypedDict, total=False):
    """State for the Intake Graph.

    ARCH:IntakeGraph
    """

    # Source reference — what came in
    source_record_ids: list[uuid.UUID]
    record_type: str  # message, calendar_event, imported_signal
    connected_account_id: uuid.UUID
    provider_type: str
    profile_id: Optional[uuid.UUID]

    # Routing decision
    route_target: str  # triage, planner, drafting, telegram, voice
    route_reason: str

    # Triage results (populated by triage_handoff when pipeline runs)
    triage_classification_ids: list[uuid.UUID]
    triage_extraction_ids: list[uuid.UUID]
    triage_needs_review: bool
    triage_review_reasons: list[str]
    triage_records_processed: int
    triage_error: Optional[str]

    # Metadata
    workflow_id: str
    initiated_at: str
    channel: str  # web, telegram, voice, api
    current_step: str


# ── Triage Graph State ───────────────────────────────────────────────


class TriageState(TypedDict, total=False):
    """State for the Triage Graph.

    ARCH:TriageGraph
    ARCH:GraphState.ConfidenceSignals
    """

    # Source context
    source_record_ids: list[uuid.UUID]
    record_type: str
    connected_account_id: uuid.UUID
    provider_type: str

    # Classification result
    classified_project_id: Optional[uuid.UUID]
    classification_confidence: float  # 0.0 to 1.0
    classification_rationale: str
    classification_candidates: list[dict]  # [{project_id, score, reason}]

    # Stakeholder resolution
    resolved_stakeholder_ids: list[uuid.UUID]
    stakeholder_confidence: float
    stakeholder_ambiguities: list[dict]

    # Extraction results
    extracted_action_ids: list[uuid.UUID]
    extracted_decision_ids: list[uuid.UUID]
    extracted_deadline_ids: list[uuid.UUID]

    # Review state
    needs_review: bool
    review_reasons: list[str]
    review_artifact_ids: list[uuid.UUID]

    # Workflow tracking
    workflow_id: str
    current_step: str
    is_interrupted: bool


# ── Review Request Model ─────────────────────────────────────────────


class ReviewRequest(TypedDict):
    """A structured review request for human operator input.

    ARCH:InterruptAndResumeModel
    ARCH:InterruptPersistenceContract
    """

    review_id: str
    workflow_id: str
    review_type: str  # classification_ambiguity, stakeholder_uncertain, action_ambiguous, external_impact
    decision_required: str
    candidate_outcomes: list[dict]
    context_summary: str
    source_record_ids: list[str]
    continuation_path: str
    created_at: str


# ── Planner Graph State ──────────────────────────────────────────────


class PlannerState(TypedDict, total=False):
    """State for the Planner Graph.

    ARCH:PlannerGraph
    ARCH:PlannerGraphExplainability
    """

    # Input context
    project_ids: list[uuid.UUID]
    trigger_type: str  # daily, on_demand, post_triage, scheduled_refresh

    # Output artifacts
    focus_pack_id: Optional[uuid.UUID]
    priority_items: list[dict]  # [{item_id, priority, rationale}]
    refresh_event_ids: list[uuid.UUID]

    # Work breakdown
    suggested_next_steps: list[dict]  # [{project_id, step, rationale}]
    restructure_proposed: bool  # must trigger review if True

    # Workflow tracking
    workflow_id: str
    current_step: str


# ── Drafting Graph State ─────────────────────────────────────────────


class DraftingState(TypedDict, total=False):
    """State for the Drafting Graph.

    ARCH:DraftingGraph
    ARCH:DraftingGraphNoAutoSend
    """

    # Input context
    source_message_id: Optional[uuid.UUID]
    project_id: Optional[uuid.UUID]
    stakeholder_ids: list[uuid.UUID]
    intent: str  # reply, follow_up, initiate, brief

    # Output
    draft_id: Optional[uuid.UUID]
    variant_ids: list[uuid.UUID]
    tone: str

    # Safety
    auto_send_blocked: bool  # Always True — hard rule
    review_required: bool  # Always True for drafts

    # Workflow tracking
    workflow_id: str
    current_step: str


# ── Voice Session Graph State ─────────────────────────────────────────


class VoiceSessionGraphState(TypedDict, total=False):
    """State for the Voice Session Graph.

    ARCH:VoiceSessionGraph
    ARCH:VoiceInteractionArchitecture

    Carries transient voice-session context through graph execution.
    Durable state lives in ChannelSession/VoiceSessionState rows.
    """

    # Session identity
    session_id: uuid.UUID
    channel_session_id: uuid.UUID
    operator_id: Optional[uuid.UUID]

    # Transcript segments [{text, timestamp, index}]
    transcript_segments: list[dict]
    imported_signal_ids: list[uuid.UUID]

    # Continuity context — bounded, not unbounded memory
    current_topic: Optional[str]
    referenced_project_ids: list[uuid.UUID]
    unresolved_prompts: list[str]
    recent_assistant_context: Optional[str]

    # Pending actions extracted from voice
    pending_actions: list[dict]

    # Routing to shared core
    route_target: str  # triage, planner, drafting
    route_reason: str

    # Review state
    needs_review: bool
    review_reasons: list[str]

    # Safety — same rules as all other channels
    auto_send_blocked: bool  # Always True — hard rule

    # Workflow tracking
    workflow_id: str
    current_step: str


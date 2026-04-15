"""Intake graph — routes incoming source references to the correct triage path.

ARCH:IntakeGraph
ARCH:IntakeGraphRouting

The Intake Graph accepts IntakeReferences from the connector layer
and routes them to the appropriate downstream workflow:
- Messages and signals → Triage Graph
- Calendar events → Triage Graph (for project classification)
- Telegram signals → Telegram Companion path
- Voice transcripts → Voice Session path
- Explicit draft requests → Drafting Graph
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any  # noqa: F401 — preserved for potential subclass usage

from langgraph.graph import StateGraph, END

from app.graphs.state import IntakeState

logger = logging.getLogger(__name__)


def _genuuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Graph Nodes ──────────────────────────────────────────────────────


def classify_source(state: IntakeState) -> IntakeState:
    """Determine the routing target based on source type and context.

    ARCH:IntakeGraphRouting

    Routes:
    - message, imported_signal → triage (default path)
    - calendar_event → triage (for project-context classification)
    - telegram signals → triage (enters via shared triage for now)
    - voice transcripts → triage (enters via shared triage for now)
    """
    record_type = state.get("record_type", "")
    provider_type = state.get("provider_type", "")
    channel = state.get("channel", "web")

    # Determine route based on record type and channel
    if record_type in ("message", "thread"):
        route = "triage"
        reason = f"Mail message from {provider_type} → triage for classification"
    elif record_type == "calendar_event":
        route = "triage"
        reason = f"Calendar event from {provider_type} → triage for project context"
    elif record_type == "imported_signal":
        route = "triage"
        reason = "Imported signal → triage for classification"
    else:
        route = "triage"
        reason = f"Unknown record type '{record_type}' → default triage path"

    return {
        **state,
        "route_target": route,
        "route_reason": reason,
        "workflow_id": state.get("workflow_id", _genuuid()),
        "initiated_at": state.get("initiated_at", _utcnow()),
    }


def route_to_target(state: IntakeState) -> str:
    """Conditional routing function — returns the next graph node name."""
    return state.get("route_target", "triage")


# ── Graph Construction ───────────────────────────────────────────────


def triage_handoff(state: IntakeState) -> IntakeState:
    """Execute real triage on source records that were routed to triage.

    ARCH:TriageGraph
    ARCH:OrchestrationPrinciple.VisibleArtifacts
    PLAN:WorkstreamI.PackageI8.OrchestrationWiring
    TEST:Triage.Pipeline.EndToEndClassificationAndExtraction

    Loads the source records from DB, classifies each, extracts
    actions/decisions/deadlines, and persists the results.  If DB is
    unavailable or records are not found, degrades gracefully.
    """
    source_record_ids = state.get("source_record_ids", [])
    record_type = state.get("record_type", "")
    connected_account_id = state.get("connected_account_id")

    if not source_record_ids:
        logger.debug("triage_handoff: no source_record_ids, skipping pipeline")
        return {**state, "current_step": "triage_handoff_complete"}

    try:
        from app.db import get_session
        from app.services.triage_pipeline import process_triage_batch

        session = get_session()
        try:
            result = process_triage_batch(
                session=session,
                source_record_ids=source_record_ids,
                record_type=record_type,
                connected_account_id=connected_account_id,
            )
            session.commit()

            logger.info(
                "triage_handoff: processed=%d skipped=%d needs_review=%s",
                result.records_processed,
                result.records_skipped,
                result.needs_review,
            )

            return {
                **state,
                "current_step": "triage_handoff_complete",
                "triage_classification_ids": result.classification_ids,
                "triage_extraction_ids": result.extraction_ids,
                "triage_needs_review": result.needs_review,
                "triage_review_reasons": result.review_reasons,
                "triage_records_processed": result.records_processed,
            }
        finally:
            session.close()

    except Exception as exc:
        logger.warning("triage_handoff: pipeline error — %s", exc)
        return {
            **state,
            "current_step": "triage_handoff_failed",
            "triage_error": str(exc),
        }


def build_intake_graph() -> StateGraph:
    """Build the Intake Graph.

    ARCH:IntakeGraph

    Shape:
    START → classify_source → route → [triage | planner | drafting | END]
    """
    graph = StateGraph(IntakeState)

    graph.add_node("classify_source", classify_source)

    # Triage handoff — runs real classification and extraction pipeline
    graph.add_node("triage_handoff", triage_handoff)
    graph.add_node("planner_handoff", lambda s: {**s, "current_step": "planner_handoff_complete"})
    graph.add_node("drafting_handoff", lambda s: {**s, "current_step": "drafting_handoff_complete"})

    graph.set_entry_point("classify_source")

    graph.add_conditional_edges(
        "classify_source",
        route_to_target,
        {
            "triage": "triage_handoff",
            "planner": "planner_handoff",
            "drafting": "drafting_handoff",
        },
    )

    graph.add_edge("triage_handoff", END)
    graph.add_edge("planner_handoff", END)
    graph.add_edge("drafting_handoff", END)

    return graph


def get_intake_graph():
    """Get a compiled intake graph ready for invocation."""
    return build_intake_graph().compile()


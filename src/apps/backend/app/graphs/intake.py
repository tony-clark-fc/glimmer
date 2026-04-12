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

import uuid
from datetime import datetime, timezone
from typing import Any

from langgraph.graph import StateGraph, END

from app.graphs.state import IntakeState


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


def build_intake_graph() -> StateGraph:
    """Build the Intake Graph.

    ARCH:IntakeGraph

    Shape:
    START → classify_source → route → [triage | planner | drafting | END]
    """
    graph = StateGraph(IntakeState)

    graph.add_node("classify_source", classify_source)

    # Terminal routing — the intake graph hands off to the next graph
    # In a production setup these would invoke subgraphs.
    # For now, routing decision is the output.
    graph.add_node("triage_handoff", lambda s: {**s, "current_step": "triage_handoff_complete"})
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


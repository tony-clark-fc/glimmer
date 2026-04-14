"""Glimmer graph orchestration layer.

ARCH:LangGraphTopology
ARCH:OrchestrationRole

This package contains the LangGraph-based orchestration workflows:
- Intake graph: routes incoming source references to the correct triage path
- Triage graph: classifies, interprets, and extracts from source records
- Planner graph: generates focus packs and priorities
- Drafting graph: creates reviewable draft artifacts
- Research escalation graph: routes to deep research or expert advice

Graphs coordinate; they do not become memory stores.
Durable truth belongs in the domain/persistence layer (Workstream B).
"""


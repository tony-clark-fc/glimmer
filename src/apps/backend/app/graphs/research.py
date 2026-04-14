"""Research Escalation Graph and Expert Advice orchestration.

ARCH:ResearchEscalationGraph
ARCH:ResearchEscalationPolicy
ARCH:ExpertAdviceSubflow
ARCH:ExpertAdviceEscalationPolicy

This module provides:
- determine_escalation_mode() — routing policy (H8)
- Research Escalation Graph — LangGraph workflow that routes
  escalation requests to deep research or expert advice (H4)
- Persistence integration for ResearchRun and ExpertAdviceExchange

Results always enter as interpreted candidates (pending_review).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.research import (
    ExpertAdviceExchange,
    ResearchRun,
    ResearchSummaryArtifact,
)
from app.models.audit import AuditRecord
from app.research.adapter import GeminiAdapter
from app.research.contracts import ChatRequest, ResearchRequest


# ── Escalation Routing Policy (H8) ──────────────────────────────────


# Keywords that suggest a multi-step research investigation
_RESEARCH_KEYWORDS = [
    "research", "investigate", "deep dive", "comprehensive",
    "survey", "analysis", "compare", "benchmark", "literature",
    "systematic", "explore", "review the evidence",
]


def determine_escalation_mode(
    task_description: str,
    explicit_mode: Optional[str] = None,
) -> str:
    """Determine whether to route to deep research or expert advice.

    ARCH:ExpertAdviceEscalationPolicy
    ARCH:ResearchEscalationPolicy

    TEST:ExpertAdvice.Routing.EscalationDistinguishesResearchFromAdvice

    Priority:
    1. Explicit operator choice wins
    2. Heuristic based on task keywords
    3. Default → "advice" (fast path)
    """
    if explicit_mode:
        if explicit_mode.lower() in ("research", "deep_research"):
            return "research"
        if explicit_mode.lower() in ("advice", "expert_advice", "chat"):
            return "advice"

    # Heuristic: check for research-suggesting keywords
    lower = task_description.lower()
    research_signals = sum(1 for kw in _RESEARCH_KEYWORDS if kw in lower)

    if research_signals >= 2:
        return "research"
    if len(task_description) > 500:
        # Long task descriptions suggest research over quick advice
        return "research"

    return "advice"


# ── Research Escalation Result ───────────────────────────────────────


@dataclass
class EscalationResult:
    """Result of a research escalation — either deep research or expert advice."""

    mode: str
    status: str
    research_run_id: Optional[uuid.UUID] = field(default=None)
    expert_advice_exchange_id: Optional[uuid.UUID] = field(default=None)
    document_url: Optional[str] = field(default=None)
    response_text: Optional[str] = field(default=None)
    error_message: Optional[str] = field(default=None)


# ── Execute Research Escalation ──────────────────────────────────────


async def execute_research_escalation(
    session: Session,
    adapter: GeminiAdapter,
    prompt: str,
    mode: Optional[str] = None,
    gemini_mode: str = "Pro",
    project_id: Optional[uuid.UUID] = None,
    invocation_origin: str = "operator_request",
    triggering_context: Optional[dict] = None,
    document_name: Optional[str] = None,
) -> EscalationResult:
    """Execute a research escalation — routes to deep research or expert advice.

    ARCH:ResearchEscalationGraph
    TEST:Research.Escalation.RoutesWhenTaskRequiresDeepResearch

    This is the top-level entry point for the research/advice capability.
    It:
    1. Determines escalation mode (research vs advice)
    2. Creates the appropriate domain record
    3. Invokes the adapter
    4. Persists results with review_state=pending_review
    5. Creates audit record
    """
    escalation_mode = determine_escalation_mode(prompt, explicit_mode=mode)

    if escalation_mode == "research":
        return await _execute_deep_research(
            session=session,
            adapter=adapter,
            prompt=prompt,
            project_id=project_id,
            invocation_origin=invocation_origin,
            triggering_context=triggering_context,
            document_name=document_name or f"Glimmer-Research-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M')}",
        )
    else:
        return await _execute_expert_advice(
            session=session,
            adapter=adapter,
            prompt=prompt,
            gemini_mode=gemini_mode,
            project_id=project_id,
            invocation_origin=invocation_origin,
            triggering_context=triggering_context,
        )


# ── Deep Research Execution ──────────────────────────────────────────


async def _execute_deep_research(
    session: Session,
    adapter: GeminiAdapter,
    prompt: str,
    project_id: Optional[uuid.UUID],
    invocation_origin: str,
    triggering_context: Optional[dict],
    document_name: str,
) -> EscalationResult:
    """Execute deep research with full persistence and audit.

    ARCH:ResearchRunLifecycle
    TEST:Research.Invocation.StartsBoundedResearchRun
    TEST:Research.Provenance.RunAndSourceTrailPersisted
    """
    # Create research run record
    run = ResearchRun(
        invocation_origin=invocation_origin,
        triggering_context=triggering_context,
        project_id=project_id,
        research_query=prompt,
        document_name=document_name,
        status="in_progress",
        started_at=datetime.now(timezone.utc),
    )
    session.add(run)
    session.flush()

    try:
        result = await adapter.execute_research(
            ResearchRequest(prompt=prompt, document_name=document_name)
        )

        # Update run with success
        run.status = "completed"
        run.completion_signal = "success"
        run.document_url = result.document_url
        run.document_renamed = result.document_renamed
        run.completed_at = datetime.now(timezone.utc)

        # Create summary artifact as interpreted candidate
        summary = ResearchSummaryArtifact(
            research_run_id=run.id,
            summary_text=f"Deep research completed for: {prompt[:200]}",
            linked_project_ids=(
                {"project_ids": [str(project_id)]} if project_id else None
            ),
            review_state="pending_review",
        )
        session.add(summary)

        # Audit
        audit = AuditRecord(
            entity_type="research_run",
            entity_id=run.id,
            action="completed",
            actor=invocation_origin,
            change_summary=f"Deep research completed — doc: {result.document_url}",
            new_state={
                "run_id": str(run.id),
                "status": "completed",
                "document_url": result.document_url,
            },
        )
        session.add(audit)
        session.flush()

        return EscalationResult(
            mode="research",
            status="completed",
            research_run_id=run.id,
            document_url=result.document_url,
        )

    except Exception as exc:
        # Record failure
        run.status = "failed"
        run.completion_signal = "error"
        run.error_message = str(exc)
        run.completed_at = datetime.now(timezone.utc)

        audit = AuditRecord(
            entity_type="research_run",
            entity_id=run.id,
            action="failed",
            actor=invocation_origin,
            change_summary=f"Deep research failed: {str(exc)[:200]}",
            new_state={"run_id": str(run.id), "status": "failed"},
        )
        session.add(audit)
        session.flush()

        return EscalationResult(
            mode="research",
            status="failed",
            research_run_id=run.id,
            error_message=str(exc),
        )


# ── Expert Advice Execution ──────────────────────────────────────────


async def _execute_expert_advice(
    session: Session,
    adapter: GeminiAdapter,
    prompt: str,
    gemini_mode: str,
    project_id: Optional[uuid.UUID],
    invocation_origin: str,
    triggering_context: Optional[dict],
) -> EscalationResult:
    """Execute expert advice with full persistence and audit.

    ARCH:ExpertAdviceSubflow
    TEST:ExpertAdvice.Invocation.SendsPromptAndReturnsResponse
    TEST:ExpertAdvice.Provenance.ExchangeRecordPersisted
    """
    # Create exchange record
    exchange = ExpertAdviceExchange(
        invocation_origin=invocation_origin,
        triggering_context=triggering_context,
        project_id=project_id,
        prompt=prompt,
        gemini_mode=gemini_mode,
        status="in_progress",
    )
    session.add(exchange)
    session.flush()

    try:
        result = await adapter.execute_chat(
            ChatRequest(prompt=prompt, mode=gemini_mode)
        )

        # Update exchange with success
        exchange.status = "completed"
        exchange.response_text = result.response_text
        exchange.duration_ms = result.duration_ms
        exchange.completed_at = datetime.now(timezone.utc)
        exchange.review_state = "pending_review"

        # Audit
        audit = AuditRecord(
            entity_type="expert_advice_exchange",
            entity_id=exchange.id,
            action="completed",
            actor=invocation_origin,
            change_summary=(
                f"Expert advice completed — mode: {gemini_mode}, "
                f"duration: {result.duration_ms}ms"
            ),
            new_state={
                "exchange_id": str(exchange.id),
                "status": "completed",
                "mode": gemini_mode,
            },
        )
        session.add(audit)
        session.flush()

        return EscalationResult(
            mode="advice",
            status="completed",
            expert_advice_exchange_id=exchange.id,
            response_text=result.response_text,
        )

    except Exception as exc:
        # Record failure
        exchange.status = "failed"
        exchange.error_message = str(exc)

        audit = AuditRecord(
            entity_type="expert_advice_exchange",
            entity_id=exchange.id,
            action="failed",
            actor=invocation_origin,
            change_summary=f"Expert advice failed: {str(exc)[:200]}",
            new_state={"exchange_id": str(exchange.id), "status": "failed"},
        )
        session.add(audit)
        session.flush()

        return EscalationResult(
            mode="advice",
            status="failed",
            expert_advice_exchange_id=exchange.id,
            error_message=str(exc),
        )


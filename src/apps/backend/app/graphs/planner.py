"""Planner services — focus-pack generation, priority scoring, work-breakdown.

ARCH:PlannerGraph
ARCH:PlannerGraphExplainability
ARCH:PlannerGraphReviewGate
ARCH:FocusPackModel
ARCH:TodayViewArchitecture
PLAN:WorkstreamI.PackageI8.OrchestrationWiring

These services produce explainable priority outputs and durable
focus-pack artifacts from the current operational state.

When the LLM is available and enabled, the planner enriches focus
packs with a natural-language narrative summary.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.portfolio import Project
from app.models.execution import WorkItem, BlockerRecord, WaitingOnRecord, RiskRecord
from app.models.interpretation import ExtractedAction, ExtractedDeadlineSignal
from app.models.drafting import FocusPack
from app.models.audit import AuditRecord

logger = logging.getLogger(__name__)


# ── Priority Item ────────────────────────────────────────────────────


class PriorityItem:
    """A single scored priority item with rationale."""

    def __init__(
        self,
        item_id: uuid.UUID,
        item_type: str,
        project_id: Optional[uuid.UUID],
        priority_score: float,
        rationale: str,
        title: str,
    ):
        self.item_id = item_id
        self.item_type = item_type
        self.project_id = project_id
        self.priority_score = priority_score
        self.rationale = rationale
        self.title = title

    def to_dict(self) -> dict:
        return {
            "item_id": str(self.item_id),
            "item_type": self.item_type,
            "project_id": str(self.project_id) if self.project_id else None,
            "priority_score": self.priority_score,
            "rationale": self.rationale,
            "title": self.title,
        }


# ── Focus Pack Result ────────────────────────────────────────────────


class FocusPackResult:
    """Result of focus-pack generation."""

    def __init__(
        self,
        focus_pack_id: uuid.UUID,
        priority_items: list[PriorityItem],
        top_actions: list[dict],
        high_risk_items: list[dict],
        waiting_on_items: list[dict],
        reply_debt_summary: Optional[str],
        calendar_pressure_summary: Optional[str],
        narrative_summary: Optional[str] = None,
    ):
        self.focus_pack_id = focus_pack_id
        self.priority_items = priority_items
        self.top_actions = top_actions
        self.high_risk_items = high_risk_items
        self.waiting_on_items = waiting_on_items
        self.reply_debt_summary = reply_debt_summary
        self.calendar_pressure_summary = calendar_pressure_summary
        self.narrative_summary = narrative_summary


# ── Priority Scoring ─────────────────────────────────────────────────


def _score_work_item(item: WorkItem) -> PriorityItem:
    """Score a work item for priority ranking.

    ARCH:PlannerGraphExplainability — rationale preserved.
    """
    score = 0.0
    reasons: list[str] = []

    # Status urgency
    if item.status == "open":
        score += 0.3
        reasons.append("Open work item")
    elif item.status == "in_progress":
        score += 0.4
        reasons.append("In-progress work item")

    # Due date urgency
    if item.due_date:
        now = datetime.now(timezone.utc)
        delta = (item.due_date - now).total_seconds()
        if delta < 0:
            score += 0.5
            reasons.append("Overdue")
        elif delta < 86400:  # within 24 hours
            score += 0.4
            reasons.append("Due within 24 hours")
        elif delta < 259200:  # within 3 days
            score += 0.2
            reasons.append("Due within 3 days")

    # Priority indicators
    if item.priority_indicators:
        if item.priority_indicators.get("urgency") == "high":
            score += 0.3
            reasons.append("High urgency indicator")
        elif item.priority_indicators.get("urgency") == "medium":
            score += 0.1
            reasons.append("Medium urgency indicator")

    return PriorityItem(
        item_id=item.id,
        item_type="work_item",
        project_id=item.project_id,
        priority_score=round(min(score, 1.0), 3),
        rationale="; ".join(reasons) if reasons else "Baseline priority",
        title=item.title,
    )


def _score_pending_action(action: ExtractedAction) -> PriorityItem:
    """Score a pending extracted action for priority ranking."""
    score = 0.3  # baseline for pending review
    reasons = ["Pending action awaiting review"]

    if action.urgency_signal == "high":
        score += 0.3
        reasons.append("High urgency signal")
    elif action.urgency_signal == "medium":
        score += 0.1
        reasons.append("Medium urgency signal")

    if action.due_date_signal:
        score += 0.2
        reasons.append(f"Due date signal: {action.due_date_signal}")

    return PriorityItem(
        item_id=action.id,
        item_type="pending_action",
        project_id=action.linked_project_id,
        priority_score=round(min(score, 1.0), 3),
        rationale="; ".join(reasons),
        title=action.action_text[:100],
    )


# ── Focus Pack Generation ────────────────────────────────────────────


def generate_focus_pack(
    session: Session,
    project_ids: Optional[list[uuid.UUID]] = None,
    trigger_type: str = "on_demand",
) -> FocusPackResult:
    """Generate a focus pack from current operational state.

    ARCH:PlannerGraph — priority generation
    ARCH:PlannerGraphExplainability — rationale visibility
    ARCH:FocusPackModel — persisted focus artifacts

    The focus pack includes:
    - Top prioritized actions/work items
    - High-risk items
    - Waiting-on items
    - Reply-debt pressure summary
    - Calendar pressure summary (placeholder for now)
    """
    # Gather open work items
    work_query = select(WorkItem).where(
        WorkItem.status.in_(["open", "in_progress"])
    )
    if project_ids:
        work_query = work_query.where(WorkItem.project_id.in_(project_ids))
    work_items = session.execute(work_query).scalars().all()

    # Gather pending actions
    action_query = select(ExtractedAction).where(
        ExtractedAction.review_state == "pending_review"
    )
    if project_ids:
        action_query = action_query.where(
            ExtractedAction.linked_project_id.in_(project_ids)
        )
    pending_actions = session.execute(action_query).scalars().all()

    # Gather risks
    risk_query = select(RiskRecord).where(RiskRecord.status == "open")
    if project_ids:
        risk_query = risk_query.where(RiskRecord.project_id.in_(project_ids))
    risks = session.execute(risk_query).scalars().all()

    # Gather waiting-on
    waiting_query = select(WaitingOnRecord).where(
        WaitingOnRecord.status == "waiting"
    )
    if project_ids:
        waiting_query = waiting_query.where(
            WaitingOnRecord.project_id.in_(project_ids)
        )
    waiting_items = session.execute(waiting_query).scalars().all()

    # Gather blockers
    blocker_query = select(BlockerRecord).where(
        BlockerRecord.status == "active"
    )
    if project_ids:
        blocker_query = blocker_query.where(
            BlockerRecord.project_id.in_(project_ids)
        )
    blockers = session.execute(blocker_query).scalars().all()

    # Score and rank
    priority_items: list[PriorityItem] = []
    for wi in work_items:
        priority_items.append(_score_work_item(wi))
    for pa in pending_actions:
        priority_items.append(_score_pending_action(pa))

    # Sort by score descending
    priority_items.sort(key=lambda x: x.priority_score, reverse=True)

    # Build focus pack data
    top_actions_data = [pi.to_dict() for pi in priority_items[:5]]

    high_risk_data = [
        {
            "risk_id": str(r.id),
            "project_id": str(r.project_id),
            "summary": r.summary,
            "severity": r.severity_signal,
        }
        for r in risks
    ]

    waiting_on_data = [
        {
            "waiting_id": str(w.id),
            "project_id": str(w.project_id),
            "waiting_on": w.waiting_on_whom,
            "description": w.description,
            "expected_by": w.expected_by.isoformat() if w.expected_by else None,
        }
        for w in waiting_items
    ]

    # Reply debt: count pending actions (proxy for unreplied items)
    reply_debt = f"{len(pending_actions)} pending actions awaiting review" if pending_actions else None

    # Blocker pressure
    blocker_pressure = None
    if blockers:
        blocker_pressure = f"{len(blockers)} active blocker(s) across projects"

    # Persist focus pack
    focus_pack = FocusPack(
        top_actions={"items": top_actions_data} if top_actions_data else None,
        high_risk_items={"items": high_risk_data} if high_risk_data else None,
        waiting_on_items={"items": waiting_on_data} if waiting_on_data else None,
        reply_debt_summary=reply_debt,
        calendar_pressure_summary=blocker_pressure,
    )
    session.add(focus_pack)
    session.flush()

    # Attempt LLM narrative enrichment
    narrative = _try_llm_narrative(
        top_actions_data, high_risk_data, waiting_on_data,
        reply_debt, blocker_pressure, project_ids, session,
    )
    if narrative:
        focus_pack.narrative_summary = narrative
        session.flush()

    return FocusPackResult(
        focus_pack_id=focus_pack.id,
        priority_items=priority_items,
        top_actions=top_actions_data,
        high_risk_items=high_risk_data,
        waiting_on_items=waiting_on_data,
        reply_debt_summary=reply_debt,
        calendar_pressure_summary=blocker_pressure,
        narrative_summary=narrative,
    )


# ── Work Breakdown Advisory ──────────────────────────────────────────


class NextStepSuggestion:
    """An advisory next-step suggestion — does not mutate project state.

    ARCH:PlannerGraphReviewGate — restructuring proposals trigger review.
    """

    def __init__(
        self,
        project_id: uuid.UUID,
        suggestion: str,
        rationale: str,
        is_restructuring: bool = False,
    ):
        self.project_id = project_id
        self.suggestion = suggestion
        self.rationale = rationale
        self.is_restructuring = is_restructuring

    def to_dict(self) -> dict:
        return {
            "project_id": str(self.project_id),
            "suggestion": self.suggestion,
            "rationale": self.rationale,
            "is_restructuring": self.is_restructuring,
        }


def suggest_next_steps(
    session: Session,
    project_id: uuid.UUID,
) -> list[NextStepSuggestion]:
    """Generate advisory next-step suggestions for a project.

    ARCH:PlannerGraphReviewGate — advisory only, does not mutate state.

    Returns bounded suggestions based on current operational state.
    Does NOT silently restructure project workstreams or accepted records.
    """
    suggestions: list[NextStepSuggestion] = []

    project = session.get(Project, project_id)
    if not project:
        return suggestions

    # Check for active blockers
    blockers = session.execute(
        select(BlockerRecord).where(
            BlockerRecord.project_id == project_id,
            BlockerRecord.status == "active",
        )
    ).scalars().all()
    for b in blockers:
        suggestions.append(NextStepSuggestion(
            project_id=project_id,
            suggestion=f"Resolve blocker: {b.summary[:80]}",
            rationale="Active blockers impede project progress",
            is_restructuring=False,
        ))

    # Check for overdue work items
    now = datetime.now(timezone.utc)
    overdue = session.execute(
        select(WorkItem).where(
            WorkItem.project_id == project_id,
            WorkItem.status.in_(["open", "in_progress"]),
            WorkItem.due_date < now,
        )
    ).scalars().all()
    for wi in overdue:
        suggestions.append(NextStepSuggestion(
            project_id=project_id,
            suggestion=f"Address overdue item: {wi.title[:80]}",
            rationale=f"Due {wi.due_date.isoformat()} — now overdue",
            is_restructuring=False,
        ))

    # Check for pending actions needing review
    pending = session.execute(
        select(ExtractedAction).where(
            ExtractedAction.linked_project_id == project_id,
            ExtractedAction.review_state == "pending_review",
        )
    ).scalars().all()
    if len(pending) > 3:
        suggestions.append(NextStepSuggestion(
            project_id=project_id,
            suggestion=f"Review {len(pending)} pending extracted actions",
            rationale="Accumulating unreviewed actions reduce operational clarity",
            is_restructuring=False,
        ))

    # Check for waiting-on items nearing expected date
    waiting = session.execute(
        select(WaitingOnRecord).where(
            WaitingOnRecord.project_id == project_id,
            WaitingOnRecord.status == "waiting",
        )
    ).scalars().all()
    for w in waiting:
        if w.expected_by and w.expected_by <= now:
            suggestions.append(NextStepSuggestion(
                project_id=project_id,
                suggestion=f"Follow up: waiting on {w.waiting_on_whom}",
                rationale=f"Expected by {w.expected_by.isoformat()} — now overdue",
                is_restructuring=False,
            ))

    # If no specific actions found, suggest general progress
    if not suggestions:
        open_items = session.execute(
            select(WorkItem).where(
                WorkItem.project_id == project_id,
                WorkItem.status.in_(["open", "in_progress"]),
            )
        ).scalars().all()
        if open_items:
            top = open_items[0]
            suggestions.append(NextStepSuggestion(
                project_id=project_id,
                suggestion=f"Continue: {top.title[:80]}",
                rationale="Next open work item in queue",
                is_restructuring=False,
            ))
        else:
            suggestions.append(NextStepSuggestion(
                project_id=project_id,
                suggestion="All current work items complete — review project goals",
                rationale="No open work items remain; project may need new planning",
                is_restructuring=False,
            ))

    return suggestions


# ── LLM Narrative Enrichment ─────────────────────────────────────────


def _try_llm_narrative(
    top_actions: list[dict],
    high_risk_items: list[dict],
    waiting_on_items: list[dict],
    reply_debt: Optional[str],
    calendar_pressure: Optional[str],
    project_ids: Optional[list[uuid.UUID]],
    session: Session,
) -> Optional[str]:
    """Attempt LLM-powered narrative enrichment for a focus pack.

    PLAN:WorkstreamI.PackageI8.OrchestrationWiring
    ARCH:PlannerGraphExplainability

    Returns a natural-language narrative summary, or None if LLM is
    disabled or unavailable.  Never blocks focus pack generation —
    the deterministic data is always persisted first.
    """
    from app.inference.config import InferenceSettings

    settings = InferenceSettings()
    if not settings.llm_prioritization_enabled:
        return None

    try:
        from app.inference.orchestration import generate_briefing_smart

        # Gather project names for context
        project_names: list[str] = []
        if project_ids:
            from app.models.portfolio import Project as _Project

            for pid in project_ids:
                p = session.get(_Project, pid)
                if p and p.name:
                    project_names.append(p.name)

        result = asyncio.run(generate_briefing_smart(
            top_actions=[
                {"title": a.get("title", ""), "rationale": a.get("rationale", "")}
                for a in top_actions
            ] if top_actions else None,
            high_risk_items=[
                {"summary": r.get("summary", ""), "severity": r.get("severity", "")}
                for r in high_risk_items
            ] if high_risk_items else None,
            waiting_on_items=[
                {"waiting_on": w.get("waiting_on", ""), "description": w.get("description", "")}
                for w in waiting_on_items
            ] if waiting_on_items else None,
            reply_debt_summary=reply_debt,
            calendar_pressure_summary=calendar_pressure,
            project_names=project_names if project_names else None,
        ))

        if result.used_llm and result.briefing_text:
            logger.info(
                "Focus pack enriched with LLM narrative (%d chars)",
                len(result.briefing_text),
            )
            return result.briefing_text

        return None

    except Exception as exc:
        logger.info("LLM narrative enrichment skipped: %s", exc)
        return None



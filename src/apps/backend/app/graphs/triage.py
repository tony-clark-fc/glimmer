"""Triage services — classification, stakeholder resolution, extraction.

ARCH:TriageGraph
ARCH:TriageGraphReviewGate
ARCH:OrchestrationPrinciple.LowConfidenceReview
PLAN:WorkstreamI.PackageI8.OrchestrationWiring

These services implement the core triage logic:
- Project classification with confidence scoring
- Stakeholder resolution with uncertainty handling
- Action/decision/deadline extraction
- Review-gate enforcement for ambiguous outcomes

When the LLM inference provider is available and per-task toggles are
enabled, classification and extraction use LLM-first with deterministic
fallback.  When LLM is disabled or unavailable, the deterministic
baseline is used directly.
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
from app.models.stakeholder import Stakeholder, StakeholderIdentity
from app.models.interpretation import (
    MessageClassification,
    ExtractedAction,
    ExtractedDecision,
    ExtractedDeadlineSignal,
)

logger = logging.getLogger(__name__)


# ── Classification ───────────────────────────────────────────────────


class ClassificationResult:
    """Result of project classification for a source record."""

    def __init__(
        self,
        project_id: Optional[uuid.UUID],
        confidence: float,
        rationale: str,
        candidates: list[dict],
        needs_review: bool,
        review_reason: Optional[str] = None,
    ):
        self.project_id = project_id
        self.confidence = confidence
        self.rationale = rationale
        self.candidates = candidates  # [{project_id, score, reason}]
        self.needs_review = needs_review
        self.review_reason = review_reason


CONFIDENCE_THRESHOLD_STRONG = 0.50
CONFIDENCE_THRESHOLD_AMBIGUOUS = 0.35


def classify_project(
    session: Session,
    sender_identity: Optional[str],
    subject: Optional[str],
    body_text: Optional[str],
    source_account_label: Optional[str] = None,
) -> ClassificationResult:
    """Classify which project a message belongs to.

    Uses simple keyword/stakeholder matching for the deterministic layer.
    The LLM-augmented classification will enhance this later.

    ARCH:TriageGraph — project classification
    ARCH:TriageGraphReviewGate — ambiguity handling
    """
    projects = session.execute(
        select(Project).where(Project.status == "active")
    ).scalars().all()

    if not projects:
        return ClassificationResult(
            project_id=None,
            confidence=0.0,
            rationale="No active projects in portfolio",
            candidates=[],
            needs_review=False,
        )

    # Score each project based on name/context matching
    scored: list[dict] = []
    text_blob = " ".join(
        filter(None, [subject, body_text, sender_identity, source_account_label])
    ).lower()

    for project in projects:
        score = 0.0
        reasons = []

        # Name match
        if project.name and project.name.lower() in text_blob:
            score += 0.5
            reasons.append(f"Project name '{project.name}' found in content")

        # Objective match
        if project.objective and project.objective.lower() in text_blob:
            score += 0.3
            reasons.append("Project objective matches")

        # Summary keywords
        if project.short_summary:
            keywords = [w.lower() for w in project.short_summary.split() if len(w) > 4]
            matches = sum(1 for kw in keywords if kw in text_blob)
            if matches > 0:
                keyword_score = min(0.2, matches * 0.05)
                score += keyword_score
                reasons.append(f"{matches} summary keywords found")

        if score > 0:
            scored.append({
                "project_id": str(project.id),
                "score": round(score, 3),
                "reason": "; ".join(reasons),
            })

    # Sort by score
    scored.sort(key=lambda x: x["score"], reverse=True)

    if not scored:
        return ClassificationResult(
            project_id=None,
            confidence=0.0,
            rationale="No project match found — no keywords or context overlap",
            candidates=[],
            needs_review=True,
            review_reason="No matching project found — operator should classify manually",
        )

    top = scored[0]
    top_score = top["score"]

    if top_score >= CONFIDENCE_THRESHOLD_STRONG:
        # Strong single match
        if len(scored) > 1 and scored[1]["score"] >= CONFIDENCE_THRESHOLD_AMBIGUOUS:
            # Multiple strong candidates — ambiguous
            return ClassificationResult(
                project_id=uuid.UUID(top["project_id"]),
                confidence=top_score,
                rationale=f"Top match: {top['reason']}",
                candidates=scored[:3],
                needs_review=True,
                review_reason="Multiple projects match with similar confidence",
            )
        return ClassificationResult(
            project_id=uuid.UUID(top["project_id"]),
            confidence=top_score,
            rationale=top["reason"],
            candidates=scored[:3],
            needs_review=False,
        )

    # Weak match — needs review
    return ClassificationResult(
        project_id=uuid.UUID(top["project_id"]) if top_score > 0 else None,
        confidence=top_score,
        rationale=top["reason"] if top_score > 0 else "Very low confidence",
        candidates=scored[:3],
        needs_review=True,
        review_reason="Classification confidence below threshold",
    )


# ── Stakeholder Resolution ───────────────────────────────────────────


class StakeholderResolutionResult:
    """Result of stakeholder identity resolution."""

    def __init__(
        self,
        stakeholder_ids: list[uuid.UUID],
        confidence: float,
        ambiguities: list[dict],
        needs_review: bool,
        review_reason: Optional[str] = None,
    ):
        self.stakeholder_ids = stakeholder_ids
        self.confidence = confidence
        self.ambiguities = ambiguities
        self.needs_review = needs_review
        self.review_reason = review_reason


def resolve_stakeholders(
    session: Session,
    sender_identity: Optional[str],
    recipient_identities: Optional[dict] = None,
) -> StakeholderResolutionResult:
    """Resolve sender/recipient identities to known stakeholders.

    ARCH:StakeholderModel — identity resolution
    ARCH:TriageGraphReviewGate — uncertain identity handling
    """
    if not sender_identity:
        return StakeholderResolutionResult(
            stakeholder_ids=[],
            confidence=0.0,
            ambiguities=[],
            needs_review=False,
        )

    found_ids: list[uuid.UUID] = []
    ambiguities: list[dict] = []

    # Resolve sender
    sender_matches = _find_stakeholder_by_value(session, sender_identity)
    if len(sender_matches) == 1:
        found_ids.append(sender_matches[0])
    elif len(sender_matches) > 1:
        ambiguities.append({
            "identity_value": sender_identity,
            "role": "sender",
            "candidate_stakeholder_ids": [str(sid) for sid in sender_matches],
            "issue": "Multiple stakeholders match this identity",
        })

    # Resolve recipients if provided
    if recipient_identities:
        for role, addrs in recipient_identities.items():
            if isinstance(addrs, list):
                for addr in addrs:
                    matches = _find_stakeholder_by_value(session, addr)
                    if len(matches) == 1:
                        if matches[0] not in found_ids:
                            found_ids.append(matches[0])
                    elif len(matches) > 1:
                        ambiguities.append({
                            "identity_value": addr,
                            "role": role,
                            "candidate_stakeholder_ids": [str(s) for s in matches],
                            "issue": "Multiple stakeholders match",
                        })

    needs_review = len(ambiguities) > 0
    confidence = 1.0 if found_ids and not ambiguities else (0.5 if found_ids else 0.0)

    return StakeholderResolutionResult(
        stakeholder_ids=found_ids,
        confidence=confidence,
        ambiguities=ambiguities,
        needs_review=needs_review,
        review_reason="Uncertain stakeholder identity — multiple matches" if needs_review else None,
    )


def _find_stakeholder_by_value(
    session: Session, identity_value: str
) -> list[uuid.UUID]:
    """Find stakeholder(s) whose identities match the given value."""
    # Normalize email: extract address from "Name <email>" format
    clean = identity_value.strip()
    if "<" in clean and ">" in clean:
        clean = clean.split("<")[1].split(">")[0].strip()
    clean = clean.lower()

    identities = session.execute(
        select(StakeholderIdentity).where(
            StakeholderIdentity.identity_value == clean
        )
    ).scalars().all()

    return list({si.stakeholder_id for si in identities})


# ── Extraction ───────────────────────────────────────────────────────


class ExtractionResult:
    """Result of action/decision/deadline extraction."""

    def __init__(
        self,
        action_ids: list[uuid.UUID],
        decision_ids: list[uuid.UUID],
        deadline_ids: list[uuid.UUID],
        needs_review: bool,
        review_reasons: list[str],
    ):
        self.action_ids = action_ids
        self.decision_ids = decision_ids
        self.deadline_ids = deadline_ids
        self.needs_review = needs_review
        self.review_reasons = review_reasons


def extract_and_persist(
    session: Session,
    source_record_id: uuid.UUID,
    source_record_type: str,
    project_id: Optional[uuid.UUID],
    actions: list[dict],
    decisions: list[dict],
    deadlines: list[dict],
) -> ExtractionResult:
    """Persist extracted candidate artifacts as interpreted records.

    All extracted items begin in 'pending_review' state.
    Clear extractions may be auto-accepted later; uncertain ones
    require explicit review.

    ARCH:OrchestrationPrinciple.VisibleArtifacts
    ARCH:OrchestrationPrinciple.LowConfidenceReview
    """
    action_ids: list[uuid.UUID] = []
    decision_ids: list[uuid.UUID] = []
    deadline_ids: list[uuid.UUID] = []
    review_reasons: list[str] = []
    needs_review = False

    for action_data in actions:
        confidence = action_data.get("confidence", 0.5)
        review_state = "pending_review"

        if confidence < CONFIDENCE_THRESHOLD_AMBIGUOUS:
            needs_review = True
            review_reasons.append(
                f"Action '{action_data.get('description', '?')[:50]}' has low confidence ({confidence})"
            )

        action = ExtractedAction(
            source_record_id=source_record_id,
            source_record_type=source_record_type,
            linked_project_id=project_id,
            action_text=action_data.get("description", ""),
            proposed_owner=action_data.get("proposed_owner"),
            due_date_signal=action_data.get("due_date_signal"),
            urgency_signal=action_data.get("urgency_signal"),
            review_state=review_state,
        )
        session.add(action)
        session.flush()
        action_ids.append(action.id)

    for decision_data in decisions:
        decision = ExtractedDecision(
            source_record_id=source_record_id,
            source_record_type=source_record_type,
            linked_project_id=project_id,
            decision_text=decision_data.get("description", ""),
            rationale=decision_data.get("rationale"),
            review_state="pending_review",
        )
        session.add(decision)
        session.flush()
        decision_ids.append(decision.id)

    for deadline_data in deadlines:
        deadline = ExtractedDeadlineSignal(
            source_record_id=source_record_id,
            source_record_type=source_record_type,
            linked_project_id=project_id,
            deadline_text=deadline_data.get("description", ""),
            inferred_date=deadline_data.get("inferred_date"),
            confidence=deadline_data.get("confidence", 0.5),
            review_state="pending_review",
        )
        session.add(deadline)
        session.flush()
        deadline_ids.append(deadline.id)

    return ExtractionResult(
        action_ids=action_ids,
        decision_ids=decision_ids,
        deadline_ids=deadline_ids,
        needs_review=needs_review,
        review_reasons=review_reasons,
    )


# ── Classification Persistence ───────────────────────────────────────


def persist_classification(
    session: Session,
    source_record_id: uuid.UUID,
    source_record_type: str,
    result: ClassificationResult,
) -> uuid.UUID:
    """Persist a MessageClassification from a classification result.

    ARCH:OrchestrationPrinciple.VisibleArtifacts
    """
    classification = MessageClassification(
        source_record_id=source_record_id,
        source_record_type=source_record_type,
        selected_project_id=result.project_id,
        candidate_project_ids={
            "candidates": result.candidates
        } if result.candidates else None,
        confidence=result.confidence,
        ambiguity_flag=result.needs_review,
        classification_rationale=result.rationale,
        review_state="pending_review" if result.needs_review else "accepted",
    )
    session.add(classification)
    session.flush()
    return classification.id


# ── LLM-Enhanced Entry Points ────────────────────────────────────────


def classify_project_enhanced(
    session: Session,
    sender_identity: Optional[str],
    subject: Optional[str],
    body_text: Optional[str],
    source_account_label: Optional[str] = None,
) -> ClassificationResult:
    """Classify a message using LLM when available, deterministic otherwise.

    PLAN:WorkstreamI.PackageI8.OrchestrationWiring
    TEST:LLM.Orchestration.TriagePipelineUsesLLMWhenAvailable

    Checks the per-task LLM toggle.  When enabled, calls the async
    smart orchestration function via asyncio.run() which tries LLM
    first and falls back to deterministic on failure.
    """
    from app.inference.config import InferenceSettings

    settings = InferenceSettings()
    if not settings.llm_classification_enabled:
        return classify_project(
            session, sender_identity, subject, body_text, source_account_label
        )

    try:
        from app.inference.orchestration import classify_project_smart

        smart_result = asyncio.run(classify_project_smart(
            session,
            sender_identity,
            subject,
            body_text,
            source_account_label,
        ))

        logger.info(
            "Classification via %s path — confidence=%.2f, needs_review=%s",
            "LLM" if smart_result.used_llm else "deterministic-fallback",
            smart_result.confidence,
            smart_result.needs_review,
        )

        return ClassificationResult(
            project_id=smart_result.project_id,
            confidence=smart_result.confidence,
            rationale=smart_result.rationale,
            candidates=smart_result.candidates,
            needs_review=smart_result.needs_review,
            review_reason=smart_result.review_reason,
        )
    except Exception as exc:
        logger.warning(
            "LLM-enhanced classification failed, using deterministic: %s", exc
        )
        return classify_project(
            session, sender_identity, subject, body_text, source_account_label
        )


def extract_with_llm(
    sender: Optional[str],
    subject: Optional[str],
    body: Optional[str],
    project_name: Optional[str] = None,
    project_objective: Optional[str] = None,
) -> dict:
    """Extract actions/decisions/deadlines using LLM when available.

    PLAN:WorkstreamI.PackageI8.OrchestrationWiring
    TEST:LLM.Extraction.ProducesValidStructuredActions

    Returns a dict with keys 'actions', 'decisions', 'deadlines' suitable
    for passing to extract_and_persist().  When LLM is unavailable or
    disabled, returns empty lists (caller may supply manual extractions).
    """
    from app.inference.config import InferenceSettings

    settings = InferenceSettings()
    if not settings.llm_extraction_enabled:
        return {"actions": [], "decisions": [], "deadlines": []}

    try:
        from app.inference.orchestration import extract_from_message_smart

        result = asyncio.run(extract_from_message_smart(
            sender=sender,
            subject=subject,
            body=body,
            project_name=project_name,
            project_objective=project_objective,
        ))

        logger.info(
            "Extraction via %s path — %d items",
            "LLM" if result.used_llm else "empty-fallback",
            result.total_items,
        )

        return {
            "actions": result.actions,
            "decisions": result.decisions,
            "deadlines": result.deadlines,
        }
    except Exception as exc:
        logger.warning(
            "LLM-enhanced extraction failed, returning empty: %s", exc
        )
        return {"actions": [], "decisions": [], "deadlines": []}

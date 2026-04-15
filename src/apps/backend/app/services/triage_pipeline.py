"""Triage pipeline service — orchestrates classification and extraction for source records.

ARCH:TriageGraph
ARCH:IntakeGraph
PLAN:WorkstreamI.PackageI8.OrchestrationWiring

Loads persisted source records by ID, classifies each against the active
project portfolio (LLM-first when available, deterministic fallback),
extracts actions/decisions/deadlines, and persists all results.

This service bridges the gap between the Intake Graph routing decision
and real triage work.  It is called from the intake graph's triage_handoff
node and from the manual-trigger API endpoint.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy.orm import Session

from app.models.source import CalendarEvent, ConnectedAccount, ImportedSignal, Message
from app.models.portfolio import Project

logger = logging.getLogger(__name__)


# ── Result Contract ──────────────────────────────────────────────────


@dataclass
class TriageRecordResult:
    """Result for a single triaged record."""

    source_record_id: uuid.UUID
    classification_id: Optional[uuid.UUID] = None
    extracted_action_ids: list[uuid.UUID] = field(default_factory=list)
    extracted_decision_ids: list[uuid.UUID] = field(default_factory=list)
    extracted_deadline_ids: list[uuid.UUID] = field(default_factory=list)
    classified_project_id: Optional[uuid.UUID] = None
    classification_confidence: float = 0.0
    needs_review: bool = False
    review_reasons: list[str] = field(default_factory=list)
    error: Optional[str] = None


@dataclass
class TriagePipelineResult:
    """Aggregate result from processing a batch of source records."""

    record_results: list[TriageRecordResult] = field(default_factory=list)
    classification_ids: list[uuid.UUID] = field(default_factory=list)
    extraction_ids: list[uuid.UUID] = field(default_factory=list)
    needs_review: bool = False
    review_reasons: list[str] = field(default_factory=list)
    records_processed: int = 0
    records_skipped: int = 0
    errors: list[str] = field(default_factory=list)


# ── Source Record Loading ────────────────────────────────────────────


def _load_message(session: Session, record_id: uuid.UUID) -> Optional[Message]:
    """Load a Message by ID."""
    return session.get(Message, record_id)


def _load_calendar_event(session: Session, record_id: uuid.UUID) -> Optional[CalendarEvent]:
    """Load a CalendarEvent by ID."""
    return session.get(CalendarEvent, record_id)


def _load_imported_signal(session: Session, record_id: uuid.UUID) -> Optional[ImportedSignal]:
    """Load an ImportedSignal by ID."""
    return session.get(ImportedSignal, record_id)


def _extract_triage_fields(
    record_type: str, record: Message | CalendarEvent | ImportedSignal
) -> dict:
    """Extract sender, subject, body from a source record for triage functions.

    Returns a dict with keys: sender_identity, subject, body_text.
    """
    if isinstance(record, Message):
        return {
            "sender_identity": record.sender_identity,
            "subject": record.subject,
            "body_text": record.body_text,
        }
    elif isinstance(record, CalendarEvent):
        return {
            "sender_identity": None,
            "subject": record.title,
            "body_text": record.description_summary,
        }
    elif isinstance(record, ImportedSignal):
        return {
            "sender_identity": record.source_label,
            "subject": record.signal_type,
            "body_text": record.content,
        }
    return {"sender_identity": None, "subject": None, "body_text": None}


def _get_account_label(
    session: Session, connected_account_id: Optional[uuid.UUID]
) -> Optional[str]:
    """Get the account label for a connected account."""
    if not connected_account_id:
        return None
    account = session.get(ConnectedAccount, connected_account_id)
    return account.account_label if account else None


# ── Pipeline ─────────────────────────────────────────────────────────


def process_triage_batch(
    session: Session,
    source_record_ids: list[uuid.UUID],
    record_type: str,
    connected_account_id: Optional[uuid.UUID] = None,
) -> TriagePipelineResult:
    """Classify and extract from a batch of source records.

    ARCH:TriageGraph
    ARCH:OrchestrationPrinciple.VisibleArtifacts
    ARCH:OrchestrationPrinciple.LowConfidenceReview
    PLAN:WorkstreamI.PackageI8.OrchestrationWiring
    TEST:Triage.Pipeline.EndToEndClassificationAndExtraction

    For each record ID:
    1. Load the source record from DB
    2. Classify against the active project portfolio
    3. Persist the classification
    4. Extract actions/decisions/deadlines
    5. Persist extraction results

    Uses LLM-enhanced functions when toggles are enabled, otherwise
    deterministic.  All results begin in pending_review state.
    """
    from app.graphs.triage import (
        classify_project_enhanced,
        extract_with_llm,
        extract_and_persist,
        persist_classification,
    )

    result = TriagePipelineResult()
    account_label = _get_account_label(session, connected_account_id)

    # Resolve the project name/objective lookup for extraction context
    _project_cache: dict[uuid.UUID, Project] = {}

    for record_id in source_record_ids:
        rec_result = _process_single_record(
            session=session,
            record_id=record_id,
            record_type=record_type,
            account_label=account_label,
            project_cache=_project_cache,
            classify_fn=classify_project_enhanced,
            extract_fn=extract_with_llm,
            persist_classification_fn=persist_classification,
            persist_extraction_fn=extract_and_persist,
        )

        result.record_results.append(rec_result)

        if rec_result.error:
            result.records_skipped += 1
            result.errors.append(rec_result.error)
        else:
            result.records_processed += 1
            if rec_result.classification_id:
                result.classification_ids.append(rec_result.classification_id)
            result.extraction_ids.extend(rec_result.extracted_action_ids)
            result.extraction_ids.extend(rec_result.extracted_decision_ids)
            result.extraction_ids.extend(rec_result.extracted_deadline_ids)

        if rec_result.needs_review:
            result.needs_review = True
            result.review_reasons.extend(rec_result.review_reasons)

    return result


def _process_single_record(
    *,
    session: Session,
    record_id: uuid.UUID,
    record_type: str,
    account_label: Optional[str],
    project_cache: dict[uuid.UUID, Project],
    classify_fn,
    extract_fn,
    persist_classification_fn,
    persist_extraction_fn,
) -> TriageRecordResult:
    """Process a single source record through classification and extraction."""
    rec_result = TriageRecordResult(source_record_id=record_id)

    try:
        # Load the source record
        record = _load_record(session, record_id, record_type)
        if record is None:
            rec_result.error = f"Source record {record_id} not found for type '{record_type}'"
            logger.warning(rec_result.error)
            return rec_result

        # Extract fields for triage
        fields = _extract_triage_fields(record_type, record)

        # ── Classification ──
        classification_result = classify_fn(
            session,
            fields["sender_identity"],
            fields["subject"],
            fields["body_text"],
            account_label,
        )

        classification_id = persist_classification_fn(
            session,
            source_record_id=record_id,
            source_record_type=record_type,
            result=classification_result,
        )
        rec_result.classification_id = classification_id
        rec_result.classified_project_id = classification_result.project_id
        rec_result.classification_confidence = classification_result.confidence

        if classification_result.needs_review:
            rec_result.needs_review = True
            if classification_result.review_reason:
                rec_result.review_reasons.append(classification_result.review_reason)

        # ── Extraction ──
        # Get project context for extraction if we have a classified project
        project_name: Optional[str] = None
        project_objective: Optional[str] = None
        if classification_result.project_id:
            project = project_cache.get(classification_result.project_id)
            if project is None:
                project = session.get(Project, classification_result.project_id)
                if project:
                    project_cache[classification_result.project_id] = project
            if project:
                project_name = project.name
                project_objective = project.objective

        extracted = extract_fn(
            sender=fields["sender_identity"],
            subject=fields["subject"],
            body=fields["body_text"],
            project_name=project_name,
            project_objective=project_objective,
        )

        extraction_result = persist_extraction_fn(
            session,
            source_record_id=record_id,
            source_record_type=record_type,
            project_id=classification_result.project_id,
            actions=extracted.get("actions", []),
            decisions=extracted.get("decisions", []),
            deadlines=extracted.get("deadlines", []),
        )
        rec_result.extracted_action_ids = extraction_result.action_ids
        rec_result.extracted_decision_ids = extraction_result.decision_ids
        rec_result.extracted_deadline_ids = extraction_result.deadline_ids

        if extraction_result.needs_review:
            rec_result.needs_review = True
            rec_result.review_reasons.extend(extraction_result.review_reasons)

    except Exception as exc:
        rec_result.error = f"Triage failed for record {record_id}: {exc}"
        logger.exception(rec_result.error)

    return rec_result


def _load_record(
    session: Session, record_id: uuid.UUID, record_type: str
) -> Optional[Message | CalendarEvent | ImportedSignal]:
    """Load a source record by type."""
    if record_type in ("message", "thread"):
        return _load_message(session, record_id)
    elif record_type == "calendar_event":
        return _load_calendar_event(session, record_id)
    elif record_type == "imported_signal":
        return _load_imported_signal(session, record_id)
    else:
        # Best-effort: try message first, then signal
        msg = _load_message(session, record_id)
        if msg:
            return msg
        return _load_imported_signal(session, record_id)



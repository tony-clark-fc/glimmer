"""Planner and focus-pack generation tests.

TEST:Planner.FocusPack.GeneratesExplainablePriorities
TEST:Planner.FocusPack.PersistsTopActionsAndPressureSignals
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from app.models.portfolio import Project
from app.models.execution import WorkItem, RiskRecord, WaitingOnRecord, BlockerRecord
from app.models.interpretation import ExtractedAction
from app.models.drafting import FocusPack
from app.graphs.planner import (
    generate_focus_pack,
    PriorityItem,
    _score_work_item,
    _score_pending_action,
)


class TestFocusPackGeneration:
    """TEST:Planner.FocusPack.GeneratesExplainablePriorities

    Proves that the planner generates explainable priority outputs
    grounded in current project state.
    """

    def test_empty_state_produces_empty_focus_pack(self, db_session) -> None:
        """No items → empty focus pack with no errors."""
        result = generate_focus_pack(db_session)
        assert result.focus_pack_id is not None
        assert result.priority_items == []
        assert result.top_actions == []
        assert result.reply_debt_summary is None

    def test_work_items_appear_in_focus_pack(self, db_session) -> None:
        """Open work items are scored and included in the focus pack."""
        project = Project(name="Test Project", status="active")
        db_session.add(project)
        db_session.flush()

        wi = WorkItem(
            project_id=project.id,
            title="Finish report",
            status="open",
            due_date=datetime.now(timezone.utc) + timedelta(hours=12),
        )
        db_session.add(wi)
        db_session.flush()

        result = generate_focus_pack(db_session)
        assert len(result.priority_items) >= 1
        assert result.priority_items[0].item_type == "work_item"
        assert result.priority_items[0].title == "Finish report"

    def test_overdue_item_scores_highest(self, db_session) -> None:
        """An overdue work item scores higher than a future one."""
        project = Project(name="Test", status="active")
        db_session.add(project)
        db_session.flush()

        overdue = WorkItem(
            project_id=project.id,
            title="Overdue task",
            status="open",
            due_date=datetime.now(timezone.utc) - timedelta(hours=24),
        )
        future = WorkItem(
            project_id=project.id,
            title="Future task",
            status="open",
            due_date=datetime.now(timezone.utc) + timedelta(days=7),
        )
        db_session.add_all([overdue, future])
        db_session.flush()

        result = generate_focus_pack(db_session)
        assert len(result.priority_items) == 2
        assert result.priority_items[0].title == "Overdue task"
        assert result.priority_items[0].priority_score > result.priority_items[1].priority_score

    def test_priority_items_have_rationale(self, db_session) -> None:
        """Each priority item carries an explanation."""
        project = Project(name="Test", status="active")
        db_session.add(project)
        db_session.flush()

        wi = WorkItem(
            project_id=project.id,
            title="Urgent delivery",
            status="in_progress",
            priority_indicators={"urgency": "high"},
        )
        db_session.add(wi)
        db_session.flush()

        result = generate_focus_pack(db_session)
        assert len(result.priority_items) >= 1
        item = result.priority_items[0]
        assert item.rationale != ""
        assert "high" in item.rationale.lower() or "in-progress" in item.rationale.lower()

    def test_pending_actions_included(self, db_session) -> None:
        """Pending extracted actions appear in priority items."""
        project = Project(name="Test", status="active")
        db_session.add(project)
        db_session.flush()

        action = ExtractedAction(
            source_record_id=uuid.uuid4(),
            source_record_type="message",
            linked_project_id=project.id,
            action_text="Follow up with client",
            urgency_signal="high",
            review_state="pending_review",
        )
        db_session.add(action)
        db_session.flush()

        result = generate_focus_pack(db_session)
        assert len(result.priority_items) >= 1
        action_item = [pi for pi in result.priority_items if pi.item_type == "pending_action"]
        assert len(action_item) == 1
        assert result.reply_debt_summary is not None


class TestFocusPackPersistence:
    """TEST:Planner.FocusPack.PersistsTopActionsAndPressureSignals

    Proves that focus packs are persisted with top actions,
    risk items, waiting-on items, and pressure signals.
    """

    def test_focus_pack_persists(self, db_session) -> None:
        """FocusPack is persisted to the database."""
        result = generate_focus_pack(db_session)
        db_session.flush()

        loaded = db_session.get(FocusPack, result.focus_pack_id)
        assert loaded is not None
        assert loaded.id == result.focus_pack_id

    def test_risk_items_included(self, db_session) -> None:
        """High-risk items appear in the focus pack."""
        project = Project(name="Test", status="active")
        db_session.add(project)
        db_session.flush()

        risk = RiskRecord(
            project_id=project.id,
            summary="Vendor may not deliver on time",
            severity_signal="high",
            status="open",
        )
        db_session.add(risk)
        db_session.flush()

        result = generate_focus_pack(db_session)
        assert len(result.high_risk_items) == 1
        assert result.high_risk_items[0]["severity"] == "high"

    def test_waiting_on_included(self, db_session) -> None:
        """Waiting-on items appear in the focus pack."""
        project = Project(name="Test", status="active")
        db_session.add(project)
        db_session.flush()

        wo = WaitingOnRecord(
            project_id=project.id,
            waiting_on_whom="External vendor",
            description="Waiting for API credentials",
            status="waiting",
        )
        db_session.add(wo)
        db_session.flush()

        result = generate_focus_pack(db_session)
        assert len(result.waiting_on_items) == 1
        assert result.waiting_on_items[0]["waiting_on"] == "External vendor"

    def test_project_filter_works(self, db_session) -> None:
        """Focus pack filters by project_ids when provided."""
        p1 = Project(name="Alpha", status="active")
        p2 = Project(name="Beta", status="active")
        db_session.add_all([p1, p2])
        db_session.flush()

        wi1 = WorkItem(project_id=p1.id, title="Alpha task", status="open")
        wi2 = WorkItem(project_id=p2.id, title="Beta task", status="open")
        db_session.add_all([wi1, wi2])
        db_session.flush()

        result = generate_focus_pack(db_session, project_ids=[p1.id])
        titles = [pi.title for pi in result.priority_items]
        assert "Alpha task" in titles
        assert "Beta task" not in titles


class TestPriorityScoring:
    """Additional priority scoring unit tests."""

    def test_score_work_item_baseline(self, db_session) -> None:
        """Open work item gets baseline score."""
        project = Project(name="Test", status="active")
        db_session.add(project)
        db_session.flush()

        wi = WorkItem(project_id=project.id, title="Test", status="open")
        db_session.add(wi)
        db_session.flush()

        scored = _score_work_item(wi)
        assert scored.priority_score > 0
        assert scored.item_type == "work_item"

    def test_score_pending_action_with_urgency(self, db_session) -> None:
        """High-urgency pending action scores higher."""
        action = ExtractedAction(
            source_record_id=uuid.uuid4(),
            source_record_type="message",
            action_text="Urgent follow-up",
            urgency_signal="high",
            review_state="pending_review",
        )
        db_session.add(action)
        db_session.flush()

        scored = _score_pending_action(action)
        assert scored.priority_score >= 0.6
        assert "high" in scored.rationale.lower()


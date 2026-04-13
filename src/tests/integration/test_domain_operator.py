"""Integration tests for PrimaryOperator domain model.

TEST:Domain.Operator.PersistsWithPreferences
TEST:Domain.Operator.OwnsProjectsAccountsSessions

Proves entity group 1 (Operator context) from ARCH:PrimaryOperatorModel.
"""

from __future__ import annotations

import uuid

from app.models.operator import PrimaryOperator
from app.models.portfolio import Project
from app.models.source import ConnectedAccount
from app.models.channel import ChannelSession


class TestPrimaryOperatorPersistence:
    """Prove PrimaryOperator can be created and persisted with preferences."""

    def test_create_operator_minimal(self, db_session):
        """Operator can be created with just a display name."""
        op = PrimaryOperator(display_name="Tony")
        db_session.add(op)
        db_session.flush()

        assert op.id is not None
        assert op.display_name == "Tony"
        assert op.preferred_timezone is None
        assert op.created_at is not None

    def test_create_operator_with_preferences(self, db_session):
        """Operator persists all preference fields."""
        op = PrimaryOperator(
            display_name="Tony",
            preferred_timezone="Europe/London",
            preferred_working_hours="09:00-18:00 Mon-Fri",
            preferred_language="en-GB",
            tone_preferences="Warm, direct, slightly British-sophisticated",
            channel_preferences={"telegram_enabled": True, "voice_enabled": True},
            summary_preferences={"daily_focus_pack": True, "weekly_review": True},
            escalation_preferences={"interrupt_for_urgent": True, "research_auto_escalate": False},
        )
        db_session.add(op)
        db_session.flush()

        fetched = db_session.get(PrimaryOperator, op.id)
        assert fetched is not None
        assert fetched.preferred_timezone == "Europe/London"
        assert fetched.preferred_working_hours == "09:00-18:00 Mon-Fri"
        assert fetched.preferred_language == "en-GB"
        assert fetched.tone_preferences == "Warm, direct, slightly British-sophisticated"
        assert fetched.channel_preferences["telegram_enabled"] is True
        assert fetched.summary_preferences["daily_focus_pack"] is True
        assert fetched.escalation_preferences["research_auto_escalate"] is False

    def test_operator_update(self, db_session):
        """Operator preferences can be updated."""
        op = PrimaryOperator(display_name="Tony")
        db_session.add(op)
        db_session.flush()

        op.preferred_timezone = "America/New_York"
        db_session.flush()

        fetched = db_session.get(PrimaryOperator, op.id)
        assert fetched.preferred_timezone == "America/New_York"

    def test_multiple_operators_coexist(self, db_session):
        """Multiple operators can exist (even though MVP is single-operator)."""
        op1 = PrimaryOperator(display_name="Tony")
        op2 = PrimaryOperator(display_name="Test Operator")
        db_session.add_all([op1, op2])
        db_session.flush()

        assert op1.id != op2.id


class TestOperatorOwnership:
    """Prove the operator→project/account/session ownership chain."""

    def test_project_has_operator_id(self, db_session):
        """Project can be linked to an operator."""
        op = PrimaryOperator(display_name="Tony")
        db_session.add(op)
        db_session.flush()

        project = Project(name="Alpha", operator_id=op.id)
        db_session.add(project)
        db_session.flush()

        fetched = db_session.get(Project, project.id)
        assert fetched.operator_id == op.id

    def test_project_without_operator_still_works(self, db_session):
        """Projects created without operator_id remain valid (backward compat)."""
        project = Project(name="Legacy Project")
        db_session.add(project)
        db_session.flush()

        assert project.operator_id is None

    def test_connected_account_has_operator_id(self, db_session):
        """ConnectedAccount can be linked to an operator."""
        op = PrimaryOperator(display_name="Tony")
        db_session.add(op)
        db_session.flush()

        account = ConnectedAccount(
            provider_type="google",
            account_label="tony@gmail.com",
            operator_id=op.id,
        )
        db_session.add(account)
        db_session.flush()

        fetched = db_session.get(ConnectedAccount, account.id)
        assert fetched.operator_id == op.id

    def test_connected_account_without_operator_still_works(self, db_session):
        """ConnectedAccount without operator_id remains valid."""
        account = ConnectedAccount(
            provider_type="microsoft_365",
            account_label="tony@company.com",
        )
        db_session.add(account)
        db_session.flush()

        assert account.operator_id is None

    def test_channel_session_has_operator_id(self, db_session):
        """ChannelSession can be linked to an operator."""
        op = PrimaryOperator(display_name="Tony")
        db_session.add(op)
        db_session.flush()

        session = ChannelSession(
            channel_type="telegram",
            operator_id=op.id,
        )
        db_session.add(session)
        db_session.flush()

        fetched = db_session.get(ChannelSession, session.id)
        assert fetched.operator_id == op.id

    def test_channel_session_without_operator_still_works(self, db_session):
        """ChannelSession without operator_id remains valid."""
        session = ChannelSession(channel_type="voice")
        db_session.add(session)
        db_session.flush()

        assert session.operator_id is None

    def test_one_operator_many_projects(self, db_session):
        """One operator can own multiple projects."""
        op = PrimaryOperator(display_name="Tony")
        db_session.add(op)
        db_session.flush()

        p1 = Project(name="Alpha", operator_id=op.id)
        p2 = Project(name="Beta", operator_id=op.id)
        p3 = Project(name="Gamma", operator_id=op.id)
        db_session.add_all([p1, p2, p3])
        db_session.flush()

        from sqlalchemy import select
        stmt = select(Project).where(Project.operator_id == op.id)
        projects = db_session.execute(stmt).scalars().all()
        assert len(projects) == 3

    def test_one_operator_many_accounts(self, db_session):
        """One operator can own multiple connected accounts."""
        op = PrimaryOperator(display_name="Tony")
        db_session.add(op)
        db_session.flush()

        a1 = ConnectedAccount(
            provider_type="google",
            account_label="tony@gmail.com",
            operator_id=op.id,
        )
        a2 = ConnectedAccount(
            provider_type="microsoft_365",
            account_label="tony@company.com",
            operator_id=op.id,
        )
        db_session.add_all([a1, a2])
        db_session.flush()

        from sqlalchemy import select
        stmt = select(ConnectedAccount).where(ConnectedAccount.operator_id == op.id)
        accounts = db_session.execute(stmt).scalars().all()
        assert len(accounts) == 2


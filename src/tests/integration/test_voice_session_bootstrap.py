"""Voice session bootstrap and lifecycle tests — WF1.

TEST:Voice.Session.BootstrapBindsCorrectOperatorAndSession
"""

from __future__ import annotations

import uuid

from app.models.channel import ChannelSession, VoiceSessionState
from app.models.operator import PrimaryOperator
from app.services.voice import bootstrap_voice_session


class TestVoiceSessionBootstrap:
    """TEST:Voice.Session.BootstrapBindsCorrectOperatorAndSession"""

    def test_bootstrap_creates_channel_session(self, db_session) -> None:
        cs, vs = bootstrap_voice_session(db_session)
        assert cs.id is not None
        assert cs.channel_type == "voice"
        assert cs.session_state == "active"
        assert cs.last_interaction_at is not None

    def test_bootstrap_creates_voice_state(self, db_session) -> None:
        cs, vs = bootstrap_voice_session(db_session)
        assert vs.id is not None
        assert vs.channel_session_id == cs.id
        assert vs.session_status == "in_progress"

    def test_bootstrap_binds_operator(self, db_session) -> None:
        op = PrimaryOperator(
            display_name="Test Operator",
        )
        db_session.add(op)
        db_session.flush()

        cs, vs = bootstrap_voice_session(db_session, operator_id=op.id)
        assert cs.operator_id == op.id

    def test_bootstrap_preserves_project_context(self, db_session) -> None:
        project_ids = [uuid.uuid4(), uuid.uuid4()]
        cs, vs = bootstrap_voice_session(
            db_session, project_context_ids=project_ids
        )
        state_data = vs.state_data or {}
        assert len(state_data.get("referenced_project_ids", [])) == 2

    def test_bootstrap_without_operator_succeeds(self, db_session) -> None:
        cs, vs = bootstrap_voice_session(db_session)
        assert cs.operator_id is None
        assert vs.session_status == "in_progress"

    def test_bootstrap_channel_identity_has_voice_prefix(self, db_session) -> None:
        cs, vs = bootstrap_voice_session(db_session)
        assert cs.channel_identity.startswith("voice_")

    def test_bootstrap_voice_state_linked_to_channel_session(self, db_session) -> None:
        cs, vs = bootstrap_voice_session(db_session)
        fetched_vs = db_session.get(VoiceSessionState, vs.id)
        fetched_cs = db_session.get(ChannelSession, cs.id)
        assert fetched_vs is not None
        assert fetched_cs is not None
        assert fetched_vs.channel_session_id == fetched_cs.id



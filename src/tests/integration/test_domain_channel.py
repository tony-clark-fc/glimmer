"""Channel-session continuity persistence tests.

TEST:Domain.ChannelSessions.TelegramAndVoiceStatePersist
"""

from __future__ import annotations

from datetime import datetime, timezone

from app.models.portfolio import Project
from app.models.channel import (
    ChannelSession,
    TelegramConversationState,
    VoiceSessionState,
)


class TestChannelSessionPersistence:
    """TEST:Domain.ChannelSessions.TelegramAndVoiceStatePersist"""

    def test_channel_session_persists(self, db_session) -> None:
        session = ChannelSession(
            channel_type="telegram",
            channel_identity="chat_12345",
            session_state="active",
            last_interaction_at=datetime.now(timezone.utc),
        )
        db_session.add(session)
        db_session.flush()

        fetched = db_session.get(ChannelSession, session.id)
        assert fetched is not None
        assert fetched.channel_type == "telegram"
        assert fetched.session_state == "active"

    def test_telegram_state_persists(self, db_session) -> None:
        project = Project(name="TG Test Project")
        db_session.add(project)
        db_session.flush()

        session = ChannelSession(
            channel_type="telegram",
            channel_identity="chat_67890",
        )
        db_session.add(session)
        db_session.flush()

        tg_state = TelegramConversationState(
            channel_session_id=session.id,
            telegram_chat_id="67890",
            current_topic="Q2 budget discussion",
            last_referenced_project_id=project.id,
            pending_clarification="Did you mean the revised budget?",
            temporary_reply_mode="concise",
            state_data={"last_message_id": 42},
        )
        db_session.add(tg_state)
        db_session.flush()

        fetched = db_session.get(TelegramConversationState, tg_state.id)
        assert fetched is not None
        assert fetched.telegram_chat_id == "67890"
        assert fetched.current_topic == "Q2 budget discussion"
        assert fetched.last_referenced_project_id == project.id
        assert fetched.pending_clarification is not None
        assert fetched.state_data["last_message_id"] == 42

    def test_voice_session_state_persists(self, db_session) -> None:
        session = ChannelSession(
            channel_type="voice",
            channel_identity="voice_session_abc",
        )
        db_session.add(session)
        db_session.flush()

        voice = VoiceSessionState(
            channel_session_id=session.id,
            transcript_content="Hey Glimmer, what's my top priority today?",
            summary_content="Operator asked about top priority",
            extracted_action_ids={"actions": ["action-id-1"]},
            session_status="in_progress",
        )
        db_session.add(voice)
        db_session.flush()

        fetched = db_session.get(VoiceSessionState, voice.id)
        assert fetched is not None
        assert fetched.session_status == "in_progress"
        assert "top priority" in fetched.transcript_content

    def test_voice_session_completion(self, db_session) -> None:
        session = ChannelSession(
            channel_type="voice",
            channel_identity="voice_session_xyz",
        )
        db_session.add(session)
        db_session.flush()

        voice = VoiceSessionState(
            channel_session_id=session.id,
            session_status="in_progress",
        )
        db_session.add(voice)
        db_session.flush()

        voice.session_status = "completed"
        voice.ended_at = datetime.now(timezone.utc)
        voice.summary_content = "Session concluded with 2 actions extracted."
        db_session.flush()

        fetched = db_session.get(VoiceSessionState, voice.id)
        assert fetched.session_status == "completed"
        assert fetched.ended_at is not None

    def test_web_channel_session(self, db_session) -> None:
        """Web session type also persists."""
        session = ChannelSession(
            channel_type="web",
            session_state="active",
        )
        db_session.add(session)
        db_session.flush()

        fetched = db_session.get(ChannelSession, session.id)
        assert fetched.channel_type == "web"


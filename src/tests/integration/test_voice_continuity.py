"""Voice session continuity tests — WF3.

TEST:Voice.Session.ContinuityPreservedWithinSession
TEST:ChannelSession.SummariesPersistWithTraceableOrigin
"""

from __future__ import annotations

import uuid

from app.models.channel import ChannelSession, VoiceSessionState
from app.services.voice import (
    bootstrap_voice_session,
    update_session_context,
    create_session_summary,
)


class TestVoiceContinuity:
    """TEST:Voice.Session.ContinuityPreservedWithinSession"""

    def test_update_sets_current_topic(self, db_session) -> None:
        cs, vs = bootstrap_voice_session(db_session)
        updated = update_session_context(
            db_session,
            voice_state_id=vs.id,
            current_topic="project deadlines",
        )
        state_data = updated.state_data or {}
        assert state_data["current_topic"] == "project deadlines"

    def test_update_preserves_recent_topics_bounded(self, db_session) -> None:
        cs, vs = bootstrap_voice_session(db_session)
        for i in range(8):
            update_session_context(
                db_session,
                voice_state_id=vs.id,
                current_topic=f"topic_{i}",
            )
        state_data = vs.state_data or {}
        recent = state_data.get("recent_topics", [])
        # Should be capped at MAX_RECENT_TOPICS (5)
        assert len(recent) == 5
        assert recent[-1] == "topic_7"

    def test_update_merges_referenced_projects(self, db_session) -> None:
        cs, vs = bootstrap_voice_session(db_session)
        p1, p2, p3 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()

        update_session_context(
            db_session,
            voice_state_id=vs.id,
            referenced_project_ids=[p1, p2],
        )
        update_session_context(
            db_session,
            voice_state_id=vs.id,
            referenced_project_ids=[p2, p3],
        )

        state_data = vs.state_data or {}
        refs = state_data.get("referenced_project_ids", [])
        # p1, p2, p3 — all three should be present (set merge)
        assert len(refs) == 3

    def test_update_caps_unresolved_prompts(self, db_session) -> None:
        cs, vs = bootstrap_voice_session(db_session)
        update_session_context(
            db_session,
            voice_state_id=vs.id,
            unresolved_prompts=[f"prompt_{i}" for i in range(15)],
        )
        state_data = vs.state_data or {}
        prompts = state_data.get("unresolved_prompts", [])
        assert len(prompts) == 10  # MAX_UNRESOLVED_PROMPTS

    def test_update_increments_utterance_count(self, db_session) -> None:
        cs, vs = bootstrap_voice_session(db_session)
        update_session_context(db_session, voice_state_id=vs.id)
        update_session_context(db_session, voice_state_id=vs.id)
        update_session_context(db_session, voice_state_id=vs.id)

        state_data = vs.state_data or {}
        # Initial is 0, each call adds 1
        assert state_data.get("utterance_count", 0) == 3

    def test_nonexistent_session_raises(self, db_session) -> None:
        import pytest
        with pytest.raises(ValueError, match="not found"):
            update_session_context(
                db_session,
                voice_state_id=uuid.uuid4(),
            )


class TestSessionSummary:
    """TEST:ChannelSession.SummariesPersistWithTraceableOrigin"""

    def test_summary_creates_content(self, db_session) -> None:
        cs, vs = bootstrap_voice_session(db_session)
        update_session_context(
            db_session,
            voice_state_id=vs.id,
            current_topic="project review",
        )
        result = create_session_summary(db_session, voice_state_id=vs.id)
        assert result.summary_content is not None
        assert "project review" in result.summary_content

    def test_summary_marks_session_completed(self, db_session) -> None:
        cs, vs = bootstrap_voice_session(db_session)
        result = create_session_summary(db_session, voice_state_id=vs.id)
        assert result.session_status == "completed"
        assert result.ended_at is not None

    def test_summary_updates_channel_session(self, db_session) -> None:
        cs, vs = bootstrap_voice_session(db_session)
        create_session_summary(db_session, voice_state_id=vs.id)
        refreshed_cs = db_session.get(ChannelSession, cs.id)
        assert refreshed_cs.session_state == "completed"

    def test_summary_includes_utterance_count(self, db_session) -> None:
        cs, vs = bootstrap_voice_session(db_session)
        for _ in range(3):
            update_session_context(db_session, voice_state_id=vs.id)
        result = create_session_summary(db_session, voice_state_id=vs.id)
        assert "3" in result.summary_content

    def test_summary_includes_project_references(self, db_session) -> None:
        cs, vs = bootstrap_voice_session(db_session)
        update_session_context(
            db_session,
            voice_state_id=vs.id,
            referenced_project_ids=[uuid.uuid4(), uuid.uuid4()],
        )
        result = create_session_summary(db_session, voice_state_id=vs.id)
        assert "2 project" in result.summary_content


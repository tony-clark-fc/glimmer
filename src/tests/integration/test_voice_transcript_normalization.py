"""Voice transcript normalization tests — WF2.

TEST:Voice.Session.TranscriptBecomesStructuredSignal
"""

from __future__ import annotations

import uuid

from app.models.channel import ChannelSession, VoiceSessionState
from app.models.source import ImportedSignal
from app.services.voice import (
    bootstrap_voice_session,
    normalize_utterances,
)


class TestTranscriptNormalization:
    """TEST:Voice.Session.TranscriptBecomesStructuredSignal"""

    def test_utterance_creates_imported_signal(self, db_session) -> None:
        cs, vs = bootstrap_voice_session(db_session)
        signal_ids = normalize_utterances(
            db_session,
            channel_session_id=cs.id,
            transcript_segments=[{"text": "What's my top priority today?"}],
        )
        assert len(signal_ids) == 1
        signal = db_session.get(ImportedSignal, signal_ids[0])
        assert signal is not None
        assert signal.signal_type == "voice_transcript"
        assert signal.content == "What's my top priority today?"

    def test_signal_has_voice_provenance(self, db_session) -> None:
        cs, vs = bootstrap_voice_session(db_session)
        signal_ids = normalize_utterances(
            db_session,
            channel_session_id=cs.id,
            transcript_segments=[{"text": "Check project Alpha status"}],
        )
        signal = db_session.get(ImportedSignal, signal_ids[0])
        assert signal.source_label == f"voice_session:{cs.id}"
        assert signal.raw_metadata is not None
        assert signal.raw_metadata["channel_session_id"] == str(cs.id)

    def test_multiple_segments_create_multiple_signals(self, db_session) -> None:
        cs, vs = bootstrap_voice_session(db_session)
        signal_ids = normalize_utterances(
            db_session,
            channel_session_id=cs.id,
            transcript_segments=[
                {"text": "First thing"},
                {"text": "Second thing"},
                {"text": "Third thing"},
            ],
        )
        assert len(signal_ids) == 3

    def test_empty_text_is_skipped(self, db_session) -> None:
        cs, vs = bootstrap_voice_session(db_session)
        signal_ids = normalize_utterances(
            db_session,
            channel_session_id=cs.id,
            transcript_segments=[
                {"text": "Real utterance"},
                {"text": ""},
                {"text": "   "},
            ],
        )
        assert len(signal_ids) == 1

    def test_utterance_index_preserved_in_metadata(self, db_session) -> None:
        cs, vs = bootstrap_voice_session(db_session)
        signal_ids = normalize_utterances(
            db_session,
            channel_session_id=cs.id,
            transcript_segments=[
                {"text": "First", "index": 0},
                {"text": "Second", "index": 1},
            ],
        )
        sig0 = db_session.get(ImportedSignal, signal_ids[0])
        sig1 = db_session.get(ImportedSignal, signal_ids[1])
        assert sig0.raw_metadata["utterance_index"] == 0
        assert sig1.raw_metadata["utterance_index"] == 1

    def test_timestamp_preserved_in_metadata(self, db_session) -> None:
        cs, vs = bootstrap_voice_session(db_session)
        signal_ids = normalize_utterances(
            db_session,
            channel_session_id=cs.id,
            transcript_segments=[
                {"text": "Timed utterance", "timestamp": "2026-04-13T10:00:00Z"},
            ],
        )
        signal = db_session.get(ImportedSignal, signal_ids[0])
        assert signal.raw_metadata["timestamp"] == "2026-04-13T10:00:00Z"


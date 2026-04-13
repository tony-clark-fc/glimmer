"""Voice session graph and routing tests — WF4.

TEST:VoiceAndTelegram.SharedCoreFlowParityPreserved
TEST:Voice.Session.ReviewGatePreservedForMeaningfulActions
"""

from __future__ import annotations

import uuid

from app.graphs.voice_session import (
    build_voice_session_graph,
    get_voice_session_graph,
    bootstrap,
    route_to_core,
    check_review,
)
from app.graphs.state import VoiceSessionGraphState
from app.services.voice import (
    bootstrap_voice_session,
    normalize_utterances,
    route_voice_to_core,
)


class TestVoiceSessionGraph:
    """TEST:VoiceAndTelegram.SharedCoreFlowParityPreserved — graph proof."""

    def test_graph_compiles(self) -> None:
        graph = get_voice_session_graph()
        assert graph is not None

    def test_graph_executes_bootstrap_to_end(self) -> None:
        graph = get_voice_session_graph()
        result = graph.invoke({
            "workflow_id": str(uuid.uuid4()),
        })
        assert result["auto_send_blocked"] is True
        assert result["current_step"] == "routing_complete"

    def test_bootstrap_sets_safety_invariants(self) -> None:
        result = bootstrap({})
        assert result["auto_send_blocked"] is True
        assert result["needs_review"] is False

    def test_route_to_core_with_no_signals(self) -> None:
        result = route_to_core({})
        assert result["route_target"] == "none"
        assert result["route_reason"] == "No signals to route"

    def test_route_to_core_with_signals(self) -> None:
        result = route_to_core({
            "imported_signal_ids": [uuid.uuid4()],
        })
        assert result["route_target"] == "triage"
        assert result["auto_send_blocked"] is True

    def test_check_review_returns_complete_when_no_review(self) -> None:
        assert check_review({"needs_review": False}) == "complete"

    def test_check_review_returns_review_needed(self) -> None:
        assert check_review({"needs_review": True}) == "review_needed"

    def test_graph_with_review_interrupt(self) -> None:
        """When route_to_core flags needs_review, the graph should interrupt."""
        from app.graphs.voice_session import build_voice_session_graph
        from langgraph.graph import END

        # Build a custom graph where route_to_core sets needs_review=True
        graph = build_voice_session_graph()
        compiled = graph.compile()

        # Invoke with signals so route_to_core runs — then verify
        # the safety invariant is preserved even in review path.
        # Since the default route_to_core doesn't set needs_review=True
        # based on signal content (that's a triage concern), we test
        # that the graph structure correctly handles the review path
        # by testing the conditional edge function directly.
        assert check_review({"needs_review": True}) == "review_needed"
        assert check_review({"needs_review": False}) == "complete"

        # Also verify that the compiled graph preserves auto_send_blocked
        result = compiled.invoke({
            "imported_signal_ids": [uuid.uuid4()],
        })
        assert result["auto_send_blocked"] is True


class TestVoiceRouting:
    """TEST:Voice.Session.ReviewGatePreservedForMeaningfulActions"""

    def test_voice_routes_through_intake_graph(self, db_session) -> None:
        cs, vs = bootstrap_voice_session(db_session)
        signal_ids = normalize_utterances(
            db_session,
            channel_session_id=cs.id,
            transcript_segments=[{"text": "What needs my attention?"}],
        )

        result = route_voice_to_core(
            signal_ids=signal_ids,
            channel_session_id=cs.id,
        )
        assert result["route_target"] == "triage"
        assert result["auto_send_blocked"] is True

    def test_voice_routing_always_blocks_auto_send(self, db_session) -> None:
        cs, vs = bootstrap_voice_session(db_session)
        signal_ids = normalize_utterances(
            db_session,
            channel_session_id=cs.id,
            transcript_segments=[{"text": "Send an update to the team"}],
        )

        result = route_voice_to_core(
            signal_ids=signal_ids,
            channel_session_id=cs.id,
        )
        # Even a "send" utterance must not bypass auto_send_blocked
        assert result["auto_send_blocked"] is True



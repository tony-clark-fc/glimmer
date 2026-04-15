"""Tests for E16 — Cross-surface "Ask Glimmer" contextual interaction.

PLAN:WorkstreamE.PackageE16.ContextualAskGlimmer
TEST:UI.AskGlimmer.AffordanceVisibleOnDataElements
TEST:UI.AskGlimmer.ResponseRespectsReviewGates

Proves the contextual Ask Glimmer API:
1. Returns a response with reply and review flags
2. Validates input (empty question, missing fields)
3. Respects review-gate discipline (review_required flag)
4. Handles inference fallback gracefully
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture()
def client():
    """Create a test client."""
    app = create_app()
    with TestClient(app) as c:
        yield c


def _mock_contextual_ask_result(**overrides):
    """Build a mock SmartContextualAskResult-like object."""
    from dataclasses import dataclass

    @dataclass
    class _MockResult:
        used_llm: bool = False
        fallback_reason: str | None = None
        reply_content: str = "This project is on track with 3 open items."
        review_required: bool = False
        review_reason: str | None = None
        inference_latency_ms: float = 0.0

    defaults = {
        "reply_content": "This project is on track with 3 open items.",
        "review_required": False,
        "review_reason": None,
    }
    defaults.update(overrides)
    return _MockResult(**defaults)


def _mock_review_required_result():
    """Build a mock result that implies external action."""
    return _mock_contextual_ask_result(
        reply_content="I can draft a follow-up email to Alice about the timeline.",
        review_required=True,
        review_reason="Response implies an externally meaningful action that requires operator approval.",
    )


_MOCK_TARGET = "app.api.ask.contextual_ask_smart"


# ── Basic endpoint behavior ──────────────────────────────────────────


class TestContextualAskEndpoint:
    """Prove the /ask/contextual endpoint works correctly."""

    @patch(_MOCK_TARGET, new_callable=AsyncMock, return_value=_mock_contextual_ask_result())
    def test_returns_200_with_reply(self, mock_ask, client: TestClient):
        """A valid request returns 200 with a reply."""
        resp = client.post(
            "/ask/contextual",
            json={
                "element_type": "project",
                "element_id": "proj-123",
                "element_context": {"name": "Phoenix", "status": "active"},
                "surface": "portfolio",
                "question": "What is the status of this project?",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "reply" in data
        assert len(data["reply"]) > 0

    @patch(_MOCK_TARGET, new_callable=AsyncMock, return_value=_mock_contextual_ask_result())
    def test_response_includes_review_fields(self, mock_ask, client: TestClient):
        """Response includes review_required and used_llm fields."""
        resp = client.post(
            "/ask/contextual",
            json={
                "element_type": "risk",
                "element_id": "risk-456",
                "element_context": {"summary": "Budget overrun risk"},
                "surface": "today",
                "question": "How serious is this risk?",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "review_required" in data
        assert "used_llm" in data
        assert isinstance(data["review_required"], bool)

    @patch(_MOCK_TARGET, new_callable=AsyncMock, return_value=_mock_contextual_ask_result())
    def test_passes_context_to_orchestration(self, mock_ask, client: TestClient):
        """Element context is passed through to the orchestration function."""
        client.post(
            "/ask/contextual",
            json={
                "element_type": "blocker",
                "element_id": "blk-789",
                "element_context": {"summary": "Missing specs from vendor"},
                "surface": "project",
                "question": "When can we resolve this?",
            },
        )
        mock_ask.assert_called_once()
        call_kwargs = mock_ask.call_args[1]
        assert call_kwargs["element_type"] == "blocker"
        assert call_kwargs["element_id"] == "blk-789"
        assert call_kwargs["surface"] == "project"
        assert "Missing specs" in call_kwargs["element_context"]["summary"]


# ── Review-gate compliance ────────────────────────────────────────────


class TestReviewGateCompliance:
    """Prove that review_required flag is correctly propagated."""

    @patch(_MOCK_TARGET, new_callable=AsyncMock, return_value=_mock_review_required_result())
    def test_review_required_flag_propagated(self, mock_ask, client: TestClient):
        """When orchestration flags review_required, it appears in the response."""
        resp = client.post(
            "/ask/contextual",
            json={
                "element_type": "draft",
                "element_id": "draft-001",
                "element_context": {"body": "Hi Alice..."},
                "surface": "drafts",
                "question": "Can you draft a follow-up to this?",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["review_required"] is True
        assert data["review_reason"] is not None
        assert "approval" in data["review_reason"].lower() or "externally" in data["review_reason"].lower()

    @patch(_MOCK_TARGET, new_callable=AsyncMock, return_value=_mock_contextual_ask_result())
    def test_informational_response_not_review_flagged(self, mock_ask, client: TestClient):
        """Informational responses do NOT have review_required."""
        resp = client.post(
            "/ask/contextual",
            json={
                "element_type": "project",
                "element_id": "proj-100",
                "element_context": {"name": "Test"},
                "surface": "portfolio",
                "question": "Tell me about this project",
            },
        )
        assert resp.status_code == 200
        assert resp.json()["review_required"] is False


# ── Validation ────────────────────────────────────────────────────────


class TestValidation:
    """Prove input validation works correctly."""

    def test_empty_question_rejected(self, client: TestClient):
        """Empty question is rejected with 422."""
        resp = client.post(
            "/ask/contextual",
            json={
                "element_type": "project",
                "element_id": "proj-1",
                "element_context": {},
                "surface": "today",
                "question": "",
            },
        )
        assert resp.status_code == 422

    def test_whitespace_only_question_rejected(self, client: TestClient):
        """Whitespace-only question is rejected."""
        resp = client.post(
            "/ask/contextual",
            json={
                "element_type": "project",
                "element_id": "proj-1",
                "element_context": {},
                "surface": "today",
                "question": "   \n\t  ",
            },
        )
        assert resp.status_code == 422

    def test_empty_element_type_rejected(self, client: TestClient):
        """Empty element_type is rejected."""
        resp = client.post(
            "/ask/contextual",
            json={
                "element_type": "",
                "element_id": "proj-1",
                "element_context": {},
                "surface": "today",
                "question": "What is this?",
            },
        )
        assert resp.status_code == 422

    def test_empty_surface_rejected(self, client: TestClient):
        """Empty surface is rejected."""
        resp = client.post(
            "/ask/contextual",
            json={
                "element_type": "project",
                "element_id": "proj-1",
                "element_context": {},
                "surface": "",
                "question": "What is this?",
            },
        )
        assert resp.status_code == 422

    def test_missing_required_fields(self, client: TestClient):
        """Missing required fields return 422."""
        resp = client.post(
            "/ask/contextual",
            json={"question": "What is this?"},
        )
        assert resp.status_code == 422


# ── Fallback behavior ─────────────────────────────────────────────────


class TestFallbackBehavior:
    """Prove fallback works when LLM is unavailable."""

    @patch(
        _MOCK_TARGET,
        new_callable=AsyncMock,
        return_value=_mock_contextual_ask_result(
            used_llm=False,
            fallback_reason="Inference unavailable",
            reply_content="I'd like to help with your question about this project, but my reasoning engine isn't available right now. Please try again shortly.",
        ),
    )
    def test_fallback_returns_graceful_response(self, mock_ask, client: TestClient):
        """When LLM is unavailable, a graceful fallback response is returned."""
        resp = client.post(
            "/ask/contextual",
            json={
                "element_type": "project",
                "element_id": "proj-1",
                "element_context": {"name": "Test"},
                "surface": "portfolio",
                "question": "What is the status?",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["used_llm"] is False
        assert len(data["reply"]) > 0
        assert data["review_required"] is False


# ── Various element types ─────────────────────────────────────────────


class TestVariousElementTypes:
    """Prove the endpoint handles different element types."""

    @pytest.mark.parametrize(
        "element_type,surface",
        [
            ("project", "portfolio"),
            ("action_item", "today"),
            ("risk", "today"),
            ("waiting_on", "today"),
            ("classification", "triage"),
            ("extracted_action", "triage"),
            ("draft", "drafts"),
            ("blocker", "project"),
            ("work_item", "project"),
            ("pending_action", "project"),
            ("classification", "review"),
        ],
    )
    @patch(_MOCK_TARGET, new_callable=AsyncMock, return_value=_mock_contextual_ask_result())
    def test_accepts_various_element_types(
        self, mock_ask, element_type: str, surface: str, client: TestClient,
    ):
        """The endpoint accepts all expected element types across surfaces."""
        resp = client.post(
            "/ask/contextual",
            json={
                "element_type": element_type,
                "element_id": f"{element_type}-test-1",
                "element_context": {"label": "Test element"},
                "surface": surface,
                "question": f"Tell me about this {element_type}",
            },
        )
        assert resp.status_code == 200
        assert len(resp.json()["reply"]) > 0

    @patch(_MOCK_TARGET, new_callable=AsyncMock, return_value=_mock_contextual_ask_result())
    def test_empty_element_context_accepted(self, mock_ask, client: TestClient):
        """Empty element_context dict is accepted (optional metadata)."""
        resp = client.post(
            "/ask/contextual",
            json={
                "element_type": "project",
                "element_id": "proj-1",
                "element_context": {},
                "surface": "portfolio",
                "question": "What is this?",
            },
        )
        assert resp.status_code == 200


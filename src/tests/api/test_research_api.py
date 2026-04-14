"""Tests for the research and expert advice API routes.

TEST:ExpertAdvice.Routing.EscalationDistinguishesResearchFromAdvice
TEST:Research.Output.ResultsReenterWorkflowSafely
TEST:ExpertAdvice.Output.ResponseEntersAsInterpretedCandidate
PLAN:WorkstreamH.PackageH5.WorkspaceVisibility
"""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from app.db import get_session
from app.models.research import (
    ExpertAdviceExchange,
    ResearchFinding,
    ResearchRun,
    ResearchSourceReference,
    ResearchSummaryArtifact,
)


# ── Helpers ───────────────────────────────────────────────────────


def _create_research_run(*, with_summary: bool = False, with_findings: int = 0, with_sources: int = 0) -> ResearchRun:
    """Create a research run in the test database with optional children."""
    db = get_session()
    try:
        run = ResearchRun(
            invocation_origin="operator_request",
            research_query="Test research query for H5 workspace visibility",
            status="completed",
            document_name="Test Doc",
        )
        db.add(run)
        db.flush()

        for i in range(with_findings):
            db.add(ResearchFinding(
                research_run_id=run.id,
                finding_type="evidence_point",
                content=f"Finding #{i + 1}",
                ordering=i,
            ))

        for i in range(with_sources):
            db.add(ResearchSourceReference(
                research_run_id=run.id,
                source_url=f"https://example.com/source-{i + 1}",
                source_title=f"Source {i + 1}",
            ))

        if with_summary:
            db.add(ResearchSummaryArtifact(
                research_run_id=run.id,
                summary_text="This is the research summary.",
                review_state="pending_review",
            ))

        db.commit()
        db.refresh(run)
        return run
    finally:
        db.close()


def _create_exchange(*, review_state: str = "pending_review") -> ExpertAdviceExchange:
    """Create an expert advice exchange in the test database."""
    db = get_session()
    try:
        exchange = ExpertAdviceExchange(
            invocation_origin="operator_request",
            prompt="What is the best approach to X?",
            gemini_mode="Pro",
            response_text="The best approach is Y.",
            status="completed",
            review_state=review_state,
            duration_ms=1200,
        )
        db.add(exchange)
        db.commit()
        db.refresh(exchange)
        return exchange
    finally:
        db.close()


# ── Routing Preview Tests ─────────────────────────────────────────────


class TestResearchRoutingPreview:
    """TEST:ExpertAdvice.Routing.EscalationDistinguishesResearchFromAdvice"""

    def test_preview_routes_simple_question_to_advice(self, client: TestClient) -> None:
        resp = client.post(
            "/research/preview-routing",
            json={"prompt": "What is the capital of Australia?"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["determined_mode"] == "advice"

    def test_preview_routes_research_keywords_to_research(self, client: TestClient) -> None:
        resp = client.post(
            "/research/preview-routing",
            json={
                "prompt": "Research and investigate the comprehensive literature on soil carbon benchmarks",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["determined_mode"] == "research"

    def test_preview_respects_explicit_mode(self, client: TestClient) -> None:
        resp = client.post(
            "/research/preview-routing",
            json={
                "prompt": "Quick question",
                "mode": "research",
            },
        )
        assert resp.status_code == 200
        assert resp.json()["determined_mode"] == "research"

    def test_preview_explicit_advice_overrides_keywords(self, client: TestClient) -> None:
        resp = client.post(
            "/research/preview-routing",
            json={
                "prompt": "Research and investigate comprehensively",
                "mode": "advice",
            },
        )
        assert resp.status_code == 200
        assert resp.json()["determined_mode"] == "advice"


# ── Research Runs List Tests ──────────────────────────────────────────


class TestResearchRunsAPI:
    def test_list_runs(self, client: TestClient) -> None:
        resp = client.get("/research/runs")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_run_not_found(self, client: TestClient) -> None:
        resp = client.get(
            "/research/runs/00000000-0000-0000-0000-000000000000"
        )
        assert resp.status_code == 404

    def test_list_runs_includes_enriched_fields(self, client: TestClient) -> None:
        """List response includes summary_review_state, findings_count, sources_count."""
        run = _create_research_run(with_summary=True, with_findings=3, with_sources=2)
        resp = client.get("/research/runs")
        assert resp.status_code == 200
        data = resp.json()
        matching = [r for r in data if r["id"] == str(run.id)]
        assert len(matching) == 1
        item = matching[0]
        assert item["findings_count"] == 3
        assert item["sources_count"] == 2
        assert item["summary_review_state"] == "pending_review"

    def test_run_detail_includes_findings_and_sources(self, client: TestClient) -> None:
        """GET /runs/{id} returns findings, sources, and summary."""
        run = _create_research_run(with_summary=True, with_findings=2, with_sources=1)
        resp = client.get(f"/research/runs/{run.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["findings"]) == 2
        assert len(data["sources"]) == 1
        assert data["summary"] is not None
        assert data["summary"]["review_state"] == "pending_review"
        assert data["summary"]["summary_text"] == "This is the research summary."

    def test_run_detail_without_summary(self, client: TestClient) -> None:
        """Run detail gracefully handles missing summary."""
        run = _create_research_run(with_summary=False)
        resp = client.get(f"/research/runs/{run.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["summary"] is None
        assert data["findings"] == []
        assert data["sources"] == []


# ── Research Summary Review Tests ─────────────────────────────────────


class TestResearchSummaryReview:
    """TEST:Research.Output.ResultsReenterWorkflowSafely"""

    def test_accept_summary(self, client: TestClient) -> None:
        """Accepting a research summary transitions review_state to 'accepted'."""
        run = _create_research_run(with_summary=True)
        resp = client.patch(
            f"/research/runs/{run.id}/summary/review",
            json={"action": "accepted"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["review_state"] == "accepted"

    def test_reject_summary(self, client: TestClient) -> None:
        """Rejecting a research summary transitions review_state to 'rejected'."""
        run = _create_research_run(with_summary=True)
        resp = client.patch(
            f"/research/runs/{run.id}/summary/review",
            json={"action": "rejected"},
        )
        assert resp.status_code == 200
        assert resp.json()["review_state"] == "rejected"

    def test_invalid_review_action(self, client: TestClient) -> None:
        """Invalid action returns 400."""
        run = _create_research_run(with_summary=True)
        resp = client.patch(
            f"/research/runs/{run.id}/summary/review",
            json={"action": "maybe"},
        )
        assert resp.status_code == 400

    def test_review_nonexistent_run(self, client: TestClient) -> None:
        """Reviewing a nonexistent run returns 404."""
        resp = client.patch(
            "/research/runs/00000000-0000-0000-0000-000000000000/summary/review",
            json={"action": "accepted"},
        )
        assert resp.status_code == 404

    def test_review_run_without_summary(self, client: TestClient) -> None:
        """Reviewing a run with no summary returns 404."""
        run = _create_research_run(with_summary=False)
        resp = client.patch(
            f"/research/runs/{run.id}/summary/review",
            json={"action": "accepted"},
        )
        assert resp.status_code == 404

    def test_accepted_summary_reflected_in_list(self, client: TestClient) -> None:
        """After accepting, the list view shows updated review_state."""
        run = _create_research_run(with_summary=True)
        client.patch(
            f"/research/runs/{run.id}/summary/review",
            json={"action": "accepted"},
        )
        resp = client.get("/research/runs")
        matching = [r for r in resp.json() if r["id"] == str(run.id)]
        assert matching[0]["summary_review_state"] == "accepted"


# ── Expert Advice Exchanges List Tests ────────────────────────────────


class TestExchangesAPI:
    def test_list_exchanges(self, client: TestClient) -> None:
        resp = client.get("/research/exchanges")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_exchange_not_found(self, client: TestClient) -> None:
        resp = client.get(
            "/research/exchanges/00000000-0000-0000-0000-000000000000"
        )
        assert resp.status_code == 404

    def test_exchange_includes_response_and_review_state(self, client: TestClient) -> None:
        """Exchange response includes expected fields."""
        exchange = _create_exchange()
        resp = client.get(f"/research/exchanges/{exchange.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["response_text"] == "The best approach is Y."
        assert data["review_state"] == "pending_review"
        assert data["gemini_mode"] == "Pro"
        assert data["duration_ms"] == 1200


# ── Expert Advice Exchange Review Tests ───────────────────────────────


class TestExchangeReview:
    """TEST:ExpertAdvice.Output.ResponseEntersAsInterpretedCandidate"""

    def test_accept_exchange(self, client: TestClient) -> None:
        """Accepting an exchange transitions review_state to 'accepted'."""
        exchange = _create_exchange()
        resp = client.patch(
            f"/research/exchanges/{exchange.id}/review",
            json={"action": "accepted"},
        )
        assert resp.status_code == 200
        assert resp.json()["review_state"] == "accepted"

    def test_reject_exchange(self, client: TestClient) -> None:
        """Rejecting an exchange transitions review_state to 'rejected'."""
        exchange = _create_exchange()
        resp = client.patch(
            f"/research/exchanges/{exchange.id}/review",
            json={"action": "rejected"},
        )
        assert resp.status_code == 200
        assert resp.json()["review_state"] == "rejected"

    def test_invalid_action(self, client: TestClient) -> None:
        """Invalid action returns 400."""
        exchange = _create_exchange()
        resp = client.patch(
            f"/research/exchanges/{exchange.id}/review",
            json={"action": "maybe"},
        )
        assert resp.status_code == 400

    def test_review_nonexistent_exchange(self, client: TestClient) -> None:
        """Reviewing a nonexistent exchange returns 404."""
        resp = client.patch(
            "/research/exchanges/00000000-0000-0000-0000-000000000000/review",
            json={"action": "accepted"},
        )
        assert resp.status_code == 404

    def test_exchange_starts_as_pending_review(self, client: TestClient) -> None:
        """New exchanges enter with pending_review state — interpreted candidates, not accepted truth."""
        exchange = _create_exchange()
        resp = client.get(f"/research/exchanges/{exchange.id}")
        assert resp.json()["review_state"] == "pending_review"


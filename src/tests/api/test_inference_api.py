"""API tests — LLM inference health endpoint.

PLAN:WorkstreamI.PackageI9.HealthStatusAPI
TEST:LLM.API.HealthEndpointReportsProviderStatus
TEST:LLM.API.HealthEndpointHandlesUnavailableGracefully
"""

from __future__ import annotations

from fastapi.testclient import TestClient


class TestInferenceHealthEndpoint:
    """TEST:LLM.API.HealthEndpointReportsProviderStatus"""

    def test_endpoint_responds(self, client: TestClient) -> None:
        """The /health/inference endpoint responds with a valid status."""
        resp = client.get("/health/inference")
        assert resp.status_code == 200
        body = resp.json()
        # Must have required fields
        assert "status" in body
        assert body["status"] in ("healthy", "degraded", "unavailable", "error")
        assert "provider_type" in body
        assert body["provider_type"] == "openai_compatible"

    def test_endpoint_has_model_info_when_healthy(self, client: TestClient) -> None:
        """When the provider is reachable, model info is present."""
        resp = client.get("/health/inference")
        body = resp.json()
        # If LM Studio is running, we get model info
        # If not, status will be "unavailable" or "error" — both are valid
        if body["status"] == "healthy":
            assert body.get("model_name") is not None
            assert body.get("latency_ms") is not None
            assert body["latency_ms"] > 0

    def test_endpoint_handles_unavailable_gracefully(self, client: TestClient) -> None:
        """TEST:LLM.API.HealthEndpointHandlesUnavailableGracefully

        Even if LM Studio is not running, the endpoint responds cleanly.
        """
        resp = client.get("/health/inference")
        assert resp.status_code == 200
        body = resp.json()
        # Must NOT crash — any valid status is acceptable
        assert body["status"] in ("healthy", "degraded", "unavailable", "error")


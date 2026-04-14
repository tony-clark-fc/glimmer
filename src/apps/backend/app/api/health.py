"""Health and status routes — thin diagnostic surface."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel
from sqlalchemy import text

from app.config import get_settings
from app.db import get_engine

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    app_name: str
    database: str  # "ok" | "error"


class ResearchHealthResponse(BaseModel):
    """Health status for the Chrome/Gemini research adapter."""

    chrome_status: str  # "available" | "unavailable" | "unknown"
    chrome_port: int
    chrome_port_open: bool
    last_check_at: Optional[str] = None
    last_transition_at: Optional[str] = None
    consecutive_failures: int = 0
    monitor_running: bool = False


class InferenceHealthResponse(BaseModel):
    """Health status for the LLM inference provider.

    PLAN:WorkstreamI.PackageI9.HealthStatusAPI
    TEST:LLM.API.HealthEndpointReportsProviderStatus
    """

    status: str  # "healthy" | "degraded" | "unavailable" | "error"
    model_name: Optional[str] = None
    latency_ms: Optional[float] = None
    detail: Optional[str] = None
    provider_type: str = "openai_compatible"
    base_url: str = ""


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Lightweight liveness/readiness probe.

    Reports backend process health and basic database connectivity.
    """
    settings = get_settings()

    db_status = "ok"
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        database=db_status,
    )


@router.get("/health/research", response_model=ResearchHealthResponse)
def health_research(request: Request) -> ResearchHealthResponse:
    """Research adapter health — Chrome CDP and Gemini availability.

    Reports whether Chrome is reachable on the configured CDP port,
    the current monitor status, and any recent failures.
    """
    monitor = getattr(request.app.state, "chrome_monitor", None)

    if monitor is None:
        # Monitor not started (e.g., during testing without lifespan)
        from app.research.config import ChromeConfig
        from app.research.browser import _is_port_open

        config = ChromeConfig()
        port_open = _is_port_open(config.remote_debugging_port)
        return ResearchHealthResponse(
            chrome_status="available" if port_open else "unavailable",
            chrome_port=config.remote_debugging_port,
            chrome_port_open=port_open,
            monitor_running=False,
        )

    status_dict = monitor.get_status_dict()
    return ResearchHealthResponse(**status_dict)


@router.get("/health/inference", response_model=InferenceHealthResponse)
async def health_inference() -> InferenceHealthResponse:
    """LLM inference provider health — LM Studio availability and model status.

    PLAN:WorkstreamI.PackageI9.HealthStatusAPI
    TEST:LLM.API.HealthEndpointReportsProviderStatus

    Reports whether the local LLM provider is reachable, which model
    is loaded, and the health-check latency.
    """
    from app.inference.config import InferenceSettings
    from app.inference.openai_compat import OpenAICompatibleProvider
    from app.inference.base import ProviderStatus

    try:
        settings = InferenceSettings()
        provider = OpenAICompatibleProvider(settings)
        health = await provider.health_check()

        return InferenceHealthResponse(
            status=health.status.value,
            model_name=health.model_name,
            latency_ms=health.latency_ms,
            detail=health.detail,
            provider_type="openai_compatible",
            base_url=settings.base_url,
        )
    except Exception as exc:
        return InferenceHealthResponse(
            status="error",
            detail=f"Health check failed: {exc}",
            provider_type="openai_compatible",
        )

"""Health and status routes — thin diagnostic surface."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text

from app.config import get_settings
from app.db import get_engine

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    app_name: str
    database: str  # "ok" | "error"


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


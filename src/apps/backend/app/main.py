"""Glimmer backend — FastAPI application factory.

Creates and configures the root FastAPI application.  Route modules are
registered here; business logic stays in services/orchestration layers.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.operator import router as operator_router
from app.api.triage import router as triage_router
from app.config import get_settings


def create_app() -> FastAPI:
    """Build and return the configured FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
    )

    # ── CORS — allow access from other devices on the network ─────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Route registration ───────────────────────────────────────
    app.include_router(health_router)
    app.include_router(operator_router)
    app.include_router(triage_router)

    return app


app = create_app()


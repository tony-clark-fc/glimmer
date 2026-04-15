"""Glimmer backend — FastAPI application factory.

Creates and configures the root FastAPI application.  Route modules are
registered here; business logic stays in services/orchestration layers.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.operator import router as operator_router
from app.api.triage import router as triage_router
from app.api.projects import router as projects_router
from app.api.drafts import router as drafts_router
from app.api.persona import router as persona_router
from app.api.voice import router as voice_router
from app.api.telegram import router as telegram_router
from app.api.research import router as research_router
from app.api.connectors import router as connectors_router
from app.api.ask import router as ask_router
from app.config import get_settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — start/stop background services."""
    settings = get_settings()

    # ── Chrome Health Monitor ─────────────────────────────────────
    from app.research.config import ChromeConfig
    from app.research.chrome_monitor import ChromeHealthMonitor
    from app.services.telegram_notifier import TelegramNotifier

    chrome_config = ChromeConfig()
    notifier = TelegramNotifier(
        bot_token=settings.telegram_bot_token,
        chat_id=settings.telegram_operator_chat_id,
    )
    monitor = ChromeHealthMonitor(
        chrome_config=chrome_config,
        notifier=notifier,
    )
    monitor.start()
    app.state.chrome_monitor = monitor

    logger.info("Chrome health monitor started")

    yield

    # ── Shutdown ──────────────────────────────────────────────────
    await monitor.stop()
    logger.info("Chrome health monitor stopped")


def create_app() -> FastAPI:
    """Build and return the configured FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
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
    app.include_router(projects_router)
    app.include_router(drafts_router)
    app.include_router(persona_router)
    app.include_router(voice_router)
    app.include_router(telegram_router)
    app.include_router(research_router)
    app.include_router(connectors_router)
    app.include_router(ask_router)

    return app


app = create_app()

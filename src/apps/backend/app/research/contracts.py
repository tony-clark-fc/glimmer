"""Request/response contracts for the Gemini adapter.

Ported from C# Models/ directory. These are Pydantic DTOs used at the
adapter service boundary. They do NOT depend on SQLAlchemy — domain
model persistence uses the models in app/models/research.py.

ARCH:ResearchToolBoundary
ARCH:GeminiChatAdapter
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ── Deep Research contracts ──────────────────────────────────────────


class ResearchRequest(BaseModel):
    """Request to start a Gemini Deep Research job."""

    prompt: str = Field(..., min_length=1, description="The research prompt")
    document_name: str = Field(
        ..., min_length=1, description="Desired Google Doc filename"
    )


class ResearchResult(BaseModel):
    """Result of a completed deep research execution."""

    document_url: str = Field(..., description="URL of the exported Google Doc")
    document_renamed: bool = Field(
        ..., description="Whether the doc was renamed to the requested name"
    )


class ResearchJobStatus(BaseModel):
    """Status of a research job (for polling)."""

    job_id: UUID
    status: str  # queued, running, completed, completed_with_warning, failed, rate_limited
    message: Optional[str] = None
    document_url: Optional[str] = None
    queued_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


# ── Expert Advice (chat) contracts ───────────────────────────────────


class ChatRequest(BaseModel):
    """Request for a synchronous Gemini chat consultation."""

    prompt: str = Field(..., min_length=1, description="The prompt to send")
    mode: str = Field(
        default="Pro",
        description="Gemini mode: Fast, Thinking, or Pro",
    )


class ChatResult(BaseModel):
    """Result of a completed expert advice chat."""

    response_text: str = Field(
        ..., description="Full text of Gemini's response"
    )
    mode: str = Field(..., description="The Gemini mode that was used")
    duration_ms: int = Field(
        ..., description="Wall-clock duration in milliseconds"
    )


# ── Adapter status contracts ─────────────────────────────────────────


class AdapterStatus(BaseModel):
    """Operational status of the Gemini adapter."""

    status: str = Field(
        ..., description="Busy if an operation is active, Idle otherwise"
    )
    browser_available: bool = Field(
        ..., description="Whether Chrome is reachable on the CDP port"
    )
    queue_depth: int = Field(
        default=0, description="Research jobs waiting in queue"
    )
    today_completions: int = Field(
        default=0, description="Research jobs completed today (UTC)"
    )
    daily_rate_limit: int = Field(
        default=0, description="Configured max completions per day"
    )
    is_rate_limited: bool = Field(
        default=False, description="Whether the daily rate limit is reached"
    )


class AdapterHealthCheck(BaseModel):
    """Health check response for the adapter."""

    status: str = "healthy"
    chrome_port_open: bool = False
    chrome_connected: bool = False
    queue_depth: int = 0
    today_completions: int = 0


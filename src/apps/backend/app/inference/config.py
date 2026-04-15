"""Inference configuration — pydantic-settings for LLM provider setup.

PLAN:WorkstreamI.PackageI1.InferenceAbstraction
ARCH:LocalInferenceBaseline

Configuration for the inference layer, loaded from environment variables
with GLIMMER_INFERENCE_ prefix.  Sensible defaults point at the standard
LM Studio local endpoint.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class InferenceSettings(BaseSettings):
    """Configuration for the LLM inference provider."""

    model_config = SettingsConfigDict(
        env_prefix="GLIMMER_INFERENCE_",
        extra="ignore",
    )

    # ── Provider endpoint ─────────────────────────────────────────
    # LM Studio default; change for vLLM, Ollama, etc.
    base_url: str = "http://127.0.0.1:1234/v1"

    # API key — LM Studio accepts any non-empty string by default.
    # Kept as a setting so it works with providers that require one.
    api_key: str = "lm-studio"

    # ── Model selection ───────────────────────────────────────────
    # Model identifier as reported by the provider's /v1/models.
    model_name: str = "google/gemma-4-31b"

    # ── Generation defaults ───────────────────────────────────────
    default_temperature: float = 0.3
    default_max_tokens: int = 2000

    # ── Timeouts ──────────────────────────────────────────────────
    # Connect timeout (seconds) — how long to wait for TCP connection
    connect_timeout_seconds: float = 5.0

    # Read timeout (seconds) — how long to wait for a full response.
    # At ~20 tok/s and 2000 max tokens, worst case is ~100s.
    # 120s gives comfortable headroom.
    read_timeout_seconds: float = 120.0

    # Health check timeout (seconds) — quick probe
    health_timeout_seconds: float = 5.0

    # ── Operational ───────────────────────────────────────────────
    # Whether to request JSON mode from the provider when supported.
    # LM Studio supports this via response_format={"type": "json_object"}.
    prefer_json_mode: bool = True

    # Maximum retries on transient errors (connection reset, etc.)
    max_retries: int = 1

    # ── Per-task LLM toggles ──────────────────────────────────────
    # These allow the operator to enable/disable LLM inference per task
    # type for operational tuning.  When disabled for a given task, the
    # system uses the deterministic baseline instead.
    #
    # Operational tuning guidance:
    # - Start with all enabled and observe quality + latency.
    # - Disable individual tasks if the LLM adds unacceptable latency
    #   (e.g. classification at ~15s may be too slow for interactive use).
    # - Disable drafting LLM if tone/style calibration is incomplete.
    # - Disable briefing LLM if the template output is preferred.
    # - All tasks fall back cleanly to deterministic logic when disabled.
    llm_classification_enabled: bool = True
    llm_extraction_enabled: bool = True
    llm_prioritization_enabled: bool = True
    llm_drafting_enabled: bool = True
    llm_briefing_enabled: bool = True


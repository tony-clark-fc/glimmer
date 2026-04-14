"""Research and expert advice adapter configuration.

Ported from C# ResearchAgentOptions and ChromeOptions.
Configuration is loaded from environment variables with GLIMMER_ prefix.

ARCH:GeminiBrowserMediatedAdapter
"""

from __future__ import annotations

import platform
from pydantic_settings import BaseSettings, SettingsConfigDict


class ChromeConfig(BaseSettings):
    """Chrome/CDP configuration for the browser-mediated adapter."""

    model_config = SettingsConfigDict(
        env_prefix="GLIMMER_CHROME_",
        extra="ignore",
    )

    # Path to Chrome executable — platform-aware defaults
    exe_path: str = (
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if platform.system() == "Darwin"
        else "/usr/bin/google-chrome"
    )

    # Chrome user data directory — isolated profile for Gemini
    user_data_dir: str = ""

    # Chrome profile directory name within user_data_dir
    profile_name: str = "Default"

    # Google account email (logging/diagnostics only)
    google_account: str = ""

    # CDP remote debugging port
    remote_debugging_port: int = 9222

    # Maximum seconds to wait when connecting to Chrome via CDP
    connection_timeout_seconds: int = 30


class ResearchAdapterConfig(BaseSettings):
    """Configuration for the Gemini adapter — timeouts, rate limits, modes."""

    model_config = SettingsConfigDict(
        env_prefix="GLIMMER_RESEARCH_",
        extra="ignore",
    )

    # ── Deep Research settings ────────────────────────────────────
    # Maximum minutes to wait for Gemini Deep Research to complete
    research_timeout_minutes: int = 60

    # Maximum seconds to wait for the research plan to appear
    plan_timeout_seconds: int = 240

    # Maximum research jobs completed per calendar day (UTC). 0 = no limit.
    daily_rate_limit: int = 19

    # Seconds to wait after "Export to Docs" for Drive to save
    export_settle_seconds: int = 15

    # Seconds between completing one research job and starting the next
    inter_job_delay_seconds: int = 5

    # ── Expert Advice (chat) settings ─────────────────────────────
    # Maximum seconds to wait for a Gemini chat response
    chat_response_timeout_seconds: int = 300

    # Valid Gemini mode names accepted by the chat path
    valid_modes: list[str] = ["Fast", "Thinking", "Pro"]

    # Default mode for expert advice when not specified
    default_chat_mode: str = "Pro"


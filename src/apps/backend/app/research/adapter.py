"""Unified Gemini adapter — the service boundary for deep research and expert advice.

This is the public interface that the rest of Glimmer depends on. It hides
Playwright internals and exposes clean async methods for research and chat.

The adapter enforces a single-operation lock: only one Gemini interaction
(research or chat) can run at a time, matching the C# SemaphoreSlim(1,1)
pattern. This is a Gemini constraint — one session per Google account.

ARCH:GeminiBrowserMediatedAdapter
ARCH:GeminiChatAdapter
ARCH:ResearchToolBoundary
"""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

from app.research.browser import ChromeBrowserProvider
from app.research.config import ChromeConfig, ResearchAdapterConfig
from app.research.contracts import (
    AdapterHealthCheck,
    AdapterStatus,
    ChatRequest,
    ChatResult,
    ResearchRequest,
    ResearchResult,
)

logger = logging.getLogger(__name__)


class GeminiAdapter:
    """Unified adapter for Gemini deep research and expert advice.

    This is the service boundary that the orchestration layer, API routes,
    and graphs interact with. It exposes:

    - execute_research() — async deep research (long-running)
    - execute_chat() — synchronous expert advice (seconds to minutes)
    - check_browser_available() — health check
    - get_status() — operational status

    Only one Gemini operation at a time is supported.

    TEST:Research.Invocation.StartsBoundedResearchRun
    TEST:ExpertAdvice.Invocation.SendsPromptAndReturnsResponse
    """

    def __init__(
        self,
        chrome_config: Optional[ChromeConfig] = None,
        adapter_config: Optional[ResearchAdapterConfig] = None,
    ) -> None:
        self._chrome_config = chrome_config or ChromeConfig()
        self._adapter_config = adapter_config or ResearchAdapterConfig()
        self._browser_provider = ChromeBrowserProvider(self._chrome_config)
        self._operation_lock = asyncio.Lock()

    @property
    def is_busy(self) -> bool:
        """Whether a Gemini operation is currently in progress."""
        return self._operation_lock.locked()

    async def check_browser_available(self) -> bool:
        """Check whether Chrome is reachable on the CDP port.

        This does NOT trigger full initialization — safe for health checks.
        """
        return self._browser_provider.is_chrome_port_open

    async def get_health(self) -> AdapterHealthCheck:
        """Return adapter health check information."""
        return AdapterHealthCheck(
            status="healthy",
            chrome_port_open=self._browser_provider.is_chrome_port_open,
            chrome_connected=self._browser_provider.is_available,
        )

    async def get_status(self) -> AdapterStatus:
        """Return operational status of the adapter."""
        return AdapterStatus(
            status="Busy" if self.is_busy else "Idle",
            browser_available=self._browser_provider.is_chrome_port_open,
            daily_rate_limit=self._adapter_config.daily_rate_limit,
        )

    async def execute_chat(self, request: ChatRequest) -> ChatResult:
        """Execute a synchronous Gemini chat (expert advice).

        Acquires the operation lock, sends a prompt, waits for the response,
        and returns the text. Returns 409-equivalent if another op is running.

        TEST:ExpertAdvice.Invocation.SendsPromptAndReturnsResponse
        TEST:ExpertAdvice.ModeSelection.FastThinkingProRespected
        TEST:ExpertAdvice.Failure.GeminiUnavailableHandledSafely
        """
        # Validate mode
        if request.mode not in self._adapter_config.valid_modes:
            raise ValueError(
                f"Invalid mode '{request.mode}'. "
                f"Valid modes: {', '.join(self._adapter_config.valid_modes)}"
            )

        # Try to acquire the lock with a short timeout
        try:
            acquired = await asyncio.wait_for(
                self._operation_lock.acquire(), timeout=5.0
            )
        except asyncio.TimeoutError:
            raise RuntimeError(
                "Another Gemini operation is in progress — "
                "only one interaction at a time is supported."
            )

        if not acquired:
            raise RuntimeError(
                "Another Gemini operation is in progress."
            )

        try:
            browser = await self._browser_provider.get_browser()
            if browser is None:
                raise RuntimeError(
                    "Chrome is not available — ensure Chrome is running "
                    "with --remote-debugging-port on the configured port."
                )

            # Delegate to the chat interaction module
            from app.research.gemini_chat import execute_gemini_chat

            return await execute_gemini_chat(
                browser=browser,
                request=request,
                config=self._adapter_config,
            )
        finally:
            self._operation_lock.release()

    async def execute_research(
        self, request: ResearchRequest
    ) -> ResearchResult:
        """Execute a Gemini Deep Research job.

        Acquires the operation lock, drives the full Deep Research flow,
        and returns the result. Long-running (5-60 minutes).

        TEST:Research.Invocation.StartsBoundedResearchRun
        TEST:Research.Adapter.GeminiBrowserPathReturnsStructuredResult
        """
        # Try to acquire the lock — for research, we wait longer
        try:
            acquired = await asyncio.wait_for(
                self._operation_lock.acquire(), timeout=10.0
            )
        except asyncio.TimeoutError:
            raise RuntimeError(
                "Another Gemini operation is in progress — "
                "cannot start research while another operation is running."
            )

        if not acquired:
            raise RuntimeError(
                "Another Gemini operation is in progress."
            )

        try:
            browser = await self._browser_provider.get_browser()
            if browser is None:
                raise RuntimeError(
                    "Chrome is not available — ensure Chrome is running "
                    "with --remote-debugging-port on the configured port."
                )

            # Delegate to the research interaction module
            from app.research.gemini_research import execute_gemini_research

            return await execute_gemini_research(
                browser=browser,
                request=request,
                config=self._adapter_config,
            )
        finally:
            self._operation_lock.release()

    async def close(self) -> None:
        """Shut down the adapter and release browser resources."""
        await self._browser_provider.close()


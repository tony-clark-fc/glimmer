"""Background Chrome health monitor — periodic CDP port check and alerting.

Runs as an asyncio task during the FastAPI application lifespan. Checks
Chrome's CDP port availability at regular intervals and:

- logs state transitions (available ↔ unavailable)
- attempts auto-launch when Chrome is lost
- fires Telegram alerts on significant transitions
- exposes in-memory status for the health endpoint and workspace UI

ARCH:BrowserResearchSecurityBoundary
ARCH:ResearchAdapterSafetyBoundary
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Literal, Optional

from app.research.browser import ChromeBrowserProvider, _is_port_open
from app.research.config import ChromeConfig
from app.services.telegram_notifier import TelegramNotifier

logger = logging.getLogger(__name__)

ChromeStatus = Literal["available", "unavailable", "unknown"]


class ChromeHealthMonitor:
    """Periodic Chrome CDP health monitor with auto-recovery and alerting.

    Tracks Chrome availability and fires callbacks on state transitions.
    Designed to run as a long-lived asyncio task in the app lifespan.
    """

    def __init__(
        self,
        chrome_config: ChromeConfig,
        notifier: Optional[TelegramNotifier] = None,
        check_interval_seconds: float = 30.0,
    ) -> None:
        self._config = chrome_config
        self._notifier = notifier
        self._check_interval = check_interval_seconds
        self._browser_provider = ChromeBrowserProvider(chrome_config)

        # Public status — read by health endpoint and UI
        self.status: ChromeStatus = "unknown"
        self.last_check_at: Optional[datetime] = None
        self.last_transition_at: Optional[datetime] = None
        self.consecutive_failures: int = 0

        self._task: Optional[asyncio.Task] = None
        self._running = False

    @property
    def is_running(self) -> bool:
        """Whether the monitor loop is active."""
        return self._running

    def start(self) -> asyncio.Task:
        """Start the background monitor loop.

        Returns the asyncio task for lifecycle management.
        """
        if self._task is not None and not self._task.done():
            return self._task
        self._running = True
        self._task = asyncio.create_task(
            self._run_loop(), name="chrome-health-monitor"
        )
        return self._task

    async def stop(self) -> None:
        """Stop the monitor loop and clean up."""
        self._running = False
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        await self._browser_provider.close()
        if self._notifier:
            await self._notifier.close()

    async def _run_loop(self) -> None:
        """Main monitor loop — runs until stopped."""
        logger.info(
            "Chrome health monitor started (interval: %.0fs, port: %d)",
            self._check_interval,
            self._config.remote_debugging_port,
        )
        try:
            while self._running:
                await self._check_once()
                await asyncio.sleep(self._check_interval)
        except asyncio.CancelledError:
            logger.info("Chrome health monitor stopped")
            raise

    async def _check_once(self) -> None:
        """Perform a single health check and handle transitions."""
        now = datetime.now(timezone.utc)
        self.last_check_at = now

        port_open = _is_port_open(self._config.remote_debugging_port)
        previous_status = self.status

        if port_open:
            new_status: ChromeStatus = "available"
            self.consecutive_failures = 0
        else:
            new_status = "unavailable"
            self.consecutive_failures += 1

        # Detect transitions
        if previous_status != new_status:
            self.status = new_status
            self.last_transition_at = now

            if new_status == "unavailable":
                await self._on_chrome_lost()
            elif new_status == "available" and previous_status == "unavailable":
                await self._on_chrome_restored()
        else:
            self.status = new_status

    async def _on_chrome_lost(self) -> None:
        """Handle Chrome becoming unavailable."""
        logger.warning(
            "Chrome CDP port %d is no longer reachable — "
            "attempting auto-launch",
            self._config.remote_debugging_port,
        )

        # Attempt auto-launch
        launched = await self._browser_provider.launch_chrome()

        if launched:
            logger.info(
                "Chrome auto-launch successful — CDP port %d recovered",
                self._config.remote_debugging_port,
            )
            self.status = "available"
            self.consecutive_failures = 0
            # No need to alert the operator if recovery was automatic
            return

        logger.error(
            "Chrome auto-launch failed — research and expert advice "
            "capabilities are offline"
        )

        # Alert operator via Telegram
        if self._notifier and self._notifier.is_configured:
            await self._notifier.send_alert(
                "⚠️ <b>Glimmer — Chrome Offline</b>\n\n"
                "Chrome debug session is no longer available. "
                "Auto-launch was attempted but failed.\n\n"
                "Research and expert advice capabilities are offline.\n\n"
                "Please check the Chrome setup or restart Chrome manually."
            )

    async def _on_chrome_restored(self) -> None:
        """Handle Chrome becoming available again."""
        logger.info(
            "Chrome CDP port %d is now reachable — "
            "research and expert advice capabilities restored",
            self._config.remote_debugging_port,
        )

        # Notify operator of recovery
        if self._notifier and self._notifier.is_configured:
            await self._notifier.send_alert(
                "✅ <b>Glimmer — Chrome Restored</b>\n\n"
                "Chrome debug session is available again. "
                "Research and expert advice capabilities are online."
            )

    def get_status_dict(self) -> dict:
        """Return current status as a serializable dict for the health API."""
        return {
            "chrome_status": self.status,
            "chrome_port": self._config.remote_debugging_port,
            "chrome_port_open": self.status == "available",
            "last_check_at": (
                self.last_check_at.isoformat() if self.last_check_at else None
            ),
            "last_transition_at": (
                self.last_transition_at.isoformat()
                if self.last_transition_at
                else None
            ),
            "consecutive_failures": self.consecutive_failures,
            "monitor_running": self.is_running,
        }


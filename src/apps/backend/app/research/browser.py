"""Chrome debug-mode browser provider for the Gemini adapter.

Ported from C# ChromeBrowserProvider.cs. Manages a singleton connection
to Chrome via CDP (Chrome DevTools Protocol) using Playwright.

If Chrome is not running, the provider will automatically launch it with
the configured debug flags and user-data directory. The adapter uses the
operator's cookies/auth to access Gemini.

ARCH:GeminiBrowserMediatedAdapter
ARCH:BrowserResearchSecurityBoundary
"""

from __future__ import annotations

import asyncio
import logging
import os
import socket
from typing import TYPE_CHECKING, Optional

from app.research.config import ChromeConfig

if TYPE_CHECKING:
    from playwright.async_api import Browser, Playwright

logger = logging.getLogger(__name__)


class ChromeBrowserProvider:
    """Singleton service managing Chrome CDP connection via Playwright.

    ResearchAgent REQUIRES real Chrome (not Playwright Chromium) because
    Gemini needs the operator's Google account session and Gemini Pro
    subscription, which live in the Chrome profile.

    If Chrome is not running, it will be auto-launched with the correct
    debug flags. Only one process may connect via CDP at a time.

    TEST:Research.Failure.BrowserUnavailableHandledSafely
    """

    def __init__(self, config: ChromeConfig) -> None:
        self._config = config
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._init_lock = asyncio.Lock()
        self._launch_lock = asyncio.Lock()
        self._initialized = False

    @property
    def is_available(self) -> bool:
        """Whether a browser is currently connected."""
        if self._browser is None:
            return False
        # Playwright's Browser.is_connected() is a method, not a property
        is_connected = getattr(self._browser, "is_connected", None)
        if callable(is_connected):
            return is_connected()
        return bool(is_connected)

    @property
    def is_chrome_port_open(self) -> bool:
        """Quick check: is Chrome's CDP port accepting connections?

        Does NOT trigger initialization — safe for health checks.
        """
        return _is_port_open(self._config.remote_debugging_port)

    async def launch_chrome(self) -> bool:
        """Launch Chrome with CDP remote debugging enabled.

        Ported from C# ChromeBrowserProvider.LaunchChrome().
        Returns True if Chrome started and the CDP port opened within
        ~5 seconds. Idempotent: if Chrome is already running on the
        CDP port, returns True immediately.
        """
        # Already running — nothing to do
        if _is_port_open(self._config.remote_debugging_port):
            return True

        async with self._launch_lock:
            # Double-check after acquiring lock
            if _is_port_open(self._config.remote_debugging_port):
                return True

            exe_path = self._config.exe_path
            if not exe_path or not os.path.exists(exe_path):
                logger.error(
                    "Chrome executable not found at '%s'", exe_path
                )
                return False

            user_data_dir = self._config.user_data_dir
            if not user_data_dir:
                logger.error(
                    "GLIMMER_CHROME_USER_DATA_DIR is not configured — "
                    "cannot auto-launch Chrome without a dedicated profile. "
                    "See the Chrome Profile Setup Guide."
                )
                return False

            # Expand ~ in path
            user_data_dir = os.path.expanduser(user_data_dir)

            args = [
                exe_path,
                f"--remote-debugging-port={self._config.remote_debugging_port}",
                f"--user-data-dir={user_data_dir}",
                f"--profile-directory={self._config.profile_name}",
                "--no-first-run",
                "--no-default-browser-check",
            ]

            logger.info(
                "Launching Chrome: %s",
                " ".join(f'"{a}"' if " " in a else a for a in args),
            )

            try:
                await asyncio.create_subprocess_exec(
                    *args,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                )
            except Exception:
                logger.exception("Failed to launch Chrome process")
                return False

            # Wait for CDP port to open (up to 5 seconds)
            for _ in range(10):
                await asyncio.sleep(0.5)
                if _is_port_open(self._config.remote_debugging_port):
                    logger.info(
                        "Chrome started — CDP port %d is now open",
                        self._config.remote_debugging_port,
                    )
                    return True

            logger.error(
                "Chrome launched but CDP port %d did not open within "
                "5 seconds",
                self._config.remote_debugging_port,
            )
            return False

    async def get_browser(self) -> Optional[Browser]:
        """Get the shared browser instance.

        Initializes on first call. Reconnects automatically if the
        browser has disconnected. Auto-launches Chrome if not running.
        Returns None if Chrome cannot be started or connected.
        """
        # Fast path — already connected
        if self._initialized and self.is_available:
            return self._browser

        async with self._init_lock:
            # Double-check after acquiring lock
            if self._initialized and self.is_available:
                return self._browser

            # Clean up if previously connected but now disconnected
            if self._initialized:
                logger.warning(
                    "Chrome browser disconnected — attempting reconnection"
                )
                await self._cleanup()
                self._initialized = False

            # Auto-launch Chrome if not running
            if not _is_port_open(self._config.remote_debugging_port):
                logger.info(
                    "Chrome not detected on port %d — "
                    "attempting auto-launch",
                    self._config.remote_debugging_port,
                )
                launched = await self.launch_chrome()
                if not launched:
                    logger.error(
                        "Chrome auto-launch failed. Start Chrome manually:\n"
                        '  "%s" --remote-debugging-port=%d '
                        '--user-data-dir="%s" '
                        "--profile-directory=%s "
                        "--no-first-run --no-default-browser-check",
                        self._config.exe_path,
                        self._config.remote_debugging_port,
                        self._config.user_data_dir,
                        self._config.profile_name,
                    )
                    return None

            try:
                logger.info(
                    "Connecting to Chrome via CDP on port %d",
                    self._config.remote_debugging_port,
                )

                from playwright.async_api import async_playwright

                self._playwright = await async_playwright().start()

                cdp_url = (
                    f"http://localhost:{self._config.remote_debugging_port}"
                )
                self._browser = (
                    await self._playwright.chromium.connect_over_cdp(
                        cdp_url,
                        timeout=self._config.connection_timeout_seconds * 1000,
                    )
                )

                self._initialized = True

                logger.info(
                    "Connected to Chrome via CDP (port %d, profile: %s, "
                    "account: %s)",
                    self._config.remote_debugging_port,
                    self._config.profile_name,
                    self._config.google_account or "(not configured)",
                )

                return self._browser

            except Exception:
                logger.exception(
                    "Failed to connect to Chrome via CDP on port %d",
                    self._config.remote_debugging_port,
                )
                await self._cleanup()
                return None

    async def _cleanup(self) -> None:
        """Clean up Playwright and browser resources."""
        if self._browser is not None:
            try:
                await self._browser.close()
            except Exception:
                pass  # best effort
            self._browser = None

        if self._playwright is not None:
            try:
                await self._playwright.stop()
            except Exception:
                pass  # best effort
            self._playwright = None

    async def close(self) -> None:
        """Shut down the browser provider."""
        await self._cleanup()
        self._initialized = False


def _is_port_open(port: int, host: str = "127.0.0.1") -> bool:
    """Check whether a TCP port is accepting connections."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1.0)
            sock.connect((host, port))
            return True
    except (ConnectionRefusedError, TimeoutError, OSError):
        return False


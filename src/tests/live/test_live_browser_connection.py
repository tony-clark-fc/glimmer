"""Live browser connection and Gemini navigation tests.

TEST:Research.Failure.BrowserUnavailableHandledSafely
TEST:Research.Failure.GeminiInteractionFailureVisible

These tests prove that the adapter can:
1. Launch Chrome with the operator's profile
2. Connect via CDP
3. Navigate to gemini.google.com
4. Detect that the user is signed in and the input box is ready

They do NOT send prompts or interact with Gemini beyond page load.
"""

from __future__ import annotations

import pytest
from app.research.adapter import GeminiAdapter
from app.research.browser import _is_port_open
from app.research._browser_helpers import (
    navigate_to_gemini,
    wait_for_input_box,
)

pytestmark = [pytest.mark.manual_only]


class TestChromeConnection:
    """Prove Chrome can be launched and connected via CDP."""

    @pytest.mark.asyncio
    async def test_chrome_port_is_open(self, adapter: GeminiAdapter) -> None:
        """Chrome CDP port 9222 is accepting connections.

        The adapter auto-launches Chrome if it isn't running, so we
        trigger get_browser() first, then verify the port is open.
        """
        browser = await adapter._browser_provider.get_browser()
        assert browser is not None, "get_browser() should auto-launch Chrome"
        assert _is_port_open(9222), "CDP port 9222 should be open after auto-launch"

    @pytest.mark.asyncio
    async def test_cdp_connection_succeeds(self, adapter: GeminiAdapter) -> None:
        """Playwright connects to Chrome via CDP and gets a browser instance."""
        browser = await adapter._browser_provider.get_browser()
        assert browser is not None, "get_browser() returned None — CDP connection failed"
        assert browser.is_connected(), "Browser reports not connected"

    @pytest.mark.asyncio
    async def test_health_check_after_connection(self, adapter: GeminiAdapter) -> None:
        """After get_browser(), health check reports Chrome connected."""
        # Trigger initialization first
        browser = await adapter._browser_provider.get_browser()
        assert browser is not None

        health = await adapter.get_health()
        assert health.chrome_port_open is True, "Chrome port should be open"
        assert health.chrome_connected is True, "Chrome should be connected after get_browser()"
        assert health.status == "healthy"

    @pytest.mark.asyncio
    async def test_status_reports_idle(self, adapter: GeminiAdapter) -> None:
        """Adapter status reports Idle with browser available."""
        status = await adapter.get_status()
        assert status.status == "Idle"
        assert status.browser_available is True


class TestGeminiNavigation:
    """Prove the adapter can navigate to Gemini and the page loads."""

    @pytest.mark.asyncio
    async def test_navigate_to_gemini(self, adapter: GeminiAdapter) -> None:
        """Navigate to gemini.google.com — page loads and input box appears.

        This proves the Chrome profile is authenticated and Gemini is accessible.
        If sign-in is required, navigate_to_gemini() raises RuntimeError.
        """
        browser = await adapter._browser_provider.get_browser()
        assert browser is not None

        context = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = await context.new_page()

        try:
            await navigate_to_gemini(page)
            # If we get here, the page loaded and no sign-in was needed
            title = await page.title()
            assert title, "Page title should not be empty"

            # Verify the input box is present
            await wait_for_input_box(page, timeout_ms=10_000)
        finally:
            await page.close()

    @pytest.mark.asyncio
    async def test_page_url_is_gemini(self, adapter: GeminiAdapter) -> None:
        """After navigation, the URL should be on gemini.google.com."""
        browser = await adapter._browser_provider.get_browser()
        assert browser is not None

        context = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = await context.new_page()

        try:
            await navigate_to_gemini(page)
            assert "gemini.google.com" in page.url, (
                f"Expected gemini.google.com in URL, got: {page.url}"
            )
        finally:
            await page.close()

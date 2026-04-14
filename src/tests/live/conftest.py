"""Shared fixtures for live browser tests.

Provides a configured GeminiAdapter backed by a real Chrome instance
using the operator's Gemini profile at /Users/tony/PlaywrightProfiles/Gemini.

These fixtures auto-launch Chrome if it isn't already running.
"""

from __future__ import annotations

import logging
from typing import AsyncGenerator

import pytest
import pytest_asyncio

from app.research.adapter import GeminiAdapter
from app.research.config import ChromeConfig, ResearchAdapterConfig

# Show real-time adapter logging during live tests
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)

logger = logging.getLogger(__name__)

# ── Operator profile configuration ───────────────────────────────────
# This is the Chrome user-data directory that has been pre-authenticated
# with a Google account that has Gemini access.
LIVE_CHROME_CONFIG = ChromeConfig(
    user_data_dir="/Users/tony/PlaywrightProfiles/Gemini",
    profile_name="Default",
    remote_debugging_port=9222,
    connection_timeout_seconds=30,
)

LIVE_ADAPTER_CONFIG = ResearchAdapterConfig(
    chat_response_timeout_seconds=120,  # shorter for test
    default_chat_mode="Fast",
)


def pytest_configure(config: pytest.Config) -> None:
    """Register markers for live tests."""
    config.addinivalue_line("markers", "manual_only: requires live browser")


async def _close_all_test_pages(adapter: GeminiAdapter) -> None:
    """Close every page/tab opened during a test, before disconnecting.

    With CDP connections, page.close() inside adapter code can silently
    fail if the Playwright context is being torn down concurrently.
    This function proactively closes all pages to prevent tab accumulation.

    We skip the very first page in the first context (index 0) because
    that is typically Chrome's pre-existing tab — closing it would close
    the user's original tab.
    """
    browser = adapter._browser_provider._browser
    if browser is None:
        return

    for ctx_idx, context in enumerate(browser.contexts):
        pages = context.pages
        for page_idx, page in enumerate(pages):
            # Keep the first page in the first context — that's the
            # user's pre-existing tab from before we connected.
            if ctx_idx == 0 and page_idx == 0:
                continue
            try:
                url = page.url
                await page.close()
                logger.debug("Closed leftover tab: %s", url)
            except Exception as exc:
                logger.warning("Could not close tab: %s", exc)


@pytest_asyncio.fixture()
async def adapter() -> AsyncGenerator[GeminiAdapter, None]:
    """Provide a GeminiAdapter connected to the operator's live Chrome.

    Each test gets a fresh adapter instance. On teardown, ALL pages/tabs
    created during the test are explicitly closed before the CDP
    connection is dropped — preventing tab accumulation in Chrome.
    """
    a = GeminiAdapter(
        chrome_config=LIVE_CHROME_CONFIG,
        adapter_config=LIVE_ADAPTER_CONFIG,
    )
    yield a
    # Close all test-created tabs BEFORE disconnecting CDP
    await _close_all_test_pages(a)
    await a.close()

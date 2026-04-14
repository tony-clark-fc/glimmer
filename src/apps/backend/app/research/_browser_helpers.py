"""Shared browser-interaction helpers for the Gemini adapter.

Used by both gemini_chat.py and gemini_research.py to avoid
duplication of navigation, input-finding, and diagnostic code.

ARCH:GeminiBrowserMediatedAdapter
ARCH:BrowserResearchSecurityBoundary
"""

from __future__ import annotations

import asyncio
import logging
import random
from typing import Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# ── Whitelisted destinations ─────────────────────────────────────

# The adapter may ONLY navigate to these domains. Any navigation
# outside this list is blocked as a safety boundary enforcement.
# This is a load-bearing security rule: ARCH:BrowserResearchSecurityBoundary
ALLOWED_DESTINATION_DOMAINS: frozenset[str] = frozenset({
    "gemini.google.com",
    "docs.google.com",
    "accounts.google.com",  # sign-in redirect
})


class DestinationBlockedError(Exception):
    """Raised when navigation to a non-whitelisted URL is attempted."""
    pass


def validate_destination_url(url: str) -> None:
    """Validate that a URL is within the whitelisted destinations.

    Raises DestinationBlockedError if the URL is not on the allowlist.

    ARCH:BrowserResearchSecurityBoundary
    TEST:Research.Security.NoUnboundedActionTaking
    """
    parsed = urlparse(url)
    hostname = parsed.hostname or ""

    if hostname not in ALLOWED_DESTINATION_DOMAINS:
        raise DestinationBlockedError(
            f"Navigation to '{hostname}' is blocked — only whitelisted "
            f"destinations are allowed: {', '.join(sorted(ALLOWED_DESTINATION_DOMAINS))}. "
            f"Attempted URL: {url}"
        )


async def safe_goto(page: Any, url: str, **kwargs: Any) -> None:
    """Navigate to a URL after validating it is a whitelisted destination.

    This MUST be used instead of raw page.goto() in all adapter code.

    ARCH:BrowserResearchSecurityBoundary
    """
    validate_destination_url(url)
    await page.goto(url, **kwargs)

# Multi-strategy selectors for Gemini UI elements.
# Google frequently changes element IDs/classes; text-based selectors
# are most resilient. Each list is tried in order.
INPUT_SELECTORS = [
    "div[contenteditable][role='textbox'][aria-label='Enter a prompt here']",
    "div[contenteditable='true'][role='textbox']",
    "div.ql-editor[contenteditable='true']",
    "div[contenteditable='plaintext-only']",
    "div[contenteditable='true']",
]


async def wait_for_input_box(page: Any, timeout_ms: int = 30_000) -> None:
    """Wait for any of the known input box selectors to appear."""
    compound = ", ".join(INPUT_SELECTORS)
    await page.wait_for_selector(compound, timeout=timeout_ms)


async def find_input_box(page: Any) -> Any:
    """Find and return a locator for the Gemini prompt input box."""
    for selector in INPUT_SELECTORS:
        locator = page.locator(selector).first
        try:
            await locator.wait_for(state="visible", timeout=2_000)
            logger.debug("Using input selector: %s", selector)
            return locator
        except Exception:
            continue

    raise RuntimeError(
        "Could not find the Gemini prompt input box. "
        "The Gemini UI may have changed — check INPUT_SELECTORS."
    )


async def ensure_fresh_chat(page: Any) -> None:
    """Ensure a fresh Gemini chat via sidebar New Chat button."""
    # Try direct "New chat" link
    new_chat_selectors = [
        "a[data-test-id='expanded-button'][aria-label='New chat']",
        "a[aria-label='New chat']",
        "button:has-text('New chat')",
        "a:has-text('New chat')",
    ]

    for selector in new_chat_selectors:
        try:
            btn = page.locator(selector).first
            await btn.wait_for(state="visible", timeout=2_000)
            await btn.click()
            logger.debug("Clicked 'New chat' via: %s", selector)
            await page.wait_for_timeout(1_000)
            return
        except Exception:
            continue

    # Try hamburger menu first
    hamburger_selectors = [
        "button[data-test-id='side-nav-menu-button']",
        "button[aria-label='Main menu']",
    ]
    for selector in hamburger_selectors:
        try:
            btn = page.locator(selector).first
            await btn.wait_for(state="visible", timeout=2_000)
            await btn.click()
            await page.wait_for_timeout(800)

            for nc_selector in new_chat_selectors:
                try:
                    nc_btn = page.locator(nc_selector).first
                    await nc_btn.wait_for(state="visible", timeout=2_000)
                    await nc_btn.click()
                    logger.debug("Clicked 'New chat' after hamburger")
                    await page.wait_for_timeout(1_000)
                    return
                except Exception:
                    continue
        except Exception:
            continue

    logger.debug("Could not find 'New chat' — assuming fresh state")


async def human_pause(
    min_ms: int, max_ms: int, context: str
) -> None:
    """Simulate human pacing with randomized delay."""
    delay = random.randint(min_ms, max_ms)
    logger.debug("Human pacing: %s — waiting %dms", context, delay)
    await asyncio.sleep(delay / 1000)


# ── Proficient-typist parameters ─────────────────────────────────
# Models ~90 WPM (a proficient typist). Average word is ~5 chars,
# so 90 WPM ≈ 450 chars/min ≈ 133ms per character base rate.
# We add jitter and natural rhythm breaks at word/punctuation
# boundaries. Total typing time is capped at MAX_TYPING_SECONDS.

_BASE_CHAR_MS: int = 105          # base delay per character
_JITTER_MS: int = 40              # ± random jitter per keystroke
_SPACE_EXTRA_MS: int = 60         # extra pause at word boundaries
_PUNCTUATION_EXTRA_MS: int = 90   # extra pause after punctuation
_PUNCTUATION_CHARS: str = ".,;:!?—-"
MAX_TYPING_SECONDS: float = 30.0  # hard cap on total typing time


async def human_type(
    page: Any,
    locator: Any,
    text: str,
    max_seconds: float = MAX_TYPING_SECONDS,
) -> None:
    """Type text into a locator with human-like keystroke timing.

    Simulates a proficient typist (~90 WPM) with natural rhythm:
    - per-character random delay
    - longer pauses at word boundaries and after punctuation
    - total time capped at *max_seconds* (scales speed if text is long)

    Falls back to instant fill() if the text is empty.
    """
    if not text:
        await locator.fill("")
        return

    # Calculate the ideal total typing time
    ideal_ms = 0.0
    for ch in text:
        ideal_ms += _BASE_CHAR_MS
        if ch == " ":
            ideal_ms += _SPACE_EXTRA_MS
        elif ch in _PUNCTUATION_CHARS:
            ideal_ms += _PUNCTUATION_EXTRA_MS

    cap_ms = max_seconds * 1000
    # If the ideal time exceeds the cap, scale all delays down
    scale = min(1.0, cap_ms / ideal_ms) if ideal_ms > 0 else 1.0

    logger.debug(
        "Human typing: %d chars, estimated %.1fs (scale=%.2f, cap=%.0fs)",
        len(text), (ideal_ms * scale) / 1000, scale, max_seconds,
    )

    # Focus the input
    await locator.click()
    await asyncio.sleep(random.uniform(0.1, 0.3))

    for ch in text:
        # Base delay with jitter
        delay_ms = _BASE_CHAR_MS + random.randint(-_JITTER_MS, _JITTER_MS)

        # Rhythm breaks
        if ch == " ":
            delay_ms += random.randint(0, _SPACE_EXTRA_MS)
        elif ch in _PUNCTUATION_CHARS:
            delay_ms += random.randint(0, _PUNCTUATION_EXTRA_MS)

        delay_ms = max(30, delay_ms) * scale  # floor at 30ms, then scale

        await page.keyboard.type(ch, delay=0)
        await asyncio.sleep(delay_ms / 1000)

    logger.debug("Human typing complete (%d chars)", len(text))


async def try_save_screenshot(page: Any, suffix: str = "failure") -> None:
    """Save a diagnostic screenshot. Best-effort — never raises."""
    try:
        import uuid as _uuid

        path = f"/tmp/glimmer-{suffix}_{_uuid.uuid4().hex[:8]}.png"
        await page.screenshot(path=path, full_page=True)
        logger.warning("Diagnostic screenshot saved: %s", path)
    except Exception:
        logger.debug("Could not save diagnostic screenshot")


async def navigate_to_gemini(page: Any) -> None:
    """Navigate to Gemini and verify the input box is ready.

    Uses safe_goto to enforce whitelisted destination policy.
    Raises RuntimeError if the page doesn't load or sign-in is needed.

    ARCH:BrowserResearchSecurityBoundary
    """
    await safe_goto(
        page,
        "https://gemini.google.com/",
        timeout=30_000,
        wait_until="domcontentloaded",
    )
    await wait_for_input_box(page, timeout_ms=30_000)

    # Check if sign-in is required
    sign_in = await page.query_selector("input[type=email]")
    if sign_in is not None:
        raise RuntimeError(
            "Chrome profile is not signed into Google. "
            "Sign in manually, then restart."
        )


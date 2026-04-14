"""Gemini synchronous chat interaction flow (Expert Advice).

Ported from C# GeminiAutomationService.ExecuteChatAsync().
Drives Chrome via Playwright to send a prompt to Gemini and capture
the response text.

ARCH:GeminiChatAdapter
ARCH:ExpertAdviceCapability

Flow:
1. Navigate to gemini.google.com/app
2. Expand sidebar → click New Chat (ensures clean conversation)
3. Select mode from the mode picker dropdown (Fast / Thinking / Pro)
4. Enter prompt into the input textbox
5. Send the prompt
6. Wait for the copy button to appear (signals response is complete)
7. Click "Copy response" and read the clipboard text
8. Return the response to the caller
9. Close the browser tab
"""

from __future__ import annotations

import logging
import time
from typing import Any

from app.research.config import ResearchAdapterConfig
from app.research.contracts import ChatRequest, ChatResult
from app.research._browser_helpers import (
    ensure_fresh_chat,
    find_input_box,
    human_pause,
    safe_goto,
    try_save_screenshot,
    wait_for_input_box,
)

logger = logging.getLogger(__name__)


async def execute_gemini_chat(
    browser: Any,
    request: ChatRequest,
    config: ResearchAdapterConfig,
) -> ChatResult:
    """Execute a synchronous Gemini chat and return the response.

    This function implements the full chat flow ported from the C# agent.
    It creates a new browser tab, navigates to Gemini, sends the prompt,
    and captures the response.
    """
    start_time = time.monotonic()

    context = browser.contexts[0] if browser.contexts else await browser.new_context()
    page = await context.new_page()
    await page.bring_to_front()

    logger.info(
        "Starting Gemini chat — mode: %s, prompt length: %d",
        request.mode,
        len(request.prompt),
    )

    try:
        # ── 1. Navigate to Gemini ──
        await safe_goto(
            page,
            "https://gemini.google.com/app",
            timeout=30_000,
            wait_until="domcontentloaded",
        )
        await wait_for_input_box(page, timeout_ms=30_000)

        # Human pacing: page loaded
        await human_pause(1500, 2500, "page loaded")

        # ── 2. New Chat ──
        await ensure_fresh_chat(page)
        await wait_for_input_box(page, timeout_ms=10_000)

        await human_pause(1000, 2000, "new chat ready")

        # ── 3. Select mode ──
        await _select_gemini_mode(page, request.mode)

        await human_pause(1000, 2000, "mode selected")

        # ── 4. Enter prompt ──
        input_locator = await find_input_box(page)
        await input_locator.fill(request.prompt)
        logger.debug("Prompt entered (%d chars)", len(request.prompt))

        await human_pause(1500, 3000, "reviewing prompt")

        # ── 5. Send ──
        await page.click(
            "button[aria-label='Send message']", timeout=5_000
        )
        logger.info("Prompt sent — waiting for response")

        # ── 6. Wait for response and capture ──
        response_text = await _wait_for_response_and_copy(page, config)

        elapsed_ms = int((time.monotonic() - start_time) * 1000)
        logger.info(
            "Chat complete — %d chars in %.1fs",
            len(response_text),
            elapsed_ms / 1000,
        )

        return ChatResult(
            response_text=response_text,
            mode=request.mode,
            duration_ms=elapsed_ms,
        )

    except Exception:
        await try_save_screenshot(page, "chat-failure")
        raise
    finally:
        try:
            await page.close()
        except Exception:
            pass  # best effort


# ═══════════════════════════════════════════════════════════════════════
# Private helper functions — each phase of the Gemini chat interaction
# ═══════════════════════════════════════════════════════════════════════


async def _select_gemini_mode(page: Any, mode: str) -> None:
    """Select the Gemini mode (Fast / Thinking / Pro)."""
    mode_btn = page.locator(
        "button[data-test-id='bard-mode-menu-button']"
    ).first

    try:
        await mode_btn.wait_for(state="visible", timeout=5_000)
    except Exception:
        logger.warning(
            "Mode picker button not found — proceeding with default mode"
        )
        return

    # Check if already in the desired mode
    try:
        current_mode = await page.locator(
            "[data-test-id='logo-pill-label-container'] span"
        ).first.inner_text()
        if current_mode.strip().lower() == mode.lower():
            logger.debug("Already in %s mode — no switch needed", mode)
            return
    except Exception:
        pass

    # Open dropdown and select
    await mode_btn.click()
    await page.wait_for_timeout(600)

    # Strategy 1: exact text match
    try:
        option = page.get_by_text(mode, exact=True).first
        await option.wait_for(state="visible", timeout=3_000)
        await option.click()
        logger.info("Gemini mode set to: %s", mode)
        await page.wait_for_timeout(500)
        return
    except Exception:
        pass

    # Strategy 2: JavaScript
    try:
        clicked = await page.evaluate(
            """(targetMode) => {
                const candidates = Array.from(document.querySelectorAll('*'));
                const match = candidates.find(el =>
                    el.children.length === 0 &&
                    el.textContent.trim() === targetMode &&
                    el.offsetParent !== null);
                if (match) {
                    const clickable = match.closest('button')
                        || match.closest('[role="menuitem"]')
                        || match.closest('[role="option"]')
                        || match;
                    clickable.click();
                    return true;
                }
                return false;
            }""",
            mode,
        )
        if clicked:
            logger.info("Gemini mode set to: %s (via JS)", mode)
            await page.wait_for_timeout(500)
            return
    except Exception:
        pass

    # Failed — dismiss dropdown
    await page.keyboard.press("Escape")
    logger.warning("Could not select mode '%s' — using current mode", mode)


async def _wait_for_response_and_copy(
    page: Any, config: ResearchAdapterConfig
) -> str:
    """Wait for Gemini to finish responding, then capture the text."""
    timeout = config.chat_response_timeout_seconds * 1_000

    # Wait for copy button
    copy_btn = page.locator("button[data-test-id='copy-button']").last
    try:
        await copy_btn.wait_for(state="visible", timeout=timeout)
    except Exception:
        raise TimeoutError(
            f"Gemini did not finish responding within "
            f"{config.chat_response_timeout_seconds} seconds."
        )

    logger.debug("Copy button visible — response complete")
    await human_pause(2000, 4000, "reading response")

    # Click copy
    await copy_btn.click()
    await page.wait_for_timeout(800)

    # Strategy 1: clipboard read
    try:
        text = await page.evaluate("() => navigator.clipboard.readText()")
        if text and text.strip():
            logger.debug(
                "Captured response via clipboard (%d chars)", len(text)
            )
            return text
    except Exception:
        logger.debug("clipboard.readText() failed — trying intercept")

    # Strategy 2: clipboard intercept
    try:
        await page.evaluate(
            """() => {
                window.__geminiCopiedText = null;
                const origWrite = navigator.clipboard.writeText.bind(
                    navigator.clipboard);
                navigator.clipboard.writeText = async (text) => {
                    window.__geminiCopiedText = text;
                    return origWrite(text);
                };
            }"""
        )
        await copy_btn.click()
        await page.wait_for_timeout(800)
        text = await page.evaluate("() => window.__geminiCopiedText")
        if text and text.strip():
            logger.debug(
                "Captured response via intercept (%d chars)", len(text)
            )
            return text
    except Exception:
        logger.debug("Clipboard intercept failed — trying DOM extraction")

    # Strategy 3: DOM extraction
    text = await page.evaluate(
        """() => {
            const selectors = [
                'model-response .model-response-text',
                'model-response message-content',
                '[data-test-id="model-response"]',
                'message-content',
                '.response-container'
            ];
            for (const sel of selectors) {
                const elements = document.querySelectorAll(sel);
                if (elements.length > 0) {
                    const last = elements[elements.length - 1];
                    const text = last.innerText?.trim();
                    if (text && text.length > 0) return text;
                }
            }
            const all = Array.from(document.querySelectorAll('.markdown'));
            if (all.length > 0) {
                return all[all.length - 1].innerText?.trim() || null;
            }
            return null;
        }"""
    )

    if text and text.strip():
        logger.debug("Captured response via DOM (%d chars)", len(text))
        return text

    raise RuntimeError(
        "Could not extract Gemini response text — "
        "clipboard and DOM extraction all failed."
    )


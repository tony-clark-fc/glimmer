"""Gemini Deep Research interaction flow.

Ported from C# GeminiAutomationService.ExecuteResearchAsync().
Drives Chrome via Playwright to run Gemini Deep Research mode,
export to Google Docs, and rename the document.

ARCH:GeminiBrowserMediatedAdapter

Flow:
1. Navigate to gemini.google.com
2. Ensure fresh chat
3. Enter the research prompt
4. Activate Deep Research mode (Tools → Deep research)
5. Send the prompt
6. Click "Start research" when the plan appears
7. Wait for research to complete (5–60 minutes)
8. Export to Google Docs
9. Rename the document
10. Close tabs
"""

from __future__ import annotations

import logging
import time
from typing import Any

from app.research.config import ResearchAdapterConfig
from app.research.contracts import ResearchRequest, ResearchResult
from app.research._browser_helpers import (
    ensure_fresh_chat,
    find_input_box,
    human_pause,
    navigate_to_gemini,
    try_save_screenshot,
    wait_for_input_box,
)

logger = logging.getLogger(__name__)


async def execute_gemini_research(
    browser: Any,
    request: ResearchRequest,
    config: ResearchAdapterConfig,
) -> ResearchResult:
    """Execute a Gemini Deep Research job end-to-end.

    Ported from C# GeminiAutomationService.ExecuteResearchAsync().

    TEST:Research.Adapter.GeminiBrowserPathReturnsStructuredResult
    TEST:Research.Invocation.StartsBoundedResearchRun
    """
    start_time = time.monotonic()

    context = browser.contexts[0] if browser.contexts else await browser.new_context()
    page = await context.new_page()
    await page.bring_to_front()

    logger.info(
        "Starting Gemini Deep Research for '%s', prompt length: %d",
        request.document_name,
        len(request.prompt),
    )

    succeeded = False
    try:
        # ── 1. Navigate to Gemini and ensure clean chat ──
        await navigate_to_gemini(page)
        await human_pause(1500, 2500, "page loaded")

        # ── 2. Ensure fresh chat ──
        await ensure_fresh_chat(page)
        await wait_for_input_box(page, timeout_ms=10_000)
        await human_pause(1000, 2000, "fresh chat ready")

        # ── 3. Enter the research prompt ──
        input_locator = await find_input_box(page)
        await input_locator.fill(request.prompt)
        logger.info("Prompt entered (%d chars)", len(request.prompt))
        await human_pause(1500, 3000, "reviewing prompt")

        # ── 4. Activate Deep Research mode ──
        await try_save_screenshot(page, "pre-deep-research")
        await _activate_deep_research(page)
        await human_pause(1000, 2000, "Deep Research activated")

        # ── 5. Send the prompt ──
        await page.click(
            "button[aria-label='Send message']", timeout=5_000
        )
        logger.info("Prompt sent")

        # ── 6. Click "Start research" when the plan appears ──
        await _click_start_research(page, config)
        logger.info("Research started — waiting for completion")

        # ── 7. Wait for research completion (Export button) ──
        export_btn = await _wait_for_export_button(page, config)
        logger.info("Research complete — Export button found")

        # ── 8. Export to Google Docs ──
        doc_page, doc_url = await _export_to_google_docs(page, export_btn, config)
        logger.info("Google Doc created: %s", doc_url)

        # ── 9. Rename the document ──
        renamed = await _try_rename_document(doc_page, request.document_name)
        if renamed:
            logger.info("Document renamed to '%s'", request.document_name)
        else:
            logger.warning(
                "Document rename failed — doc exists but has default name"
            )

        # ── 10. Close the doc tab ──
        try:
            await doc_page.close()
        except Exception:
            pass  # best effort

        succeeded = True
        elapsed = time.monotonic() - start_time
        logger.info("Deep Research complete in %.1f minutes", elapsed / 60)

        return ResearchResult(
            document_url=doc_url,
            document_renamed=renamed,
        )

    except Exception:
        await try_save_screenshot(page, "research-failure")
        raise
    finally:
        if succeeded:
            try:
                await page.close()
            except Exception:
                pass  # best effort
        else:
            # Leave the tab open for operator debugging (matching C# behavior)
            logger.warning(
                "Tab left open for debugging — close it manually "
                "before submitting the next job"
            )


# ═══════════════════════════════════════════════════════════════════════
# Private helper functions — each phase of the deep research interaction
# ═══════════════════════════════════════════════════════════════════════


async def _activate_deep_research(page: Any) -> None:
    """Activate Gemini Deep Research mode via Tools → Deep research.

    Ported from C# ActivateDeepResearchAsync (lines 388–423).
    """
    tools_opened = await _click_tools_button(page)
    if not tools_opened:
        raise RuntimeError(
            "Could not find or click the 'Tools' button in the Gemini UI. "
            "The UI may have changed — check selectors."
        )

    logger.debug("Tools dropdown opened — looking for 'Deep research'")
    await page.wait_for_timeout(1_000)

    dr_clicked = await _click_deep_research_item(page)
    if not dr_clicked:
        await _dump_dropdown_diagnostics(page)
        raise RuntimeError(
            "Could not find 'Deep research' in the Tools dropdown. "
            "Check the diagnostic log for the actual dropdown contents."
        )

    logger.info("Activated Deep Research mode")
    await page.wait_for_timeout(500)


async def _click_tools_button(page: Any) -> bool:
    """Click the 'Tools' button to open the tools dropdown.

    Ported from C# ClickToolsButtonAsync (lines 429–493).
    """
    # Strategy 1: role=button with name
    try:
        btn = page.get_by_role("button", name="Tools")
        await btn.wait_for(state="visible", timeout=3_000)
        await btn.click()
        logger.debug("Clicked 'Tools' via role=button[name=Tools]")
        return True
    except Exception:
        pass

    # Strategy 2: button with text
    try:
        btn = page.locator("button:has-text('Tools')").first
        await btn.wait_for(state="visible", timeout=2_000)
        await btn.click()
        logger.debug("Clicked 'Tools' via button:has-text")
        return True
    except Exception:
        pass

    # Strategy 3: text locator
    try:
        btn = page.locator("text=Tools").first
        await btn.wait_for(state="visible", timeout=2_000)
        await btn.click()
        logger.debug("Clicked 'Tools' via text= locator")
        return True
    except Exception:
        pass

    # Strategy 4: JavaScript
    try:
        clicked = await page.evaluate(
            """() => {
                const candidates = Array.from(document.querySelectorAll(
                    'button, [role="button"], div[role="button"]'));
                const btn = candidates.find(el =>
                    el.textContent.trim() === 'Tools' ||
                    el.innerText.trim() === 'Tools');
                if (btn) { btn.click(); return true; }
                return false;
            }"""
        )
        if clicked:
            logger.debug("Clicked 'Tools' via JavaScript")
            return True
    except Exception:
        pass

    logger.warning("Could not find 'Tools' button")
    return False


async def _click_deep_research_item(page: Any) -> bool:
    """Click 'Deep research' from the already-open Tools dropdown.

    Ported from C# ClickDeepResearchItemAsync (lines 499–577).
    """
    # Strategy 1: exact text match
    try:
        item = page.get_by_text("Deep research", exact=True)
        await item.wait_for(state="visible", timeout=3_000)
        await item.click()
        logger.debug("Clicked 'Deep research' via GetByText(exact)")
        return True
    except Exception:
        pass

    # Strategy 2: regex text match
    try:
        item = page.locator("text=/[Dd]eep\\s+[Rr]esearch/").first
        await item.wait_for(state="visible", timeout=2_000)
        await item.click()
        logger.debug("Clicked 'Deep research' via regex text locator")
        return True
    except Exception:
        pass

    # Strategy 3: menu/role context selectors
    try:
        compound = (
            "[role='menu'] :text-is('Deep research'),"
            "[role='listbox'] :text-is('Deep research'),"
            "[role='menuitem']:has-text('Deep research'),"
            "div.label:text-is('Deep research'),"
            "span:text-is('Deep research')"
        )
        item = page.locator(compound).first
        await item.wait_for(state="visible", timeout=2_000)
        await item.click()
        logger.debug("Clicked 'Deep research' via menu/role selector")
        return True
    except Exception:
        pass

    # Strategy 4: JavaScript broadest fallback
    try:
        clicked = await page.evaluate(
            """() => {
                const all = Array.from(document.querySelectorAll('*'));
                const target = all.find(el =>
                    el.children.length === 0 &&
                    el.textContent.trim().toLowerCase() === 'deep research' &&
                    el.offsetParent !== null);
                if (target) {
                    const clickable = target.closest('button')
                        || target.closest('[role="menuitem"]')
                        || target.closest('[role="option"]')
                        || target.closest('a')
                        || target;
                    clickable.click();
                    return true;
                }
                return false;
            }"""
        )
        if clicked:
            logger.debug("Clicked 'Deep research' via JavaScript")
            return True
    except Exception:
        pass

    logger.warning("Could not find 'Deep research' in dropdown")
    return False


async def _dump_dropdown_diagnostics(page: Any) -> None:
    """Log diagnostic info about the dropdown contents.

    Ported from C# DumpDropdownDiagnosticsAsync (lines 584–609).
    """
    try:
        dump = await page.evaluate(
            """() => {
                const all = Array.from(document.querySelectorAll('*'));
                const visible = all.filter(el =>
                    el.children.length === 0 &&
                    el.offsetParent !== null &&
                    el.textContent.trim().length > 0 &&
                    el.textContent.trim().length < 100);
                const items = visible
                    .map(el => '<' + el.tagName.toLowerCase() + ' class="' + el.className + '"> "' + el.textContent.trim() + '"')
                    .slice(-50);
                return 'VISIBLE TEXT ELEMENTS (last 50):\\n' + items.join('\\n');
            }"""
        )
        logger.error("Deep Research dropdown diagnostic:\n%s", dump)
    except Exception:
        logger.debug("Could not capture dropdown diagnostic")


async def _click_start_research(page: Any, config: ResearchAdapterConfig) -> None:
    """Wait for and click 'Start research' after the plan appears.

    Ported from C# ClickStartResearchAsync (lines 616–687).
    """
    timeout = config.plan_timeout_seconds * 1_000
    quarter = timeout // 4

    # Strategy 1: data-test-id
    try:
        btn = await page.wait_for_selector(
            "button[data-test-id='confirm-button']", timeout=quarter
        )
        if btn:
            await btn.click()
            logger.debug("Clicked 'Start research' via data-test-id")
            return
    except Exception:
        pass

    # Strategy 2: aria-label
    try:
        btn = await page.wait_for_selector(
            "button[aria-label='Start research']", timeout=quarter
        )
        if btn:
            await btn.click()
            logger.debug("Clicked 'Start research' via aria-label")
            return
    except Exception:
        pass

    # Strategy 3: text content
    try:
        btn = await page.wait_for_selector(
            "button:has-text('Start research')", timeout=quarter
        )
        if btn:
            await btn.click()
            logger.debug("Clicked 'Start research' via text content")
            return
    except Exception:
        pass

    # Strategy 4: JavaScript
    clicked = await page.evaluate(
        """() => {
            const buttons = Array.from(document.querySelectorAll('button'));
            let btn = buttons.find(b => b.innerText.trim().includes('Start research'));
            if (!btn) btn = buttons.find(b => b.getAttribute('aria-label') === 'Start research');
            if (!btn) btn = document.querySelector('button[data-test-id="confirm-button"]');
            if (!btn) btn = document.querySelector('.confirm-button');
            if (btn) { btn.click(); return true; }
            return false;
        }"""
    )

    if clicked:
        logger.debug("Clicked 'Start research' via JavaScript")
        return

    raise RuntimeError(
        "Could not find 'Start research' button — the research plan "
        "may not have loaded, or the Gemini UI has changed."
    )


async def _wait_for_export_button(
    page: Any, config: ResearchAdapterConfig
) -> Any:
    """Wait for the Export button — indicates research is complete.

    This is the longest wait — Deep Research takes 5–60 minutes.
    Ported from C# WaitForExportButtonAsync (lines 693–706).
    """
    timeout = config.research_timeout_minutes * 60_000

    export_btn = await page.wait_for_selector(
        "button:has-text('Export')", timeout=timeout
    )

    if export_btn is None:
        raise TimeoutError(
            f"Research did not complete within {config.research_timeout_minutes} "
            "minutes — Export button never appeared."
        )

    return export_btn


async def _export_to_google_docs(
    page: Any, export_btn: Any, config: ResearchAdapterConfig
) -> tuple[Any, str]:
    """Click Export → Export to Docs, capture the Google Doc popup.

    Ported from C# ExportToGoogleDocsAsync (lines 711–742).
    Returns (doc_page, doc_url).
    """
    import asyncio

    # Set up popup listener BEFORE clicking (popup opens asynchronously)
    popup_future = asyncio.create_task(page.wait_for_event("popup"))

    await export_btn.click()
    logger.debug("Clicked Export button")

    # Click "Export to Docs" in the dropdown
    await page.click("text=Export to Docs", timeout=10_000)
    logger.debug("Clicked 'Export to Docs'")

    # Wait for Drive to finish saving
    logger.debug(
        "Waiting %ds for Drive to save", config.export_settle_seconds
    )
    await asyncio.sleep(config.export_settle_seconds)

    # Capture the Google Doc page from the popup
    doc_page = await popup_future
    await doc_page.wait_for_load_state("domcontentloaded")

    doc_url = doc_page.url

    # Clean up common URL suffixes
    doc_url = (
        doc_url.replace("/edit?tab=t.0", "")
        .replace("/edit?pli=1&tab=t.0", "")
    )

    return doc_page, doc_url


async def _try_rename_document(doc_page: Any, new_name: str) -> bool:
    """Rename a Google Doc by interacting with the title bar.

    Returns True if rename succeeded, False if all strategies failed.
    Rename failure is non-fatal — the document still exists in Drive.

    Ported from C# TryRenameDocumentAsync (lines 749–932).
    """
    try:
        await doc_page.bring_to_front()
        await doc_page.wait_for_load_state("networkidle")

        settle_delays_ms = [3_000, 5_000, 8_000]

        for attempt, delay in enumerate(settle_delays_ms, 1):
            await doc_page.wait_for_timeout(delay)
            logger.debug(
                "Rename attempt %d/%d after %dms settle",
                attempt, len(settle_delays_ms), delay,
            )

            # Strategy 1: Click title area to activate, then fill input
            try:
                title_outer = doc_page.locator(".docs-title-outer").first
                await title_outer.wait_for(state="visible", timeout=5_000)
                await title_outer.click()
                await doc_page.wait_for_timeout(500)
            except Exception:
                logger.debug("Title outer container not visible")

            title_input_selectors = [
                "input.docs-title-input-input",
                "input[aria-label='Rename']",
                "input[aria-label='Rename document']",
                ".docs-title-input input[type='text']",
            ]

            for selector in title_input_selectors:
                try:
                    inp = doc_page.locator(selector).first
                    await inp.wait_for(state="visible", timeout=2_000)
                    await inp.click(click_count=3)
                    await inp.fill(new_name)
                    await inp.press("Enter")
                    await doc_page.wait_for_timeout(2_000)
                    logger.debug("Renamed via selector: %s", selector)
                    return True
                except Exception:
                    continue

            # Strategy 2: JavaScript direct manipulation
            try:
                js_result = await doc_page.evaluate(
                    """(name) => {
                        const input = document.querySelector('input.docs-title-input-input')
                            || document.querySelector('input[aria-label="Rename"]')
                            || document.querySelector('input[aria-label="Rename document"]')
                            || document.querySelector('.docs-title-input input');
                        if (input) {
                            input.focus();
                            input.select();
                            input.value = name;
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                            input.dispatchEvent(new Event('change', { bubbles: true }));
                            input.dispatchEvent(new KeyboardEvent('keydown',
                                { key: 'Enter', code: 'Enter', bubbles: true }));
                            return true;
                        }
                        return false;
                    }""",
                    new_name,
                )
                if js_result:
                    await doc_page.wait_for_timeout(2_000)
                    logger.debug("Renamed via JavaScript on attempt %d", attempt)
                    return True
            except Exception:
                pass

            # Strategy 3 (last attempt only): F2 keyboard shortcut
            if attempt == len(settle_delays_ms):
                logger.debug("Trying F2 keyboard shortcut to activate title")
                try:
                    await doc_page.keyboard.press("F2")
                    await doc_page.wait_for_timeout(1_000)
                    focused = doc_page.locator("input:focus").first
                    await focused.wait_for(state="visible", timeout=2_000)
                    await focused.fill(new_name)
                    await focused.press("Enter")
                    await doc_page.wait_for_timeout(2_000)
                    logger.debug("Renamed via F2 keyboard shortcut")
                    return True
                except Exception:
                    pass

        logger.warning(
            "Could not rename document to '%s' — all strategies failed. "
            "Document was created with default Gemini name.",
            new_name,
        )
        return False

    except Exception as exc:
        logger.warning("Error during document rename: %s", exc)
        return False

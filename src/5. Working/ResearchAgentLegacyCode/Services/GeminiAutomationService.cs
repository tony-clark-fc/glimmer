using System.Diagnostics;
using Microsoft.Extensions.Options;
using Microsoft.Playwright;
using ResearchAgent.Models;

namespace ResearchAgent.Services;

/// <summary>
/// Core Gemini Deep Research automation service.
///
/// Drives Chrome via CDP/Playwright to:
///   1. Navigate to Gemini
///   2. Enter the research prompt
///   3. Activate Deep Research mode
///   4. Wait for research to complete (5–60 minutes)
///   5. Export to Google Docs
///   6. Rename the document to the requested name
///
/// Ported from LegacyCode/Program.cs ProcessIndicator() with:
///   - Updated selectors for March 2026 Gemini UI ("Tools" dropdown)
///   - Multi-strategy fallbacks for all interactive elements
///   - Structured logging via ILogger
///   - Configuration via strongly-typed options
///   - Google Doc rename via Playwright title bar interaction (new)
///
/// One research at a time — Gemini Deep Research is single-session per account.
/// </summary>
public class GeminiAutomationService
{
    private readonly ChromeBrowserProvider _browserProvider;
    private readonly ResearchAgentOptions _options;
    private readonly ILogger<GeminiAutomationService> _logger;

    /// <summary>
    /// Serialises all Gemini browser operations (research + chat).
    /// Only one interaction at a time — Gemini is single-session per account.
    /// </summary>
    private readonly SemaphoreSlim _operationLock = new(1, 1);

    /// <summary>
    /// Whether a Gemini operation (research or chat) is currently in progress.
    /// Derived from the operation lock semaphore: count 0 = busy, count 1 = idle.
    /// Used by the <c>GET /api/status</c> endpoint (ARCH:ResearchAgentStatusAPI).
    /// </summary>
    public bool IsBusy => _operationLock.CurrentCount == 0;

    /// <summary>Gemini prompt input textbox selectors (multi-strategy, most→least specific).</summary>
    private static readonly string[] InputSelectors =
    [
        "div[contenteditable][role='textbox'][aria-label='Enter a prompt here']",
        "div[contenteditable='true'][role='textbox']",
        "div.ql-editor[contenteditable='true']",
        "div[contenteditable='plaintext-only']",
        "div[contenteditable='true']"
    ];

    public GeminiAutomationService(
        ChromeBrowserProvider browserProvider,
        IOptions<ResearchAgentOptions> options,
        ILogger<GeminiAutomationService> logger)
    {
        _browserProvider = browserProvider;
        _options = options.Value;
        _logger = logger;
    }

    /// <summary>
    /// Execute one Gemini Deep Research job end-to-end.
    /// </summary>
    public async Task<ResearchResult> ExecuteResearchAsync(
        ResearchJob job, CancellationToken ct)
    {
        var browser = await _browserProvider.GetBrowserAsync(ct)
            ?? throw new InvalidOperationException(
                "Chrome is not available — ensure Chrome is running with " +
                "--remote-debugging-port on the configured port. " +
                "See CHROME_PROFILE_SETUP_GUIDE.md.");

        var context = browser.Contexts.FirstOrDefault()
            ?? await browser.NewContextAsync();

        // Always create a NEW tab so the user sees Gemini open.
        // Reusing context.Pages.FirstOrDefault() would silently hijack
        // whatever tab Chrome already had in focus.
        var page = await context.NewPageAsync();
        await page.BringToFrontAsync();

        _logger.LogInformation(
            "[{JobId}] Starting Gemini Deep Research for '{DocName}'",
            job.Id, job.DocumentName);

        var succeeded = false;
        try
        {
            // ── 1. Navigate to Gemini and ensure clean chat ──
            await NavigateToFreshChatAsync(page, job.Id, ct);

            // Human pacing: page loaded, orient before typing
            await HumanPauseAsync(1500, 2500, "page loaded, looking around", ct);

            // ── 2. Enter the research prompt ──
            var inputLocator = await FindInputBoxAsync(page);
            await inputLocator.FillAsync(job.Prompt);
            _logger.LogInformation(
                "[{JobId}] Prompt entered ({Length:N0} chars)",
                job.Id, job.Prompt.Length);

            // Human pacing: prompt pasted, pause before activating Deep Research
            await HumanPauseAsync(1500, 3000, "reviewing prompt", ct);

            // ── 3. Activate Deep Research mode ──
            // Snapshot the UI before attempting — helps diagnose selector mismatches
            await TrySaveScreenshotAsync(page, job.Id, "pre-deep-research");
            await ActivateDeepResearchAsync(page);

            // Human pacing: Deep Research selected, pause before sending
            await HumanPauseAsync(1000, 2000, "Deep Research activated, about to send", ct);

            // ── 4. Send the prompt ──
            await page.ClickAsync("button[aria-label='Send message']");
            _logger.LogInformation("[{JobId}] Prompt sent", job.Id);

            // ── 5. Click "Start research" when the plan appears ──
            await ClickStartResearchAsync(page, ct);
            _logger.LogInformation("[{JobId}] Research started — waiting for completion", job.Id);

            // ── 6. Wait for research completion (Export button) ──
            var exportBtn = await WaitForExportButtonAsync(page, ct);
            _logger.LogInformation("[{JobId}] Research complete — Export button found", job.Id);

            // ── 7. Export to Google Docs ──
            var (docPage, docUrl) = await ExportToGoogleDocsAsync(page, exportBtn, ct);
            _logger.LogInformation("[{JobId}] Google Doc created: {Url}", job.Id, docUrl);

            // ── 8. Rename the document ──
            var renamed = await TryRenameDocumentAsync(docPage, job.DocumentName);
            if (renamed)
                _logger.LogInformation("[{JobId}] Document renamed to '{Name}'",
                    job.Id, job.DocumentName);
            else
                _logger.LogWarning("[{JobId}] Document rename failed — doc exists but " +
                    "has the default Gemini-generated name", job.Id);

            // ── 9. Close the doc tab ──
            try { await docPage.CloseAsync(); } catch { /* best effort */ }

            succeeded = true;
            return new ResearchResult
            {
                DocumentUrl = docUrl,
                DocumentRenamed = renamed
            };
        }
        catch
        {
            // Capture a diagnostic screenshot on failure
            await TrySaveScreenshotAsync(page, job.Id, "failure");
            throw;
        }
        finally
        {
            if (succeeded)
            {
                // Happy path — clean up the Gemini tab
                try { await page.CloseAsync(); } catch { /* best effort */ }
            }
            else
            {
                // ── Failure: leave the tab open so the operator can see
                //    the Gemini UI state and diagnose selector issues. ──
                _logger.LogWarning(
                    "[{JobId}] Tab left open for debugging — close it manually " +
                    "before submitting the next job",
                    job.Id);
            }
        }
    }

    // ═══════════════════════════════════════════════════════════════════
    // Private helper methods — each phase of the Gemini interaction
    // ═══════════════════════════════════════════════════════════════════

    /// <summary>
    /// Check whether a locator becomes visible within a timeout.
    /// Replaces the obsolete <c>LocatorIsVisibleOptions.Timeout</c> pattern
    /// deprecated in Playwright 1.58+.
    /// </summary>
    private static async Task<bool> IsVisibleWithinAsync(
        ILocator locator, int timeoutMs)
    {
        try
        {
            await locator.WaitForAsync(new LocatorWaitForOptions
            {
                State = WaitForSelectorState.Visible,
                Timeout = timeoutMs
            });
            return true;
        }
        catch (TimeoutException)
        {
            return false;
        }
    }

    /// <summary>
    /// Navigate to Gemini and ensure we have a fresh chat session.
    /// </summary>
    private async Task NavigateToFreshChatAsync(IPage page, Guid jobId, CancellationToken ct)
    {
        _logger.LogInformation("[{JobId}] Navigating to gemini.google.com", jobId);

        await page.GotoAsync("https://gemini.google.com/",
            new PageGotoOptions { Timeout = 30_000, WaitUntil = WaitUntilState.DOMContentLoaded });

        _logger.LogInformation("[{JobId}] Navigation complete — landed on {Url}",
            jobId, page.Url);

        // Wait for the prompt input box to confirm we're on the Gemini page.
        // Uses multi-strategy fallback because Google changes selectors frequently.
        try
        {
            await WaitForInputBoxAsync(page, 30_000);
        }
        catch (TimeoutException)
        {
            // Capture diagnostic info before re-throwing
            _logger.LogError(
                "[{JobId}] Input box not found after 30s. Current URL: {Url}",
                jobId, page.Url);
            await TrySaveScreenshotAsync(page, jobId, "nav-timeout");
            throw new InvalidOperationException(
                $"Gemini input box not found after 30 seconds. " +
                $"Landed on: {page.Url}. " +
                "Check the diagnostic screenshot and verify the Chrome profile " +
                "is signed into Google with Gemini Pro access.");
        }

        _logger.LogDebug("[{JobId}] Input textbox found", jobId);

        // Check if sign-in is required (profile session expired)
        if (await page.QuerySelectorAsync("input[type=email]") is not null)
            throw new InvalidOperationException(
                "Chrome profile is not signed into Google. " +
                "Sign in manually, then restart the API. " +
                "See CHROME_PROFILE_SETUP_GUIDE.md Step 3.");

        // Try to start a new chat to ensure clean state.
        // If we land on an existing conversation, the "New chat" button resets it.
        await TryStartNewChatAsync(page);

        // Re-wait for the input to be ready after potential new-chat navigation
        await WaitForInputBoxAsync(page, 10_000);

        _logger.LogInformation("[{JobId}] Gemini ready — fresh chat confirmed", jobId);
    }

    /// <summary>
    /// Wait for any of the known input box selectors to appear.
    /// </summary>
    private async Task WaitForInputBoxAsync(IPage page, int timeoutMs)
    {
        // Build a compound selector: try all known patterns
        var compound = string.Join(", ", InputSelectors);
        await page.WaitForSelectorAsync(compound,
            new PageWaitForSelectorOptions { Timeout = timeoutMs });
    }

    /// <summary>
    /// Find and return a Locator for the Gemini prompt input box.
    /// Tries each selector in order and returns the first visible one.
    /// </summary>
    private async Task<ILocator> FindInputBoxAsync(IPage page)
    {
        foreach (var selector in InputSelectors)
        {
            var locator = page.Locator(selector).First;
            if (await IsVisibleWithinAsync(locator, 2_000))
            {
                _logger.LogDebug("Using input selector: {Selector}", selector);
                return locator;
            }
        }

        throw new InvalidOperationException(
            "Could not find the Gemini prompt input box. " +
            "The Gemini UI may have changed — check InputSelectors.");
    }

    /// <summary>
    /// Attempt to click "New chat" in the Gemini UI.
    /// Uses multiple selector strategies — if all fail, we proceed anyway
    /// (the current state might already be a fresh chat).
    /// Ported from LegacyCode/Program.cs with selector updates.
    /// </summary>
    private async Task TryStartNewChatAsync(IPage page)
    {
        // Strategy 1: Direct "New chat" button
        string[] newChatSelectors =
        [
            "button:has-text('New chat')",
            "a:has-text('New chat')",
            "div[aria-label='New chat']",
            "[data-test-id='new-chat-button']"
        ];

        foreach (var selector in newChatSelectors)
        {
            try
            {
                var btn = page.Locator(selector).First;
                if (await IsVisibleWithinAsync(btn, 2_000))
                {
                    await btn.ClickAsync();
                    _logger.LogDebug("Clicked 'New chat' via: {Selector}", selector);
                    await Task.Delay(1_000);
                    return;
                }
            }
            catch { /* try next */ }
        }

        // Strategy 2: Open hamburger menu first, then find "New chat"
        try
        {
            var hamburger = page.Locator(
                "button[aria-label='Main menu'], " +
                "button:has(mat-icon[fonticon='menu'])").First;

            if (await IsVisibleWithinAsync(hamburger, 2_000))
            {
                await hamburger.ClickAsync();
                await Task.Delay(1_000);

                foreach (var selector in newChatSelectors)
                {
                    try
                    {
                        var btn = page.Locator(selector).First;
                        if (await IsVisibleWithinAsync(btn, 2_000))
                        {
                            await btn.ClickAsync();
                            _logger.LogDebug(
                                "Clicked 'New chat' after hamburger via: {Selector}",
                                selector);
                            await Task.Delay(1_000);
                            return;
                        }
                    }
                    catch { /* try next */ }
                }
            }
        }
        catch { /* proceed without new chat */ }

        // Strategy 3: JavaScript fallback
        try
        {
            var clicked = await page.EvaluateAsync<bool>("""
                () => {
                    const btn = Array.from(document.querySelectorAll('button, a, div[role="button"]'))
                        .find(el => el.textContent.trim().includes('New chat'));
                    if (btn) { btn.click(); return true; }
                    return false;
                }
            """);

            if (clicked)
            {
                _logger.LogDebug("Clicked 'New chat' via JavaScript");
                await Task.Delay(1_000);
                return;
            }
        }
        catch { /* proceed anyway */ }

        _logger.LogDebug("Could not find 'New chat' button — assuming fresh state");
    }

    /// <summary>
    /// Activate Gemini Deep Research mode.
    /// March 2026 UI flow (confirmed from live screenshot):
    ///   1. Click the "Tools" button (below the prompt input) to open the tools dropdown
    ///   2. Click "Deep research" from the dropdown menu
    /// The dropdown items include: Create image, Canvas, Deep research, Create video, etc.
    /// Text-based selectors are preferred — Google frequently rotates element IDs/classes.
    /// </summary>
    private async Task ActivateDeepResearchAsync(IPage page)
    {
        // ═══════════════════════════════════════════════════════════════
        // Step 1: Open the "Tools" dropdown
        // ═══════════════════════════════════════════════════════════════
        var toolsOpened = await ClickToolsButtonAsync(page);
        if (!toolsOpened)
        {
            throw new InvalidOperationException(
                "Could not find or click the 'Tools' button in the Gemini UI. " +
                "The UI may have changed — check selectors.");
        }

        _logger.LogDebug("Tools dropdown opened — looking for 'Deep research'");

        // Brief pause to let the dropdown animate/render
        await Task.Delay(1_000);

        // ═══════════════════════════════════════════════════════════════
        // Step 2: Click "Deep research" from the dropdown
        // ═══════════════════════════════════════════════════════════════
        var deepResearchClicked = await ClickDeepResearchItemAsync(page);
        if (!deepResearchClicked)
        {
            // Diagnostic: dump what IS in the dropdown
            await DumpDropdownDiagnosticsAsync(page);

            throw new InvalidOperationException(
                "Could not find 'Deep research' in the Tools dropdown. " +
                "The dropdown opened but the menu item was not found. " +
                "Check the diagnostic log for the actual dropdown contents.");
        }

        _logger.LogInformation("Activated Deep Research mode");
        await Task.Delay(500); // Let the UI settle after selection
    }

    /// <summary>
    /// Click the "Tools" button to open the tools dropdown menu.
    /// Multiple strategies for resilience against selector changes.
    /// </summary>
    private async Task<bool> ClickToolsButtonAsync(IPage page)
    {
        // Strategy 1: Playwright text locator (most readable, resilient)
        try
        {
            var btn = page.GetByRole(AriaRole.Button, new() { Name = "Tools" });
            if (await IsVisibleWithinAsync(btn, 3_000))
            {
                await btn.ClickAsync();
                _logger.LogDebug("Clicked 'Tools' via role=button[name=Tools]");
                return true;
            }
        }
        catch { /* try next */ }

        // Strategy 2: Button with text "Tools"
        try
        {
            var btn = page.Locator("button:has-text('Tools')").First;
            if (await IsVisibleWithinAsync(btn, 2_000))
            {
                await btn.ClickAsync();
                _logger.LogDebug("Clicked 'Tools' via button:has-text");
                return true;
            }
        }
        catch { /* try next */ }

        // Strategy 3: Any clickable element with exact "Tools" text
        try
        {
            var btn = page.Locator("text=Tools").First;
            if (await IsVisibleWithinAsync(btn, 2_000))
            {
                await btn.ClickAsync();
                _logger.LogDebug("Clicked 'Tools' via text= locator");
                return true;
            }
        }
        catch { /* try next */ }

        // Strategy 4: JavaScript — find by visible text content
        try
        {
            var clicked = await page.EvaluateAsync<bool>("""
                () => {
                    const candidates = Array.from(document.querySelectorAll(
                        'button, [role="button"], div[role="button"]'));
                    const btn = candidates.find(el =>
                        el.textContent.trim() === 'Tools' ||
                        el.innerText.trim() === 'Tools');
                    if (btn) { btn.click(); return true; }
                    return false;
                }
            """);
            if (clicked)
            {
                _logger.LogDebug("Clicked 'Tools' via JavaScript");
                return true;
            }
        }
        catch { /* fall through */ }

        _logger.LogWarning("Could not find 'Tools' button");
        return false;
    }

    /// <summary>
    /// Click "Deep research" from the already-open Tools dropdown.
    /// </summary>
    private async Task<bool> ClickDeepResearchItemAsync(IPage page)
    {
        // Strategy 1: Playwright text locator — exact text match
        try
        {
            var item = page.GetByText("Deep research", new() { Exact = true });
            if (await IsVisibleWithinAsync(item, 3_000))
            {
                await item.ClickAsync();
                _logger.LogDebug("Clicked 'Deep research' via GetByText(exact)");
                return true;
            }
        }
        catch { /* try next */ }

        // Strategy 2: Case-insensitive text match
        try
        {
            var item = page.Locator(
                "text=/[Dd]eep\\s+[Rr]esearch/").First;
            if (await IsVisibleWithinAsync(item, 2_000))
            {
                await item.ClickAsync();
                _logger.LogDebug("Clicked 'Deep research' via regex text locator");
                return true;
            }
        }
        catch { /* try next */ }

        // Strategy 3: Any element in a menu/dropdown context with matching text
        try
        {
            var item = page.Locator(
                "[role='menu'] :text-is('Deep research')," +
                "[role='listbox'] :text-is('Deep research')," +
                "[role='menuitem']:has-text('Deep research')," +
                "div.label:text-is('Deep research')," +
                "span:text-is('Deep research')").First;
            if (await IsVisibleWithinAsync(item, 2_000))
            {
                await item.ClickAsync();
                _logger.LogDebug("Clicked 'Deep research' via menu/role selector");
                return true;
            }
        }
        catch { /* try next */ }

        // Strategy 4: JavaScript — broadest fallback
        try
        {
            var clicked = await page.EvaluateAsync<bool>("""
                () => {
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
                }
            """);
            if (clicked)
            {
                _logger.LogDebug("Clicked 'Deep research' via JavaScript");
                return true;
            }
        }
        catch { /* fall through */ }

        _logger.LogWarning("Could not find 'Deep research' in dropdown");
        return false;
    }

    /// <summary>
    /// Log diagnostic info about the dropdown contents when Deep research
    /// cannot be found.
    /// </summary>
    private async Task DumpDropdownDiagnosticsAsync(IPage page)
    {
        try
        {
            var dump = await page.EvaluateAsync<string>("""
                () => {
                    // Gather all visible leaf-text elements that might be menu items
                    const all = Array.from(document.querySelectorAll('*'));
                    const visible = all.filter(el =>
                        el.children.length === 0 &&
                        el.offsetParent !== null &&
                        el.textContent.trim().length > 0 &&
                        el.textContent.trim().length < 100);
                    const items = visible
                        .map(el => `<${el.tagName.toLowerCase()} class="${el.className}"> "${el.textContent.trim()}"`)
                        .slice(-50);
                    return 'VISIBLE TEXT ELEMENTS (last 50):\n' + items.join('\n');
                }
            """);
            _logger.LogError("Deep Research dropdown diagnostic:\n{Dump}", dump);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Could not capture dropdown diagnostic");
        }
    }

    /// <summary>
    /// Wait for and click the "Start research" button that appears after
    /// Gemini generates the research plan.
    /// Ported from LegacyCode/Program.cs with all 4 fallback strategies.
    /// </summary>
    private async Task ClickStartResearchAsync(IPage page, CancellationToken ct)
    {
        var timeout = _options.PlanTimeoutSeconds * 1_000;

        // Strategy 1: data-test-id
        try
        {
            var btn = await page.WaitForSelectorAsync(
                "button[data-test-id='confirm-button']",
                new PageWaitForSelectorOptions { Timeout = timeout / 4 });
            if (btn is not null)
            {
                await btn.ClickAsync();
                _logger.LogDebug("Clicked 'Start research' via data-test-id");
                return;
            }
        }
        catch { /* try next */ }

        // Strategy 2: aria-label
        try
        {
            var btn = await page.WaitForSelectorAsync(
                "button[aria-label='Start research']",
                new PageWaitForSelectorOptions { Timeout = timeout / 4 });
            if (btn is not null)
            {
                await btn.ClickAsync();
                _logger.LogDebug("Clicked 'Start research' via aria-label");
                return;
            }
        }
        catch { /* try next */ }

        // Strategy 3: text content
        try
        {
            var btn = await page.WaitForSelectorAsync(
                "button:has-text('Start research')",
                new PageWaitForSelectorOptions { Timeout = timeout / 4 });
            if (btn is not null)
            {
                await btn.ClickAsync();
                _logger.LogDebug("Clicked 'Start research' via text content");
                return;
            }
        }
        catch { /* try next */ }

        // Strategy 4: JavaScript
        var jsClicked = await page.EvaluateAsync<bool>("""
            () => {
                const buttons = Array.from(document.querySelectorAll('button'));
                let btn = buttons.find(b => b.innerText.trim().includes('Start research'));
                if (!btn) btn = buttons.find(b => b.getAttribute('aria-label') === 'Start research');
                if (!btn) btn = document.querySelector('button[data-test-id="confirm-button"]');
                if (!btn) btn = document.querySelector('.confirm-button');
                if (btn) { btn.click(); return true; }
                return false;
            }
        """);

        if (jsClicked)
        {
            _logger.LogDebug("Clicked 'Start research' via JavaScript");
            return;
        }

        throw new InvalidOperationException(
            "Could not find 'Start research' button — the research plan " +
            "may not have loaded, or the Gemini UI has changed.");
    }

    /// <summary>
    /// Wait for the Export button to appear, indicating research is complete.
    /// This is the longest wait — Deep Research takes 5–60 minutes.
    /// </summary>
    private async Task<IElementHandle> WaitForExportButtonAsync(
        IPage page, CancellationToken ct)
    {
        var timeout = _options.ResearchTimeoutMinutes * 60_000;

        var exportBtn = await page.WaitForSelectorAsync(
            "button:has-text('Export')",
            new PageWaitForSelectorOptions { Timeout = timeout });

        return exportBtn
            ?? throw new TimeoutException(
                $"Research did not complete within {_options.ResearchTimeoutMinutes} minutes — " +
                "Export button never appeared.");
    }

    /// <summary>
    /// Click Export → Export to Docs, capture the Google Doc popup page.
    /// </summary>
    private async Task<(IPage DocPage, string DocUrl)> ExportToGoogleDocsAsync(
        IPage page, IElementHandle exportBtn, CancellationToken ct)
    {
        // Set up popup listener BEFORE clicking (popup opens asynchronously)
        var popupTask = page.WaitForPopupAsync();

        await exportBtn.ClickAsync();
        _logger.LogDebug("Clicked Export button");

        // Click "Export to Docs" in the dropdown
        await page.ClickAsync("text=Export to Docs",
            new PageClickOptions { Timeout = 10_000 });
        _logger.LogDebug("Clicked 'Export to Docs'");

        // Wait for Google Drive to finish saving the document
        _logger.LogDebug("Waiting {Seconds}s for Drive to save",
            _options.ExportSettleSeconds);
        await Task.Delay(_options.ExportSettleSeconds * 1_000, ct);

        // Capture the Google Doc page from the popup
        var docPage = await popupTask;
        await docPage.WaitForLoadStateAsync(LoadState.DOMContentLoaded);

        var docUrl = docPage.Url;

        // Clean up common URL suffixes that vary between sessions
        docUrl = docUrl
            .Replace("/edit?tab=t.0", "")
            .Replace("/edit?pli=1&tab=t.0", "");

        return (docPage, docUrl);
    }

    /// <summary>
    /// Rename a Google Doc by interacting with the title bar in the Docs UI.
    /// Returns true if rename succeeded, false if all strategies failed.
    /// Rename failure is non-fatal — the document still exists in Drive.
    /// </summary>
    private async Task<bool> TryRenameDocumentAsync(IPage docPage, string newName)
    {
        try
        {
            // ── Bring the doc tab to the foreground ──
            // Google Docs may not fully render interactive elements (including the
            // title input) when the tab is in the background. This is critical when
            // running via CDP on real Chrome — the Gemini tab still has focus after
            // export. Without this, all selector strategies silently fail because
            // the title input is never placed in the DOM.
            await docPage.BringToFrontAsync();

            // Wait for Google Docs UI to fully load
            await docPage.WaitForLoadStateAsync(LoadState.NetworkIdle);

            // Google Docs is a heavy SPA — the title bar input is rendered
            // asynchronously AFTER the main document content loads. With CDP on
            // real Chrome the timing is less predictable than Playwright-launched
            // browsers. We retry the full rename sequence up to 3 times with
            // increasing settle delays to give the Docs UI time to render.
            int[] settleDelaysMs = [3_000, 5_000, 8_000];

            for (var attempt = 0; attempt < settleDelaysMs.Length; attempt++)
            {
                await Task.Delay(settleDelaysMs[attempt]);

                _logger.LogDebug(
                    "Rename attempt {Attempt}/{Max} after {Delay}ms settle",
                    attempt + 1, settleDelaysMs.Length, settleDelaysMs[attempt]);

                // ── Strategy 1: Click title area to activate input, then fill ──
                try
                {
                    // Click on the outer title container to activate editing
                    var titleOuter = docPage.Locator(".docs-title-outer").First;
                    if (await IsVisibleWithinAsync(titleOuter, 5_000))
                    {
                        _logger.LogDebug("Title outer container found — clicking to activate");
                        await titleOuter.ClickAsync();
                        await Task.Delay(500);
                    }
                    else
                    {
                        _logger.LogDebug("Title outer container (.docs-title-outer) not visible");
                    }
                }
                catch (Exception ex)
                {
                    _logger.LogDebug("Title outer click failed: {Message}", ex.Message);
                }

                // Try known input selectors for the title field
                string[] titleInputSelectors =
                [
                    "input.docs-title-input-input",
                    "input[aria-label='Rename']",
                    "input[aria-label='Rename document']",
                    ".docs-title-input input[type='text']"
                ];

                foreach (var selector in titleInputSelectors)
                {
                    try
                    {
                        var input = docPage.Locator(selector).First;
                        if (await IsVisibleWithinAsync(input, 2_000))
                        {
                            _logger.LogDebug(
                                "Title input found via selector: {Selector} — filling with '{Name}'",
                                selector, newName);

                            // Select all existing text and replace
                            await input.ClickAsync(new LocatorClickOptions { ClickCount = 3 });
                            await input.FillAsync(newName);
                            await input.PressAsync("Enter");
                            await Task.Delay(2_000); // Wait for auto-save

                            _logger.LogDebug(
                                "Renamed document via selector: {Selector}", selector);
                            return true;
                        }
                        else
                        {
                            _logger.LogDebug(
                                "Title input selector not visible: {Selector}", selector);
                        }
                    }
                    catch (Exception ex)
                    {
                        _logger.LogDebug(
                            "Selector {Selector} failed: {Message}", selector, ex.Message);
                    }
                }

                // ── Strategy 2: JavaScript direct manipulation ──
                var jsResult = await docPage.EvaluateAsync<bool>("""
                    (name) => {
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
                    }
                """, newName);

                if (jsResult)
                {
                    await Task.Delay(2_000);
                    _logger.LogDebug("Renamed document via JavaScript on attempt {Attempt}",
                        attempt + 1);
                    return true;
                }

                // ── Strategy 3 (last attempt only): Keyboard shortcut ──
                // Google Docs supports Ctrl+Shift+S or F2 to focus the title input
                // in some builds. Try this as a last resort on the final attempt.
                if (attempt == settleDelaysMs.Length - 1)
                {
                    _logger.LogDebug("Trying keyboard shortcut (F2) to activate title rename");
                    try
                    {
                        // F2 focuses the title field in Google Docs
                        await docPage.Keyboard.PressAsync("F2");
                        await Task.Delay(1_000);

                        // Now try to find the now-focused input
                        var focusedInput = docPage.Locator("input:focus").First;
                        if (await IsVisibleWithinAsync(focusedInput, 2_000))
                        {
                            await focusedInput.FillAsync(newName);
                            await focusedInput.PressAsync("Enter");
                            await Task.Delay(2_000);
                            _logger.LogDebug("Renamed document via F2 keyboard shortcut");
                            return true;
                        }
                    }
                    catch (Exception ex)
                    {
                        _logger.LogDebug("F2 shortcut strategy failed: {Message}", ex.Message);
                    }
                }

                _logger.LogDebug(
                    "Rename attempt {Attempt} failed — all strategies exhausted for this attempt",
                    attempt + 1);
            }

            // ── Final diagnostic: dump what we can see ──
            try
            {
                var pageTitle = await docPage.TitleAsync();
                var pageUrl = docPage.Url;
                _logger.LogWarning(
                    "Could not rename document to '{Name}' — all strategies failed after {Attempts} attempts. " +
                    "Page title: '{PageTitle}', URL: '{PageUrl}'. " +
                    "Document was created with default Gemini name.",
                    newName, settleDelaysMs.Length, pageTitle, pageUrl);
            }
            catch
            {
                _logger.LogWarning(
                    "Could not rename document to '{Name}' — all strategies failed. " +
                    "Document was created with default Gemini name.", newName);
            }

            return false;
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex,
                "Error during document rename to '{Name}'", newName);
            return false;
        }
    }

    // ═══════════════════════════════════════════════════════════════════
    // Synchronous Chat — POST /api/chat flow
    // ═══════════════════════════════════════════════════════════════════

    /// <summary>
    /// Execute a synchronous Gemini chat interaction.
    /// Opens a fresh chat, selects the requested mode, sends the prompt,
    /// waits for the response, and returns the text.
    /// </summary>
    public async Task<ChatResult> ExecuteChatAsync(
        ChatRequest request, CancellationToken ct)
    {
        // Acquire the operation lock — returns 409 if another op is in progress
        if (!await _operationLock.WaitAsync(TimeSpan.FromSeconds(5), ct))
            throw new InvalidOperationException(
                "Another Gemini operation is in progress — " +
                "only one interaction at a time is supported.");

        try
        {
            var sw = Stopwatch.StartNew();

            var browser = await _browserProvider.GetBrowserAsync(ct)
                ?? throw new InvalidOperationException(
                    "Chrome is not available — ensure Chrome is running with " +
                    "--remote-debugging-port on the configured port.");

            var context = browser.Contexts.FirstOrDefault()
                ?? await browser.NewContextAsync();

            var page = await context.NewPageAsync();
            await page.BringToFrontAsync();

            _logger.LogInformation(
                "Starting Gemini chat — mode: {Mode}, prompt length: {Length:N0}",
                request.Mode, request.Prompt.Length);

            try
            {
                // ── 1. Navigate to Gemini ──
                await page.GotoAsync("https://gemini.google.com/app",
                    new PageGotoOptions
                    {
                        Timeout = 30_000,
                        WaitUntil = WaitUntilState.DOMContentLoaded
                    });
                await WaitForInputBoxAsync(page, 30_000);

                // Human pacing: page just loaded, pause before interacting
                await HumanPauseAsync(1500, 2500, "page loaded, looking around", ct);

                // ── 2. Expand sidebar → click New Chat ──
                await EnsureFreshChatViaMenuAsync(page);
                await WaitForInputBoxAsync(page, 10_000);

                // Human pacing: fresh chat ready, pause before picking mode
                await HumanPauseAsync(1000, 2000, "new chat ready", ct);

                // ── 3. Select the requested mode ──
                await SelectGeminiModeAsync(page, request.Mode);

                // Human pacing: mode selected, pause before typing
                await HumanPauseAsync(1000, 2000, "mode selected, about to type", ct);

                // ── 4. Enter prompt ──
                var inputLocator = await FindInputBoxAsync(page);
                await inputLocator.FillAsync(request.Prompt);
                _logger.LogDebug(
                    "Prompt entered ({Length:N0} chars)", request.Prompt.Length);

                // Human pacing: prompt pasted, pause before hitting send
                await HumanPauseAsync(1500, 3000, "reviewing prompt before send", ct);

                // ── 5. Send the prompt ──
                await page.ClickAsync("button[aria-label='Send message']",
                    new PageClickOptions { Timeout = 5_000 });
                _logger.LogInformation("Prompt sent — waiting for response");

                // ── 6. Wait for response and capture text ──
                var responseText = await WaitForResponseAndCopyAsync(page, ct);

                sw.Stop();
                _logger.LogInformation(
                    "Chat complete — {Length:N0} chars in {Duration:N1}s",
                    responseText.Length, sw.Elapsed.TotalSeconds);

                return new ChatResult
                {
                    ResponseText = responseText,
                    Mode = request.Mode,
                    DurationMs = sw.ElapsedMilliseconds
                };
            }
            catch
            {
                await TrySaveScreenshotAsync(page, Guid.NewGuid(), "chat-failure");
                throw;
            }
            finally
            {
                try { await page.CloseAsync(); }
                catch { /* best effort */ }
            }
        }
        finally
        {
            _operationLock.Release();
        }
    }

    /// <summary>
    /// Ensure a fresh Gemini chat by expanding the sidebar and clicking "New chat".
    /// Uses the operator-provided HTML selectors (March 2026 Gemini UI).
    /// </summary>
    private async Task EnsureFreshChatViaMenuAsync(IPage page)
    {
        // Check if the sidebar "New chat" link is already visible
        // (data-test-id="expanded-button" with aria-label="New chat")
        var newChatBtn = page.Locator(
            "a[data-test-id='expanded-button'][aria-label='New chat']").First;

        if (!await IsVisibleWithinAsync(newChatBtn, 2_000))
        {
            // Sidebar is collapsed — click the hamburger menu to expand it
            _logger.LogDebug("Sidebar collapsed — expanding via hamburger menu");

            var hamburgerClicked = false;

            // Strategy 1: data-test-id selector
            try
            {
                var hamburger = page.Locator(
                    "button[data-test-id='side-nav-menu-button']").First;
                if (await IsVisibleWithinAsync(hamburger, 2_000))
                {
                    await hamburger.ClickAsync();
                    hamburgerClicked = true;
                    _logger.LogDebug("Clicked hamburger via data-test-id");
                }
            }
            catch { /* try next */ }

            // Strategy 2: aria-label
            if (!hamburgerClicked)
            {
                try
                {
                    var hamburger = page.Locator(
                        "button[aria-label='Main menu']").First;
                    if (await IsVisibleWithinAsync(hamburger, 2_000))
                    {
                        await hamburger.ClickAsync();
                        hamburgerClicked = true;
                        _logger.LogDebug("Clicked hamburger via aria-label");
                    }
                }
                catch { /* try next */ }
            }

            // Strategy 3: mat-icon with menu fonticon
            if (!hamburgerClicked)
            {
                try
                {
                    var hamburger = page.Locator(
                        "button:has(mat-icon[fonticon='menu'])").First;
                    if (await IsVisibleWithinAsync(hamburger, 2_000))
                    {
                        await hamburger.ClickAsync();
                        hamburgerClicked = true;
                        _logger.LogDebug("Clicked hamburger via mat-icon[fonticon=menu]");
                    }
                }
                catch { /* try next */ }
            }

            if (!hamburgerClicked)
            {
                _logger.LogWarning(
                    "Could not find hamburger menu — trying direct navigation");
                await page.GotoAsync("https://gemini.google.com/app");
                await WaitForInputBoxAsync(page, 10_000);
                return;
            }

            await Task.Delay(800); // Let sidebar animate open
        }

        // Now click the "New chat" button in the expanded sidebar
        newChatBtn = page.Locator(
            "a[data-test-id='expanded-button'][aria-label='New chat']").First;

        if (await IsVisibleWithinAsync(newChatBtn, 3_000))
        {
            await newChatBtn.ClickAsync();
            _logger.LogDebug("Clicked 'New chat' in sidebar");
            await Task.Delay(1_000); // Let navigation settle
        }
        else
        {
            // Fallback: try broader selectors
            string[] fallbackSelectors =
            [
                "a[aria-label='New chat']",
                "a:has-text('New chat')",
                "button:has-text('New chat')"
            ];

            var clicked = false;
            foreach (var selector in fallbackSelectors)
            {
                try
                {
                    var btn = page.Locator(selector).First;
                    if (await IsVisibleWithinAsync(btn, 2_000))
                    {
                        await btn.ClickAsync();
                        clicked = true;
                        _logger.LogDebug(
                            "Clicked 'New chat' via fallback: {Selector}", selector);
                        await Task.Delay(1_000);
                        break;
                    }
                }
                catch { /* try next */ }
            }

            if (!clicked)
            {
                // Last resort: JS click
                var jsClicked = await page.EvaluateAsync<bool>("""
                    () => {
                        const link = Array.from(document.querySelectorAll('a, button'))
                            .find(el => el.textContent.trim().includes('New chat'));
                        if (link) { link.click(); return true; }
                        return false;
                    }
                """);

                if (jsClicked)
                {
                    _logger.LogDebug("Clicked 'New chat' via JavaScript");
                    await Task.Delay(1_000);
                }
                else
                {
                    _logger.LogWarning(
                        "Could not find 'New chat' — navigating directly");
                    await page.GotoAsync("https://gemini.google.com/app");
                }
            }
        }

        _logger.LogInformation("Fresh chat confirmed");
    }

    /// <summary>
    /// Select the Gemini mode (Fast / Thinking / Pro) from the mode picker dropdown.
    /// Skips selection if the current mode already matches.
    /// </summary>
    private async Task SelectGeminiModeAsync(IPage page, string mode)
    {
        // ── Find the mode picker button ──
        var modeBtn = page.Locator(
            "button[data-test-id='bard-mode-menu-button']").First;

        if (!await IsVisibleWithinAsync(modeBtn, 5_000))
        {
            _logger.LogWarning(
                "Mode picker button not found — proceeding with current default mode");
            return;
        }

        // ── Check if we're already in the desired mode ──
        try
        {
            var currentModeText = await page.Locator(
                "[data-test-id='logo-pill-label-container'] span")
                .First.InnerTextAsync();

            if (currentModeText.Trim().Equals(mode, StringComparison.OrdinalIgnoreCase))
            {
                _logger.LogDebug("Already in {Mode} mode — no switch needed", mode);
                return;
            }

            _logger.LogDebug(
                "Current mode is '{Current}', switching to '{Target}'",
                currentModeText.Trim(), mode);
        }
        catch
        {
            _logger.LogDebug("Could not read current mode — will attempt selection");
        }

        // ── Open the mode picker dropdown ──
        await modeBtn.ClickAsync();
        await Task.Delay(600); // Let dropdown animate

        // ── Click the desired mode option ──
        // Strategy 1: Playwright exact text match on leaf text nodes
        var selected = false;

        try
        {
            // Use a selector targeting the specific mode text inside the dropdown
            // The dropdown is rendered in a CDK overlay panel
            var modeOption = page.GetByText(mode, new() { Exact = true }).First;
            if (await IsVisibleWithinAsync(modeOption, 3_000))
            {
                await modeOption.ClickAsync();
                selected = true;
                _logger.LogDebug("Selected mode '{Mode}' via GetByText(exact)", mode);
            }
        }
        catch { /* try next */ }

        // Strategy 2: JavaScript — find by visible leaf text content
        if (!selected)
        {
            try
            {
                selected = await page.EvaluateAsync<bool>("""
                    (targetMode) => {
                        const candidates = Array.from(document.querySelectorAll('*'));
                        const match = candidates.find(el =>
                            el.children.length === 0 &&
                            el.textContent.trim() === targetMode &&
                            el.offsetParent !== null);
                        if (match) {
                            const clickable = match.closest('button')
                                || match.closest('[role="menuitem"]')
                                || match.closest('[role="option"]')
                                || match.closest('mat-option')
                                || match.closest('[mat-menu-item]')
                                || match.closest('a')
                                || match;
                            clickable.click();
                            return true;
                        }
                        return false;
                    }
                """, mode);

                if (selected)
                    _logger.LogDebug("Selected mode '{Mode}' via JavaScript", mode);
            }
            catch { /* fall through */ }
        }

        if (selected)
        {
            _logger.LogInformation("Gemini mode set to: {Mode}", mode);
            await Task.Delay(500); // Let UI settle after selection
        }
        else
        {
            // Close the dropdown if mode selection failed
            await page.Keyboard.PressAsync("Escape");
            _logger.LogWarning(
                "Could not select mode '{Mode}' — proceeding with current mode. " +
                "Check that the mode name matches the Gemini UI text exactly.", mode);
        }
    }

    /// <summary>
    /// Wait for Gemini to finish responding, then capture the response text
    /// by clicking the "Copy response" button and intercepting the clipboard write.
    /// Falls back to DOM text extraction if clipboard capture fails.
    /// </summary>
    private async Task<string> WaitForResponseAndCopyAsync(
        IPage page, CancellationToken ct)
    {
        var timeout = _options.ChatResponseTimeoutSeconds * 1_000;

        // ── Wait for the copy button to appear — indicates response is complete ──
        // In "Thinking" mode there's a thinking phase first, then the response
        // streams in. The copy button only appears once the full response is done.
        _logger.LogDebug(
            "Waiting up to {Timeout}s for response (copy button appearance)",
            _options.ChatResponseTimeoutSeconds);

        var copyBtn = page.Locator("button[data-test-id='copy-button']").Last;

        try
        {
            await copyBtn.WaitForAsync(new LocatorWaitForOptions
            {
                State = WaitForSelectorState.Visible,
                Timeout = timeout
            });
        }
        catch (TimeoutException)
        {
            throw new TimeoutException(
                $"Gemini did not finish responding within " +
                $"{_options.ChatResponseTimeoutSeconds} seconds. " +
                "The response may still be generating, or the copy button " +
                "selector has changed.");
        }

        _logger.LogDebug("Copy button visible — response complete");

        // Human pacing: response just appeared, pause to "read" before copying
        await HumanPauseAsync(2000, 4000, "reading response before copy", ct);

        // ── Click the copy button to populate the clipboard ──
        await copyBtn.ClickAsync();
        await Task.Delay(800); // Brief pause for clipboard write to complete

        // ── Strategy 1 (primary): read clipboard directly ──
        // Proven reliable in live testing — Gemini's copy button uses
        // navigator.clipboard.writeText which we can read back.
        string? text = null;
        try
        {
            text = await page.EvaluateAsync<string?>(
                "() => navigator.clipboard.readText()");
            if (!string.IsNullOrWhiteSpace(text))
            {
                _logger.LogDebug(
                    "Captured response via clipboard.readText ({Length:N0} chars)",
                    text.Length);
                return text;
            }
        }
        catch (Exception ex)
        {
            _logger.LogDebug(ex, "clipboard.readText() failed — trying intercept");
        }

        // ── Strategy 2: clipboard writeText intercept ──
        // Gemini may override clipboard.writeText itself, so this is a
        // secondary strategy. Install hook, click copy again, read captured text.
        _logger.LogDebug("Primary clipboard read empty — trying intercept strategy");
        try
        {
            await page.EvaluateAsync("""
                () => {
                    window.__geminiCopiedText = null;
                    const origWrite = navigator.clipboard.writeText.bind(navigator.clipboard);
                    navigator.clipboard.writeText = async (text) => {
                        window.__geminiCopiedText = text;
                        return origWrite(text);
                    };
                }
            """);

            await copyBtn.ClickAsync();
            await Task.Delay(800);

            text = await page.EvaluateAsync<string?>(
                "() => window.__geminiCopiedText");

            if (!string.IsNullOrWhiteSpace(text))
            {
                _logger.LogDebug(
                    "Captured response via clipboard intercept ({Length:N0} chars)",
                    text.Length);
                return text;
            }
        }
        catch (Exception ex)
        {
            _logger.LogDebug(ex, "Clipboard intercept failed — trying DOM extraction");
        }

        // ── Strategy 3: extract text from the response DOM ──
        _logger.LogWarning("Clipboard strategies failed — falling back to DOM extraction");
        text = await page.EvaluateAsync<string?>("""
            () => {
                // Try known response container selectors (March 2026 Gemini UI)
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

                // Broadest fallback — find the largest text block that appeared
                // after the user message (heuristic)
                const all = Array.from(document.querySelectorAll('.markdown'));
                if (all.length > 0) {
                    const last = all[all.length - 1];
                    return last.innerText?.trim() || null;
                }
                return null;
            }
        """);

        if (!string.IsNullOrWhiteSpace(text))
        {
            _logger.LogDebug(
                "Captured response via DOM extraction ({Length:N0} chars)",
                text.Length);
            return text;
        }

        throw new InvalidOperationException(
            "Could not extract Gemini response text — " +
            "clipboard intercept, clipboard read, and DOM extraction all failed. " +
            "Check the diagnostic screenshot for UI state.");
    }

    /// <summary>
    /// Simulate a real user by pausing for a randomised duration between interactions.
    /// Delays are jittered between <paramref name="minMs"/> and <paramref name="maxMs"/>
    /// to avoid a robotic cadence that could trigger bot detection.
    /// </summary>
    private async Task HumanPauseAsync(
        int minMs, int maxMs, string context, CancellationToken ct)
    {
        var delay = Random.Shared.Next(minMs, maxMs + 1);
        _logger.LogDebug("Human pacing: {Context} — waiting {Delay}ms", context, delay);
        await Task.Delay(delay, ct);
    }

    /// <summary>
    /// Save a diagnostic screenshot on failure. Best-effort — never throws.
    /// Screenshots are saved to the app's content root directory.
    /// </summary>
    private async Task TrySaveScreenshotAsync(IPage page, Guid jobId, string suffix = "failure")
    {
        try
        {
            var path = Path.Combine(
                AppContext.BaseDirectory, $"{suffix}_{jobId:N}.png");
            await page.ScreenshotAsync(new PageScreenshotOptions
            {
                Path = path,
                FullPage = true
            });
            _logger.LogWarning(
                "[{JobId}] Diagnostic screenshot saved: {Path}",
                jobId, path);
        }
        catch (Exception ex)
        {
            _logger.LogDebug(ex,
                "[{JobId}] Could not save diagnostic screenshot", jobId);
        }
    }
}



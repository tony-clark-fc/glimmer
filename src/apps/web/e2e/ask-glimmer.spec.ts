/**
 * E16 — Cross-surface "Ask Glimmer" contextual interaction — Playwright tests.
 *
 * TEST:UI.AskGlimmer.AffordanceVisibleOnDataElements
 * TEST:UI.AskGlimmer.ResponseRespectsReviewGates
 *
 * Proves:
 * 1. The sparkle ✦ affordance is visible on data elements across surfaces
 * 2. The popover opens with input and submit controls
 * 3. Response display and review badge behavior
 */

import { test, expect } from "@playwright/test";

// ── API route mocking ────────────────────────────────────────────────

async function mockCommonRoutes(page: import("@playwright/test").Page) {
  // Persona mood
  await page.route("**/persona/mood", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ mood: "bau", reason: "Business as usual", portfolio_health: { active_projects: 2, active_blockers: 0, overdue_items: 0, high_risks: 0 } }),
    }),
  );

  // Persona sessions
  await page.route("**/persona/sessions", (route) => {
    if (route.request().method() === "POST") {
      return route.fulfill({
        status: 201,
        contentType: "application/json",
        body: JSON.stringify({ id: "test-session-1", session_status: "active", workspace_mode: "update", messages: [] }),
      });
    }
    return route.fulfill({ status: 200, contentType: "application/json", body: "[]" });
  });

  // Ask Glimmer contextual
  await page.route("**/ask/contextual", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        reply: "This project is on track with 3 open items and no major blockers.",
        review_required: false,
        review_reason: null,
        used_llm: false,
        inference_latency_ms: 0,
      }),
    }),
  );
}

// ── TEST:UI.AskGlimmer.AffordanceVisibleOnDataElements ──────────────

test.describe("Ask Glimmer affordance visibility", () => {
  test("sparkle trigger visible on Today page action items", async ({ page }) => {
    await mockCommonRoutes(page);

    // Mock focus pack with action items
    await page.route("**/triage/focus-pack/latest", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          id: "fp-1",
          generated_at: new Date().toISOString(),
          narrative_summary: "Test brief",
          top_actions: {
            items: [
              { item_id: "act-1", item_type: "work_item", project_id: "p1", priority_score: 0.8, rationale: "Important", title: "Complete specs" },
            ],
          },
          high_risk_items: {
            items: [
              { risk_id: "r-1", project_id: "p1", summary: "Budget overrun", severity: "high" },
            ],
          },
          waiting_on_items: {
            items: [
              { waiting_id: "w-1", project_id: "p1", waiting_on: "Alice", description: "Specs review", expected_by: null },
            ],
          },
          reply_debt_summary: null,
          calendar_pressure_summary: null,
        }),
      }),
    );

    await page.route("**/health/research", (route) =>
      route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ chrome_status: "unknown", chrome_port: 9222, chrome_port_open: false, last_check_at: null, last_transition_at: null, consecutive_failures: 0, monitor_running: false }) }),
    );

    await page.goto("/today");
    await page.waitForSelector('[data-testid="today-focus-pack"]');

    // Sparkle should be visible on action items, risks, and waiting-on items
    const triggers = page.locator('[data-testid="ask-glimmer-trigger"]');
    await expect(triggers.first()).toBeVisible();
    expect(await triggers.count()).toBeGreaterThanOrEqual(3);
  });

  test("sparkle trigger visible on Portfolio page project cards", async ({ page }) => {
    await mockCommonRoutes(page);

    await page.route("**/projects*", (route) => {
      if (route.request().url().includes("/projects/")) return route.fallback();
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([
          { id: "p1", name: "Phoenix", status: "active", objective: "Launch v1", short_summary: "Core product", open_items: 5, active_blockers: 1, pending_actions: 2, archived: false, created_at: new Date().toISOString() },
          { id: "p2", name: "Aurora", status: "active", objective: "Research", short_summary: "R&D", open_items: 3, active_blockers: 0, pending_actions: 1, archived: false, created_at: new Date().toISOString() },
        ]),
      });
    });

    await page.goto("/portfolio");
    await page.waitForSelector('[data-testid="portfolio-project-list"]');

    const triggers = page.locator('[data-testid="ask-glimmer-trigger"]');
    await expect(triggers.first()).toBeVisible();
    expect(await triggers.count()).toBeGreaterThanOrEqual(2);
  });

  test("sparkle trigger visible on Triage page items", async ({ page }) => {
    await mockCommonRoutes(page);

    await page.route("**/triage/review-queue", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          classifications: [
            { id: "c1", source_record_id: "sr-1", source_record_type: "email", selected_project_id: null, confidence: 0.7, ambiguity_flag: true, classification_rationale: "Looks project-related", review_state: "pending", created_at: new Date().toISOString() },
          ],
          actions: [
            { id: "a1", source_record_id: "sr-2", source_record_type: "email", linked_project_id: null, action_text: "Follow up on specs", urgency_signal: "medium", review_state: "pending", created_at: new Date().toISOString() },
          ],
          total_pending: 2,
        }),
      }),
    );

    await page.goto("/triage");
    await page.waitForSelector('[data-testid="triage-classifications"]');

    const triggers = page.locator('[data-testid="ask-glimmer-trigger"]');
    await expect(triggers.first()).toBeVisible();
    expect(await triggers.count()).toBeGreaterThanOrEqual(2);
  });
});

// ── TEST:UI.AskGlimmer.ResponseRespectsReviewGates ──────────────────

test.describe("Ask Glimmer popover interaction", () => {
  test("clicking sparkle opens popover with input", async ({ page }) => {
    await mockCommonRoutes(page);

    await page.route("**/projects*", (route) => {
      if (route.request().url().includes("/projects/")) return route.fallback();
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([
          { id: "p1", name: "Phoenix", status: "active", objective: null, short_summary: null, open_items: 3, active_blockers: 0, pending_actions: 1, archived: false, created_at: new Date().toISOString() },
        ]),
      });
    });

    await page.goto("/portfolio");
    await page.waitForSelector('[data-testid="portfolio-project-list"]');

    // Click sparkle trigger
    await page.locator('[data-testid="ask-glimmer-trigger"]').first().click();

    // Popover should appear with input and submit
    await expect(page.locator('[data-testid="ask-glimmer-popover"]')).toBeVisible();
    await expect(page.locator('[data-testid="ask-glimmer-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="ask-glimmer-submit"]')).toBeVisible();
  });

  test("submitting question shows Glimmer reply", async ({ page }) => {
    await mockCommonRoutes(page);

    await page.route("**/projects*", (route) => {
      if (route.request().url().includes("/projects/")) return route.fallback();
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([
          { id: "p1", name: "Phoenix", status: "active", objective: null, short_summary: null, open_items: 3, active_blockers: 0, pending_actions: 1, archived: false, created_at: new Date().toISOString() },
        ]),
      });
    });

    await page.goto("/portfolio");
    await page.waitForSelector('[data-testid="portfolio-project-list"]');

    await page.locator('[data-testid="ask-glimmer-trigger"]').first().click();
    await page.locator('[data-testid="ask-glimmer-input"]').fill("What is the status?");
    await page.locator('[data-testid="ask-glimmer-submit"]').click();

    // Should show reply
    await expect(page.locator('[data-testid="ask-glimmer-reply"]')).toBeVisible({ timeout: 5000 });
    const replyText = await page.locator('[data-testid="ask-glimmer-reply"]').textContent();
    expect(replyText?.length).toBeGreaterThan(0);
  });

  test("review-required response shows review badge", async ({ page }) => {
    await mockCommonRoutes(page);

    // Override the ask contextual mock to return review_required
    await page.route("**/ask/contextual", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          reply: "I can draft a follow-up email to the stakeholder about the timeline.",
          review_required: true,
          review_reason: "Response implies an externally meaningful action that requires operator approval.",
          used_llm: false,
          inference_latency_ms: 0,
        }),
      }),
    );

    await page.route("**/projects*", (route) => {
      if (route.request().url().includes("/projects/")) return route.fallback();
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([
          { id: "p1", name: "Phoenix", status: "active", objective: null, short_summary: null, open_items: 3, active_blockers: 0, pending_actions: 1, archived: false, created_at: new Date().toISOString() },
        ]),
      });
    });

    await page.goto("/portfolio");
    await page.waitForSelector('[data-testid="portfolio-project-list"]');

    await page.locator('[data-testid="ask-glimmer-trigger"]').first().click();
    await page.locator('[data-testid="ask-glimmer-input"]').fill("Draft a follow-up email");
    await page.locator('[data-testid="ask-glimmer-submit"]').click();

    // Should show reply AND review badge
    await expect(page.locator('[data-testid="ask-glimmer-reply"]')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('[data-testid="ask-glimmer-review-badge"]')).toBeVisible();
  });

  test("popover closes on Escape key", async ({ page }) => {
    await mockCommonRoutes(page);

    await page.route("**/projects*", (route) => {
      if (route.request().url().includes("/projects/")) return route.fallback();
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([
          { id: "p1", name: "Phoenix", status: "active", objective: null, short_summary: null, open_items: 3, active_blockers: 0, pending_actions: 1, archived: false, created_at: new Date().toISOString() },
        ]),
      });
    });

    await page.goto("/portfolio");
    await page.waitForSelector('[data-testid="portfolio-project-list"]');

    await page.locator('[data-testid="ask-glimmer-trigger"]').first().click();
    await expect(page.locator('[data-testid="ask-glimmer-popover"]')).toBeVisible();

    await page.keyboard.press("Escape");
    await expect(page.locator('[data-testid="ask-glimmer-popover"]')).not.toBeVisible();
  });
});


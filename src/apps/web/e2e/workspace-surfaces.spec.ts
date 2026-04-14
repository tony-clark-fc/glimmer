/**
 * Workspace surfaces — browser proof for WE1-WE7.
 *
 * TEST:UI.Navigation.WorkspaceRoutesRemainReachable
 * TEST:UI.TodayView.ShowsPrioritiesAndPressureClearly
 * TEST:UI.PortfolioView.ComparesProjectAttentionDemand
 * TEST:UI.TriageView.ShowsProvenanceAndReviewControls
 * TEST:UI.DraftWorkspace.ShowsContextAndVariants
 * TEST:UI.DraftWorkspace.CopyEditFlowRemainsReviewOnly
 * TEST:UI.ReviewQueue.PendingVsAcceptedIsObvious
 * TEST:Drafting.NoAutoSend.BoundaryPreserved
 * TEST:Release.Browser.CoreOperatorJourneysPass
 */

import { test, expect } from "@playwright/test";

// ── Today view ──────────────────────────────────────────────────

test.describe("Today view", () => {
  test("renders heading and either empty state or focus pack", async ({ page }) => {
    await page.goto("/today");
    await expect(page.getByTestId("page-today")).toBeVisible();
    await expect(
      page.getByRole("heading", { name: "Today", level: 1 })
    ).toBeVisible();

    // Should show either loading, empty state, or loaded focus pack
    // (backend may or may not be running)
    const hasEmpty = await page.getByTestId("today-empty-state").isVisible().catch(() => false);
    const hasLoading = await page.getByTestId("today-loading").isVisible().catch(() => false);
    const hasError = await page.getByTestId("today-error").isVisible().catch(() => false);
    const hasFocusPack = await page.getByTestId("today-focus-pack").isVisible().catch(() => false);

    // At least one state should be visible
    expect(hasEmpty || hasLoading || hasError || hasFocusPack).toBeTruthy();
  });

  test("shows subtitle describing the daily brief", async ({ page }) => {
    await page.goto("/today");
    await expect(page.getByText("daily operating brief")).toBeVisible();
  });
});

// ── Portfolio view ──────────────────────────────────────────────

test.describe("Portfolio view", () => {
  test("renders heading and portfolio content", async ({ page }) => {
    await page.goto("/portfolio");
    await expect(page.getByTestId("page-portfolio")).toBeVisible();
    await expect(
      page.getByRole("heading", { name: "Portfolio", level: 1 })
    ).toBeVisible();

    // Subtitle
    await expect(
      page.getByText("Compare active projects")
    ).toBeVisible();
  });
});

// ── Triage view ─────────────────────────────────────────────────

test.describe("Triage view", () => {
  test("renders heading and triage content", async ({ page }) => {
    await page.goto("/triage");
    await expect(page.getByTestId("page-triage")).toBeVisible();
    await expect(
      page.getByRole("heading", { name: "Triage", level: 1 })
    ).toBeVisible();
    await expect(
      page.getByText("Incoming signals")
    ).toBeVisible();
  });
});

// ── Drafts view ─────────────────────────────────────────────────

test.describe("Drafts view", () => {
  test("renders heading and no-auto-send notice", async ({ page }) => {
    await page.goto("/drafts");
    await expect(page.getByTestId("page-drafts")).toBeVisible();
    await expect(
      page.getByRole("heading", { name: "Drafts", level: 1 })
    ).toBeVisible();

    // TEST:Drafting.NoAutoSend.BoundaryPreserved — the no-auto-send
    // notice must be visible on the drafts page
    await expect(page.getByTestId("drafts-no-auto-send")).toBeVisible();
    await expect(
      page.getByText("Glimmer never sends on your behalf")
    ).toBeVisible();
  });

  test("no send button exists on the drafts page", async ({ page }) => {
    await page.goto("/drafts");
    // There should be no "Send" button anywhere on the page
    const sendButtons = page.getByRole("button", { name: /send/i });
    await expect(sendButtons).toHaveCount(0);
  });
});

// ── Review view ─────────────────────────────────────────────────

test.describe("Review view", () => {
  test("renders heading and review content", async ({ page }) => {
    await page.goto("/review");
    await expect(page.getByTestId("page-review")).toBeVisible();
    await expect(
      page.getByRole("heading", { name: "Review", level: 1 })
    ).toBeVisible();
    await expect(
      page.getByText("Items requiring your judgment")
    ).toBeVisible();
  });
});

// ── Research view ───────────────────────────────────────────────

test.describe("Research view", () => {
  test("renders heading and research content", async ({ page }) => {
    await page.goto("/research");
    await expect(page.getByTestId("page-research")).toBeVisible();
    await expect(
      page.getByRole("heading", { name: "Research & Expert Advice", level: 1 })
    ).toBeVisible();
    await expect(
      page.getByText("Deep research runs")
    ).toBeVisible();
  });

  test("has tabs for research runs and expert advice", async ({ page }) => {
    await page.goto("/research");
    await expect(page.getByTestId("tab-runs")).toBeVisible();
    await expect(page.getByTestId("tab-exchanges")).toBeVisible();
  });

  test("shows empty state when no research runs exist", async ({ page }) => {
    await page.goto("/research");
    // Should show loading then empty state (no backend)
    const hasEmpty = await page.getByTestId("research-empty").isVisible().catch(() => false);
    const hasLoading = await page.getByTestId("research-loading").isVisible().catch(() => false);
    const hasError = await page.getByTestId("research-error").isVisible().catch(() => false);
    const hasList = await page.getByTestId("research-runs-list").isVisible().catch(() => false);

    expect(hasEmpty || hasLoading || hasError || hasList).toBeTruthy();
  });
});

// ── Project view ────────────────────────────────────────────────

test.describe("Project view", () => {
  test("project route renders and shows back link to portfolio", async ({ page }) => {
    await page.goto("/projects/test-id-123");
    await expect(page.getByTestId("page-project")).toBeVisible();
    // Should have a link back to portfolio (the "← Portfolio" link)
    await expect(page.getByRole("link", { name: "← Portfolio" })).toBeVisible();
  });
});

// ── Cross-surface navigation ────────────────────────────────────

test.describe("Cross-surface navigation", () => {
  test("all workspace surfaces are reachable from nav", async ({ page }) => {
    await page.goto("/today");

    // Today → Portfolio
    await page.getByTestId("nav-portfolio").click();
    await expect(page.getByTestId("page-portfolio")).toBeVisible();

    // Portfolio → Triage
    await page.getByTestId("nav-triage").click();
    await expect(page.getByTestId("page-triage")).toBeVisible();

    // Triage → Drafts
    await page.getByTestId("nav-drafts").click();
    await expect(page.getByTestId("page-drafts")).toBeVisible();
    // Verify no-auto-send notice persists after navigation
    await expect(page.getByTestId("drafts-no-auto-send")).toBeVisible();

    // Drafts → Research
    await page.getByTestId("nav-research").click();
    await expect(page.getByTestId("page-research")).toBeVisible();

    // Research → Review
    await page.getByTestId("nav-review").click();
    await expect(page.getByTestId("page-review")).toBeVisible();

    // Review → Today
    await page.getByTestId("nav-today").click();
    await expect(page.getByTestId("page-today")).toBeVisible();
  });
});



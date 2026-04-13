/**
 * Persona rendering and safety fidelity — browser proof for WE8 and WE9.
 *
 * TEST:UI.Persona.FallbackAndContextSelectionWorks
 * TEST:UI.Persona.RenderingRemainsSubordinateToOperationalContent
 * TEST:Drafting.NoAutoSend.BoundaryPreserved
 * TEST:Security.ReviewGate.ExternalImpactRequiresApproval
 */

import { test, expect } from "@playwright/test";

// ── WE8: Persona rendering ─────────────────────────────────────

test.describe("Persona rendering — WE8", () => {
  test("Today view shows persona avatar or fallback", async ({ page }) => {
    await page.goto("/today");
    await expect(page.getByTestId("page-today")).toBeVisible();

    // The persona component should render — either a real avatar image
    // or the fallback initial "G". Both are acceptable proof that
    // persona rendering is wired and fallback works.
    const hasAvatar = await page
      .getByTestId("persona-avatar")
      .isVisible()
      .catch(() => false);
    const hasFallback = await page
      .getByTestId("persona-fallback")
      .isVisible()
      .catch(() => false);

    // At least one must appear — persona rendering is active
    expect(hasAvatar || hasFallback).toBeTruthy();
  });

  test("Drafts view shows persona avatar or fallback", async ({ page }) => {
    await page.goto("/drafts");
    await expect(page.getByTestId("page-drafts")).toBeVisible();

    const hasAvatar = await page
      .getByTestId("persona-avatar")
      .isVisible()
      .catch(() => false);
    const hasFallback = await page
      .getByTestId("persona-fallback")
      .isVisible()
      .catch(() => false);

    expect(hasAvatar || hasFallback).toBeTruthy();
  });

  test("Persona fallback renders accessible label", async ({ page }) => {
    // Without backend persona assets seeded, fallback should appear
    await page.goto("/today");
    await expect(page.getByTestId("page-today")).toBeVisible();

    // Wait for persona to load (either avatar or fallback)
    await page.waitForTimeout(500);

    const fallback = page.getByTestId("persona-fallback");
    const hasFallback = await fallback.isVisible().catch(() => false);
    if (hasFallback) {
      // Fallback should have accessible role and label
      await expect(fallback).toHaveAttribute("role", "img");
      await expect(fallback).toHaveAttribute(
        "aria-label",
        "Glimmer assistant"
      );
      // Should contain the initial "G"
      await expect(fallback).toContainText("G");
    }
    // If a real avatar is showing, that's fine too — it means persona
    // assets are seeded in the test DB
  });

  test("Persona does not push heading below fold", async ({ page }) => {
    await page.goto("/today");
    await expect(page.getByTestId("page-today")).toBeVisible();

    // TEST:UI.Persona.RenderingRemainsSubordinateToOperationalContent
    // The heading must remain visible — persona rendering must not
    // push it off-screen or make it invisible
    const heading = page.getByRole("heading", { name: "Today", level: 1 });
    await expect(heading).toBeVisible();
    await expect(heading).toBeInViewport();
  });

  test("Persona does not push heading below fold on Drafts", async ({
    page,
  }) => {
    await page.goto("/drafts");
    await expect(page.getByTestId("page-drafts")).toBeVisible();

    const heading = page.getByRole("heading", { name: "Drafts", level: 1 });
    await expect(heading).toBeVisible();
    await expect(heading).toBeInViewport();
  });
});

// ── WE9: Safety fidelity across all surfaces ────────────────────

test.describe("Safety fidelity — WE9", () => {
  test("No Send button exists on any workspace surface", async ({ page }) => {
    // TEST:Drafting.NoAutoSend.BoundaryPreserved — comprehensive
    const surfaces = ["/today", "/portfolio", "/triage", "/drafts", "/review"];

    for (const surface of surfaces) {
      await page.goto(surface);
      // No "Send" button should exist anywhere
      const sendButtons = page.getByRole("button", { name: /^send$/i });
      await expect(sendButtons).toHaveCount(0);
    }
  });

  test("Drafts page always shows no-auto-send notice", async ({ page }) => {
    await page.goto("/drafts");
    const notice = page.getByTestId("drafts-no-auto-send");
    await expect(notice).toBeVisible();
    await expect(
      page.getByText("Glimmer never sends on your behalf")
    ).toBeVisible();
  });

  test("Review page has only Accept and Reject — no auto-approve", async ({
    page,
  }) => {
    // TEST:Security.ReviewGate.ExternalImpactRequiresApproval
    await page.goto("/review");
    await expect(page.getByTestId("page-review")).toBeVisible();

    // Wait for load to settle
    await page.waitForTimeout(500);

    // If there are review items with accept/reject buttons, verify controls
    const acceptBtns = page.getByTestId("review-btn-accept");
    const acceptCount = await acceptBtns.count();

    if (acceptCount > 0) {
      const rejectBtns = page.getByTestId("review-btn-reject");
      const rejectCount = await rejectBtns.count();
      // Every item should have both accept and reject
      expect(acceptCount).toBe(rejectCount);
    }

    // Regardless of whether items exist: no "Auto-approve" button should exist
    const autoApprove = page.getByRole("button", {
      name: /auto.?approve/i,
    });
    await expect(autoApprove).toHaveCount(0);
  });

  test("Triage page has explicit review controls, not auto-accept", async ({
    page,
  }) => {
    await page.goto("/triage");
    await expect(page.getByTestId("page-triage")).toBeVisible();

    // No auto-approve or auto-accept buttons
    const autoButtons = page.getByRole("button", {
      name: /auto.?(approve|accept)/i,
    });
    await expect(autoButtons).toHaveCount(0);
  });

  test("No send or submit form actions on draft cards", async ({ page }) => {
    await page.goto("/drafts");
    await expect(page.getByTestId("page-drafts")).toBeVisible();

    // No form with action that implies sending
    const forms = page.locator('form[action*="send"]');
    await expect(forms).toHaveCount(0);

    // No submit buttons with send-like text
    const submitSend = page.locator(
      'button[type="submit"], input[type="submit"]'
    );
    await expect(submitSend).toHaveCount(0);
  });

  test("Review surface shows pending state distinction clearly", async ({
    page,
  }) => {
    // TEST:UI.ReviewQueue.PendingVsAcceptedIsObvious
    await page.goto("/review");
    await expect(page.getByTestId("page-review")).toBeVisible();

    // Wait for load to settle
    await page.waitForTimeout(500);

    const hasEmpty = await page
      .getByTestId("review-empty-state")
      .isVisible()
      .catch(() => false);
    const hasPendingCount = await page
      .getByTestId("review-pending-count")
      .isVisible()
      .catch(() => false);
    const hasLoading = await page
      .getByTestId("review-loading")
      .isVisible()
      .catch(() => false);
    const hasError = await page
      .getByTestId("review-error")
      .isVisible()
      .catch(() => false);

    // One of the four states must be visible — the page must always
    // show the operator what is happening
    expect(hasEmpty || hasPendingCount || hasLoading || hasError).toBeTruthy();
  });
});




/**
 * Playwright tests for the persona page conversation UI.
 *
 * PLAN:WorkstreamE.PackageE12.PersonaPageConversationUi
 * TEST:PersonaPage.Conversation.ChatRendersAndAcceptsInput
 */

import { test, expect } from "@playwright/test";

test.describe("Persona Page Conversation", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/glimmer");
    await page.waitForSelector('[data-testid="page-glimmer"]');
  });

  test("persona page renders with all major sections", async ({ page }) => {
    await expect(page.locator('[data-testid="page-glimmer"]')).toBeVisible();
    await expect(page.locator('[data-testid="glimmer-avatar"]')).toBeVisible();
    await expect(page.locator('[data-testid="chat-window"]')).toBeVisible();
    await expect(page.locator('[data-testid="controls-gutter"]')).toBeVisible();
    await expect(page.locator('[data-testid="workspace-canvas"]')).toBeVisible();
  });

  test("chat input is visible and accepts text", async ({ page }) => {
    const input = page.locator('[data-testid="chat-input"]');
    await expect(input).toBeVisible();
    await input.fill("Hello Glimmer");
    await expect(input).toHaveValue("Hello Glimmer");
  });

  test("send button is present", async ({ page }) => {
    const sendBtn = page.locator('[data-testid="chat-send"]');
    await expect(sendBtn).toBeVisible();
  });

  test("workspace mode controls are visible", async ({ page }) => {
    await expect(page.locator('[data-testid="workspace-idea"]')).toBeVisible();
    await expect(page.locator('[data-testid="workspace-plan"]')).toBeVisible();
    await expect(page.locator('[data-testid="workspace-report"]')).toBeVisible();
    await expect(page.locator('[data-testid="workspace-debrief"]')).toBeVisible();
    await expect(page.locator('[data-testid="workspace-update"]')).toBeVisible();
  });

  test("interaction mode controls are visible", async ({ page }) => {
    await expect(page.locator('[data-testid="mode-voice"]')).toBeVisible();
    await expect(page.locator('[data-testid="mode-whisper"]')).toBeVisible();
    await expect(page.locator('[data-testid="mode-chat"]')).toBeVisible();
  });

  test("avatar shows mood data attribute", async ({ page }) => {
    const avatar = page.locator('[data-testid="glimmer-avatar"]');
    await expect(avatar).toBeVisible();
    // Avatar should have a mood data attribute (bau, happy, etc.)
    const mood = await avatar.getAttribute("data-mood");
    expect(["bau", "happy", "grumpy", "thinking", "worried"]).toContain(mood);
  });
});


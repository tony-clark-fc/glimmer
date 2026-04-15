/**
 * Playwright tests for the persona page mind-map visualization.
 *
 * PLAN:WorkstreamE.PackageE13.PersonaPageMindMap
 * TEST:PersonaPage.MindMap.NodesRenderWithSemanticTypes
 * TEST:PersonaPage.MindMap.CanvasSupportsZoomPanInteraction
 */

import { test, expect } from "@playwright/test";

test.describe("Persona Page Mind-Map", () => {
  test.beforeEach(async ({ page }) => {
    // Mock backend API calls so the page loads cleanly without a running backend.
    // The persona page calls /persona/mood and POST /persona/sessions on mount.
    // Backend runs at http://localhost:8000 (no /api prefix).
    await page.route("**/persona/mood", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ mood: "bau", reason: "Test mode" }),
      }),
    );
    await page.route("**/persona/sessions", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          id: "test-session-1",
          status: "active",
          workspace_mode: "update",
          created_at: new Date().toISOString(),
          messages: [],
        }),
      }),
    );
    // Mock projects list for plan mode canvas
    await page.route("**/projects*", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([]),
      }),
    );

    await page.goto("/glimmer");
    await page.waitForSelector('[data-testid="page-glimmer"]');
  });

  test("idea mode shows the mind-map canvas", async ({ page }) => {
    // Switch to idea mode if not already there
    const ideaBtn = page.locator('[data-testid="workspace-idea"]');
    await ideaBtn.click();

    // Wait for workspace canvas to switch to idea mode
    await expect(page.locator('[data-testid="workspace-canvas"][data-mode="idea"]')).toBeVisible();

    // The mind-map canvas should be rendered
    await expect(page.locator('[data-testid="mindmap-canvas"]')).toBeVisible();
  });

  test("mind-map renders nodes with semantic types", async ({ page }) => {
    const ideaBtn = page.locator('[data-testid="workspace-idea"]');
    await ideaBtn.click();

    await expect(page.locator('[data-testid="mindmap-canvas"]')).toBeVisible();

    // Demo data should render nodes for different entity types
    await expect(page.locator('[data-testid="mindmap-node-project"]')).toBeVisible();
    await expect(page.locator('[data-testid="mindmap-node-stakeholder"]')).toBeVisible();
    await expect(page.locator('[data-testid="mindmap-node-milestone"]')).toBeVisible();
    await expect(page.locator('[data-testid="mindmap-node-risk"]')).toBeVisible();
    await expect(page.locator('[data-testid="mindmap-node-blocker"]')).toBeVisible();
    await expect(page.locator('[data-testid="mindmap-node-work_item"]')).toBeVisible();
    await expect(page.locator('[data-testid="mindmap-node-decision"]')).toBeVisible();
    await expect(page.locator('[data-testid="mindmap-node-dependency"]')).toBeVisible();
  });

  test("mind-map nodes show working state indicator", async ({ page }) => {
    const ideaBtn = page.locator('[data-testid="workspace-idea"]');
    await ideaBtn.click();

    await expect(page.locator('[data-testid="mindmap-canvas"]')).toBeVisible();

    // Pending (draft) nodes should have status="pending"
    const pendingNodes = page.locator('[data-node-status="pending"]');
    const count = await pendingNodes.count();
    expect(count).toBeGreaterThan(0);

    // Should also have at least one accepted node (decision in demo)
    await expect(page.locator('[data-node-status="accepted"]')).toBeVisible();
  });

  test("React Flow controls are visible", async ({ page }) => {
    const ideaBtn = page.locator('[data-testid="workspace-idea"]');
    await ideaBtn.click();

    await expect(page.locator('[data-testid="mindmap-canvas"]')).toBeVisible();

    // React Flow renders zoom controls
    await expect(page.locator(".react-flow__controls")).toBeVisible();
  });

  test("React Flow minimap is visible", async ({ page }) => {
    const ideaBtn = page.locator('[data-testid="workspace-idea"]');
    await ideaBtn.click();

    await expect(page.locator('[data-testid="mindmap-canvas"]')).toBeVisible();

    // React Flow renders minimap
    await expect(page.locator(".react-flow__minimap")).toBeVisible();
  });

  test("other modes do not show mind-map", async ({ page }) => {
    // Plan mode
    const planBtn = page.locator('[data-testid="workspace-plan"]');
    await planBtn.click();
    await expect(page.locator('[data-testid="workspace-canvas"][data-mode="plan"]')).toBeVisible();
    await expect(page.locator('[data-testid="mindmap-canvas"]')).not.toBeVisible();
  });
});




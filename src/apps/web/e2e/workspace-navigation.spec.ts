/**
 * Workspace navigation and shell — browser proof.
 *
 * TEST:Smoke.FrontendStarts
 * TEST:Smoke.WorkspaceNavigationBasic
 * TEST:Foundation.Frontend.WorkspaceShellExists
 */

import { test, expect } from "@playwright/test";

// ── TEST:Smoke.FrontendStarts ────────────────────────────────────────
test("frontend starts and redirects to /today", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveURL(/\/today/);
});

// ── TEST:Foundation.Frontend.WorkspaceShellExists ────────────────────
test("workspace nav is visible with all primary routes", async ({ page }) => {
  await page.goto("/today");

  const nav = page.locator('nav[aria-label="Workspace navigation"]');
  await expect(nav).toBeVisible();

  // All five primary nav items
  await expect(page.getByTestId("nav-today")).toBeVisible();
  await expect(page.getByTestId("nav-portfolio")).toBeVisible();
  await expect(page.getByTestId("nav-triage")).toBeVisible();
  await expect(page.getByTestId("nav-drafts")).toBeVisible();
  await expect(page.getByTestId("nav-review")).toBeVisible();

  // Glimmer brand link
  await expect(page.getByTestId("nav-home")).toHaveText("Glimmer");
});

// ── TEST:Smoke.WorkspaceNavigationBasic ──────────────────────────────
const WORKSPACE_ROUTES = [
  { path: "/today", testId: "page-today", heading: "Today" },
  { path: "/portfolio", testId: "page-portfolio", heading: "Portfolio" },
  { path: "/triage", testId: "page-triage", heading: "Triage" },
  { path: "/drafts", testId: "page-drafts", heading: "Drafts" },
  { path: "/review", testId: "page-review", heading: "Review" },
];

for (const route of WORKSPACE_ROUTES) {
  test(`route ${route.path} is reachable and renders correctly`, async ({
    page,
  }) => {
    await page.goto(route.path);
    await expect(page.getByTestId(route.testId)).toBeVisible();
    await expect(
      page.getByRole("heading", { name: route.heading, level: 1 })
    ).toBeVisible();
  });
}

test("project route /projects/[id] is reachable", async ({ page }) => {
  await page.goto("/projects/test-project-1");
  await expect(page.getByTestId("page-project")).toBeVisible();
});

test("clicking nav links navigates between surfaces", async ({ page }) => {
  await page.goto("/today");
  await expect(page.getByTestId("page-today")).toBeVisible();

  await page.getByTestId("nav-portfolio").click();
  await expect(page.getByTestId("page-portfolio")).toBeVisible();

  await page.getByTestId("nav-triage").click();
  await expect(page.getByTestId("page-triage")).toBeVisible();

  await page.getByTestId("nav-drafts").click();
  await expect(page.getByTestId("page-drafts")).toBeVisible();

  await page.getByTestId("nav-review").click();
  await expect(page.getByTestId("page-review")).toBeVisible();

  await page.getByTestId("nav-today").click();
  await expect(page.getByTestId("page-today")).toBeVisible();
});


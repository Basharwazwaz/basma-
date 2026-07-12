import { test, expect } from "@playwright/test";

const BASE = process.env.BASE_URL ?? "http://localhost:5173";

test.describe("Mood Page (unauthenticated)", () => {
  test("should redirect to login when accessing mood page", async ({ page }) => {
    await page.goto(`${BASE}/mood`);
    await expect(page).toHaveURL(/login/);
  });
});

test.describe("Dashboard (unauthenticated)", () => {
  test("should redirect to login when accessing dashboard", async ({ page }) => {
    await page.goto(`${BASE}/dashboard`);
    await expect(page).toHaveURL(/login/);
  });
});

test.describe("Planner (unauthenticated)", () => {
  test("should redirect to login when accessing planner", async ({ page }) => {
    await page.goto(`${BASE}/planner`);
    await expect(page).toHaveURL(/login/);
  });
});

import { test, expect } from '@playwright/test';

const BASE = process.env.BASE_URL ?? 'http://localhost:5173';

test.describe('Forgot Password', () => {
  test('should show email input form', async ({ page }) => {
    await page.goto(`${BASE}/auth/forgot-password`);
    await expect(page.locator('text=نسيت كلمة المرور')).toBeVisible();
    await expect(page.locator('input[type="email"]')).toBeVisible();
  });

  test('should have back to login link', async ({ page }) => {
    await page.goto(`${BASE}/auth/forgot-password`);
    await expect(page.locator('text=العودة لتسجيل الدخول').or(page.locator('text=تسجيل الدخول'))).toBeVisible();
  });
});

test.describe('Reset Password', () => {
  test('should show new password form with token', async ({ page }) => {
    await page.goto(`${BASE}/auth/reset-password?token=test-token-123`);
    await expect(page.locator('text=كلمة المرور الجديدة')).toBeVisible();
  });
});

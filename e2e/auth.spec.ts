import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test('should navigate to login page', async ({ page }) => {
    await page.goto('/auth/login');
    // Assuming there's a heading or button with 'تسجيل الدخول' (Login in Arabic) or similar
    await expect(page.locator('body')).toContainText(/login|تسجيل الدخول/i);
  });
});

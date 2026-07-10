import { test, expect } from '@playwright/test';

const BASE = process.env.BASE_URL ?? 'http://localhost:5173';

test.describe('Landing Page', () => {
  test('should show hero text and CTA buttons', async ({ page }) => {
    await page.goto(`${BASE}/`);
    await expect(page.locator('text=بصمة+')).toBeVisible();
    await expect(page.locator('text=تسجيل الدخول').or(page.locator('text=ابدأ'))).toBeVisible();
  });
});

test.describe('Authentication Flow', () => {
  test('should navigate to login page', async ({ page }) => {
    await page.goto(`${BASE}/auth/login`);
    await expect(page.locator('text=تسجيل الدخول')).toBeVisible();
  });

  test('should show forgot password link', async ({ page }) => {
    await page.goto(`${BASE}/auth/login`);
    await expect(page.locator('text=نسيت كلمة المرور؟')).toBeVisible();
  });

  test('should navigate to register page', async ({ page }) => {
    await page.goto(`${BASE}/auth/login`);
    await page.click('text=أنشئ حسابًا');
    await expect(page).toHaveURL(/register/);
  });

  test('should show validation error on empty login', async ({ page }) => {
    await page.goto(`${BASE}/auth/login`);
    await page.click('button[type="submit"]');
    await expect(page.locator('text=يرجى تعبئة')).toBeVisible();
  });

  test('should show Google login button', async ({ page }) => {
    await page.goto(`${BASE}/auth/login`);
    await expect(page.locator('text=المتابعة عبر Google')).toBeVisible();
  });

  test('should navigate to forgot password page', async ({ page }) => {
    await page.goto(`${BASE}/auth/login`);
    await page.click('text=نسيت كلمة المرور؟');
    await expect(page).toHaveURL(/forgot-password/);
  });
});

test.describe('Register Page', () => {
  test('should show registration form', async ({ page }) => {
    await page.goto(`${BASE}/auth/register`);
    await expect(page.locator('text=أنشئ حسابك')).toBeVisible();
  });

  test('should have link to login', async ({ page }) => {
    await page.goto(`${BASE}/auth/register`);
    await expect(page.locator('text=تسجيل الدخول')).toBeVisible();
  });
});

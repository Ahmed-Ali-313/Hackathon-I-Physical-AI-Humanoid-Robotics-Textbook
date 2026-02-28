/**
 * E2E Tests for Translation Flow
 * Feature: 005-urdu-translation
 * Purpose: Test full translation workflow from UI
 */

import { test, expect } from '@playwright/test';

test.describe('Translation Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to textbook
    await page.goto('http://localhost:3001');
  });

  test('T019: Full translation flow - authenticated user', async ({ page }) => {
    // Step 1: Login
    await page.goto('http://localhost:3001/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');

    // Wait for redirect
    await page.waitForURL('http://localhost:3001/');

    // Step 2: Navigate to a chapter
    await page.goto('http://localhost:3001/docs/01-introduction-to-ros2');

    // Step 3: Verify translate button is visible
    const translateButton = page.locator('button:has-text("Translate to Urdu")');
    await expect(translateButton).toBeVisible();

    // Step 4: Click translate button
    await translateButton.click();

    // Step 5: Wait for loading indicator
    await expect(page.locator('text=Translating...')).toBeVisible();

    // Step 6: Wait for translation to complete (max 10 seconds)
    await expect(page.locator('button:has-text("Show Original English")')).toBeVisible({ timeout: 10000 });

    // Step 7: Verify Urdu content is displayed
    const content = page.locator('article');
    await expect(content).toHaveCSS('direction', 'rtl');

    // Step 8: Verify technical terms are preserved
    await expect(content).toContainText('ROS 2');

    // Step 9: Toggle back to English
    await page.click('button:has-text("Show Original English")');
    await expect(page.locator('button:has-text("Translate to Urdu")')).toBeVisible();
  });

  test('T040: Unauthenticated user experience', async ({ page }) => {
    // Step 1: Navigate to chapter without logging in
    await page.goto('http://localhost:3001/docs/01-introduction-to-ros2');

    // Step 2: Verify translate button is NOT visible
    const translateButton = page.locator('button:has-text("Translate to Urdu")');
    await expect(translateButton).not.toBeVisible();

    // Step 3: Verify auth message is shown
    await expect(page.locator('text=Urdu translations are available for registered users')).toBeVisible();

    // Step 4: Verify signup link is present
    const signupLink = page.locator('a:has-text("Sign up")');
    await expect(signupLink).toBeVisible();
    await expect(signupLink).toHaveAttribute('href', '/signup');

    // Step 5: Verify login link is present
    const loginLink = page.locator('a:has-text("log in")');
    await expect(loginLink).toBeVisible();
    await expect(loginLink).toHaveAttribute('href', '/login');
  });

  test('T046: Preference persistence across chapters', async ({ page }) => {
    // Step 1: Login
    await page.goto('http://localhost:3001/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('http://localhost:3001/');

    // Step 2: Navigate to Chapter 1
    await page.goto('http://localhost:3001/docs/01-introduction-to-ros2');

    // Step 3: Translate to Urdu
    await page.click('button:has-text("Translate to Urdu")');
    await expect(page.locator('button:has-text("Show Original English")')).toBeVisible({ timeout: 10000 });

    // Step 4: Navigate to Chapter 2
    await page.goto('http://localhost:3001/docs/02-ros2-architecture');

    // Step 5: Verify Chapter 2 automatically displays in Urdu
    await expect(page.locator('button:has-text("Show Original English")')).toBeVisible();
    const content = page.locator('article');
    await expect(content).toHaveCSS('direction', 'rtl');
  });

  test('T047: Preference persistence across sessions', async ({ page, context }) => {
    // Step 1: Login and translate
    await page.goto('http://localhost:3001/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('http://localhost:3001/');

    await page.goto('http://localhost:3001/docs/01-introduction-to-ros2');
    await page.click('button:has-text("Translate to Urdu")');
    await expect(page.locator('button:has-text("Show Original English")')).toBeVisible({ timeout: 10000 });

    // Step 2: Close browser and reopen (simulate session restart)
    await page.close();
    const newPage = await context.newPage();

    // Step 3: Navigate to chapter (still logged in via cookies)
    await newPage.goto('http://localhost:3001/docs/01-introduction-to-ros2');

    // Step 4: Verify Urdu is still active
    await expect(newPage.locator('button:has-text("Show Original English")')).toBeVisible();
  });

  test('T063: Cache hit performance', async ({ page }) => {
    // Step 1: Login
    await page.goto('http://localhost:3001/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('http://localhost:3001/');

    // Step 2: First translation (fresh)
    await page.goto('http://localhost:3001/docs/01-introduction-to-ros2');
    const startTime1 = Date.now();
    await page.click('button:has-text("Translate to Urdu")');
    await expect(page.locator('button:has-text("Show Original English")')).toBeVisible({ timeout: 10000 });
    const duration1 = Date.now() - startTime1;

    // Step 3: Toggle back to English
    await page.click('button:has-text("Show Original English")');

    // Step 4: Second translation (cached)
    const startTime2 = Date.now();
    await page.click('button:has-text("Translate to Urdu")');
    await expect(page.locator('button:has-text("Show Original English")')).toBeVisible({ timeout: 2000 });
    const duration2 = Date.now() - startTime2;

    // Step 5: Verify cached translation is faster
    expect(duration2).toBeLessThan(1000); // Should be <1s for cached
    expect(duration2).toBeLessThan(duration1 / 2); // At least 2x faster
  });

  test('Translation error handling', async ({ page }) => {
    // Step 1: Login
    await page.goto('http://localhost:3001/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('http://localhost:3001/');

    // Step 2: Mock API failure (would need to intercept network)
    await page.route('**/api/v1/translate', route => {
      route.fulfill({
        status: 500,
        body: JSON.stringify({ error: 'Translation service error' })
      });
    });

    // Step 3: Navigate to chapter and try to translate
    await page.goto('http://localhost:3001/docs/01-introduction-to-ros2');
    await page.click('button:has-text("Translate to Urdu")');

    // Step 4: Verify error message is shown
    await expect(page.locator('text=Translation failed')).toBeVisible({ timeout: 5000 });

    // Step 5: Verify dismiss button works
    await page.click('button[aria-label="Dismiss error"]');
    await expect(page.locator('text=Translation failed')).not.toBeVisible();
  });
});

/**
 * E2E Test: Visual Regression Tests (User Story 5)
 *
 * Screenshot comparison tests for light/dark modes to ensure visual consistency.
 */

import { test, expect } from '@playwright/test';

test.describe('Visual Regression Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
    await page.evaluate(() => {
      localStorage.setItem('auth_token', 'test-token-123');
    });
  });

  test('T085: Chat panel in light mode matches baseline', async ({ page }) => {
    // Set light mode
    await page.emulateMedia({ colorScheme: 'light' });

    // Open chat panel
    await page.click('button:has-text("Ask")');
    await expect(page.locator('[role="dialog"]')).toBeVisible();

    // Wait for panel to fully render
    await page.waitForTimeout(500);

    // Take screenshot
    const chatPanel = page.locator('.chatPanel').first();
    await expect(chatPanel).toHaveScreenshot('chat-panel-light.png', {
      maxDiffPixels: 100,
    });
  });

  test('T085: Chat panel in dark mode matches baseline', async ({ page }) => {
    // Set dark mode
    await page.emulateMedia({ colorScheme: 'dark' });

    // Open chat panel
    await page.click('button:has-text("Ask")');
    await expect(page.locator('[role="dialog"]')).toBeVisible();

    // Wait for panel to fully render
    await page.waitForTimeout(500);

    // Take screenshot
    const chatPanel = page.locator('.chatPanel').first();
    await expect(chatPanel).toHaveScreenshot('chat-panel-dark.png', {
      maxDiffPixels: 100,
    });
  });

  test('T085: Conversation sidebar in light mode', async ({ page }) => {
    await page.emulateMedia({ colorScheme: 'light' });
    await page.click('button:has-text("Ask")');

    const sidebar = page.locator('.sidebar').first();
    await expect(sidebar).toBeVisible();

    await expect(sidebar).toHaveScreenshot('sidebar-light.png', {
      maxDiffPixels: 50,
    });
  });

  test('T085: Conversation sidebar in dark mode', async ({ page }) => {
    await page.emulateMedia({ colorScheme: 'dark' });
    await page.click('button:has-text("Ask")');

    const sidebar = page.locator('.sidebar').first();
    await expect(sidebar).toBeVisible();

    await expect(sidebar).toHaveScreenshot('sidebar-dark.png', {
      maxDiffPixels: 50,
    });
  });

  test('T085: Message input in light mode', async ({ page }) => {
    await page.emulateMedia({ colorScheme: 'light' });
    await page.click('button:has-text("Ask")');

    const inputArea = page.locator('.inputArea').first();
    await expect(inputArea).toBeVisible();

    await expect(inputArea).toHaveScreenshot('message-input-light.png', {
      maxDiffPixels: 50,
    });
  });

  test('T085: Message input in dark mode', async ({ page }) => {
    await page.emulateMedia({ colorScheme: 'dark' });
    await page.click('button:has-text("Ask")');

    const inputArea = page.locator('.inputArea').first();
    await expect(inputArea).toBeVisible();

    await expect(inputArea).toHaveScreenshot('message-input-dark.png', {
      maxDiffPixels: 50,
    });
  });

  test('T085: Error message in light mode', async ({ page, context }) => {
    await page.emulateMedia({ colorScheme: 'light' });

    // Mock error
    await context.route('**/api/chat/conversations', route => {
      route.fulfill({
        status: 503,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'Service unavailable',
          error_type: 'service_unavailable'
        })
      });
    });

    await page.click('button:has-text("Ask")');
    await expect(page.locator('[role="alert"]')).toBeVisible({ timeout: 5000 });

    const errorMessage = page.locator('[role="alert"]').first();
    await expect(errorMessage).toHaveScreenshot('error-message-light.png', {
      maxDiffPixels: 50,
    });
  });

  test('T085: Error message in dark mode', async ({ page, context }) => {
    await page.emulateMedia({ colorScheme: 'dark' });

    // Mock error
    await context.route('**/api/chat/conversations', route => {
      route.fulfill({
        status: 503,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'Service unavailable',
          error_type: 'service_unavailable'
        })
      });
    });

    await page.click('button:has-text("Ask")');
    await expect(page.locator('[role="alert"]')).toBeVisible({ timeout: 5000 });

    const errorMessage = page.locator('[role="alert"]').first();
    await expect(errorMessage).toHaveScreenshot('error-message-dark.png', {
      maxDiffPixels: 50,
    });
  });

  test('T085: Chat button in light mode', async ({ page }) => {
    await page.emulateMedia({ colorScheme: 'light' });

    const chatButton = page.locator('button:has-text("Ask")');
    await expect(chatButton).toBeVisible();

    await expect(chatButton).toHaveScreenshot('chat-button-light.png', {
      maxDiffPixels: 20,
    });
  });

  test('T085: Chat button in dark mode', async ({ page }) => {
    await page.emulateMedia({ colorScheme: 'dark' });

    const chatButton = page.locator('button:has-text("Ask")');
    await expect(chatButton).toBeVisible();

    await expect(chatButton).toHaveScreenshot('chat-button-dark.png', {
      maxDiffPixels: 20,
    });
  });

  test('T085: Full chat panel with conversation', async ({ page, context }) => {
    await page.emulateMedia({ colorScheme: 'light' });

    // Mock successful conversation
    await context.route('**/api/chat/conversations', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 'conv-1',
            user_id: 'test-user',
            title: 'What is ROS2?',
            message_count: 2,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          }
        ])
      });
    });

    await page.click('button:has-text("Ask")');
    await page.waitForTimeout(1000);

    const chatPanel = page.locator('.chatPanel').first();
    await expect(chatPanel).toHaveScreenshot('chat-panel-with-conversation.png', {
      maxDiffPixels: 150,
    });
  });
});

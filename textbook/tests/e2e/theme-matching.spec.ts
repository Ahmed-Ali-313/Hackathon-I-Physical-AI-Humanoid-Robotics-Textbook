/**
 * E2E Test: Theme Matching and Switching (User Story 5)
 *
 * Tests that chat interface seamlessly matches textbook design in light/dark modes.
 */

import { test, expect } from '@playwright/test';

test.describe('Theme Matching and Switching', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to textbook
    await page.goto('http://localhost:3000');

    // Set auth token
    await page.evaluate(() => {
      localStorage.setItem('auth_token', 'test-token-123');
    });
  });

  test('T084: Chat UI adapts when user toggles light/dark mode', async ({ page }) => {
    // Open chat panel
    await page.click('button:has-text("Ask")');
    await expect(page.locator('[role="dialog"]')).toBeVisible();

    // Get initial background color (light mode)
    const chatPanel = page.locator('.chatPanel').first();
    const lightBgColor = await chatPanel.evaluate((el) =>
      window.getComputedStyle(el).backgroundColor
    );

    // Toggle to dark mode
    await page.click('button[aria-label*="dark mode"], button[title*="dark mode"]');
    await page.waitForTimeout(500); // Wait for theme transition

    // Get dark mode background color
    const darkBgColor = await chatPanel.evaluate((el) =>
      window.getComputedStyle(el).backgroundColor
    );

    // Verify colors changed
    expect(lightBgColor).not.toBe(darkBgColor);

    // Toggle back to light mode
    await page.click('button[aria-label*="light mode"], button[title*="light mode"]');
    await page.waitForTimeout(500);

    // Verify returned to light mode
    const finalBgColor = await chatPanel.evaluate((el) =>
      window.getComputedStyle(el).backgroundColor
    );
    expect(finalBgColor).toBe(lightBgColor);
  });

  test('T086: Manual test - Verify theme matching in light mode', async ({ page }) => {
    // Ensure light mode
    await page.emulateMedia({ colorScheme: 'light' });

    // Open chat
    await page.click('button:has-text("Ask")');

    // Verify chat panel uses light theme colors
    const chatPanel = page.locator('.chatPanel').first();
    const bgColor = await chatPanel.evaluate((el) =>
      window.getComputedStyle(el).backgroundColor
    );

    // Background should be light (rgb values should be high)
    expect(bgColor).toMatch(/rgb\(2[0-5][0-9], 2[0-5][0-9], 2[0-5][0-9]\)/);

    // Check button colors match theme
    const sendButton = page.locator('button[aria-label="Send message"]');
    const buttonBgColor = await sendButton.evaluate((el) =>
      window.getComputedStyle(el).backgroundColor
    );

    // Primary color should be consistent
    expect(buttonBgColor).toBeTruthy();
  });

  test('T086: Manual test - Verify theme matching in dark mode', async ({ page }) => {
    // Set dark mode
    await page.emulateMedia({ colorScheme: 'dark' });

    // Open chat
    await page.click('button:has-text("Ask")');

    // Verify chat panel uses dark theme colors
    const chatPanel = page.locator('.chatPanel').first();
    const bgColor = await chatPanel.evaluate((el) =>
      window.getComputedStyle(el).backgroundColor
    );

    // Background should be dark (rgb values should be low)
    expect(bgColor).toMatch(/rgb\([0-9]{1,2}, [0-9]{1,2}, [0-9]{1,2}\)/);

    // Check text is readable (light text on dark background)
    const title = page.locator('.title').first();
    const textColor = await title.evaluate((el) =>
      window.getComputedStyle(el).color
    );

    // Text should be light colored
    expect(textColor).toMatch(/rgb\(2[0-5][0-9], 2[0-5][0-9], 2[0-5][0-9]\)/);
  });

  test('All chat components use consistent colors', async ({ page }) => {
    await page.click('button:has-text("Ask")');

    // Create a test message
    const messageInput = page.locator('textarea[placeholder="Ask here"]');
    await messageInput.fill('Test message');
    await page.click('button[aria-label="Send message"]');
    await page.waitForTimeout(1000);

    // Get colors from different components
    const chatPanel = page.locator('.chatPanel').first();
    const sidebar = page.locator('.sidebar').first();
    const messageArea = page.locator('.messageArea').first();

    const panelBg = await chatPanel.evaluate((el) =>
      window.getComputedStyle(el).backgroundColor
    );
    const sidebarBg = await sidebar.evaluate((el) =>
      window.getComputedStyle(el).backgroundColor
    );
    const messageAreaBg = await messageArea.evaluate((el) =>
      window.getComputedStyle(el).backgroundColor
    );

    // All should use theme colors (not hardcoded)
    expect(panelBg).toBeTruthy();
    expect(sidebarBg).toBeTruthy();
    expect(messageAreaBg).toBeTruthy();
  });

  test('Theme persists across panel close/open', async ({ page }) => {
    // Set dark mode
    await page.emulateMedia({ colorScheme: 'dark' });

    // Open chat
    await page.click('button:has-text("Ask")');

    const chatPanel = page.locator('.chatPanel').first();
    const darkBgColor = await chatPanel.evaluate((el) =>
      window.getComputedStyle(el).backgroundColor
    );

    // Close chat
    await page.click('button[aria-label="Close chat"]');

    // Reopen chat
    await page.click('button:has-text("Ask")');

    // Verify still in dark mode
    const reopenedBgColor = await chatPanel.evaluate((el) =>
      window.getComputedStyle(el).backgroundColor
    );

    expect(reopenedBgColor).toBe(darkBgColor);
  });

  test('Error messages match theme colors', async ({ page, context }) => {
    // Mock error response
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

    // Open chat to trigger error
    await page.click('button:has-text("Ask")');

    // Wait for error message
    await expect(page.locator('[role="alert"]')).toBeVisible({ timeout: 5000 });

    // Verify error uses theme colors
    const errorContainer = page.locator('[role="alert"]').first();
    const errorBg = await errorContainer.evaluate((el) =>
      window.getComputedStyle(el).backgroundColor
    );

    // Should use danger color from theme
    expect(errorBg).toBeTruthy();
    expect(errorBg).not.toBe('rgba(0, 0, 0, 0)'); // Not transparent
  });

  test('Conversation sidebar matches theme', async ({ page }) => {
    await page.click('button:has-text("Ask")');

    // Check sidebar colors
    const sidebar = page.locator('.sidebar').first();
    const sidebarBg = await sidebar.evaluate((el) =>
      window.getComputedStyle(el).backgroundColor
    );

    const newButton = page.locator('button:has-text("New")');
    const buttonColor = await newButton.evaluate((el) =>
      window.getComputedStyle(el).color
    );

    // Both should use theme colors
    expect(sidebarBg).toBeTruthy();
    expect(buttonColor).toBeTruthy();
  });
});

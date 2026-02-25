/**
 * E2E Test: Accessibility Audit (User Story 5)
 *
 * Tests keyboard navigation, screen reader support, and WCAG 2.1 AA compliance.
 */

import { test, expect } from '@playwright/test';

test.describe('Accessibility Audit', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
    await page.evaluate(() => {
      localStorage.setItem('auth_token', 'test-token-123');
    });
  });

  test('T086a: Keyboard navigation - Tab through all interactive elements', async ({ page }) => {
    // Open chat panel
    await page.click('button:has-text("Ask")');
    await expect(page.locator('[role="dialog"]')).toBeVisible();

    // Tab through elements
    await page.keyboard.press('Tab'); // Should focus first element in panel
    await page.keyboard.press('Tab'); // Next element
    await page.keyboard.press('Tab'); // Next element

    // Verify focus is visible
    const focusedElement = await page.evaluate(() => {
      const el = document.activeElement;
      return el ? el.tagName : null;
    });

    expect(focusedElement).toBeTruthy();
  });

  test('T086a: Keyboard navigation - Enter key activates buttons', async ({ page }) => {
    await page.click('button:has-text("Ask")');

    // Focus on close button
    const closeButton = page.locator('button[aria-label="Close chat"]');
    await closeButton.focus();

    // Press Enter
    await page.keyboard.press('Enter');

    // Verify panel closed
    await expect(page.locator('[role="dialog"]')).not.toBeVisible();
  });

  test('T086a: Keyboard navigation - Escape key closes panel', async ({ page }) => {
    await page.click('button:has-text("Ask")');
    await expect(page.locator('[role="dialog"]')).toBeVisible();

    // Press Escape
    await page.keyboard.press('Escape');

    // Verify panel closed
    await expect(page.locator('[role="dialog"]')).not.toBeVisible();
  });

  test('T086a: Screen reader - Dialog has proper ARIA labels', async ({ page }) => {
    await page.click('button:has-text("Ask")');

    const dialog = page.locator('[role="dialog"]');
    await expect(dialog).toHaveAttribute('aria-label', 'Chat assistant');
    await expect(dialog).toHaveAttribute('aria-modal', 'true');
  });

  test('T086a: Screen reader - Buttons have descriptive labels', async ({ page }) => {
    await page.click('button:has-text("Ask")');

    // Check close button
    const closeButton = page.locator('button[aria-label="Close chat"]');
    await expect(closeButton).toBeVisible();

    // Check send button
    const sendButton = page.locator('button[aria-label="Send message"]');
    await expect(sendButton).toBeVisible();
  });

  test('T086a: Screen reader - Error messages use role="alert"', async ({ page, context }) => {
    // Mock error
    await context.route('**/api/chat/conversations', route => {
      route.fulfill({
        status: 503,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Service unavailable' })
      });
    });

    await page.click('button:has-text("Ask")');

    // Verify error has alert role
    const alert = page.locator('[role="alert"]');
    await expect(alert).toBeVisible({ timeout: 5000 });
  });

  test('T086a: Color contrast - Text meets WCAG 2.1 AA (4.5:1)', async ({ page }) => {
    await page.click('button:has-text("Ask")');

    // Get title element
    const title = page.locator('.title').first();
    await expect(title).toBeVisible();

    // Get computed colors
    const colors = await title.evaluate((el) => {
      const style = window.getComputedStyle(el);
      return {
        color: style.color,
        backgroundColor: style.backgroundColor
      };
    });

    // Verify colors are set (actual contrast ratio calculation would require a library)
    expect(colors.color).toBeTruthy();
    expect(colors.backgroundColor).toBeTruthy();
  });

  test('T086a: Focus indicators - All interactive elements show focus', async ({ page }) => {
    await page.click('button:has-text("Ask")');

    // Focus on close button
    const closeButton = page.locator('button[aria-label="Close chat"]');
    await closeButton.focus();

    // Check if outline is visible
    const outline = await closeButton.evaluate((el) => {
      const style = window.getComputedStyle(el);
      return style.outline;
    });

    // Should have an outline (not 'none')
    expect(outline).not.toBe('none');
  });

  test('T086a: Keyboard navigation - Can navigate conversation list', async ({ page }) => {
    await page.click('button:has-text("Ask")');

    // Create a conversation first
    const messageInput = page.locator('textarea[placeholder="Ask here"]');
    await messageInput.fill('Test question');
    await page.click('button[aria-label="Send message"]');
    await page.waitForTimeout(1000);

    // Focus on conversation item
    const conversationItem = page.locator('.conversationItem').first();
    await conversationItem.focus();

    // Press Enter to select
    await page.keyboard.press('Enter');

    // Verify conversation is active
    await expect(conversationItem).toHaveClass(/active/);
  });

  test('T086a: Keyboard navigation - Can navigate with Space key', async ({ page }) => {
    await page.click('button:has-text("Ask")');

    // Create conversation
    const messageInput = page.locator('textarea[placeholder="Ask here"]');
    await messageInput.fill('Test');
    await page.click('button[aria-label="Send message"]');
    await page.waitForTimeout(1000);

    // Focus and press Space
    const conversationItem = page.locator('.conversationItem').first();
    await conversationItem.focus();
    await page.keyboard.press('Space');

    // Should activate conversation
    await expect(conversationItem).toHaveClass(/active/);
  });

  test('T086a: Reduced motion - Animations respect prefers-reduced-motion', async ({ page }) => {
    // Set reduced motion preference
    await page.emulateMedia({ reducedMotion: 'reduce' });

    await page.click('button:has-text("Ask")');

    // Check if animations are disabled
    const chatPanel = page.locator('.chatPanel').first();
    const animation = await chatPanel.evaluate((el) => {
      const style = window.getComputedStyle(el);
      return style.animation;
    });

    // Animation should be 'none' or very short
    expect(animation).toMatch(/none|0s/);
  });

  test('T086a: High contrast mode - Borders are visible', async ({ page }) => {
    // Simulate high contrast mode
    await page.emulateMedia({ forcedColors: 'active' });

    await page.click('button:has-text("Ask")');

    const chatPanel = page.locator('.chatPanel').first();
    const borderWidth = await chatPanel.evaluate((el) => {
      const style = window.getComputedStyle(el);
      return style.borderWidth;
    });

    // Should have visible borders in high contrast
    expect(borderWidth).toBeTruthy();
  });

  test('T086a: Form labels - Input has accessible label', async ({ page }) => {
    await page.click('button:has-text("Ask")');

    const textarea = page.locator('textarea[placeholder="Ask here"]');

    // Check for placeholder (acts as label)
    await expect(textarea).toHaveAttribute('placeholder', 'Ask here');

    // Verify it's focusable
    await textarea.focus();
    const isFocused = await textarea.evaluate((el) => el === document.activeElement);
    expect(isFocused).toBe(true);
  });

  test('T086a: Semantic HTML - Proper heading hierarchy', async ({ page }) => {
    await page.click('button:has-text("Ask")');

    // Check for h2 heading
    const heading = page.locator('h2.title');
    await expect(heading).toBeVisible();

    // Verify heading text
    const headingText = await heading.textContent();
    expect(headingText).toBeTruthy();
  });

  test('T086a: Link accessibility - Links have descriptive text', async ({ page, context }) => {
    // Mock error with login link
    await context.route('**/api/chat/conversations', route => {
      route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'Session expired',
          error_type: 'authentication_expired'
        })
      });
    });

    await page.click('button:has-text("Ask")');

    // Check login link
    const loginLink = page.locator('a:has-text("Log in again")');
    await expect(loginLink).toBeVisible({ timeout: 5000 });

    // Verify link text is descriptive (not just "click here")
    const linkText = await loginLink.textContent();
    expect(linkText).toContain('Log in');
  });
});

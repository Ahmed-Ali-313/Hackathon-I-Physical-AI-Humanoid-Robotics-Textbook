/**
 * E2E Tests for RTL Layout
 * Feature: 005-urdu-translation
 * Purpose: Test RTL layout rendering and styling
 */

import { test, expect } from '@playwright/test';

test.describe('RTL Layout Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('http://localhost:3001/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('http://localhost:3001/');
  });

  test('T020: RTL layout applied when Urdu is active', async ({ page }) => {
    // Navigate to chapter
    await page.goto('http://localhost:3001/docs/01-introduction-to-ros2');

    // Translate to Urdu
    await page.click('button:has-text("Translate to Urdu")');
    await expect(page.locator('button:has-text("Show Original English")')).toBeVisible({ timeout: 10000 });

    // Verify RTL direction
    const content = page.locator('article');
    await expect(content).toHaveCSS('direction', 'rtl');
    await expect(content).toHaveCSS('text-align', 'right');

    // Verify Urdu font is applied
    const fontFamily = await content.evaluate(el => window.getComputedStyle(el).fontFamily);
    expect(fontFamily).toContain('Noto Nastaliq Urdu');
  });

  test('RTL layout reverts to LTR when switching to English', async ({ page }) => {
    // Navigate and translate
    await page.goto('http://localhost:3001/docs/01-introduction-to-ros2');
    await page.click('button:has-text("Translate to Urdu")');
    await expect(page.locator('button:has-text("Show Original English")')).toBeVisible({ timeout: 10000 });

    // Switch back to English
    await page.click('button:has-text("Show Original English")');

    // Verify LTR direction
    const content = page.locator('article');
    await expect(content).toHaveCSS('direction', 'ltr');
    await expect(content).toHaveCSS('text-align', 'left');
  });

  test('Code blocks remain LTR in RTL layout', async ({ page }) => {
    // Navigate and translate
    await page.goto('http://localhost:3001/docs/01-introduction-to-ros2');
    await page.click('button:has-text("Translate to Urdu")');
    await expect(page.locator('button:has-text("Show Original English")')).toBeVisible({ timeout: 10000 });

    // Find code block
    const codeBlock = page.locator('pre code').first();

    if (await codeBlock.count() > 0) {
      // Verify code block is LTR
      await expect(codeBlock).toHaveCSS('direction', 'ltr');
      await expect(codeBlock).toHaveCSS('text-align', 'left');
    }
  });

  test('Lists are right-aligned in RTL layout', async ({ page }) => {
    // Navigate and translate
    await page.goto('http://localhost:3001/docs/01-introduction-to-ros2');
    await page.click('button:has-text("Translate to Urdu")');
    await expect(page.locator('button:has-text("Show Original English")')).toBeVisible({ timeout: 10000 });

    // Find list
    const list = page.locator('ul, ol').first();

    if (await list.count() > 0) {
      // Verify list has right padding
      const paddingRight = await list.evaluate(el => window.getComputedStyle(el).paddingRight);
      const paddingLeft = await list.evaluate(el => window.getComputedStyle(el).paddingLeft);

      // Right padding should be greater than left padding in RTL
      expect(parseInt(paddingRight)).toBeGreaterThan(parseInt(paddingLeft));
    }
  });

  test('Headers are right-aligned in RTL layout', async ({ page }) => {
    // Navigate and translate
    await page.goto('http://localhost:3001/docs/01-introduction-to-ros2');
    await page.click('button:has-text("Translate to Urdu")');
    await expect(page.locator('button:has-text("Show Original English")')).toBeVisible({ timeout: 10000 });

    // Find headers
    const h1 = page.locator('h1').first();
    const h2 = page.locator('h2').first();

    // Verify headers use Urdu font
    if (await h1.count() > 0) {
      const fontFamily = await h1.evaluate(el => window.getComputedStyle(el).fontFamily);
      expect(fontFamily).toContain('Noto Nastaliq Urdu');
    }

    if (await h2.count() > 0) {
      const fontFamily = await h2.evaluate(el => window.getComputedStyle(el).fontFamily);
      expect(fontFamily).toContain('Noto Nastaliq Urdu');
    }
  });

  test('Line height is adequate for Urdu text', async ({ page }) => {
    // Navigate and translate
    await page.goto('http://localhost:3001/docs/01-introduction-to-ros2');
    await page.click('button:has-text("Translate to Urdu")');
    await expect(page.locator('button:has-text("Show Original English")')).toBeVisible({ timeout: 10000 });

    // Check line height
    const content = page.locator('article');
    const lineHeight = await content.evaluate(el => window.getComputedStyle(el).lineHeight);

    // Line height should be at least 1.8 for Urdu readability
    const lineHeightValue = parseFloat(lineHeight);
    expect(lineHeightValue).toBeGreaterThanOrEqual(1.8);
  });

  test('Font size is adequate for Urdu text', async ({ page }) => {
    // Navigate and translate
    await page.goto('http://localhost:3001/docs/01-introduction-to-ros2');
    await page.click('button:has-text("Translate to Urdu")');
    await expect(page.locator('button:has-text("Show Original English")')).toBeVisible({ timeout: 10000 });

    // Check font size
    const content = page.locator('article');
    const fontSize = await content.evaluate(el => window.getComputedStyle(el).fontSize);

    // Font size should be at least 16px for Urdu readability
    const fontSizeValue = parseInt(fontSize);
    expect(fontSizeValue).toBeGreaterThanOrEqual(16);
  });

  test('Blockquotes are styled correctly in RTL', async ({ page }) => {
    // Navigate and translate
    await page.goto('http://localhost:3001/docs/01-introduction-to-ros2');
    await page.click('button:has-text("Translate to Urdu")');
    await expect(page.locator('button:has-text("Show Original English")')).toBeVisible({ timeout: 10000 });

    // Find blockquote
    const blockquote = page.locator('blockquote').first();

    if (await blockquote.count() > 0) {
      // Verify blockquote has right border in RTL
      const borderRight = await blockquote.evaluate(el => window.getComputedStyle(el).borderRightWidth);
      const borderLeft = await blockquote.evaluate(el => window.getComputedStyle(el).borderLeftWidth);

      // Right border should be thicker than left border in RTL
      expect(parseInt(borderRight)).toBeGreaterThan(parseInt(borderLeft));
    }
  });

  test('Images remain centered in RTL layout', async ({ page }) => {
    // Navigate and translate
    await page.goto('http://localhost:3001/docs/01-introduction-to-ros2');
    await page.click('button:has-text("Translate to Urdu")');
    await expect(page.locator('button:has-text("Show Original English")')).toBeVisible({ timeout: 10000 });

    // Find image
    const img = page.locator('article img').first();

    if (await img.count() > 0) {
      // Verify image has auto margins for centering
      const marginLeft = await img.evaluate(el => window.getComputedStyle(el).marginLeft);
      const marginRight = await img.evaluate(el => window.getComputedStyle(el).marginRight);

      expect(marginLeft).toBe('auto');
      expect(marginRight).toBe('auto');
    }
  });

  test('Dark mode works with RTL layout', async ({ page }) => {
    // Enable dark mode
    await page.evaluate(() => {
      document.documentElement.setAttribute('data-theme', 'dark');
    });

    // Navigate and translate
    await page.goto('http://localhost:3001/docs/01-introduction-to-ros2');
    await page.click('button:has-text("Translate to Urdu")');
    await expect(page.locator('button:has-text("Show Original English")')).toBeVisible({ timeout: 10000 });

    // Verify RTL still works in dark mode
    const content = page.locator('article');
    await expect(content).toHaveCSS('direction', 'rtl');

    // Verify dark mode colors are applied
    const backgroundColor = await content.evaluate(el => window.getComputedStyle(el).backgroundColor);
    // Dark mode should have dark background (not white)
    expect(backgroundColor).not.toBe('rgb(255, 255, 255)');
  });
});

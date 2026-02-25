/**
 * E2E Test: Error Handling (User Story 4)
 *
 * Tests that students receive clear, actionable error messages for all failure scenarios.
 */

import { test, expect } from '@playwright/test';

test.describe('Error Handling', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to textbook
    await page.goto('http://localhost:3000');
  });

  test('T078: Unauthenticated access shows login prompt', async ({ page }) => {
    // Clear any existing auth token
    await page.evaluate(() => {
      localStorage.removeItem('auth_token');
    });

    // Try to open chat panel
    await page.click('button:has-text("Ask")');

    // Should show error message about authentication
    await expect(page.locator('text=/please log in/i')).toBeVisible({ timeout: 5000 });

    // Should show login link
    const loginLink = page.locator('a:has-text("Log in again")');
    await expect(loginLink).toBeVisible();
    await expect(loginLink).toHaveAttribute('href', '/login');
  });

  test('T079: Manual test - Try chatbot without login', async ({ page }) => {
    // Clear auth token
    await page.evaluate(() => {
      localStorage.removeItem('auth_token');
    });

    // Click chat button
    await page.click('button:has-text("Ask")');

    // Verify error message appears
    await expect(page.locator('[role="alert"]')).toBeVisible();

    // Verify message content
    const errorMessage = page.locator('[role="alert"]');
    await expect(errorMessage).toContainText(/log in/i);

    // Verify login link is present
    await expect(page.locator('a[href="/login"]')).toBeVisible();
  });

  test('Network error shows retry button', async ({ page, context }) => {
    // Set auth token
    await page.evaluate(() => {
      localStorage.setItem('auth_token', 'test-token-123');
    });

    // Simulate network failure by blocking API requests
    await context.route('**/api/chat/**', route => {
      route.abort('failed');
    });

    // Open chat panel
    await page.click('button:has-text("Ask")');

    // Wait for error message
    await expect(page.locator('[role="alert"]')).toBeVisible({ timeout: 5000 });

    // Verify retry button exists
    const retryButton = page.locator('button:has-text("Try again")');
    await expect(retryButton).toBeVisible();

    // Verify error message mentions connection
    await expect(page.locator('[role="alert"]')).toContainText(/connection|network|failed/i);
  });

  test('Service unavailable error shows appropriate message', async ({ page, context }) => {
    // Set auth token
    await page.evaluate(() => {
      localStorage.setItem('auth_token', 'test-token-123');
    });

    // Mock 503 Service Unavailable response
    await context.route('**/api/chat/conversations', route => {
      route.fulfill({
        status: 503,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'The chatbot is temporarily unavailable. Please try again in a few moments.',
          error_type: 'service_unavailable'
        })
      });
    });

    // Open chat panel
    await page.click('button:has-text("Ask")');

    // Wait for error message
    await expect(page.locator('[role="alert"]')).toBeVisible({ timeout: 5000 });

    // Verify error message
    await expect(page.locator('[role="alert"]')).toContainText(/temporarily unavailable/i);

    // Verify retry button
    await expect(page.locator('button:has-text("Try again")')).toBeVisible();
  });

  test('Timeout error shows appropriate message', async ({ page, context }) => {
    // Set auth token
    await page.evaluate(() => {
      localStorage.setItem('auth_token', 'test-token-123');
    });

    // Mock 504 Gateway Timeout response
    await context.route('**/api/chat/conversations', route => {
      route.fulfill({
        status: 504,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'The request took too long to complete. Please try again.',
          error_type: 'timeout_error'
        })
      });
    });

    // Open chat panel
    await page.click('button:has-text("Ask")');

    // Wait for error message
    await expect(page.locator('[role="alert"]')).toBeVisible({ timeout: 5000 });

    // Verify error message mentions timeout
    await expect(page.locator('[role="alert"]')).toContainText(/too long|timeout/i);

    // Verify timeout icon
    await expect(page.locator('text=⏱️')).toBeVisible();
  });

  test('Error can be dismissed', async ({ page, context }) => {
    // Set auth token
    await page.evaluate(() => {
      localStorage.setItem('auth_token', 'test-token-123');
    });

    // Mock error response
    await context.route('**/api/chat/conversations', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'An unexpected error occurred.',
          error_type: 'internal_error'
        })
      });
    });

    // Open chat panel
    await page.click('button:has-text("Ask")');

    // Wait for error message
    await expect(page.locator('[role="alert"]')).toBeVisible({ timeout: 5000 });

    // Click dismiss button
    await page.click('button[aria-label="Dismiss error"]');

    // Verify error is dismissed
    await expect(page.locator('[role="alert"]')).not.toBeVisible();
  });

  test('Retry button attempts to reload data', async ({ page, context }) => {
    // Set auth token
    await page.evaluate(() => {
      localStorage.setItem('auth_token', 'test-token-123');
    });

    let requestCount = 0;

    // Mock first request to fail, second to succeed
    await context.route('**/api/chat/conversations', route => {
      requestCount++;
      if (requestCount === 1) {
        route.fulfill({
          status: 503,
          contentType: 'application/json',
          body: JSON.stringify({
            detail: 'Service unavailable',
            error_type: 'service_unavailable'
          })
        });
      } else {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([])
        });
      }
    });

    // Open chat panel
    await page.click('button:has-text("Ask")');

    // Wait for error message
    await expect(page.locator('[role="alert"]')).toBeVisible({ timeout: 5000 });

    // Click retry button
    await page.click('button:has-text("Try again")');

    // Verify error is dismissed after successful retry
    await expect(page.locator('[role="alert"]')).not.toBeVisible({ timeout: 5000 });
  });

  test('Different error types show appropriate icons', async ({ page, context }) => {
    // Set auth token
    await page.evaluate(() => {
      localStorage.setItem('auth_token', 'test-token-123');
    });

    // Test database error icon
    await context.route('**/api/chat/conversations', route => {
      route.fulfill({
        status: 503,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'Database error',
          error_type: 'database_error'
        })
      });
    });

    await page.click('button:has-text("Ask")');
    await expect(page.locator('text=⚠️')).toBeVisible({ timeout: 5000 });

    // Close and reopen to test another error type
    await page.click('button[aria-label="Close chat"]');
    await page.click('button[aria-label="Dismiss error"]').catch(() => {});

    // Test connection error icon
    await context.route('**/api/chat/conversations', route => {
      route.fulfill({
        status: 503,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'Connection error',
          error_type: 'connection_error'
        })
      });
    });

    await page.click('button:has-text("Ask")');
    await expect(page.locator('text=📡')).toBeVisible({ timeout: 5000 });
  });
});

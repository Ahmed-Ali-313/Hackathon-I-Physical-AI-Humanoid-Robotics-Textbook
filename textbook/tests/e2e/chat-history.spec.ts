/**
 * E2E Test: Chat History Across Sessions (User Story 3)
 *
 * Tests that students can view previous conversations and continue where they left off.
 */

import { test, expect } from '@playwright/test';

test.describe('Chat History Across Sessions', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to textbook
    await page.goto('http://localhost:3000');

    // Mock authentication (since Better-Auth not fully integrated)
    await page.evaluate(() => {
      localStorage.setItem('auth_token', 'test-token-123');
    });
  });

  test('T067: Ask questions, logout, login, verify history preserved', async ({ page }) => {
    // Step 1: Open chat panel
    await page.click('button:has-text("Ask")');
    await expect(page.locator('[role="dialog"][aria-label="Chat assistant"]')).toBeVisible();

    // Step 2: Ask first question
    const messageInput = page.locator('textarea[placeholder="Ask here"]');
    await messageInput.fill('What is ROS2?');
    await page.click('button[aria-label="Send message"]');

    // Wait for response
    await expect(page.locator('text=What is ROS2?')).toBeVisible();
    await page.waitForSelector('[data-sender="assistant"]', { timeout: 10000 });

    // Step 3: Verify conversation appears in sidebar
    await expect(page.locator('.conversationItem')).toHaveCount(1);
    await expect(page.locator('.conversationTitle')).toContainText('What is ROS2?');

    // Step 4: Ask second question in same conversation
    await messageInput.fill('How do I install it?');
    await page.click('button[aria-label="Send message"]');
    await page.waitForSelector('[data-sender="assistant"]:nth-of-type(2)', { timeout: 10000 });

    // Step 5: Create new conversation
    await page.click('button:has-text("New")');
    await expect(page.locator('.conversationItem')).toHaveCount(2);

    // Step 6: Ask question in new conversation
    await messageInput.fill('What is VSLAM?');
    await page.click('button[aria-label="Send message"]');
    await page.waitForSelector('[data-sender="assistant"]', { timeout: 10000 });

    // Step 7: Close chat panel
    await page.click('button[aria-label="Close chat"]');
    await expect(page.locator('[role="dialog"]')).not.toBeVisible();

    // Step 8: Simulate logout/login by reloading page
    await page.reload();
    await page.evaluate(() => {
      localStorage.setItem('auth_token', 'test-token-123');
    });

    // Step 9: Reopen chat panel
    await page.click('button:has-text("Ask")');
    await expect(page.locator('[role="dialog"]')).toBeVisible();

    // Step 10: Verify both conversations are preserved
    await expect(page.locator('.conversationItem')).toHaveCount(2);
    await expect(page.locator('.conversationTitle').first()).toContainText('What is VSLAM?');
    await expect(page.locator('.conversationTitle').nth(1)).toContainText('What is ROS2?');

    // Step 11: Switch to first conversation
    await page.locator('.conversationItem').nth(1).click();

    // Step 12: Verify messages are loaded
    await expect(page.locator('text=What is ROS2?')).toBeVisible();
    await expect(page.locator('text=How do I install it?')).toBeVisible();
  });

  test('T068: Manual test - Ask 3 questions, close browser, reopen, verify history', async ({ page }) => {
    // This test simulates the manual test scenario

    // Open chat
    await page.click('button:has-text("Ask")');

    // Ask 3 questions
    const questions = [
      'What is ROS2 middleware?',
      'How does VSLAM work?',
      'What is Isaac Sim?'
    ];

    for (const question of questions) {
      const messageInput = page.locator('textarea[placeholder="Ask here"]');
      await messageInput.fill(question);
      await page.click('button[aria-label="Send message"]');

      // Wait for response
      await page.waitForSelector(`text=${question}`, { timeout: 5000 });
      await page.waitForTimeout(2000); // Wait for AI response
    }

    // Verify all 3 messages are visible
    for (const question of questions) {
      await expect(page.locator(`text=${question}`)).toBeVisible();
    }

    // Close and reopen (simulating browser close)
    await page.click('button[aria-label="Close chat"]');
    await page.reload();
    await page.evaluate(() => {
      localStorage.setItem('auth_token', 'test-token-123');
    });

    // Reopen chat
    await page.click('button:has-text("Ask")');

    // Verify conversation exists in sidebar
    await expect(page.locator('.conversationItem')).toHaveCount(1);

    // Click conversation to load messages
    await page.locator('.conversationItem').first().click();

    // Verify all 3 messages are preserved
    for (const question of questions) {
      await expect(page.locator(`text=${question}`)).toBeVisible();
    }
  });

  test('Switch between conversations loads correct messages', async ({ page }) => {
    // Open chat
    await page.click('button:has-text("Ask")');

    // Create first conversation
    const messageInput = page.locator('textarea[placeholder="Ask here"]');
    await messageInput.fill('Question in conversation 1');
    await page.click('button[aria-label="Send message"]');
    await page.waitForTimeout(2000);

    // Create second conversation
    await page.click('button:has-text("New")');
    await messageInput.fill('Question in conversation 2');
    await page.click('button[aria-label="Send message"]');
    await page.waitForTimeout(2000);

    // Verify we're in conversation 2
    await expect(page.locator('text=Question in conversation 2')).toBeVisible();
    await expect(page.locator('text=Question in conversation 1')).not.toBeVisible();

    // Switch to conversation 1
    await page.locator('.conversationItem').nth(1).click();

    // Verify conversation 1 messages loaded
    await expect(page.locator('text=Question in conversation 1')).toBeVisible();
    await expect(page.locator('text=Question in conversation 2')).not.toBeVisible();
  });

  test('Delete conversation removes it from list', async ({ page }) => {
    // Open chat and create conversation
    await page.click('button:has-text("Ask")');

    const messageInput = page.locator('textarea[placeholder="Ask here"]');
    await messageInput.fill('Test conversation to delete');
    await page.click('button[aria-label="Send message"]');
    await page.waitForTimeout(2000);

    // Verify conversation exists
    await expect(page.locator('.conversationItem')).toHaveCount(1);

    // Hover over conversation to show delete button
    await page.locator('.conversationItem').hover();

    // Mock confirm dialog
    page.on('dialog', dialog => dialog.accept());

    // Click delete button
    await page.click('button[aria-label="Delete conversation"]');

    // Verify conversation removed
    await expect(page.locator('.conversationItem')).toHaveCount(0);
    await expect(page.locator('text=No conversations yet')).toBeVisible();
  });
});

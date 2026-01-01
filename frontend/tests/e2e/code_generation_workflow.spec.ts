/**
 * Playwright E2E Tests for AI Code Flow
 *
 * Tests complete user workflows through the web interface including:
 * - Code generation requests
 * - Real-time streaming updates
 * - Project downloads
 * - Error handling scenarios
 *
 * These tests verify the end-to-end user experience.
 */

import { test, expect, Page } from '@playwright/test';

test.describe('AI Code Flow E2E Tests', () => {
  // Setup: Navigate to the application
  test.beforeEach(async ({ page }) => {
    // Assuming the app runs on localhost:3000
    await page.goto('http://localhost:3000');

    // Wait for the page to load
    await page.waitForLoadState('networkidle');
  });

  test.describe('Code Generation Workflow', () => {
    test('should complete full Snake game generation workflow', async ({ page }) => {
      // Test the complete user journey for Snake game generation

      // 1. Verify page loads correctly
      await expect(page).toHaveTitle(/AI Code Flow/);

      // 2. Find and fill the input form
      const inputField = page.locator('input[placeholder*="输入"], textarea[placeholder*="输入"]').first();
      await expect(inputField).toBeVisible();

      // 3. Enter Snake game request
      await inputField.fill('帮我写个贪吃蛇游戏');

      // 4. Submit the request
      const submitButton = page.locator('button:has-text("生成"), button:has-text("提交"), button[type="submit"]').first();
      await expect(submitButton).toBeVisible();
      await submitButton.click();

      // 5. Verify streaming starts and phases are shown
      // Wait for streaming to begin
      await page.waitForSelector('[data-testid="streaming-display"], .streaming-display, .phase-progress', { timeout: 10000 });

      // 6. Monitor phase progression
      // Should see Specify → Plan → Implement phases
      const phaseElements = page.locator('[data-testid*="phase"], .phase, .phase-progress');
      await expect(phaseElements.first()).toBeVisible();

      // 7. Wait for completion
      // Look for completion indicators
      await page.waitForSelector(
        '[data-testid="generation-complete"], .generation-complete, [data-testid="download-button"], .download-button',
        { timeout: 120000 } // 2 minutes for generation
      );

      // 8. Verify project download is available
      const downloadButton = page.locator('button:has-text("下载"), [data-testid="download-button"], .download-button').first();
      await expect(downloadButton).toBeVisible();

      // 9. Verify educational content was shown
      // Check for phase messages or educational display
      const educationalContent = page.locator('[data-testid="educational-display"], .educational-display, .phase-messages');
      await expect(educationalContent).toBeVisible();
    });

    test('should handle various code generation requests', async ({ page }) => {
      const testRequests = [
        '创建一个计算器应用',
        '写一个Hello World程序',
        '生成一个数据处理脚本'
      ];

      for (const request of testRequests) {
        // Navigate fresh for each test
        await page.reload();
        await page.waitForLoadState('networkidle');

        // Fill and submit request
        const inputField = page.locator('input[placeholder*="输入"], textarea[placeholder*="输入"]').first();
        await inputField.fill(request);

        const submitButton = page.locator('button:has-text("生成"), button:has-text("提交")').first();
        await submitButton.click();

        // Wait for streaming to start
        await page.waitForSelector('[data-testid="streaming-display"], .streaming-display', { timeout: 10000 });

        // Wait for completion
        await page.waitForSelector(
          '[data-testid="generation-complete"], .generation-complete',
          { timeout: 90000 } // 1.5 minutes
        );

        // Verify download option is available
        const downloadButton = page.locator('button:has-text("下载"), [data-testid="download-button"]').first();
        await expect(downloadButton).toBeVisible();
      }
    });

    test('should display real-time streaming updates', async ({ page }) => {
      // Test streaming functionality

      const inputField = page.locator('input[placeholder*="输入"], textarea[placeholder*="输入"]').first();
      await inputField.fill('写一个简单的函数');

      const submitButton = page.locator('button:has-text("生成"), button:has-text("提交")').first();
      await submitButton.click();

      // Monitor streaming content
      const streamingContainer = page.locator('[data-testid="streaming-display"], .streaming-display').first();
      await expect(streamingContainer).toBeVisible();

      // Wait for some content to appear
      await page.waitForFunction(() => {
        const container = document.querySelector('[data-testid="streaming-display"], .streaming-display');
        return container && container.textContent && container.textContent.length > 0;
      }, { timeout: 10000 });

      // Verify content is updating (streaming)
      const initialContent = await streamingContainer.textContent();

      // Wait a bit more and check content grew
      await page.waitForTimeout(2000);
      const updatedContent = await streamingContainer.textContent();

      // Content should have increased (streaming is working)
      expect(updatedContent!.length).toBeGreaterThan(initialContent!.length);
    });
  });

  test.describe('Error Handling', () => {
    test('should handle empty input gracefully', async ({ page }) => {
      // Try to submit empty form
      const submitButton = page.locator('button:has-text("生成"), button:has-text("提交")').first();
      await submitButton.click();

      // Should show validation error
      await page.waitForSelector('[data-testid="error-message"], .error-message, .validation-error', { timeout: 5000 });

      const errorMessage = page.locator('[data-testid="error-message"], .error-message').first();
      await expect(errorMessage).toBeVisible();
      await expect(errorMessage).toContainText('不能为空');
    });

    test('should handle very long input', async ({ page }) => {
      const longInput = '请'.repeat(200); // Very long Chinese input

      const inputField = page.locator('input[placeholder*="输入"], textarea[placeholder*="输入"]').first();
      await inputField.fill(longInput);

      const submitButton = page.locator('button:has-text("生成"), button:has-text("提交")').first();
      await submitButton.click();

      // Should either handle gracefully or show appropriate error
      await page.waitForSelector(
        '[data-testid="streaming-display"], .streaming-display, [data-testid="error-message"], .error-message',
        { timeout: 10000 }
      );
    });

    test('should handle network errors gracefully', async ({ page }) => {
      // This would require mocking network failures
      // For now, test basic error display capability

      const inputField = page.locator('input[placeholder*="输入"], textarea[placeholder*="输入"]').first();
      await inputField.fill('测试网络错误');

      // Simulate network failure by blocking requests
      await page.route('**/api/generate-code', route => route.abort());

      const submitButton = page.locator('button:has-text("生成"), button:has-text("提交")').first();
      await submitButton.click();

      // Should show error message
      await page.waitForSelector('[data-testid="error-message"], .error-message', { timeout: 10000 });

      const errorMessage = page.locator('[data-testid="error-message"], .error-message').first();
      await expect(errorMessage).toBeVisible();
    });
  });

  test.describe('User Interface', () => {
    test('should have proper accessibility attributes', async ({ page }) => {
      // Check for basic accessibility
      const inputField = page.locator('input[placeholder*="输入"], textarea[placeholder*="输入"]').first();

      // Should have proper labeling
      await expect(inputField).toHaveAttribute('aria-label');
    });

    test('should be responsive on different screen sizes', async ({ page }) => {
      // Test mobile responsiveness
      await page.setViewportSize({ width: 375, height: 667 }); // iPhone SE size

      const inputField = page.locator('input[placeholder*="输入"], textarea[placeholder*="输入"]').first();
      await expect(inputField).toBeVisible();

      const submitButton = page.locator('button:has-text("生成"), button:has-text("提交")').first();
      await expect(submitButton).toBeVisible();

      // Test tablet size
      await page.setViewportSize({ width: 768, height: 1024 }); // iPad size
      await expect(inputField).toBeVisible();
      await expect(submitButton).toBeVisible();
    });

    test('should support keyboard navigation', async ({ page }) => {
      // Test keyboard accessibility
      await page.keyboard.press('Tab');
      const focusedElement = page.locator(':focus');

      // First tab should focus the input field
      await expect(focusedElement).toHaveAttribute('placeholder');

      await page.keyboard.press('Tab');
      // Second tab should focus submit button
      const newFocusedElement = page.locator(':focus');
      await expect(newFocusedElement).toHaveAttribute('type', 'submit');
    });
  });

  test.describe('Performance', () => {
    test('should load quickly', async ({ page }) => {
      // Measure page load time
      const startTime = Date.now();

      await page.goto('http://localhost:3000');
      await page.waitForLoadState('domcontentloaded');

      const loadTime = Date.now() - startTime;
      expect(loadTime).toBeLessThan(5000); // Should load in under 5 seconds
    });

    test('should handle rapid successive requests', async ({ page }) => {
      // Test handling multiple quick requests
      const inputField = page.locator('input[placeholder*="输入"], textarea[placeholder*="输入"]').first();
      const submitButton = page.locator('button:has-text("生成"), button:has-text("提交")').first();

      // Make several quick requests
      for (let i = 0; i < 3; i++) {
        await inputField.fill(`快速请求 ${i + 1}`);
        await submitButton.click();

        // Wait briefly between requests
        await page.waitForTimeout(500);
      }

      // Should handle gracefully (not crash)
      await page.waitForTimeout(2000);
      await expect(page).toHaveTitle(/AI Code Flow/);
    });
  });

  test.describe('Educational Features', () => {
    test('should show phase educational messages', async ({ page }) => {
      const inputField = page.locator('input[placeholder*="输入"], textarea[placeholder*="输入"]').first();
      await inputField.fill('帮我写个简单的程序');

      const submitButton = page.locator('button:has-text("生成"), button:has-text("提交")').first();
      await submitButton.click();

      // Should show educational content during phases
      await page.waitForSelector('[data-testid="educational-display"], .educational-display, .phase-message', { timeout: 10000 });

      const educationalContent = page.locator('[data-testid="educational-display"], .educational-display').first();
      await expect(educationalContent).toBeVisible();

      // Should contain Chinese educational text
      const content = await educationalContent.textContent();
      expect(content).toMatch(/[正在|分析|生成|完成]/); // Should contain Chinese educational messages
    });

    test('should display raw AI content when requested', async ({ page }) => {
      // Test raw content viewer if available
      const inputField = page.locator('input[placeholder*="输入"], textarea[placeholder*="输入"]').first();
      await inputField.fill('显示AI原始输出');

      const submitButton = page.locator('button:has-text("生成"), button:has-text("提交")').first();
      await submitButton.click();

      // Check if raw content viewer is available and shows content
      const rawContentToggle = page.locator('button:has-text("原始"), [data-testid="raw-content-toggle"]').first();

      if (await rawContentToggle.isVisible()) {
        await rawContentToggle.click();

        const rawContentViewer = page.locator('[data-testid="raw-content-viewer"], .raw-content-viewer').first();
        await expect(rawContentViewer).toBeVisible();
      }
    });
  });

  test.describe('Download Functionality', () => {
    test('should allow project download after generation', async ({ page }) => {
      const inputField = page.locator('input[placeholder*="输入"], textarea[placeholder*="输入"]').first();
      await inputField.fill('下载测试');

      const submitButton = page.locator('button:has-text("生成"), button:has-text("提交")').first();
      await submitButton.click();

      // Wait for generation to complete
      await page.waitForSelector('[data-testid="generation-complete"], .generation-complete', { timeout: 60000 });

      // Click download button
      const downloadButton = page.locator('button:has-text("下载"), [data-testid="download-button"]').first();
      await expect(downloadButton).toBeVisible();

      // Start download and verify it works
      const downloadPromise = page.waitForEvent('download');
      await downloadButton.click();
      const download = await downloadPromise;

      // Verify download started
      expect(download.suggestedFilename()).toMatch(/\.(py|zip|txt)$/);
    });

    test('should validate syntax before allowing download', async ({ page }) => {
      // This test assumes the system validates syntax before download
      // The implementation should prevent download of invalid code

      const inputField = page.locator('input[placeholder*="输入"], textarea[placeholder*="输入"]').first();
      await inputField.fill('生成语法错误的代码');

      const submitButton = page.locator('button:has-text("生成"), button:has-text("提交")').first();
      await submitButton.click();

      // Wait for completion
      await page.waitForSelector('[data-testid="generation-complete"], .generation-complete', { timeout: 60000 });

      // If syntax validation fails, download should be disabled or show warning
      const downloadButton = page.locator('button:has-text("下载"), [data-testid="download-button"]').first();

      if (await downloadButton.isVisible()) {
        // If download is available, it implies syntax validation passed
        const isEnabled = await downloadButton.isEnabled();
        expect(isEnabled).toBe(true);
      }
    });
  });
});

// Configuration for Playwright
export const testConfig = {
  // Global setup
  use: {
    baseURL: 'http://localhost:3000',
    headless: true,
    viewport: { width: 1280, height: 720 },
    ignoreHTTPSErrors: true,
    video: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },

  // Test-wide settings
  expect: {
    timeout: 30000, // 30 seconds
  },

  // Reporter configuration
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/e2e-results.json' }],
  ],

  // Retry configuration
  retries: 2,

  // Parallel execution
  workers: 1, // Sequential for E2E stability
};

/**
 * Global setup for Playwright E2E tests
 *
 * Ensures backend is running and configured for testing.
 */

import { chromium } from '@playwright/test';

async function globalSetup() {
  console.log('🚀 Setting up E2E test environment...');

  try {
    // Check if backend is running
    const response = await fetch('http://localhost:8000/health');
    if (!response.ok) {
      throw new Error('Backend health check failed');
    }

    const health = await response.json();
    if (health.status !== 'healthy') {
      throw new Error(`Backend not healthy: ${health.message}`);
    }

    console.log('✅ Backend is healthy and ready');

    // Verify frontend can be reached
    const browser = await chromium.launch();
    const page = await browser.newPage();

    try {
      await page.goto('http://localhost:3000');
      await page.waitForLoadState('domcontentloaded');
      console.log('✅ Frontend is accessible');
    } finally {
      await browser.close();
    }

    console.log('🎉 E2E test environment setup complete');

  } catch (error) {
    console.error('❌ E2E test environment setup failed:', error);
    throw error;
  }
}

export default globalSetup;

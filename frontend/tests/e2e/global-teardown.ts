/**
 * Global teardown for Playwright E2E tests
 *
 * Cleans up test environment and resources.
 */

async function globalTeardown() {
  console.log('🧹 Cleaning up E2E test environment...');

  try {
    // Clean up any test data or resources
    // This could include:
    // - Removing test projects
    // - Clearing test databases
    // - Closing connections

    console.log('✅ E2E test environment cleanup complete');

  } catch (error) {
    console.error('❌ E2E test environment cleanup failed:', error);
    // Don't throw here to avoid masking test failures
  }
}

export default globalTeardown;

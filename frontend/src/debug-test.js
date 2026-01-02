// Debug test script to check file system operations
const fs = require('fs/promises');
const path = require('path');

// Test the smoke test write function
async function smokeTestWrite() {
  const PROJECTS_ROOT = '../projects';
  const debugPath = path.join(PROJECTS_ROOT, 'debug_test.txt');
  const debugContent = `SMOKE TEST - ${new Date().toISOString()}\nAPI Key: TEST\nCWD: ${process.cwd()}\nPROJECTS_ROOT: ${PROJECTS_ROOT}\n`;

  console.log('[SMOKE TEST] Writing debug file to:', debugPath);
  console.log('[SMOKE TEST] Resolved path:', path.resolve(debugPath));

  try {
    await fs.mkdir(PROJECTS_ROOT, { recursive: true });
    await fs.writeFile(debugPath, debugContent, 'utf-8');
    console.log('[SMOKE TEST] Debug file written successfully');
  } catch (error) {
    console.error('[SMOKE TEST] Failed to write debug file:', error);
    throw error;
  }
}

// Run the test
smokeTestWrite().catch(console.error);


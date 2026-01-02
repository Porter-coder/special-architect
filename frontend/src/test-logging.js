/**
 * Test script to trigger persistent logging
 *
 * Run this to generate logs and test the debugging system.
 */

// Simulate a fetch request to test logging
async function testLogging() {
  console.log('Testing persistent logging system...');
  console.log('Watch the logs with: Get-Content debug.log -Wait (PowerShell)');

  // Import the logger to test it
  const { log, clearLog } = require('./lib/logger');

  // Clear existing log
  clearLog();
  log('TEST', 'Starting logging test');

  // Import and test the generate route
  try {
    const { POST } = require('./app/api/generate/route');

    // Create a mock request
    const mockRequest = {
      method: 'POST',
      url: 'http://localhost:3000/api/generate',
      json: async () => ({ prompt: 'Create a simple hello world program' }),
      headers: new Map([['content-type', 'application/json']])
    };

    log('TEST', 'Calling generate API');
    const response = await POST(mockRequest);

    log('TEST', 'API call completed', {
      status: response.status,
      hasBody: !!response.body
    });

  } catch (error) {
    log('TEST', 'Error during test', { error: error.message });
    console.error('Test error:', error);
  }
}

testLogging();

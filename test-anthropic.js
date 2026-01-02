// Simple test script for Anthropic SDK integration
const { minimaxClient } = require('./frontend/src/lib/minimax.ts');

async function testAnthropic() {
  console.log('[TEST] Starting Anthropic SDK test...');

  try {
    // Test the connection
    const connected = await minimaxClient.testConnection();
    console.log(`[TEST] Connection test: ${connected ? 'SUCCESS' : 'FAILED'}`);

    if (!connected) {
      console.log('[TEST] Using smoke test mode...');
      return;
    }

    // Test streaming generation
    console.log('[TEST] Testing streaming generation...');
    const prompt = "Create a python script that prints the first 10 Fibonacci numbers.";

    for await (const chunk of minimaxClient.generateCodeStream(prompt, 'implement')) {
      if (chunk.type === 'text') {
        process.stdout.write(chunk.content);
      }
    }

    console.log('\n[TEST] Streaming test completed successfully!');

  } catch (error) {
    console.error('[TEST] Error:', error.message);
  }
}

testAnthropic();

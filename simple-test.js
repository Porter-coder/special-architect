// Simple test for Anthropic SDK
const Anthropic = require('@anthropic-ai/sdk');

async function testAnthropic() {
  console.log('[TEST] Testing Anthropic SDK directly...');

  const apiKey = 'sk-cp-KpU_eRsDWRR7TBd1IB5LEqsL0GTTGSD78ToBVgpgBWP1PzLmEi7B08sSGQofBgFlduQFytQiX-NIQzH_akTRwo_-MmCrHfVoM-OHPe9Qm05PUyCUHyVmv-g';

  try {
    const client = new Anthropic({
      apiKey: apiKey,
      baseURL: 'https://api.minimaxi.com/anthropic'
    });

    console.log('[TEST] Client created successfully');

    // Simple test message
    const response = await client.messages.create({
      model: 'MiniMax-M2.1',
      max_tokens: 100,
      messages: [{ role: 'user', content: 'Say hello' }]
    });

    console.log('[TEST] SUCCESS: Anthropic SDK is working!');
    console.log('[TEST] Response:', response.content[0].text);

  } catch (error) {
    console.error('[TEST] FAILED: Anthropic SDK error:', error.message);
  }
}

testAnthropic();

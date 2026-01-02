// Comprehensive test for Anthropic SDK streaming with Fibonacci prompt
const Anthropic = require('@anthropic-ai/sdk');

async function testFibonacciGeneration() {
  console.log('[Minimax] Connected via Anthropic SDK');

  const apiKey = 'sk-cp-KpU_eRsDWRR7TBd1IB5LEqsL0GTTGSD78ToBVgpgBWP1PzLmEi7B08sSGQofBgFlduQFytQiX-NIQzH_akTRwo_-MmCrHfVoM-OHPe9Qm05PUyCUHyVmv-g';

  const client = new Anthropic({
    apiKey: apiKey,
    baseURL: 'https://api.minimaxi.com/anthropic'
  });

  const prompt = "Create a python script that prints the first 10 Fibonacci numbers.";
  const phase = 'implement';

  console.log(`[API] Starting generation for prompt: "${prompt}"`);

  try {
    // Use Anthropic SDK for streaming (mimicking the minimax.ts implementation)
    const stream = await client.messages.create({
      model: 'MiniMax-M2.1',
      max_tokens: 2000,
      system: 'You are an expert software engineer. Generate clean, well-documented code based on user requirements.',
      messages: [
        {
          role: 'user',
          content: prompt
        }
      ],
      stream: true,
      temperature: 0.7
    });

    console.log(`[API] Minimax Streaming: ${prompt.length} chars`);

    let fullContent = '';

    for await (const chunk of stream) {
      // Handle Anthropic streaming format (mimicking minimax.ts)
      if (chunk.type === 'content_block_delta') {
        const deltaChunk = chunk;
        if (deltaChunk.delta?.type === 'text_delta' && deltaChunk.delta.text) {
          const text = deltaChunk.delta.text;
          fullContent += text;
          process.stdout.write(text); // Stream the output
        } else if (deltaChunk.delta?.type === 'thinking_delta' && deltaChunk.delta.thinking) {
          // Log thinking but don't yield it to the parser
          console.log(`[API] Minimax Thinking: ${deltaChunk.delta.thinking.length} chars`);
        }
      }
    }

    console.log('\n[GENERATION] Streaming completed successfully!');
    console.log(`[GENERATION] Generated content length: ${fullContent.length}`);

    // Check if it contains Fibonacci logic
    const hasFibonacci = fullContent.toLowerCase().includes('fibonacci') ||
                        fullContent.includes('def fibonacci') ||
                        (fullContent.includes('for') && fullContent.includes('range(10)'));

    const hasCodeBlock = fullContent.includes('```python') || fullContent.includes('```');

    console.log(`[TEST] Contains Fibonacci logic: ${hasFibonacci}`);
    console.log(`[TEST] Contains code block: ${hasCodeBlock}`);
    console.log(`[TEST] Content is not empty: ${fullContent.trim().length > 0}`);
    console.log(`[TEST] Not default template: ${!fullContent.includes('Hello World')}`);

    if (hasFibonacci && hasCodeBlock && fullContent.trim().length > 0 && !fullContent.includes('Hello World')) {
      console.log('[TEST] SUCCESS: All validation criteria met!');
    } else {
      console.log('[TEST] PARTIAL: Some validation criteria failed');
    }

  } catch (error) {
    console.error('[TEST] FAILED: Streaming error:', error.message);
  }
}

testFibonacciGeneration();

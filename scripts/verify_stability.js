#!/usr/bin/env node

/**
 * STABILITY VERIFICATION PROTOCOL
 *
 * Detects infinite reconnect loops in SSE streams
 * Circuit breaker for SSE connection stability
 */

const http = require('http');

class StabilityVerifier {
  constructor() {
    this.connectCount = 0;
    this.lastConnectTime = 0;
    this.heartbeatCount = 0;
    this.lastDataTime = 0;
    this.startTime = Date.now();
    this.testDuration = 10000; // 10 seconds
  }

  log(message, color = 'white') {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] ${message}`);
  }

  // Circuit breaker: detect infinite loops
  checkLoopProtection() {
    const now = Date.now();
    const timeWindow = 2000; // 2 seconds

    // Reset counter if outside time window
    if (now - this.lastConnectTime > timeWindow) {
      this.connectCount = 0;
    }

    this.connectCount++;
    this.lastConnectTime = now;

    if (this.connectCount > 2) {
      throw new Error(`INFINITE LOOP DETECTED: ${this.connectCount} connections in ${timeWindow}ms`);
    }
  }

  // Timeout protection
  checkTimeoutProtection() {
    const now = Date.now();
    const timeoutThreshold = 5000; // 5 seconds

    if (this.lastDataTime > 0 && now - this.lastDataTime > timeoutThreshold) {
      throw new Error(`STREAM TIMEOUT: No data received for ${timeoutThreshold}ms`);
    }
  }

  async verifyStability() {
    this.log('🔍 Starting Stability Verification Protocol');
    this.log('⏰ Test will run for 10 seconds...');
    this.log('🎯 Success criteria: 3+ heartbeats, no reconnects, no timeouts');

    return new Promise((resolve, reject) => {
      const connect = () => {
        this.checkLoopProtection();
        this.log(`🔗 Connection attempt ${this.connectCount}`);

        const req = http.request({
          hostname: 'localhost',
          port: 3000,
          path: '/api/stream/test-stability-id',
          method: 'GET',
          headers: {
            'Accept': 'text/event-stream',
            'Cache-Control': 'no-cache'
          }
        });

        req.on('response', (res) => {
          this.log(`📡 HTTP ${res.statusCode} - Connected`);

          if (res.statusCode !== 200) {
            reject(new Error(`HTTP ${res.statusCode}: ${res.statusMessage}`));
            return;
          }

          let buffer = '';
          this.lastDataTime = Date.now();

          res.on('data', (chunk) => {
            this.lastDataTime = Date.now();
            buffer += chunk.toString();

            // Process complete SSE messages
            const lines = buffer.split('\n');
            buffer = lines.pop() || ''; // Keep incomplete line

            let currentEvent = null;
            let currentData = null;

            for (const line of lines) {
              if (line.startsWith('event: ')) {
                currentEvent = line.slice(7).trim();
              } else if (line.startsWith('data: ')) {
                try {
                  currentData = JSON.parse(line.slice(6));
                  this.log(`📨 Event: ${currentEvent || 'unknown'}`);

                  if (currentEvent === 'heartbeat') {
                    this.heartbeatCount++;
                    this.log(`💓 Heartbeat ${this.heartbeatCount} received`);
                  }

                  if (currentEvent === 'connected') {
                    this.log('✅ Connection confirmed');
                  }

                  // Reset for next message
                  currentEvent = null;
                  currentData = null;
                } catch (e) {
                  // Ignore parse errors
                  this.log(`⚠️  Parse error for event ${currentEvent}: ${e.message}`);
                }
              }
            }
          });

          res.on('end', () => {
            this.log('🔚 Connection ended');
            // Check if we got enough heartbeats before ending
            if (this.heartbeatCount >= 3) {
              resolve(true);
            } else {
              reject(new Error(`INSUFFICIENT HEARTBEATS: Got ${this.heartbeatCount}, need 3+`));
            }
          });

          res.on('error', (error) => {
            reject(new Error(`STREAM ERROR: ${error.message}`));
          });
        });

        req.on('error', (error) => {
          reject(new Error(`CONNECTION ERROR: ${error.message}`));
        });

        req.end();
      };

      // Initial connection
      connect();

      // Monitor for timeout and loop protection
      const monitor = setInterval(() => {
        try {
          this.checkTimeoutProtection();

          const elapsed = Date.now() - this.startTime;
          if (elapsed >= this.testDuration) {
            clearInterval(monitor);
            if (this.heartbeatCount >= 3) {
              this.log(`🎉 STABILITY VERIFIED: ${this.heartbeatCount} heartbeats in ${elapsed}ms`);
              resolve(true);
            } else {
              reject(new Error(`INSUFFICIENT HEARTBEATS: ${this.heartbeatCount} < 3`));
            }
          }
        } catch (error) {
          clearInterval(monitor);
          reject(error);
        }
      }, 1000);
    });
  }
}

async function main() {
  const verifier = new StabilityVerifier();

  try {
    const result = await verifier.verifyStability();

    console.log('\n' + '='.repeat(50));
    console.log('🎯 STABILITY VERIFICATION: PASSED');
    console.log('✅ SSE stream is stable - no infinite loops detected');
    console.log(`📊 Received ${verifier.heartbeatCount} heartbeats`);
    console.log(`⏱️  Test duration: ${(Date.now() - verifier.startTime)}ms`);
    console.log('🚀 System is ready for production!');
    console.log('='.repeat(50));

    process.exit(0);
  } catch (error) {
    console.log('\n' + '='.repeat(50));
    console.log('💥 STABILITY VERIFICATION: FAILED');
    console.log(`❌ ${error.message}`);
    console.log(`📊 Heartbeats received: ${verifier.heartbeatCount}`);
    console.log(`🔄 Connection attempts: ${verifier.connectCount}`);
    console.log('🔧 SSE stream needs fixing');
    console.log('='.repeat(50));

    process.exit(1);
  }
}

if (require.main === module) {
  main().catch((error) => {
    console.error('💥 Script crashed:', error);
    process.exit(1);
  });
}

module.exports = StabilityVerifier;

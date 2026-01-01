/**
 * Retry Service for Frontend
 *
 * Provides automatic retry logic for failed API requests with exponential backoff.
 * Implements circuit breaker pattern for resilient API communication.
 */

export interface RetryOptions {
  /** Maximum number of retry attempts */
  maxRetries?: number;
  /** Base delay between retries in milliseconds */
  baseDelay?: number;
  /** Maximum delay between retries in milliseconds */
  maxDelay?: number;
  /** Backoff multiplier */
  backoffFactor?: number;
  /** Timeout for individual requests in milliseconds */
  timeout?: number;
  /** HTTP status codes that should trigger retries */
  retryableStatusCodes?: number[];
}

export interface RetryState {
  /** Current attempt number (0-based) */
  attempt: number;
  /** Total attempts made so far */
  totalAttempts: number;
  /** Next retry delay in milliseconds */
  nextDelay: number;
  /** Error from the last attempt */
  lastError?: Error;
}

export class RetryError extends Error {
  /** Original error that caused the retry to fail */
  public readonly originalError: Error;
  /** All errors encountered during retry attempts */
  public readonly allErrors: Error[];
  /** Final retry state */
  public readonly retryState: RetryState;

  constructor(
    message: string,
    originalError: Error,
    allErrors: Error[],
    retryState: RetryState
  ) {
    super(message);
    this.name = 'RetryError';
    this.originalError = originalError;
    this.allErrors = allErrors;
    this.retryState = retryState;
  }
}

export class CircuitBreakerError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'CircuitBreakerError';
  }
}

export class RetryService {
  private static instance: RetryService;

  // Circuit breaker state
  private circuitBreakerFailures = 0;
  private circuitBreakerLastFailureTime = 0;
  private readonly circuitBreakerThreshold = 5; // Failures before opening circuit
  private readonly circuitBreakerTimeout = 30000; // 30 seconds timeout
  private readonly circuitBreakerResetTimeout = 60000; // 1 minute to try reset

  // Default retry options
  private readonly defaultOptions: Required<RetryOptions> = {
    maxRetries: 3,
    baseDelay: 1000, // 1 second
    maxDelay: 30000, // 30 seconds
    backoffFactor: 2,
    timeout: 120000, // 2 minutes (constitution requirement)
    retryableStatusCodes: [408, 429, 500, 502, 503, 504], // Timeout, rate limit, server errors
  };

  public static getInstance(): RetryService {
    if (!RetryService.instance) {
      RetryService.instance = new RetryService();
    }
    return RetryService.instance;
  }

  /**
   * Execute a request with automatic retry logic
   */
  async executeWithRetry<T>(
    requestFn: () => Promise<T>,
    options: RetryOptions = {}
  ): Promise<T> {
    const opts = { ...this.defaultOptions, ...options };
    const allErrors: Error[] = [];
    let lastDelay = 0;

    // Check circuit breaker
    this.checkCircuitBreaker();

    for (let attempt = 0; attempt <= opts.maxRetries; attempt++) {
      try {
        // Execute the request with timeout
        const result = await this.executeWithTimeout(requestFn, opts.timeout);

        // Success - reset circuit breaker
        this.circuitBreakerFailures = 0;
        return result;

      } catch (error) {
        const err = error instanceof Error ? error : new Error(String(error));
        allErrors.push(err);

        // Check if this error is retryable
        if (!this.isRetryableError(err, opts.retryableStatusCodes)) {
          // Not retryable - fail immediately
          throw new RetryError(
            `请求失败 (不可重试): ${err.message}`,
            err,
            allErrors,
            {
              attempt,
              totalAttempts: attempt + 1,
              nextDelay: 0,
              lastError: err
            }
          );
        }

        // Check if we've exhausted retries
        if (attempt >= opts.maxRetries) {
          // Record circuit breaker failure
          this.recordCircuitBreakerFailure();

          throw new RetryError(
            `请求失败，已达到最大重试次数 (${opts.maxRetries + 1} 次): ${err.message}`,
            err,
            allErrors,
            {
              attempt,
              totalAttempts: attempt + 1,
              nextDelay: 0,
              lastError: err
            }
          );
        }

        // Calculate next delay with exponential backoff
        lastDelay = Math.min(
          opts.baseDelay * Math.pow(opts.backoffFactor, attempt),
          opts.maxDelay
        );

        // Add jitter to prevent thundering herd
        const jitter = Math.random() * 0.1 * lastDelay;
        const actualDelay = lastDelay + jitter;

        console.warn(
          `请求失败 (尝试 ${attempt + 1}/${opts.maxRetries + 1}): ${err.message}。${Math.round(actualDelay)}ms 后重试...`
        );

        // Wait before retrying
        await this.delay(actualDelay);
      }
    }

    // This should never be reached, but just in case
    throw new Error('Unexpected retry loop exit');
  }

  /**
   * Execute a request with timeout
   */
  private async executeWithTimeout<T>(
    requestFn: () => Promise<T>,
    timeoutMs: number
  ): Promise<T> {
    return new Promise((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        reject(new Error(`请求超时 (${timeoutMs}ms)`));
      }, timeoutMs);

      requestFn()
        .then((result) => {
          clearTimeout(timeoutId);
          resolve(result);
        })
        .catch((error) => {
          clearTimeout(timeoutId);
          reject(error);
        });
    });
  }

  /**
   * Check if an error is retryable
   */
  private isRetryableError(error: Error, retryableStatusCodes: number[]): boolean {
    // Network errors are always retryable
    if (error.message.includes('fetch') ||
        error.message.includes('network') ||
        error.message.includes('timeout') ||
        error.message.includes('连接') ||
        error.message.includes('超时')) {
      return true;
    }

    // Check for HTTP status codes in error message
    const statusMatch = error.message.match(/status (\d+)/i);
    if (statusMatch) {
      const statusCode = parseInt(statusMatch[1], 10);
      return retryableStatusCodes.includes(statusCode);
    }

    // Check for specific error types
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      return true; // Network error
    }

    return false;
  }

  /**
   * Check circuit breaker state
   */
  private checkCircuitBreaker(): void {
    const now = Date.now();

    // If circuit breaker is open
    if (this.circuitBreakerFailures >= this.circuitBreakerThreshold) {
      // Check if we should try to reset
      if (now - this.circuitBreakerLastFailureTime > this.circuitBreakerResetTimeout) {
        console.log('尝试重置熔断器...');
        this.circuitBreakerFailures = Math.floor(this.circuitBreakerThreshold / 2); // Half-open
      } else {
        throw new CircuitBreakerError('服务暂时不可用，请稍后重试');
      }
    }
  }

  /**
   * Record a circuit breaker failure
   */
  private recordCircuitBreakerFailure(): void {
    this.circuitBreakerFailures++;
    this.circuitBreakerLastFailureTime = Date.now();

    console.warn(`熔断器记录失败: ${this.circuitBreakerFailures}/${this.circuitBreakerThreshold}`);
  }

  /**
   * Utility method for delays
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Get current retry statistics
   */
  getStats() {
    return {
      circuitBreakerFailures: this.circuitBreakerFailures,
      circuitBreakerThreshold: this.circuitBreakerThreshold,
      circuitBreakerLastFailureTime: this.circuitBreakerLastFailureTime,
      isCircuitBreakerOpen: this.circuitBreakerFailures >= this.circuitBreakerThreshold
    };
  }

  /**
   * Reset circuit breaker (for testing/admin purposes)
   */
  resetCircuitBreaker(): void {
    this.circuitBreakerFailures = 0;
    this.circuitBreakerLastFailureTime = 0;
    console.log('熔断器已重置');
  }
}

// Export singleton instance
export const retryService = RetryService.getInstance();

// Export convenience function
export async function withRetry<T>(
  requestFn: () => Promise<T>,
  options?: RetryOptions
): Promise<T> {
  return retryService.executeWithRetry(requestFn, options);
}

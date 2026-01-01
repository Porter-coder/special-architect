"""
Circuit breaker pattern implementation for external API calls.

Provides automatic failure detection and recovery to prevent cascade failures
when external services become unavailable.
"""

import asyncio
import time
from contextlib import asynccontextmanager
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type, Union

from .logging_config import get_logger

logger = get_logger()


class CircuitBreakerState(Enum):
    """Circuit breaker operational states."""
    CLOSED = "closed"       # Normal operation
    OPEN = "open"          # Failing, requests blocked
    HALF_OPEN = "half_open" # Testing recovery


class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open."""
    pass


class CircuitBreaker:
    """
    Circuit breaker implementation with configurable failure thresholds and recovery.

    Automatically transitions between CLOSED, OPEN, and HALF_OPEN states based on
    failure patterns and recovery attempts.
    """

    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout: float = 60.0,
        expected_exceptions: Optional[List[Type[Exception]]] = None,
        name: str = "default"
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of consecutive failures before opening
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exceptions: Exception types to count as failures
            name: Identifier for logging and monitoring
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exceptions = expected_exceptions or [Exception]
        self.name = name

        # State management
        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._last_failure_time: Optional[float] = None
        self._success_count = 0

        # Thread safety
        self._lock = asyncio.Lock()

        logger.info(f"Circuit breaker '{name}' initialized", {
            "failure_threshold": failure_threshold,
            "recovery_timeout": recovery_timeout,
            "expected_exceptions": [e.__name__ for e in expected_exceptions]
        })

    @property
    def state(self) -> CircuitBreakerState:
        """Get current circuit breaker state."""
        return self._state

    @property
    def failure_count(self) -> int:
        """Get current failure count."""
        return self._failure_count

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        if self._last_failure_time is None:
            return False
        return time.time() - self._last_failure_time >= self.recovery_timeout

    def _is_failure_exception(self, exception: Exception) -> bool:
        """Check if exception should be counted as a failure."""
        return any(isinstance(exception, exc_type) for exc_type in self.expected_exceptions)

    async def _record_success(self) -> None:
        """Record successful operation."""
        async with self._lock:
            self._failure_count = 0
            self._success_count += 1

            # Transition from HALF_OPEN to CLOSED after first success
            if self._state == CircuitBreakerState.HALF_OPEN:
                self._state = CircuitBreakerState.CLOSED
                logger.info(f"Circuit breaker '{self.name}' recovered to CLOSED state", {
                    "success_count": self._success_count
                })

    async def _record_failure(self, exception: Exception) -> None:
        """Record failed operation."""
        async with self._lock:
            if self._is_failure_exception(exception):
                self._failure_count += 1
                self._last_failure_time = time.time()

                # Transition to OPEN if threshold exceeded
                if (self._state == CircuitBreakerState.CLOSED and
                    self._failure_count >= self.failure_threshold):
                    self._state = CircuitBreakerState.OPEN
                    logger.warning(f"Circuit breaker '{self.name}' opened", {
                        "failure_count": self._failure_count,
                        "threshold": self.failure_threshold,
                        "last_exception": str(exception)
                    })

                # Reset success count on failure
                self._success_count = 0

    @asynccontextmanager
    async def call_context(self):
        """
        Context manager for circuit breaker protected calls.

        Usage:
            async with circuit_breaker.call_context():
                result = await some_async_call()
        """
        if self._state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                async with self._lock:
                    if self._should_attempt_reset():  # Double-check after lock
                        self._state = CircuitBreakerState.HALF_OPEN
                        logger.info(f"Circuit breaker '{self.name}' attempting recovery")
            else:
                logger.warning(f"Circuit breaker '{self.name}' blocking request (OPEN state)")
                raise CircuitBreakerOpenException(f"Circuit breaker '{self.name}' is OPEN")

        try:
            yield
            await self._record_success()
        except Exception as e:
            await self._record_failure(e)
            raise

    async def call(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.

        Args:
            func: Async function to call
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Function result

        Raises:
            CircuitBreakerOpenException: If circuit breaker is open
            Exception: Original function exception
        """
        async with self.call_context():
            return await func(*args, **kwargs)

    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status for monitoring."""
        return {
            "name": self.name,
            "state": self._state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout": self.recovery_timeout,
            "last_failure_time": self._last_failure_time,
            "can_attempt_reset": self._should_attempt_reset() if self._state == CircuitBreakerState.OPEN else None
        }


# Global circuit breaker instances
_circuit_breakers: Dict[str, CircuitBreaker] = {}


def get_circuit_breaker(
    name: str = "minimax_api",
    failure_threshold: int = 3,
    recovery_timeout: float = 60.0,
    expected_exceptions: Optional[List[Type[Exception]]] = None
) -> CircuitBreaker:
    """
    Get or create a circuit breaker instance.

    Args:
        name: Circuit breaker identifier
        failure_threshold: Number of failures before opening
        recovery_timeout: Seconds to wait before recovery attempt
        expected_exceptions: Exception types to count as failures

    Returns:
        CircuitBreaker instance
    """
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            expected_exceptions=expected_exceptions,
            name=name
        )

    return _circuit_breakers[name]


def get_all_circuit_breakers() -> Dict[str, CircuitBreaker]:
    """Get all circuit breaker instances for monitoring."""
    return _circuit_breakers.copy()


def reset_circuit_breaker(name: str) -> bool:
    """
    Manually reset a circuit breaker to CLOSED state.

    Args:
        name: Circuit breaker name

    Returns:
        True if reset successful, False if breaker doesn't exist
    """
    if name in _circuit_breakers:
        breaker = _circuit_breakers[name]
        asyncio.create_task(_reset_breaker_async(breaker))
        return True
    return False


async def _reset_breaker_async(breaker: CircuitBreaker) -> None:
    """Async helper for manual reset."""
    async with breaker._lock:
        breaker._state = CircuitBreakerState.CLOSED
        breaker._failure_count = 0
        breaker._success_count = 0
        logger.info(f"Circuit breaker '{breaker.name}' manually reset to CLOSED")

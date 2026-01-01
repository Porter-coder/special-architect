"""
Concurrency Manager Service

Manages concurrent user requests and enforces the 1-5 user limit per constitution.
Provides thread-safe request tracking and queue management.
"""

import asyncio
import logging
import threading
from typing import Dict, List, Set
from uuid import UUID
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class ActiveRequest:
    """Represents an active request."""
    request_id: UUID
    user_id: str  # IP address or session identifier
    start_time: datetime
    endpoint: str


class ConcurrencyManagerError(Exception):
    """Exception raised for concurrency management errors."""
    pass


class ConcurrencyManager:
    """
    Manages concurrent requests and enforces user limits.

    Constitution requirement: 1-5 concurrent users maximum.
    """

    def __init__(self, max_concurrent_users: int = 5):
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.max_concurrent_users = max_concurrent_users

        # Thread-safe storage
        self._lock = threading.RLock()
        self._active_requests: Dict[UUID, ActiveRequest] = {}
        self._user_request_counts: Dict[str, int] = {}

        # Request history for monitoring
        self._request_history: List[ActiveRequest] = []
        self._max_history_size = 1000

        # Statistics
        self._total_requests_processed = 0
        self._peak_concurrent_users = 0
        self._rejected_requests = 0

    def can_accept_request(self, user_id: str) -> bool:
        """
        Check if a new request can be accepted for the given user.

        Args:
            user_id: User identifier (IP address or session ID)

        Returns:
            bool: True if request can be accepted, False otherwise
        """
        with self._lock:
            current_active = len(self._active_requests)
            user_active = self._user_request_counts.get(user_id, 0)

            # Check overall concurrent limit
            if current_active >= self.max_concurrent_users:
                self.logger.warning(f"Concurrent limit reached: {current_active}/{self.max_concurrent_users}")
                return False

            # Check per-user limit (constitution allows max 1-5 concurrent users total)
            # For fairness, limit individual users to reasonable concurrent requests
            if user_active >= 2:  # Allow max 2 concurrent requests per user
                self.logger.warning(f"User {user_id} has too many active requests: {user_active}")
                return False

            return True

    def register_request(self, request_id: UUID, user_id: str, endpoint: str) -> None:
        """
        Register a new active request.

        Args:
            request_id: Unique request identifier
            user_id: User identifier
            endpoint: API endpoint being accessed

        Raises:
            ConcurrencyManagerError: If request cannot be registered
        """
        with self._lock:
            if not self.can_accept_request(user_id):
                self._rejected_requests += 1
                raise ConcurrencyManagerError("当前并发请求过多，请稍后重试")

            if request_id in self._active_requests:
                raise ConcurrencyManagerError(f"请求 {request_id} 已在处理中")

            # Register the request
            active_request = ActiveRequest(
                request_id=request_id,
                user_id=user_id,
                start_time=datetime.now(),
                endpoint=endpoint
            )

            self._active_requests[request_id] = active_request
            self._user_request_counts[user_id] = self._user_request_counts.get(user_id, 0) + 1

            # Update peak statistics
            current_active = len(self._active_requests)
            if current_active > self._peak_concurrent_users:
                self._peak_concurrent_users = current_active

            # Add to history
            self._request_history.append(active_request)
            if len(self._request_history) > self._max_history_size:
                self._request_history.pop(0)

            self.logger.info(f"注册请求: {request_id}, 用户: {user_id}, 活跃请求: {current_active}/{self.max_concurrent_users}")

    def unregister_request(self, request_id: UUID) -> None:
        """
        Unregister a completed request.

        Args:
            request_id: Request identifier to remove
        """
        with self._lock:
            if request_id in self._active_requests:
                request = self._active_requests[request_id]
                user_id = request.user_id

                # Remove from active requests
                del self._active_requests[request_id]

                # Update user count
                if user_id in self._user_request_counts:
                    self._user_request_counts[user_id] -= 1
                    if self._user_request_counts[user_id] <= 0:
                        del self._user_request_counts[user_id]

                self._total_requests_processed += 1

                duration = datetime.now() - request.start_time
                self.logger.info(f"完成请求: {request_id}, 持续时间: {duration.total_seconds():.2f}s, 剩余活跃请求: {len(self._active_requests)}")

    def get_active_requests_count(self) -> int:
        """
        Get the current number of active requests.

        Returns:
            int: Number of active requests
        """
        with self._lock:
            return len(self._active_requests)

    def get_user_active_requests(self, user_id: str) -> int:
        """
        Get the number of active requests for a specific user.

        Args:
            user_id: User identifier

        Returns:
            int: Number of active requests for the user
        """
        with self._lock:
            return self._user_request_counts.get(user_id, 0)

    def get_statistics(self) -> Dict:
        """
        Get concurrency statistics.

        Returns:
            Dict: Statistics about request handling
        """
        with self._lock:
            return {
                "current_active_requests": len(self._active_requests),
                "max_concurrent_users": self.max_concurrent_users,
                "total_requests_processed": self._total_requests_processed,
                "peak_concurrent_users": self._peak_concurrent_users,
                "rejected_requests": self._rejected_requests,
                "unique_active_users": len(self._user_request_counts),
                "active_requests_by_user": dict(self._user_request_counts)
            }

    def cleanup_stale_requests(self, max_age_seconds: int = 3600) -> int:
        """
        Clean up stale requests that have been active for too long.

        Args:
            max_age_seconds: Maximum age for requests in seconds

        Returns:
            int: Number of requests cleaned up
        """
        with self._lock:
            cutoff_time = datetime.now() - timedelta(seconds=max_age_seconds)
            stale_requests = []

            for request_id, request in self._active_requests.items():
                if request.start_time < cutoff_time:
                    stale_requests.append(request_id)

            # Clean up stale requests
            for request_id in stale_requests:
                self.unregister_request(request_id)

            if stale_requests:
                self.logger.warning(f"清理了 {len(stale_requests)} 个过期的活跃请求")

            return len(stale_requests)

    def get_active_requests_details(self) -> List[Dict]:
        """
        Get detailed information about active requests.

        Returns:
            List[Dict]: Details of active requests
        """
        with self._lock:
            result = []
            for request in self._active_requests.values():
                duration = datetime.now() - request.start_time
                result.append({
                    "request_id": str(request.request_id),
                    "user_id": request.user_id,
                    "endpoint": request.endpoint,
                    "start_time": request.start_time.isoformat(),
                    "duration_seconds": duration.total_seconds()
                })
            return result

    async def periodic_cleanup(self, interval_seconds: int = 300) -> None:
        """
        Run periodic cleanup of stale requests.

        Args:
            interval_seconds: Cleanup interval in seconds
        """
        while True:
            try:
                await asyncio.sleep(interval_seconds)
                cleaned = self.cleanup_stale_requests()
                if cleaned > 0:
                    self.logger.info(f"定期清理: 移除了 {cleaned} 个过期请求")
            except Exception as e:
                self.logger.error(f"定期清理失败: {e}")


# Global concurrency manager instance
concurrency_manager = ConcurrencyManager()

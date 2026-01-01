"""
API Dependencies for AI Code Flow

FastAPI dependencies for request validation and service injection.
"""

from typing import Optional

from fastapi import Request
from pydantic import BaseModel


class CodeGenerationRequest(BaseModel):
    """Request model for code generation."""
    user_input: str

    class Config:
        schema_extra = {
            "example": {
                "user_input": "帮我写个贪吃蛇游戏"
            }
        }


async def get_request_ip(request: Request) -> str:
    """Extract client IP address from request."""
    # Get IP from various headers (handle proxies)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    return request.client.host if request.client else "unknown"


def validate_concurrent_requests(current_requests: int, max_requests: int = 5) -> bool:
    """
    Validate that current concurrent requests don't exceed limit.

    Args:
        current_requests: Number of currently active requests
        max_requests: Maximum allowed concurrent requests

    Returns:
        True if within limits, False if exceeded
    """
    return current_requests < max_requests

"""
Health API Endpoints

Provides service health check endpoints for monitoring and diagnostics.
"""

import logging
from typing import Dict

from fastapi import APIRouter

from ..services.code_generation_service import CodeGenerationService


# Create router for health endpoints
router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize service for health checks
code_generation_service = CodeGenerationService()

# Constants for concurrent requests (shared with other API modules)
MAX_CONCURRENT_REQUESTS = 5


@router.get("/health")
async def health_check() -> Dict:
    """
    Health check endpoint.

    Returns service health status and concurrent request information.
    """
    try:
        # Basic health check - try to validate AI service connection
        connection_ok = await code_generation_service.ai_service.validate_connection()

        # Get current active requests count (simplified - in production would use shared state)
        # For now, return 0 as we don't have shared state management
        current_active = 0

        if connection_ok:
            return {
                "status": "healthy",
                "concurrent_requests": current_active,
                "max_concurrent": MAX_CONCURRENT_REQUESTS,
                "message": "服务运行正常"
            }
        else:
            return {
                "status": "degraded",
                "concurrent_requests": current_active,
                "max_concurrent": MAX_CONCURRENT_REQUESTS,
                "message": "AI 服务连接异常"
            }

    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "concurrent_requests": 0,
            "max_concurrent": MAX_CONCURRENT_REQUESTS,
            "message": "服务异常"
        }

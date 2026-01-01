"""
API package for AI Code Flow backend.

Contains all API routes and dependencies.
"""

from .routes import router
from .health import router as health_router
from .projects import router as projects_router
from .dependencies import CodeGenerationRequest, get_request_ip, validate_concurrent_requests

__all__ = [
    'router',
    'health_router',
    'projects_router',
    'CodeGenerationRequest',
    'get_request_ip',
    'validate_concurrent_requests'
]

"""
AI Code Flow Backend Application

FastAPI application for AI-powered code generation with educational process transparency.
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict, List

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .api.routes import router
from .services.ai_service import AIServiceError
from .services.container import container


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("正在启动 AI Code Flow 后端服务...")

    try:
        # Initialize services
        await container.initialize_services()

        logger.info("AI Code Flow 后端服务启动成功")

    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        raise

    yield

    # Shutdown
    logger.info("正在关闭 AI Code Flow 后端服务...")
    container.shutdown_services()


# Create FastAPI application
app = FastAPI(
    title="AI Code Flow API",
    description="AI-powered code generation with educational process transparency",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")


@app.get("/health")
async def health_check() -> Dict:
    """
    Health check endpoint.

    Returns service health status and basic metrics.
    """
    try:
        # Check AI service connectivity
        ai_healthy = await container.ai_service.validate_connection()

        # Get basic metrics
        project_count = len(container.file_service.get_project_list())

        return {
            "status": "healthy" if ai_healthy else "degraded",
            "services": {
                "ai_service": "healthy" if ai_healthy else "unhealthy",
                "file_service": "healthy"
            },
            "metrics": {
                "total_projects": project_count
            },
            "message": "服务运行正常" if ai_healthy else "AI 服务连接异常"
        }

    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "services": {
                "ai_service": "unknown",
                "file_service": "unknown"
            },
            "metrics": {},
            "message": "服务状态检查失败"
        }


@app.exception_handler(AIServiceError)
async def ai_service_exception_handler(request: Request, exc: AIServiceError) -> JSONResponse:
    """Handle AI service exceptions with Chinese error messages."""
    logger.error(f"AI 服务错误: {exc}")

    if isinstance(exc, AIServiceError):
        return JSONResponse(
            status_code=500,
            content={"message": f"AI 服务错误: {str(exc)}"}
        )

    return JSONResponse(
        status_code=500,
        content={"message": "AI 服务暂时不可用，请稍后重试"}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions with Chinese error messages per constitution."""
    logger.error(f"未处理的异常: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={"message": "服务器内部错误，请稍后重试"}
    )


@app.get("/")
async def root() -> Dict:
    """Root endpoint with basic service information."""
    return {
        "name": "AI Code Flow Backend",
        "version": "1.0.0",
        "description": "AI-powered code generation with educational process transparency",
        "health": "/health",
        "docs": "/docs"
    }


if __name__ == "__main__":
    # Development server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

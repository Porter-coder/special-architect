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
from .api.health import router as health_router
from .api.projects import router as projects_router
from .services.ai_service import AIServiceError
from .services.code_generation_service import CodeGenerationServiceError
from .services.project_service import ProjectServiceError
from .services.file_service import FileServiceError
from .services.code_parser import CodeParserError
from .services.content_processor import ContentProcessorError
from .services.dependency_validator import DependencyValidationError
from .services.phase_manager import PhaseManagerError
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
app.include_router(health_router, prefix="/api")
app.include_router(projects_router, prefix="/api")




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


@app.exception_handler(CodeGenerationServiceError)
async def code_generation_service_exception_handler(request: Request, exc: CodeGenerationServiceError) -> JSONResponse:
    """Handle code generation service exceptions with Chinese error messages."""
    logger.error(f"代码生成服务错误: {exc}")

    return JSONResponse(
        status_code=500,
        content={"message": f"代码生成失败: {str(exc)}"}
    )


@app.exception_handler(ProjectServiceError)
async def project_service_exception_handler(request: Request, exc: ProjectServiceError) -> JSONResponse:
    """Handle project service exceptions with Chinese error messages."""
    logger.error(f"项目服务错误: {exc}")

    return JSONResponse(
        status_code=500,
        content={"message": f"项目操作失败: {str(exc)}"}
    )


@app.exception_handler(FileServiceError)
async def file_service_exception_handler(request: Request, exc: FileServiceError) -> JSONResponse:
    """Handle file service exceptions with Chinese error messages."""
    logger.error(f"文件服务错误: {exc}")

    return JSONResponse(
        status_code=500,
        content={"message": f"文件操作失败: {str(exc)}"}
    )


@app.exception_handler(CodeParserError)
async def code_parser_exception_handler(request: Request, exc: CodeParserError) -> JSONResponse:
    """Handle code parser exceptions with Chinese error messages."""
    logger.error(f"代码解析错误: {exc}")

    return JSONResponse(
        status_code=400,
        content={"message": f"代码解析失败: {str(exc)}"}
    )


@app.exception_handler(ContentProcessorError)
async def content_processor_exception_handler(request: Request, exc: ContentProcessorError) -> JSONResponse:
    """Handle content processor exceptions with Chinese error messages."""
    logger.error(f"内容处理错误: {exc}")

    return JSONResponse(
        status_code=400,
        content={"message": f"内容处理失败: {str(exc)}"}
    )


@app.exception_handler(DependencyValidationError)
async def dependency_validation_exception_handler(request: Request, exc: DependencyValidationError) -> JSONResponse:
    """Handle dependency validation exceptions with Chinese error messages."""
    logger.error(f"依赖验证错误: {exc}")

    return JSONResponse(
        status_code=400,
        content={"message": f"依赖验证失败: {str(exc)}"}
    )


@app.exception_handler(PhaseManagerError)
async def phase_manager_exception_handler(request: Request, exc: PhaseManagerError) -> JSONResponse:
    """Handle phase manager exceptions with Chinese error messages."""
    logger.error(f"阶段管理错误: {exc}")

    return JSONResponse(
        status_code=500,
        content={"message": f"处理阶段错误: {str(exc)}"}
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

"""
Generate API Endpoints

Handles code generation requests and streaming responses.
Implements the core /generate-code endpoint with Server-Sent Events.
"""

import asyncio
import logging
from typing import Dict, List
from uuid import UUID

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel

from ..models.code_generation_request import CodeGenerationRequest, RequestStatus
from ..models.process_phase import ProcessPhase, PhaseName, get_phase_message, is_valid_phase_transition
from ..services.ai_service import AIServiceError
from ..services.code_generation_service import CodeGenerationService, CodeGenerationServiceError


class GenerateRequest(BaseModel):
    """Request model for code generation."""
    user_input: str
    application_type: str = ""  # Optional application type for US3


# Global service instances
from ..services.code_generation_service import CodeGenerationService
from ..services.concurrency_manager import concurrency_manager

# Initialize service
code_generation_service = CodeGenerationService()

# In-memory storage for active requests (in production, use Redis/database)
active_requests: Dict[UUID, CodeGenerationRequest] = {}
request_phases: Dict[UUID, List[ProcessPhase]] = {}


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/generate-code", response_model=Dict)
async def generate_code(request: GenerateRequest, background_tasks: BackgroundTasks) -> Dict:
    """
    Generate code from natural language request with three-phase workflow.

    This endpoint implements the core AI Code Flow functionality:
    1. Accepts natural language requests (e.g., "Create a web app" or "Build a calculator")
    2. Processes through Specify → Plan → Implement phases
    3. Returns streaming progress updates via Server-Sent Events
    4. Generates working, executable code

    Args:
        request: GenerateRequest with user_input field

    Returns:
        Dictionary with request_id for tracking progress

    Raises:
        HTTPException: For validation errors or system overload
    """
    global current_active_requests

    try:
        # Get user identifier (use IP address for simplicity)
        user_id = "127.0.0.1"  # In production, extract from request headers

        # Validate input
        if not request.user_input or not request.user_input.strip():
            raise HTTPException(status_code=400, detail="用户输入不能为空")

        if len(request.user_input) > 1000:
            raise HTTPException(status_code=400, detail="用户输入长度不能超过1000个字符")

        # Create new request using our service
        code_request = await code_generation_service.start_generation(
            request.user_input,
            request.application_type
        )

        # Register with concurrency manager
        try:
            concurrency_manager.register_request(
                code_request.request_id,
                user_id,
                "/api/generate-code"
            )
        except Exception as e:
            logger.error(f"并发管理器注册失败: {e}")
            raise HTTPException(status_code=429, detail="当前并发请求过多，请稍后重试")

        # Store request
        active_requests[code_request.request_id] = code_request
        request_phases[code_request.request_id] = []

        active_count = concurrency_manager.get_active_requests_count()
        logger.info(f"代码生成请求已创建: {code_request.request_id} (活跃请求: {active_count})")

        # Start background processing
        background_tasks.add_task(process_code_generation, code_request.request_id)

        return {
            "request_id": str(code_request.request_id),
            "message": "代码生成请求已开始处理",
            "status": "processing",
            "phases": ["specify", "plan", "implement"]  # Inform client of expected phases
        }

    except HTTPException:
        raise
    except Exception as e:
        # Unregister from concurrency manager on failure if request was registered
        if 'code_request' in locals():
            try:
                concurrency_manager.unregister_request(code_request.request_id)
            except:
                pass  # Ignore errors during cleanup
        logger.error(f"启动代码生成失败: {e}")
        raise HTTPException(status_code=500, detail="启动代码生成失败，请稍后重试")


@router.get("/generate-code/{request_id}/stream")
async def stream_generation_progress(request_id: UUID):
    """
    Stream real-time progress updates for a code generation request.

    Uses Server-Sent Events (SSE) to provide live updates of the generation process,
    including phase transitions, educational messages, and AI thinking traces.

    Event Types:
    - phase_update: Phase transitions with educational messages
    - content_chunk: Raw AI output (thinking, code, documentation)
    - completion: Generation complete with project details
    - error: Generation failed with retry options

    Args:
        request_id: Unique request identifier

    Returns:
        Server-Sent Events stream
    """
    logger.info(f"开始处理 SSE 请求: {request_id}")

    if request_id not in active_requests:
        logger.warning(f"请求不存在: {request_id}")
        raise HTTPException(status_code=404, detail="请求不存在")

    async def event_generator():
        """Generate SSE events for the request progress."""
        try:
            # Send initial connection success event
            yield {
                "event": "connected",
                "data": f"已连接到请求 {request_id}"
            }

            # Check current request status
            request = active_requests[request_id]

            # If request is already completed or failed, send final status
            if request.status == RequestStatus.COMPLETED:
                # Load project info
                project = code_generation_service.project_service.load_project_metadata(request_id)
                if project:
                    yield {
                        "event": "completion",
                        "data": {
                            "project_id": str(project.id),
                            "main_file": project.main_file,
                            "project_name": project.project_name,
                            "status": "success",
                            "message": "代码生成完成"
                        }
                    }
                else:
                    yield {"event": "error", "data": "项目生成失败"}
                return
            elif request.status == RequestStatus.FAILED:
                yield {
                    "event": "error",
                    "data": {
                        "message": request.error_message or "代码生成失败",
                        "can_retry": True
                    }
                }
                return

            # For active requests, stream the generation process
            try:
                # Stream the generation process
                async for event in code_generation_service.generate_code_stream(request):
                    if event.get("type") == "phase_start":
                        yield {
                            "event": "phase_update",
                            "data": {
                                "phase": event.get("phase"),
                                "message": event.get("message", ""),
                                "status": "active"
                            }
                        }
                    elif event.get("type") == "phase_complete":
                        yield {
                            "event": "phase_update",
                            "data": {
                                "phase": event.get("phase"),
                                "status": "completed",
                                "result": event.get("result", "")
                            }
                        }
                    elif event.get("type") == "content_chunk":
                        yield {
                            "event": "content_chunk",
                            "data": {
                                "type": event.get("content_type", "text"),
                                "content": event.get("content", "")
                            }
                        }
                    elif event.get("type") == "thinking":
                        # Raw AI thinking content streaming (FR-022)
                        yield {
                            "event": "ai_thinking",
                            "data": {
                                "phase": event.get("phase"),
                                "content": event.get("content", ""),
                                "timestamp": event.get("timestamp", ""),
                                "raw_type": "thinking_trace"
                            }
                        }
                    elif event.get("type") == "text":
                        # Raw AI text content streaming (FR-022)
                        yield {
                            "event": "ai_content",
                            "data": {
                                "phase": event.get("phase"),
                                "content": event.get("content", ""),
                                "timestamp": event.get("timestamp", ""),
                                "raw_type": "generated_text"
                            }
                        }
                    elif event.get("type") == "workflow_complete":
                        yield {
                            "event": "completion",
                            "data": {
                                "status": "success",
                                "message": "所有阶段执行完成"
                            }
                        }
                    elif event.get("type") == "workflow_failed":
                        yield {
                            "event": "error",
                            "data": {
                                "message": "工作流执行失败",
                                "completed_phases": event.get("completed_phases", [])
                            }
                        }

                    # Small delay to prevent overwhelming the client
                    await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"流式生成错误: {e}")
                yield {
                    "event": "error",
                    "data": f"生成过程出错: {str(e)}"
                }

        except Exception as e:
            logger.error(f"SSE 生成器错误: {e}")
            yield {
                "event": "error",
                "data": "流式响应错误"
            }

    return EventSourceResponse(event_generator())


async def process_code_generation(request_id: UUID):
    """
    Background task to process code generation through all phases.

    Args:
        request_id: Unique request identifier
    """
    try:
        logger.info(f"开始处理代码生成请求: {request_id}")

        # Get the request object
        if request_id not in active_requests:
            logger.error(f"请求不存在: {request_id}")
            return

        request = active_requests[request_id]

        # Process the generation using our service
        try:
            # Run the generation workflow
            async for event in code_generation_service.generate_code_stream(request):
                # Events are handled by the streaming endpoint
                # Here we just ensure the process completes
                pass

            # Check final status
            if request_id in active_requests:
                current_request = active_requests[request_id]
                if current_request.status == RequestStatus.COMPLETED:
                    logger.info(f"代码生成完成: {request_id}")
                elif current_request.status == RequestStatus.FAILED:
                    logger.error(f"代码生成失败: {request_id} - {current_request.error_message}")

        except CodeGenerationServiceError as e:
            logger.error(f"代码生成服务错误: {request_id} - {e}")
            if request_id in active_requests:
                active_requests[request_id].update_status(RequestStatus.FAILED, str(e))

        except Exception as e:
            logger.error(f"代码生成处理失败: {request_id} - {e}", exc_info=True)
            if request_id in active_requests:
                active_requests[request_id].update_status(RequestStatus.FAILED, f"系统错误: {str(e)}")

    finally:
        # Always unregister from concurrency manager
        concurrency_manager.unregister_request(request_id)
        active_count = concurrency_manager.get_active_requests_count()
        logger.info(f"请求处理完成: {request_id} (剩余活跃请求: {active_count})")

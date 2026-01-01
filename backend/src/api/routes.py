"""
API Routes for AI Code Flow

FastAPI routes for code generation, progress streaming, and file retrieval.
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
from ..models.generated_project import GeneratedProject
from ..services.ai_service import AIServiceError
from ..services.file_service import FileServiceError
from ..services.code_generation_service import CodeGenerationService, CodeGenerationServiceError


class GenerateRequest(BaseModel):
    """Request model for code generation."""
    user_input: str


# Global service instances
code_generation_service = CodeGenerationService()

# In-memory storage for active requests (in production, use Redis/database)
active_requests: Dict[UUID, CodeGenerationRequest] = {}

# Concurrent request limiting (constitution requirement: 1-5 users)
MAX_CONCURRENT_REQUESTS = 5
current_active_requests = 0


router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory storage for active requests (in production, use Redis/database)
active_requests: Dict[UUID, CodeGenerationRequest] = {}
request_phases: Dict[UUID, List[ProcessPhase]] = {}

# Concurrent request limiting (constitution requirement: 1-5 users)
MAX_CONCURRENT_REQUESTS = 5
current_active_requests = 0


@router.post("/generate-code", response_model=Dict)
async def start_code_generation(request: GenerateRequest, background_tasks: BackgroundTasks) -> Dict:
    """
    Start a code generation request.

    Accepts a natural language request and initiates the AI-powered code generation process.
    Returns immediately with a request ID for progress tracking.
    """
    global current_active_requests

    try:
        # Check concurrent request limit (constitution requirement: 1-5 users)
        if current_active_requests >= MAX_CONCURRENT_REQUESTS:
            raise HTTPException(
                status_code=429,
                detail="当前并发请求过多，请稍后重试"
            )

        # Increment active request counter
        current_active_requests += 1

        # Create new request using our service
        code_request = await code_generation_service.start_generation(request.user_input)

        # Store request
        active_requests[code_request.request_id] = code_request

        logger.info(f"代码生成请求已创建: {code_request.request_id} (活跃请求: {current_active_requests}/{MAX_CONCURRENT_REQUESTS})")

        # Start background processing
        background_tasks.add_task(process_code_generation, code_request.request_id)

        return {
            "request_id": str(code_request.request_id),
            "message": "代码生成请求已开始处理",
            "status": "processing"
        }

    except HTTPException:
        raise
    except Exception as e:
        # Decrement counter on failure
        current_active_requests = max(0, current_active_requests - 1)
        logger.error(f"启动代码生成失败: {e}")
        raise HTTPException(status_code=500, detail="启动代码生成失败，请稍后重试")


@router.get("/generate-code/{request_id}/stream")
async def stream_generation_progress(request_id: UUID):
    """
    Stream real-time progress updates for a code generation request.

    Uses Server-Sent Events to provide live updates of the generation process,
    including phase changes and educational messages.
    """
    logger.info(f"开始处理 SSE 请求: {request_id}")

    if request_id not in active_requests:
        logger.warning(f"请求不存在: {request_id}")
        raise HTTPException(status_code=404, detail="请求不存在")

    async def event_generator():
        """Generate SSE events for the request progress."""
        try:
            # Send initial connection success event
            yield {"event": "connected", "data": f"已连接到请求 {request_id}"}

            # Check current request status
            request = active_requests[request_id]

            # If request is already completed or failed, send final status
            if request.status == RequestStatus.COMPLETED:
                project = code_generation_service.file_service.load_project_metadata(request_id)
                if project:
                    yield {
                        "event": "complete",
                        "data": {
                            "project_id": str(project.project_id),
                            "main_file": project.main_file_path,
                            "project_name": project.project_name
                        }
                    }
                else:
                    yield {"event": "error", "data": "项目生成失败"}
                return
            elif request.status == RequestStatus.FAILED:
                yield {
                    "event": "error",
                    "data": request.error_message or "代码生成失败"
                }
                return

            # For active requests, poll for status updates
            while True:
                try:
                    # Check if request is still active
                    if request_id not in active_requests:
                        yield {"event": "error", "data": "请求已完成或不存在"}
                        break

                    request = active_requests[request_id]

                    # Check if generation is complete
                    if request.status in [RequestStatus.COMPLETED, RequestStatus.FAILED]:
                        logger.info(f"生成完成 - 请求: {request_id}, 状态: {request.status}")
                        if request.status == RequestStatus.COMPLETED:
                            # Load project info
                            project = code_generation_service.file_service.load_project_metadata(request_id)
                            if project:
                                yield {
                                    "event": "complete",
                                    "data": {
                                        "project_id": str(project.project_id),
                                        "main_file": project.main_file_path,
                                        "project_name": project.project_name
                                    }
                                }
                            else:
                                yield {"event": "error", "data": "项目生成失败"}
                        else:
                            yield {
                                "event": "error",
                                "data": request.error_message or "代码生成失败"
                            }
                        break

                    # Wait before next check
                    await asyncio.sleep(1)

                except Exception as e:
                    logger.error(f"SSE 循环错误: {e}")
                    yield {"event": "error", "data": f"流式响应错误: {str(e)}"}
                    break

        except Exception as e:
            logger.error(f"SSE 生成器错误: {e}")
            yield {"event": "error", "data": "流式响应错误"}

    return EventSourceResponse(event_generator())


@router.get("/generate/{request_id}/files")
async def get_generated_files(request_id: UUID) -> Dict:
    """
    Retrieve all files generated for a completed request.

    Returns the project structure and file contents for download.
    """
    try:
        # Check if request exists and is completed
        if request_id not in active_requests:
            raise HTTPException(status_code=404, detail="请求不存在")

        request = active_requests[request_id]
        if request.status == RequestStatus.PROCESSING:
            raise HTTPException(status_code=425, detail="请求正在处理中，请稍后查看")

        if request.status != RequestStatus.COMPLETED:
            raise HTTPException(status_code=404, detail="请求尚未完成或生成失败")

        # Load project metadata
        project = code_generation_service.file_service.load_project_metadata(request_id)
        if not project:
            raise HTTPException(status_code=404, detail="项目文件不存在")

        # Load all files
        files = await code_generation_service.get_generated_files(request_id)

        return {
            "project_name": project.project_name,
            "main_file": project.main_file_path,
            "files": [
                {
                    "path": path,
                    "content": content,
                    "encoding": "utf-8"  # Constitution requirement
                }
                for path, content in files.items()
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取生成文件失败: {e}")
        raise HTTPException(status_code=500, detail="获取文件失败，请稍后重试")


@router.post("/generate/{request_id}/retry")
async def retry_generation(request_id: UUID, background_tasks: BackgroundTasks) -> Dict:
    """
    Retry a failed code generation request.

    Creates a new request cycle for the same user input.
    """
    global current_active_requests

    try:
        # Check if original request exists and failed
        if request_id not in active_requests:
            raise HTTPException(status_code=404, detail="原请求不存在")

        original_request = active_requests[request_id]
        if original_request.status != RequestStatus.FAILED:
            raise HTTPException(status_code=400, detail="只有失败的请求才能重试")

        # Check concurrent request limit
        if current_active_requests >= MAX_CONCURRENT_REQUESTS:
            raise HTTPException(
                status_code=429,
                detail="当前并发请求过多，请稍后重试"
            )

        # Increment active request counter
        current_active_requests += 1

        # Create new request with same input
        from uuid import uuid4
        new_request_id = uuid4()
        new_request = CodeGenerationRequest(
            request_id=new_request_id,
            user_input=original_request.user_input
        )

        # Store new request
        active_requests[new_request_id] = new_request
        request_phases[new_request_id] = []

        # Start background processing
        background_tasks.add_task(process_code_generation, new_request_id, new_request.user_input)

        logger.info(f"重试请求已启动: {new_request_id} (原请求: {request_id}) - 活跃请求: {current_active_requests}/{MAX_CONCURRENT_REQUESTS}")

        return {
            "request_id": str(new_request_id),
            "message": "重试请求已开始处理",
            "status": "processing"
        }

    except HTTPException:
        raise
    except Exception as e:
        # Decrement counter on failure
        current_active_requests = max(0, current_active_requests - 1)
        logger.error(f"重试请求失败: {e}")
        raise HTTPException(status_code=500, detail="重试请求失败，请稍后重试")


@router.get("/health")
async def health_check() -> Dict:
    """
    Health check endpoint.

    Returns service health status and concurrent request information.
    """
    global current_active_requests

    try:
        # Basic health check - try to validate AI service connection
        connection_ok = await code_generation_service.ai_service.validate_connection()

        if connection_ok:
            return {
                "status": "healthy",
                "concurrent_requests": current_active_requests,
                "max_concurrent": MAX_CONCURRENT_REQUESTS,
                "message": "服务运行正常"
            }
        else:
            return {
                "status": "degraded",
                "concurrent_requests": current_active_requests,
                "max_concurrent": MAX_CONCURRENT_REQUESTS,
                "message": "AI 服务连接异常"
            }

    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "concurrent_requests": current_active_requests,
            "max_concurrent": MAX_CONCURRENT_REQUESTS,
            "message": "服务异常"
        }


async def process_code_generation(request_id: UUID):
    """
    Background task to process code generation through all phases.

    Args:
        request_id: Unique request identifier
    """
    global current_active_requests

    try:
        logger.info(f"开始处理代码生成请求: {request_id}")

        # Get the request object
        if request_id not in active_requests:
            logger.error(f"请求不存在: {request_id}")
            return

        request = active_requests[request_id]

        # Process the generation using our service
        # Note: This will handle all streaming internally, but we need to collect the results
        # For now, we'll run it without streaming to collect the final result
        # In a future enhancement, we could store streaming events for later retrieval

        # Since our service yields streaming events, we need to consume them
        events = []
        async for event in code_generation_service.generate_code_stream(request):
            events.append(event)
            logger.info(f"生成事件: {event.get('type')} - {request_id}")

        # Check final status
        if request_id in active_requests:
            current_request = active_requests[request_id]
            if current_request.status == RequestStatus.COMPLETED:
                logger.info(f"代码生成完成: {request_id}")
            elif current_request.status == RequestStatus.FAILED:
                logger.error(f"代码生成失败: {request_id} - {current_request.error_message}")
            else:
                logger.warning(f"代码生成状态异常: {request_id} - {current_request.status}")

    except CodeGenerationServiceError as e:
        logger.error(f"代码生成失败: {request_id} - {e}")
        if request_id in active_requests:
            active_requests[request_id].update_status(RequestStatus.FAILED, str(e))

    except Exception as e:
        logger.error(f"代码生成处理失败: {request_id} - {e}", exc_info=True)
        if request_id in active_requests:
            active_requests[request_id].update_status(RequestStatus.FAILED, f"系统错误: {str(e)}")

    finally:
        # Always decrement active request counter
        current_active_requests = max(0, current_active_requests - 1)
        logger.info(f"请求处理完成: {request_id} (活跃请求: {current_active_requests}/{MAX_CONCURRENT_REQUESTS})")


async def _enter_phase(request_id: UUID, phase: PhaseName, message: str, thinking_trace: str = None):
    """Enter a new processing phase and notify listeners."""
    try:
        new_phase = ProcessPhase(
            request_id=request_id,
            phase_name=phase,
            educational_message=message,
            thinking_trace=thinking_trace
        )

        # Validate phase transition
        phases = request_phases.get(request_id, [])
        if phases:
            last_phase = phases[-1]
            if not is_valid_phase_transition(last_phase.phase_name, phase):
                logger.warning(f"无效的阶段转换: {last_phase.phase_name} -> {phase}")

        # Add phase to history
        request_phases[request_id].append(new_phase)

        logger.info(f"进入阶段 {phase.value}: {request_id}")

    except Exception as e:
        logger.error(f"进入阶段失败: {e}")



"""
Generate API Endpoints

Handles code generation requests and streaming responses.
Implements the core /generate-code endpoint with Server-Sent Events.
"""

import asyncio
import logging
from datetime import datetime
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
from ..services.container import container

# Initialize service - try to use container first, fallback to direct instantiation
try:
    code_generation_service = container.code_generation_service
except:
    code_generation_service = CodeGenerationService()

# In-memory storage for active requests (in production, use Redis/database)
active_requests: Dict[UUID, CodeGenerationRequest] = {}
request_phases: Dict[UUID, List[ProcessPhase]] = {}

# Event queue for streaming events (in production, use Redis pub/sub)
streaming_events: Dict[UUID, List[Dict]] = {}
streaming_event_locks: Dict[UUID, asyncio.Lock] = {}

# Content buffer for "store & replay" streaming
content_buffers: Dict[UUID, Dict[str, str]] = {}
content_buffer_locks: Dict[UUID, asyncio.Lock] = {}


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
                # Clean up streaming events
                request_id = code_request.request_id
                if request_id in streaming_events:
                    del streaming_events[request_id]
                if request_id in streaming_event_locks:
                    del streaming_event_locks[request_id]
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

    # Check if request exists in memory or on disk
    request = active_requests.get(request_id)

    if not request:
        # Request not in memory - check if project exists on disk for offline replay
        logger.info(f"请求 {request_id} 不在内存中，尝试离线回放...")
        try:
            logger.info(f"Attempting to load project metadata for {request_id} (type: {type(request_id)})")
            project = await code_generation_service.project_service.load_project_metadata(request_id)
            logger.info(f"Project load result: {project is not None}")
            if project:
                logger.info(f"✓ 发现磁盘项目 {request_id}，项目名称: {project.project_name}")
                # Return StreamingResponse for offline replay
                from fastapi.responses import StreamingResponse
                import json

                async def format_sse(event_generator):
                    """Format events as SSE"""
                    async for event in event_generator:
                        if isinstance(event, dict):
                            event_type = event.get("event", "message")
                            data = event.get("data", "")
                            if isinstance(data, dict):
                                data = json.dumps(data, ensure_ascii=False)
                            yield f"event: {event_type}\ndata: {data}\n\n"
                        await asyncio.sleep(0.01)

                return StreamingResponse(
                    format_sse(_replay_content_stream(request_id)),
                    media_type="text/event-stream",
                    headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
                )
            else:
                logger.warning(f"磁盘项目 {request_id} 不存在")
                raise HTTPException(status_code=404, detail="请求不存在")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"加载磁盘项目失败 {request_id}: {e}")
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
            # For offline replay, request might be a mock object
            if hasattr(request, 'status') and hasattr(request.status, 'value'):
                request_status = request.status.value
            else:
                # Assume completed for offline replay
                request_status = 'COMPLETED'

            # If request is already completed or failed, send final status
            if request_status == 'COMPLETED':
                # For offline replay, simulate the full streaming experience
                logger.info(f"开始离线回放流式内容: {request_id}")
                async for event in _replay_content_stream(request_id):
                    yield event
                return
            elif request_status == 'FAILED':
                yield {
                    "event": "error",
                    "data": {
                        "message": request.error_message or "代码生成失败",
                        "can_retry": True
                    }
                }
                return

            # Implement "Store & Replay" streaming
            try:
                # Phase 1: Wait for generation to complete with fake thinking messages
                thinking_messages = [
                    "正在分析用户需求...",
                    "正在制定技术方案...",
                    "正在设计系统架构...",
                    "正在准备代码生成...",
                    "正在优化生成参数...",
                    "即将开始代码生成..."
                ]

                message_index = 0
                wait_start = asyncio.get_event_loop().time()

                while True:
                    current_time = asyncio.get_event_loop().time()

                    # Check if request is still active
                    if request_id not in active_requests:
                        yield {"event": "error", "data": "请求已完成或不存在"}
                        break

                    current_request = active_requests[request_id]

                    # Check if generation failed
                    if current_request.status == RequestStatus.FAILED:
                        yield {
                            "event": "error",
                            "data": {
                                "message": current_request.error_message or "代码生成失败",
                                "can_retry": True
                            }
                        }
                        break

                    # Check if generation completed
                    if current_request.status == RequestStatus.COMPLETED:
                        # Phase 2: Replay the stored content
                        await _replay_content_stream(request_id)
                        return

                    # Send thinking message every 1 second
                    if current_time - wait_start >= 1.0:
                        yield {
                            "event": "ai_thinking",
                            "data": {
                                "phase": "waiting",
                                "content": thinking_messages[message_index % len(thinking_messages)],
                                "timestamp": datetime.utcnow().isoformat() + 'Z',
                                "raw_type": "waiting_message"
                            }
                        }
                        message_index += 1
                        wait_start = current_time

                    await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"流式响应错误: {e}")
                yield {
                    "event": "error",
                    "data": f"流式响应错误: {str(e)}"
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
            # Initialize content buffer for this request
            content_buffers[request_id] = {}
            content_buffer_locks[request_id] = asyncio.Lock()

            # Run the generation workflow and collect all content
            phases_content = {}
            async for event in code_generation_service.generate_code_stream(request):
                # Collect content by phase
                if event.get("type") in ["text", "thinking"]:
                    phase = event.get("phase", "unknown")
                    content_type = event["type"]
                    content = event.get("content", "")

                    if phase not in phases_content:
                        phases_content[phase] = {"text": [], "thinking": []}

                    phases_content[phase][content_type].append(content)

            # Store the collected content in buffer
            async with content_buffer_locks[request_id]:
                for phase, contents in phases_content.items():
                    content_buffers[request_id][f"{phase}_text"] = "".join(contents["text"])
                    content_buffers[request_id][f"{phase}_thinking"] = "".join(contents["thinking"])

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

        # Clean up streaming events and content buffers
        if request_id in streaming_events:
            del streaming_events[request_id]
        if request_id in streaming_event_locks:
            del streaming_event_locks[request_id]
        if request_id in content_buffers:
            del content_buffers[request_id]
        if request_id in content_buffer_locks:
            del content_buffer_locks[request_id]

async def _replay_content_stream(request_id: UUID):
        """Replay stored content with controlled timing for 'hacker typing' effect."""
        try:
            # Get the completed project
            project = await code_generation_service.project_service.load_project_metadata(request_id)
            if not project:
                yield {"event": "error", "data": "项目数据不存在"}
                return

            # Get all project files
            files = await code_generation_service.project_service.get_project_files(request_id)
            if not files:
                yield {"event": "error", "data": "项目文件不存在"}
                return

            # For offline replay, simulate streaming from actual files
            # Find the main file and stream it as "implement" phase content
            main_file_content = ""
            if project.main_file in files:
                main_file_content = files[project.main_file]
            else:
                # Fallback to any Python file
                for filename, content in files.items():
                    if filename.endswith('.py'):
                        main_file_content = content
                        break

            # Phase order for replay
            phases = ["specify", "plan", "implement"]

            for phase in phases:
                # Send phase start event
                yield {
                    "event": "phase_update",
                    "data": {
                        "phase": phase,
                        "message": f"正在{phase}阶段..." if phase == "specify" else
                                 f"正在{phase}阶段..." if phase == "plan" else
                                 "正在生成代码...",
                        "status": "active"
                    }
                }

                if phase == "implement" and main_file_content:
                    # For implement phase, stream the actual code content
                    # Split content into reasonable chunks and stream with delays
                    lines = main_file_content.split('\n')
                    for i, line in enumerate(lines):
                        if line.strip():  # Skip empty lines for cleaner effect
                            # Stream line by line with typing effect
                            for char in line + '\n':
                                yield {
                                    "event": "ai_content",
                                    "data": {
                                        "phase": phase,
                                        "content": char,
                                        "timestamp": datetime.utcnow().isoformat() + 'Z',
                                        "raw_type": "generated_text"
                                    }
                                }
                                await asyncio.sleep(0.01)  # Hacker typing effect

                            # Small pause between lines
                            await asyncio.sleep(0.05)
                else:
                    # For specify/plan phases, show some generic thinking content
                    thinking_messages = [
                        "分析用户需求...",
                        "制定技术方案...",
                        "准备代码结构..."
                    ]

                    for msg in thinking_messages[:2 if phase != "implement" else 1]:
                        yield {
                            "event": "ai_thinking",
                            "data": {
                                "phase": phase,
                                "content": msg,
                                "timestamp": datetime.utcnow().isoformat() + 'Z',
                                "raw_type": "thinking_trace"
                            }
                        }
                        await asyncio.sleep(0.1)

                # Send phase complete event
                content_length = len(main_file_content) if phase == "implement" else 100
                yield {
                    "event": "phase_update",
                    "data": {
                        "phase": phase,
                        "status": "completed",
                        "result": content_length
                    }
                }

            # Send final completion event
            yield {
                "event": "completion",
                "data": {
                    "project_id": str(project.id),
                    "project_name": project.project_name,
                    "main_file": project.main_file,
                    "files_count": len(files),
                    "status": "success",
                    "message": "代码生成完成"
                }
            }

        except Exception as e:
            logger.error(f"内容回放失败: {e}")
            yield {
                "event": "error",
                "data": f"内容回放失败: {str(e)}"
            }

# This function should return a StreamingResponse
from fastapi.responses import StreamingResponse
import json

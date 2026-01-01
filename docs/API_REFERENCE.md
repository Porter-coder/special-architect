# AI Code Flow API Reference

Complete API documentation for the AI Code Flow backend service.

## Base URL
```
http://localhost:8000/api
```

## Authentication
Currently open access (no authentication required). Future versions will include API key authentication.

## Response Format

### Success Response
```json
{
  "success": true,
  "data": {},
  "message": "操作成功"
}
```

### Error Response
```json
{
  "success": false,
  "error": "ERROR_CODE",
  "message": "错误描述（中文）"
}
```

## Endpoints

## POST /generate-code

Start a code generation workflow from natural language input.

### Request

```http
POST /api/generate-code
Content-Type: application/json

{
  "user_input": "帮我写个贪吃蛇游戏",
  "application_type": "game"
}
```

### Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_input` | string | Yes | Natural language description of desired code |
| `application_type` | string | No | Type hint for the application (game, utility, web, etc.) |

### Response

**Initial Response:**
```json
{
  "request_id": "uuid-string",
  "message": "代码生成请求已开始处理",
  "status": "processing",
  "phases": ["specify", "plan", "implement"]
}
```

### Streaming Events

The generation process provides real-time updates via Server-Sent Events.

**Connection Event:**
```json
{
  "event": "connected",
  "data": "已连接到请求 uuid-string"
}
```

**Phase Update Events:**
```json
{
  "event": "phase_update",
  "data": {
    "phase": "specify",
    "message": "正在分析用户需求并制定规范...",
    "status": "active"
  }
}
```

**Content Chunk Events:**
```json
{
  "event": "content_chunk",
  "data": {
    "type": "markdown",
    "content": "# 项目规范\\n\\n游戏需要蛇、食物、移动控制...",
    "phase": "specify"
  }
}
```

**AI Thinking Events (Raw Content):**
```json
{
  "event": "ai_thinking",
  "data": {
    "phase": "plan",
    "content": "分析用户需求：贪吃蛇游戏需要...",
    "timestamp": "2026-01-01T12:00:00Z",
    "raw_type": "thinking_trace"
  }
}
```

**Completion Event:**
```json
{
  "event": "completion",
  "data": {
    "project_id": "uuid-string",
    "main_file": "main.py",
    "project_name": "snake_game_001",
    "status": "success",
    "message": "代码生成完成"
  }
}
```

**Error Event:**
```json
{
  "event": "error",
  "data": {
    "message": "AI 服务暂时不可用，请稍后重试",
    "can_retry": true
  }
}
```

### Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Invalid input parameters |
| `RATE_LIMIT_EXCEEDED` | Too many concurrent requests |
| `AI_SERVICE_ERROR` | AI service unavailable |
| `GENERATION_FAILED` | Code generation process failed |
| `TIMEOUT_ERROR` | Request timed out |

---

## GET /generate-code/{request_id}/stream

Stream real-time progress for an active code generation request.

### Request

```http
GET /api/generate-code/{request_id}/stream
Accept: text/event-stream
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `request_id` | UUID | Yes | Request identifier from generation start |

### Response

Server-Sent Events stream with progress updates (see above).

---

## GET /projects/{project_id}

Retrieve details for a completed code generation project.

### Request

```http
GET /api/projects/{project_id}
```

### Response

```json
{
  "id": "uuid-string",
  "project_name": "snake_game_001",
  "created_at": 1704067200,
  "file_structure": {
    "type": "directory",
    "name": "snake_game_001",
    "children": [
      {
        "type": "file",
        "name": "main.py",
        "size": 2048,
        "language": "python"
      },
      {
        "type": "file",
        "name": "README.md",
        "size": 512,
        "language": "markdown"
      }
    ]
  },
  "dependencies": ["pygame"],
  "total_files": 2,
  "total_size_bytes": 2560,
  "syntax_validated": true,
  "main_file": "main.py"
}
```

### Error Responses

**404 Not Found:**
```json
{
  "success": false,
  "error": "PROJECT_NOT_FOUND",
  "message": "项目不存在"
}
```

---

## GET /projects/{project_id}/download

Download the generated project files as a single file or archive.

### Request

```http
GET /api/projects/{project_id}/download
```

### Response

**Content-Type:** `text/plain` or `application/zip`
**Content-Disposition:** `attachment; filename="project_name_main.py"`

Returns the main file content directly, or a ZIP archive containing all project files.

### Error Responses

**404 Not Found:**
```json
{
  "success": false,
  "error": "PROJECT_NOT_FOUND",
  "message": "项目不存在"
}
```

**400 Bad Request:**
```json
{
  "success": false,
  "error": "VALIDATION_FAILED",
  "message": "项目尚未通过语法验证，无法下载"
}
```

---

## GET /health

System health check and status monitoring.

### Request

```http
GET /api/health
```

### Response

```json
{
  "status": "healthy",
  "concurrent_requests": 2,
  "max_concurrent": 5,
  "message": "服务运行正常",
  "services": {
    "ai_service": "healthy",
    "file_service": "healthy",
    "code_generation_service": "healthy"
  },
  "metrics": {
    "total_projects": 42,
    "uptime_seconds": 3600
  }
}
```

### Status Values

| Status | Description |
|--------|-------------|
| `healthy` | All systems operational |
| `degraded` | Some services have issues |
| `unhealthy` | System requires attention |

---

## POST /generate/{request_id}/retry

Retry a failed code generation request.

### Request

```http
POST /api/generate/{request_id}/retry
Content-Type: application/json
```

### Response

```json
{
  "request_id": "new-uuid-string",
  "message": "重试请求已开始处理",
  "status": "processing"
}
```

### Error Responses

**404 Not Found:**
```json
{
  "success": false,
  "error": "ORIGINAL_REQUEST_NOT_FOUND",
  "message": "原请求不存在"
}
```

**400 Bad Request:**
```json
{
  "success": false,
  "error": "REQUEST_NOT_FAILED",
  "message": "只有失败的请求才能重试"
}
```

---

## GET /projects

List all available projects (future endpoint).

### Request

```http
GET /api/projects
```

### Response

```json
{
  "projects": [
    {
      "id": "uuid-1",
      "project_name": "snake_game_001",
      "created_at": 1704067200,
      "main_file": "main.py",
      "language": "python"
    }
  ],
  "total": 1
}
```

---

## WebSocket Support (Future)

Real-time communication via WebSocket for enhanced streaming:

```javascript
const ws = new WebSocket('ws://localhost:8000/api/ws/generate/{request_id}');

// Listen for messages
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

## Rate Limiting

- **Concurrent Users**: Maximum 5 concurrent active requests
- **Per User Limit**: Maximum 2 concurrent requests per user
- **Timeout**: 60 seconds per AI API call
- **Circuit Breaker**: Automatic failure detection and recovery

## Error Handling

All endpoints include comprehensive error handling with Chinese error messages:

- **Network Errors**: Automatic retry with exponential backoff
- **Validation Errors**: Clear parameter validation messages
- **Service Errors**: Graceful degradation and fallback options
- **Timeout Errors**: Configurable timeouts with user feedback

## SDK Compatibility

The API is compatible with both MiniMax and OpenAI SDKs:

- **Automatic Fallback**: Switches between providers on failure
- **Unified Interface**: Same API regardless of backend provider
- **Configuration**: Runtime provider selection via config.json

## Data Formats

### Project Structure
```json
{
  "type": "directory|file",
  "name": "filename",
  "size": 1024,
  "language": "python",
  "children": [...]  // for directories
}
```

### Dependency Information
```json
{
  "name": "pygame",
  "version": "2.5.2",
  "required": true,
  "description": "Python game library"
}
```

### Phase Information
```json
{
  "name": "specify",
  "status": "completed|active|failed",
  "message": "正在分析用户需求...",
  "duration_seconds": 5.2,
  "content_chunks": 3
}
```

## Monitoring

### Health Metrics
- Service availability status
- Concurrent request counts
- AI provider connectivity
- File system availability

### Performance Metrics
- Request latency distribution
- Generation success rates
- Error type frequencies
- Resource utilization

### Logging
- TRACE level logging with JSONL output
- Automatic log rotation (100MB files)
- 30-day retention policy
- Real-time log streaming

## Development

### Local Development
```bash
# Start backend with reload
cd backend
.venv/Scripts/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation
Interactive API docs available at: `http://localhost:8000/docs`

### Testing
```bash
# Run API tests
cd backend
python -m pytest tests/ -v --tb=short

# Run E2E tests
cd frontend
npx playwright test
```

## Migration Guide

### From v0.x to v1.0
- New streaming endpoints replace polling
- Enhanced error messages in Chinese
- Improved concurrent user management
- Added project download functionality

## Support

For API support and questions:
- Check the troubleshooting guide in `docs/README.md`
- Review example implementations in `frontend/src/services/`
- Open issues for bugs and feature requests

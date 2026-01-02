# Streaming Protocol: Real-Time Workbench Rendering

**Version**: 1.0.0
**Date**: 2026-01-02
**Context**: Server-Sent Events (SSE) protocol for live project generation updates

## Overview

The streaming protocol enables real-time communication between the Python Factory (server) and the frontend Workbench (client) during project generation. This replaces the static "waiting screen" with a live, file-by-file project building experience.

## Connection Establishment

### Endpoint
```
GET /api/stream/{project_id}
```

### Headers
```
Accept: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```

### Response Headers
```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: Cache-Control
```

## Event Format

All events follow the Server-Sent Events specification with JSON data payloads.

### Basic Structure
```
event: {event_type}
data: {json_payload}

```

### Heartbeat Mechanism
```
event: heartbeat
data: {"timestamp": "2026-01-02T10:00:00Z"}

```

**Purpose**: Keep connection alive and detect broken connections
**Frequency**: Every 30 seconds during active generation
**Client Action**: Reset reconnection timer

## File Creation Events

### file_written
Emitted immediately after each file is written to disk.

```json
{
  "event": "file_written",
  "data": {
    "filename": "main.py",
    "path": "src/main.py",
    "type": "file",
    "status": "created",
    "size_bytes": 1024,
    "timestamp": "2026-01-02T10:00:05Z"
  }
}
```

**Fields**:
- `filename`: Just the filename (no path components)
- `path`: Full relative path from project root
- `type`: "file" or "directory"
- `status`: Always "created" for this event
- `size_bytes`: File size in bytes (omitted for directories)
- `timestamp`: ISO 8601 timestamp of file creation

### directory_created
Emitted when a directory is created.

```json
{
  "event": "file_written",
  "data": {
    "filename": "src",
    "path": "src",
    "type": "directory",
    "status": "created",
    "timestamp": "2026-01-02T10:00:03Z"
  }
}
```

## Generation Lifecycle Events

### generation_started
Emitted when generation begins (after UUID returned but before first file).

```json
{
  "event": "generation_started",
  "data": {
    "project_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2026-01-02T10:00:00Z"
  }
}
```

### generation_complete
Emitted when all files have been successfully written.

```json
{
  "event": "generation_complete",
  "data": {
    "project_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "total_files": 15,
    "total_size_bytes": 15360,
    "duration_seconds": 45.2,
    "timestamp": "2026-01-02T10:00:45Z"
  }
}
```

### generation_error
Emitted when generation fails with an error.

```json
{
  "event": "generation_error",
  "data": {
    "project_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "failed",
    "error": "磁盘空间不足",
    "error_code": "DISK_FULL",
    "timestamp": "2026-01-02T10:01:23Z"
  }
}
```

## Client-Side Handling

### Connection Management
1. **Initial Connection**: Connect immediately after redirect to `/workbench?mode=streaming`
2. **Reconnection**: Automatically reconnect on connection loss (up to 3 attempts with exponential backoff)
3. **Timeout**: Treat lack of heartbeat for 60 seconds as connection failure
4. **Cleanup**: Close connection when generation completes or fails

### Event Processing
1. **Parse JSON**: Extract data from each SSE event
2. **Update UI**: Add new nodes to file explorer tree
3. **State Management**: Track generation progress and completion
4. **Error Handling**: Display user-friendly messages for generation failures

### Performance Considerations
- **Event Frequency**: Expect 1-10 events per second during active generation
- **Memory Usage**: Process events immediately, don't buffer
- **UI Updates**: Batch DOM updates for smooth rendering
- **Connection Limits**: Single SSE connection per generation session

## Error Scenarios

### Network Interruptions
- **Detection**: Missing heartbeat events
- **Recovery**: Automatic reconnection with state recovery
- **Fallback**: Poll `/api/projects/{id}` for current state if reconnection fails

### Malformed Events
- **Detection**: JSON parsing errors
- **Recovery**: Log error and continue processing other events
- **User Impact**: Degraded experience but generation continues

### Server Errors
- **Detection**: HTTP error status codes
- **Recovery**: Display error message and stop generation
- **User Impact**: Clear failure indication with retry option

## Implementation Notes

### Python Factory (Server)
- Emit events synchronously after each successful file write
- Use atomic file operations (temp file + rename) before emitting events
- Include timestamps for debugging and client-side ordering
- Handle encoding errors gracefully

### Frontend Workbench (Client)
- Use native EventSource API for SSE connection
- Implement proper error boundaries for malformed event data
- Provide visual feedback for connection states (connecting, connected, reconnecting, failed)
- Handle browser tab/backgrounding gracefully

### Windows Compatibility
- Ensure proper UTF-8 encoding for filenames and paths
- Handle Windows path separators in event data
- Test with Windows firewall and antivirus software

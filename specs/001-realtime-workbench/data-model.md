# Data Model: Real-Time Workbench Rendering

**Date**: 2026-01-02
**Context**: Handover architecture with real-time file generation and serving

## Core Entities

### Project
Represents a generated codebase with physical file structure and real-time generation state.

**Fields**:
- `id`: string (UUID v4, primary identifier)
- `created_at`: datetime (generation start timestamp)
- `status`: enum ["generating", "completed", "failed"]
- `root_path`: Path (absolute path to project directory)
- `file_count`: integer (total files created, updated during generation)

**Relationships**:
- 1:N with FileNode (hierarchical structure)
- 1:1 with GenerationSession (current SSE streaming session)

**Validation Rules**:
- `id` must be valid UUID format
- `root_path` must exist and be writable
- `file_count` >= 0
- Status transitions: generating → completed/failed (no reversions)

**State Transitions**:
```
generating ──(all files written)──→ completed
    │
    └────(error during generation)──→ failed
```

### FileNode
Individual file or directory in the project structure.

**Fields**:
- `project_id`: string (foreign key to Project.id)
- `path`: string (relative path from project root, e.g., "src/main.py")
- `name`: string (filename or directory name)
- `type`: enum ["file", "directory"]
- `size_bytes`: integer (file size, null for directories)
- `created_at`: datetime (when file was written to disk)
- `content_type`: string (MIME type for files, null for directories)

**Relationships**:
- N:1 with Project
- Self-referential for directory hierarchy (parent_path)

**Validation Rules**:
- `path` must not contain ".." or absolute paths
- `name` must not contain path separators
- `size_bytes` >= 0 for files
- Paths must be unique within project

### SSE Event
Real-time notification emitted when files are created during generation.

**Fields**:
- `project_id`: string (associated project)
- `event_type`: string (always "file_written")
- `filename`: string (just the filename, no path)
- `path`: string (full relative path from project root)
- `type`: enum ["file", "directory"]
- `status`: enum ["created", "error"]
- `timestamp`: datetime (emission time)
- `size_bytes`: integer (file size if applicable)

**Validation Rules**:
- `event_type` must be "file_written"
- `path` must match existing file on disk
- `timestamp` must be current time (±5 seconds)

### Directory Tree (API Response)
Hierarchical JSON structure served by Librarian API.

**Structure**:
```json
{
  "project_id": "uuid-string",
  "root": {
    "type": "directory",
    "name": "root",
    "path": "",
    "children": [
      {
        "type": "file",
        "name": "main.py",
        "path": "main.py",
        "size_bytes": 1024,
        "created_at": "2026-01-02T10:00:00Z"
      },
      {
        "type": "directory",
        "name": "src",
        "path": "src",
        "children": [...]
      }
    ]
  },
  "total_files": 15,
  "generated_at": "2026-01-02T10:05:00Z"
}
```

**Validation Rules**:
- Root must be directory type
- All paths must be relative to project root
- No circular references in hierarchy
- File sizes must match actual disk files

## API Contracts

### Factory API (Python Backend)
**Endpoint**: `POST /api/generate`
- **Request**: `{"prompt": "string", "template": "optional string"}`
- **Response**: `{"project_id": "uuid-string", "status": "generating"}`
- **Streaming**: SSE events on separate connection

### Librarian API (Node.js Backend)
**Endpoint**: `GET /api/projects/{project_id}`
- **Response**: DirectoryTree JSON structure
- **Error Responses**: 404 (project not found), 500 (filesystem error)

### SSE Stream (Factory Backend)
**Endpoint**: `GET /api/stream/{project_id}`
- **Event Format**: Server-Sent Events with JSON data
- **Connection**: Single connection per generation session
- **Timeout**: 30-second heartbeat, auto-reconnect on client

## Data Flow

```
User Request ──→ Factory API ──→ Generate Project
                      │
                      ├─→ Write Files to Disk ──→ Emit SSE Events
                      │
                      └─→ Return Project UUID ──→ Frontend Redirect

Frontend ──→ Librarian API ──→ Read Directory Tree ──→ Render Workbench
    │
    └─→ SSE Stream ──→ Live File Updates ──→ Dynamic Tree Updates
```

## Performance Considerations

- **File Writing**: Atomic operations (temp file + rename)
- **Event Emission**: <100ms delay between disk write and SSE event
- **Tree Building**: Cached directory traversal with filesystem watching
- **Memory Usage**: Streaming responses, no full project buffering

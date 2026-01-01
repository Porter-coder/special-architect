# Data Model: AI Code Flow MVP

**Date**: 2026-01-01
**Feature**: AI Code Flow MVP (Foundation)
**Status**: Design Complete

## Overview

The AI Code Flow system manages the lifecycle of code generation requests from natural language input to executable code output. The data model supports three-phase processing (Specify → Plan → Implement) with real-time educational feedback and Windows-native compatibility.

## Core Entities

### 1. CodeGenerationRequest

Represents a user's natural language request for code generation and tracks its processing lifecycle.

**Fields**:
- `id` (string, UUID): Unique identifier for the request
- `user_input` (string, required): Natural language request text (e.g., "帮我写个贪吃蛇")
- `status` (enum): Request processing status
  - `pending`: Initial state, waiting to start
  - `processing`: Currently being processed by AI
  - `completed`: Successfully generated code
  - `failed`: Generation failed with error
  - `retrying`: User-initiated retry after failure
- `created_at` (datetime): Request creation timestamp
- `updated_at` (datetime): Last status update timestamp
- `error_message` (string, optional): Error details in Chinese if status is `failed`
- `retry_count` (integer, default 0): Number of retry attempts (max 3)

**Validation Rules**:
- `user_input`: 1-1000 characters, supports Chinese characters
- `status`: Must transition logically (pending → processing → completed/failed)
- `retry_count`: Cannot exceed 3, only incrementable when status is `failed`

**Relationships**:
- One-to-many with `ProcessPhase` (phases belong to request)
- One-to-one with `GeneratedProject` (final output)

### 2. ProcessPhase

Tracks the three-phase educational workflow with real-time status and messaging.

**Fields**:
- `id` (string, UUID): Unique identifier for the phase instance
- `request_id` (string, UUID, foreign key): Reference to parent CodeGenerationRequest
- `phase_type` (enum, required): Type of development phase
  - `specify`: Phase 1 - Natural language to technical specification
  - `plan`: Phase 2 - Specification to code structure design
  - `implement`: Phase 3 - Design to executable code
- `status` (enum): Phase execution status
  - `pending`: Not yet started
  - `active`: Currently executing
  - `completed`: Successfully finished
  - `failed`: Phase execution failed
- `educational_message` (string, required): Chinese educational message explaining the phase
- `started_at` (datetime, optional): Phase start timestamp
- `completed_at` (datetime, optional): Phase completion timestamp
- `sequence_order` (integer): Phase execution order (1, 2, 3)

**Validation Rules**:
- `educational_message`: Must be in Chinese, 10-200 characters
- `sequence_order`: Must be 1, 2, or 3 corresponding to phase_type
- Phases must execute in order: specify (1) → plan (2) → implement (3)
- Only one phase can be `active` per request at a time

**Relationships**:
- Many-to-one with `CodeGenerationRequest`

### 3. GeneratedProject

Represents the final output artifacts from a successful code generation request.

**Fields**:
- `id` (string, UUID): Unique identifier for the project
- `request_id` (string, UUID, foreign key): Reference to originating CodeGenerationRequest
- `project_name` (string, required): Auto-generated project name (e.g., "snake_game_20260101_123456")
- `main_file_path` (string, required): Path to main executable file (e.g., "projects/snake_game_20260101_123456/main.py")
- `file_structure` (JSON object): Complete project file tree structure
  ```json
  {
    "type": "directory",
    "name": "snake_game_20260101_123456",
    "children": [
      {
        "type": "file",
        "name": "main.py",
        "size": 1234,
        "language": "python"
      },
      {
        "type": "file",
        "name": "README.md",
        "size": 567,
        "language": "markdown"
      }
    ]
  }
  ```
- `dependencies` (array of strings): List of required dependencies (e.g., ["pygame"])
- `total_files` (integer): Total number of files in project
- `total_size_bytes` (integer): Total project size in bytes
- `syntax_validated` (boolean): Whether all code files passed AST validation
- `created_at` (datetime): Project creation timestamp

**Validation Rules**:
- `project_name`: Auto-generated, format: `{project_type}_{timestamp}_{random_suffix}`
- `main_file_path`: Must exist and be readable
- `syntax_validated`: Must be true for project to be downloadable
- `total_size_bytes`: Must not exceed 10MB per project

**Relationships**:
- One-to-one with `CodeGenerationRequest`

## Data Flow & State Transitions

### Request Lifecycle

```
User Input → CodeGenerationRequest (pending)
    ↓
ProcessPhase[specify] (pending → active → completed)
    ↓
ProcessPhase[plan] (pending → active → completed)
    ↓
ProcessPhase[implement] (pending → active → completed)
    ↓
GeneratedProject (created) → CodeGenerationRequest (completed)
```

### Error Handling States

```
Any Phase Failed → CodeGenerationRequest (failed)
    ↓ User Retry
CodeGenerationRequest (retrying) → Reset phases → Retry flow
    ↓ Max retries exceeded
CodeGenerationRequest (failed) [permanent]
```

## Storage Strategy

### Primary Storage: Filesystem
- **Generated Projects**: Stored in `projects/` directory with UUID-based subdirectories
- **Session History**: Transient (not persisted between sessions)
- **Configuration**: `backend/config.json` (mandatory)

### State Management: Frontend-Centric
- **Business State**: Managed in frontend (localStorage/Zustand)
- **Backend**: Stateless, restart-safe at any time
- **Persistence**: Only generated code files persist indefinitely

## Validation & Business Rules

### Code Generation Rules
1. **Syntax Validation**: All generated Python code must pass `ast.parse()` validation
2. **Windows Compatibility**: Generated code must run natively on Windows without modifications
3. **Dependency Management**: Only approved dependencies (pygame for MVP)
4. **File Size Limits**: Individual files <1MB, total project <10MB

### Process Rules
1. **Phase Ordering**: Strict sequential execution (Specify → Plan → Implement)
2. **Educational Feedback**: Each phase must display appropriate Chinese educational message
3. **Timeout Controls**: 60s API timeout, 120s frontend circuit breaker
4. **Retry Logic**: Maximum 3 retries per failed request

### Environment Rules
1. **Virtual Environment**: Backend execution must verify `sys.prefix` points to `backend\.venv`
2. **Configuration**: Mandatory `backend/config.json` validation at startup
3. **Logging**: Comprehensive TRACE logging to `logs/system_trace.jsonl`
4. **Encoding**: All file operations use UTF-8 encoding explicitly

## API Integration Points

### MiniMax AI Engine
- **Request Format**: Natural language input with reasoning_split parameter
- **Response Format**: Streaming chunks with thinking/content separation
- **Error Handling**: Circuit breaker pattern with automatic retry
- **Validation**: AST parsing of extracted code blocks

### Frontend-Backend Communication
- **Real-time Updates**: Server-Sent Events (SSE) for phase progress
- **State Synchronization**: Frontend manages business state, backend processes requests
- **Error Propagation**: Chinese error messages with retry capabilities

## Scalability Considerations

### Concurrent Users (1-5)
- **Resource Isolation**: Each request processes independently
- **Memory Management**: Transient state, no persistent sessions
- **File System**: UUID-based project isolation prevents conflicts

### Performance Targets
- **Generation Time**: <5 minutes per request
- **Startup Time**: Zero errors across 100 consecutive runs
- **Syntax Success Rate**: 95% of generated code runs without errors

## Migration & Evolution

### Version Compatibility
- **OpenAI SDK Migration**: Maintains backward compatibility with existing interfaces
- **Streaming Format**: Preserves identical chunk format for frontend compatibility
- **Error Messages**: Continues to return Chinese error messages

### Future Extensions
- **Multiple Languages**: Framework supports extending beyond Python
- **Additional Dependencies**: Approval process for new libraries
- **Advanced Features**: Plugin architecture for specialized generators

## Implementation Notes

### Key Technical Decisions
1. **UUID-based Identification**: Ensures uniqueness across concurrent requests
2. **Filesystem Storage**: Simple, reliable persistence for generated code
3. **Stateless Backend**: Enables horizontal scaling and restart reliability
4. **AST Validation**: Guarantees syntactic correctness of generated code
5. **Phase-based Processing**: Provides educational transparency and error isolation

### Monitoring & Observability
1. **Request Metrics**: Response times, success rates, error frequencies
2. **Phase Tracking**: Completion times and failure points per phase
3. **Resource Usage**: Memory, CPU, and API usage patterns
4. **User Behavior**: Retry patterns and request types
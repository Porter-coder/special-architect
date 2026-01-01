# Data Model: AI Code Flow MVP

**Date**: 2025-12-31
**Feature**: AI Code Flow MVP (Foundation)

## Overview

The AI Code Flow MVP uses a minimal data model focused on code generation requests and results. All data is stored locally with no database requirements, maintaining stateless backend design per constitution requirements.

## Core Entities

### CodeGenerationRequest

Represents a user-initiated code generation request with progress tracking.

**Fields**:
- `request_id` (string, UUID): Unique identifier for the request
- `user_input` (string): Original natural language request from user
- `status` (enum): Current request status
  - `pending`: Request received, not yet started
  - `processing`: Currently being processed by AI
  - `completed`: Successfully generated code
  - `failed`: Generation failed with error
- `created_at` (datetime): Request creation timestamp
- `updated_at` (datetime): Last status update timestamp
- `error_message` (string, optional): Error details if status is 'failed'

**Validation Rules**:
- `request_id` must be valid UUID format
- `user_input` cannot be empty, max 1000 characters
- `created_at` and `updated_at` auto-managed by system

**Relationships**:
- One-to-one with GeneratedProject
- One-to-many with ProcessPhase (ordered by timestamp)

### ProcessPhase

Tracks the three-phase progress of the software engineering process.

**Fields**:
- `phase_id` (string, UUID): Unique identifier for phase record
- `request_id` (string, UUID): Reference to parent request
- `phase_name` (enum): Current development phase
  - `specify`: Analyzing requirements and defining boundaries
  - `plan`: Designing technical solution and selecting technologies
  - `implement`: Writing and generating code
- `educational_message` (string): Chinese message explaining current phase
- `timestamp` (datetime): When this phase was entered
- `thinking_trace` (string, optional): AI thinking content for current phase

**Validation Rules**:
- `phase_name` must be one of the three defined phases
- `educational_message` must be in Chinese
- Phases must occur in order: specify → plan → implement

**Relationships**:
- Many-to-one with CodeGenerationRequest

### GeneratedProject

Represents the output of a successful code generation with dual-track artifacts.

**Fields**:
- `project_id` (string, UUID): Unique identifier for generated project
- `request_id` (string, UUID): Reference to originating request
- `project_name` (string): Auto-generated project name (e.g., "snake_game_20251231")
- `main_file_path` (string): Relative path to main executable file (e.g., "main.py")
- `spec_file_path` (string): Relative path to specification document (e.g., "spec.md")
- `plan_file_path` (string): Relative path to planning document (e.g., "plan.md")
- `project_structure` (JSON): Directory structure with file paths and types
- `dependencies` (JSON): List of required packages/libraries identified
- `created_at` (datetime): Project generation completion timestamp

**Validation Rules**:
- `project_name` must be filesystem-safe (no special characters)
- `main_file_path` must exist in generated files and pass AST validation
- `spec_file_path` and `plan_file_path` must exist for documentation artifacts
- `project_structure` must be valid JSON with file listings

**Relationships**:
- One-to-one with CodeGenerationRequest
- Contains raw phase content (Phase 1: spec.md, Phase 2: plan.md) and cleaned Phase 3 content (main.py)

## Data Flow & State Transitions

### Request Lifecycle

```
User Input → CodeGenerationRequest (pending)
    ↓
ProcessPhase (specify) → AI Analysis
    ↓
ProcessPhase (plan) → Technology Selection
    ↓
ProcessPhase (implement) → Code Generation
    ↓
GeneratedProject (completed) + File Persistence
```

### Phase Transition Rules

1. **Specify → Plan**: Only after AI has analyzed user input and identified requirements
2. **Plan → Implement**: Only after technology stack and approach are determined
3. **Implement → Complete**: Only after all code files are generated and validated

### Error Handling States

- Any phase can transition to `failed` status with error details
- Failed requests retain all phase information for debugging
- Users can retry failed requests (creates new request cycle)

## Storage Strategy

**Local File System (Constitution Compliant)**:
- No database required (stateless backend design)
- Generated projects persist in `projects/` directory indefinitely
- Request metadata stored in JSON files alongside projects
- Session data is transient (not persisted)

**File Structure**:
```
projects/
├── {request_id}/
│   ├── metadata.json          # CodeGenerationRequest + ProcessPhases
│   ├── spec.md                # Phase 1: Raw specification content
│   ├── plan.md                # Phase 2: Raw planning content
│   ├── main.py                # Phase 3: Clean, AST-validated Python code
│   ├── requirements.txt       # Dependencies (auto-generated)
│   └── README.md              # Usage instructions (auto-generated)
└── index.json                # Global project registry
```

**Data Serialization**:
- All metadata stored as UTF-8 encoded JSON
- File paths use forward slashes (/) for consistency
- Timestamps in ISO 8601 format
- Chinese strings properly encoded

## Validation & Constraints

### Business Rules

1. **Concurrency Limit**: Maximum 5 simultaneous active requests (constitution requirement)
2. **Request Isolation**: Each request generates independent project directory
3. **File Safety**: All generated file names are sanitized for Windows compatibility
4. **Encoding Enforcement**: All file operations use UTF-8 encoding (constitution requirement)

### Technical Constraints

1. **Stateless Backend**: No server-side session persistence
2. **Local Storage Only**: No cloud storage or databases
3. **Windows Compatibility**: All paths and operations work on Windows
4. **Resource Limits**: Memory and CPU usage appropriate for 1-5 concurrent users

## Migration & Evolution

**Current Scope (MVP)**: File-based storage with JSON metadata
**Future Considerations**: Could evolve to SQLite for complex queries, but not required for MVP
**Backward Compatibility**: JSON format designed for easy migration if needed

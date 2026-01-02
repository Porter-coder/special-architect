# Feature Specification: Real-Time Workbench Rendering (Next.js Monolith)

**Feature Branch**: `001-realtime-workbench`
**Created**: 2026-01-02
**Status**: Draft
**Input**: User description: "WE ARE ON WINDOWS ENV

**ARCHITECTURE**: Next.js Monolith (Constitution v2.0.0)
**LLM PROVIDER**: MiniMax (Node.js integration)

001-PROJECT DEFINITION: NEXT.JS MONOLITH ARCHITECTURE (Constitution v2.0.0)

1. Status Quo (The Foundation):

Frontend UI: The "Silent Luxury" UI assets have been manually migrated from ONLY-REFERENCE to frontend/src. Do NOT regenerate UI visual components.

Next.js Core: The monolith application handles all generation, parsing, and file serving through API routes.

2. The Architecture (Next.js Monolith):

A. The Monolith (Next.js API Routes):

Role: Sole Generator & File Manager (unified service).

Runtime: Node.js v20 only (Constitution v2.0.0 compliance).

Input: User prompt via POST /api/generate.

Action:
- Calls MiniMax API with streaming
- Regex parser extracts code blocks from AI response
- Writes files to PROJECTS_ROOT/{uuid}/ directory
- Emits SSE events for real-time UI updates
- Serves file tree via GET /api/projects/{id}

Output: Streaming SSE events + project UUID.

Constraint: Single Next.js application, no separate services.

3. The Workflow:

User clicks "Generate" → POST /api/generate (Next.js API route).

MiniMax streaming → Regex parser → File writing → SSE events.

UI redirects to /workbench?mode=streaming.

SSE connection → Real-time file tree updates.

Action:

Implement complete generation pipeline within Next.js monolith.

ARCHITECTURAL UPGRADE: REAL-TIME WORKBENCH RENDERING

User Goal:

Replace the static "Waiting Screen" with a Live Workbench Experience. The user watches the project being built file-by-file.

Revised Workflow:

Immediate Transition:

User clicks "Generate".

UI immediately redirects to /workbench?mode=streaming.

Workbench initializes with an Empty File Tree and a "Connecting to Factory..." status.

Protocol Upgrade (Granular SSE):

Update streaming_protocol.md.

New Event: file_written

<JSON>

event: file_written

data: {

  "filename": "main.py",

  "path": "root/main.py",

  "type": "file",

  "status": "created"

}

Python Logic: As the generator writes a file to disk, it MUST immediately yield this SSE event.

Frontend "Live" Logic:

Socket Listener: The Workbench connects to the SSE stream.

Dynamic Tree: On file_written, append the new node to the File Explorer UI.

Auto-Preview: (Optional) Automatically fetch the content of the newly created file via Node API (/api/file-content) to animate the code editor.

Impact:

This maintains the Handover Architecture (Python writes, Node reads), but tightens the loop. Node reads specific files as soon as Python confirms they are written.

Action:

Update the streaming_protocol.md and frontend_logic to support this "Live Rendering" capability."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Live Project Generation Experience (Priority: P1)

As a developer, I want to watch my project being built file-by-file in real-time so that I can see progress and feel engaged during the generation process.

**Why this priority**: This is the core user experience improvement that transforms a static waiting screen into an interactive, engaging experience. It provides immediate feedback and reduces perceived wait time.

**Independent Test**: Can be fully tested by initiating project generation and observing files appear in the workbench file explorer in real-time, delivering immediate visual feedback and engagement during generation.

**Acceptance Scenarios**:

1. **Given** a user clicks "Generate" on an empty workbench, **When** the system starts generating a project, **Then** the workbench immediately shows a file tree that populates with files as they are created
2. **Given** a project is being generated, **When** the Next.js API route creates a new file, **Then** the file appears in the workbench file explorer within 1 second
3. **Given** a user is watching project generation, **When** all files are created, **Then** the complete project structure is visible and the user can immediately browse and edit any file

---

### User Story 2 - Monolith File Management (Priority: P2)

As a system architect, I want the Next.js monolith to handle both generation and file serving so that all operations are unified within a single, maintainable application.

**Why this priority**: This establishes a clean, unified architecture where all file operations are handled consistently within the Next.js monolith, eliminating service coordination complexity.

**Independent Test**: Can be fully tested by generating a project through the monolith and verifying that it correctly serves the complete file tree via unified API endpoints.

**Acceptance Scenarios**:

1. **Given** the monolith has generated a project with UUID "abc123", **When** the frontend requests `/api/projects/abc123`, **Then** the monolith returns the complete directory structure as JSON
2. **Given** a project exists on disk, **When** the monolith parses the directory tree, **Then** it correctly identifies files, folders, and their hierarchical relationships
3. **Given** the monolith uses consistent PROJECTS_ROOT configuration, **When** generation and serving operations reference the same UUID, **Then** they access the identical physical folder location

---

### User Story 3 - Stateless Generation (Priority: P3)

As a system architect, I want the Next.js API route to only write files and return UUIDs so that generation remains stateless and independently scalable.

**Why this priority**: This enforces the architectural principle that generation is stateless, enabling horizontal scaling and preventing resource coupling.

**Independent Test**: Can be fully tested by verifying that the API route only returns UUIDs after generation and maintains no persistent state.

**Acceptance Scenarios**:

1. **Given** a generation request is made, **When** the API route completes writing files, **Then** it returns only the project UUID without any file content or metadata
2. **Given** a project has been generated, **When** checking the API route state, **Then** no persistent project knowledge exists
3. **Given** the API route generates a project, **When** it writes each file to disk, **Then** it immediately emits a file_written SSE event for that specific file

---

### Edge Cases

- What happens when the SSE connection is lost during generation?
- How does the system handle Windows path separators in cross-platform file operations?
- What happens when the Python factory fails to write a file?
- How does the system recover if the initial file tree request fails?
- What happens when multiple users generate projects simultaneously?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Next.js API route MUST emit a `file_written` SSE event immediately after writing each file to disk
- **FR-002**: Next.js monolith MUST parse physical directory structures into JSON format for API responses
- **FR-003**: Frontend workbench MUST establish SSE connection and update file tree in real-time as files are created
- **FR-004**: Next.js monolith MUST use consistent PROJECTS_ROOT path configuration
- **FR-005**: System MUST handle Windows file system paths and separators correctly in cross-platform operations
- **FR-006**: Frontend MUST redirect to `/workbench?mode=streaming` immediately upon generation start
- **FR-007**: Workbench MUST initialize with empty file tree and "Connecting to Generator..." status
- **FR-008**: SSE `file_written` event data MUST include filename, path, type, and status fields
- **FR-009**: Next.js monolith MUST provide `/api/projects/[id]` endpoint returning complete directory tree
- **FR-010**: Next.js API route MUST return only UUID after generation completion with no additional query capabilities

### Key Entities *(include if feature involves data)*

- **Project**: Represents a generated codebase with unique UUID identifier and physical file structure in Next.js monolith
- **File Node**: Individual file or directory with name, path, and type attributes parsed by regex engine
- **SSE Event**: Real-time notification containing file creation metadata (filename, path, type, status) from API route
- **Directory Tree**: Hierarchical JSON representation of project structure served by Next.js monolith

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users see each generated file appear in the workbench within 1 second of creation
- **SC-002**: Project generation completes with no performance degradation compared to static waiting screen
- **SC-003**: 95% of users report improved experience when watching live project generation vs static waiting
- **SC-004**: Python Factory maintains zero query API endpoints while Node.js Librarian serves complete file trees
- **SC-005**: System correctly handles Windows file paths and directory structures in all operations
- **SC-006**: SSE connection establishes successfully for 99% of generation sessions on Windows environment

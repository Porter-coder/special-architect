# Tasks: Real-Time Workbench Rendering (Next.js Migration)

**Input**: Design documents from `/specs/001-realtime-workbench/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Jest/vitest tests included for API routes and core business logic per Constitution v2.0.0

**Migration Strategy**: Python → Next.js Monolith with Regex-based parsing (no AST library)
**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Dependencies & Implementation Strategy

**Migration Phases**:
1. **Phase 1**: Intelligence Extraction & Adaptation (Python prompts → Next.js)
2. **Phase 2**: Streaming API Implementation (Minimax integration)
3. **Phase 3**: Frontend Connection (UI updates)

**User Story Completion Order** (based on priorities from spec.md):
1. **US1 (P1)**: Live Project Generation Experience - Core MVP functionality
2. **US2 (P2)**: Librarian File Serving - Architectural foundation
3. **US3 (P3)**: Factory Write-Only Constraint - Advanced optimization

**MVP Scope**: User Story 1 (US1) provides complete real-time workbench experience

**Implementation Strategy**:
- Start with Phase 1 migration tasks for clean slate
- Regex-based parsing replaces Python AST validation
- Explicit requirements.txt generation in prompts
- All AI calls through Node.js MiniMax API (no Python dependencies)

## Phase 1: Intelligence Extraction & Adaptation

**Purpose**: Extract Python intelligence and adapt for Next.js monolith (Regex-based parsing)

- [X] T001 Extract and port generation prompts from Python backend (frontend/src/lib/prompts.ts)
- [X] T002 Upgrade system prompt to explicitly require requirements.txt generation
- [X] T003 Create regex-based parser library (frontend/src/lib/parser.ts)
- [X] T004 Implement markdown code block detection (```python ... ```)
- [X] T005 Add regex validation for Python file structure (def, class, import statements)
- [X] T006 Create file extraction logic from AI responses
- [X] T007 Test parser against sample Python code blocks (jest unit tests)
- [X] T008 Delete backend/ folder to remove Python confusion

## Phase 2: The Streaming API (Minimax)

**Purpose**: Implement Minimax streaming integration and Next.js API generation endpoint

- [X] T009 Create Minimax API client with streaming support (frontend/src/lib/minimax.ts)
- [X] T010 Implement fetch-based streaming to Minimax API
- [X] T011 Create Next.js API route for generation (frontend/src/pages/api/generate.ts)
- [X] T012 Implement three-phase generation workflow (SPECIFY → PLAN → IMPLEMENT)
- [X] T013 Integrate parser with Minimax streaming responses
- [X] T014 Add real-time file writing to disk (fs.promises)
- [X] T015 Implement SSE event emission for file_written events
- [X] T016 Add project directory creation and atomic file operations
- [X] T017 Generate requirements.txt automatically from parsed dependencies
- [X] T018 Create automatic documentation files (README.md, spec.md, plan.md)
- [X] T019 Add comprehensive error handling with Chinese messages
- [X] T020 Implement Windows path compatibility (path.join/resolve)
- [X] T021 Test streaming generation workflow (jest integration test)

## Phase 3: Frontend Connection

**Purpose**: Update UI components to connect to new Next.js streaming API

- [X] T022 Create main generation page with prompt input (frontend/src/app/page.tsx)
- [X] T023 Implement workbench page with streaming mode (frontend/src/app/workbench/page.tsx)
- [X] T024 Create WorkbenchScene component with real-time file tree (frontend/src/components/WorkbenchScene.tsx)
- [X] T025 Create FileExplorer component with live updates (frontend/src/components/FileExplorer.tsx)
- [X] T026 Implement SSEConnector for stream management (frontend/src/components/SSEConnector.tsx)
- [X] T027 Add connection status indicators and error handling
- [X] T028 Implement automatic redirect to workbench on generation start
- [X] T029 Add loading states and progress feedback
- [ ] T030 Test complete streaming workflow (E2E with Playwright)
- [ ] T031 Add Windows-specific UI testing scenarios

## Phase 4: Librarian File Serving (Architectural Separation)

**Purpose**: Implement read-only file serving capabilities for clean separation

- [ ] T032 Create file serving API endpoint (frontend/src/pages/api/projects/[id].ts)
- [ ] T033 Implement directory tree parsing and JSON serving
- [ ] T034 Add individual file content serving endpoint
- [ ] T035 Create file system traversal utilities
- [ ] T036 Implement project metadata and file listing
- [ ] T037 Add Windows path handling for all file operations
- [ ] T038 Test file serving endpoints (jest unit tests)
- [ ] T039 Verify PROJECTS_ROOT configuration sharing

## Final Phase: Polish & Production Readiness

**Purpose**: Quality assurance, performance optimization, and production deployment

- [ ] T040 Configure production environment variables and Minimax credentials
- [ ] T041 Implement comprehensive SSE reconnection with heartbeat monitoring
- [ ] T042 Add timeout handling for long-running generations (60s+)
- [ ] T043 Optimize memory usage in streaming responses
- [ ] T044 Add comprehensive error handling with Chinese user messages
- [ ] T045 Implement proper cleanup of failed generations and temp files
- [ ] T046 Add logging and debugging capabilities throughout pipeline
- [ ] T047 Create health check endpoints for monitoring
- [ ] T048 Add Windows-specific testing and validation
- [ ] T049 Create deployment configuration and Docker setup
- [ ] T050 Documentation updates and user guide completion
- [ ] T051 Performance testing and optimization
- [ ] T052 Final E2E testing with Playwright

## Parallel Execution Opportunities

**High Parallelization Potential**:
- **Phase 1**: Prompt extraction and parser creation can run in parallel
- **Phase 3**: UI components (FileExplorer, WorkbenchScene, SSEConnector) can be developed in parallel
- **Phase 4**: File serving endpoints can be implemented independently
- **Testing**: Unit tests for parser, Minimax client, and UI components run in parallel

**Dependencies**:
- Phase 1 must complete before Phase 2 (provides prompts and parser)
- Phase 2 must complete before Phase 3 (provides streaming API)
- Phase 3 and Phase 4 can execute in parallel after Phase 2
- Polish phase requires all previous phases to be complete

## Task Summary

- **Total Tasks**: 52
- **Phase 1**: Intelligence Extraction & Adaptation (8 tasks, T001-T008)
- **Phase 2**: Streaming API Implementation (13 tasks, T009-T021)
- **Phase 3**: Frontend Connection (10 tasks, T022-T031)
- **Phase 4**: Librarian File Serving (8 tasks, T032-T039)
- **Final Phase**: Polish & Production (13 tasks, T040-T052)

**MVP Delivery**: Complete Phases 1-3 for full real-time workbench experience
**Migration Scope**: Complete all phases for Python → Next.js monolith transition
**Parallel Opportunities**: 10+ tasks for concurrent development across phases

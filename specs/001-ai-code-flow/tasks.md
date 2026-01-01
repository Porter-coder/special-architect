# Tasks: AI Code Flow MVP (Foundation)

**Input**: Design documents from `/specs/001-ai-code-flow/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Integration tests included as requested in FR-017 (OpenAI SDK migration tests) and SC-008 (SDK comparison tests)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- **Generated projects**: `projects/` directory
- **Configuration**: `backend/config.json`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for web application

- [ ] T001 Create backend directory structure with FastAPI setup in backend/src/
- [ ] T002 Create frontend directory structure with React/Next.js setup in frontend/src/
- [ ] T003 Initialize Python virtual environment in backend/.venv
- [ ] T004 Create projects/ directory for generated code storage
- [ ] T005 Create logs/ directory for system trace logging
- [ ] T006 [P] Setup backend requirements.txt with FastAPI, httpx, openai, pygame dependencies
- [ ] T007 [P] Setup frontend package.json with React, Next.js dependencies

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 Create backend/src/main.py with FastAPI application setup
- [ ] T009 Create backend/config.json with MiniMax/OpenAI SDK configuration
- [ ] T010 Implement virtual environment validation in backend/src/main.py (FR-025)
- [ ] T011 Implement configuration loading and validation in backend/src/config.py (FR-026)
- [ ] T012 Implement comprehensive TRACE logging system in backend/src/logging_config.py (FR-029)
- [ ] T013 Create backend/src/api/ directory structure for API endpoints
- [ ] T014 Create frontend/src/ directory structure with basic React components
- [ ] T015 Implement circuit breaker pattern for external API calls in backend/src/circuit_breaker.py (FR-028)
- [ ] T016 Create data models from data-model.md in backend/src/models/
- [ ] T017 Implement timeout handling (60s) for all network requests (FR-027)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Generate Snake Game (Priority: P1) 🎯 MVP

**Goal**: Enable users to request "帮我写个贪吃蛇" and receive working Snake game code with transparent three-phase process

**Independent Test**: Enter "帮我写个贪吃蛇" in web interface, verify all three phases (Specify/Plan/Implement) complete with educational messages, and download working main.py file

### Integration Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T018 [P] [US1] OpenAI SDK migration test comparing outputs in backend/tests/test_sdk_migration.py (FR-017, SC-008)
- [ ] T019 [P] [US1] E2E test for Snake game generation workflow in tests/test_snake_game_e2e.py

### Implementation for User Story 1

- [ ] T020 [US1] Implement CodeGenerationRequest model in backend/src/models/code_generation_request.py
- [ ] T021 [US1] Implement ProcessPhase model in backend/src/models/process_phase.py
- [ ] T022 [US1] Implement GeneratedProject model in backend/src/models/generated_project.py
- [ ] T023 [US1] Create AI service with MiniMax SDK integration in backend/src/services/ai_service.py
- [ ] T024 [US1] Implement code generation service in backend/src/services/code_generation_service.py
- [ ] T025 [US1] Implement Markdown parsing and AST validation in backend/src/services/code_parser.py (FR-020, FR-021)
- [ ] T026 [US1] Create POST /generate-code endpoint with SSE streaming in backend/src/api/generate.py (FR-015, FR-022)
- [ ] T027 [US1] Implement three-phase educational workflow (Specify → Plan → Implement) in backend/src/services/phase_manager.py
- [ ] T028 [US1] Add project file management and storage in backend/src/services/project_service.py
- [ ] T029 [US1] Create basic frontend interface with input form in frontend/src/components/CodeGenerator.tsx
- [ ] T030 [US1] Implement SSE streaming display in frontend with phase messages in frontend/src/components/StreamingDisplay.tsx
- [ ] T031 [US1] Add download functionality for generated projects in frontend/src/components/ProjectDownloader.tsx

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently - users can generate working Snake game code

---

## Phase 4: User Story 2 - Process Transparency Education (Priority: P1)

**Goal**: Show real-time educational feedback during all phases with raw AI content including Markdown explanations

**Independent Test**: Submit any code generation request and observe raw AI output in SSE stream with educational messages for each phase

### Implementation for User Story 2

- [X] T032 [US2] Enhance phase manager with detailed educational messages in Chinese in backend/src/services/phase_manager.py
- [X] T033 [US2] Implement raw AI content streaming in SSE responses (FR-022) in backend/src/api/generate.py
- [X] T034 [US2] Add Markdown documentation generation for spec.md and plan.md outputs (FR-023) in backend/src/services/documentation_service.py
- [X] T035 [US2] Implement content cleaning and validation only at Phase 3 completion (FR-024) in backend/src/services/content_processor.py
- [X] T036 [US2] Create educational message display component in frontend/src/components/EducationalDisplay.tsx
- [X] T037 [US2] Add raw content viewer for AI explanations and thinking in frontend/src/components/RawContentViewer.tsx
- [X] T038 [US2] Implement phase progress visualization in frontend/src/components/PhaseProgress.tsx

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - educational transparency is fully functional

---

## Phase 5: User Story 3 - Generic Code Generation (Priority: P2)

**Goal**: Support various application types beyond Snake game with dynamic technology selection

**Independent Test**: Submit requests for web app, data processing script, or other application types and verify appropriate code generation

### Implementation for User Story 3

- [ ] T039 [US3] Implement dynamic technology detection and library selection in backend/src/services/technology_detector.py
- [ ] T040 [US3] Add support for multiple application types (web, data processing, games, utilities) in backend/src/services/code_generation_service.py
- [ ] T041 [US3] Create extensible prompt templates for different application categories in backend/src/services/prompt_templates.py
- [ ] T042 [US3] Implement dependency analysis and requirements generation in backend/src/services/dependency_analyzer.py
- [ ] T043 [US3] Add Windows compatibility validation for generated code (FR-006) in backend/src/services/compatibility_checker.py
- [ ] T044 [US3] Enhance frontend to show available application types and technology options in frontend/src/components/ApplicationTypeSelector.tsx

**Checkpoint**: All user stories should now be independently functional - system supports generic code generation

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final system hardening

- [ ] T045 [P] Implement GET /health endpoint in backend/src/api/health.py
- [ ] T046 [P] Implement GET /projects/{id} endpoint in backend/src/api/projects.py
- [ ] T047 [P] Implement GET /projects/{id}/download endpoint in backend/src/api/projects.py
- [ ] T048 [P] Add comprehensive error handling with Chinese messages throughout backend (FR-014)
- [ ] T049 [P] Implement development mode with mock responses in backend/src/services/mock_service.py (FR-018)
- [ ] T050 [P] Add concurrent user management (1-5 users) in backend/src/services/concurrency_manager.py (FR-009, FR-010)
- [ ] T051 [P] Implement retry logic for failed requests in frontend/src/services/retry_service.ts (FR-011)
- [ ] T052 [P] Add log rotation and cleanup policies in backend/src/logging_config.py (FR-029)
- [ ] T053 [P] Create comprehensive integration tests for SDK migration verification in backend/tests/test_integration.py
- [ ] T054 [P] Add Playwright E2E tests for complete user workflows in tests/test_e2e.py
- [ ] T055 [P] Implement final validation per quickstart.md checklist in tests/test_validation.py
- [ ] T056 [P] Documentation updates and README completion in docs/

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P1 → P2)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories - MVP CORE
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - May use US1 infrastructure but independently testable
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - May use US1/US2 infrastructure but independently testable

### Within Each User Story

- Integration tests (if included) MUST be written and FAIL before implementation
- Models before services before endpoints
- Core generation before educational features before generic support
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "OpenAI SDK migration test comparing outputs in backend/tests/test_sdk_migration.py"
Task: "E2E test for Snake game generation workflow in tests/test_snake_game_e2e.py"

# Launch all models for User Story 1 together:
Task: "Implement CodeGenerationRequest model in backend/src/models/code_generation_request.py"
Task: "Implement ProcessPhase model in backend/src/models/process_phase.py"
Task: "Implement GeneratedProject model in backend/src/models/generated_project.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently - Snake game generation works
5. Deploy/demo if ready - Core MVP achieved!

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP: Snake game generation!)
3. Add User Story 2 → Test independently → Deploy/Demo (Educational transparency!)
4. Add User Story 3 → Test independently → Deploy/Demo (Generic code generation!)
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (1-2 days)
2. Once Foundational is done:
   - Developer A: User Story 1 (Snake game generation)
   - Developer B: User Story 2 (Educational transparency)
   - Developer C: User Story 3 (Generic code generation)
3. Stories complete and integrate independently

---

## Success Criteria Mapping

- **SC-001** (<5 min generation): Covered in US1 implementation
- **SC-002** (95% syntax correct): Covered in code validation (FR-021)
- **SC-003** (understand phases): Covered in US2 educational messages
- **SC-004** (zero startup errors): Covered in foundational setup
- **SC-006-S-008** (OpenAI migration): Covered in integration tests
- **SC-009** (AST validation): Covered in code parser implementation
- **SC-010-S-011** (educational content, artifacts): Covered in US2 and documentation

## Notes

- [P] tasks = different files, no dependencies - can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Integration tests written FIRST and verified to FAIL before implementation
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- MVP achieved with just User Story 1 completion
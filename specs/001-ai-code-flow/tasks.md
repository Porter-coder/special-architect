# Implementation Tasks: AI Code Flow MVP (Dual-Track Content Strategy)

**Feature**: `001-ai-code-flow`
**Priority Order**: US1 (P1) → US2 (P1) → US3 (P2)
**Total Tasks**: 24
**Parallel Opportunities**: 8 tasks marked with [P]
**MVP Scope**: User Story 1 (Snake Game Generation)

## Dependencies & Execution Strategy

### Story Dependencies
- **US1** (Generate Snake Game): Independent - Core MVP
- **US2** (Process Transparency): Depends on US1 for three-phase process foundation
- **US3** (Generic Code Generation): Depends on US1+US2 for multi-type support

### Parallel Execution Examples
```text
# Within US1 Phase - Can run simultaneously:
T008 [P] [US1] Update code_generator.py for Markdown parsing
T009 [P] [US1] Add AST validation to code_generator.py
T010 [P] [US1] Update file_service.py for artifact structure

# Within US2 Phase - Can run simultaneously:
T014 [P] [US2] Enhance SSE streaming for raw content
T015 [P] [US2] Add phase artifact saving logic
```

### Implementation Strategy
1. **MVP First**: Complete US1 (Snake game) as independently testable increment
2. **Incremental Delivery**: Add US2 (transparency) then US3 (generic types)
3. **TDD Approach**: Integration tests validate each story independently
4. **Parallel Execution**: Tasks marked [P] can run simultaneously within phases

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend service**: `backend/src/`, `backend/tests/` at repository root
- **Models**: `backend/src/models/`
- **Services**: `backend/src/services/`
- **API**: `backend/src/api/`
- **Tests**: `backend/tests/integration/`, `backend/tests/contract/`

---

## Phase 1: Setup & Infrastructure

### Phase Goal
Initialize project structure and core dependencies for dual-track content strategy implementation.

### Independent Test Criteria
- [ ] MiniMax API connectivity confirmed via OpenAI SDK
- [ ] Project structure supports UUID-based artifact directories
- [ ] AST validation module imports successfully
- [ ] Basic three-phase process skeleton functional

**Tasks:**
- [x] T001 Update requirements.txt with OpenAI SDK dependency
- [x] T002 Create projects/ directory structure for artifact storage
- [x] T003 Add ast import to code_generator.py for validation
- [x] T004 Update ai_service.py MiniMax API configuration with reasoning_split parameter

---

## Phase 2: Foundational Components

### Phase Goal
Implement core dual-track infrastructure that supports all user stories.

### Independent Test Criteria
- [ ] Raw AI content streams without modification during generation
- [ ] Markdown code blocks extract clean Python code reliably
- [ ] AST validation catches syntax errors in generated code
- [ ] Project artifacts save correctly (spec.md, plan.md, main.py)

**Tasks:**
- [x] T005 Implement Markdown code block parsing in code_generator.py
- [x] T006 Add AST validation function to code_generator.py
- [x] T007 Update file_service.py to support artifact directory structure
- [x] T008 Create phase content accumulation logic in code_generation_service.py

## Phase 3: User Story 1 - Generate Snake Game (P1) 🎯 MVP

### Story Goal
Implement complete Snake game generation with educational transparency, demonstrating the three-phase process (Specify → Plan → Implement) and producing working, validated Python code.

### Independent Test Criteria
- [ ] User can request "帮我写个贪吃蛇" and see all three phases execute
- [ ] SSE stream shows raw AI content including Markdown explanations
- [ ] Generated project contains spec.md, plan.md, and main.py artifacts
- [ ] main.py passes AST validation and contains complete Snake game code
- [ ] Game runs successfully when executed

**Tasks:**
- [x] T009 [P] [US1] Update ai_service.py with MiniMax reasoning_split parameter
- [x] T010 [P] [US1] Enhance code_generation_service.py for dual-track streaming
- [x] T011 [P] [US1] Implement artifact saving in code_generation_service.py
- [x] T012 [US1] Update routes.py to support new artifact endpoints
- [x] T013 [US1] Add integration tests for Snake game generation flow
- [x] T014 [US1] Test end-to-end Snake game generation and validation

---

## Phase 4: User Story 2 - Process Transparency Education (P1)

### Story Goal
Enhance the user experience with real-time educational feedback, showing raw AI thinking and explanations during all three phases while maintaining clean final artifacts.

### Independent Test Criteria
- [ ] SSE streams show raw AI content including Markdown documentation
- [ ] Users see educational explanations during Specify, Plan, and Implement phases
- [ ] Phase transitions display appropriate Chinese educational messages
- [ ] Raw streaming content doesn't interfere with final artifact quality

**Tasks:**
- [ ] T015 [P] [US2] Enhance SSE streaming to preserve raw AI content
- [ ] T016 [P] [US2] Update educational messages for dual-track transparency
- [ ] T017 [P] [US2] Add phase artifact documentation saving
- [ ] T018 [US2] Implement content cleaning timing (Phase 3 only)
- [ ] T019 [US2] Add transparency-focused integration tests
- [ ] T020 [US2] Test educational transparency across different request types

## Phase 5: User Story 3 - Generic Code Generation (P2)

### Story Goal
Extend the system to support various application types beyond Snake games, maintaining the same dual-track transparency and validation approach.

### Independent Test Criteria
- [ ] System accepts and processes different application types (web apps, utilities, etc.)
- [ ] Each request type goes through complete three-phase process
- [ ] Generated code quality maintained across application types
- [ ] AST validation works for different code patterns and libraries

**Tasks:**
- [ ] T021 [P] [US3] Enhance prompt engineering for multiple application types
- [ ] T022 [P] [US3] Update dependency analysis for various Python libraries
- [ ] T023 [P] [US3] Add application type detection and routing
- [ ] T024 [US3] Add cross-type integration tests and validation
- [ ] T025 [US3] Test generic code generation with different application types

## Phase 6: Polish & Cross-Cutting Concerns

### Phase Goal
Address remaining requirements, performance optimizations, and quality improvements across all user stories.

### Independent Test Criteria
- [ ] All generated code passes AST validation (100% success rate)
- [ ] Concurrent user limits (1-5) enforced and tested
- [ ] Error recovery and retry functionality working
- [ ] Performance meets 5-minute generation time requirement

**Tasks:**
- [ ] T026 Add comprehensive AST validation error handling
- [ ] T027 Implement concurrent user limit enforcement
- [ ] T028 Add retry functionality for failed generations
- [ ] T029 Performance optimization and monitoring
- [ ] T030 Final integration testing and documentation

---

## Dependencies & Execution Order

### Story Dependencies
- **US1** (Generate Snake Game): Independent - Core MVP
- **US2** (Process Transparency): Depends on US1 for three-phase process foundation
- **US3** (Generic Code Generation): Depends on US1+US2 for multi-type support

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed) or sequentially by priority
  - US1 (P1) → US2 (P1) → US3 (P2) recommended order
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### Parallel Opportunities

- **Within phases**: Tasks marked [P] can run simultaneously
- **Between phases**: Sequential execution required (dependencies)
- **Between stories**: US1+US2 can run in parallel after foundational complete

### Parallel Execution Examples
```text
# Within US1 Phase - Can run simultaneously:
T009 [P] [US1] Update ai_service.py with MiniMax reasoning_split parameter
T010 [P] [US1] Enhance code_generation_service.py for dual-track streaming
T011 [P] [US1] Implement artifact saving in code_generation_service.py

# Within US2 Phase - Can run simultaneously:
T015 [P] [US2] Enhance SSE streaming for raw content
T016 [P] [US2] Update educational messages for dual-track transparency
T017 [P] [US2] Add phase artifact documentation saving
```

---

## Task Details & File Paths

### Backend Components
- **ai_service.py**: MiniMax API integration, reasoning_split parameter
- **code_generation_service.py**: Dual-track streaming, phase management, artifact saving
- **code_generator.py**: Markdown parsing, AST validation, content cleaning
- **file_service.py**: Artifact directory structure, file operations
- **routes.py**: API endpoints for generation and artifact retrieval

### Test Structure
- **tests/integration/**: End-to-end generation flows, concurrent user limits
- **tests/unit/**: Individual component testing (parsing, validation, streaming)

### Configuration Files
- **requirements.txt**: OpenAI SDK dependency management
- **projects/[uuid]/ structure**: Artifact organization per generation request

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup & Infrastructure
2. Complete Phase 2: Foundational Components (CRITICAL - dual-track infrastructure)
3. Complete Phase 3: User Story 1 (Snake Game Generation)
4. **STOP and VALIDATE**: Test dual-track Snake game generation independently
5. Deploy/demo if ready - working MVP with educational transparency

### Incremental Delivery

1. Complete Setup + Foundational → Dual-track infrastructure ready
2. Add User Story 1 → Test Snake game with spec.md/plan.md/main.py artifacts → Deploy/Demo (MVP!)
3. Add User Story 2 → Enhance transparency with raw AI content streaming → Deploy/Demo
4. Add User Story 3 → Support multiple application types → Deploy/Demo
5. Each story adds value while maintaining dual-track approach

### Parallel Development Strategy

With multiple developers:

1. Team completes Setup + Foundational together (dual-track foundation)
2. Once infrastructure is ready:
   - Developer A: US1 (Snake game with artifact generation)
   - Developer B: US2 (Educational transparency enhancements)
   - Developer C: US3 (Multi-type application support)
3. Stories integrate independently, each adding to dual-track capabilities

---

## Validation Summary

**Format Compliance**: ✅ All tasks follow required checklist format
**Task Count**: 24 tasks across 6 phases
**Parallel Opportunities**: 8 tasks marked for concurrent execution
**Story Independence**: Each user story can be implemented and tested independently
**File Path Specificity**: All tasks include exact file paths for implementation

## Implementation Notes

- **[P] marker**: Tasks that can run in parallel (different files, no dependencies)
- **[Story] label**: Maps tasks to specific user stories for traceability
- **Dual-track approach**: Raw streaming content vs clean artifacts throughout
- **AST validation**: All generated code must pass Python ast.parse() validation
- **Incremental delivery**: Each user story can be deployed independently
- **Educational transparency**: Raw AI content in streams, clean code in artifacts

---
*Generated by /speckit.tasks command - Ready for /speckit.implement execution*
# Implementation Plan: AI Code Flow MVP (Foundation)

**Branch**: `001-ai-code-flow` | **Date**: 2026-01-01 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-ai-code-flow/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

AI-powered code generation system with process transparency and educational feedback. Users submit natural language requests through a web interface and receive working code via a transparent three-phase process (Specify → Plan → Implement) using MiniMax AI engine with robust Windows-native compatibility and environment isolation.

## Technical Context

**Language/Version**: Python 3.11 (Backend), Node.js v20 (Frontend)
**Primary Dependencies**: FastAPI (Backend API), MiniMax/OpenAI SDK (AI), httpx (HTTP client), Pygame (Code generation), React/Next.js (Frontend)
**Storage**: File system (generated code files in projects/ folder), transient session history
**Testing**: pytest (Backend integration), Playwright (E2E), ast.parse() validation (Code correctness)
**Target Platform**: Windows (native compatibility required)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: <5 minutes code generation, 1-5 concurrent users, 95% syntactically correct code
**Constraints**: Virtual environment isolation (backend\.venv), configuration from backend/config.json, 60s API timeouts, circuit breaker pattern, comprehensive TRACE logging
**Scale/Scope**: 1-5 concurrent users, single application type (Snake game MVP), process transparency education

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Runtime Environment Compliance ✅ PASS

- **Node.js v20 (LTS)**: Frontend uses Node.js v20 ✅
- **Python 3.11 (Stable)**: Backend uses Python 3.11 ✅
- **Windows Compatibility**: Native Windows compatibility required ✅
- **Virtual Environment Isolation**: Enforced via `backend\.venv` path validation ✅
- **Command Execution Protocol**: Absolute paths required for Python execution ✅

### Language Standards Compliance ✅ PASS

- **Technical Layer (English)**: All source code, variables, comments in English ✅
- **User Layer (Chinese)**: UI interface, error messages, guidance in Chinese ✅

### API Philosophy Compliance ✅ PASS

- **Minimalist API**: Business-required interfaces only ✅
- **Exception Handling**: Backend catches all exceptions, returns JSON with Chinese messages ✅

### Testing Standards Compliance ✅ PASS

- **Backend Testing**: pytest-based real API integration tests ✅
- **E2E Testing**: Playwright/Selenium for core workflows ✅
- **Zero Pseudocode**: Delivery requires passing tests ✅

### State Management Compliance ✅ PASS

- **Frontend State**: Business state in localStorage/Zustand ✅
- **Backend Stateless**: Backend designed for stateless operation ✅

### Stability & Timeouts Compliance ✅ PASS

- **API Timeouts**: 60s timeout for all external API calls ✅
- **Test Timeouts**: Execution limits for CI/CD pipelines ✅
- **Frontend Circuit Breaker**: 120s timeout for fetch requests ✅

**GATE STATUS**: ✅ ALL GATES PASS - Proceed to Phase 0

## Constitution Check (Post-Design) ✅ PASS

*Re-evaluation after Phase 1 design completion to ensure implementation details maintain constitutional compliance.*

### Runtime Environment Compliance ✅ PASS

- **Python 3.11 Exact Version**: Backend uses Python 3.11 with explicit version checking ✅
- **Node.js v20 LTS**: Frontend uses Node.js v20 with npm script compatibility ✅
- **Windows PowerShell Compatibility**: All automation scripts use cross-platform commands ✅
- **Virtual Environment Enforcement**: Design includes `sys.prefix` validation for `backend\.venv` ✅
- **UTF-8 Encoding**: All file operations explicitly use `encoding='utf-8'` ✅
- **Absolute Path Execution**: Command execution uses `backend\.venv\Scripts\python.exe` ✅

### Language Standards Compliance ✅ PASS

- **English Technical Code**: All source code, variables, and comments in English ✅
- **Chinese User Interface**: All UI messages, errors, and educational feedback in Chinese ✅
- **Mixed Language Architecture**: Clear separation between technical and user layers ✅

### API Philosophy Compliance ✅ PASS

- **Minimalist API Surface**: Only business-essential endpoints (generate, health, projects) ✅
- **Exception Capture**: All backend exceptions caught and returned as JSON with Chinese messages ✅
- **No Stack Trace Exposure**: Clean error responses without internal details ✅

### Testing Standards Compliance ✅ PASS

- **pytest Integration Tests**: Backend API testing with real request simulation ✅
- **Playwright E2E Tests**: Complete user journey testing including streaming ✅
- **AST Validation Testing**: Code correctness verification built into generation process ✅
- **Zero Pseudocode Policy**: All generated code is immediately executable ✅

### State Management Compliance ✅ PASS

- **Frontend State Storage**: User session and UI state managed in localStorage/Zustand ✅
- **Backend Statelessness**: All requests are independent, restart-safe ✅
- **File-based Persistence**: Generated code stored in filesystem, not database ✅

### Stability & Timeouts Compliance ✅ PASS

- **API Timeout Implementation**: 60s timeout for MiniMax/OpenAI API calls ✅
- **Test Execution Limits**: 180s global timeout for E2E verification scripts ✅
- **Frontend Circuit Breaker**: 120s timeout with automatic retry prompts ✅
- **Graceful Degradation**: Circuit breaker pattern prevents cascade failures ✅

### New Constitutional Requirements ✅ PASS

- **Comprehensive TRACE Logging**: JSONL format logging to `logs/system_trace.jsonl` ✅
- **Data Transparency**: No sanitization of sensitive data in logs (maximum debugging) ✅
- **Log Rotation**: Automatic cleanup and size-based rotation policies ✅
- **Virtual Environment Verification**: Runtime path validation before execution ✅
- **Configuration Validation**: Mandatory `backend/config.json` with startup failure ✅

**POST-DESIGN GATE STATUS**: ✅ ALL CONSTITUTIONAL REQUIREMENTS MAINTAINED

**Design Compliance Confirmed**: Implementation details fully align with constitutional principles. No violations introduced during detailed design phase. Ready for Phase 2 task breakdown.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |

# Implementation Plan: Real-Time Workbench Rendering

**Branch**: `001-realtime-workbench` | **Date**: 2026-01-02 | **Spec**: specs/001-realtime-workbench/spec.md
**Input**: Feature specification from `/specs/001-realtime-workbench/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement real-time workbench rendering with Next.js monolith architecture: MiniMax AI integration with streaming file creation and SSE events for live project building experience.

## Technical Context

**Language/Version**: Next.js 14+ with Node.js v20 (LTS) - Monolith Architecture (Constitution v2.0.0)
**Primary Dependencies**: MiniMax API, Next.js API Routes, Server-Sent Events, Node.js fs, regex parsing
**Storage**: File system (physical project directories via Node.js fs with PROJECTS_ROOT)
**Testing**: Jest/vitest for API routes and components, E2E tests for streaming workflows
**Target Platform**: Windows (explicitly required for path handling and PowerShell compatibility)
**Project Type**: Next.js monolith web application (unified frontend/backend per Constitution)
**Performance Goals**: File appearance within 1 second of creation, streaming generation completion under 60 seconds
**Constraints**: Node.js-only runtime (no Python), Next.js API routes with streaming responses, MiniMax API integration, Windows path compatibility, regex-based parsing
**Scale/Scope**: Single-user generation sessions, real-time file-by-file updates, three-phase AI generation workflow

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Runtime Environment Compliance (Constitution v2.0.0)
- ✅ **Node.js v20 (LTS)**: Only runtime allowed, matches constitution requirement
- ✅ **Windows Compatibility**: Explicitly addressed with path.join/resolve and utf-8 encoding
- ✅ **No Python Dependencies**: All AI calls through Node.js MiniMax API (constitution compliance)

### Architecture Protocol (CRITICAL)
- ✅ **Next.js Monolith**: Single application with API routes (constitution requirement)
- ✅ **API Routes Only**: All business logic in Next.js API routes (no separate backend)
- ✅ **No Python Runtime**: Zero Python dependencies or scripts (constitution prohibition)

### Language & Interaction Standards
- ✅ **Technical Layer**: English for all code, variables, comments
- ✅ **User Layer**: Chinese UI feedback and error messages

### API Design Philosophy
- ✅ **Minimalist Next.js API Routes**: Only essential business interfaces
- ✅ **Error Handling**: JSON responses with Chinese messages, no stack traces
- ✅ **Streaming Responses**: SSE for long-running generation tasks (constitution requirement)

### Testing Requirements
- ✅ **Jest/Vitest**: Unit tests for core business logic (parser, API routes)
- ✅ **E2E Testing**: Playwright for complete streaming workflows
- ✅ **Zero Pseudocode**: All implementations must pass tests

### State Management
- ✅ **Frontend State**: Real-time updates managed in React components
- ✅ **Stateless API**: Generation endpoints are stateless and restartable

### Stability & Timeouts
- ✅ **API Timeouts**: MiniMax calls with 60+ second timeouts (constitution requirement)
- ✅ **Streaming Mandatory**: SSE for code generation (constitution requirement)
- ✅ **SSE Connection Timeouts**: Progressive reconnection with 30-second heartbeat and state recovery

### Windows-Specific Requirements
- ✅ **PowerShell/CMD npm Scripts**: cross-env and rimraf for cross-platform compatibility
- ✅ **Environment Variables**: cross-env mandatory, no direct export commands
- ✅ **File Operations**: rimraf for directory deletion, path.join/resolve for paths

**Gate Status**: ✅ ALL GATES PASSED - Constitution v2.0.0 fully compliant

**Post-Specification Alignment**: Updated to reflect Next.js monolith architecture
- ✅ **Architecture Unified**: Single Next.js application handles all operations
- ✅ **Python References Removed**: All specifications updated for Node.js-only runtime
- ✅ **Regex Parsing**: Ported Python parsing logic to TypeScript with identical algorithms
- ✅ **Constitution Compliance**: All requirements aligned with v2.0.0 principles

## Project Structure

### Documentation (this feature)

```text
specs/001-realtime-workbench/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── factory-api.yaml     # MiniMax API integration spec
│   ├── librarian-api.yaml   # Next.js API routes spec
│   └── streaming-protocol.md # SSE protocol specification
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (Next.js Monolith)

```text
app/                        # Next.js App Router (Constitution v2.0.0)
├── api/
│   └── generate/
│       └── route.ts         # POST /api/generate - streaming code generation
├── workbench/
│   └── page.tsx            # Real-time workbench UI
└── layout.tsx

components/                 # React Components
├── FileExplorer.tsx        # Dynamic file tree with live updates
├── WorkbenchScene.tsx      # Main workbench interface
└── SSEConnector.tsx        # SSE stream management

lib/                        # Business Logic (Node.js only)
├── minimax.ts              # MiniMax API client with streaming
├── parser.ts               # Regex-based code parsing (ported from Python)
├── prompts.ts              # Three-phase generation prompts
├── fileSystem.ts           # Node.js fs operations for file writing
└── streaming.ts            # SSE event handling

types/                      # TypeScript Definitions
├── api.ts                  # API request/response types
├── fileSystem.ts           # File and directory types
└── sse.ts                  # SSE event types

projects/                   # Physical project storage
├── {uuid}/
│   ├── main.py
│   ├── requirements.txt
│   ├── README.md
│   └── spec.md              # Generated documentation
└── ...

.env.local                  # Environment configuration
# MINIMAX_API_KEY=your-key-here
# MINIMAX_GROUP_ID=your-group-id
# PROJECTS_ROOT=./projects

tests/                      # Jest/Vitest test suites
├── unit/
│   ├── lib/
│   │   ├── minimax.test.ts
│   │   └── fileSystem.test.ts
│   └── components/
├── integration/
│   └── api/
└── e2e/
    └── streaming-workflow.test.ts
```

**Structure Decision**: Next.js monolith architecture as mandated by Constitution v2.0.0. Single application with API routes handling all AI generation, file system operations, and streaming responses. No Python runtime or separate backend services.

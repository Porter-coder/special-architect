# Implementation Plan: AI Code Flow MVP (Foundation)

**Branch**: `001-ai-code-flow` | **Date**: 2025-12-31 | **Spec**: specs/001-ai-code-flow/spec.md
**Input**: Feature specification from `/specs/001-ai-code-flow/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement dual-track content strategy for AI code generation: preserve raw AI content in streaming responses for educational transparency while saving clean, validated artifacts (spec.md, plan.md, main.py) to disk. Integrate MiniMax API with reasoning_split parameter for clean content separation and AST validation for code quality assurance.

## Technical Context

**Language/Version**: Python 3.11 (locked by Constitution Article I)
**Primary Dependencies**: OpenAI SDK >=1.0.0, MiniMax API (via OpenAI compatibility), FastAPI (existing), ast (built-in)
**AI Integration**: MiniMax API with reasoning_split parameter for clean content/thinking separation
**Content Strategy**: Dual-track - raw streaming content (educational) vs clean artifacts (production)
**Storage**: File system with structured project artifacts (spec.md, plan.md, main.py per project)
**Validation**: AST parsing for Python code syntactic correctness
**Testing**: pytest (Constitution Article IV requirement) plus AST validation tests
**Target Platform**: Windows (Constitution Article I Windows compatibility)
**Project Type**: Backend web service (existing FastAPI structure)
**Performance Goals**: Support 1-5 concurrent users for code generation requests
**Constraints**: Windows-native compatibility, UTF-8 encoding, stateless backend design, no global package pollution
**Scale/Scope**: 1-5 concurrent users, three-phase code generation with streaming responses and artifact persistence

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Design Check (Phase 0)
- ✅ **Python 3.11**: Using locked Python 3.11 version
- ✅ **Windows Compatibility**: Explicit Windows-native requirements (pathlib.Path, UTF-8 encoding)
- ✅ **Environment Isolation**: Using requirements.txt for dependency management, no global packages
- ✅ **Technical Layer**: Python source code and comments in English
- ✅ **User Layer**: Error messages and feedback in Chinese (preserved from existing implementation)
- ✅ **Business Interfaces**: Maintaining existing API endpoints and functionality
- ✅ **Exception Handling**: Preserving Chinese error messages and JSON response format
- ✅ **pytest Integration Tests**: Existing test structure maintained
- ✅ **Zero Pseudocode**: Real MiniMax API integration with reasoning_split parameter
- ✅ **Stateless Backend**: Existing design maintained (no server-side session state)
- ✅ **AST Validation**: Using Python's built-in ast module for syntactic validation
- ✅ **Dual-Track Content**: Raw streaming content for education, clean artifacts for production

### Post-Design Check (Phase 1)
- ✅ **MiniMax API Compatibility**: API works with Python 3.11 and Windows environment via OpenAI SDK
- ✅ **Dependency Management**: OpenAI SDK added to requirements.txt (no global installations)
- ✅ **Error Message Preservation**: Chinese error messages maintained in exception mapping
- ✅ **Streaming Interface**: Raw content preserved in SSE for educational transparency
- ✅ **UTF-8 Encoding**: All file operations continue to use UTF-8 encoding
- ✅ **API Contract Stability**: OpenAPI specification unchanged, ensuring frontend compatibility
- ✅ **AST Validation**: Python ast module integration for code syntactic validation
- ✅ **Artifact Structure**: spec.md, plan.md, main.py saved per project with appropriate content types
- ✅ **Content Cleaning**: Markdown parsing and code extraction only at Phase 3 completion

**GATE STATUS**: ✅ PASS - All constitution requirements satisfied post-design

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

```text
backend/
├── requirements.txt                    # Python dependencies (updated with OpenAI SDK)
├── src/
│   ├── api/
│   │   └── routes.py                   # FastAPI routes (existing)
│   ├── models/
│   │   ├── generated_project.py        # Project structure models (existing)
│   │   └── process_phase.py            # Phase enumeration (existing)
│   └── services/
│       ├── ai_service.py               # TARGET: MiniMax API integration with reasoning_split
│       ├── code_generation_service.py  # TARGET: Dual-track content streaming and artifact saving
│       └── code_generator.py           # TARGET: Markdown parsing, AST validation, artifact creation
├── projects/                           # Generated project artifacts
│   └── [uuid]/
│       ├── spec.md                     # Phase 1: Raw specification content
│       ├── plan.md                     # Phase 2: Raw planning content
│       ├── main.py                     # Phase 3: Clean, validated Python code
│       ├── requirements.txt            # Auto-generated dependencies
│       ├── README.md                   # Auto-generated project documentation
│       └── metadata.json               # Project metadata and structure info
└── tests/
    ├── integration/                    # API integration tests
    └── unit/                          # Unit tests for services, AST validation
```

**Structure Decision**: Backend Python service with dual-track content handling. Phase 1-2 content saved raw for documentation, Phase 3 content cleaned and AST-validated. Project artifacts stored in structured directories with UUID-based naming.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |

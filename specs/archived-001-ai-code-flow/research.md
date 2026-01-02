# Research & Technical Decisions: AI Code Flow MVP

**Date**: 2026-01-01
**Feature**: AI Code Flow MVP (Foundation)
**Status**: Complete - All technical decisions resolved

## Research Scope

The AI Code Flow MVP requires research across multiple technical domains to ensure Windows-native compatibility, robust AI integration, and educational process transparency. This research focused on:

1. **AI Engine Integration**: MiniMax API with OpenAI SDK compatibility
2. **Streaming Architecture**: Progressive status feedback with educational waiting messages during asynchronous code generation
3. **Content Processing**: Markdown parsing and AST validation for code extraction
4. **Windows Environment**: Native compatibility and isolation requirements
5. **Process Transparency**: Educational workflow visualization

## Key Findings & Decisions

### Decision: MiniMax AI Engine with OpenAI SDK
**Rationale**: Feature requirement FR-013 mandates OpenAI SDK migration while FR-004 requires MiniMax engine
**Alternatives Considered**:
- Direct MiniMax SDK: Rejected due to maintenance overhead and compatibility issues
- Anthropic SDK: Rejected due to migration requirement and cost considerations
**Chosen**: OpenAI SDK with MiniMax compatibility mode for standardized interface

### Decision: Three-Phase Educational Workflow
**Rationale**: Core MVP philosophy emphasizes process transparency over magic
**Implementation**:
- Phase 1 (Specify): Natural language → technical specification conversion
- Phase 2 (Plan): Specification → code structure design
- Phase 3 (Implement): Design → executable code generation
**Educational Value**: Users see rigorous software engineering process through progressive status updates and result replay

**Note**: Due to Python asyncio blocking on heavy CPU tasks, a store-and-replay pattern was adopted for stability instead of real-time streaming.

### Decision: SSE Streaming with Raw Content Preservation
**Rationale**: FR-022 requires raw AI content preservation for process transparency
**Implementation**:
- Server-Sent Events (SSE) for progressive status feedback and content replay
- Preserve Markdown documentation and AI explanations
- Content cleaning occurs only at Phase 3 completion (FR-024)
**Benefits**: Rich educational content visible during generation process

### Decision: Robust Markdown Code Extraction
**Rationale**: FR-020 requires robust parsing to extract clean Python code from AI responses
**Implementation**:
- Multi-pattern regex matching for code blocks
- Fallback parsing strategies
- AST validation (FR-021) ensures syntactic correctness
**Validation**: 100% of generated code must pass `ast.parse()` (SC-009)

### Decision: Virtual Environment Isolation Enforcement
**Rationale**: Constitution Article I requires strict environment isolation
**Implementation**:
- Runtime verification: `sys.prefix` must point to `backend\.venv`
- Immediate termination with "VENV_NOT_ACTIVATED" error if violated
- Windows-compatible absolute paths: `backend\.venv\Scripts\python.exe`
**Security**: Prevents execution outside controlled environment

### Decision: Configuration-Driven Architecture
**Rationale**: FR-026 requires `backend/config.json` with fail-fast behavior
**Implementation**:
- Mandatory configuration file validation at startup
- Clear error messages for missing/invalid configuration
- Environment-specific settings (development vs production)
**Benefits**: Predictable deployment and debugging

### Decision: Circuit Breaker Pattern for API Resilience
**Rationale**: FR-028 requires circuit breaker for external API calls
**Implementation**:
- Automatic retry logic for temporary failures
- Fail-fast during extended outages
- Prevents cascade failures in concurrent user scenarios
**Limits**: Supports 1-5 concurrent users (FR-009) without additional rate limiting

### Decision: Comprehensive TRACE Logging
**Rationale**: FR-029 requires maximum debugging visibility for environment issues
**Implementation**:
- JSONL format to `logs/system_trace.jsonl`
- TRACE level always enabled (including third-party libraries)
- No data sanitization for maximum transparency
- Log rotation and cleanup policies
**Trade-offs**: High overhead but critical for Windows environment debugging

### Decision: Windows-Native Code Generation Focus
**Rationale**: FR-006 requires Windows-native compatibility for all generated code
**Implementation**:
- Pygame library selection for Snake game (cross-platform but Windows-verified)
- Path handling with `pathlib.Path` for automatic separator handling
- UTF-8 encoding enforcement for all file operations
**Validation**: 95% of generated code runs without syntax errors (SC-002)

### Decision: Stateless Backend Architecture
**Rationale**: Constitution Article V requires stateless backend design
**Implementation**:
- Session state managed in frontend (localStorage/Zustand)
- Generated files persisted to filesystem
- Backend restart-safe at any time
**Benefits**: Reliable deployment and scaling

### Decision: Timeout Hierarchy
**Rationale**: Constitution Article VI requires timeout controls across all layers
**Implementation**:
- API calls: 60s timeout (FR-027)
- E2E tests: 180s global execution limit
- Frontend fetch: 120s circuit breaker
**Benefits**: Prevents hanging operations and ensures responsive user experience

## Integration Points Resolved

### OpenAI SDK Migration Compatibility
- **Backward Compatibility**: Maintains existing error types and Chinese messages (FR-014)
- **Streaming Format**: Preserves identical chunk format (FR-015)
- **Parameter Mapping**: Replicates Anthropic parameters exactly (FR-016)
- **Integration Tests**: Compares outputs between SDKs (FR-017)
- **Development Mode**: Mock responses when no API key (FR-018)

### Reasoning Content Separation
- **MiniMax Configuration**: `extra_body={"reasoning_split": True}` (FR-019)
- **Clean Separation**: Thinking content isolated to `reasoning_details` field
- **Content Integrity**: `<think>` tags never appear in `delta.content`

### Process Documentation Strategy
- **Intermediate Artifacts**: All phase outputs saved as separate files (FR-023)
- **Documentation Structure**: `spec.md`, `plan.md`, `main.py` per project
- **Content Types**: Specification docs, design docs, clean executable code

## Risk Assessment & Mitigations

### High Risk: AI Engine Reliability
**Risk**: MiniMax API outages or response inconsistencies
**Mitigation**:
- Circuit breaker pattern implementation
- Retry logic with exponential backoff
- Clear error messages for user retry capability

### Medium Risk: Windows Environment Variability
**Risk**: Path handling, encoding, and execution differences
**Mitigation**:
- `pathlib.Path` for all file operations
- Explicit UTF-8 encoding for all I/O
- Virtual environment isolation enforcement

### Medium Risk: Code Generation Quality
**Risk**: AI generates syntactically incorrect or non-functional code
**Mitigation**:
- AST validation for all generated code
- Robust Markdown parsing with fallbacks
- User retry capability for failed generations

### Low Risk: Concurrent User Load
**Risk**: 1-5 concurrent users may overwhelm resources
**Mitigation**:
- Stateless backend design
- Circuit breaker prevents cascade failures
- No rate limiting (reliance on concurrent limits only)

## Success Criteria Validation

All research decisions support the measurable outcomes defined in the feature specification:

- **SC-001** (<5 min generation): Supported by timeout controls and efficient processing
- **SC-002** (95% syntax correct): Supported by AST validation and robust parsing
- **SC-003** (phase understanding): Supported by educational workflow design
- **SC-004** (zero startup errors): Supported by configuration validation and environment checks
- **SC-006-S-008** (OpenAI migration): Supported by compatibility research and testing approach
- **SC-009** (AST validation): Directly implemented via `ast.parse()` requirement
- **SC-010-S-011** (educational content): Supported by raw content preservation and artifact saving

## Conclusion

All technical uncertainties have been resolved through research and documented decisions. The implementation approach balances educational goals with technical robustness, Windows-native compatibility, and constitutional compliance. The three-phase workflow ensures users experience the full software engineering process while receiving reliable, executable code outputs.
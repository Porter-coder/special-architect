# Feature Specification: AI Code Flow MVP (Foundation)

**Feature Branch**: `001-ai-code-flow`
**Created**: 2025-12-31
**Status**: Draft
**Input**: User description: "AI Code Flow MVP Foundation with process transparency and educational feedback"

## Clarifications

### Session 2025-12-31

- Q: What is the expected maximum number of concurrent users the system should support? → A: 1-5 concurrent users (minimal prototype scale)
- Q: Should the system require user authentication to access the code generation functionality? → A: No authentication required (completely open access)
- Q: When errors occur during code generation, how should the system recover and what should users see? → A: Allow users to retry failed requests with clear error messages
- Q: How long should the system retain user requests and generated code results? → A: Generated files persist in local projects/ folder indefinitely; session history is transient
- Q: What specific rate limits should be applied to prevent abuse of the open-access system? → A: No rate limiting (rely on concurrent user limits only)

### Session 2025-12-31 (Migration to OpenAI SDK)

- Q: Should the OpenAI SDK migration maintain full backward compatibility with existing Anthropic SDK error types and messages? → A: Yes - preserve existing error types and Chinese error messages
- Q: Should the OpenAI SDK implementation maintain the exact same streaming response format (thinking/text chunks) as the current Anthropic SDK? → A: Yes - maintain identical chunk format for frontend compatibility
- Q: Should the OpenAI SDK configuration exactly replicate current Anthropic parameters (model, max_tokens, temperature) for consistent behavior? → A: Yes - use identical model and parameter values
- Q: Should the migration include integration tests to verify OpenAI SDK produces identical results to Anthropic SDK for same inputs? → A: Yes - add integration tests comparing both SDK outputs
- Q: Should the OpenAI SDK migration preserve the existing development mode functionality (mock responses when no API key)? → A: Yes - maintain dev mode with mock streaming responses

### Session 2025-12-31 (MiniMax API Response Format)

- Q: When using extra_body={"reasoning_split": True}, does MiniMax guarantee that <think> tags never appear in delta.content, with thinking content isolated to reasoning_details field? → A: Yes - reasoning_split ensures clean separation of thinking and code content
- Q: Should the system force pure code output via strict prompts OR allow Markdown code blocks with robust backend parsing? → A: Allow Markdown code blocks with robust backend parsing and AST validation
- Q: Should all generated code be required to pass ast.parse() validation to ensure syntactic correctness? → A: Yes - all generated code must pass ast.parse() validation

### Session 2025-12-31 (Dual-Track Content Strategy)

- Q: Should SSE streaming preserve raw AI content (including Markdown/explanations) OR clean content during streaming? → A: Preserve raw AI content in SSE streams for process transparency
- Q: Should intermediate phase outputs be saved as separate documentation files OR only final code saved? → A: Save all phase outputs as separate documentation files
- Q: When should content cleaning and validation occur - incrementally per phase OR only at completion? → A: Clean only at Phase 3 completion, validate all artifacts

### Session 2025-01-01

- Q: How strict should virtual environment enforcement be for Python code execution? → A: Strict enforcement required (block execution if not in backend\.venv)
- Q: How should the system handle configuration management? → A: Require backend/config.json (fail fast if missing)
- Q: What timeout values should be used for network requests? → A: 60 seconds for all requests (180s for E2E verification script)
- Q: How should the system handle external API failures? → A: Circuit breaker with retry (fail fast during outages, auto-retry)
- Q: What observability features should be implemented? → A: Structured logging with request metrics (response times, error rates, API usage)
- Q: How should comprehensive system trace logging be configured across environments? → A: TRACE level always enabled everywhere (maximum debugging, potential performance impact)
- Q: How should sensitive data be handled in comprehensive logging? → A: Log everything as-is (maximum transparency, potential security risk)
- Q: How should log file storage and cleanup be managed? → A: Implement log rotation and cleanup (size-based rotation, retention policies)
- Q: What scope should comprehensive system trace logging cover? → A: Everything including third-party libraries (maximum detail, high overhead)

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Generate Snake Game (Priority: P1)

As a user who wants to learn programming through AI assistance, I want to request "帮我写个贪吃蛇" (help me write a Snake game) and see the complete software engineering process unfold transparently, so that I understand how AI breaks down the task into specification, planning, and implementation phases.

**Why this priority**: This is the core MVP functionality that demonstrates the educational value - users can immediately experience the process transparency and get a working Snake game as their first interaction.

**Independent Test**: Can be fully tested by entering "帮我写个贪吃蛇" in the web interface and verifying that all three phases (Specify, Plan, Implement) are shown with appropriate educational messages, resulting in a working Snake game code that can be downloaded.

**Acceptance Scenarios**:

1. **Given** a web interface is loaded, **When** user enters "帮我写个贪吃蛇", **Then** the interface shows Step 1: Specify with message "正在分析需求，定义功能边界..."
2. **Given** Step 1 is complete, **When** system processes the request, **Then** interface shows Step 2: Plan with message "正在设计技术方案，确定使用 Pygame 库..."
3. **Given** Step 2 is complete, **When** system generates code, **Then** interface shows Step 3: Implement with message "正在编写代码..."
4. **Given** Step 3 is complete, **When** generation finishes, **Then** user can view and download the generated `main.py` file containing working Snake game code

---

### User Story 2 - Process Transparency Education (Priority: P1)

As a user curious about how AI programming works, I want to see real-time feedback during each phase of the development process, so that I understand that AI programming is not magic but follows rigorous software engineering principles.

**Why this priority**: This addresses the core philosophy of "process transparency" - users need to see the Specify -> Plan -> Implement workflow to break the "AI magic" misconception.

**Independent Test**: Can be fully tested by observing the interface during any code generation request and verifying that appropriate educational messages are displayed for each phase without requiring code generation to complete.

**Acceptance Scenarios**:

1. **Given** user submits any code generation request, **When** Specify phase begins, **Then** interface displays educational message explaining natural language to technical specification conversion
2. **Given** Specify phase completes, **When** Plan phase begins, **Then** interface displays educational message explaining specification to code structure design
3. **Given** Plan phase begins, **When** AI generates content, **Then** SSE stream shows raw AI output including Markdown documentation and explanations
4. **Given** Plan phase completes, **When** Implement phase begins, **Then** interface displays educational message explaining code writing process
5. **Given** Implement phase completes, **When** project is saved, **Then** spec.md contains specification docs, plan.md contains design docs, and main.py contains clean executable code

---

### User Story 3 - Generic Code Generation (Priority: P2)

As a developer exploring different programming needs, I want to request various types of applications beyond Snake game, so that I can use this as a general-purpose code generation tool for different projects.

**Why this priority**: Establishes the system as a universal code generation engine rather than a single-purpose tool, enabling broader use cases and demonstrating AI adaptability.

**Independent Test**: Can be fully tested by submitting different types of requests (web app, data processing script, game, utility) and verifying that each goes through the full Specify-Plan-Implement process with appropriate educational feedback.

**Acceptance Scenarios**:

1. **Given** user requests a web application, **When** system processes the request, **Then** it identifies web-specific technologies and generates appropriate code structure
2. **Given** user requests a data processing script, **When** system processes the request, **Then** it identifies data processing libraries and generates appropriate code structure
3. **Given** user requests any application type, **When** system processes the request, **Then** it dynamically selects appropriate technologies without hardcoded responses

### Edge Cases

- What happens when user requests extremely complex applications beyond MVP scope?
- How does system handle requests in different languages (English vs Chinese)?
- What happens when AI engine returns incomplete or invalid code?
- How does system handle network connectivity issues during generation?
- What happens when user requests applications requiring external dependencies not available on target platform?
- How does system handle ambiguous or incomplete user requests?
- What happens when multiple users request generation simultaneously?

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST accept natural language requests for code generation through a web interface
- **FR-002**: System MUST display real-time educational feedback showing the Specify-Plan-Implement process phases
- **FR-003**: System MUST generate working, executable code based on user requests without hardcoded responses
- **FR-004**: System MUST use MiniMax AI engine for all code generation operations
- **FR-005**: System MUST provide downloadable code files as the final output
- **FR-006**: System MUST maintain Windows-native compatibility for all generated code and scripts
- **FR-007**: System MUST follow Constitution's environment isolation requirements
- **FR-008**: System MUST start without errors in Windows environment
- **FR-009**: System MUST support 1-5 concurrent users for code generation requests
- **FR-010**: System MUST rely on concurrent user limits (1-5 users) for abuse prevention (no additional rate limiting)
- **FR-011**: System MUST allow users to retry failed code generation requests with clear error messages displayed
- **FR-012**: System MUST persist generated code files in local projects/ folder indefinitely while keeping session history transient
- **FR-013**: System MUST use OpenAI SDK with MiniMax compatibility mode instead of Anthropic SDK
- **FR-014**: System MUST maintain full backward compatibility with existing error types and Chinese error messages during SDK migration
- **FR-015**: System MUST preserve identical streaming response format (thinking/text chunks) for frontend compatibility
- **FR-016**: System MUST replicate current Anthropic SDK parameters (model, max_tokens, temperature) in OpenAI SDK configuration
- **FR-017**: System MUST include integration tests comparing OpenAI SDK outputs with Anthropic SDK for same inputs
- **FR-018**: System MUST preserve development mode functionality with mock streaming responses when no API key is provided
- **FR-019**: System MUST use extra_body={"reasoning_split": True} to ensure <think> tags never appear in delta.content
- **FR-020**: System MUST implement robust Markdown code block parsing to extract clean Python code from AI responses
- **FR-021**: System MUST validate all extracted code using ast.parse() to ensure syntactic correctness before saving files
- **FR-022**: System MUST preserve raw AI content in SSE streams to show full generation process including Markdown and explanations
- **FR-023**: System MUST save intermediate phase outputs as separate documentation files (spec.md for Phase 1, plan.md for Phase 2)
- **FR-024**: System MUST perform content cleaning and validation only at Phase 3 completion, not during streaming
- **FR-025**: System MUST enforce virtual environment isolation - any Python code execution MUST verify `sys.prefix` points to `backend\.venv` and immediately exit with "VENV_NOT_ACTIVATED" if not in the correct environment
- **FR-026**: System MUST read configuration from `backend/config.json` at startup and fail fast with clear error message if file is missing or invalid
- **FR-027**: System MUST include `timeout=60` parameter in all network requests (httpx, openai, fetch); E2E verification scripts MUST use 180s global execution limit
- **FR-028**: System MUST implement circuit breaker pattern for external API calls with automatic retry logic to handle temporary failures and prevent cascade failures
- **FR-029**: System MUST implement comprehensive system trace logging capturing ALL program execution details including function entry/exit, variable state changes, environment loading, dependency injection, file I/O, and API request/response data (with headers and partial chunks) in strict JSONL format to `logs/system_trace.jsonl` with TRACE level always enabled everywhere (including third-party libraries) without data sanitization, implementing log rotation and cleanup policies for post-mortem debugging of environment issues

### Key Entities *(include if feature involves data)*

- **Code Generation Request**: User input text, processing status, generated code output
- **Process Phase**: Current phase (Specify/Plan/Implement), educational message, timestamp
- **Generated Project**: File structure, main code file, dependencies list

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: Users can generate working Snake game code in under 5 minutes from request submission
- **SC-002**: 95% of generated code runs without syntax errors on target Windows environment
- **SC-003**: Users can successfully identify and understand the three development phases (Specify, Plan, Implement) after using the system once
- **SC-004**: System maintains zero startup errors across 100 consecutive runs on Windows
- **SC-005**: 90% of users report improved understanding of software development process after first use
- **SC-006**: OpenAI SDK migration completes successfully with "OpenAI Migration Complete" confirmation
- **SC-007**: All existing functionality (streaming, error handling, dev mode) works identically after migration
- **SC-008**: Integration tests pass showing OpenAI SDK produces equivalent results to Anthropic SDK
- **SC-009**: 100% of generated code files pass ast.parse() validation for syntactic correctness
- **SC-010**: SSE streams contain rich educational content (Markdown docs, explanations) visible to users
- **SC-011**: All projects contain complete documentation artifacts (spec.md, plan.md, main.py) with appropriate content types

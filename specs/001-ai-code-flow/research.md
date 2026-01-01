# Research: Dual-Track Content Strategy Implementation

**Date**: 2025-12-31
**Feature**: AI Code Flow MVP with Dual-Track Content Strategy
**Status**: Complete

## Research Questions & Findings

### RQ-001: MiniMax API reasoning_split Parameter Behavior

**Question**: How does the `extra_body={"reasoning_split": True}` parameter work in MiniMax API integration with OpenAI SDK?

**Findings**:
- **Decision**: Use `extra_body={"reasoning_split": True}` in OpenAI client configuration
- **Rationale**: Ensures clean separation between thinking content (reasoning_details) and actual content (delta.content), preventing `<think>` tags from appearing in code streams
- **Implementation**: Add to client initialization: `extra_body={"reasoning_split": True}`
- **Alternatives Considered**: Manual regex filtering (rejected due to complexity and unreliability)

**Source**: MiniMax API documentation, OpenAI SDK compatibility layer

---

### RQ-002: AST Validation for Python Code Quality

**Question**: What are best practices for using Python's ast module to validate generated code syntactically?

**Findings**:
- **Decision**: Use `ast.parse(code_string, mode='exec')` for full module validation
- **Rationale**: Catches syntax errors, undefined names, and structural issues while being fast and built-in
- **Implementation**: Wrap in try/except, return validation result with error details if parsing fails
- **Alternatives Considered**:
  - `compile()` function (rejected - less comprehensive error reporting)
  - External linters (rejected - adds dependencies and complexity)

**Source**: Python ast module documentation, static analysis best practices

---

### RQ-003: Markdown Code Block Extraction Strategies

**Question**: What are reliable patterns for extracting Python code from Markdown-formatted AI responses?

**Findings**:
- **Decision**: Multi-stage regex approach with priority scoring
- **Rationale**: AI responses may contain multiple code blocks; need to identify the most relevant Python code
- **Implementation**:
  1. Extract all ```python blocks
  2. Score blocks by indicators (import statements, function definitions, pygame references)
  3. Select highest-scoring block as final code
  4. Fallback to general ``` blocks if no python-specific blocks found
- **Alternatives Considered**: Simple first-match extraction (rejected - misses optimal code blocks)

**Source**: Common LLM output patterns, regex best practices

---

### RQ-004: Dual-Track Content Streaming Architecture

**Question**: How to implement streaming that preserves educational content while ensuring clean artifact saving?

**Findings**:
- **Decision**: Raw streaming with batched post-processing
- **Rationale**: Educational value requires showing full AI thought process; production quality requires clean artifacts
- **Implementation**:
  - SSE streams: Pass raw AI content unchanged for real-time user experience
  - Artifact saving: Accumulate content per phase, clean only at Phase 3 completion
  - Phase artifacts: spec.md (raw Phase 1), plan.md (raw Phase 2), main.py (cleaned Phase 3)
- **Alternatives Considered**: Clean during streaming (rejected - loses educational transparency)

**Source**: Real-time system design patterns, educational software architectures

## Technical Decisions Summary

| Component | Decision | Rationale |
|-----------|----------|-----------|
| API Integration | MiniMax with reasoning_split | Clean content separation |
| Code Validation | Python ast.parse() | Built-in, comprehensive syntax checking |
| Content Parsing | Priority-scored regex extraction | Handles multiple code blocks reliably |
| Streaming Strategy | Raw content preservation | Maintains educational transparency |
| Artifact Structure | Per-project UUID directories | Clean organization, persistent storage |

## Implementation Notes

- **Phase Timing**: Content cleaning occurs only after Phase 3 completion, not during streaming
- **Error Handling**: AST validation failures should be logged but not block streaming (user still sees process)
- **Performance**: AST parsing is fast enough for real-time validation in Phase 3
- **Compatibility**: Windows path handling with pathlib.Path throughout

## Next Steps

Research complete. Ready for Phase 1 design artifacts (data-model.md, contracts/, quickstart.md).
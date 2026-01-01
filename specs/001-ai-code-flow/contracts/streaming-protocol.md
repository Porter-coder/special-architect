# Streaming Protocol Specification: AI Code Flow

**Version**: 1.0.0
**Date**: 2026-01-01
**Protocol**: Server-Sent Events (SSE)

## Overview

The AI Code Flow system uses Server-Sent Events (SSE) to provide real-time educational feedback during the three-phase code generation process. This protocol ensures process transparency while maintaining compatibility with existing frontend implementations.

## Connection Establishment

### Endpoint
```
POST /generate-code
Content-Type: application/json
Accept: text/event-stream
```

### Request Format
```json
{
  "user_input": "帮我写个贪吃蛇"
}
```

### Response Headers
```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: Content-Type
```

## Event Types

### 1. phase_update
Indicates transition between development phases with educational messaging.

**Frequency**: Once per phase transition
**Purpose**: Educational workflow transparency

**Event Format**:
```
event: phase_update
data: {"phase": "specify", "message": "正在分析需求，定义功能边界...", "timestamp": "2026-01-01T12:00:00Z"}
```

**Data Schema**:
```typescript
interface PhaseUpdateData {
  phase: "specify" | "plan" | "implement";
  message: string;  // Chinese educational message
  timestamp: string; // ISO 8601 datetime
}
```

### 2. content_chunk
Streams raw AI-generated content including thinking process and code.

**Frequency**: Multiple times per phase
**Purpose**: Process transparency and real-time feedback

**Event Format**:
```
event: content_chunk
data: {"type": "thinking", "content": "分析用户需求：贪吃蛇游戏需要基本的游戏循环、蛇的移动逻辑、食物生成和碰撞检测...", "phase": "specify"}
```

**Data Schema**:
```typescript
interface ContentChunkData {
  type: "thinking" | "code" | "documentation";
  content: string;    // Raw AI output (may include Markdown)
  phase: "specify" | "plan" | "implement";
  sequence?: number;  // Optional chunk ordering
}
```

### 3. completion
Signals successful completion of code generation.

**Frequency**: Once at completion
**Purpose**: Provide access to generated project

**Event Format**:
```
event: completion
data: {"project_id": "123e4567-e89b-12d3-a456-426614174000", "status": "success", "project_name": "snake_game_20260101_123456"}
```

**Data Schema**:
```typescript
interface CompletionData {
  project_id: string;     // UUID of generated project
  status: "success" | "partial_success" | "validation_failed";
  project_name: string;   // Human-readable project identifier
  validation_errors?: string[]; // Present if status is validation_failed
}
```

### 4. error
Signals generation failure with retry capability.

**Frequency**: Once on failure
**Purpose**: Error handling and user recovery

**Event Format**:
```
event: error
data: {"error": "AI_ENGINE_ERROR", "message": "AI 引擎暂时不可用，请稍后重试", "retryable": true, "retry_after": 30}
```

**Data Schema**:
```typescript
interface ErrorData {
  error: "VENV_NOT_ACTIVATED" | "CONFIG_MISSING" | "AI_ENGINE_ERROR" | "TIMEOUT_ERROR" | "VALIDATION_ERROR" | "SYSTEM_OVERLOAD";
  message: string;        // Chinese error message
  retryable: boolean;     // Whether user can retry
  retry_after?: number;   // Seconds to wait before retry (optional)
  request_id?: string;    // For debugging (optional)
}
```

## Content Processing Rules

### Raw Content Preservation
- **SSE Stream**: Contains complete raw AI output including Markdown, explanations, and thinking content
- **Educational Value**: Users see the actual AI reasoning process unfold
- **No Cleaning**: Content filtering occurs only at Phase 3 completion, not during streaming

### Content Types
1. **thinking**: AI's reasoning and analysis process
   - May include Chinese text and technical analysis
   - Shows problem decomposition and solution planning

2. **code**: Raw code blocks from AI response
   - May include Markdown code fence markers
   - Preserves original formatting and comments

3. **documentation**: Generated specification or design documents
   - Includes README files, design docs, API documentation
   - Maintains Markdown formatting

### Chunk Size Management
- **Maximum Chunk Size**: 4096 characters per event
- **Chunking Strategy**: Split large responses at natural boundaries (sentences, code blocks)
- **Sequence Numbers**: Optional ordering for multi-chunk content

## Error Handling

### Connection Errors
- **Automatic Retry**: Frontend implements exponential backoff (1s, 2s, 4s, 8s max)
- **Circuit Breaker**: 120-second timeout before showing user error
- **Recovery**: Failed requests can be retried by user

### Content Validation Errors
- **AST Validation**: Python code validated using `ast.parse()` at completion
- **Error Reporting**: Validation failures reported in completion event
- **Partial Success**: Projects with validation errors still downloadable but flagged

### System Limits
- **Concurrent Users**: Maximum 1-5 simultaneous connections
- **Rate Limiting**: None (reliance on concurrent user limits)
- **Timeout**: 60 seconds for AI API calls, 180 seconds for E2E operations

## Frontend Integration

### EventSource Usage
```javascript
const eventSource = new EventSource('/generate-code', {
  method: 'POST',
  body: JSON.stringify({ user_input: userInput }),
  headers: { 'Content-Type': 'application/json' }
});

// Handle different event types
eventSource.addEventListener('phase_update', (event) => {
  const data = JSON.parse(event.data);
  updatePhaseDisplay(data.phase, data.message);
});

eventSource.addEventListener('content_chunk', (event) => {
  const data = JSON.parse(event.data);
  appendToStream(data.content, data.type);
});

eventSource.addEventListener('completion', (event) => {
  const data = JSON.parse(event.data);
  handleCompletion(data);
});

eventSource.addEventListener('error', (event) => {
  const data = JSON.parse(event.data);
  handleError(data);
});
```

### State Management
- **Phase Tracking**: Update UI based on phase_update events
- **Content Accumulation**: Build complete response from content_chunk events
- **Progress Indication**: Show real-time progress through streaming
- **Error Recovery**: Provide retry options for retryable errors

## Backward Compatibility

### Existing Frontend Support
- **Streaming Format**: Maintains identical chunk format to Anthropic SDK
- **Event Types**: Compatible with existing event handling code
- **Error Types**: Preserves existing error type constants

### Migration Path
- **OpenAI SDK**: Drop-in replacement with MiniMax compatibility
- **Response Format**: Identical streaming response structure
- **Parameter Mapping**: Same model, max_tokens, temperature values

## Testing & Validation

### Integration Tests
- **SDK Comparison**: Verify OpenAI SDK produces equivalent results to Anthropic SDK
- **Streaming Verification**: Ensure all event types are properly formatted
- **Error Scenarios**: Test all error conditions and recovery paths

### Performance Benchmarks
- **Connection Latency**: <100ms event delivery
- **Throughput**: Support 1-5 concurrent streaming connections
- **Memory Usage**: Efficient content buffering without excessive memory growth

## Future Extensions

### Enhanced Content Types
- **file_creation**: Specific events for file creation notifications
- **dependency_resolution**: Events for dependency analysis and validation
- **testing_progress**: Real-time test execution feedback

### Advanced Features
- **Interactive Streaming**: Allow user input during generation process
- **Partial Results**: Download intermediate results before completion
- **Collaborative Generation**: Multi-user participation in generation process

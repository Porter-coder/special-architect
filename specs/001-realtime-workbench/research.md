# Research & Implementation: Real-Time Workbench Rendering

**Date**: 2026-01-02
**Context**: Resolving technical clarifications for Next.js monolith architecture with MiniMax streaming and Windows compatibility (Constitution v2.0.0)

## ✅ IMPLEMENTATION COMPLETED: Next.js Monolith Migration

Successfully migrated from Python backend to Next.js monolith with MiniMax streaming integration. All clarifications from Constitution v2.0.0 addressed.

### Windows-Specific Research & Decisions

Successfully implemented streaming file creation with SSE events. AI generation completes first (30s), then files are written one-by-one with real-time SSE events for immediate workbench updates.

### Implementation Summary

#### Modified Files:
1. **`backend/src/services/project_service.py`**:
   - Added `save_project_files_streaming()` method
   - Converts bulk file writing to async generator yielding SSE events
   - Maintains atomic file operations with `write_text()`

2. **`backend/src/services/code_generation_service.py`**:
   - Modified `generate_code_stream()` to use streaming file saving
   - Yields `file_written` events as files are created on disk

3. **`backend/src/api/generate.py`**:
   - Added `_emit_streaming_event()` helper function
   - Modified SSE endpoint to forward file creation events
   - Events are queued and sent to connected clients immediately

#### Event Flow:
```
AI Generation (30s) → File Parsing → Streaming File Creation
                                      ↓
                               file_written SSE Events
                                      ↓
                            Frontend Workbench Updates
```

#### SSE Event Format:
```json
{
  "event": "file_written",
  "data": {
    "filename": "main.py",
    "path": "src/main.py",
    "type": "file",
    "status": "created",
    "size_bytes": 1024,
    "timestamp": "2026-01-02T10:00:05Z"
  }
}
```

### User Experience Achieved:
- ✅ **30s AI wait** (unchanged from current)
- ✅ **Instant file visibility** (files appear in workbench immediately after creation)
- ✅ **Real-time progress** (like watching a ZIP file extract)
- ✅ **Windows compatible** (pathlib.Path handles separators automatically)

## SSE Connection Timeout Handling

### Decision: Implement progressive timeout strategy with automatic reconnection

**Rationale**:
- SSE connections for long-running generation (minutes) need robust timeout handling
- Windows environment may have network interruptions or firewall timeouts
- User experience requires seamless reconnection without losing progress

**Implementation Approach**:
- Frontend SSE connection with 30-second heartbeat
- Automatic reconnection on connection loss (up to 3 attempts)
- Server-side ping/pong mechanism to detect broken connections
- Client-side buffering of missed events during reconnection

**Alternatives Considered**:
- WebSocket upgrade: Rejected due to increased complexity and server requirements
- Polling fallback: Rejected due to higher latency and server load
- No timeout handling: Rejected due to poor user experience on network issues

## Command Execution Protocol - Absolute Virtual Environment Paths

### Decision: Runtime environment detection with absolute path resolution

**Rationale**:
- Constitution requires absolute virtual environment paths for security and isolation
- Windows and cross-platform compatibility needed for development and deployment
- Must prevent accidental execution outside virtual environments

**Implementation Approach**:
```python
# Runtime detection pattern
import sys
import os
from pathlib import Path

def get_python_executable():
    """Get absolute path to virtual environment Python executable"""
    if os.name == 'nt':  # Windows
        venv_python = Path('backend/.venv/Scripts/python.exe')
    else:  # Unix-like
        venv_python = Path('backend/.venv/bin/python')

    if venv_python.exists():
        return str(venv_python.absolute())
    else:
        raise RuntimeError("Virtual environment not found. Run setup first.")

# In all scripts - validate environment before execution
def validate_environment():
    python_exe = get_python_executable()
    if sys.executable != python_exe:
        print(f"ERROR: Must run with virtual environment Python: {python_exe}")
        sys.exit(1)
```

**Windows-Specific Patterns**:
- Use `subprocess.run()` with `shell=True` for PowerShell commands
- Environment variables via `os.environ` (not `export`)
- File operations via `pathlib.Path` for automatic separator handling
- Encoding explicitly set to `utf-8` for all file operations

**Alternatives Considered**:
- Global Python installation: Rejected due to constitution violation and dependency conflicts
- Relative path detection: Rejected due to potential execution from wrong directories
- Manual path configuration: Rejected due to maintenance burden and error-proneness

## Additional Research Findings

### SSE Event Structure Validation
- Event format confirmed: `event: file_written\ndata: {"filename": "...", "path": "...", "type": "file", "status": "created"}\n\n`
- JSON parsing in frontend: Use `JSON.parse()` with error handling
- Event deduplication: Implement client-side tracking to prevent duplicate file additions

### Windows File System Considerations
- `pathlib.Path` automatically handles `\` vs `/` separators
- Atomic file writes: Use temporary files + atomic rename pattern
- File watching: Consider `watchdog` library for cross-platform file monitoring (if needed)
- Permissions: Ensure write access to `projects/` directory

### Performance Considerations
- SSE event frequency: Target <100ms delay between file write and event emission
- Memory usage: Stream events without buffering entire project state
- Connection pooling: Single SSE connection per generation session

## ✅ MIGRATION COMPLETE: Python → Next.js

**Successfully migrated code generation from Python backend to Next.js API routes with MiniMax integration.**

### Migration Summary

#### **Architecture Change**
- **BEFORE**: Python FastAPI backend with separate Node.js frontend
- **AFTER**: Unified Next.js application with API routes

#### **Created Files**
1. **`frontend/src/app/api/generate/route.ts`** - Next.js API route for streaming generation
   - MiniMax API integration with streaming
   - Three-phase generation (SPECIFY → PLAN → IMPLEMENT)
   - Real-time file writing with SSE events
   - Automatic documentation generation

2. **`frontend/src/app/workbench/page.tsx`** - Real-time workbench UI
   - SSE connection management
   - Live file tree updates
   - Connection status indicators

3. **`frontend/src/app/page.tsx`** - Main generation interface
   - User prompt input
   - Generation initiation
   - Redirect to streaming workbench

4. **`frontend/src/components/WorkbenchScene.tsx`** - Enhanced workbench component
   - Streaming file display
   - Connection status visualization
   - Real-time file tree updates

5. **`frontend/env.config.ts`** - Environment configuration
   - MiniMax API credentials
   - Project storage paths

6. **Updated `frontend/package.json`** - Next.js dependencies and scripts

#### **Migrated Intelligence**
- **Prompts**: All three-phase generation prompts extracted from Python
- **Logic**: File parsing, documentation generation, project structure
- **API Integration**: MiniMax streaming API calls
- **Error Handling**: Comprehensive error management and user feedback

## Windows-Specific Constitution Compliance (v2.0.0)

### SSE Connection Timeout Handling for Interrupted Streams

**Decision**: Implement progressive SSE reconnection with state recovery

**Rationale**:
- Next.js monolith runs on single runtime, network interruptions can break long-running generation streams
- Windows environment may have firewall or network issues during 30-60 second generation periods
- User experience requires seamless continuation without losing generation progress

**Implementation Approach**:
- SSE connection with 30-second heartbeat mechanism
- Automatic reconnection (up to 3 attempts) with exponential backoff
- Client-side event buffering during reconnection periods
- Server-side generation state persistence for recovery

**Alternatives Considered**:
- WebSocket upgrade: Rejected due to increased complexity and Next.js API route limitations
- HTTP polling fallback: Rejected due to higher server load and latency
- No reconnection: Rejected due to poor user experience on Windows network issues

### PowerShell/CMD npm Script Compatibility

**Decision**: Use cross-platform npm script patterns with explicit PowerShell compatibility

**Rationale**:
- Constitution v2.0.0 mandates Windows PowerShell/CMD compatibility
- Next.js development and build scripts must work in Windows environment
- Development workflow requires consistent script execution across platforms

**Implementation Approach**:
```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "jest",
    "test:watch": "jest --watch",
    "clean": "rimraf .next && rimraf node_modules/.cache"
  }
}
```

**Windows-Specific Patterns**:
- `rimraf` instead of `rm -rf` for directory deletion
- `cross-env` for environment variable setting in scripts
- PowerShell-compatible path separators in scripts
- No Unix-specific commands or glob patterns

**Alternatives Considered**:
- Unix-only scripts: Rejected due to constitution violation
- Manual Windows batch files: Rejected due to maintenance overhead
- Platform detection scripts: Rejected due to complexity vs benefit

### cross-env and rimraf Command Handling

**Decision**: Mandatory cross-env for environment variables, rimraf for file operations

**Rationale**:
- Constitution prohibits direct `export` commands (Unix-only)
- Windows environment variables must work in PowerShell and CMD
- File deletion operations need cross-platform compatibility

**Implementation Approach**:
```json
{
  "scripts": {
    "build:prod": "cross-env NODE_ENV=production next build",
    "start:prod": "cross-env NODE_ENV=production next start",
    "clean:all": "rimraf .next && rimraf node_modules/.cache && rimraf dist"
  },
  "dependencies": {
    "cross-env": "^7.0.3",
    "rimraf": "^5.0.5"
  }
}
```

**Windows Command Handling**:
- `cross-env VAR=value command` instead of `export VAR=value && command`
- `rimraf directory` instead of `rm -rf directory`
- PowerShell-compatible variable syntax: `$env:NODE_ENV = 'production'`

**Alternatives Considered**:
- Direct environment variable setting: Rejected due to constitution violation
- Unix commands with WSL: Rejected due to inconsistent Windows environments
- Platform-specific script files: Rejected due to maintenance complexity

#### **New Event Flow**
```
User Input → Next.js API Route → MiniMax Streaming
                ↓
        Three-Phase Generation (30s total)
                ↓
     File Parsing + Documentation Generation
                ↓
       Streaming File Writing with SSE Events
                ↓
         Frontend Real-Time Workbench Updates
```

# Quick Start: Real-Time Workbench Rendering

**Feature**: 001-realtime-workbench
**Date**: 2026-01-02

## Overview

This feature implements real-time workbench rendering with a handover architecture. Users watch projects build file-by-file through SSE streaming, replacing the static waiting screen with an engaging live experience.

## Architecture

### Handover Pattern
- **Python Factory**: Write-only generation service (creates files, emits events)
- **Node.js Librarian**: Read-only file serving service (parses directories, serves JSON)
- **Frontend Workbench**: Real-time UI updates via SSE stream

### Key Components
- SSE streaming for live file creation updates
- Shared PROJECTS_ROOT configuration
- Windows-compatible path handling
- Atomic file operations

## Development Setup

### Prerequisites
- Python 3.11 (Factory backend)
- Node.js v20 (Librarian frontend)
- Windows environment (path separator compatibility)

### Environment Setup
```bash
# Python virtual environment
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Node.js dependencies
cd frontend
npm install
```

### Configuration
Both services must share identical PROJECTS_ROOT:

```python
# backend/config.py
PROJECTS_ROOT = Path("../projects")

# frontend/.env.local
PROJECTS_ROOT=../projects
```

## API Usage

### Start Generation (Python Factory)
```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a Python calculator app"}'
```

**Response**:
```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "generating"
}
```

### Monitor Progress (SSE Stream)
```javascript
const eventSource = new EventSource(
  `http://localhost:8000/api/stream/550e8400-e29b-41d4-a716-446655440000`
);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (event.type === 'file_written') {
    // Add file to workbench tree
    addFileToTree(data.filename, data.path, data.type);
  }
};
```

### Get Project Structure (Node.js Librarian)
```bash
curl http://localhost:3000/api/projects/550e8400-e29b-41d4-a716-446655440000
```

**Response**:
```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "root": {
    "type": "directory",
    "name": "root",
    "path": "",
    "children": [
      {
        "type": "file",
        "name": "main.py",
        "path": "main.py",
        "size_bytes": 256,
        "created_at": "2026-01-02T10:00:05Z"
      }
    ]
  },
  "total_files": 1,
  "generated_at": "2026-01-02T10:00:10Z"
}
```

## Workflow Integration

### User Journey
1. User clicks "Generate" in frontend
2. Frontend calls Python Factory `/api/generate`
3. Python returns UUID, frontend redirects to `/workbench?mode=streaming`
4. Workbench initializes with empty tree and connects to SSE stream
5. Python generates files, emits `file_written` events
6. Workbench updates tree in real-time
7. When complete, user can browse and edit all files

### Error Handling
- **Connection Loss**: Automatic reconnection (up to 3 attempts)
- **Generation Failure**: SSE `generation_error` event with user-friendly message
- **File System Errors**: JSON error responses with Chinese messages
- **Timeout**: 120-second frontend timeout with retry option

## Testing

### Unit Tests (Python)
```bash
cd backend
python -m pytest tests/ -v
```

### Integration Tests (SSE Streaming)
```python
# Test file creation triggers SSE event
def test_file_creation_emits_event():
    # Generate project
    response = client.post("/api/generate", json={"prompt": "test"})
    project_id = response.json()["project_id"]

    # Connect to SSE stream
    # Verify file_written events are emitted
    # Assert event data matches created files
```

### E2E Tests (Playwright)
```javascript
// Test complete generation workflow
test('generates project with live updates', async ({ page }) => {
  await page.goto('/');

  // Click generate
  await page.click('button:has-text("Generate")');

  // Should redirect to workbench
  await expect(page).toHaveURL(/\/workbench\?mode=streaming/);

  // Should show connecting status
  await expect(page.locator('text=Connecting to Factory...')).toBeVisible();

  // Should populate file tree in real-time
  await expect(page.locator('.file-tree')).not.toBeEmpty();

  // Should complete successfully
  await expect(page.locator('text=Generation completed')).toBeVisible();
});
```

## Windows Compatibility

### Path Handling
- Use `pathlib.Path` for automatic separator handling
- Explicit `encoding='utf-8'` for all file operations
- Test with Windows absolute paths (`C:\projects\`)

### Command Execution
```python
# Correct: Absolute virtual environment paths
python_exe = Path("backend/.venv/Scripts/python.exe").absolute()
subprocess.run([str(python_exe), "script.py"], check=True)
```

### Development Scripts
```powershell
# Use cross-env for environment variables
cross-env NODE_ENV=development npm run dev

# Use rimraf for cross-platform deletion
rimraf dist/
```

## Deployment Considerations

### Environment Variables
- `PROJECTS_ROOT`: Shared path configuration
- `SSE_HEARTBEAT_INTERVAL`: Default 30 seconds
- `GENERATION_TIMEOUT`: Default 300 seconds
- `MAX_RECONNECTION_ATTEMPTS`: Default 3

### Monitoring
- SSE connection success rate (>99%)
- File write-to-event emission latency (<100ms)
- Generation completion rate (>95%)
- Error rates by type (network, filesystem, generation)

### Scaling
- Single SSE connection per generation session
- Stateless services (horizontal scaling ready)
- File system as persistent storage layer

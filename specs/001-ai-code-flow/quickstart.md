# Quick Start: AI Code Flow MVP

**Version**: 1.0.0
**Last Updated**: 2026-01-01
**Target Users**: Developers, DevOps engineers, System administrators

## Overview

AI Code Flow is an AI-powered code generation system that transforms natural language requests into working, executable code through a transparent three-phase process. This guide provides everything needed to set up, deploy, and operate the system.

## Prerequisites

### System Requirements

#### Hardware
- **CPU**: 2+ cores (4+ recommended for concurrent users)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 10GB free space for generated projects
- **Network**: Stable internet connection for AI API calls

#### Software
- **Operating System**: Windows 10/11 (native compatibility required)
- **Python**: Version 3.11 (exact match required)
- **Node.js**: Version 20 LTS (exact match required)
- **PowerShell**: Version 5.1+ (included with Windows)

### API Keys
- **MiniMax API Key**: Required for AI code generation
- **OpenAI API Key**: Alternative/fallback AI provider

## Installation

### 1. Repository Setup

```powershell
# Clone the repository
git clone <repository-url>
cd ai-code-flow

# Switch to the feature branch
git checkout 001-ai-code-flow
```

### 2. Backend Setup

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment with Windows-compatible path
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# Install dependencies (exact versions from requirements.txt)
pip install -r requirements.txt

# Verify Python version and environment
python --version  # Should show Python 3.11.x
python -c "import sys; print(sys.prefix)"  # Should end with backend\.venv
```

### 3. Configuration

```powershell
# Create required configuration file
# File: backend/config.json
{
  "minimax": {
    "api_key": "your-minimax-api-key-here",
    "base_url": "https://api.minimax.chat/v1"
  },
  "openai": {
    "api_key": "your-openai-api-key-here",
    "base_url": "https://api.openai.com/v1"
  },
  "generation": {
    "model": "MiniMax-Text-01",
    "max_tokens": 4000,
    "temperature": 0.1,
    "timeout": 60
  },
  "system": {
    "max_concurrent_users": 5,
    "log_level": "TRACE",
    "projects_dir": "../projects"
  }
}
```

### 4. Frontend Setup (Optional)

```powershell
# Navigate to frontend directory
cd ../frontend

# Install Node.js dependencies
npm install

# Verify Node.js version
node --version  # Should show v20.x.x
```

## Quick Start Commands

### Development Mode

```powershell
# Start backend server (from backend/ directory)
.venv\Scripts\activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Start frontend server (from frontend/ directory, new terminal)
npm run dev
```

### Production Deployment

```powershell
# Backend production start
.venv\Scripts\activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Frontend production build
npm run build
npm run start
```

## Testing the System

### 1. Health Check

```powershell
# Verify system is running correctly
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2026-01-01T12:00:00Z",
  "version": "1.0.0",
  "config_valid": true,
  "venv_active": true
}
```

### 2. Code Generation Test

```powershell
# Test code generation with curl
curl -X POST http://localhost:8000/generate-code \
  -H "Content-Type: application/json" \
  -d '{"user_input": "帮我写个简单的计算器"}' \
  -H "Accept: text/event-stream"

# Or test with PowerShell
Invoke-WebRequest -Uri "http://localhost:8000/generate-code" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"user_input": "帮我写个简单的计算器"}'
```

### 3. Web Interface Test

1. Open browser to `http://localhost:3000` (frontend)
2. Enter "帮我写个贪吃蛇" in the input field
3. Observe the three-phase process:
   - **Specify**: "正在分析需求，定义功能边界..."
   - **Plan**: "正在设计技术方案，确定使用 Pygame 库..."
   - **Implement**: "正在编写代码..."
4. Download the generated `main.py` file
5. Run the downloaded code: `python main.py`

## Troubleshooting

### Common Issues

#### VENV_NOT_ACTIVATED Error

**Symptoms**: System returns `{"error": "VENV_NOT_ACTIVATED", "message": "虚拟环境未激活"}`

**Solution**:
```powershell
# Ensure you're in the backend directory
cd backend

# Activate virtual environment
.venv\Scripts\activate

# Verify activation
python -c "import sys; print('Active' if 'backend\\.venv' in sys.prefix else 'Inactive')"
```

#### CONFIG_MISSING Error

**Symptoms**: System returns `{"error": "CONFIG_MISSING", "message": "配置文件缺失"}`

**Solution**:
```powershell
# Verify config.json exists and is valid JSON
Test-Path backend/config.json
Get-Content backend/config.json | ConvertFrom-Json
```

#### AI_ENGINE_ERROR

**Symptoms**: Code generation fails with AI engine errors

**Solutions**:
1. **Check API Keys**: Verify MiniMax and OpenAI API keys are valid
2. **Network Connectivity**: Ensure stable internet connection
3. **Rate Limits**: Wait and retry if hitting API limits
4. **Fallback**: System automatically tries OpenAI if MiniMax fails

#### Windows Compatibility Issues

**Symptoms**: Generated code fails to run on Windows

**Solutions**:
1. **Path Separators**: Ensure code uses `pathlib.Path` for file operations
2. **Encoding**: Verify all files use UTF-8 encoding
3. **Dependencies**: Confirm Pygame and other libraries are Windows-compatible

### Debug Logging

```powershell
# Enable maximum logging for troubleshooting
# Edit backend/config.json:
{
  "system": {
    "log_level": "TRACE"
  }
}

# View logs in real-time
Get-Content logs/system_trace.jsonl -Wait -Tail 10
```

## API Reference

### Core Endpoints

#### POST /generate-code
Generate code from natural language input.

**Request**:
```json
{
  "user_input": "帮我写个贪吃蛇"
}
```

**Response**: Server-Sent Events stream with real-time progress.

#### GET /health
System health check.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-01T12:00:00Z",
  "version": "1.0.0",
  "config_valid": true,
  "venv_active": true
}
```

#### GET /projects/{id}
Get project details.

#### GET /projects/{id}/download
Download generated project files.

### Streaming Events

The system uses Server-Sent Events for real-time feedback:

- `phase_update`: Phase transitions with educational messages
- `content_chunk`: Raw AI output (thinking, code, documentation)
- `completion`: Generation complete with project details
- `error`: Generation failed with retry options

## Performance Tuning

### Concurrent Users
- **Maximum**: 5 concurrent users (configurable in config.json)
- **Monitoring**: Check active requests via health endpoint
- **Scaling**: Increase worker processes for higher concurrency

### Response Times
- **Target**: <5 minutes per code generation request
- **AI API**: 60-second timeout per call
- **Frontend**: 120-second circuit breaker timeout

### Resource Usage
- **Memory**: ~100MB per active generation request
- **Storage**: ~10MB per generated project
- **Cleanup**: Projects persist indefinitely, implement rotation if needed

## Security Considerations

### Environment Isolation
- **Virtual Environment**: Mandatory backend\.venv usage
- **No Global Installs**: All dependencies isolated
- **Path Validation**: Runtime verification of environment paths

### API Security
- **Current**: Open access (no authentication required)
- **Future**: API key authentication planned
- **Network**: HTTPS recommended for production

### Data Handling
- **Generated Code**: Stored in local filesystem
- **Session Data**: Transient (not persisted)
- **Logs**: Comprehensive TRACE logging with no data sanitization

## Monitoring & Maintenance

### Key Metrics

```powershell
# Monitor system health
while ($true) {
  $health = Invoke-RestMethod -Uri "http://localhost:8000/health"
  Write-Host "Status: $($health.status), Active: $($health.activeRequests)"
  Start-Sleep -Seconds 30
}
```

### Log Analysis

```powershell
# Search for errors in logs
Select-String -Path logs/system_trace.jsonl -Pattern "ERROR" |
  Select-Object -Last 10

# Monitor API usage
Select-String -Path logs/system_trace.jsonl -Pattern "minimax|openai" |
  Measure-Object
```

### Backup Strategy

```powershell
# Backup generated projects
Compress-Archive -Path projects/ -DestinationPath "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').zip"

# Backup configuration
Copy-Item backend/config.json "config_backup_$(Get-Date -Format 'yyyyMMdd').json"
```

## Development Workflow

### Code Generation Process

1. **User Request**: Natural language input via web interface
2. **Phase 1 - Specify**: AI analyzes requirements, defines boundaries
3. **Phase 2 - Plan**: AI designs technical approach, selects libraries
4. **Phase 3 - Implement**: AI generates executable code
5. **Validation**: AST parsing ensures syntax correctness
6. **Delivery**: User downloads working project files

### Educational Features

- **Process Transparency**: Users see AI reasoning in real-time
- **Phase Messages**: Chinese educational feedback for each step
- **Raw Content**: Preserves AI explanations and documentation
- **Retry Capability**: Failed requests can be retried with clear errors

## Support & Resources

### Documentation
- `specs/001-ai-code-flow/spec.md`: Complete feature specification
- `specs/001-ai-code-flow/plan.md`: Implementation planning details
- `contracts/`: API specifications and protocols

### Community
- **Issues**: Report bugs and request features
- **Discussions**: Share use cases and best practices
- **Contributing**: See contribution guidelines for code changes

### Professional Services
- **Setup Assistance**: Contact for complex deployment scenarios
- **Custom Integration**: Enterprise integration support
- **Training**: Educational workshops on AI-assisted development

---

## Success Checklist

- [ ] System starts without errors on Windows
- [ ] Health endpoint returns "healthy" status
- [ ] Code generation completes in <5 minutes
- [ ] Generated code runs without syntax errors
- [ ] Users can identify the three development phases
- [ ] OpenAI SDK migration confirmed working
- [ ] All code files pass AST validation
- [ ] SSE streams contain educational content
- [ ] Projects include complete documentation artifacts

**Ready for production when all checklist items pass!**
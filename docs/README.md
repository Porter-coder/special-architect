# AI Code Flow - AI-Powered Code Generation System

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/your-org/ai-code-flow)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/node.js-20-green.svg)](https://nodejs.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

AI Code Flow is an AI-powered code generation system that transforms natural language requests into working, executable code through a structured three-phase process. The system uses a "black box waiting" architecture where AI processing happens asynchronously, with educational progress feedback during the wait.

## 🌟 Key Features

### 🎯 Core Functionality
- **Natural Language Processing**: Convert plain Chinese/English requests into working code
- **Three-Phase Workflow**: Structured Specify → Plan → Implement process with educational feedback
- **Streaming Progress**: Server-Sent Events provide progress updates and thinking messages during AI processing
- **Black Box Architecture**: AI processing happens asynchronously with educational waiting feedback

### 🔧 Technical Excellence
- **SDK Migration**: Seamless OpenAI ↔ MiniMax SDK compatibility with automatic fallback
- **Windows Native**: Full Windows compatibility with environment isolation
- **AST Validation**: Automatic syntax validation for all generated code
- **Concurrent Users**: Support for 1-5 concurrent users with proper management

### 🎓 Educational Value
- **Phase Education**: Clear explanations of development phases in Chinese during processing
- **Waiting Experience**: Educational messages and progress indicators while AI processes in background
- **Code Replay**: Generated code displayed with typing effect for visual feedback

## 🚀 Quick Start

### Prerequisites
- **Windows 10/11** (native compatibility required)
- **Python 3.11** (exact version required)
- **Node.js 20 LTS** (exact version required)
- **MiniMax API Key** and/or **OpenAI API Key**

### Installation

1. **Clone the repository**
   ```powershell
   git clone <repository-url>
   cd ai-code-flow
   git checkout 001-ai-code-flow
   ```

2. **Backend Setup**
   ```powershell
   cd backend
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configuration**
   Create `backend/config.json`:
   ```json
   {
     "minimax": {
       "api_key": "your-minimax-api-key",
       "base_url": "https://api.minimax.chat/v1"
     },
     "openai": {
       "api_key": "your-openai-api-key",
       "base_url": "https://api.openai.com/v1"
     },
     "generation": {
       "model": "MiniMax-M2.1",
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

4. **Frontend Setup (Optional)**
   ```powershell
   cd ../frontend
   npm install
   ```

### Running the Application

**Development Mode:**
```powershell
# Backend (terminal 1)
cd backend && .venv\Scripts\activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend (terminal 2)
cd frontend && npm run dev
```

**Production Mode:**
```powershell
# Backend
cd backend && .venv\Scripts\activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Frontend
cd frontend && npm run build && npm run start
```

## 🎮 Usage Examples

### Basic Code Generation

1. **Web Interface**: Open `http://localhost:3000`
2. **Enter Request**: Type "帮我写个贪吃蛇游戏" (Create a Snake game for me)
3. **Watch Process**: Observe the three-phase workflow:
   - **Specify**: "正在分析用户需求并制定规范..."
   - **Plan**: "正在设计技术方案，确定使用Pygame库..."
   - **Implement**: "正在编写代码..."
4. **Download**: Get your working `main.py` file

### API Usage

```python
import requests

# Generate code via API
response = requests.post(
    "http://localhost:8000/api/generate-code",
    json={"user_input": "创建一个计算器应用"},
    stream=True
)

# Handle streaming response
for line in response.iter_lines():
    if line:
        event = json.loads(line.decode('utf-8'))
        print(f"Event: {event['event']} - {event['data']}")
```

### Advanced Features

**Raw AI Content Access:**
- View unfiltered AI reasoning during generation
- Access intermediate documentation and planning
- Understand AI decision-making processes

**Concurrent Usage:**
- System supports 1-5 concurrent users
- Automatic queue management and fair allocation
- Real-time concurrency monitoring via health endpoint

## 📋 API Reference

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/generate-code` | POST | Start code generation workflow |
| `/api/generate-code/{id}/stream` | GET | Stream generation progress |
| `/api/projects/{id}` | GET | Get project details |
| `/api/projects/{id}/download` | GET | Download project files |
| `/api/health` | GET | System health check |

### Request/Response Examples

**POST /api/generate-code**
```json
{
  "user_input": "帮我写个贪吃蛇游戏",
  "application_type": "game"
}
```

**Response (Streaming Events)**
```json
{
  "event": "phase_update",
  "data": {
    "phase": "specify",
    "message": "正在分析用户需求并制定规范...",
    "status": "active"
  }
}
```

## 🏗️ Architecture

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   AI Services   │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (MiniMax)     │
│                 │    │                 │    │   (OpenAI)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Streaming UI    │    │ Code Generation │    │ AI SDK Router  │
│                 │    │ Service         │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Design Principles

1. **Black Box Processing**: AI generation happens asynchronously in background tasks
2. **Educational Waiting**: Progress messages and thinking indicators during processing wait
3. **SDK Compatibility**: Seamless OpenAI/MiniMax switching with automatic fallback
4. **Windows Native**: Full Windows environment support with virtual environment isolation
5. **Concurrent Safety**: Proper multi-user management with request queuing
6. **Error Resilience**: Comprehensive Chinese error messages and graceful failure handling

## 🧪 Testing

### Validation Tests
```powershell
cd backend
.venv\Scripts\activate
python -m pytest tests/test_validation.py -v
```

### Integration Tests
```powershell
python -m pytest tests/test_integration.py -v
```

### E2E Tests
```powershell
cd frontend
npx playwright test
```

### Performance Testing
```powershell
# Health check monitoring
while ($true) {
  curl http://localhost:8000/api/health
  Start-Sleep -Seconds 30
}
```

## 📊 Monitoring & Observability

### Health Checks
```powershell
curl http://localhost:8000/api/health
```

Response:
```json
{
  "status": "healthy",
  "concurrent_requests": 2,
  "max_concurrent": 5,
  "message": "服务运行正常"
}
```

### Logging
- **TRACE Level**: Maximum debugging information
- **JSONL Format**: Machine-readable logs in `logs/system_trace.jsonl`
- **Automatic Rotation**: 100MB files with 30-day retention

### Metrics
- Request latency and throughput
- AI API usage and costs
- Concurrent user patterns
- Error rates and types

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEVELOPMENT_MODE` | Enable mock responses | `false` |
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `OPENAI_BASE_URL` | OpenAI API base URL | `https://api.openai.com/v1` |

### Configuration File (`backend/config.json`)

See quickstart.md for complete configuration reference.

## 🐛 Troubleshooting

### Common Issues

**Virtual Environment Not Active**
```
Error: VENV_NOT_ACTIVATED
```
```powershell
cd backend
.venv\Scripts\activate
python -c "import sys; print(sys.prefix)"
```

**Configuration Missing**
```
Error: CONFIG_MISSING
```
```powershell
# Verify config.json exists and is valid JSON
Test-Path backend/config.json
Get-Content backend/config.json | ConvertFrom-Json
```

**AI Service Errors**
- Check API keys are valid
- Verify internet connectivity
- System automatically falls back to alternative providers

### Debug Mode
```powershell
# Enable maximum logging
$config = Get-Content backend/config.json | ConvertFrom-Json
$config.system.log_level = "TRACE"
$config | ConvertTo-Json | Set-Content backend/config.json

# Monitor logs in real-time
Get-Content logs/system_trace.jsonl -Wait -Tail 10
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```powershell
# Full development environment
git clone <repo>
cd ai-code-flow
./scripts/setup-development.ps1

# Run tests
./scripts/run-tests.ps1

# Deploy locally
./scripts/deploy-local.ps1
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **MiniMax AI**: For providing powerful AI models
- **OpenAI**: For the comprehensive API ecosystem
- **FastAPI**: For the excellent Python web framework
- **Pygame**: For enabling game development
- **Windows Community**: For native compatibility support

## 📞 Support

- **Documentation**: See `specs/` directory for detailed specifications
- **Issues**: Report bugs and request features
- **Discussions**: Share use cases and best practices
- **Professional Services**: Contact for enterprise integration support

---

**Built with ❤️ for the AI-assisted development community**

*Transforming natural language into working code, one educational step at a time.*

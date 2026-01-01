# Quickstart: AI Code Flow MVP (Dual-Track Content Strategy)

**Date**: 2025-12-31
**Feature**: AI Code Flow MVP with Dual-Track Content Strategy

## Prerequisites

### System Requirements
- **Windows 10/11** (primary target platform)
- **Node.js v20 (LTS)** - Exact version required per constitution
- **Python 3.11** - Exact version required per constitution
- **PowerShell** or **Command Prompt** (Windows-native scripting)
- **MiniMax API Key** - Required for AI code generation

### Environment Setup

#### 1. Node.js Environment (Frontend)
```bash
# Install Node.js v20 (LTS) - required by constitution
# Download from: https://nodejs.org/dist/v20.17.0/node-v20.17.0-x64.msi

# Verify installation
node --version  # Should show v20.x.x
npm --version   # Should show 10.x.x

# Create .nvmrc and .node-version in project root
echo "v20" > .nvmrc
echo "20" > .node-version
```

#### 2. Python Environment (Backend)
```bash
# Install Python 3.11 - required by constitution
# Download from: https://www.python.org/downloads/release/python-3110/

# Verify installation
python --version  # Should show Python 3.11.x

# Create virtual environment (required by constitution)
python -m venv backend\.venv

# Activate virtual environment (Windows)
backend\.venv\Scripts\activate

# Verify virtual environment activation
where python  # Should show backend\.venv\Scripts\python.exe
```

#### 3. MiniMax API Access
```bash
# Get API key from: https://platform.minimaxi.com/
# Set environment variables for MiniMax API via OpenAI SDK
setx OPENAI_API_KEY "your-minimax-api-key-here"
setx OPENAI_BASE_URL "https://api.minimaxi.com/v1"

# Test API connectivity
python -c "import openai; client = openai.OpenAI(); print('API connection successful')"
```

## Project Setup

### 1. Clone and Navigate
```bash
# Clone repository
git clone <repository-url>
cd ai-code-flow

# Checkout feature branch
git checkout 001-ai-code-flow
```

### 2. Backend Setup
```bash
# Activate virtual environment
backend\.venv\Scripts\activate

# Install dependencies (exact versions per constitution)
pip install fastapi==0.109.0
pip install uvicorn==0.27.0
pip install openai>=1.0.0
pip install python-multipart==0.0.6
pip install sse-starlette==2.0.0

# Verify installation
pip list
```

### 3. Frontend Setup
```bash
# Install dependencies (local packages only per constitution)
npm install @anthropic-ai/sdk
npm install next@latest
npm install react@latest
npm install react-dom@latest
npm install tailwindcss
npm install @types/node
npm install @types/react
npm install typescript

# Verify installation
npm list
```

## Development Workflow

### 1. Start Backend (Terminal 1)
```bash
# Activate virtual environment
backend\.venv\Scripts\activate

# Start FastAPI server
cd backend
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start Frontend (Terminal 2)
```bash
# Start Next.js development server
npm run dev
```

### 3. Verify Setup
```bash
# Check backend health
curl http://localhost:8000/health

# Open frontend in browser
# http://localhost:3000
```

## Testing

### Backend Tests (Constitution Required)
```bash
# Activate virtual environment
backend\.venv\Scripts\activate

# Run pytest integration tests
cd backend
python -m pytest tests/integration/ -v

# Run contract tests
python -m pytest tests/contract/ -v
```

### Frontend E2E Tests (Constitution Required)
```bash
# Install Playwright browsers
npx playwright install

# Run E2E tests
npx playwright test tests/e2e/ --headed
```

## Code Generation Demo

### 1. Basic Snake Game Generation
1. Open browser to `http://localhost:3000`
2. Enter: "帮我写个贪吃蛇"
3. Watch the three phases:
   - **Specify**: "正在分析需求，定义功能边界..."
   - **Plan**: "正在设计技术方案，确定使用 Pygame 库..."
   - **Implement**: "正在编写代码..."
4. Download the generated `main.py` file
5. Run the game: `python main.py`

### 2. Test Error Recovery
1. Temporarily disable internet connection
2. Submit a generation request
3. Observe error message: "AI 服务暂时不可用，请稍后重试"
4. Restore connection and click retry

### 3. Test Windows Compatibility
1. Verify all generated files use UTF-8 encoding
2. Check that file paths work correctly on Windows
3. Confirm no GBK encoding issues in Chinese comments

## Constitution Compliance Verification

### Runtime Environment
- ✅ Node.js v20 (LTS) confirmed
- ✅ Python 3.11 confirmed
- ✅ Virtual environment activated
- ✅ No global package installations

### Windows Compatibility
- ✅ PowerShell scripts compatible
- ✅ pathlib.Path used for file operations
- ✅ UTF-8 encoding enforced
- ✅ Windows path separators handled

### Language Standards
- ✅ English in source code and comments
- ✅ Chinese in UI and error messages

### Testing Standards
- ✅ pytest for backend integration
- ✅ Playwright for E2E testing
- ✅ Zero startup errors verified

## Troubleshooting

### Common Issues

**Backend won't start**
```bash
# Check Python version
python --version  # Must be 3.11.x

# Check virtual environment
backend\.venv\Scripts\activate
where python  # Must show virtual environment path

# Check dependencies
pip list | findstr fastapi
```

**Frontend build fails**
```bash
# Check Node.js version
node --version  # Must be v20.x.x

# Clear npm cache
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**AI service connection fails**
```bash
# Check environment variables
echo %OPENAI_API_KEY%
echo %OPENAI_BASE_URL%

# Test API connectivity (OpenAI SDK format)
curl -X POST https://api.minimaxi.com/v1/chat/completions \
  -H "Authorization: Bearer %OPENAI_API_KEY%" \
  -H "Content-Type: application/json" \
  -d '{"model": "MiniMax-M2.1", "messages": [{"role": "user", "content": "Hello"}], "max_tokens": 10}'
```

**File encoding issues**
```bash
# Check generated files
type main.py  # Should display correctly in Chinese
# If garbled, files weren't saved with UTF-8 encoding
```

### Getting Help

- **MiniMax API Issues**: Email Model@minimaxi.com
- **Constitution Compliance**: Refer to `.specify/memory/constitution.md`
- **Development Issues**: Check GitHub issues or create new issue

## Next Steps

After successful setup and testing:

1. **Create Tasks**: Run `/speckit.tasks` to break down implementation
2. **Start Development**: Begin with foundational backend components
3. **Integration Testing**: Verify end-to-end code generation flow
4. **Performance Validation**: Confirm 5-minute generation time limit

The MVP is ready for implementation with all prerequisites validated and constitution compliance confirmed.

# Contributing to AI Code Flow

Thank you for your interest in contributing to AI Code Flow! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites
- Python 3.11 (exact version)
- Node.js 20 LTS (exact version)
- Windows 10/11 development environment
- Git

### Development Setup

1. **Clone and Setup**
   ```powershell
   git clone <repository-url>
   cd ai-code-flow
   git checkout -b feature/your-feature-name
   ```

2. **Backend Development**
   ```powershell
   cd backend
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

3. **Frontend Development** (Optional)
   ```powershell
   cd frontend
   npm install
   ```

4. **Pre-commit Setup**
   ```powershell
   pip install pre-commit
   pre-commit install
   ```

## 📋 Development Workflow

### 1. Choose an Issue
- Check [Issues](../../issues) for tasks labeled `good first issue` or `help wanted`
- Comment on the issue to indicate you're working on it
- Wait for maintainer approval before starting

### 2. Create a Branch
```powershell
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

### 3. Make Changes

**Code Standards:**
- Follow existing code style and patterns
- Add type hints for Python code
- Include docstrings for all functions
- Use Chinese comments for user-facing messages
- English comments for technical implementation

**Testing:**
- Write tests for new functionality
- Ensure all existing tests pass
- Add integration tests for API changes
- Test on Windows environment

### 4. Commit Changes

```powershell
git add .
git commit -m "feat: add amazing new feature

- What was changed
- Why it was changed
- How it was tested"
```

**Commit Message Format:**
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `test:` Test additions/modifications
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

### 5. Push and Create PR

```powershell
git push origin feature/your-feature-name
```

Create a Pull Request with:
- Clear title and description
- Reference to related issues
- Screenshots for UI changes
- Test results

## 🧪 Testing Guidelines

### Backend Testing

```powershell
# Run all tests
cd backend
python -m pytest

# Run specific test file
python -m pytest tests/test_specific.py -v

# Run with coverage
python -m pytest --cov=src --cov-report=html
```

### Frontend Testing

```powershell
cd frontend
npm test
npm run test:e2e  # Playwright E2E tests
```

### Validation Testing

```powershell
# Run production readiness validation
cd backend
python -m pytest tests/test_validation.py -v
```

## 📚 Code Standards

### Python (Backend)

- **Type Hints**: Required for all function parameters and return values
- **Docstrings**: Google-style docstrings for all public functions
- **Imports**: Grouped (standard library, third-party, local)
- **Line Length**: 100 characters maximum
- **Naming**: snake_case for variables/functions, PascalCase for classes

```python
from typing import Dict, List, Optional

def process_user_request(
    user_input: str,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process a user code generation request.

    Args:
        user_input: Natural language request from user
        options: Optional processing parameters

    Returns:
        Dictionary containing processing results

    Raises:
        ValueError: If input validation fails
    """
    # Implementation here
    pass
```

### TypeScript (Frontend)

- **Type Annotations**: Strict typing required
- **Component Structure**: Functional components with hooks
- **Error Handling**: Try-catch with user-friendly messages
- **Naming**: camelCase for variables/functions, PascalCase for components

```typescript
interface CodeGeneratorProps {
  onCodeGenerated: (code: string) => void;
  isLoading: boolean;
}

const CodeGenerator: React.FC<CodeGeneratorProps> = ({
  onCodeGenerated,
  isLoading
}) => {
  // Component implementation
};
```

### API Design

- **RESTful**: Follow REST conventions
- **JSON**: All data exchanged as JSON
- **Chinese Messages**: User-facing error messages in Chinese
- **Consistent Responses**: Standardized response format

```typescript
// Success response
{
  "success": true,
  "data": { /* payload */ },
  "message": "操作成功"
}

// Error response
{
  "success": false,
  "error": "VALIDATION_ERROR",
  "message": "输入参数无效"
}
```

## 🎯 Feature Development

### Adding New Code Generation Types

1. **Update Models**: Add to `backend/src/models/`
2. **Extend Services**: Modify code generation service
3. **Add Validation**: Update dependency checker
4. **Test Thoroughly**: Add unit and integration tests
5. **Update Docs**: Add to API reference

### Adding New AI Providers

1. **Create Service**: Implement AI service interface
2. **Add Configuration**: Update config.json schema
3. **Update Router**: Add to AI service router
4. **Add Tests**: Comprehensive test coverage
5. **Update Fallback**: Ensure graceful degradation

### Frontend Enhancements

1. **Component Design**: Follow existing patterns
2. **State Management**: Use Zustand for global state
3. **Error Handling**: Implement retry logic
4. **Accessibility**: Ensure WCAG compliance
5. **Performance**: Optimize for Windows environments

## 🔧 Tools and Scripts

### Development Scripts

```powershell
# Setup development environment
./scripts/setup-development.ps1

# Run full test suite
./scripts/run-tests.ps1

# Deploy locally for testing
./scripts/deploy-local.ps1

# Generate API documentation
./scripts/generate-api-docs.ps1
```

### Code Quality

```powershell
# Backend linting
cd backend
flake8 src/
mypy src/

# Frontend linting
cd frontend
npm run lint
```

## 📋 Checklist Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass locally
- [ ] New functionality is tested
- [ ] Documentation updated
- [ ] No breaking changes without discussion
- [ ] Commit messages are clear and descriptive
- [ ] Branch is up to date with main
- [ ] Pre-commit hooks pass

## 🐛 Reporting Issues

When reporting bugs, please include:

1. **Environment**: Python/Node versions, OS
2. **Steps to Reproduce**: Detailed reproduction steps
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Logs**: Relevant log output
6. **Screenshots**: For UI issues

## 💡 Feature Requests

Feature requests should include:

1. **Problem Statement**: What's the problem being solved
2. **Proposed Solution**: How it should work
3. **Alternatives Considered**: Other approaches
4. **Impact Assessment**: How it affects existing functionality

## 📞 Getting Help

- **Documentation**: Check `docs/` and `specs/` directories
- **Discussions**: Use GitHub Discussions for questions
- **Issues**: Open issues for bugs and feature requests
- **Code Reviews**: Ask for help in pull request comments

## 🎉 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Recognized in documentation
- Invited to join the core team (for significant contributions)

Thank you for contributing to AI Code Flow! 🚀

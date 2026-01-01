<!-- Sync Impact Report:
Version change: 1.2.0 → 1.3.0
Added sections: New Article VI - Stability & Timeouts
Modified principles: Added stability and timeout controls for API calls, tests, and frontend
Added sections: API timeout requirements, test execution limits, frontend circuit breaker
Removed sections: none
Templates requiring updates: none (new principle aligns with existing templates)
Follow-up TODOs: none
-->

# AI Code Flow Constitution

## Core Principles

### I. 运行时环境锁死与隔离 (Runtime Locking & Isolation)

1.  **Node.js (Frontend)**:

    -   **版本锁死**: 强制使用 **Node.js v20 (LTS)**。

    -   **Windows 适配**:

        -   所有 npm scripts 必须兼容 Windows PowerShell/CMD。

        -   使用 `cross-env` 设置环境变量，使用 `rimraf` 删除文件，严禁使用 `rm -rf` 或 `export`。

    -   **局部执行**: 严禁全局安装，仅通过 `npm run` 调用局部工具。

2.  **Python (Backend)**:

    -   **版本锁死**: 强制使用 **Python 3.11 (Stable)**。

    -   **Windows 适配**:

        -   虚拟环境激活路径需兼容 Windows: `backend\.venv\Scripts\activate`。

        -   文件路径操作必须使用 `pathlib.Path` 以自动处理分隔符 (`\` vs `/`)。

        -   **编码强制**: 所有文件读写 (`open()`) 必须显式指定 `encoding='utf-8'`，严禁依赖系统默认编码 (GBK)。

    -   **依赖锁死**: `requirements.txt` 版本固定。

3.  **[CRITICAL] 命令执行铁律 (Execution Protocol)**:

    -   **禁止隐式调用**: 严禁在脚本或终端中直接使用 `python`, `pip`, `uvicorn` 等全局命令别名。

    -   **强制绝对路径**:

        -   Windows: 必须使用 `backend\.venv\Scripts\python.exe`。

        -   Linux/Mac: 必须使用 `backend/.venv/bin/python`。

    -   **脚本合规**: 所有自动化脚本内部必须检测并使用上述绝对路径来启动子进程。若检测到非虚拟环境执行，直接终止程序。

### II. 语言与交互规范 (Language & Interaction)
**技术层 (Technical)**: 所有源码、变量名、注释必须使用英文。

**用户层 (User Face)**: 所有 UI 界面、错误反馈、操作引导必须使用简体中文。

### III. 极简接口原则 (Minimalist API Philosophy)
API 仅保留业务必需接口。后端必须捕获所有异常并返回包含中文 `message` 的 JSON，严禁暴露原始堆栈。

### IV. 质量红线 - 双重测试验证 (Testing & Verification)
后端必须通过基于 `pytest` 的真实 API 集成测试。核心链路必须通过 E2E 测试 (Playwright/Selenium)。伪代码零容忍，交付即通过测试。

### V. 状态管理规范 (State Management)
业务状态优先存储于前端 (localStorage/Zustand)。后端设计为 Stateless，随时可重启。

### VI. 稳定性与超时控制 (Stability & Timeouts)

1.  **API 超时**: 所有外部 API 调用（如 MiniMax/OpenAI）必须显式设置 `timeout` 参数（建议 30-60秒）。

2.  **测试超时**: 所有自动化测试脚本必须包含执行时间上限，防止 CI/CD 流水线卡死。

3.  **前端熔断**: 前端 `fetch` 请求超过预定时间（如 120秒）无响应时，必须自动中断并提示用户重试。

## Additional Constraints

Technology stack locked to Node.js v20 (LTS) for frontend and Python 3.11 for backend. All dependencies must specify exact versions. Environment isolation mandatory - no global package pollution.

## Development Workflow

All development must adhere to runtime locking and isolation principles. Code reviews must verify environment compliance. Testing gates required before any deployment. Amendments to constitution require technical validation and migration planning.

## Governance

Constitution supersedes all other practices. All PRs/reviews must verify compliance with runtime locking, language standards, and testing requirements. Complexity must be justified against minimalist principles. Constitution amendments require documentation, approval, and migration plan. Version follows semantic versioning with major changes requiring full compliance review.

**Version**: 1.3.0 | **Ratified**: 2025-12-31 | **Last Amended**: 2026-01-01

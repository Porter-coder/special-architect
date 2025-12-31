<!-- Sync Impact Report:
Version change: none → 1.0.0
Added sections: AI Code Flow constitution with 5 core principles
Modified principles: All 5 principles added
Added sections: Runtime environment isolation, language standards, API design, testing requirements, state management
Removed sections: none
Templates requiring updates: none (constitution principles align with existing templates)
Follow-up TODOs: none
-->

# AI Code Flow Constitution

## Core Principles

### I. 运行时环境锁死与隔离 (Runtime Locking & Isolation)
**Node.js (Frontend)**: 强制使用 Node.js v20 (LTS)。必须在根目录创建 `.nvmrc` (内容: `v20`) 和 `.node-version` (内容: `20`)。`frontend/package.json` 必须包含 `"engines": { "node": ">=20.0.0 <21.0.0", "npm": ">=10.0.0" }`。严禁使用全局安装的包，所有工具必须安装在项目的 `node_modules` 中，仅通过 `npm run` 或 `npx` 调用。

**Python (Backend)**: 强制使用 Python 3.11 (Stable)。必须在 `backend/` 下创建 `.venv`。严禁直接使用系统 `python` 命令，脚本和开发文档必须明确指示使用虚拟环境解释器路径。所有依赖必须在 `requirements.txt` 中指定明确的版本号，禁止使用 `*` 或宽泛范围。

### II. 语言与交互规范 (Language & Interaction)
**技术层 (Technical)**: 所有源码、变量名、注释必须使用英文。

**用户层 (User Face)**: 所有 UI 界面、错误反馈、操作引导必须使用简体中文。

### III. 极简接口原则 (Minimalist API Philosophy)
API 仅保留业务必需接口。后端必须捕获所有异常并返回包含中文 `message` 的 JSON，严禁暴露原始堆栈。

### IV. 质量红线 - 双重测试验证 (Testing & Verification)
后端必须通过基于 `pytest` 的真实 API 集成测试。核心链路必须通过 E2E 测试 (Playwright/Selenium)。伪代码零容忍，交付即通过测试。

### V. 状态管理规范 (State Management)
业务状态优先存储于前端 (localStorage/Zustand)。后端设计为 Stateless，随时可重启。

## Additional Constraints

Technology stack locked to Node.js v20 (LTS) for frontend and Python 3.11 for backend. All dependencies must specify exact versions. Environment isolation mandatory - no global package pollution.

## Development Workflow

All development must adhere to runtime locking and isolation principles. Code reviews must verify environment compliance. Testing gates required before any deployment. Amendments to constitution require technical validation and migration planning.

## Governance

Constitution supersedes all other practices. All PRs/reviews must verify compliance with runtime locking, language standards, and testing requirements. Complexity must be justified against minimalist principles. Constitution amendments require documentation, approval, and migration plan. Version follows semantic versioning with major changes requiring full compliance review.

**Version**: 1.0.0 | **Ratified**: 2025-12-31 | **Last Amended**: 2025-12-31

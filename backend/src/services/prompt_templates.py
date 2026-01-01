"""
Prompt Templates Service

Provides extensible prompt templates for different application categories and technologies.
Supports dynamic prompt generation based on detected requirements.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from ..logging_config import get_logger

logger = get_logger()


class PromptPhase(Enum):
    """Different phases of code generation that need prompts."""
    SPECIFY = "specify"
    PLAN = "plan"
    IMPLEMENT = "implement"


@dataclass
class PromptTemplate:
    """Template for generating prompts."""
    template: str
    variables: List[str]
    description: str


class PromptTemplates:
    """Service for managing prompt templates for different application types."""

    def __init__(self):
        self.templates = self._build_templates()
        self.technology_prompts = self._build_technology_prompts()

    def _build_templates(self) -> Dict[str, Dict[str, PromptTemplate]]:
        """Build prompt templates for different application types and phases."""
        return {
            "web_app": {
                PromptPhase.SPECIFY.value: PromptTemplate(
                    template="""分析用户需求并制定详细的技术规格。

用户需求：{user_request}

请分析这个Web应用需求，包括：
1. 功能需求和技术特性
2. 用户界面和交互设计
3. 数据结构和API设计
4. 安全性和性能要求
5. 部署和运维考虑

请用中文详细说明技术规格。""",
                    variables=["user_request"],
                    description="Web应用需求分析模板"
                ),
                PromptPhase.PLAN.value: PromptTemplate(
                    template="""基于技术规格制定详细的实现计划。

技术规格：
{spec_content}

技术栈：
{technologies}

请制定详细的实现计划，包括：
1. 项目结构和文件组织
2. 前后端分离架构设计
3. 数据库设计和API规划
4. 关键组件和模块划分
5. 开发阶段和里程碑
6. 测试策略和部署计划

请用中文提供完整的实现计划。""",
                    variables=["spec_content", "technologies"],
                    description="Web应用实现计划模板"
                ),
                PromptPhase.IMPLEMENT.value: PromptTemplate(
                    template="""基于实现计划生成完整的、可运行的单文件代码。

实现计划：
{plan_content}

技术栈：{technologies}
依赖包：{dependencies}

CRITICAL SINGLE-FILE CONSTRAINT:
===============================
- 生成的代码必须且只能包含一个文件：main.py
- 严禁生成任何其他.py文件（如utils.py, config.py, models.py等）
- 所有类、函数、配置必须全部内联到main.py中
- 严禁使用任何本地模块导入语句（如from utils import helper）
- 代码必须完全自包含、可直接运行

请生成完整的、可运行的代码，包括：
1. 完整的后端API服务（使用FastAPI）
2. 所有必要的辅助函数和类（全部内联）
3. 数据模型和业务逻辑（全部内联）
4. 配置和常量（全部内联）

代码要符合Python最佳实践，确保可直接运行。请用中文注释说明关键部分。""",
                    variables=["plan_content", "technologies", "dependencies"],
                    description="Web应用代码生成模板"
                )
            },

            "game": {
                PromptPhase.SPECIFY.value: PromptTemplate(
                    template="""分析游戏需求并制定详细的技术规格。

用户需求：{user_request}

请分析这个游戏需求，包括：
1. 游戏类型和核心机制
2. 玩家交互和控制方式
3. 视觉效果和音效设计
4. 难度平衡和进度系统
5. 技术实现的可行性

请用中文详细说明游戏规格。""",
                    variables=["user_request"],
                    description="游戏需求分析模板"
                ),
                PromptPhase.PLAN.value: PromptTemplate(
                    template="""基于游戏规格制定详细的实现计划。

游戏规格：
{spec_content}

游戏引擎：{technologies}

请制定详细的实现计划，包括：
1. 游戏循环和状态管理
2. 精灵系统和碰撞检测
3. 关卡设计和难度递进
4. 音效和视觉效果
5. 分数系统和保存机制
6. 代码结构和模块划分

请用中文提供完整的游戏实现计划。""",
                    variables=["spec_content", "technologies"],
                    description="游戏实现计划模板"
                ),
                PromptPhase.IMPLEMENT.value: PromptTemplate(
                    template="""基于实现计划生成完整的、可运行的单文件游戏代码。

实现计划：
{plan_content}

游戏库：{technologies}
依赖包：{dependencies}

CRITICAL SINGLE-FILE CONSTRAINT:
===============================
- 生成的代码必须且只能包含一个文件：main.py
- 严禁生成任何其他.py文件（如game_logic.py, config.py, sprites.py等）
- 所有游戏类、函数、配置必须全部内联到main.py中
- 严禁使用任何本地模块导入语句（如from game_logic import update）
- 代码必须完全自包含、可直接运行

请生成完整的、可运行的游戏代码，包括：
1. 游戏主循环和初始化（全部内联）
2. 玩家控制和游戏逻辑（全部内联）
3. 图形渲染和动画效果（全部内联）
4. 碰撞检测和物理效果（全部内联）
5. 分数统计和游戏结束处理（全部内联）
6. 完整的游戏体验

代码要使用Pygame等游戏库，确保游戏可以正常运行。请用中文注释说明游戏逻辑。""",
                    variables=["plan_content", "technologies", "dependencies"],
                    description="游戏代码生成模板"
                )
            },

            "data_processing": {
                PromptPhase.SPECIFY.value: PromptTemplate(
                    template="""分析数据处理需求并制定详细的技术规格。

用户需求：{user_request}

请分析这个数据处理需求，包括：
1. 数据输入输出格式和来源
2. 处理算法和数据转换逻辑
3. 性能要求和数据量估算
4. 错误处理和数据验证
5. 可视化和结果展示

请用中文详细说明数据处理规格。""",
                    variables=["user_request"],
                    description="数据处理需求分析模板"
                ),
                PromptPhase.PLAN.value: PromptTemplate(
                    template="""基于数据处理规格制定详细的实现计划。

数据处理规格：
{spec_content}

数据工具：{technologies}

请制定详细的实现计划，包括：
1. 数据管道和处理流程
2. 数据结构设计和内存管理
3. 算法选择和优化策略
4. 输入输出接口设计
5. 错误处理和异常管理
6. 性能监控和优化方案

请用中文提供完整的数据处理实现计划。""",
                    variables=["spec_content", "technologies"],
                    description="数据处理实现计划模板"
                ),
                PromptPhase.IMPLEMENT.value: PromptTemplate(
                    template="""基于实现计划生成完整的、可运行的单文件数据处理代码。

实现计划：
{plan_content}

数据工具：{technologies}
依赖包：{dependencies}

CRITICAL SINGLE-FILE CONSTRAINT:
===============================
- 生成的代码必须且只能包含一个文件：main.py
- 严禁生成任何其他.py文件（如data_utils.py, config.py, processors.py等）
- 所有数据处理函数、类、配置必须全部内联到main.py中
- 严禁使用任何本地模块导入语句（如from data_utils import load_data）
- 代码必须完全自包含、可直接运行

请生成完整的、可运行的数据处理代码，包括：
1. 数据加载和预处理函数（全部内联）
2. 核心处理算法实现（全部内联）
3. 数据验证和错误处理（全部内联）
4. 结果输出和格式化（全部内联）
5. 性能优化和内存管理（全部内联）
6. 命令行接口或API接口（全部内联）

代码要使用pandas、numpy等数据处理库，确保处理逻辑正确。请用中文注释说明算法实现。""",
                    variables=["plan_content", "technologies", "dependencies"],
                    description="数据处理代码生成模板"
                )
            },

            "utility": {
                PromptPhase.SPECIFY.value: PromptTemplate(
                    template="""分析工具需求并制定详细的技术规格。

用户需求：{user_request}

请分析这个工具需求，包括：
1. 工具功能和使用场景
2. 输入输出格式和参数设计
3. 用户界面和交互方式
4. 错误处理和边界情况
5. 跨平台兼容性要求

请用中文详细说明工具规格。""",
                    variables=["user_request"],
                    description="工具需求分析模板"
                ),
                PromptPhase.PLAN.value: PromptTemplate(
                    template="""基于工具规格制定详细的实现计划。

工具规格：
{spec_content}

工具库：{technologies}

请制定详细的实现计划，包括：
1. 命令行参数解析和验证
2. 核心功能模块设计
3. 文件I/O和数据处理
4. 错误处理和用户反馈
5. 配置管理和帮助系统
6. 测试用例和边界条件

请用中文提供完整的工具实现计划。""",
                    variables=["spec_content", "technologies"],
                    description="工具实现计划模板"
                ),
                PromptPhase.IMPLEMENT.value: PromptTemplate(
                    template="""基于实现计划生成完整的、可运行的单文件工具代码。

实现计划：
{plan_content}

工具库：{technologies}
依赖包：{dependencies}

CRITICAL SINGLE-FILE CONSTRAINT:
===============================
- 生成的代码必须且只能包含一个文件：main.py
- 严禁生成任何其他.py文件（如cli_utils.py, config.py, handlers.py等）
- 所有工具函数、类、配置必须全部内联到main.py中
- 严禁使用任何本地模块导入语句（如from cli_utils import parse_args）
- 代码必须完全自包含、可直接运行

请生成完整的、可运行的工具代码，包括：
1. 命令行参数解析和帮助（全部内联）
2. 核心功能实现（全部内联）
3. 文件操作和数据处理（全部内联）
4. 错误处理和用户提示（全部内联）
5. 配置管理和日志记录（全部内联）
6. 完整的命令行工具体验

代码要使用click、rich等工具库，确保工具易用且稳定。请用中文注释说明功能实现。""",
                    variables=["plan_content", "technologies", "dependencies"],
                    description="工具代码生成模板"
                )
            },

            "educational": {
                PromptPhase.SPECIFY.value: PromptTemplate(
                    template="""分析教学需求并制定详细的技术规格。

用户需求：{user_request}

请分析这个教学需求，包括：
1. 教学目标和学习内容
2. 交互式学习体验设计
3. 视觉化教学元素
4. 难度分级和进度跟踪
5. 教学反馈和评估机制

请用中文详细说明教学规格。""",
                    variables=["user_request"],
                    description="教学需求分析模板"
                ),
                PromptPhase.PLAN.value: PromptTemplate(
                    template="""基于教学规格制定详细的实现计划。

教学规格：
{spec_content}

教学工具：{technologies}

请制定详细的实现计划，包括：
1. 教学内容结构和流程
2. 交互式学习组件设计
3. 视觉化展示和动画效果
4. 学习进度跟踪系统
5. 教学评估和反馈机制
6. 代码结构和模块组织

请用中文提供完整的教学实现计划。""",
                    variables=["spec_content", "technologies"],
                    description="教学实现计划模板"
                ),
                PromptPhase.IMPLEMENT.value: PromptTemplate(
                    template="""基于实现计划生成完整的教学代码。

实现计划：
{plan_content}

教学工具：{technologies}
依赖包：{dependencies}

请生成完整的、可运行的教学代码，包括：
1. 教学内容展示和导航
2. 交互式学习组件
3. 视觉化教学演示
4. 学习进度跟踪
5. 教学评估和反馈
6. 完整的学习体验

代码要易于理解和修改，适合教学用途。请用中文注释详细说明教学逻辑。""",
                    variables=["plan_content", "technologies", "dependencies"],
                    description="教学代码生成模板"
                )
            }
        }

    def _build_technology_prompts(self) -> Dict[str, str]:
        """Build technology-specific prompt additions."""
        return {
            "pygame": "使用Pygame游戏库，包含游戏循环、事件处理、图形渲染等核心功能。",
            "pandas": "使用pandas进行数据处理，包含DataFrame操作、数据清洗、统计分析等功能。",
            "fastapi": "使用FastAPI构建Web API，包含路由定义、请求响应处理、数据验证等功能。",
            "click": "使用Click构建命令行工具，包含参数解析、命令分组、帮助信息等功能。",
            "turtle": "使用turtle绘图库创建图形化教学示例，包含基本绘图和动画功能。"
        }

    def get_prompt(self, app_type: str, phase: PromptPhase,
                   variables: Dict[str, Any]) -> Optional[str]:
        """
        Get a formatted prompt for the specified application type and phase.

        Args:
            app_type: Application type (e.g., "web_app", "game")
            phase: Generation phase
            variables: Variables to substitute in the template

        Returns:
            Formatted prompt string or None if template not found
        """
        try:
            template = self.templates.get(app_type, {}).get(phase.value)
            if not template:
                logger.warning(f"No template found for {app_type}.{phase.value}, using generic template")
                # Fallback to generic template based on phase
                prompt = self._generate_generic_prompt(app_type, phase, variables)
            else:
                # Format the template with provided variables
                prompt = template.template.format(**variables)

            # Add technology-specific guidance if available
            tech_additions = []
            technologies = variables.get("technologies", "")
            if technologies:
                for tech_name, addition in self.technology_prompts.items():
                    if tech_name in technologies.lower():
                        tech_additions.append(addition)

            if tech_additions:
                prompt += "\n\n技术要求：\n" + "\n".join(tech_additions)

            # Add self-containment constraints for robust delivery
            prompt += """

CRITICAL DELIVERY CONSTRAINTS:
==============================
SINGLE-FILE ONLY: Generate EXACTLY ONE file named 'main.py'. NO other .py files.
SELF-CONTAINED: ALL code must be in main.py. NO local imports like 'from config import' or 'import utils'.
CONTENT ACCURACY: Generate code that matches the user's request EXACTLY. If user asks for "numpy arrays", generate numpy code ONLY - NO snake games, NO pygame, NO unrelated code.
SYNTAX PERFECTION: Code MUST be syntactically perfect Python. NO unterminated strings, NO syntax errors, NO invalid characters.

CRITICAL RULE: YOU CANNOT IMPORT A LOCAL MODULE UNLESS YOU GENERATE IT AS PART OF main.py.
If you need helper functions, DEFINE THEM INLINE in main.py.
NO PLACEHOLDERS. NO ASSUMPTIONS. COMPLETE CODE ONLY.

STABILITY RULE - PREVENT CODE TRUNCATION:
========================================
To prevent code truncation (cutoff) that causes syntax errors:
- DO NOT hardcode large datasets (e.g., NO long CSV/JSON strings in code)
- MUST use Python code to generate mock data (e.g., import random, np.random, or loops)
- For data processing: Generate sample data programmatically, don't embed it
- Keep code length manageable to avoid token limit truncation

Example data generation patterns:
- ✅ data = [random.randint(1, 100) for _ in range(50)]  # Good
- ✅ df = pd.DataFrame({{'x': np.random.randn(100), 'y': np.random.randn(100)}})  # Good
- ❌ data = 'name,age,city\\nJohn,25,NYC\\nJane,30,LA\\n...'  # BAD - long string
- ❌ json_data = '{{"users": [{{"id": 1, "name": "John"}}, ...]}}'  # BAD - long string

SYNTAX REQUIREMENTS:
- All strings must be properly quoted and terminated
- All parentheses, brackets, braces must be balanced
- All Python syntax must be valid and parseable
- NO Chinese punctuation (use standard ASCII: , . : ; " ' ( ) [ ] {{ }})
- Code must pass Python AST parsing without errors

Examples of what NOT to do:
- ❌ import config  # Local module not generated
- ❌ from utils import helper  # Local module not generated
- ❌ Snake game code when user asks for numpy  # Wrong content
- ❌ Pygame code when user asks for data analysis  # Wrong content
- ❌ print("hello  # Unterminated string
- ❌ def func(  # Unbalanced parentheses
- ❌ print("hello，world")  # Chinese comma instead of standard comma
- ❌ Long hardcoded CSV strings that cause truncation

Examples of what TO do:
- ✅ Define all functions/classes directly in main.py
- ✅ Use only standard library + requested third-party packages
- ✅ Generate content that exactly matches user request
- ✅ print("hello, world")  # Proper ASCII punctuation
- ✅ def func(): pass  # Balanced syntax
- ✅ Generate data programmatically with random/numpy"""

            return prompt

        except KeyError as e:
            logger.error(f"Missing variable in prompt template: {e}")
            return None
        except Exception as e:
            logger.error(f"Error generating prompt: {e}")
            return None

    def get_supported_types(self) -> List[str]:
        """Get list of supported application types."""
        return list(self.templates.keys())

    def _generate_generic_prompt(self, app_type: str, phase: PromptPhase, variables: Dict[str, Any]) -> str:
        """
        Generate a generic prompt when no specific template exists.
        Uses the user's actual request to create relevant content.
        """
        user_request = variables.get("user_request", "")
        technologies = variables.get("technologies", "")
        dependencies = variables.get("dependencies", "")

        base_constraints = """

CRITICAL DELIVERY CONSTRAINTS:
==============================
SINGLE-FILE ONLY: Generate EXACTLY ONE file named 'main.py'. NO other .py files.
SELF-CONTAINED: ALL code must be in main.py. NO local imports like 'from config import' or 'import utils'.
CONTENT ACCURACY: Generate code that matches the user's request EXACTLY: "{user_request}"

CRITICAL RULE: YOU CANNOT IMPORT A LOCAL MODULE UNLESS YOU GENERATE IT AS PART OF main.py.
If you need helper functions, DEFINE THEM INLINE in main.py.
NO PLACEHOLDERS. NO ASSUMPTIONS. COMPLETE CODE ONLY.

DO NOT generate snake games, pygame code, or any other content unless specifically requested by the user."""

        if phase == PromptPhase.SPECIFY:
            return f"""分析用户需求并制定详细的技术规格。

用户需求：{user_request}

请分析这个{app_type}需求，包括：
1. 功能需求和技术特性
2. 用户界面和交互设计
3. 数据结构和API设计
4. 安全性和性能要求
5. 部署和运维考虑

请用中文详细说明技术规格。{base_constraints}"""

        elif phase == PromptPhase.PLAN:
            spec_content = variables.get("spec_content", "")
            return f"""基于技术规格制定详细的实现计划。

技术规格：
{spec_content}

请制定详细的实现计划，包括：
1. 项目结构和文件组织（记住：只能是单个main.py文件）
2. 核心功能模块设计（全部内联在main.py中）
3. 数据处理和存储方案
4. 错误处理和边界情况
5. 测试策略和部署计划

请用中文提供完整的实现计划。{base_constraints}"""

        elif phase == PromptPhase.IMPLEMENT:
            plan_content = variables.get("plan_content", "")
            return f"""基于实现计划生成完整的、可运行的单文件代码。

实现计划：
{plan_content}

技术栈：{technologies}
依赖包：{dependencies}

请生成完整的、可运行的代码：
1. 完整的应用程序逻辑（全部内联在main.py中）
2. 所有必要的辅助函数和类（全部内联）
3. 数据模型和业务逻辑（全部内联）
4. 错误处理和用户界面（全部内联）

代码要符合最佳实践，确保可直接运行。请用中文注释说明关键部分。

{base_constraints}

IMPORTANT: Generate code that EXACTLY matches: "{user_request}". Do NOT generate snake games or pygame code unless the user specifically requests it."""

        else:
            return f"Generate content for {app_type} {phase.value} phase based on: {user_request}{base_constraints}"

    def get_template_info(self, app_type: str, phase: PromptPhase) -> Optional[Dict]:
        """Get information about a specific template."""
        template = self.templates.get(app_type, {}).get(phase.value)
        if not template:
            return None

        return {
            "description": template.description,
            "variables": template.variables,
            "template_length": len(template.template)
        }

    def add_template(self, app_type: str, phase: PromptPhase, template: PromptTemplate):
        """Add a new prompt template."""
        if app_type not in self.templates:
            self.templates[app_type] = {}

        self.templates[app_type][phase.value] = template
        logger.info(f"Added template for {app_type}.{phase.value}")

    def update_technology_prompt(self, technology: str, prompt: str):
        """Update technology-specific prompt addition."""
        self.technology_prompts[technology] = prompt
        logger.info(f"Updated technology prompt for {technology}")

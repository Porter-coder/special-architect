"""
Phase Manager Service

Manages the three-phase educational workflow (Specify → Plan → Implement)
with real-time progress tracking and Chinese educational messages.
"""

from typing import AsyncGenerator, Dict, List, Optional
from uuid import UUID

from ..logging_config import get_logger
from ..models.process_phase import PhaseName, ProcessPhase, get_phase_message
from .ai_service import AIService, AIServiceError

logger = get_logger()


class PhaseManagerError(Exception):
    """Base exception for phase manager errors."""
    pass


class PhaseManager:
    """
    Manages the three-phase code generation workflow.

    Handles:
    - Phase execution coordination
    - Educational message generation
    - Progress tracking and streaming
    - Error handling and recovery
    """

    def __init__(self, ai_service: Optional[AIService] = None):
        """
        Initialize phase manager.

        Args:
            ai_service: AI service instance (optional)
        """
        self.ai_service = ai_service
        logger.info("Phase manager initialized")

    async def execute_phase(
        self,
        user_request: str,
        phase: PhaseName,
        context: Optional[Dict] = None
    ) -> str:
        """
        Execute a specific development phase.

        Args:
            user_request: Original user request
            phase: Phase to execute
            context: Optional context from previous phases

        Returns:
            Phase output content

        Raises:
            PhaseManagerError: If phase execution fails
        """
        try:
            logger.info(f"Executing phase: {phase.value}")

            # Get phase-specific prompt
            prompt = self._create_phase_prompt(user_request, phase, context)

            # Execute phase using AI service
            if not self.ai_service:
                raise PhaseManagerError("AI service not available")

            # Collect streaming output
            full_output = ""
            async for chunk in self.ai_service.generate_code_stream(user_request, phase):
                if chunk.get('type') == 'text':
                    full_output += chunk.get('content', '')

            if not full_output.strip():
                raise PhaseManagerError(f"Phase {phase.value} produced no output")

            logger.info(f"Phase {phase.value} completed successfully")
            return full_output.strip()

        except AIServiceError as e:
            logger.error(f"AI service error in phase {phase.value}: {e}")
            raise PhaseManagerError(f"AI 服务错误: {e}")
        except Exception as e:
            logger.error(f"Phase execution error: {e}")
            raise PhaseManagerError(f"阶段执行失败: {e}")

    async def execute_workflow(
        self,
        user_request: str,
        progress_callback: Optional[callable] = None
    ) -> AsyncGenerator[Dict, None]:
        """
        Execute the complete three-phase workflow.

        Args:
            user_request: Original user request
            progress_callback: Optional callback for progress updates

        Yields:
            Progress updates and phase results
        """
        from ..models.process_phase import PHASE_ORDER

        context = {}
        phases_completed = []

        for phase in PHASE_ORDER:
            try:
                # Send phase start event
                phase_message = get_phase_message(phase)
                yield {
                    "type": "phase_start",
                    "phase": phase.value,
                    "message": phase_message
                }

                if progress_callback:
                    progress_callback(f"开始{phase.value}阶段...")

                # Execute phase
                result = await self.execute_phase(user_request, phase, context)

                # Update context for next phase
                context[phase.value] = result
                phases_completed.append(phase)

                # Send phase completion event
                yield {
                    "type": "phase_complete",
                    "phase": phase.value,
                    "result": result[:500] + "..." if len(result) > 500 else result
                }

                if progress_callback:
                    progress_callback(f"{phase.value}阶段完成")

            except Exception as e:
                logger.error(f"Workflow failed at phase {phase.value}: {e}")
                yield {
                    "type": "phase_error",
                    "phase": phase.value,
                    "error": str(e)
                }
                break

        # Send workflow completion
        if len(phases_completed) == len(PHASE_ORDER):
            yield {
                "type": "workflow_complete",
                "message": "所有阶段执行完成"
            }
        else:
            yield {
                "type": "workflow_failed",
                "completed_phases": [p.value for p in phases_completed],
                "message": "工作流执行失败"
            }

    def _create_phase_prompt(self, user_request: str, phase: PhaseName, context: Optional[Dict] = None) -> str:
        """
        Create phase-specific prompt for AI generation.

        Args:
            user_request: Original user request
            phase: Current phase
            context: Context from previous phases

        Returns:
            Formatted prompt for the phase
        """
        context = context or {}

        if phase == PhaseName.SPECIFY:
            return f"""请分析用户的需求，将自然语言转换为技术规格说明。

用户需求：{user_request}

请按照以下格式输出：
## 功能需求
- 列出核心功能点

## 技术要求
- 列出技术约束和要求

## 边界条件
- 明确功能边界和限制

请详细分析用户意图，确保规格说明清晰可执行。"""

        elif phase == PhaseName.PLAN:
            specify_output = context.get('specify', '')
            return f"""基于需求分析，制定详细的技术实现方案。

用户原始需求：{user_request}

需求分析结果：
{specify_output}

请制定以下方面的技术方案：
## 技术栈选择
- 编程语言和框架

## 系统架构
- 组件设计和数据流

## 实现步骤
- 分步开发计划

## 依赖管理
- 所需的库和工具

请提供具体、可操作的技术方案。"""

        elif phase == PhaseName.IMPLEMENT:
            specify_output = context.get('specify', '')
            plan_output = context.get('plan', '')

            return f"""基于需求分析和技术方案，生成完整的、可执行的代码。

用户原始需求：{user_request}

需求分析：
{specify_output}

技术方案：
{plan_output}

请生成：
1. 完整的源代码文件
2. 清晰的代码结构
3. 适当的注释和文档
4. 可直接运行的程序

确保代码：
- 语法正确
- 逻辑完整
- 包含错误处理
- 符合最佳实践

请用 ```python 开始和结束代码块。"""

        else:
            raise PhaseManagerError(f"Unknown phase: {phase}")

    def get_phase_status(self, phase: PhaseName) -> Dict:
        """
        Get status information for a phase.

        Args:
            phase: Phase to check

        Returns:
            Status dictionary
        """
        return {
            "phase": phase.value,
            "educational_message": get_phase_message(phase),
            "is_required": True,
            "estimated_duration": self._get_phase_duration_estimate(phase)
        }

    def _get_phase_duration_estimate(self, phase: PhaseName) -> str:
        """Get estimated duration for a phase."""
        estimates = {
            PhaseName.SPECIFY: "10-20秒",
            PhaseName.PLAN: "15-30秒",
            PhaseName.IMPLEMENT: "30-60秒"
        }
        return estimates.get(phase, "未知")

    def validate_workflow_result(self, results: Dict[str, str]) -> List[str]:
        """
        Validate the results of a complete workflow.

        Args:
            results: Dictionary mapping phase names to outputs

        Returns:
            List of validation issues (empty if valid)
        """
        issues = []

        required_phases = ['specify', 'plan', 'implement']
        for phase in required_phases:
            if phase not in results:
                issues.append(f"缺少{phase}阶段的输出")
            elif not results[phase].strip():
                issues.append(f"{phase}阶段输出为空")

        # Check for code in implement phase
        if 'implement' in results:
            implement_output = results['implement']
            if '```python' not in implement_output and '```' not in implement_output:
                issues.append("实现阶段未检测到代码块")

        return issues

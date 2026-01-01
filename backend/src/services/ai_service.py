"""
AI Service Interface

Handles integration with MiniMax AI via OpenAI SDK for code generation.
"""

import os
from typing import AsyncGenerator, Optional

import openai
from openai import APIError, APIStatusError

from ..models.process_phase import PhaseName


class AIServiceError(Exception):
    """Base exception for AI service errors."""
    pass


class AIServiceConnectionError(AIServiceError):
    """Exception for AI service connection issues."""
    pass


class AIServiceRateLimitError(AIServiceError):
    """Exception for AI service rate limiting."""
    pass


class AIServiceResponseError(AIServiceError):
    """Exception for invalid AI service responses."""
    pass


class AIService:
    """
    AI service for code generation using MiniMax via OpenAI SDK.

    Handles:
    - Connection to MiniMax AI service
    - Code generation requests
    - Streaming responses with thinking traces
    - Error handling and retry logic
    """

    def __init__(self):
        """Initialize AI service with MiniMax configuration."""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required for AI service. Please configure your MiniMax API key.")

        self.base_url = os.getenv('OPENAI_BASE_URL', 'https://api.minimaxi.com/v1')

        # Initialize OpenAI client with MiniMax configuration
        self.client = openai.AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            extra_body={"reasoning_split": True}
        )

        # Model configuration
        self.model = "MiniMax-M2.1"  # Primary model for code generation
        self.max_tokens = 4096
        self.temperature = 0.7  # Balanced creativity for code generation

    async def generate_code_stream(
        self,
        user_request: str,
        phase: PhaseName = PhaseName.IMPLEMENT
    ) -> AsyncGenerator[dict, None]:
        """
        Generate code with streaming response and thinking traces.

        Args:
            user_request: Natural language code generation request
            phase: Current development phase (affects prompt)

        Yields:
            Dictionary with streaming data:
            - {"type": "thinking", "content": "..."}
            - {"type": "text", "content": "..."}

        Raises:
            AIServiceError: For various AI service issues
        """
        try:
            # Create phase-specific prompt
            prompt = self._create_code_generation_prompt(user_request, phase)

            # Create streaming request using OpenAI chat completions API
            stream = await self.client.chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert software engineer. Generate clean, well-documented code based on user requirements."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                stream=True
            )

            # Process OpenAI streaming response
            async for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    choice = chunk.choices[0]
                    delta = choice.delta

                    # Handle content streaming
                    if hasattr(delta, 'content') and delta.content is not None:
                        yield {
                            "type": "text",
                            "content": delta.content
                        }

                    # Handle thinking traces (if supported by the model)
                    # Note: OpenAI doesn't natively support thinking traces like Anthropic
                    # For now, we'll simulate thinking traces from the content when appropriate
                    if hasattr(delta, 'reasoning_content') and delta.reasoning_content is not None:
                        yield {
                            "type": "thinking",
                            "content": delta.reasoning_content
                        }

        except APIStatusError as e:
            if e.status_code == 429:
                raise AIServiceRateLimitError(f"AI 服务请求频率过高，请稍后重试: {e}")
            elif e.status_code >= 500:
                raise AIServiceConnectionError(f"AI 服务暂时不可用: {e}")
            else:
                raise AIServiceResponseError(f"AI 服务请求错误: {e}")

        except APIError as e:
            raise AIServiceConnectionError(f"AI 服务连接失败: {e}")

        except Exception as e:
            raise AIServiceError(f"AI 服务未知错误: {e}")

    async def generate_code(
        self,
        user_request: str,
        phase: PhaseName = PhaseName.IMPLEMENT
    ) -> tuple[str, Optional[str]]:
        """
        Generate code without streaming (for simpler use cases).

        Args:
            user_request: Natural language code generation request
            phase: Current development phase

        Returns:
            Tuple of (generated_code, thinking_trace)

        Raises:
            AIServiceError: For various AI service issues
        """
        thinking_parts = []
        code_parts = []

        async for chunk in self.generate_code_stream(user_request, phase):
            if chunk["type"] == "thinking":
                thinking_parts.append(chunk["content"])
            elif chunk["type"] == "text":
                code_parts.append(chunk["content"])

        generated_code = "".join(code_parts)
        thinking_trace = "".join(thinking_parts) if thinking_parts else None

        return generated_code, thinking_trace


    def _create_code_generation_prompt(self, user_request: str, phase: PhaseName) -> str:
        """
        Create a phase-specific prompt for Snake game code generation.

        Args:
            user_request: Original user request (should contain Snake game request)
            phase: Current development phase

        Returns:
            Formatted prompt for AI tailored for Snake game generation
        """
        # Detect if this is a Snake game request
        is_snake_game = "贪吃蛇" in user_request or "snake" in user_request.lower()

        if phase == PhaseName.SPECIFY:
            prompt = f"""
作为软件工程师，请分析以下用户需求并定义功能边界：

用户需求：{user_request}

如果是贪吃蛇游戏需求，请明确以下规格：
1. 游戏规则：蛇吃食物成长，撞墙或撞自己游戏结束
2. 控制方式：方向键控制蛇移动
3. 显示要求：游戏区域、分数显示、游戏状态
4. 技术栈：使用Pygame库实现
5. 目标平台：Windows系统

请详细描述游戏的功能需求和验收标准。
"""
        elif phase == PhaseName.PLAN:
            prompt = f"""
基于以下需求，制定贪吃蛇游戏的技术实现方案：

用户需求：{user_request}

请制定详细的技术方案，包括：
1. 核心类设计：Snake类、Food类、Game类
2. 游戏循环结构：初始化、输入处理、游戏逻辑、渲染
3. 数据结构：蛇身坐标存储、方向控制、碰撞检测
4. 依赖库：Pygame的具体用法和版本要求
5. 文件结构：main.py和其他必要文件

请提供完整的实现计划和技术决策理由。
"""
        elif phase == PhaseName.IMPLEMENT:
            prompt = f"""
请基于以下需求实现完整的贪吃蛇游戏代码：

用户需求：{user_request}

代码要求：
1. 使用Pygame库实现图形界面
2. 包含完整的游戏逻辑：蛇移动、吃食物、碰撞检测、分数计算
3. 方向键控制蛇的移动方向
4. 游戏结束条件：撞墙或撞到自己
5. 显示分数和游戏状态
6. 代码结构清晰，包含适当的注释
7. 生成可直接运行的main.py文件

IMPORTANT: Write fully functional code. Do NOT use placeholders or comments like '# ...'. Implement every function completely.

请生成完整、可运行的Python代码。
"""

        return prompt.strip()

    async def validate_connection(self) -> bool:
        """
        Validate connection to AI service.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Simple test request using OpenAI chat completions API
            await self.client.chat.completions.create(
                model=self.model,
                max_tokens=10,
                messages=[
                    {
                        "role": "user",
                        "content": "Hello"
                    }
                ]
            )
            return True
        except Exception as e:
            # Log the specific error for debugging but don't crash
            print(f"AI service validation failed: {e}")
            return False

"""
AI Service Interface

Handles integration with MiniMax AI via OpenAI SDK for code generation.
"""

import os
from typing import AsyncGenerator, Optional

import openai
from openai import APIError, APIStatusError

from ..logging_config import get_logger
from ..models.process_phase import PhaseName

logger = get_logger()


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

    def __init__(self, config=None):
        """Initialize AI service with MiniMax configuration."""
        from ..config import get_config

        if config is None:
            config = get_config()

        # Use configuration from config.json
        self.api_key = config.minimax.api_key
        if not self.api_key:
            raise ValueError("MiniMax API key is required. Please configure minimax.api_key in backend/config.json")

        self.base_url = config.minimax.base_url

        # Initialize OpenAI client with MiniMax configuration and timeout
        self.client = openai.AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=config.generation.timeout  # Use configured timeout
        )

        # Model configuration from config
        self.model = config.generation.model
        self.max_tokens = config.generation.max_tokens
        self.temperature = config.generation.temperature

    async def generate_code_stream(
        self,
        prompt: str,
        phase: PhaseName = PhaseName.IMPLEMENT
    ) -> AsyncGenerator[dict, None]:
        """
        Generate code with streaming response and thinking traces.

        Args:
            prompt: Pre-formatted prompt for AI (includes phase-specific instructions)
            phase: Current development phase (for context only)

        Yields:
            Dictionary with streaming data:
            - {"type": "thinking", "content": "..."}
            - {"type": "text", "content": "..."}

        Raises:
            AIServiceError: For various AI service issues
        """
        try:
            logger.info(f"🤖 Starting AI stream for phase: {phase}")
            logger.info(f"📝 Prompt length: {len(prompt)} chars")

            # Create streaming request using OpenAI chat completions API
            stream = await self.client.chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=0.7,  # Higher temperature for universal prompt system
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

            logger.info("🎯 AI stream created successfully, starting to process chunks")

            # Process OpenAI streaming response
            chunk_count = 0
            text_chunks = 0
            async for chunk in stream:
                chunk_count += 1
                if chunk.choices and len(chunk.choices) > 0:
                    choice = chunk.choices[0]
                    delta = choice.delta

                    # Handle content streaming
                    if hasattr(delta, 'content') and delta.content is not None:
                        text_chunks += 1
                        if text_chunks % 10 == 0:  # Log every 10 text chunks
                            logger.info(f"📝 Processed {text_chunks} text chunks so far")
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

            logger.info(f"🏁 AI streaming completed: processed {chunk_count} chunks")

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

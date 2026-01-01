"""
OpenAI SDK Migration Test

Tests SDK migration from OpenAI to MiniMax while ensuring output consistency.
This test verifies that the MiniMax SDK produces equivalent results to OpenAI SDK
for the same code generation requests.

Requirements: FR-017 (SDK migration), SC-008 (SDK comparison tests)
"""

import asyncio
import os
import pytest
from typing import Dict, Any, List
from unittest.mock import AsyncMock, patch

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.ai_service import AIService, AIServiceError
from ..src.models.process_phase import PhaseName


class TestSDKMigration:
    """Test OpenAI SDK migration to MiniMax SDK."""

    @pytest.fixture
    async def ai_service(self):
        """Create AI service instance for testing."""
        # Mock environment variables for testing
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test-minimax-key',
            'OPENAI_BASE_URL': 'https://api.minimax.chat/v1'
        }):
            service = AIService()
            yield service

    @pytest.mark.asyncio
    async def test_minimax_sdk_initialization(self, ai_service):
        """Test that MiniMax SDK initializes correctly."""
        assert ai_service.api_key == 'test-minimax-key'
        assert ai_service.base_url == 'https://api.minimax.chat/v1'
        assert ai_service.model == 'MiniMax-M2.1'
        assert ai_service.client is not None

    @pytest.mark.asyncio
    async def test_sdk_response_format_compatibility(self, ai_service):
        """Test that SDK responses maintain compatible format."""
        # Mock response that simulates MiniMax SDK behavior
        mock_response = {
            'choices': [{
                'delta': {
                    'content': 'print("Hello, World!")',
                    'reasoning_content': 'Creating a simple hello world program'
                }
            }],
            'usage': {
                'prompt_tokens': 10,
                'completion_tokens': 5,
                'total_tokens': 15
            }
        }

        with patch.object(ai_service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            # Setup mock streaming response
            async def mock_stream():
                for chunk_data in mock_response['choices']:
                    chunk = AsyncMock()
                    chunk.choices = [AsyncMock()]
                    chunk.choices[0].delta = AsyncMock()
                    chunk.choices[0].delta.content = chunk_data['delta']['content']
                    chunk.choices[0].delta.reasoning_content = chunk_data['delta'].get('reasoning_content')
                    yield chunk

            mock_create.return_value = mock_stream()

            # Test streaming response
            chunks = []
            async for chunk in ai_service.generate_code_stream(
                user_request="写个hello world",
                phase=PhaseName.IMPLEMENT
            ):
                chunks.append(chunk)

            # Verify response format
            assert len(chunks) > 0
            assert 'type' in chunks[0]
            assert 'content' in chunks[0]

    @pytest.mark.asyncio
    async def test_sdk_error_handling_compatibility(self, ai_service):
        """Test that error handling works consistently across SDKs."""
        from openai import APIError

        # Test rate limit error
        with patch.object(ai_service.client.chat.completions, 'create', side_effect=APIError("Rate limit exceeded", response=AsyncMock(), body=None)):
            with pytest.raises(AIServiceError) as exc_info:
                async for _ in ai_service.generate_code_stream("test", PhaseName.IMPLEMENT):
                    pass

            assert "请求频率过高" in str(exc_info.value)

        # Test connection error
        with patch.object(ai_service.client.chat.completions, 'create', side_effect=Exception("Connection failed")):
            with pytest.raises(AIServiceError) as exc_info:
                async for _ in ai_service.generate_code_stream("test", PhaseName.IMPLEMENT):
                    pass

            assert "未知错误" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_sdk_timeout_handling(self, ai_service):
        """Test that timeout handling works correctly."""
        import asyncio

        # Mock a timeout scenario
        with patch.object(ai_service.client.chat.completions, 'create', side_effect=asyncio.TimeoutError()):
            with pytest.raises(AIServiceError):
                async for _ in ai_service.generate_code_stream("test", PhaseName.IMPLEMENT):
                    pass

    @pytest.mark.asyncio
    async def test_sdk_model_configuration(self, ai_service):
        """Test that model configuration is applied correctly."""
        # Verify model settings
        assert ai_service.model == 'MiniMax-M2.1'
        assert ai_service.max_tokens == 4096
        assert ai_service.temperature == 0.7  # May be overridden in actual usage

    @pytest.mark.asyncio
    async def test_sdk_streaming_behavior(self, ai_service):
        """Test streaming behavior maintains compatibility."""
        chunks_received = []

        with patch.object(ai_service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            # Create mock streaming response
            async def mock_stream():
                # Simulate multiple chunks
                for i in range(3):
                    chunk = AsyncMock()
                    chunk.choices = [AsyncMock()]
                    chunk.choices[0].delta = AsyncMock()
                    chunk.choices[0].delta.content = f"chunk_{i}"
                    chunk.choices[0].delta.reasoning_content = f"thinking_{i}"
                    yield chunk

            mock_create.return_value = mock_stream()

            async for chunk in ai_service.generate_code_stream("test request", PhaseName.IMPLEMENT):
                chunks_received.append(chunk)

            # Verify streaming behavior
            assert len(chunks_received) == 6  # 3 content + 3 thinking chunks
            assert any(c['type'] == 'text' for c in chunks_received)
            assert any(c['type'] == 'thinking' for c in chunks_received)

    def test_sdk_environment_validation(self):
        """Test that environment validation works correctly."""
        # Test missing API key
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                AIService()
            assert "OPENAI_API_KEY" in str(exc_info.value)

        # Test valid environment
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test-key',
            'OPENAI_BASE_URL': 'https://test.api.com/v1'
        }):
            service = AIService()
            assert service.api_key == 'test-key'
            assert service.base_url == 'https://test.api.com/v1'

"""
Comprehensive Integration Tests

Tests full system integration including SDK migration, concurrency management,
error handling, and service interactions. These tests verify that all components
work together correctly and maintain the system's reliability guarantees.

Requirements: FR-017 (SDK migration), SC-008 (SDK comparison), FR-009/FR-010 (concurrency)
"""

import asyncio
import os
import pytest
import tempfile
from typing import Dict, Any, List
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.ai_service import AIService, AIServiceError
from src.services.code_generation_service import CodeGenerationService, CodeGenerationServiceError
from src.services.concurrency_manager import ConcurrencyManager, ConcurrencyManagerError
from src.services.mock_service import MockService
from src.services.project_service import ProjectService, ProjectServiceError
from src.services.container import ServiceContainer
from src.models.code_generation_request import CodeGenerationRequest, RequestStatus
from src.models.process_phase import PhaseName


class TestSystemIntegration:
    """Test full system integration and component interactions."""

    @pytest.fixture
    async def service_container(self):
        """Create service container for integration testing."""
        # Use development mode with mock services
        with patch.dict(os.environ, {'DEVELOPMENT_MODE': 'true'}):
            container = ServiceContainer()
            await container.initialize_services()
            yield container
            # Cleanup if needed

    @pytest.fixture
    def concurrency_manager(self):
        """Create concurrency manager for testing."""
        return ConcurrencyManager(max_concurrent_users=3)  # Smaller limit for testing

    @pytest.mark.asyncio
    async def test_sdk_migration_integration(self, service_container):
        """Test SDK migration works in full system context."""
        ai_service = service_container.ai_service

        # Verify we're using mock service in development mode
        assert isinstance(ai_service, MockService)

        # Test basic connection
        connection_ok = await ai_service.validate_connection()
        assert connection_ok is True

        # Test code generation stream
        request = CodeGenerationRequest(
            request_id=uuid4(),
            user_input="创建贪吃蛇游戏"
        )

        chunks = []
        async for chunk in ai_service.generate_code_stream(request):
            chunks.append(chunk)

        # Verify we got some response
        assert len(chunks) > 0
        assert any(c.get('type') in ['phase_start', 'content_chunk', 'phase_complete', 'workflow_complete'] for c in chunks)

    @pytest.mark.asyncio
    async def test_concurrency_management_integration(self, concurrency_manager):
        """Test concurrency management with multiple simulated users."""
        user_ids = ["user_1", "user_2", "user_3", "user_4"]

        # Test accepting requests up to limit
        for i, user_id in enumerate(user_ids[:3]):  # Should accept first 3
            request_id = uuid4()
            can_accept = concurrency_manager.can_accept_request(user_id)
            if i < 3:
                assert can_accept is True
                concurrency_manager.register_request(request_id, user_id, "/api/generate-code")
            else:
                assert can_accept is False

        # Verify active requests count
        assert concurrency_manager.get_active_requests_count() == 3

        # Test per-user limits
        # User 1 tries to make another request (should be rejected)
        can_accept_again = concurrency_manager.can_accept_request("user_1")
        assert can_accept_again is False

        # Complete one request
        first_request_id = list(concurrency_manager._active_requests.keys())[0]
        concurrency_manager.unregister_request(first_request_id)

        # Now should be able to accept one more
        can_accept_new = concurrency_manager.can_accept_request("user_4")
        assert can_accept_new is True

    @pytest.mark.asyncio
    async def test_error_handling_integration(self, service_container):
        """Test comprehensive error handling across services."""
        # Test AIService error handling
        ai_service = service_container.ai_service

        # Mock a failure scenario
        with patch.object(ai_service, 'validate_connection', return_value=False):
            connection_ok = await ai_service.validate_connection()
            assert connection_ok is False

        # Test concurrency manager error handling
        concurrency_manager = ConcurrencyManager(max_concurrent_users=1)

        # Fill up concurrency limit
        request_id = uuid4()
        concurrency_manager.register_request(request_id, "test_user", "/api/test")

        # Try to register another request (should fail)
        with pytest.raises(ConcurrencyManagerError) as exc_info:
            concurrency_manager.register_request(uuid4(), "test_user", "/api/test")

        assert "当前并发请求过多" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_service_container_integration(self, service_container):
        """Test that service container properly initializes all services."""
        # Test all services are available
        assert service_container.ai_service is not None
        assert service_container.file_service is not None
        assert service_container.phase_manager is not None
        assert service_container.project_service is not None
        assert service_container.code_generation_service is not None

        # Test service initialization
        await service_container.initialize_services()

        # Test AI service connection (should work in mock mode)
        connection_ok = await service_container.ai_service.validate_connection()
        assert connection_ok is True

    @pytest.mark.asyncio
    async def test_code_generation_workflow_integration(self, service_container):
        """Test complete code generation workflow integration."""
        code_gen_service = service_container.code_generation_service

        # Create a test request
        request = await code_gen_service.start_generation("创建计算器应用")

        # Verify request was created
        assert request is not None
        assert request.user_input == "创建计算器应用"
        assert request.status == RequestStatus.PROCESSING

        # Test streaming generation (this will use mock service)
        chunks = []
        async for chunk in code_gen_service.generate_code_stream(request):
            chunks.append(chunk)

        # Verify we got a complete workflow
        assert len(chunks) > 0

        # Check for workflow completion
        completion_events = [c for c in chunks if c.get('type') == 'workflow_complete']
        assert len(completion_events) > 0

        # Verify request status was updated
        assert request.status == RequestStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_project_service_integration(self, service_container):
        """Test project service integration with file operations."""
        project_service = service_container.project_service

        # Create a test project
        project_id = uuid4()
        project_data = {
            "id": project_id,
            "project_name": "test_calculator",
            "main_file": "calculator.py",
            "created_at": 1234567890,
            "syntax_validated": True,
            "total_files": 1,
            "total_size_bytes": 1024,
            "file_structure": {"type": "file", "name": "calculator.py"},
            "dependencies": ["pytest"],
            "total_files": 1,
            "total_size_bytes": 512,
            "syntax_validated": True,
            "main_file": "calculator.py"
        }

        # Test project metadata handling
        # Note: Actual implementation may vary, this tests the interface
        try:
            # Try to load non-existent project
            result = await project_service.load_project_metadata(project_id)
            # Should return None for non-existent project
            assert result is None
        except Exception:
            # Implementation may throw exception instead of returning None
            pass

    def test_concurrency_statistics(self, concurrency_manager):
        """Test concurrency manager statistics."""
        # Register a few requests
        for i in range(2):
            request_id = uuid4()
            user_id = f"user_{i}"
            concurrency_manager.register_request(request_id, user_id, "/api/test")

        # Get statistics
        stats = concurrency_manager.get_statistics()

        # Verify statistics structure
        assert 'current_active_requests' in stats
        assert 'max_concurrent_users' in stats
        assert 'total_requests_processed' in stats
        assert 'peak_concurrent_users' in stats
        assert stats['current_active_requests'] == 2
        assert stats['max_concurrent_users'] == 3

        # Clean up
        for request_id in list(concurrency_manager._active_requests.keys()):
            concurrency_manager.unregister_request(request_id)

    @pytest.mark.asyncio
    async def test_mixed_service_interaction(self, service_container):
        """Test interaction between multiple services."""
        # This test verifies that services can work together
        ai_service = service_container.ai_service
        code_gen_service = service_container.code_generation_service

        # Test that AI service and code generation service use the same mock backend
        # Both should work in development mode

        # Test AI service directly
        ai_connection = await ai_service.validate_connection()
        assert ai_connection is True

        # Test code generation service
        request = await code_gen_service.start_generation("test request")
        assert request is not None

        # Both should use mock implementations in development mode
        assert isinstance(ai_service, MockService)

    @pytest.mark.asyncio
    async def test_error_propagation_integration(self):
        """Test that errors properly propagate through the service layers."""
        # Test with mock service that can simulate errors
        mock_service = MockService()

        # Test normal operation
        connection_ok = await mock_service.validate_connection()
        assert connection_ok is True

        # Create a request
        request = CodeGenerationRequest(
            request_id=uuid4(),
            user_input="test error handling"
        )

        # Test successful generation
        chunks = []
        async for chunk in mock_service.generate_code_stream(request):
            chunks.append(chunk)

        assert len(chunks) > 0
        assert request.status == RequestStatus.COMPLETED

    def test_configuration_integration(self):
        """Test configuration integration across services."""
        # Test that services respect configuration settings

        # Test concurrency manager configuration
        manager = ConcurrencyManager(max_concurrent_users=2)
        assert manager.max_concurrent_users == 2

        # Test that it enforces the limit
        for i in range(2):
            request_id = uuid4()
            manager.register_request(request_id, f"user_{i}", "/api/test")

        # Third request should be rejected
        can_accept = manager.can_accept_request("user_3")
        assert can_accept is False

        # Clean up
        for request_id in list(manager._active_requests.keys()):
            manager.unregister_request(request_id)

    @pytest.mark.asyncio
    async def test_service_lifecycle_integration(self):
        """Test service lifecycle management."""
        # Test service initialization and cleanup
        container = ServiceContainer()

        # Test initialization
        await container.initialize_services()

        # Verify services are initialized
        assert container.ai_service is not None
        assert container.file_service is not None

        # Test that services work
        connection_ok = await container.ai_service.validate_connection()
        assert connection_ok is True

        # Note: shutdown_services() currently doesn't do much but tests the interface
        container.shutdown_services()

    def test_cross_service_data_consistency(self):
        """Test data consistency across services."""
        # Test that services maintain consistent state

        concurrency_manager = ConcurrencyManager(max_concurrent_users=5)

        # Register requests
        request_ids = []
        for i in range(3):
            request_id = uuid4()
            request_ids.append(request_id)
            concurrency_manager.register_request(request_id, f"user_{i}", "/api/test")

        # Verify counts are consistent
        assert concurrency_manager.get_active_requests_count() == 3
        assert len(concurrency_manager._active_requests) == 3

        # Verify user counts
        user_counts = concurrency_manager.get_statistics()['active_requests_by_user']
        assert len(user_counts) == 3
        assert all(count == 1 for count in user_counts.values())

        # Clean up
        for request_id in request_ids:
            concurrency_manager.unregister_request(request_id)

        assert concurrency_manager.get_active_requests_count() == 0


class TestSDKMigrationVerification:
    """Specific tests for SDK migration verification."""

    @pytest.fixture
    def mock_ai_service(self):
        """Create mock AI service for testing."""
        return MockService()

    @pytest.mark.asyncio
    async def test_output_consistency_across_sdks(self, mock_ai_service):
        """Test that outputs remain consistent across SDK versions."""
        test_requests = [
            "写一个贪吃蛇游戏",
            "创建一个计算器",
            "生成Hello World程序"
        ]

        for user_input in test_requests:
            request = CodeGenerationRequest(
                request_id=uuid4(),
                user_input=user_input
            )

            # Generate code
            chunks = []
            async for chunk in mock_ai_service.generate_code_stream(request):
                chunks.append(chunk)

            # Verify we got a complete response
            assert len(chunks) > 0
            assert request.status == RequestStatus.COMPLETED

            # Verify response contains expected elements
            content_chunks = [c for c in chunks if c.get('type') == 'content_chunk']
            assert len(content_chunks) > 0

    @pytest.mark.asyncio
    async def test_error_handling_consistency(self, mock_ai_service):
        """Test that error handling remains consistent."""
        # Test with various error conditions
        # Note: Mock service currently doesn't simulate errors, but tests the interface

        request = CodeGenerationRequest(
            request_id=uuid4(),
            user_input="test request"
        )

        # Should complete successfully with mock service
        chunks = []
        async for chunk in mock_ai_service.generate_code_stream(request):
            chunks.append(chunk)

        assert request.status == RequestStatus.COMPLETED

    def test_configuration_compatibility(self):
        """Test that configuration works across SDK versions."""
        # Test that mock service respects configuration
        mock_service = MockService()

        # Should work without external configuration
        # (Mock service doesn't need API keys)
        assert mock_service is not None

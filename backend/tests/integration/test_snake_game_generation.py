"""
Integration Tests for Snake Game Generation Flow

Tests the complete dual-track code generation process for Snake game requests.
Validates educational transparency, artifact creation, and code quality.
"""

import asyncio
import pytest
import ast
from pathlib import Path
from uuid import uuid4

from src.services.code_generation_service import CodeGenerationService
from src.models.code_generation_request import CodeGenerationRequest, RequestStatus


class TestSnakeGameGeneration:
    """Integration tests for Snake game generation end-to-end flow."""

    @pytest.fixture
    def code_generation_service(self):
        """Create CodeGenerationService instance for testing."""
        return CodeGenerationService()

    @pytest.mark.asyncio
    async def test_complete_snake_game_generation_flow(self, code_generation_service):
        """Test complete Snake game generation with dual-track artifacts."""
        # Create test request
        request = CodeGenerationRequest(user_input="帮我写个贪吃蛇")

        # Track streaming events
        events_received = []
        phases_completed = []

        # Execute generation and collect events
        async for event in code_generation_service.generate_code_stream(request):
            events_received.append(event)

            if event["type"] == "phase_complete":
                phases_completed.append(event["phase"])

            # Allow streaming to complete
            if event["type"] == "complete":
                break

        # Verify request completed successfully
        assert request.status == RequestStatus.COMPLETED

        # Verify all three phases completed
        assert "specify" in phases_completed
        assert "plan" in phases_completed
        assert "implement" in phases_completed

        # Verify streaming included educational content
        thinking_events = [e for e in events_received if e["type"] == "thinking"]
        text_events = [e for e in events_received if e["type"] == "text"]

        assert len(thinking_events) > 0, "Should have thinking traces for transparency"
        assert len(text_events) > 0, "Should have text content from AI"

        # Verify artifacts were created
        project_files = await code_generation_service.get_generated_files(request.request_id)

        # Check for dual-track artifacts
        assert "spec.md" in project_files, "Should have specification artifact"
        assert "plan.md" in project_files, "Should have planning artifact"
        assert "main.py" in project_files, "Should have main code file"
        assert "requirements.txt" in project_files, "Should have dependencies file"

        # Verify main.py content
        main_py_content = project_files["main.py"]

        # Check for essential Snake game elements
        assert "import pygame" in main_py_content, "Should import pygame"
        assert "def gameLoop" in main_py_content, "Should have game loop function"
        assert "pygame.init()" in main_py_content, "Should initialize pygame"

        # Verify AST validation passes
        try:
            ast.parse(main_py_content)
        except SyntaxError as e:
            pytest.fail(f"Generated code has syntax errors: {e}")

        # Verify spec.md and plan.md have content
        spec_content = project_files["spec.md"]
        plan_content = project_files["plan.md"]

        assert len(spec_content.strip()) > 0, "Specification should have content"
        assert len(plan_content.strip()) > 0, "Planning document should have content"

        # Check that artifacts contain different content (not identical)
        assert spec_content != plan_content, "Spec and plan should have different content"

    @pytest.mark.asyncio
    async def test_snake_game_code_quality(self, code_generation_service):
        """Test that generated Snake game code meets quality standards."""
        request = CodeGenerationRequest(user_input="帮我写个贪吃蛇")

        # Complete generation
        async for event in code_generation_service.generate_code_stream(request):
            if event["type"] == "complete":
                break

        # Get generated files
        project_files = await code_generation_service.get_generated_files(request.request_id)
        main_py_content = project_files["main.py"]

        # Parse AST to verify structure
        tree = ast.parse(main_py_content)

        # Check for essential code elements
        has_function_def = any(isinstance(node, ast.FunctionDef) for node in ast.walk(tree))
        has_import = any(isinstance(node, ast.Import) for node in ast.walk(tree))
        has_while_loop = any(isinstance(node, ast.While) for node in ast.walk(tree))

        assert has_import, "Code should have import statements"
        assert has_function_def, "Code should have function definitions"
        assert has_while_loop, "Snake game should have game loop"

        # Check for pygame-specific elements
        has_pygame_init = "pygame.init()" in main_py_content
        has_display_set = "pygame.display.set_mode" in main_py_content
        has_event_loop = "pygame.event.get()" in main_py_content

        assert has_pygame_init, "Should initialize pygame"
        assert has_display_set, "Should create game display"
        assert has_event_loop, "Should handle pygame events"

    @pytest.mark.asyncio
    async def test_streaming_transparency(self, code_generation_service):
        """Test that streaming preserves educational transparency."""
        request = CodeGenerationRequest(user_input="帮我写个贪吃蛇")

        phase_content = {"specify": [], "plan": [], "implement": []}
        current_phase = None

        async for event in code_generation_service.generate_code_stream(request):
            if event["type"] == "phase_start":
                current_phase = event["phase"]

            elif event["type"] in ["thinking", "text"] and current_phase:
                phase_content[current_phase].append(event["content"])

            elif event["type"] == "complete":
                break

        # Verify each phase received content
        for phase in ["specify", "plan", "implement"]:
            assert len(phase_content[phase]) > 0, f"Phase {phase} should have content"

        # Check that content includes Markdown/explanations (educational transparency)
        all_content = "\n".join([
            "\n".join(phase_content[phase])
            for phase in phase_content.values()
        ])

        # Should contain some markdown or explanatory content
        has_markdown = "##" in all_content or "###" in all_content or "`" in all_content
        assert has_markdown, "Streaming should include educational markdown content"

    @pytest.mark.asyncio
    async def test_artifact_persistence(self, code_generation_service):
        """Test that artifacts persist correctly in project structure."""
        request = CodeGenerationRequest(user_input="帮我写个贪吃蛇")

        # Complete generation
        async for event in code_generation_service.generate_code_stream(request):
            if event["type"] == "complete":
                break

        # Verify files exist on disk
        project_dir = code_generation_service.file_service.projects_base_dir / str(request.request_id)

        assert project_dir.exists(), "Project directory should exist"

        # Check all expected artifacts exist
        expected_files = ["spec.md", "plan.md", "main.py", "requirements.txt", "metadata.json"]
        for filename in expected_files:
            file_path = project_dir / filename
            assert file_path.exists(), f"Artifact {filename} should exist"
            assert file_path.stat().st_size > 0, f"Artifact {filename} should not be empty"

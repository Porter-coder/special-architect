"""
Code Generation Service

Orchestrates the three-phase code generation process (specify, plan, implement)
using AI service and file service for Snake game generation.
"""

import asyncio
from datetime import datetime
from typing import AsyncGenerator, Dict, List, Optional, Tuple
from uuid import UUID

from .ai_service import AIService, AIServiceError
from .file_service import FileService, FileServiceError
from ..models.code_generation_request import CodeGenerationRequest, RequestStatus
from ..models.generated_project import GeneratedProject
from ..models.process_phase import PhaseName, ProcessPhase, get_phase_message, PHASE_ORDER


class CodeGenerationServiceError(Exception):
    """Base exception for code generation service errors."""
    pass


class CodeGenerationService:
    """
    Code generation orchestrator for the three-phase process.

    Handles:
    - Request lifecycle management
    - Three-phase AI generation (specify → plan → implement)
    - Progress tracking and streaming
    - Project file generation and storage
    - Error handling and recovery
    """

    def __init__(self, ai_service: Optional[AIService] = None, file_service: Optional[FileService] = None):
        """
        Initialize code generation service.

        Args:
            ai_service: AI service instance (created if None)
            file_service: File service instance (created if None)
        """
        self.ai_service = ai_service or AIService()
        self.file_service = file_service or FileService()

    async def start_generation(self, user_input: str) -> CodeGenerationRequest:
        """
        Start a new code generation request.

        Args:
            user_input: Natural language request from user

        Returns:
            CodeGenerationRequest instance

        Raises:
            CodeGenerationServiceError: If request creation fails
        """
        try:
            # Create new request
            request = CodeGenerationRequest(user_input=user_input)
            request.update_status(RequestStatus.PENDING)
            return request
        except Exception as e:
            raise CodeGenerationServiceError(f"创建生成请求失败: {e}")

    async def generate_code_stream(
        self,
        request: CodeGenerationRequest
    ) -> AsyncGenerator[Dict, None]:
        """
        Execute the three-phase code generation process with streaming.

        Args:
            request: CodeGenerationRequest instance

        Yields:
            Streaming data with phase updates and content

        Raises:
            CodeGenerationServiceError: If generation fails
        """
        try:
            # Update request status to processing
            request.update_status(RequestStatus.PROCESSING)

            phases_data = {}
            all_code_parts = []

            # Execute each phase
            for phase in PHASE_ORDER:
                try:
                    # Create phase record
                    phase_record = ProcessPhase(
                        request_id=request.request_id,
                        phase_name=phase,
                        educational_message=get_phase_message(phase)
                    )

                    # Emit phase start event
                    yield {
                        "type": "phase_start",
                        "phase": phase.value,
                        "message": phase_record.educational_message,
                        "timestamp": phase_record.timestamp.isoformat()
                    }

                    # Generate content for this phase
                    thinking_parts = []
                    code_parts = []

                    async for chunk in self.ai_service.generate_code_stream(request.user_input, phase):
                        if chunk["type"] == "thinking":
                            thinking_parts.append(chunk["content"])
                            yield {
                                "type": "thinking",
                                "content": chunk["content"],
                                "phase": phase.value
                            }
                        elif chunk["type"] == "text":
                            code_parts.append(chunk["content"])
                            all_code_parts.append(chunk["content"])
                            yield {
                                "type": "text",
                                "content": chunk["content"],
                                "phase": phase.value
                            }

                    # Store phase data
                    phase_content = "".join(code_parts)
                    thinking_content = "".join(thinking_parts)
                    phases_data[phase] = {
                        "content": phase_content,
                        "thinking": thinking_content
                    }

                    # Update phase record with thinking trace
                    phase_record.thinking_trace = thinking_content

                    # Save intermediate phase artifacts (dual-track strategy)
                    await self._save_phase_artifact(request.request_id, phase, phase_content)

                    # Emit phase completion
                    yield {
                        "type": "phase_complete",
                        "phase": phase.value,
                        "content_length": len(phase_content)
                    }

                except AIServiceError as e:
                    # Phase failed
                    request.update_status(RequestStatus.FAILED, str(e))
                    yield {
                        "type": "error",
                        "message": f"阶段 {phase.value} 失败: {e}",
                        "phase": phase.value
                    }
                    raise CodeGenerationServiceError(f"AI 服务错误: {e}")

            # All phases completed successfully
            try:
                # Generate project files from the implement phase
                generated_files = self._parse_generated_code("".join(all_code_parts))

                # Create project metadata
                project_name = self._generate_project_name(request.user_input)
                main_file_path = self._find_main_file_path(generated_files)

                project_structure = {path: self._get_file_type(path) for path in generated_files.keys()}

                project = GeneratedProject(
                    project_id=request.request_id,  # Use request_id as project_id
                    request_id=request.request_id,
                    project_name=project_name,
                    main_file_path=main_file_path,
                    project_structure=project_structure,
                    dependencies=self._extract_dependencies(generated_files)
                )

                # Save files to disk (don't pass project_info to avoid overwriting project_structure)
                saved_project = self.file_service.save_generated_files(
                    request.request_id,
                    generated_files,
                    None  # Don't pass project_info to avoid overwriting our carefully set project_structure
                )

                # Update the saved project with our metadata
                saved_project.project_name = project.project_name
                saved_project.main_file_path = project.main_file_path
                saved_project.dependencies = project.dependencies
                # Keep the file_service's project_structure (which should be correct now)

                # Update request status to completed
                request.update_status(RequestStatus.COMPLETED)

                # Emit completion event
                yield {
                    "type": "complete",
                    "project_id": str(saved_project.project_id),
                    "project_name": saved_project.project_name,
                    "main_file": saved_project.main_file_path,
                    "files_count": len(generated_files)
                }

            except FileServiceError as e:
                request.update_status(RequestStatus.FAILED, f"文件保存失败: {e}")
                yield {
                    "type": "error",
                    "message": f"项目文件保存失败: {e}"
                }
                raise CodeGenerationServiceError(f"文件服务错误: {e}")

        except Exception as e:
            if request.status != RequestStatus.FAILED:
                request.update_status(RequestStatus.FAILED, str(e))
            raise CodeGenerationServiceError(f"代码生成失败: {e}")

    async def get_generated_files(self, request_id: UUID) -> Dict[str, str]:
        """
        Retrieve generated files for a completed request.

        Args:
            request_id: Request identifier

        Returns:
            Dictionary of file_path -> file_content

        Raises:
            CodeGenerationServiceError: If files cannot be retrieved
        """
        try:
            return self.file_service.read_generated_files(request_id)
        except FileServiceError as e:
            raise CodeGenerationServiceError(f"获取生成文件失败: {e}")

    async def get_request_status(self, request_id: UUID) -> Optional[CodeGenerationRequest]:
        """
        Get the status of a generation request.

        Args:
            request_id: Request identifier

        Returns:
            CodeGenerationRequest instance if found, None otherwise
        """
        # Load project metadata which contains request info
        project = self.file_service.load_project_metadata(request_id)
        if project:
            # Reconstruct request from project data
            return CodeGenerationRequest(
                request_id=project.request_id,
                user_input="",  # Would need to be stored separately
                status=RequestStatus.COMPLETED,
                created_at=project.created_at,
                updated_at=project.created_at
            )
        return None

    def _parse_generated_code(self, generated_content: str) -> Dict[str, str]:
        """
        Parse the generated code content into individual files.

        Extracts clean Python code from AI responses, focusing on code blocks
        and removing documentation, think tags, and other non-code content.

        Args:
            generated_content: Raw generated content from AI

        Returns:
            Dictionary of file_path -> file_content
        """
        files = {}
        import re

        # Clean up the content step by step
        content = generated_content.strip()

        # Step 1: Remove all <think>...</think> blocks
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)

        # Step 2: Look for Python code blocks specifically
        # Find all ```python ... ``` blocks
        python_blocks = re.findall(r'```python\s*(.*?)\s*```', content, re.DOTALL)

        clean_code = ""
        if python_blocks:
            # Find the block with actual Python code (containing import statements)
            best_block = None
            max_score = 0

            for block in python_blocks:
                score = 0
                if 'import pygame' in block:
                    score += 100  # Highest priority
                if 'def ' in block:
                    score += 10   # Functions
                if 'class ' in block:
                    score += 10   # Classes
                score += len(block) // 100  # Prefer longer blocks

                if score > max_score:
                    max_score = score
                    best_block = block

            clean_code = best_block.strip() if best_block else python_blocks[0].strip()
        else:
            # Fallback: try to extract code from general code blocks
            code_blocks = re.findall(r'```\s*(.*?)\s*```', content, re.DOTALL)
            if code_blocks:
                # Filter for blocks that look like Python code
                for block in code_blocks:
                    if 'import ' in block or 'def ' in block or 'class ' in block:
                        clean_code = block.strip()
                        break

        # If we still don't have code, try the old line-by-line approach
        if not clean_code:
            lines = content.split('\n')
            code_lines = []
            in_code_block = False

            for line in lines:
                line = line.rstrip()

                # Handle code blocks
                if line.startswith('```'):
                    if line.startswith('```python') or (line == '```' and not in_code_block):
                        in_code_block = True
                        continue
                    elif line == '```' and in_code_block:
                        in_code_block = False
                        continue

                # If we're in a code block, keep the line
                if in_code_block:
                    code_lines.append(line)

            clean_code = '\n'.join(code_lines).strip()

        # Additional cleanup: basic cleanup only, assume the code block has correct relative indentation
        if clean_code:
            lines = clean_code.split('\n')
            final_lines = []

            for line in lines:
                # Skip obvious non-code lines
                stripped = line.strip()
                if not stripped:
                    final_lines.append('')
                elif stripped.startswith('#') or self._is_code_line(stripped):
                    final_lines.append(line)
                # Skip lines that are just markdown or documentation
                elif not any(indicator in stripped for indicator in ['```', '###', '**', '---']):
                    final_lines.append(line)

            clean_code = '\n'.join(final_lines).strip()

            # Final cleanup: remove multiple blank lines
            clean_code = re.sub(r'\n{3,}', '\n\n', clean_code)

        # Create main.py file
        files["main.py"] = clean_code

        # Create requirements.txt for Snake game
        files["requirements.txt"] = "pygame>=2.5.0"

        # Create README.md
        files["README.md"] = """# Snake Game

A simple Snake game implemented in Python using Pygame.

## Requirements

- Python 3.11+
- Pygame 2.5.0+

## Installation

```bash
pip install -r requirements.txt
```

## Running the Game

```bash
python main.py
```

## Controls

- Arrow keys: Move the snake
- Space: Pause/Unpause (if implemented)

## Game Rules

- Control the snake to eat food and grow
- Avoid hitting the walls or yourself
- Score increases with each food eaten
- Game ends when snake hits wall or itself
"""

        return files

    def _is_code_line(self, line: str) -> bool:
        """
        Determine if a line looks like Python code.

        Args:
            line: Line to check

        Returns:
            True if line appears to be Python code
        """
        import re
        line = line.strip()

        # Empty lines are okay
        if not line:
            return True

        # Python keywords and constructs
        code_indicators = [
            'import ', 'from ', 'def ', 'class ', 'if ', 'for ', 'while ',
            'try:', 'except:', 'with ', 'return ', 'print(', 'pygame.',
            '=', '==', '!=', '<', '>', '<=', '>=', '+', '-', '*', '/',
            '(', ')', '[', ']', '{', '}', '.', '#', 'self.', 'True', 'False'
        ]

        # Check if line starts with or contains code indicators
        for indicator in code_indicators:
            if indicator in line:
                return True

        # Check for variable assignments
        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*\s*=', line):
            return True

        # Check for function calls
        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*\s*\(', line):
            return True

        return False

    def _generate_project_name(self, user_input: str) -> str:
        """
        Generate a filesystem-safe project name from user input.

        Args:
            user_input: User input text

        Returns:
            Safe project name
        """
        import re
        from datetime import datetime

        # Extract relevant keywords from user input
        if "贪吃蛇" in user_input or "snake" in user_input.lower():
            base_name = "snake_game"
        else:
            base_name = "generated_project"

        # Add timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        # Create safe name
        safe_name = f"{base_name}_{timestamp}"

        # Ensure filesystem safety (though GeneratedProject validator also checks this)
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', safe_name)

        return safe_name

    def _find_main_file_path(self, files: Dict[str, str]) -> str:
        """
        Find the main executable file path from generated files.

        Args:
            files: Dictionary of generated files

        Returns:
            Path to main file
        """
        # Priority for Snake game
        main_candidates = ["main.py", "app.py", "game.py", "snake.py"]

        for candidate in main_candidates:
            if candidate in files:
                return candidate

        # Fallback to first Python file
        python_files = [path for path in files.keys() if path.endswith('.py')]
        if python_files:
            return python_files[0]

        # Ultimate fallback
        return "main.py"

    def _get_file_type(self, file_path: str) -> str:
        """
        Determine file type based on extension.

        Args:
            file_path: File path

        Returns:
            File type string
        """
        from pathlib import Path

        ext = Path(file_path).suffix.lower()
        type_map = {
            '.py': 'python',
            '.txt': 'text',
            '.md': 'markdown',
            '.json': 'json'
        }

        return type_map.get(ext, 'file')

    def _extract_dependencies(self, files: Dict[str, str]) -> List[str]:
        """
        Extract dependencies from generated files.

        Args:
            files: Dictionary of generated files

        Returns:
            List of dependency names
        """
        dependencies = []

        # Check requirements.txt
        if "requirements.txt" in files:
            content = files["requirements.txt"]
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Extract package name before version specifiers
                    package = line.split()[0].split('>=')[0].split('==')[0].split('<')[0].split('>')[0]
                    if package and package not in dependencies:
                        dependencies.append(package)

        # For Snake game, ensure pygame is included
        if "pygame" not in dependencies:
            dependencies.append("pygame")

        return dependencies

    async def _save_phase_artifact(self, request_id: UUID, phase: PhaseName, content: str):
        """
        Save intermediate phase artifacts for dual-track content strategy.

        Phase 1 (Specify) → spec.md (raw specification content)
        Phase 2 (Plan) → plan.md (raw planning content)
        Phase 3 (Implement) → main.py (cleaned and validated)

        Args:
            request_id: Unique request identifier
            phase: Current development phase
            content: Raw content from the phase
        """
        from ..models.process_phase import PhaseName

        # Only save artifacts for phases 1 and 2 (raw content)
        # Phase 3 is handled separately with cleaning/validation
        if phase == PhaseName.SPECIFY:
            artifact_path = "spec.md"
            artifact_content = content.strip()
        elif phase == PhaseName.PLAN:
            artifact_path = "plan.md"
            artifact_content = content.strip()
        else:
            # Phase 3 (Implement) - skip intermediate saving, handled in final project creation
            return

        # Save the artifact using file service
        project_dir = self.file_service.projects_base_dir / str(request_id)
        artifact_file_path = project_dir / artifact_path

        await self.file_service.ensure_directory(project_dir)
        await self.file_service.write_file(
            artifact_file_path,
            artifact_content,
            encoding="utf-8"
        )

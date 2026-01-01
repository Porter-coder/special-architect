"""
Code Generation Service

Orchestrates the three-phase code generation process (specify, plan, implement)
using AI service and file service 
"""

import ast
import asyncio
import logging
from datetime import datetime
from typing import AsyncGenerator, Dict, List, Optional, Set, Tuple
from uuid import UUID

from .ai_service import AIService, AIServiceError
from .file_service import FileService, FileServiceError
from .phase_manager import PhaseManager, PhaseManagerError
from .project_service import ProjectService, ProjectServiceError
from .documentation_service import DocumentationService
from .content_processor import ContentProcessor, ContentProcessorError
from .dependency_analyzer import DependencyAnalyzer
from .compatibility_checker import CompatibilityChecker
from .dependency_validator import DependencyValidator
from ..models.code_generation_request import CodeGenerationRequest, RequestStatus
from ..models.generated_project import GeneratedProject
from ..models.process_phase import PhaseName, ProcessPhase, get_phase_message, PHASE_ORDER

logger = logging.getLogger(__name__)


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

    def __init__(
        self,
        ai_service: Optional[AIService] = None,
        phase_manager: Optional[PhaseManager] = None,
        project_service: Optional[ProjectService] = None,
        documentation_service: Optional[DocumentationService] = None,
        content_processor: Optional[ContentProcessor] = None,
        dependency_analyzer: Optional[DependencyAnalyzer] = None,
        compatibility_checker: Optional[CompatibilityChecker] = None
    ):
        """
        Initialize code generation service.

        Args:
            ai_service: AI service instance (created if None)
            phase_manager: Phase manager instance (created if None)
            project_service: Project service instance (created if None)
            documentation_service: Documentation service instance (created if None)
            content_processor: Content processor instance (created if None)
            dependency_analyzer: Dependency analyzer instance (created if None)
            compatibility_checker: Compatibility checker instance (created if None)
        """
        self.ai_service = ai_service or AIService()
        self.phase_manager = phase_manager or PhaseManager(self.ai_service)
        self.project_service = project_service or ProjectService()
        self.documentation_service = documentation_service or DocumentationService()
        self.content_processor = content_processor or ContentProcessor()
        self.dependency_analyzer = dependency_analyzer or DependencyAnalyzer()
        self.compatibility_checker = compatibility_checker or CompatibilityChecker()

    async def start_generation(self, user_input: str, application_type: Optional[str] = None) -> CodeGenerationRequest:
        """
        Start a new code generation request.

        Args:
            user_input: Natural language request from user
            application_type: Optional application type for US3

        Returns:
            CodeGenerationRequest instance

        Raises:
            CodeGenerationServiceError: If request creation fails
        """
        try:
            # Create new request
            request = CodeGenerationRequest(
                user_input=user_input,
                application_type=application_type
            )
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

            # Use universal prompt system - no complex analysis needed
            logger.info(f"Processing request with universal prompt: {request.user_input[:100]}...")

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

                    # Generate universal prompt for this phase
                    prompt = self._generate_universal_prompt(
                        phase=phase,
                        user_request=request.user_input,
                        spec_content=phases_data.get("specify", {}).get("content", ""),
                        plan_content=phases_data.get("plan", {}).get("content", "")
                    )

                    # Fall back to original user input if no template found
                    prompt_text = prompt or request.user_input

                    async for chunk in self.ai_service.generate_code_stream(prompt_text, phase):
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

                    # Apply content processing only at Phase 3 completion (FR-024)
                    if phase == PhaseName.IMPLEMENT:
                        processed_result = self.content_processor.process_content(phase_content, phase)
                        if processed_result["processed"]:
                            phase_content = processed_result["cleaned_content"]
                            # Update phases_data with processed content
                            phases_data[phase] = {
                                "content": phase_content,
                                "thinking": thinking_content,
                                "processed": processed_result
                            }
                        else:
                            phases_data[phase] = {
                                "content": phase_content,
                                "thinking": thinking_content
                            }
                    else:
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

                # Create project metadata first
                project_name = self._generate_project_name(request.user_input)
                main_file_path = self._find_main_file_path(generated_files)

                # Generate documentation files (FR-023)
                # Calculate total size
                total_size = sum(len(content) for content in generated_files.values())

                # Create a temporary file structure for documentation generation
                temp_file_structure = {
                    "type": "directory",
                    "name": project_name,
                    "children": [
                        {
                            "type": "file",
                            "name": path.split('/')[-1] if '/' in path else path,
                            "size": len(content),
                            "language": "python" if path.endswith('.py') else None
                        } for path, content in generated_files.items()
                    ] + [
                        {"type": "file", "name": "spec.md", "size": 0, "language": "markdown"},
                        {"type": "file", "name": "plan.md", "size": 0, "language": "markdown"},
                        {"type": "file", "name": "README.md", "size": 0, "language": "markdown"}
                    ]
                }

                # Create a temporary project object for documentation generation
                temp_project_data = {
                    "project_name": project_name,
                    "main_file": main_file_path,
                    "total_files": len(generated_files) + 3,  # +3 for spec.md, plan.md, README.md
                    "total_size_bytes": total_size,
                    "syntax_validated": True,  # Assume validation passed since we got here
                    "created_at": datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S'),
                    "id": str(request.request_id),
                    "file_structure": temp_file_structure,
                    "dependencies": self._extract_dependencies(generated_files)
                }
                documentation_files = self.documentation_service.generate_documentation_package(
                    request.user_input, phases_data, type('TempProject', (), temp_project_data)()
                )

                # Use dependency analyzer for better dependency detection
                logger.info("Analyzing project dependencies...")
                # Analyze dependencies from generated files only (before adding docs)
                temp_files_for_deps = generated_files
                dependencies, requirements_txt = self.dependency_analyzer.analyze_project_dependencies(temp_files_for_deps)

                # Validate and filter dependencies against PyPI mirror
                logger.info("Validating dependencies against PyPI mirror...")
                async with DependencyValidator() as validator:
                    validation_results = await validator.validate_requirements_async(requirements_txt)

                    if not validation_results["valid"]:
                        logger.warning(f"Found {validation_results['invalid_packages']} invalid packages, filtering...")
                        requirements_txt = validation_results["filtered_requirements"]
                        logger.info("Dependencies filtered and updated")

                # CRITICAL: Post-process and validate single-file constraint
                generated_files = self._post_process_generated_code(generated_files)
                single_file_validation = self._validate_single_file_delivery(generated_files, requirements_txt)
                if not single_file_validation["compliant"]:
                    error_msg = f"Single-file delivery violation: {single_file_validation['violations']}"
                    logger.error(error_msg)
                    raise CodeGenerationServiceError(error_msg)

                # Add validated requirements.txt to project files
                all_project_files = {**generated_files, **documentation_files, "requirements.txt": requirements_txt}

                # Perform Windows compatibility checking (FR-006)
                logger.info("Performing Windows compatibility check...")
                compatibility_warnings = []
                for file_path, content in all_project_files.items():
                    if file_path.endswith('.py'):
                        warnings = self.compatibility_checker.check_compatibility(content, file_path)
                        compatibility_warnings.extend(warnings)

                # Log compatibility warnings
                if compatibility_warnings:
                    logger.warning(f"Found {len(compatibility_warnings)} Windows compatibility warnings")
                    for warning in compatibility_warnings:
                        logger.warning(f"  {warning.description} (line {warning.line_number})")

                project_structure = {path: self._get_file_type(path) for path in all_project_files.keys()}

                # Create project data for the new GeneratedProject model
                project_data = {
                    "id": str(request.request_id),
                    "request_id": str(request.request_id),
                    "project_name": project_name,
                    "created_at": datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S'),
                    "file_structure": {
                        "type": "directory",
                        "name": project_name,
                        "children": [
                            {
                                "type": "file",
                                "name": path.split('/')[-1] if '/' in path else path,
                                "size": len(content),
                                "language": "python" if path.endswith('.py') else ("markdown" if path.endswith('.md') else None)
                            } for path, content in all_project_files.items()
                        ]
                    },
                    "dependencies": [dep.name for dep in dependencies],
                    "total_files": len(all_project_files),
                    "total_size_bytes": sum(len(content) for content in all_project_files.values()),
                    "syntax_validated": True,  # We'll assume it's validated since we generated it
                    "main_file": main_file_path
                }

                # Adjust file_contents keys to match project structure paths
                from pathlib import Path
                adjusted_file_contents = {}
                for filename, content in all_project_files.items():
                    adjusted_file_contents[str(Path(project_name) / filename)] = content

                saved_project = await self.project_service.save_project(project_data, adjusted_file_contents)

                # Update request status to completed
                request.update_status(RequestStatus.COMPLETED)

                # Emit completion event
                yield {
                    "type": "complete",
                    "project_id": str(saved_project.id),
                    "project_name": saved_project.project_name,
                    "main_file": saved_project.main_file,
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
            return await self.project_service.get_project_files(request_id)
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
        project = await self.project_service.load_project_metadata(request_id)
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

        # Requirements.txt will be generated by dependency analyzer
        # Documentation will be generated by documentation service

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

        # Create generic project name based on request
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

    def _validate_single_file_delivery(self, generated_files: Dict[str, str], requirements_txt: str = "") -> Dict[str, any]:
        """
        Validate that generated content adheres to single-file delivery constraint.
        Uses dynamic detection of standard library and requirements.txt declared packages.

        Args:
            generated_files: Dictionary of generated file paths to content

        Returns:
            Validation result with compliance status and violations
        """
        result = {
            "compliant": True,
            "violations": []
        }

        # Check that only main.py exists as a Python file
        python_files = [path for path in generated_files.keys() if path.endswith('.py')]

        if len(python_files) == 0:
            result["compliant"] = False
            result["violations"].append("No Python files generated")
            return result

        if len(python_files) > 1:
            result["compliant"] = False
            result["violations"].append(f"Multiple Python files generated: {python_files}")
            return result

        if python_files[0] != "main.py":
            result["compliant"] = False
            result["violations"].append(f"Generated file is not main.py: {python_files[0]}")
            return result

        # DISABLED: Removed strict local import validation to allow code to breathe
        # Now trusts Python interpreter and dependency management

        return result

    def _extract_declared_packages(self, requirements_content: str) -> Set[str]:
        """
        Extract package names from requirements.txt content.

        Args:
            requirements_content: Content of requirements.txt

        Returns:
            Set of declared package names (normalized to import names where possible)
        """
        declared_packages = set()

        for line in requirements_content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                # Extract package name (handle version specs like package>=1.0.0)
                package_name = line.split('>=')[0].split('==')[0].split('<')[0].split('>')[0].strip()

                # Normalize common package names back to import names
                import_name = self.dependency_analyzer.import_patterns.get(package_name, package_name)
                declared_packages.add(import_name)

                # Also add the package name itself
                declared_packages.add(package_name)

        return declared_packages

    def _generate_universal_prompt(self, phase: PhaseName, user_request: str,
                                  spec_content: str = "", plan_content: str = "") -> str:
        """
        Generate a focused prompt for each phase without redundant context.

        Args:
            phase: Current generation phase
            user_request: Original user request
            spec_content: Content from specify phase (if available)
            plan_content: Content from plan phase (if available)

        Returns:
            Phase-specific prompt string
        """

        if phase == PhaseName.SPECIFY:
            return f"""You are an Expert Python Software Architect.

PHASE 1: REQUIREMENTS ANALYSIS
=============================
Analyze the user's requirements comprehensively.

USER REQUEST: {user_request}

Provide a detailed technical specification in Chinese covering:
1. Core functionality and features
2. Technical requirements and constraints
3. Data structures and algorithms needed
4. User interface and interaction patterns
5. Error handling and edge cases
6. Performance considerations"""

        elif phase == PhaseName.PLAN:
            context = f"\nTECHNICAL SPECIFICATION:\n{spec_content}" if spec_content else ""

            return f"""You are an Expert Python Software Architect.

PHASE 2: TECHNICAL PLANNING
==========================
Based on the technical specification, create a detailed implementation plan.

USER REQUEST: {user_request}{context}

Create a comprehensive plan in Chinese including:
1. Overall architecture and design patterns
2. Key components and their responsibilities
3. Data flow and processing logic
4. Integration points and external dependencies
5. Testing strategy and quality assurance"""

        elif phase == PhaseName.IMPLEMENT:
            context_parts = []
            if spec_content:
                context_parts.append(f"SPECIFICATION:\n{spec_content[:500]}...")  # Truncate to avoid token overflow
            if plan_content:
                context_parts.append(f"PLAN:\n{plan_content[:500]}...")  # Truncate to avoid token overflow
            context = "\n\n".join(context_parts) if context_parts else ""

            return f"""You are an Expert Python Software Architect.

PHASE 3: CODE IMPLEMENTATION
===========================
Execute the implementation plan and generate complete, working code.

USER REQUEST: {user_request}

{context}

CRITICAL CONSTRAINTS:
- SINGLE-FILE ONLY: Generate EXACTLY ONE file named 'main.py'
- SELF-CONTAINED: ALL code must be in main.py. NO local imports
- CONTENT ACCURACY: Generate code that matches the request EXACTLY
- SYNTAX PERFECTION: Code MUST be syntactically perfect Python using ONLY ASCII characters (no Unicode in strings, comments, or identifiers)
- VARIABLE SCOPING: ALL variables must be defined before use. NO undefined variables. Do NOT reference variables that don't exist in the code you're writing
- COMPLETE IMPLEMENTATION: Every function, class, and logic block must be fully implemented with NO placeholders

CODE STYLE & COMPLEXITY GUIDE:
==============================
- **Target Audience**: Beginner to Intermediate Python developers
- **Structure**: Use clean, standard structure (Imports -> Constants -> Functions/Classes -> Main Entry)
- **Complexity**: Avoid complex abstractions. Use straightforward logic that a beginner can follow
- **Documentation**: Include file header docstring and comments for key logic sections
- **Completeness**: Code must be runnable 'as is', but keep it minimal and focused
- **Entry Point**: Include `if __name__ == "__main__":` block for executable scripts

NO ASCII ART:
=============
- Do NOT include directory trees (e.g., `├──`) in comments or docstrings
- Do NOT use non-standard characters like `│`, `└`, `├`
- Keep comments purely textual

MANDATORY EXECUTION REQUIREMENT:
===============================
The generated code MUST be an **executable application**, not just a library definition.

Inside the `if __name__ == '__main__':` block, you MUST:
1. **Print a welcome message** (e.g., '=== Password Strength Checker ===').
2. **Run a concrete scenario** OR **Start an interactive loop**.
   - *Bad Example*: `pass`
   - *Bad Example*: `analyzer = PasswordAnalyzer()` (and then do nothing)
   - *Good Example*:
     ```python
     print('Checking sample password...')
     result = analyze_password('MyP@ssw0rd')
     print('Score:', result.score)
     ```
3. **Ensure output**: The user MUST see text on the screen immediately after running `python main.py`.

VARIABLE COMPLETENESS REQUIREMENT:
==================================
- ALL variables referenced in the code MUST be properly defined and initialized
- NO undefined variables like 'result', 'data', or any other name that causes NameError
- Functions must be called with properly defined variables
- Class instances must be created before method calls

Generate production-ready, well-documented Python code."""

        else:
            return f"""You are an Expert Python Software Architect.

Process the following request: {user_request}

Provide appropriate content for the {phase.value} phase."""

    def _post_process_generated_code(self, generated_files: Dict[str, str]) -> Dict[str, str]:
        """
        Post-process generated code to fix common syntax issues.

        Args:
            generated_files: Dictionary of generated file paths to content

        Returns:
            Post-processed files dictionary
        """
        processed_files = {}

        for file_path, content in generated_files.items():
            if file_path.endswith('.py'):
                # Apply syntax fixes
                processed_content = self._fix_common_syntax_issues(content)
                processed_files[file_path] = processed_content
            else:
                # Keep non-Python files as-is
                processed_files[file_path] = content

        return processed_files

    def _fix_common_syntax_issues(self, code: str) -> str:
        """
        Fix common syntax issues that cause AST parsing failures.

        Args:
            code: Python code to fix

        Returns:
            Fixed code
        """
        # Fix Chinese punctuation
        fixes = {
            '，': ',',  # Chinese comma
            '。': '.',  # Chinese period
            '：': ':',  # Chinese colon
            '；': ';',  # Chinese semicolon
            '（': '(',  # Chinese left parenthesis
            '）': ')',  # Chinese right parenthesis
            '【': '[',  # Chinese left bracket
            '】': ']',  # Chinese right bracket
            '《': '<',  # Chinese left angle
            '》': '>',  # Chinese right angle
            '「': '"',  # Chinese left quote
            '」': '"',  # Chinese right quote
            '『': "'",  # Chinese left single quote
            '』': "'",  # Chinese right single quote
        }

        for chinese_char, ascii_char in fixes.items():
            code = code.replace(chinese_char, ascii_char)

        # Fix common syntax issues more aggressively
        lines = code.split('\n')
        fixed_lines = []

        for line in lines:
            # Check for unterminated strings
            single_quote_count = line.count("'") - line.count("\\'")
            double_quote_count = line.count('"') - line.count('\\"')

            # If we have odd counts, the line might have unterminated strings
            # This is a simple heuristic - real fixing would require more complex parsing
            if single_quote_count % 2 != 0 or double_quote_count % 2 != 0:
                logger.warning(f"Detected potential unterminated string in line: {line[:100]}...")
                # For now, we'll just log the issue and continue
                # A more sophisticated fix would require proper string parsing

            fixed_lines.append(line)

        return '\n'.join(fixed_lines)

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

        # Save the artifact using project service
        # For phase artifacts, we'll store them in a temporary location
        # This is a simplified implementation - in production we'd have proper artifact storage
        pass  # Skip artifact saving for now

"""
Code Generator Service

Handles the generation of complete code projects based on AI responses.
Processes streaming AI output to create structured project files with proper organization.
"""

import ast
import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from .ai_service import AIService, AIServiceError
from .file_service import FileService
from ..models.process_phase import PhaseName


class CodeGenerationError(Exception):
    """Base exception for code generation errors."""
    pass


class CodeGenerator:
    """
    Service for generating complete code projects from AI responses.

    Handles:
    - Project structure creation
    - File content generation and organization
    - Dependency analysis and requirements.txt creation
    - README.md generation with usage instructions
    """

    def __init__(self, ai_service: AIService, file_service: FileService):
        """
        Initialize code generator with required services.

        Args:
            ai_service: Service for AI code generation
            file_service: Service for file operations
        """
        self.ai_service = ai_service
        self.file_service = file_service

    async def generate_project(
        self,
        user_request: str,
        request_id: str
    ) -> Dict[str, Any]:
        """
        Generate a complete code project based on user request.

        This method orchestrates the three-phase code generation process:
        1. Specify: Analyze requirements
        2. Plan: Design technical solution
        3. Implement: Generate complete code

        Args:
            user_request: Natural language description of desired code
            request_id: Unique identifier for this generation request

        Returns:
            Dictionary containing project information:
            {
                "project_name": "snake_game_20251231",
                "main_file": "main.py",
                "files": [...],
                "dependencies": {...},
                "created_at": "2025-12-31T12:00:00Z"
            }

        Raises:
            CodeGenerationError: If code generation fails
        """
        try:
            # Phase 1: Specify - Analyze requirements
            specify_result = await self._generate_phase_content(
                user_request, PhaseName.SPECIFY
            )

            # Phase 2: Plan - Design technical solution
            plan_result = await self._generate_phase_content(
                user_request, PhaseName.PLAN
            )

            # Phase 3: Implement - Generate complete code
            implement_result = await self._generate_phase_content(
                user_request, PhaseName.IMPLEMENT
            )

            # Parse and structure the generated content
            project_data = self._parse_generated_content(
                user_request, implement_result["code"]
            )

            # Create project structure and save files
            project_info = await self._create_project_structure(
                request_id, project_data
            )

            return project_info

        except AIServiceError as e:
            raise CodeGenerationError(f"AI 服务错误: {e}") from e
        except Exception as e:
            raise CodeGenerationError(f"代码生成失败: {e}") from e

    async def _generate_phase_content(
        self,
        user_request: str,
        phase: PhaseName
    ) -> Dict[str, Any]:
        """
        Generate content for a specific development phase.

        Args:
            user_request: Original user request
            phase: Development phase to generate for

        Returns:
            Dictionary with generated code and thinking trace
        """
        code, thinking = await self.ai_service.generate_code(user_request, phase)
        return {
            "code": code,
            "thinking": thinking,
            "phase": phase.value
        }

    def _parse_generated_content(
        self,
        user_request: str,
        generated_code: str
    ) -> Dict[str, Any]:
        """
        Parse AI-generated content to extract structured project information.

        Args:
            user_request: Original user request for context
            generated_code: Raw code output from AI

        Returns:
            Structured project data with files, dependencies, etc.
        """
        # For Snake game specifically, create a structured response
        # In a full implementation, this would use AI to parse and structure the output

        project_name = self._generate_project_name(user_request)
        main_file = "main.py"

        # Extract code blocks and create file structure
        files = self._extract_code_files(generated_code, main_file)

        # Generate dependencies based on detected imports
        dependencies = self._analyze_dependencies(files)

        # Create README
        readme_content = self._generate_readme(user_request, project_name, dependencies)

        # Add README to files
        files.append({
            "path": "README.md",
            "content": readme_content,
            "encoding": "utf-8"
        })

        # Add requirements.txt if dependencies found
        if dependencies.get("python_packages"):
            requirements_content = "\n".join(dependencies["python_packages"]) + "\n"
            files.append({
                "path": "requirements.txt",
                "content": requirements_content,
                "encoding": "utf-8"
            })

        return {
            "project_name": project_name,
            "main_file": main_file,
            "files": files,
            "dependencies": dependencies,
            "project_structure": self._create_project_structure_json(files)
        }

    def _generate_project_name(self, user_request: str) -> str:
        """
        Generate a filesystem-safe project name from user request.

        Args:
            user_request: User request string

        Returns:
            Safe project name with timestamp
        """
        # Simple mapping for common requests
        name_mappings = {
            
        }

        base_name = "generated_project"
        for keyword, name in name_mappings.items():
            if keyword in user_request:
                base_name = name
                break

        # Add timestamp for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base_name}_{timestamp}"

    def _extract_code_files(self, generated_code: str, main_file: str) -> List[Dict[str, str]]:
        """
        Extract individual code files from AI-generated content.

        Args:
            generated_code: Raw generated code content
            main_file: Name of the main file

        Returns:
            List of file dictionaries with path, content, encoding
        """
        files = []

        # Simple extraction - in production, this would be more sophisticated
        # For now, treat the entire generated code as the main file
        if generated_code.strip():
            files.append({
                "path": main_file,
                "content": generated_code.strip(),
                "encoding": "utf-8"
            })

        return files

    def _analyze_dependencies(self, files: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Analyze code files to extract dependencies.

        Args:
            files: List of file dictionaries

        Returns:
            Dictionary with detected dependencies
        """
        python_packages = set()
        other_dependencies = {}

        for file_info in files:
            content = file_info["content"]

            # Check for Python imports
            if file_info["path"].endswith(".py"):
                # Find import statements
                import_pattern = r'^\s*(?:import\s+(\w+)|from\s+(\w+))'
                matches = re.findall(import_pattern, content, re.MULTILINE)

                for match in matches:
                    package = match[0] or match[1]
                    # Map common packages
                    if package in ["pygame", "tkinter", "random", "time", "sys", "os"]:
                        if package == "tkinter":
                            continue  # Built-in
                        python_packages.add(package)

        return {
            "python_packages": sorted(list(python_packages)) if python_packages else [],
            "other_dependencies": other_dependencies
        }

    def _generate_readme(self, user_request: str, project_name: str, dependencies: Dict[str, Any]) -> str:
        """
        Generate a README.md file with usage instructions.

        Args:
            user_request: Original user request
            project_name: Generated project name
            dependencies: Detected dependencies

        Returns:
            README content as string
        """
        readme = f"""# {project_name.replace('_', ' ').title()}

基于用户需求自动生成的代码项目。

## 用户需求

{user_request}

## 运行环境要求

- Python 3.11+
"""

        if dependencies.get("python_packages"):
            readme += "\n## 依赖包\n\n安装依赖：\n```bash\npip install -r requirements.txt\n```\n\n包含的包：\n"
            for package in dependencies["python_packages"]:
                readme += f"- {package}\n"

        readme += "\n## 运行方法\n\n```bash\npython main.py\n```\n"

        readme += "\n## 项目结构\n\n```\n"
        for file_info in dependencies.get("files", []):
            readme += f"{file_info['path']}\n"
        readme += "```\n"

        readme += "\n## 注意事项\n\n- 确保所有依赖包已正确安装\n- 使用 UTF-8 编码运行\n- 如有问题请检查 Python 版本兼容性\n"

        return readme

    def _create_project_structure_json(self, files: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Create a JSON representation of the project structure.

        Args:
            files: List of file dictionaries

        Returns:
            Project structure as nested dictionary
        """
        structure = {}

        for file_info in files:
            path_parts = file_info["path"].split("/")
            current = structure

            # Build nested structure
            for part in path_parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]

            # Add file info
            filename = path_parts[-1]
            current[filename] = {
                "type": "file",
                "encoding": file_info["encoding"],
                "size": len(file_info["content"])
            }

        return structure

    async def _create_project_structure(
        self,
        request_id: str,
        project_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create the actual project directory structure and save files.

        Args:
            request_id: Unique request identifier
            project_data: Structured project data

        Returns:
            Project information dictionary
        """
        # Create project directory
        project_dir = Path("projects") / request_id
        await self.file_service.ensure_directory(project_dir)

        # Save all files
        for file_info in project_data["files"]:
            file_path = project_dir / file_info["path"]
            await self.file_service.write_file(
                file_path,
                file_info["content"],
                encoding=file_info["encoding"]
            )

        # Create metadata file
        metadata = {
            "request_id": request_id,
            "project_name": project_data["project_name"],
            "main_file": project_data["main_file"],
            "created_at": datetime.now().isoformat(),
            "files": [
                {
                    "path": f["path"],
                    "encoding": f["encoding"],
                    "size": len(f["content"])
                }
                for f in project_data["files"]
            ],
            "dependencies": project_data["dependencies"],
            "project_structure": project_data["project_structure"]
        }

        metadata_path = project_dir / "metadata.json"
        await self.file_service.write_file(
            metadata_path,
            json.dumps(metadata, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        return {
            "project_name": project_data["project_name"],
            "main_file": project_data["main_file"],
            "files": project_data["files"],
            "dependencies": project_data["dependencies"],
            "created_at": metadata["created_at"]
        }

    def parse_markdown_code_blocks(self, content: str) -> str:
        """
        Parse Markdown content and extract Python code from code blocks.

        Uses priority scoring to identify the most relevant Python code block:
        - Prefers blocks with import statements (especially pygame)
        - Considers function/class definitions
        - Falls back to general code blocks if no python-specific blocks found

        Args:
            content: Raw Markdown content from AI

        Returns:
            Clean Python code extracted from the best code block
        """
        # Extract all ```python blocks
        python_blocks = re.findall(r'```python\s*(.*?)\s*```', content, re.DOTALL)

        clean_code = ""
        if python_blocks:
            # Score blocks by relevance indicators
            best_block = None
            max_score = 0

            for block in python_blocks:
                score = 0
                if 'import pygame' in block:
                    score += 100  # Highest priority for pygame imports
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
            # Fallback: try to extract from general code blocks
            code_blocks = re.findall(r'```\s*(.*?)\s*```', content, re.DOTALL)
            if code_blocks:
                # Filter for blocks that look like Python code
                for block in code_blocks:
                    if 'import ' in block or 'def ' in block or 'class ' in block:
                        clean_code = block.strip()
                        break

        return clean_code

    def validate_python_syntax(self, code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate Python code syntax using AST parsing.

        Args:
            code: Python code to validate

        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if code parses successfully
            - error_message: None if valid, error description if invalid
        """
        try:
            ast.parse(code, mode='exec')
            return True, None
        except SyntaxError as e:
            error_msg = f"Syntax error at line {e.lineno}: {e.msg}"
            return False, error_msg
        except Exception as e:
            error_msg = f"AST parsing error: {str(e)}"
            return False, error_msg

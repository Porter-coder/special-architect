"""
File Service for Windows-Compatible Operations

Handles all file operations with Windows compatibility, UTF-8 encoding, and pathlib.Path.
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from ..models.generated_project import GeneratedProject


class FileServiceError(Exception):
    """Base exception for file service errors."""
    pass


class FileService:
    """
    File service for Windows-compatible file operations.

    Handles:
    - Project directory creation and management
    - File writing with UTF-8 encoding (constitution requirement)
    - Path operations using pathlib.Path (constitution requirement)
    - Project persistence and retrieval
    """

    def __init__(self, projects_base_dir: str = "projects"):
        """
        Initialize file service.

        Args:
            projects_base_dir: Base directory for storing generated projects
        """
        self.projects_base_dir = Path(projects_base_dir)
        self._ensure_base_directory()

    def _ensure_base_directory(self):
        """Ensure the projects base directory exists."""
        self.projects_base_dir.mkdir(parents=True, exist_ok=True)

    def create_project_directory(self, request_id: UUID) -> Path:
        """
        Create a project directory for a specific request.

        Args:
            request_id: Unique identifier for the request

        Returns:
            Path to the created project directory

        Raises:
            FileServiceError: If directory creation fails
        """
        try:
            project_dir = self.projects_base_dir / str(request_id)
            project_dir.mkdir(parents=True, exist_ok=True)
            return project_dir
        except Exception as e:
            raise FileServiceError(f"创建项目目录失败: {e}")

    def save_generated_files(
        self,
        request_id: UUID,
        files: Dict[str, str],
        project_info: Optional[GeneratedProject] = None
    ) -> GeneratedProject:
        """
        Save generated files to the project directory.

        Args:
            request_id: Request identifier
            files: Dictionary of file_path -> file_content
            project_info: Optional project metadata

        Returns:
            GeneratedProject instance with saved file information

        Raises:
            FileServiceError: If file saving fails
        """
        try:
            project_dir = self.create_project_directory(request_id)

            # Save each file with UTF-8 encoding (constitution requirement)
            saved_files = {}
            for file_path, content in files.items():
                full_path = project_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)

                # Write file with UTF-8 encoding
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                # Determine file type based on extension
                file_type = self._get_file_type(file_path)
                saved_files[file_path] = file_type

            # Create or update project metadata
            if project_info:
                project = project_info
                project.project_structure = saved_files
            else:
                # Auto-generate project name
                project_name = f"project_{request_id.hex[:8]}"
                main_file = self._find_main_file(saved_files)

                project = GeneratedProject(
                    project_id=request_id,  # Use request_id as project_id for simplicity
                    request_id=request_id,
                    project_name=project_name,
                    main_file_path=main_file or "main.py",
                    project_structure=saved_files,
                    dependencies=self._extract_dependencies(files)
                )

            # Save project metadata
            self._save_project_metadata(project_dir, project)

            return project

        except Exception as e:
            raise FileServiceError(f"保存生成文件失败: {e}")

    async def ensure_directory(self, directory_path: Path) -> None:
        """
        Ensure a directory exists, creating it if necessary.

        Args:
            directory_path: Path to the directory

        Raises:
            FileServiceError: If directory creation fails
        """
        try:
            directory_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise FileServiceError(f"创建目录失败: {e}")

    async def write_file(self, file_path: Path, content: str, encoding: str = "utf-8") -> None:
        """
        Write content to a file with specified encoding.

        Args:
            file_path: Path to the file
            content: Content to write
            encoding: File encoding (default: utf-8 per constitution)

        Raises:
            FileServiceError: If file writing fails
        """
        try:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file with UTF-8 encoding (constitution requirement)
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
        except Exception as e:
            raise FileServiceError(f"写入文件失败: {e}")

    def read_generated_files(self, request_id: UUID) -> Dict[str, str]:
        """
        Read all generated files for a request.

        Args:
            request_id: Request identifier

        Returns:
            Dictionary of file_path -> file_content

        Raises:
            FileServiceError: If file reading fails
        """
        try:
            project_dir = self.projects_base_dir / str(request_id)
            if not project_dir.exists():
                raise FileServiceError(f"项目目录不存在: {project_dir}")

            files = {}
            for file_path in project_dir.rglob('*'):
                if file_path.is_file():
                    # Skip metadata files
                    if file_path.name == 'metadata.json':
                        continue

                    # Read file with UTF-8 encoding
                    relative_path = file_path.relative_to(project_dir)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        files[str(relative_path)] = f.read()

            return files

        except Exception as e:
            raise FileServiceError(f"读取生成文件失败: {e}")

    def load_project_metadata(self, request_id: UUID) -> Optional[GeneratedProject]:
        """
        Load project metadata from disk.

        Args:
            request_id: Request identifier

        Returns:
            GeneratedProject instance if found, None otherwise
        """
        try:
            project_dir = self.projects_base_dir / str(request_id)
            metadata_file = project_dir / 'metadata.json'

            if not metadata_file.exists():
                return None

            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return GeneratedProject.from_dict(data)

        except Exception:
            return None

    def cleanup_old_projects(self, max_age_days: int = 30):
        """
        Clean up old project directories.

        Args:
            max_age_days: Maximum age in days for projects to keep
        """
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_days * 24 * 60 * 60

            for project_dir in self.projects_base_dir.iterdir():
                if project_dir.is_dir():
                    # Check directory modification time
                    if current_time - project_dir.stat().st_mtime > max_age_seconds:
                        shutil.rmtree(project_dir)

        except Exception as e:
            # Log but don't raise - cleanup failures shouldn't break the service
            print(f"清理旧项目失败: {e}")

    def _save_project_metadata(self, project_dir: Path, project: GeneratedProject):
        """Save project metadata to JSON file."""
        metadata_file = project_dir / 'metadata.json'

        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(project.to_dict(), f, ensure_ascii=False, indent=2)

    def _get_file_type(self, file_path: str) -> str:
        """Determine file type based on extension."""
        path = Path(file_path)
        ext = path.suffix.lower()

        type_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.md': 'markdown',
            '.txt': 'text',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml'
        }

        return type_map.get(ext, 'file')

    def _find_main_file(self, files: Dict[str, str]) -> Optional[str]:
        """Find the main executable file in the project."""
        # Priority order for main files
        main_candidates = [
            'main.py', 'app.py', 'index.js', 'main.js',
            'Program.cs', 'main.go', 'lib.rs', 'main.rs'
        ]

        for candidate in main_candidates:
            if candidate in files:
                return candidate

        # Fallback: first Python file
        python_files = [f for f in files.keys() if f.endswith('.py')]
        if python_files:
            return python_files[0]

        return None

    def _extract_dependencies(self, files: Dict[str, str]) -> List[str]:
        """Extract dependencies from generated files."""
        dependencies = []

        # Check for Python requirements.txt
        for file_path, content in files.items():
            if 'requirements.txt' in file_path:
                # Parse requirements.txt format
                for line in content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Extract package name (before ==, >=, etc.)
                        package = line.split()[0].split('>=')[0].split('==')[0].split('<')[0].split('>')[0]
                        if package and package not in dependencies:
                            dependencies.append(package)

        return dependencies

    def get_project_list(self) -> List[Dict]:
        """
        Get list of all projects with basic metadata.

        Returns:
            List of project summaries
        """
        projects = []

        try:
            for project_dir in self.projects_base_dir.iterdir():
                if project_dir.is_dir():
                    metadata_file = project_dir / 'metadata.json'

                    if metadata_file.exists():
                        try:
                            with open(metadata_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)

                            projects.append({
                                'project_id': data.get('project_id'),
                                'project_name': data.get('project_name'),
                                'request_id': data.get('request_id'),
                                'created_at': data.get('created_at'),
                                'main_file': data.get('main_file_path')
                            })
                        except Exception:
                            # Skip corrupted metadata
                            continue

        except Exception as e:
            print(f"获取项目列表失败: {e}")

        return projects

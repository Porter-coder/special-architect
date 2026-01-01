"""
Generated Project Model

Represents the output of a successful code generation.
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class FileStructure(BaseModel):
    """File structure representation."""
    type: str = Field(..., description="Type: 'file' or 'directory'")
    name: str = Field(..., description="File or directory name")
    size: Optional[int] = Field(None, description="File size in bytes (files only)")
    language: Optional[str] = Field(None, description="Programming language (files only)")
    children: Optional[List['FileStructure']] = Field(None, description="Child files/directories (directories only)")


class GeneratedProject(BaseModel):
    """
    Represents the output of a successful code generation.

    Fields:
    - id (str): Unique identifier for generated project
    - request_id (str): Reference to originating request
    - project_name (str): Auto-generated project name (e.g., "snake_game_20251231")
    - created_at (datetime): Project generation completion timestamp
    - file_structure (FileStructure): Complete project file tree structure
    - dependencies (list): List of required packages/libraries identified
    - total_files (int): Total number of files in project
    - total_size_bytes (int): Total project size in bytes
    - syntax_validated (bool): Whether all code files passed AST validation
    - main_file (str): Path to the main executable file
    """

    id: str = Field(..., description="Unique identifier for generated project")
    request_id: str = Field(..., description="Reference to originating request")
    project_name: str = Field(..., description="Auto-generated project name")
    created_at: str = Field(..., description="Project generation completion timestamp")
    file_structure: FileStructure = Field(..., description="Complete project file tree structure")
    dependencies: List[str] = Field(default_factory=list, description="List of required packages/libraries")
    total_files: int = Field(..., description="Total number of files in project")
    total_size_bytes: int = Field(..., description="Total project size in bytes")
    syntax_validated: bool = Field(..., description="Whether all code files passed AST validation")
    main_file: str = Field(..., description="Path to the main executable file")

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }

    @validator('project_name')
    def validate_project_name(cls, v):
        """Validate project name is filesystem-safe."""
        if not v or not v.strip():
            raise ValueError('项目名称不能为空')

        # Check for filesystem-safe characters (no special chars that could cause issues)
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('项目名称只能包含字母、数字、下划线和连字符')

        # Check length
        if len(v) > 50:
            raise ValueError('项目名称长度不能超过50个字符')

        return v.strip()

    @validator('main_file')
    def validate_main_file(cls, v):
        """Validate main file path is safe and points to a valid file."""
        if not v or not v.strip():
            raise ValueError('主文件路径不能为空')

        # Basic path validation (no absolute paths, no ..)
        if v.startswith('/') or v.startswith('\\') or '..' in v:
            raise ValueError('主文件路径必须是相对路径且不包含..')

        # Check for valid file extensions
        valid_extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.go', '.rs', '.rb', '.php']
        if not any(v.endswith(ext) for ext in valid_extensions):
            raise ValueError('主文件必须是有效的代码文件')

        return v.strip()

    @validator('total_size_bytes')
    def validate_total_size(cls, v):
        """Validate total project size doesn't exceed limits."""
        max_size = 10 * 1024 * 1024  # 10MB
        if v > max_size:
            raise ValueError(f'项目总大小不能超过 {max_size} 字节 (10MB)')
        return v

    @validator('dependencies')
    def validate_dependencies(cls, v):
        """Validate dependencies list contains valid package names."""
        if not isinstance(v, list):
            raise ValueError('依赖列表必须是数组格式')

        for dep in v:
            if not isinstance(dep, str) or not dep.strip():
                raise ValueError('依赖项必须是非空字符串')

            # Basic package name validation (no dangerous characters)
            if not re.match(r'^[a-zA-Z0-9_-]+$', dep):
                raise ValueError(f'依赖项名称无效: {dep}')

        return [dep.strip() for dep in v]

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return self.dict()

    @classmethod
    def from_dict(cls, data: dict) -> 'GeneratedProject':
        """Create instance from dictionary (for JSON deserialization)."""
        return cls(**data)

    def get_python_files(self) -> List[str]:
        """Get all Python files in the project."""
        def collect_files(node: FileStructure, path: str = "") -> List[str]:
            files = []
            current_path = f"{path}/{node.name}" if path else node.name

            if node.type == "file" and node.language == "python":
                files.append(current_path)
            elif node.type == "directory" and node.children:
                for child in node.children:
                    files.extend(collect_files(child, current_path))

            return files

        return collect_files(self.file_structure)

    def get_total_files(self) -> int:
        """Count total files in project structure."""
        def count_files(node: FileStructure) -> int:
            if node.type == "file":
                return 1
            elif node.type == "directory" and node.children:
                return sum(count_files(child) for child in node.children)
            return 0

        return count_files(self.file_structure)

    def get_total_size(self) -> int:
        """Calculate total size of all files."""
        def sum_sizes(node: FileStructure) -> int:
            if node.type == "file" and node.size:
                return node.size
            elif node.type == "directory" and node.children:
                return sum(sum_sizes(child) for child in node.children)
            return 0

        return sum_sizes(self.file_structure)

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


class GeneratedProject(BaseModel):
    """
    Represents the output of a successful code generation.

    Fields:
    - project_id (UUID): Unique identifier for generated project
    - request_id (UUID): Reference to originating request
    - project_name (str): Auto-generated project name (e.g., "snake_game_20251231")
    - main_file_path (str): Relative path to main executable file (e.g., "main.py")
    - project_structure (dict): Directory structure with file paths and types
    - dependencies (list): List of required packages/libraries identified
    - created_at (datetime): Project generation completion timestamp
    """

    project_id: UUID = Field(..., description="Unique identifier for generated project")
    request_id: UUID = Field(..., description="Reference to originating request")
    project_name: str = Field(..., description="Auto-generated project name")
    main_file_path: str = Field(..., description="Relative path to main executable file")
    project_structure: Dict[str, str] = Field(..., description="Directory structure with file paths and types")
    dependencies: List[str] = Field(default_factory=list, description="List of required packages/libraries")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Project generation completion timestamp")

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

    @validator('main_file_path')
    def validate_main_file_path(cls, v):
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

    @validator('project_structure')
    def validate_project_structure(cls, v):
        """Validate project structure is a valid dictionary."""
        if not isinstance(v, dict):
            raise ValueError('项目结构必须是字典格式')

        # Ensure all values are strings (file types)
        for path, file_type in v.items():
            if not isinstance(file_type, str):
                raise ValueError(f'文件类型必须是字符串，路径: {path}')

            # Validate file types
            valid_types = ['file', 'directory', 'python', 'javascript', 'typescript', 'java', 'cpp', 'c', 'csharp', 'go', 'rust', 'ruby', 'php', 'text', 'markdown', 'json', 'yaml']
            if file_type not in valid_types:
                raise ValueError(f'无效的文件类型: {file_type}，路径: {path}')

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

    def add_file(self, file_path: str, file_type: str = 'file'):
        """
        Add a file to the project structure.

        Args:
            file_path: Relative path to the file
            file_type: Type of file (file, python, javascript, etc.)
        """
        self.project_structure[file_path] = file_type

    def add_dependency(self, dependency: str):
        """
        Add a dependency to the project.

        Args:
            dependency: Package/library name
        """
        if dependency not in self.dependencies:
            self.dependencies.append(dependency)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        data = self.dict()
        # Ensure UUIDs are converted to strings
        if 'project_id' in data and hasattr(data['project_id'], '__str__'):
            data['project_id'] = str(data['project_id'])
        if 'request_id' in data and hasattr(data['request_id'], '__str__'):
            data['request_id'] = str(data['request_id'])
        # Ensure datetimes are converted to ISO strings
        if 'created_at' in data and hasattr(data['created_at'], 'isoformat'):
            data['created_at'] = data['created_at'].isoformat()
        if 'updated_at' in data and hasattr(data['updated_at'], 'isoformat'):
            data['updated_at'] = data['updated_at'].isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'GeneratedProject':
        """Create instance from dictionary (for JSON deserialization)."""
        # Handle UUID string conversion
        for field in ['project_id', 'request_id']:
            if field in data and isinstance(data[field], str):
                data[field] = UUID(data[field])

        # Handle datetime string conversion
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))

        return cls(**data)

    def get_files_by_type(self, file_type: str) -> List[str]:
        """
        Get all file paths of a specific type.

        Args:
            file_type: File type to filter by

        Returns:
            List of file paths
        """
        return [path for path, ftype in self.project_structure.items() if ftype == file_type]

    def get_python_files(self) -> List[str]:
        """Get all Python files in the project."""
        return self.get_files_by_type('python')

    def get_main_file_content(self) -> Optional[str]:
        """
        Get the content of the main file (would be read from actual file system).

        Returns:
            File content if available, None otherwise
        """
        # This would be implemented when we have the actual file system access
        return None

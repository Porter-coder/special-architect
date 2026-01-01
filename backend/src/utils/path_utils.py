"""
Path Utilities

Provides Windows-compatible path operations and project directory management.
"""

import os
import re
from pathlib import Path
from typing import List, Optional, Set
from uuid import UUID


def ensure_directory(path: Path) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path to ensure

    Returns:
        The ensured directory path
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_project_directory(base_dir: str, request_id: UUID) -> Path:
    """
    Get the project directory path for a specific request.

    Args:
        base_dir: Base projects directory
        request_id: Request identifier

    Returns:
        Project directory path
    """
    return Path(base_dir) / str(request_id)


def get_projects_base_dir() -> Path:
    """
    Get the base directory for storing generated projects.

    Returns:
        Base projects directory path
    """
    # Default to 'projects' in the current working directory
    return Path("projects")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to be safe for Windows file system.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Replace invalid characters with underscores
    invalid_chars = '<>:"/\\|?*'
    sanitized = filename

    for char in invalid_chars:
        sanitized = sanitized.replace(char, '_')

    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip(' .')

    # Ensure it's not empty and not a reserved name
    if not sanitized:
        sanitized = "file"

    # Windows reserved names
    reserved_names = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }

    if sanitized.upper() in reserved_names:
        sanitized = f"_{sanitized}"

    return sanitized


def is_safe_path(path: str, base_dir: Path) -> bool:
    """
    Check if a path is safe (doesn't escape the base directory).

    Args:
        path: Path to check
        base_dir: Base directory that should not be escaped

    Returns:
        True if path is safe, False otherwise
    """
    try:
        full_path = (base_dir / path).resolve()
        base_resolved = base_dir.resolve()
        return full_path.is_relative_to(base_resolved)
    except (ValueError, OSError):
        return False


def get_relative_path(full_path: Path, base_dir: Path) -> Optional[str]:
    """
    Get relative path from base directory.

    Args:
        full_path: Full path
        base_dir: Base directory

    Returns:
        Relative path string, or None if not relative
    """
    try:
        return str(full_path.relative_to(base_dir))
    except ValueError:
        return None


def find_files_by_extension(directory: Path, extensions: Set[str]) -> List[Path]:
    """
    Find all files with specified extensions in a directory.

    Args:
        directory: Directory to search
        extensions: Set of file extensions (without dots)

    Returns:
        List of matching file paths
    """
    if not directory.exists():
        return []

    files = []
    for ext in extensions:
        pattern = f"**/*.{ext}"
        files.extend(directory.glob(pattern))

    return files


def get_project_structure(directory: Path) -> dict:
    """
    Get the directory structure of a project.

    Args:
        directory: Project directory

    Returns:
        Dictionary mapping relative paths to file types
    """
    if not directory.exists():
        return {}

    structure = {}

    for file_path in directory.rglob('*'):
        if file_path.is_file():
            try:
                relative_path = file_path.relative_to(directory)
                file_type = get_file_type(file_path)
                structure[str(relative_path)] = file_type
            except ValueError:
                # Skip files that can't be made relative
                continue

    return structure


def get_file_type(file_path: Path) -> str:
    """
    Determine file type based on extension.

    Args:
        file_path: File path

    Returns:
        File type string
    """
    extension = file_path.suffix.lower()

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
        '.yml': 'yaml',
        '.html': 'html',
        '.css': 'css'
    }

    return type_map.get(extension, 'file')


def validate_project_name(name: str) -> bool:
    """
    Validate if a project name is filesystem-safe.

    Args:
        name: Project name to validate

    Returns:
        True if valid, False otherwise
    """
    if not name or not name.strip():
        return False

    # Check length
    if len(name) > 50:
        return False

    # Check for filesystem-safe characters (letters, numbers, underscore, dash)
    if not re.match(r'^[a-zA-Z0-9_-]+$', name):
        return False

    # Windows reserved names
    reserved_names = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }

    if name.upper() in reserved_names:
        return False

    return True


def generate_project_name(request_id: UUID, prefix: str = "project") -> str:
    """
    Generate a filesystem-safe project name.

    Args:
        request_id: Request ID to base name on
        prefix: Name prefix

    Returns:
        Safe project name
    """
    short_id = str(request_id).replace('-', '')[:8]
    name = f"{prefix}_{short_id}"

    if validate_project_name(name):
        return name
    else:
        # Fallback to just the short ID
        return short_id


def cleanup_path_string(path_str: str) -> str:
    """
    Clean up a path string for cross-platform compatibility.

    Args:
        path_str: Path string to clean

    Returns:
        Cleaned path string
    """
    # Normalize path separators to forward slashes
    cleaned = path_str.replace('\\', '/')

    # Remove redundant separators
    while '//' in cleaned:
        cleaned = cleaned.replace('//', '/')

    # Remove leading/trailing slashes
    cleaned = cleaned.strip('/')

    return cleaned

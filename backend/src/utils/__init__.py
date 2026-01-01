"""
Utils Package

Utility functions and helpers for the backend application.
"""

from .error_utils import (
    get_error_message,
    map_openai_error,
    create_error_response,
    create_success_response,
    handle_service_error,
    ErrorContext
)

from .path_utils import (
    ensure_directory,
    get_project_directory,
    get_projects_base_dir,
    sanitize_filename,
    is_safe_path,
    get_relative_path,
    find_files_by_extension,
    get_project_structure,
    get_file_type,
    validate_project_name,
    generate_project_name,
    cleanup_path_string
)

from .uuid_utils import (
    generate_request_id,
    validate_uuid_string,
    parse_uuid,
    format_uuid,
    is_valid_uuid_format,
    generate_short_id,
    uuid_to_hex
)

__all__ = [
    # Error utilities
    'get_error_message',
    'map_openai_error',
    'create_error_response',
    'create_success_response',
    'handle_service_error',
    'ErrorContext',

    # Path utilities
    'ensure_directory',
    'get_project_directory',
    'get_projects_base_dir',
    'sanitize_filename',
    'is_safe_path',
    'get_relative_path',
    'find_files_by_extension',
    'get_project_structure',
    'get_file_type',
    'validate_project_name',
    'generate_project_name',
    'cleanup_path_string',

    # UUID utilities
    'generate_request_id',
    'validate_uuid_string',
    'parse_uuid',
    'format_uuid',
    'is_valid_uuid_format',
    'generate_short_id',
    'uuid_to_hex'
]

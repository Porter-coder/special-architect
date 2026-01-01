"""
UUID Utilities

Provides UUID generation and validation utilities for the application.
"""

import re
from typing import Optional
from uuid import UUID, uuid4


def generate_request_id() -> UUID:
    """
    Generate a new UUID for code generation requests.

    Returns:
        UUID: A new unique identifier
    """
    return uuid4()


def validate_uuid_string(uuid_str: str) -> bool:
    """
    Validate if a string is a valid UUID format.

    Args:
        uuid_str: String to validate

    Returns:
        bool: True if valid UUID format, False otherwise
    """
    try:
        UUID(uuid_str)
        return True
    except (ValueError, TypeError):
        return False


def parse_uuid(uuid_str: str) -> Optional[UUID]:
    """
    Parse a string into a UUID object.

    Args:
        uuid_str: String representation of UUID

    Returns:
        UUID object if valid, None if invalid
    """
    try:
        return UUID(uuid_str)
    except (ValueError, TypeError):
        return None


def format_uuid(uuid_obj: UUID) -> str:
    """
    Format a UUID object as a string.

    Args:
        uuid_obj: UUID object to format

    Returns:
        String representation of the UUID
    """
    return str(uuid_obj)


def is_valid_uuid_format(uuid_str: str) -> bool:
    """
    Check if a string matches UUID format (more strict than parse_uuid).

    Args:
        uuid_str: String to check

    Returns:
        bool: True if matches UUID format exactly
    """
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    return bool(uuid_pattern.match(uuid_str))


def generate_short_id(uuid_obj: UUID, length: int = 8) -> str:
    """
    Generate a short identifier from a UUID (first N characters).

    Args:
        uuid_obj: UUID object
        length: Length of short ID (default: 8)

    Returns:
        Short identifier string
    """
    return str(uuid_obj).replace('-', '')[:length]


def uuid_to_hex(uuid_obj: UUID) -> str:
    """
    Convert UUID to hexadecimal string (without dashes).

    Args:
        uuid_obj: UUID object

    Returns:
        Hexadecimal string representation
    """
    return uuid_obj.hex

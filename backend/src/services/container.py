"""
Service Container for AI Code Flow

Manages global service instances to avoid circular imports.
"""

import os
from typing import Optional

from dotenv import load_dotenv

from .ai_service import AIService
from .file_service import FileService
from .code_generation_service import CodeGenerationService


class ServiceContainer:
    """Container for managing service instances."""

    def __init__(self):
        self._ai_service: Optional[AIService] = None
        self._file_service: Optional[FileService] = None
        self._code_generation_service: Optional[CodeGenerationService] = None

    @property
    def ai_service(self) -> AIService:
        """Get AI service instance, creating if necessary."""
        if self._ai_service is None:
            self._ai_service = AIService()
        return self._ai_service

    @property
    def file_service(self) -> FileService:
        """Get file service instance, creating if necessary."""
        if self._file_service is None:
            self._file_service = FileService()
        return self._file_service

    @property
    def code_generation_service(self) -> CodeGenerationService:
        """Get code generation service instance, creating if necessary."""
        if self._code_generation_service is None:
            self._code_generation_service = CodeGenerationService(self.ai_service, self.file_service)
        return self._code_generation_service

    async def initialize_services(self) -> None:
        """Initialize all services asynchronously."""
        # Load environment variables from .env file
        load_dotenv()

        # Ensure services are created
        _ = self.ai_service
        _ = self.file_service

        # Validate AI service connection (non-blocking in development)
        try:
            connection_ok = await self.ai_service.validate_connection()
            if not connection_ok:
                print("Warning: AI service connection validation failed - will use mock responses if needed")
        except Exception as e:
            print(f"Warning: AI service validation error: {e} - will use mock responses if needed")

    def shutdown_services(self) -> None:
        """Shutdown all services."""
        # Currently no cleanup needed, but method ready for future use
        pass


# Global service container instance
container = ServiceContainer()


# Convenience functions for backward compatibility
def get_ai_service() -> AIService:
    """Get AI service instance."""
    return container.ai_service


def get_file_service() -> FileService:
    """Get file service instance."""
    return container.file_service


def get_code_generation_service() -> CodeGenerationService:
    """Get code generation service instance."""
    return container.code_generation_service

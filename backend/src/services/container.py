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
from .phase_manager import PhaseManager
from .project_service import ProjectService
from .documentation_service import DocumentationService
from .content_processor import ContentProcessor
from .dependency_analyzer import DependencyAnalyzer
from .compatibility_checker import CompatibilityChecker


class ServiceContainer:
    """Container for managing service instances."""

    def __init__(self):
        self._ai_service: Optional[AIService] = None
        self._file_service: Optional[FileService] = None
        self._phase_manager: Optional[PhaseManager] = None
        self._project_service: Optional[ProjectService] = None
        self._documentation_service: Optional[DocumentationService] = None
        self._content_processor: Optional[ContentProcessor] = None
        self._dependency_analyzer: Optional[DependencyAnalyzer] = None
        self._compatibility_checker: Optional[CompatibilityChecker] = None
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
    def phase_manager(self) -> PhaseManager:
        """Get phase manager instance, creating if necessary."""
        if self._phase_manager is None:
            self._phase_manager = PhaseManager(self.ai_service)
        return self._phase_manager

    @property
    def project_service(self) -> ProjectService:
        """Get project service instance, creating if necessary."""
        if self._project_service is None:
            self._project_service = ProjectService()
        return self._project_service

    @property
    def documentation_service(self) -> DocumentationService:
        """Get documentation service instance, creating if necessary."""
        if self._documentation_service is None:
            self._documentation_service = DocumentationService()
        return self._documentation_service

    @property
    def content_processor(self) -> ContentProcessor:
        """Get content processor instance, creating if necessary."""
        if self._content_processor is None:
            self._content_processor = ContentProcessor()
        return self._content_processor



    @property
    def dependency_analyzer(self) -> DependencyAnalyzer:
        """Get dependency analyzer instance, creating if necessary."""
        if self._dependency_analyzer is None:
            self._dependency_analyzer = DependencyAnalyzer()
        return self._dependency_analyzer

    @property
    def compatibility_checker(self) -> CompatibilityChecker:
        """Get compatibility checker instance, creating if necessary."""
        if self._compatibility_checker is None:
            self._compatibility_checker = CompatibilityChecker()
        return self._compatibility_checker

    @property
    def code_generation_service(self) -> CodeGenerationService:
        """Get code generation service instance, creating if necessary."""
        if self._code_generation_service is None:
            self._code_generation_service = CodeGenerationService(
                self.ai_service,
                self.phase_manager,
                self.project_service,
                self.documentation_service,
                self.content_processor,
                self.dependency_analyzer,
                self.compatibility_checker
            )
        return self._code_generation_service

    async def initialize_services(self) -> None:
        """Initialize all services asynchronously."""
        # Load environment variables from .env file
        load_dotenv()

        # Ensure services are created
        _ = self.ai_service
        _ = self.file_service
        _ = self.phase_manager
        _ = self.project_service
        _ = self.documentation_service
        _ = self.content_processor
        _ = self.dependency_analyzer
        _ = self.compatibility_checker

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

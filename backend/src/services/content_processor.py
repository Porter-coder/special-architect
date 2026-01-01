"""
Content Processor Service

Handles content cleaning and validation only at Phase 3 completion (FR-024).
Ensures generated code is properly cleaned and validated before delivery.
"""

import ast
import re
from typing import Dict, List, Optional, Tuple

from ..logging_config import get_logger
from ..models.process_phase import PhaseName

logger = get_logger()


class ContentProcessorError(Exception):
    """Base exception for content processor errors."""
    pass


class ContentValidationError(ContentProcessorError):
    """Exception for content validation failures."""
    pass


class ContentProcessor:
    """
    Content processor for Phase 3 completion validation.

    Only processes content after Phase 3 (implementation) is complete.
    Handles cleaning, validation, and quality assurance.
    """

    def __init__(self):
        """Initialize content processor."""
        logger.info("Content processor initialized")

    def should_process_content(self, current_phase: PhaseName) -> bool:
        """
        Determine if content should be processed based on current phase.

        Content processing only occurs at Phase 3 completion (FR-024).

        Args:
            current_phase: Current processing phase

        Returns:
            True if content should be processed, False otherwise
        """
        # Only process content after Phase 3 (implementation) is complete
        return current_phase == PhaseName.IMPLEMENT

    def process_content(self, content: str, phase: PhaseName) -> Dict[str, any]:
        """
        Process and validate content based on phase.

        Args:
            content: Raw content to process
            phase: Current phase

        Returns:
            Processing results dictionary

        Raises:
            ContentProcessorError: If processing fails
        """
        if not self.should_process_content(phase):
            return {
                "processed": False,
                "reason": f"Content processing skipped for phase {phase.value}",
                "content": content,
                "validation_results": {}
            }

        try:
            logger.info(f"Processing content for Phase {phase.value}")

            # Clean the content
            cleaned_content = self._clean_content(content)

            # Validate the content
            validation_results = self._validate_content(cleaned_content, phase)

            # Extract code blocks if it's implementation phase
            extracted_code = self._extract_code_blocks(cleaned_content) if phase == PhaseName.IMPLEMENT else {}

            result = {
                "processed": True,
                "original_content": content,
                "cleaned_content": cleaned_content,
                "extracted_code": extracted_code,
                "validation_results": validation_results,
                "phase": phase.value
            }

            logger.info(f"Content processing completed: {len(cleaned_content)} chars, {len(extracted_code)} code blocks")
            return result

        except Exception as e:
            logger.error(f"Content processing failed: {e}")
            raise ContentProcessorError(f"Content processing failed: {e}")

    def _clean_content(self, content: str) -> str:
        """
        Clean and normalize content.

        Args:
            content: Raw content

        Returns:
            Cleaned content
        """
        if not content:
            return ""

        # Remove excessive whitespace
        content = re.sub(r'\n{3,}', '\n\n', content)

        # Remove trailing whitespace from each line
        lines = [line.rstrip() for line in content.split('\n')]

        # Remove empty lines at start and end
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()

        return '\n'.join(lines)

    def _validate_content(self, content: str, phase: PhaseName) -> Dict[str, any]:
        """
        Validate content quality and correctness.

        Args:
            content: Content to validate
            phase: Current phase

        Returns:
            Validation results
        """
        results = {
            "is_valid": True,
            "issues": [],
            "metrics": self._calculate_content_metrics(content),
            "phase_specific_checks": {}
        }

        # Phase-specific validation
        if phase == PhaseName.IMPLEMENT:
            results["phase_specific_checks"] = self._validate_implementation_content(content)
        elif phase == PhaseName.PLAN:
            results["phase_specific_checks"] = self._validate_plan_content(content)
        elif phase == PhaseName.SPECIFY:
            results["phase_specific_checks"] = self._validate_specification_content(content)

        # Check for critical issues
        critical_issues = [issue for issue in results["issues"] if issue.get("severity") == "critical"]
        if critical_issues:
            results["is_valid"] = False

        return results

    def _validate_implementation_content(self, content: str) -> Dict[str, any]:
        """Validate implementation phase content (code)."""
        checks = {
            "has_code_blocks": False,
            "python_syntax_valid": False,
            "has_main_function": False,
            "has_imports": False,
            "code_blocks_extracted": 0
        }

        # Check for code blocks
        code_blocks = re.findall(r'```python\s*(.*?)\s*```', content, re.DOTALL)
        code_blocks.extend(re.findall(r'```\s*(.*?)\s*```', content, re.DOTALL))

        checks["has_code_blocks"] = len(code_blocks) > 0
        checks["code_blocks_extracted"] = len(code_blocks)

        # Validate Python syntax in code blocks
        if code_blocks:
            syntax_errors = []
            for i, block in enumerate(code_blocks):
                try:
                    ast.parse(block)
                    checks["python_syntax_valid"] = True
                except SyntaxError as e:
                    syntax_errors.append(f"Block {i+1}: {e}")

            if syntax_errors:
                checks["syntax_errors"] = syntax_errors
                checks["python_syntax_valid"] = False

        # Check for common code patterns
        all_code = '\n'.join(code_blocks)
        checks["has_main_function"] = 'def main' in all_code or 'if __name__ == "__main__"' in all_code
        checks["has_imports"] = 'import ' in all_code

        return checks

    def _validate_plan_content(self, content: str) -> Dict[str, any]:
        """Validate plan phase content (architecture and design)."""
        checks = {
            "has_architecture_info": False,
            "has_technology_choices": False,
            "has_implementation_steps": False,
            "word_count": 0
        }

        content_lower = content.lower()
        checks["has_architecture_info"] = any(term in content_lower for term in [
            'architecture', 'design', 'structure', 'component', 'module'
        ])
        checks["has_technology_choices"] = any(term in content_lower for term in [
            'python', 'pygame', 'library', 'framework', 'technology'
        ])
        checks["has_implementation_steps"] = any(term in content_lower for term in [
            'step', 'phase', 'implement', 'develop', 'create'
        ])

        # Count words (rough estimate)
        checks["word_count"] = len(content.split())

        return checks

    def _validate_specification_content(self, content: str) -> Dict[str, any]:
        """Validate specification phase content (requirements)."""
        checks = {
            "has_requirements": False,
            "has_functionality": False,
            "has_constraints": False,
            "word_count": 0
        }

        content_lower = content.lower()
        checks["has_requirements"] = any(term in content_lower for term in [
            'requirement', 'need', 'feature', 'functionality'
        ])
        checks["has_functionality"] = any(term in content_lower for term in [
            'function', 'feature', 'capability', 'behavior'
        ])
        checks["has_constraints"] = any(term in content_lower for term in [
            'constraint', 'limit', 'boundary', 'scope'
        ])

        checks["word_count"] = len(content.split())

        return checks

    def _extract_code_blocks(self, content: str) -> Dict[str, str]:
        """
        Extract code blocks from content.

        Args:
            content: Content with code blocks

        Returns:
            Dictionary mapping filenames to code content
        """
        files = {}

        # Extract Python code blocks with filenames
        # Pattern: ```python:filename.py\ncode\n```
        filename_pattern = r'```python:([^\n]+)\n(.*?)\n```'
        matches = re.findall(filename_pattern, content, re.DOTALL)

        for filename, code in matches:
            files[filename.strip()] = code.strip()

        # Extract generic code blocks (assume Python)
        if not files:
            code_blocks = re.findall(r'```python\s*(.*?)\s*```', content, re.DOTALL)
            if code_blocks:
                # Use the largest code block as main.py
                main_code = max(code_blocks, key=len)
                files["main.py"] = main_code.strip()

        # Fallback: extract any code blocks
        if not files:
            code_blocks = re.findall(r'```\s*(.*?)\s*```', content, re.DOTALL)
            if code_blocks:
                # Filter for Python-like content
                python_blocks = []
                for block in code_blocks:
                    if any(keyword in block for keyword in ['import ', 'def ', 'class ', 'if __name__']):
                        python_blocks.append(block)

                if python_blocks:
                    main_code = max(python_blocks, key=len)
                    files["main.py"] = main_code.strip()

        return files

    def _calculate_content_metrics(self, content: str) -> Dict[str, any]:
        """Calculate content quality metrics."""
        lines = content.split('\n')
        words = content.split()

        return {
            "total_characters": len(content),
            "total_lines": len(lines),
            "total_words": len(words),
            "average_line_length": len(content) / max(len(lines), 1),
            "average_word_length": sum(len(word) for word in words) / max(len(words), 1),
            "code_to_text_ratio": self._estimate_code_ratio(content)
        }

    def _estimate_code_ratio(self, content: str) -> float:
        """Estimate the ratio of code to natural language text."""
        # Simple heuristic: count lines that look like code vs text
        lines = content.split('\n')
        code_lines = 0
        text_lines = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Code-like patterns
            if any(pattern in line for pattern in [
                'import ', 'def ', 'class ', 'if ', 'for ', 'while ', 'return ',
                'print(', '{', '}', '(', ')', '[', ']', '=', '+', '-', '*', '/'
            ]):
                code_lines += 1
            else:
                text_lines += 1

        total_lines = code_lines + text_lines
        return code_lines / max(total_lines, 1)

    def validate_final_output(self, processed_content: Dict[str, any]) -> bool:
        """
        Final validation of processed content before delivery.

        Args:
            processed_content: Processed content from process_content()

        Returns:
            True if content passes final validation
        """
        if not processed_content.get("processed", False):
            return False

        validation = processed_content.get("validation_results", {})

        # Must pass basic validation
        if not validation.get("is_valid", False):
            return False

        # For implementation phase, must have valid Python code
        phase_checks = validation.get("phase_specific_checks", {})
        if processed_content.get("phase") == "implement":
            if not phase_checks.get("python_syntax_valid", False):
                logger.warning("Implementation content failed Python syntax validation")
                return False

            if not phase_checks.get("has_code_blocks", False):
                logger.warning("Implementation content has no code blocks")
                return False

        logger.info("Final content validation passed")
        return True

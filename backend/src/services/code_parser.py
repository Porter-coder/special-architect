"""
Code Parser Service

Handles Markdown parsing and Python AST validation for generated code.
Ensures code quality and extractability from AI responses.
"""

import ast
import re
from typing import Dict, List, Optional, Tuple

from ..logging_config import get_logger

logger = get_logger()


class CodeParserError(Exception):
    """Base exception for code parser errors."""
    pass


class MarkdownParseError(CodeParserError):
    """Exception for Markdown parsing errors."""
    pass


class ASTValidationError(CodeParserError):
    """Exception for AST validation errors."""
    pass


class CodeParser:
    """
    Parser for AI-generated code with Markdown and AST validation.

    Handles:
    - Markdown code block extraction
    - Python AST syntax validation
    - Code quality assessment
    - Error reporting and suggestions
    """

    def __init__(self):
        """Initialize code parser."""
        logger.info("Code parser initialized")

    def parse_markdown_code(self, markdown_text: str) -> Dict[str, str]:
        """
        Parse code blocks from Markdown text.

        Args:
            markdown_text: Markdown content with code blocks

        Returns:
            Dictionary mapping filenames to code content

        Raises:
            MarkdownParseError: If parsing fails
        """
        try:
            # Pattern to match code blocks with optional language and filename
            # Matches: ```python:main.py or ```python or ``` (unnamed)
            code_block_pattern = r'```(?:(\w+):?([^`\n]*))?\n?(.*?)\n?```'
            matches = re.findall(code_block_pattern, markdown_text, re.DOTALL)

            files = {}

            for language, filename, code in matches:
                # Clean up the code content
                code = code.strip()

                if not code:
                    continue

                # Determine filename if not provided
                if not filename:
                    if language == 'python':
                        filename = 'main.py'
                    else:
                        filename = f'file_{len(files) + 1}.{language or "txt"}'

                # Ensure proper extension
                if language == 'python' and not filename.endswith('.py'):
                    filename += '.py'

                files[filename] = code

            if not files:
                # If no code blocks found, treat the entire content as code
                logger.warning("No code blocks found in Markdown, treating as raw code")
                files['main.py'] = markdown_text.strip()

            logger.info(f"Parsed {len(files)} code files from Markdown")
            return files

        except Exception as e:
            logger.error(f"Markdown parsing failed: {e}")
            raise MarkdownParseError(f"Markdown 解析失败: {e}")

    def validate_python_code(self, code: str, filename: str = "unknown") -> Dict[str, any]:
        """
        Validate Python code using AST parsing.

        Args:
            code: Python code to validate
            filename: Filename for error reporting

        Returns:
            Validation result dictionary

        Raises:
            ASTValidationError: If validation fails
        """
        try:
            # Parse the code using AST
            tree = ast.parse(code, filename=filename)

            # Perform additional validation
            issues = self._analyze_code_quality(tree, code)

            result = {
                "valid": len(issues) == 0,
                "syntax_errors": [],
                "quality_issues": issues,
                "ast_tree": tree,
                "line_count": len(code.splitlines()),
                "character_count": len(code)
            }

            if result["valid"]:
                logger.info(f"Python code validation passed for {filename}")
            else:
                logger.warning(f"Python code validation found {len(issues)} issues for {filename}")

            return result

        except SyntaxError as e:
            error_info = {
                "filename": e.filename,
                "lineno": e.lineno,
                "offset": e.offset,
                "text": e.text,
                "message": str(e)
            }

            logger.error(f"Syntax error in {filename}: {e}")
            raise ASTValidationError(f"语法错误: {e}")

        except Exception as e:
            logger.error(f"AST validation failed for {filename}: {e}")
            raise ASTValidationError(f"AST 验证失败: {e}")

    def extract_and_validate_code(self, markdown_text: str) -> Dict[str, Dict]:
        """
        Extract code from Markdown and validate all Python files.

        Args:
            markdown_text: Markdown content with code

        Returns:
            Dictionary mapping filenames to validation results

        Raises:
            CodeParserError: If extraction or validation fails
        """
        try:
            # Extract code files from Markdown
            code_files = self.parse_markdown_code(markdown_text)

            validation_results = {}

            for filename, code in code_files.items():
                if filename.endswith('.py'):
                    # Validate Python files
                    validation_results[filename] = self.validate_python_code(code, filename)
                else:
                    # Non-Python files are considered valid
                    validation_results[filename] = {
                        "valid": True,
                        "syntax_errors": [],
                        "quality_issues": [],
                        "line_count": len(code.splitlines()),
                        "character_count": len(code)
                    }

            # Check if we have at least one valid Python file
            python_files = [f for f in validation_results.keys() if f.endswith('.py')]
            if python_files:
                valid_python_files = [
                    f for f in python_files
                    if validation_results[f]["valid"]
                ]
                if not valid_python_files:
                    raise CodeParserError("没有找到语法正确的 Python 文件")

            logger.info(f"Code extraction and validation completed: {len(validation_results)} files")
            return validation_results

        except (MarkdownParseError, ASTValidationError):
            raise
        except Exception as e:
            logger.error(f"Code extraction and validation failed: {e}")
            raise CodeParserError(f"代码提取和验证失败: {e}")

    def _analyze_code_quality(self, tree: ast.AST, code: str) -> List[Dict]:
        """
        Analyze code quality and identify potential issues.

        Args:
            tree: Parsed AST tree
            code: Original code string

        Returns:
            List of quality issues
        """
        issues = []

        # Check for common code quality issues
        lines = code.splitlines()

        # Check for missing imports
        has_main_function = any(
            isinstance(node, ast.FunctionDef) and node.name == 'main'
            for node in ast.walk(tree)
        )

        # Check for pygame import if it looks like a game
        has_pygame_import = any(
            isinstance(node, ast.Import) and any(alias.name == 'pygame' for alias in node.names)
            for node in ast.walk(tree)
        )

        # Basic heuristics for game code
        game_indicators = ['pygame', 'screen', 'snake', 'game', 'food']
        looks_like_game = any(indicator in code.lower() for indicator in game_indicators)

        if looks_like_game and not has_pygame_import:
            issues.append({
                "type": "missing_import",
                "severity": "high",
                "message": "游戏代码缺少 pygame 导入",
                "suggestion": "添加 'import pygame' 在文件顶部"
            })

        # Check for infinite loops without proper game loop structure
        has_game_loop = False
        for node in ast.walk(tree):
            if isinstance(node, ast.While):
                # Check if it's a game loop (while True with pygame events)
                if (isinstance(node.test, ast.NameConstant) and node.test.value is True):
                    has_game_loop = True
                    break

        if looks_like_game and not has_game_loop:
            issues.append({
                "type": "missing_game_loop",
                "severity": "medium",
                "message": "游戏代码缺少主游戏循环",
                "suggestion": "添加 'while True:' 主循环来处理游戏事件"
            })

        # Check for basic error handling
        has_try_except = any(isinstance(node, ast.Try) for node in ast.walk(tree))

        if not has_try_except:
            issues.append({
                "type": "missing_error_handling",
                "severity": "low",
                "message": "代码缺少错误处理",
                "suggestion": "考虑添加 try-except 块来处理运行时错误"
            })

        # Check line length (basic style check)
        long_lines = [i for i, line in enumerate(lines, 1) if len(line) > 100]
        if long_lines:
            issues.append({
                "type": "long_lines",
                "severity": "low",
                "message": f"发现 {len(long_lines)} 行代码超过 100 个字符",
                "suggestion": "考虑将长行拆分为多行以提高可读性"
            })

        return issues

    def clean_code_output(self, code: str) -> str:
        """
        Clean and normalize generated code output.

        Args:
            code: Raw code string

        Returns:
            Cleaned code string
        """
        # Remove common artifacts from AI generation
        lines = code.splitlines()

        # Remove markdown code block markers if present
        if lines and lines[0].strip().startswith('```'):
            lines = lines[1:]
        if lines and lines[-1].strip().endswith('```'):
            lines = lines[:-1]

        # Remove empty lines at start and end
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()

        # Normalize indentation (basic fix for common AI issues)
        if lines:
            # Find minimum indentation of non-empty lines
            min_indent = min(
                len(line) - len(line.lstrip())
                for line in lines
                if line.strip()
            )

            # Remove common indentation
            if min_indent > 0:
                lines = [line[min_indent:] for line in lines]

        return '\n'.join(lines)

    def get_code_stats(self, code: str) -> Dict[str, int]:
        """
        Get basic statistics about code.

        Args:
            code: Code string

        Returns:
            Statistics dictionary
        """
        lines = code.splitlines()

        return {
            "total_lines": len(lines),
            "code_lines": len([line for line in lines if line.strip() and not line.strip().startswith('#')]),
            "comment_lines": len([line for line in lines if line.strip().startswith('#')]),
            "empty_lines": len([line for line in lines if not line.strip()]),
            "max_line_length": max(len(line) for line in lines) if lines else 0
        }

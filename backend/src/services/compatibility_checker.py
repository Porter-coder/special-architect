"""
Windows Compatibility Checker

Validates generated code for Windows compatibility issues and provides fixes.
Checks for Windows-specific path handling, file permissions, and system calls.
"""

import ast
import os
import re
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum

from ..logging_config import get_logger

logger = get_logger()


class CompatibilityIssue(Enum):
    """Types of Windows compatibility issues."""
    PATH_SEPARATOR = "path_separator"
    FILE_PERMISSION = "file_permission"
    SYSTEM_CALL = "system_call"
    ENCODING = "encoding"
    LINE_ENDING = "line_ending"
    EXECUTABLE_PATH = "executable_path"
    LIBRARY_AVAILABILITY = "library_availability"


@dataclass
class CompatibilityWarning:
    """Warning about potential Windows compatibility issue."""
    issue_type: CompatibilityIssue
    line_number: Optional[int]
    code_snippet: str
    description: str
    severity: str  # "low", "medium", "high"
    suggested_fix: str


class CompatibilityChecker:
    """Service for checking Windows compatibility of generated code."""

    def __init__(self):
        self.windows_issues = self._build_windows_compatibility_checks()
        self.path_patterns = self._build_path_patterns()
        self.system_call_patterns = self._build_system_call_patterns()

    def _build_windows_compatibility_checks(self) -> Dict[str, Dict]:
        """Build patterns for Windows compatibility issues."""
        return {
            # Path separator issues
            "hardcoded_separator": {
                "pattern": r"['/']",
                "description": "使用硬编码的正斜杠路径分隔符",
                "severity": "medium",
                "fix": "使用os.path.join()或pathlib.Path代替硬编码路径"
            },
            "windows_path": {
                "pattern": r"[A-Za-z]:[/\\\\]",
                "description": "使用Windows风格的绝对路径",
                "severity": "low",
                "fix": "使用相对路径或跨平台路径处理"
            },

            # File permission issues
            "chmod_call": {
                "pattern": r"os\.chmod|stat\.S_I",
                "description": "使用Unix风格的文件权限设置",
                "severity": "high",
                "fix": "检查Windows文件权限处理或使用try/except包装"
            },

            # System calls
            "unix_command": {
                "pattern": r"subprocess\.call.*(?:ls|cat|grep|awk|sed|chmod|chown)",
                "description": "使用Unix命令行工具",
                "severity": "high",
                "fix": "使用Python标准库或检查操作系统类型"
            },

            # Library availability
            "unix_library": {
                "pattern": r"(?:import|from)\s+(?:fcntl|termios|pwd|grp|resource)",
                "description": "导入Unix特定库",
                "severity": "high",
                "fix": "检查平台兼容性或提供Windows替代方案"
            }
        }

    def _build_path_patterns(self) -> List[Tuple[str, str]]:
        """Build patterns for path-related issues."""
        return [
            (r"open\(['\"]([^'\"]*?)['\"]", "文件路径在open()中"),
            (r"with open\(['\"]([^'\"]*?)['\"]", "文件路径在open()中"),
            (r"os\.path\.join\(['\"]([^'\"]*?)['\"]", "路径拼接"),
            (r"pathlib\.Path\(['\"]([^'\"]*?)['\"]", "Path对象创建"),
        ]

    def _build_system_call_patterns(self) -> List[Tuple[str, str]]:
        """Build patterns for system call issues."""
        return [
            (r"subprocess\.(?:run|call|Popen)", "系统命令调用"),
            (r"os\.system|os\.popen", "系统命令执行"),
            (r"os\.exec", "进程替换"),
        ]

    def check_compatibility(self, code: str, filename: str = "generated_code.py") -> List[CompatibilityWarning]:
        """
        Check Python code for Windows compatibility issues.

        Args:
            code: Python code to check
            filename: Name of the file being checked

        Returns:
            List of compatibility warnings
        """
        logger.info(f"Checking Windows compatibility for {filename}")
        warnings = []

        # Parse the code to get line information
        try:
            tree = ast.parse(code)
        except SyntaxError:
            logger.warning(f"Could not parse {filename} for compatibility checking")
            return warnings

        lines = code.split('\n')

        # Check for various compatibility issues
        warnings.extend(self._check_path_issues(code, lines))
        warnings.extend(self._check_system_call_issues(code, lines))
        warnings.extend(self._check_import_issues(tree, lines))
        warnings.extend(self._check_file_operation_issues(tree, lines))

        logger.info(f"Found {len(warnings)} compatibility warnings")
        return warnings

    def _check_path_issues(self, code: str, lines: List[str]) -> List[CompatibilityWarning]:
        """Check for path-related compatibility issues."""
        warnings = []

        for line_num, line in enumerate(lines, 1):
            # Check for hardcoded path separators
            if re.search(r"['/']", line) and not re.search(r"(?:http|https|ftp)://", line):
                # More sophisticated check - look for actual path usage
                if re.search(r"(?:open|join|path|Path).*['/']", line):
                    warnings.append(CompatibilityWarning(
                        issue_type=CompatibilityIssue.PATH_SEPARATOR,
                        line_number=line_num,
                        code_snippet=line.strip(),
                        description="使用硬编码的路径分隔符，可能在Windows上不工作",
                        severity="medium",
                        suggested_fix="使用os.path.join()或pathlib.Path()"
                    ))

            # Check for Windows-style absolute paths
            if re.search(r"[A-Za-z]:[/\\\\]", line):
                warnings.append(CompatibilityWarning(
                    issue_type=CompatibilityIssue.EXECUTABLE_PATH,
                    line_number=line_num,
                    code_snippet=line.strip(),
                    description="使用Windows风格的绝对路径",
                    severity="low",
                    suggested_fix="使用相对路径或os.path.abspath()"
                ))

        return warnings

    def _check_system_call_issues(self, code: str, lines: List[str]) -> List[CompatibilityWarning]:
        """Check for system call compatibility issues."""
        warnings = []

        unix_commands = ["ls", "cat", "grep", "awk", "sed", "chmod", "chown", "ps", "kill", "top"]

        for line_num, line in enumerate(lines, 1):
            # Check for subprocess calls with Unix commands
            if "subprocess" in line:
                for cmd in unix_commands:
                    if re.search(rf"['\"]{cmd}['\"]", line):
                        warnings.append(CompatibilityWarning(
                            issue_type=CompatibilityIssue.SYSTEM_CALL,
                            line_number=line_num,
                            code_snippet=line.strip(),
                            description=f"使用Unix命令 '{cmd}'，在Windows上可能不可用",
                            severity="high",
                            suggested_fix=f"使用Python标准库替代，或检查平台类型：if os.name != 'nt': ..."
                        ))

            # Check for os.system with Unix commands
            if "os.system" in line or "os.popen" in line:
                for cmd in unix_commands:
                    if cmd in line:
                        warnings.append(CompatibilityWarning(
                            issue_type=CompatibilityIssue.SYSTEM_CALL,
                            line_number=line_num,
                            code_snippet=line.strip(),
                            description=f"使用Unix系统命令，可能在Windows上失败",
                            severity="high",
                            suggested_fix="使用subprocess模块并检查操作系统类型"
                        ))

        return warnings

    def _check_import_issues(self, tree: ast.AST, lines: List[str]) -> List[CompatibilityWarning]:
        """Check for import-related compatibility issues."""
        warnings = []
        unix_libs = ["fcntl", "termios", "pwd", "grp", "resource", "curses"]

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in unix_libs:
                        line_num = getattr(node, 'lineno', None)
                        warnings.append(CompatibilityWarning(
                            issue_type=CompatibilityIssue.LIBRARY_AVAILABILITY,
                            line_number=line_num,
                            code_snippet=f"import {alias.name}",
                            description=f"导入Unix特定库 '{alias.name}'，在Windows上不可用",
                            severity="high",
                            suggested_fix=f"条件导入：try: import {alias.name} except ImportError: ..."
                        ))

            elif isinstance(node, ast.ImportFrom):
                if node.module in unix_libs:
                    line_num = getattr(node, 'lineno', None)
                    warnings.append(CompatibilityWarning(
                        issue_type=CompatibilityIssue.LIBRARY_AVAILABILITY,
                        line_number=line_num,
                        code_snippet=f"from {node.module} import ...",
                        description=f"从Unix特定模块 '{node.module}' 导入，在Windows上不可用",
                        severity="high",
                        suggested_fix=f"条件导入：try: from {node.module} import ... except ImportError: ..."
                    ))

        return warnings

    def _check_file_operation_issues(self, tree: ast.AST, lines: List[str]) -> List[CompatibilityWarning]:
        """Check for file operation compatibility issues."""
        warnings = []

        for node in ast.walk(tree):
            # Check for chmod calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if (isinstance(node.func.value, ast.Name) and
                        node.func.value.id == "os" and
                        node.func.attr == "chmod"):
                        line_num = getattr(node, 'lineno', None)
                        warnings.append(CompatibilityWarning(
                            issue_type=CompatibilityIssue.FILE_PERMISSION,
                            line_number=line_num,
                            code_snippet="os.chmod(...)",
                            description="使用Unix风格的文件权限设置",
                            severity="high",
                            suggested_fix="检查Windows权限处理，或使用try/except包装"
                        ))

            # Check for file operations with potential permission issues
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "open":
                    # Check if open call has mode that might cause issues
                    if len(node.args) >= 2:
                        mode_arg = node.args[1]
                        if isinstance(mode_arg, ast.Constant):
                            mode = mode_arg.value
                            if "x" in str(mode):  # Exclusive creation mode
                                line_num = getattr(node, 'lineno', None)
                                warnings.append(CompatibilityWarning(
                                    issue_type=CompatibilityIssue.FILE_PERMISSION,
                                    line_number=line_num,
                                    code_snippet=f"open(..., '{mode}', ...)",
                                    description="使用'x'模式可能在某些Windows版本上有问题",
                                    severity="medium",
                                    suggested_fix="使用'w'模式并检查文件是否存在"
                                ))

        return warnings

    def generate_compatibility_report(self, warnings: List[CompatibilityWarning]) -> str:
        """Generate a human-readable compatibility report."""
        if not warnings:
            return "✅ 代码与Windows兼容，无发现兼容性问题。"

        report_lines = ["⚠️  Windows兼容性报告", "=" * 40, ""]

        # Group warnings by severity
        by_severity = {"high": [], "medium": [], "low": []}
        for warning in warnings:
            by_severity[warning.severity].append(warning)

        # Report high severity issues first
        for severity in ["high", "medium", "low"]:
            level_warnings = by_severity[severity]
            if level_warnings:
                severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}[severity]
                report_lines.append(f"{severity_emoji} {severity.upper()} SEVERITY ISSUES ({len(level_warnings)}):")
                report_lines.append("")

                for warning in level_warnings:
                    report_lines.append(f"  行 {warning.line_number or '?'}：{warning.description}")
                    report_lines.append(f"    代码：{warning.code_snippet}")
                    report_lines.append(f"    建议：{warning.suggested_fix}")
                    report_lines.append("")

        # Summary
        total_issues = len(warnings)
        high_count = len(by_severity["high"])
        medium_count = len(by_severity["medium"])
        low_count = len(by_severity["low"])

        report_lines.append("=" * 40)
        report_lines.append("📊 兼容性摘要:")
        report_lines.append(f"   总问题数：{total_issues}")
        report_lines.append(f"   🔴 高严重性：{high_count}")
        report_lines.append(f"   🟡 中严重性：{medium_count}")
        report_lines.append(f"   🟢 低严重性：{low_count}")

        if high_count > 0:
            report_lines.append("\n⚠️  建议在Windows上测试高严重性问题。")
        else:
            report_lines.append("\n✅ 代码应该可以在Windows上正常运行。")

        return "\n".join(report_lines)

    def apply_compatibility_fixes(self, code: str, warnings: List[CompatibilityWarning]) -> str:
        """
        Attempt to automatically fix some compatibility issues.

        Args:
            code: Original code
            warnings: List of compatibility warnings

        Returns:
            Code with automatic fixes applied
        """
        fixed_code = code

        # Apply fixes for known patterns
        for warning in warnings:
            if warning.issue_type == CompatibilityIssue.PATH_SEPARATOR:
                # Replace hardcoded / with os.path.join patterns
                # This is a basic fix - more sophisticated fixes would require AST manipulation
                if "open(" in warning.code_snippet and "/" in warning.code_snippet:
                    # Add a comment about Windows compatibility
                    fixed_code = fixed_code.replace(
                        warning.code_snippet,
                        f"# 注意：Windows兼容性 - {warning.code_snippet}"
                    )

        return fixed_code

    def check_platform_compatibility(self, dependencies: List[str]) -> List[str]:
        """
        Check if listed dependencies are compatible with Windows.

        Args:
            dependencies: List of package names

        Returns:
            List of compatibility warnings for dependencies
        """
        warnings = []

        # Known packages with Windows compatibility issues
        windows_problematic = {
            "pygame": "在某些Windows版本上可能需要额外的SDL依赖",
            "opencv-python": "可能需要Visual C++ Redistributable",
            "tensorflow": "GPU版本在Windows上配置复杂",
            "torch": "某些版本在Windows上有CUDA兼容性问题"
        }

        for dep in dependencies:
            if dep in windows_problematic:
                warnings.append(f"{dep}: {windows_problematic[dep]}")

        return warnings

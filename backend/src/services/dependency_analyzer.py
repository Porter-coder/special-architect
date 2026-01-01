"""
Dependency Analysis Service

Analyzes code to determine required dependencies and generates requirements.txt files.
Supports automatic dependency detection and version management.
"""

import re
import ast
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from ..logging_config import get_logger

logger = get_logger()


class DependencyType(Enum):
    """Types of dependencies."""
    PIP_PACKAGE = "pip"
    SYSTEM_PACKAGE = "system"
    BUILT_IN = "built_in"


@dataclass
class DependencyInfo:
    """Information about a dependency."""
    name: str
    version_spec: Optional[str]
    type: DependencyType
    description: str
    required: bool = True


class DependencyAnalyzer:
    """Service for analyzing code dependencies."""

    def __init__(self):
        self.known_packages = self._build_known_packages()
        self.import_patterns = self._build_import_patterns()

    def _build_known_packages(self) -> Dict[str, DependencyInfo]:
        """Build database of known Python packages."""
        return {
            # Web frameworks
            "fastapi": DependencyInfo("fastapi", ">=0.100.0", DependencyType.PIP_PACKAGE,
                                    "现代化的Web框架，支持异步和类型提示"),
            "uvicorn": DependencyInfo("uvicorn", ">=0.23.0", DependencyType.PIP_PACKAGE,
                                    "ASGI服务器，用于运行FastAPI应用"),
            "flask": DependencyInfo("flask", ">=2.3.0", DependencyType.PIP_PACKAGE,
                                  "轻量级Web框架"),
            "django": DependencyInfo("django", ">=4.2.0", DependencyType.PIP_PACKAGE,
                                   "全功能Web框架"),

            # Game libraries
            "pygame": DependencyInfo("pygame", ">=2.5.0", DependencyType.PIP_PACKAGE,
                                   "Python游戏开发库"),
            "arcade": DependencyInfo("arcade", ">=2.6.0", DependencyType.PIP_PACKAGE,
                                   "现代2D游戏框架"),

            # Data processing
            "pandas": DependencyInfo("pandas", ">=2.0.0", DependencyType.PIP_PACKAGE,
                                   "数据分析和处理库"),
            "numpy": DependencyInfo("numpy", ">=1.24.0", DependencyType.PIP_PACKAGE,
                                  "科学计算基础库"),
            "matplotlib": DependencyInfo("matplotlib", ">=3.7.0", DependencyType.PIP_PACKAGE,
                                       "数据可视化库"),
            "seaborn": DependencyInfo("seaborn", ">=0.12.0", DependencyType.PIP_PACKAGE,
                                    "统计数据可视化库"),
            "scikit-learn": DependencyInfo("scikit-learn", ">=1.3.0", DependencyType.PIP_PACKAGE,
                                         "机器学习库"),
            "tensorflow": DependencyInfo("tensorflow", ">=2.13.0", DependencyType.PIP_PACKAGE,
                                       "深度学习框架"),
            "torch": DependencyInfo("torch", ">=2.0.0", DependencyType.PIP_PACKAGE,
                                  "PyTorch深度学习框架"),

            # Utilities
            "click": DependencyInfo("click", ">=8.1.0", DependencyType.PIP_PACKAGE,
                                  "命令行界面创建工具"),
            "rich": DependencyInfo("rich", ">=13.5.0", DependencyType.PIP_PACKAGE,
                                 "富文本和美化终端输出"),
            "requests": DependencyInfo("requests", ">=2.31.0", DependencyType.PIP_PACKAGE,
                                     "HTTP请求库"),
            "pillow": DependencyInfo("pillow", ">=10.0.0", DependencyType.PIP_PACKAGE,
                                   "图像处理库"),
            "pyyaml": DependencyInfo("pyyaml", ">=6.0", DependencyType.PIP_PACKAGE,
                                   "YAML文件处理"),

            # Testing
            "pytest": DependencyInfo("pytest", ">=7.4.0", DependencyType.PIP_PACKAGE,
                                   "Python测试框架"),
            "pytest-asyncio": DependencyInfo("pytest-asyncio", ">=0.21.0", DependencyType.PIP_PACKAGE,
                                           "异步测试支持"),

            # Built-in modules (don't need installation)
            "os": DependencyInfo("os", None, DependencyType.BUILT_IN,
                               "操作系统接口模块"),
            "sys": DependencyInfo("sys", None, DependencyType.BUILT_IN,
                                "系统相关功能"),
            "json": DependencyInfo("json", None, DependencyType.BUILT_IN,
                                 "JSON编码解码"),
            "datetime": DependencyInfo("datetime", None, DependencyType.BUILT_IN,
                                     "日期时间处理"),
            "math": DependencyInfo("math", None, DependencyType.BUILT_IN,
                                 "数学函数"),
            "random": DependencyInfo("random", None, DependencyType.BUILT_IN,
                                   "随机数生成"),
            "re": DependencyInfo("re", None, DependencyType.BUILT_IN,
                               "正则表达式"),
            "pathlib": DependencyInfo("pathlib", None, DependencyType.BUILT_IN,
                                    "路径操作"),
            "typing": DependencyInfo("typing", None, DependencyType.BUILT_IN,
                                   "类型提示"),
            "turtle": DependencyInfo("turtle", None, DependencyType.BUILT_IN,
                                   "海龟绘图"),
        }

    def _build_import_patterns(self) -> Dict[str, str]:
        """Build comprehensive patterns to map imports to correct PyPI package names."""
        return {
            # === WEB FRAMEWORKS ===
            "fastapi": "fastapi",
            "uvicorn": "uvicorn",
            "flask": "flask",
            "django": "django",
            "tornado": "tornado",
            "bottle": "bottle",
            "cherrypy": "cherrypy",

            # === DATA SCIENCE & ANALYSIS ===
            "pandas": "pandas",
            "numpy": "numpy",
            "matplotlib": "matplotlib",
            "seaborn": "seaborn",
            "plotly": "plotly",
            "bokeh": "bokeh",
            "scipy": "scipy",
            "statsmodels": "statsmodels",
            "sklearn": "scikit-learn",
            "skimage": "scikit-image",

            # === MACHINE LEARNING ===
            "tensorflow": "tensorflow",
            "torch": "torch",
            "torchvision": "torchvision",
            "torchaudio": "torchaudio",
            "transformers": "transformers",
            "keras": "keras",
            "xgboost": "xgboost",
            "lightgbm": "lightgbm",
            "catboost": "catboost",

            # === IMAGE PROCESSING ===
            "PIL": "pillow",
            "Pillow": "pillow",
            "cv2": "opencv-python",
            "skimage": "scikit-image",
            "imageio": "imageio",
            "scikit-image": "scikit-image",

            # === GUI & GAME DEVELOPMENT ===
            "pygame": "pygame",
            "arcade": "arcade",
            "pymunk": "pymunk",
            "tkinter": "tk",  # Built-in, but sometimes needs explicit
            "PyQt5": "pyqt5",
            "PyQt6": "pyqt6",
            "PySide2": "pyside2",
            "PySide6": "pyside6",
            "kivy": "kivy",
            "turtle": "turtle",  # Built-in

            # === CLI TOOLS ===
            "click": "click",
            "rich": "rich",
            "typer": "typer",
            "fire": "fire",
            "argparse": "argparse",  # Built-in
            "optparse": "optparse",  # Built-in

            # === HTTP & NETWORKING ===
            "requests": "requests",
            "httpx": "httpx",
            "aiohttp": "aiohttp",
            "urllib3": "urllib3",
            "beautifulsoup4": "beautifulsoup4",
            "bs4": "beautifulsoup4",
            "lxml": "lxml",
            "selenium": "selenium",

            # === DATABASE ===
            "sqlite3": "sqlite3",  # Built-in
            "psycopg2": "psycopg2",
            "pymysql": "pymysql",
            "sqlalchemy": "sqlalchemy",
            "redis": "redis",
            "pymongo": "pymongo",
            "peewee": "peewee",

            # === ASYNC & CONCURRENT ===
            "asyncio": "asyncio",  # Built-in
            "threading": "threading",  # Built-in
            "multiprocessing": "multiprocessing",  # Built-in
            "concurrent": "concurrent",  # Built-in
            "gevent": "gevent",
            "celery": "celery",

            # === TESTING ===
            "pytest": "pytest",
            "unittest": "unittest",  # Built-in
            "doctest": "doctest",  # Built-in

            # === UTILITIES ===
            "yaml": "pyyaml",
            "json": "json",  # Built-in
            "pickle": "pickle",  # Built-in
            "csv": "csv",  # Built-in
            "os": "os",  # Built-in
            "sys": "sys",  # Built-in
            "re": "re",  # Built-in
            "datetime": "datetime",  # Built-in
            "random": "random",  # Built-in
            "collections": "collections",  # Built-in
            "itertools": "itertools",  # Built-in
            "functools": "functools",  # Built-in

            # === FILE HANDLING ===
            "pathlib": "pathlib",  # Built-in (Python 3.4+)
            "shutil": "shutil",  # Built-in
            "glob": "glob",  # Built-in
            "zipfile": "zipfile",  # Built-in
            "tarfile": "tarfile",  # Built-in

            # === MATH & SCIENCE ===
            "math": "math",  # Built-in
            "cmath": "cmath",  # Built-in
            "decimal": "decimal",  # Built-in
            "fractions": "fractions",  # Built-in
            "sympy": "sympy",
            "networkx": "networkx",

            # === VISUALIZATION ===
            "dash": "dash",
            "streamlit": "streamlit",
            "gradio": "gradio",
            "panel": "panel",

            # === SECURITY ===
            "cryptography": "cryptography",
            "bcrypt": "bcrypt",
            "hashlib": "hashlib",  # Built-in
            "secrets": "secrets",  # Built-in
            "ssl": "ssl",  # Built-in

            # === CONFIGURATION ===
            "configparser": "configparser",  # Built-in
            "toml": "toml",
            "python-dotenv": "python-dotenv",

            # === LOGGING ===
            "logging": "logging",  # Built-in
            "loguru": "loguru",

            # === DEVELOPMENT TOOLS ===
            "mypy": "mypy",
            "black": "black",
            "flake8": "flake8",
            "pylint": "pylint",

            # === COMMON SUBMODULES ===
            "mpl_toolkits": "matplotlib",  # matplotlib toolkits
            "sklearn": "scikit-learn",     # sklearn is scikit-learn
            "cv2": "opencv-python",        # opencv import
            "Image": "pillow",            # PIL.Image
        }

    def analyze_code_dependencies(self, code: str) -> List[DependencyInfo]:
        """
        Analyze Python code to determine required dependencies.

        Args:
            code: Python code to analyze

        Returns:
            List of detected dependencies
        """
        logger.info("Analyzing code dependencies...")

        dependencies = []
        seen_packages = set()

        try:
            # Parse the AST to find imports
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    # Handle 'import module' statements
                    for alias in node.names:
                        package = self._resolve_import(alias.name)
                        if package and package not in seen_packages:
                            dep_info = self.known_packages.get(package)
                            if dep_info:
                                dependencies.append(dep_info)
                                seen_packages.add(package)

                elif isinstance(node, ast.ImportFrom):
                    # Handle 'from module import ...' statements
                    if node.module:
                        package = self._resolve_import(node.module)
                        if package and package not in seen_packages:
                            dep_info = self.known_packages.get(package)
                            if dep_info:
                                dependencies.append(dep_info)
                                seen_packages.add(package)

        except SyntaxError as e:
            logger.warning(f"Could not parse code for dependency analysis: {e}")
            # Fall back to regex-based analysis
            fallback_deps = self._fallback_import_analysis(code)
            dependencies.extend(fallback_deps)

        # Convert set to sorted list
        result = sorted(dependencies, key=lambda x: x.name)
        logger.info(f"Found {len(result)} dependencies")
        return result

    def _resolve_import(self, import_name: str) -> Optional[str]:
        """Resolve import name to package name."""
        # Direct match
        if import_name in self.import_patterns:
            return self.import_patterns[import_name]

        # Check if it's a submodule (e.g., sklearn.model_selection -> sklearn)
        base_module = import_name.split('.')[0]
        if base_module in self.import_patterns:
            return self.import_patterns[base_module]

        # Check known packages
        if import_name in self.known_packages:
            return import_name

        return None

    def _fallback_import_analysis(self, code: str) -> List[DependencyInfo]:
        """Fallback regex-based import analysis."""
        dependencies = []
        seen_packages = set()

        # Find import statements
        import_pattern = r'^(?:from\s+(\w+)|import\s+(\w+))'
        matches = re.findall(import_pattern, code, re.MULTILINE)

        for match in matches:
            module_name = match[0] or match[1]  # from module or import module
            package = self._resolve_import(module_name)
            if package and package not in seen_packages:
                dep_info = self.known_packages.get(package)
                if dep_info:
                    dependencies.append(dep_info)
                    seen_packages.add(package)

        return dependencies

    def _validate_self_containment(self, code_files: Dict[str, str]) -> List[str]:
        """
        Validate that all local imports have corresponding generated files.

        Args:
            code_files: Dict mapping file paths to code content

        Returns:
            List of missing local file names
        """
        missing_files = []
        local_imports = set()

        # Collect all local imports across all files
        for file_path, code in code_files.items():
            if file_path.endswith('.py'):
                file_local_imports = self._find_local_imports(code)
                local_imports.update(file_local_imports)

        # Check if each local import has a corresponding file
        existing_files = {path.split('.')[0] for path in code_files.keys()}  # Remove .py extension

        for local_import in local_imports:
            if local_import not in existing_files and f"{local_import}.py" not in code_files:
                missing_files.append(f"{local_import}.py")

        return missing_files

    def _find_local_imports(self, code: str) -> Set[str]:
        """Find local module imports in code (relative imports and same-directory imports)."""
        local_imports = set()

        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_name = alias.name
                        # Check if it's a local import (no dots for absolute, or relative)
                        if '.' not in module_name and module_name not in self.import_patterns:
                            local_imports.add(module_name)

                elif isinstance(node, ast.ImportFrom):
                    if node.module and '.' not in node.module and node.module not in self.import_patterns:
                        local_imports.add(node.module)

        except SyntaxError:
            # If code has syntax errors, try regex fallback
            import_pattern = r'^(?:from\s+(\w+)\s+import|import\s+(\w+))'
            matches = re.findall(import_pattern, code, re.MULTILINE)
            for match in matches:
                module_name = match[0] or match[1]
                if '.' not in module_name and module_name not in self.import_patterns:
                    local_imports.add(module_name)

        return local_imports

    def generate_requirements_txt(self, dependencies: List[DependencyInfo],
                                include_versions: bool = True) -> str:
        """
        Generate requirements.txt content from dependencies.

        Args:
            dependencies: List of dependency information
            include_versions: Whether to include version specifications

        Returns:
            requirements.txt content
        """
        lines = []

        # Add header comment
        lines.append("# AI Code Flow Generated Requirements")
        lines.append("# Auto-generated dependency list")
        lines.append("")

        # Add dependencies
        for dep in dependencies:
            if dep.type == DependencyType.PIP_PACKAGE:
                if include_versions and dep.version_spec:
                    line = f"{dep.name}{dep.version_spec}"
                else:
                    line = dep.name
                lines.append(line)

        # Add testing dependencies if pytest is included
        has_pytest = any(dep.name == "pytest" for dep in dependencies)
        if has_pytest:
            lines.append("")
            lines.append("# Testing dependencies")
            lines.append("pytest>=7.4.0")
            lines.append("pytest-asyncio>=0.21.0")

        return "\n".join(lines)

    def validate_dependencies(self, dependencies: List[DependencyInfo]) -> Dict[str, List[str]]:
        """
        Validate dependency list for conflicts and missing requirements.

        Args:
            dependencies: List of dependencies to validate

        Returns:
            Dict with validation results (warnings, errors, suggestions)
        """
        warnings = []
        errors = []
        suggestions = []

        # Check for known conflicts
        package_names = [dep.name for dep in dependencies]

        # TensorFlow and PyTorch might conflict in some environments
        if "tensorflow" in package_names and "torch" in package_names:
            warnings.append("TensorFlow和PyTorch同时使用可能导致CUDA版本冲突")

        # Check for missing common dependencies
        if "fastapi" in package_names and "uvicorn" not in package_names:
            suggestions.append("FastAPI应用建议添加uvicorn作为ASGI服务器")

        if "pandas" in package_names and "numpy" not in package_names:
            suggestions.append("pandas应用通常也需要numpy")

        # Check for version conflicts (basic check)
        version_conflicts = []
        name_counts = {}
        for dep in dependencies:
            if dep.name in name_counts:
                version_conflicts.append(f"重复依赖: {dep.name}")
            name_counts[dep.name] = name_counts.get(dep.name, 0) + 1

        if version_conflicts:
            warnings.extend(version_conflicts)

        return {
            "warnings": warnings,
            "errors": errors,
            "suggestions": suggestions
        }

    def get_package_info(self, package_name: str) -> Optional[DependencyInfo]:
        """Get information about a specific package."""
        return self.known_packages.get(package_name)

    def add_package_info(self, package_name: str, info: DependencyInfo):
        """Add information about a new package."""
        self.known_packages[package_name] = info
        logger.info(f"Added package info for {package_name}")

    def get_all_packages(self) -> Dict[str, DependencyInfo]:
        """Get all known packages."""
        return self.known_packages.copy()

    def analyze_project_dependencies(self, code_files: Dict[str, str]) -> Tuple[List[DependencyInfo], str]:
        """
        Analyze all code files in a project to determine dependencies.

        Args:
            code_files: Dict mapping file paths to code content

        Returns:
            Tuple of (dependencies, requirements_txt_content)
        """
        all_dependencies = []
        seen_packages = set()

        for file_path, code in code_files.items():
            if file_path.endswith('.py'):
                file_deps = self.analyze_code_dependencies(code)
                for dep in file_deps:
                    if dep.name not in seen_packages:
                        all_dependencies.append(dep)
                        seen_packages.add(dep.name)

        # Sort by name
        dependencies = sorted(all_dependencies, key=lambda x: x.name)

        # Generate requirements.txt
        requirements_txt = self.generate_requirements_txt(dependencies)

        # Validate self-containment - check for local imports without corresponding files
        missing_local_files = self._validate_self_containment(code_files)
        if missing_local_files:
            logger.warning(f"Self-containment validation found {len(missing_local_files)} missing local files: {missing_local_files}")
            # Add warnings to requirements.txt
            requirements_txt += "\n\n# WARNING: Missing local files detected\n"
            for missing_file in missing_local_files:
                requirements_txt += f"# Missing: {missing_file}\n"

        logger.info(f"Project dependency analysis complete: {len(dependencies)} packages")
        return dependencies, requirements_txt

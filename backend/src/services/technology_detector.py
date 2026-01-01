"""
Technology Detection Service

Analyzes user requests to detect application types and recommend appropriate technologies.
Supports dynamic technology selection for generic code generation.
"""

import re
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum

from ..logging_config import get_logger

logger = get_logger()


class ApplicationType(Enum):
    """Supported application types."""
    WEB_APP = "web_app"
    GAME = "game"
    DATA_PROCESSING = "data_processing"
    UTILITY = "utility"
    API = "api"
    DESKTOP_APP = "desktop_app"
    MOBILE_APP = "mobile_app"
    CLI_TOOL = "cli_tool"
    LIBRARY = "library"
    EDUCATIONAL = "educational"


class Technology(Enum):
    """Supported technologies/frameworks."""
    # Web frameworks
    FASTAPI = "fastapi"
    FLASK = "flask"
    DJANGO = "django"
    REACT = "react"
    VUE = "vue"
    ANGULAR = "angular"
    NEXTJS = "nextjs"

    # Game libraries
    PYGAME = "pygame"
    ARCADE = "arcade"
    TURTLE = "turtle"

    # Data processing
    PANDAS = "pandas"
    NUMPY = "numpy"
    SCIKIT_LEARN = "scikit-learn"
    TENSORFLOW = "tensorflow"
    PYTORCH = "pytorch"

    # Utilities
    CLICK = "click"
    RICH = "rich"
    REQUESTS = "requests"

    # Desktop
    TKINTER = "tkinter"
    PYQT = "pyqt"
    PYGTK = "pygtk"

    # Testing
    PYTEST = "pytest"
    UNITTEST = "unittest"


@dataclass
class TechnologyRecommendation:
    """Technology recommendation with confidence score."""
    technology: Technology
    confidence: float
    reason: str


@dataclass
class ApplicationAnalysis:
    """Complete application analysis result."""
    application_type: ApplicationType
    primary_technologies: List[TechnologyRecommendation]
    secondary_technologies: List[TechnologyRecommendation]
    dependencies: List[str]
    estimated_complexity: str  # "simple", "medium", "complex"
    target_platform: str  # "windows", "cross-platform", "web"


class TechnologyDetector:
    """Service for detecting application types and recommending technologies."""

    def __init__(self):
        self.keywords_map = self._build_keywords_map()
        self.patterns_map = self._build_patterns_map()

    def _build_keywords_map(self) -> Dict[str, Dict]:
        """Build keyword mappings for application type detection."""
        return {
            ApplicationType.WEB_APP: {
                "keywords": [
                    "网站", "网页", "web", "网站", "页面", "前端", "后端", "服务器",
                    "http", "api", "rest", "路由", "模板", "响应", "请求",
                    "浏览器", "客户端", "服务端", "fullstack", "全栈"
                ],
                "technologies": [
                    Technology.FASTAPI, Technology.REACT, Technology.NEXTJS,
                    Technology.FLASK, Technology.DJANGO
                ],
                "complexity": "medium",
                "platform": "web"
            },
            ApplicationType.GAME: {
                "keywords": [
                    "游戏", "game", "贪吃蛇", "snake", "俄罗斯方块", "tetris",
                    "打砖块", "arkanoid", "飞行棋", "飞行射击", "fps", "rpg",
                    "冒险", "adventure", "角色扮演", "动作", "action", "益智", "puzzle"
                ],
                "technologies": [
                    Technology.PYGAME, Technology.ARCADE, Technology.TURTLE
                ],
                "complexity": "simple",
                "platform": "windows"
            },
            ApplicationType.DATA_PROCESSING: {
                "keywords": [
                    "数据", "分析", "处理", "统计", "可视化", "图表", "机器学习",
                    "人工智能", "ai", "ml", "数据挖掘", "预测", "分类", "聚类",
                    "回归", "神经网络", "深度学习", "nlp", "自然语言处理",
                    "图像处理", "cv", "计算机视觉", "大数据", "数据清洗"
                ],
                "technologies": [
                    Technology.PANDAS, Technology.NUMPY, Technology.SCIKIT_LEARN,
                    Technology.TENSORFLOW, Technology.PYTORCH
                ],
                "complexity": "complex",
                "platform": "cross-platform"
            },
            ApplicationType.UTILITY: {
                "keywords": [
                    "工具", "脚本", "自动化", "批处理", "转换", "格式化",
                    "utility", "script", "automation", "converter", "formatter",
                    "备份", "压缩", "解压", "下载", "上传", "同步"
                ],
                "technologies": [
                    Technology.CLICK, Technology.REQUESTS, Technology.RICH
                ],
                "complexity": "simple",
                "platform": "cross-platform"
            },
            ApplicationType.API: {
                "keywords": [
                    "接口", "api", "服务", "微服务", "restful", "graphql",
                    "后端服务", "backend", "service", "endpoint", "路由"
                ],
                "technologies": [
                    Technology.FASTAPI, Technology.FLASK, Technology.DJANGO
                ],
                "complexity": "medium",
                "platform": "cross-platform"
            },
            ApplicationType.CLI_TOOL: {
                "keywords": [
                    "命令行", "cli", "终端", "控制台", "命令", "参数", "选项",
                    "command", "terminal", "console", "argument", "flag"
                ],
                "technologies": [
                    Technology.CLICK, Technology.RICH
                ],
                "complexity": "simple",
                "platform": "cross-platform"
            },
            ApplicationType.EDUCATIONAL: {
                "keywords": [
                    "教学", "学习", "教程", "示例", "演示", "教学代码",
                    "educational", "tutorial", "example", "demo", "teaching"
                ],
                "technologies": [
                    Technology.TURTLE, Technology.PYGAME
                ],
                "complexity": "simple",
                "platform": "cross-platform"
            }
        }

    def _build_patterns_map(self) -> Dict[str, Dict]:
        """Build regex patterns for advanced detection."""
        return {
            "web_framework": {
                "pattern": r"(fastapi|flask|django|react|vue|angular|next\.?js)",
                "type": ApplicationType.WEB_APP
            },
            "game_library": {
                "pattern": r"(pygame|arcade|turtle)",
                "type": ApplicationType.GAME
            },
            "data_library": {
                "pattern": r"(pandas|numpy|scikit|tensorflow|pytorch)",
                "type": ApplicationType.DATA_PROCESSING
            },
            "language_specified": {
                "pattern": r"用\s*(python|java|javascript|typescript|c\+\+|c#|go|rust)",
                "extract_lang": True
            }
        }

    def analyze_request(self, user_request: str) -> ApplicationAnalysis:
        """
        Analyze user request to determine application type and technologies.

        Args:
            user_request: User's natural language request

        Returns:
            Complete application analysis
        """
        logger.info(f"Analyzing request: {user_request[:100]}...")

        # Normalize text for analysis
        text = user_request.lower().strip()

        # Detect application type
        app_type = self._detect_application_type(text)

        # Get technology recommendations
        primary_tech, secondary_tech = self._recommend_technologies(text, app_type)

        # Generate dependencies
        dependencies = self._generate_dependencies(primary_tech, secondary_tech)

        # Estimate complexity
        complexity = self._estimate_complexity(text, app_type)

        # Determine target platform
        platform = self._determine_platform(app_type, primary_tech)

        analysis = ApplicationAnalysis(
            application_type=app_type,
            primary_technologies=primary_tech,
            secondary_technologies=secondary_tech,
            dependencies=dependencies,
            estimated_complexity=complexity,
            target_platform=platform
        )

        logger.info(f"Analysis complete: {app_type.value}, {len(primary_tech)} primary techs, complexity: {complexity}")
        return analysis

    def _detect_application_type(self, text: str) -> ApplicationType:
        """Detect the most likely application type from text."""
        scores = {}

        # Check patterns first
        for pattern_name, pattern_info in self.patterns_map.items():
            pattern = pattern_info["pattern"]
            if re.search(pattern, text, re.IGNORECASE):
                app_type = pattern_info.get("type")
                if app_type:
                    scores[app_type] = scores.get(app_type, 0) + 10  # Pattern match = high confidence

        # Check keywords
        for app_type, type_info in self.keywords_map.items():
            keywords = type_info["keywords"]
            matches = sum(1 for keyword in keywords if keyword in text)
            if matches > 0:
                # Score based on keyword matches and keyword weight
                score = matches * 2
                scores[app_type] = scores.get(app_type, 0) + score

        # Default to utility if no clear match
        if not scores:
            return ApplicationType.UTILITY

        # Return highest scoring type
        return max(scores, key=scores.get)

    def _recommend_technologies(self, text: str, app_type: ApplicationType) -> Tuple[List[TechnologyRecommendation], List[TechnologyRecommendation]]:
        """Recommend primary and secondary technologies."""
        type_info = self.keywords_map[app_type]
        base_technologies = type_info["technologies"]

        primary_tech = []
        secondary_tech = []

        # Check for specific technology mentions in text
        mentioned_tech = []
        for tech in Technology:
            if tech.value in text:
                mentioned_tech.append(tech)

        # Prioritize mentioned technologies
        for tech in mentioned_tech:
            if tech in base_technologies:
                primary_tech.append(TechnologyRecommendation(
                    technology=tech,
                    confidence=0.9,
                    reason=f"用户明确提到 {tech.value}"
                ))

        # Add remaining base technologies
        for tech in base_technologies:
            if tech not in mentioned_tech:
                primary_tech.append(TechnologyRecommendation(
                    technology=tech,
                    confidence=0.7,
                    reason=f"适合 {app_type.value} 类型的推荐技术"
                ))

        # Add testing framework if not present
        test_tech = Technology.PYTEST
        if not any(t.technology == test_tech for t in primary_tech):
            secondary_tech.append(TechnologyRecommendation(
                technology=test_tech,
                confidence=0.6,
                reason="推荐的测试框架"
            ))

        return primary_tech, secondary_tech

    def _generate_dependencies(self, primary_tech: List[TechnologyRecommendation],
                             secondary_tech: List[TechnologyRecommendation]) -> List[str]:
        """Generate pip installable dependencies from technologies."""
        dependencies = []

        # Technology to package name mapping
        tech_to_package = {
            Technology.FASTAPI: ["fastapi", "uvicorn"],
            Technology.FLASK: ["flask"],
            Technology.DJANGO: ["django"],
            Technology.REACT: [],  # Frontend technology
            Technology.VUE: [],    # Frontend technology
            Technology.ANGULAR: [], # Frontend technology
            Technology.NEXTJS: [],  # Frontend technology
            Technology.PYGAME: ["pygame"],
            Technology.ARCADE: ["arcade"],
            Technology.TURTLE: [],  # Built-in
            Technology.PANDAS: ["pandas"],
            Technology.NUMPY: ["numpy"],
            Technology.SCIKIT_LEARN: ["scikit-learn"],
            Technology.TENSORFLOW: ["tensorflow"],
            Technology.PYTORCH: ["torch"],
            Technology.CLICK: ["click"],
            Technology.RICH: ["rich"],
            Technology.REQUESTS: ["requests"],
            Technology.TKINTER: [],  # Built-in
            Technology.PYQT: ["pyqt6"],
            Technology.PYGTK: ["pygobject"],
            Technology.PYTEST: ["pytest"]
        }

        all_tech = primary_tech + secondary_tech
        for tech_rec in all_tech:
            packages = tech_to_package.get(tech_rec.technology, [])
            dependencies.extend(packages)

        # Remove duplicates and sort
        return sorted(list(set(dependencies)))

    def _estimate_complexity(self, text: str, app_type: ApplicationType) -> str:
        """Estimate project complexity."""
        complexity_indicators = {
            "complex": ["机器学习", "深度学习", "ai", "人工智能", "大数据", "分布式", "微服务", "fullstack"],
            "medium": ["web", "api", "数据库", "authentication", "用户系统", "多线程"],
            "simple": ["游戏", "工具", "脚本", "示例", "tutorial"]
        }

        # Check for complexity indicators
        for level, indicators in complexity_indicators.items():
            if any(indicator in text for indicator in indicators):
                return level

        # Default based on application type
        type_complexity = self.keywords_map[app_type]["complexity"]
        return type_complexity

    def _determine_platform(self, app_type: ApplicationType, technologies: List[TechnologyRecommendation]) -> str:
        """Determine target platform."""
        # Check technologies first
        for tech in technologies:
            if tech.technology in [Technology.PYGAME, Technology.TKINTER, Technology.PYQT]:
                return "windows"  # These have Windows-specific considerations

        # Default based on application type
        return self.keywords_map[app_type]["platform"]

    def get_supported_types(self) -> List[Dict]:
        """Get list of supported application types with descriptions."""
        return [
            {
                "type": app_type.value,
                "name": {
                    ApplicationType.WEB_APP: "Web应用",
                    ApplicationType.GAME: "游戏",
                    ApplicationType.DATA_PROCESSING: "数据处理",
                    ApplicationType.UTILITY: "实用工具",
                    ApplicationType.API: "API服务",
                    ApplicationType.CLI_TOOL: "命令行工具",
                    ApplicationType.EDUCATIONAL: "教学示例"
                }.get(app_type, app_type.value),
                "description": f"支持 {app_type.value} 类型的应用开发",
                "complexity": self.keywords_map[app_type]["complexity"]
            }
            for app_type in ApplicationType
        ]

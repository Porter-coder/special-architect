"""
Documentation Service

Generates Markdown documentation for generated projects.
Creates spec.md and plan.md outputs with AI-generated content.
"""

from datetime import datetime
from typing import Dict, List, Optional

from ..logging_config import get_logger
from ..models.generated_project import GeneratedProject

logger = get_logger()


class DocumentationService:
    """
    Service for generating Markdown documentation for projects.

    Handles:
    - spec.md generation with project specifications
    - plan.md generation with implementation plans
    - README.md generation with project documentation
    """

    def __init__(self):
        """Initialize documentation service."""
        logger.info("Documentation service initialized")

    def generate_spec_markdown(self, user_request: str, phases_data: Dict) -> str:
        """
        Generate specification Markdown document.

        Args:
            user_request: Original user request
            phases_data: Data from all phases

        Returns:
            Markdown specification document
        """
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        spec_content = f"""# 项目规格说明 (AI 生成)

**生成时间**: {timestamp}
**原始需求**: {user_request}

## 项目概述

基于用户需求 "{user_request}"，AI 分析并生成了以下技术规格说明。

## 需求分析

{phases_data.get('specify', {}).get('content', '需求分析内容生成中...')}

## 技术规格

{phases_data.get('plan', {}).get('content', '技术规格生成中...')}

## 实现说明

{phases_data.get('implement', {}).get('content', '实现方案生成中...')}

---

*此文档由 AI Code Flow 系统自动生成*
"""

        return spec_content

    def generate_plan_markdown(self, user_request: str, phases_data: Dict, project: Optional[GeneratedProject] = None) -> str:
        """
        Generate implementation plan Markdown document.

        Args:
            user_request: Original user request
            phases_data: Data from all phases
            project: Generated project (optional)

        Returns:
            Markdown implementation plan document
        """
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        plan_content = f"""# 实现计划 (AI 生成)

**生成时间**: {timestamp}
**原始需求**: {user_request}

## 项目目标

实现用户需求：{user_request}

## 技术方案

### 第一阶段：需求分析
{phases_data.get('specify', {}).get('content', '分析阶段内容...')}

### 第二阶段：技术设计
{phases_data.get('plan', {}).get('content', '设计阶段内容...')}

### 第三阶段：代码实现
{phases_data.get('implement', {}).get('content', '实现阶段内容...')}

"""

        if project:
            plan_content += f"""
## 项目信息

- **项目名称**: {project.project_name}
- **文件数量**: {project.total_files}
- **总大小**: {project.total_size_bytes} 字节
- **语法验证**: {'通过' if project.syntax_validated else '待验证'}

### 依赖项
"""
            if project.dependencies:
                for dep in project.dependencies:
                    plan_content += f"- {dep}\n"
            else:
                plan_content += "- 无外部依赖\n"

            plan_content += f"""
### 项目结构
- 主文件: `{project.main_file}`
- 总文件数: {project.total_files}
"""

        plan_content += """
## 开发流程

1. **需求澄清**: 理解用户意图和核心功能
2. **技术选型**: 选择合适的编程语言和框架
3. **架构设计**: 确定系统结构和组件关系
4. **代码实现**: 生成可运行的程序代码
5. **测试验证**: 确保代码质量和功能完整性

## 质量保证

- ✅ 语法正确性验证
- ✅ 依赖关系检查
- ✅ 文件结构完整性
- ✅ 文档自动生成

---

*此计划由 AI Code Flow 系统自动生成*
"""

        return plan_content

    def generate_readme_markdown(self, project: GeneratedProject) -> str:
        """
        Generate README.md for the generated project.

        Args:
            project: Generated project instance

        Returns:
            Markdown README content
        """
        readme_content = f"""# {project.project_name}

AI 生成的项目 - 基于用户需求自动创建

## 项目信息

- **生成时间**: {project.created_at}
- **项目ID**: {project.id}
- **主文件**: {project.main_file}
- **文件数量**: {project.total_files}
- **项目大小**: {project.total_size_bytes} 字节

## 安装和运行

### 环境要求

- Python 3.11+
"""

        if project.dependencies:
            readme_content += """
### 安装依赖

```bash
pip install"""
            for dep in project.dependencies:
                readme_content += f" {dep}"
            readme_content += "\n```"
        else:
            readme_content += """
### 安装依赖

项目无外部依赖，直接运行即可。"""

        readme_content += f"""

### 运行程序

```bash
python {project.main_file}
```

## 项目结构

```
{project.project_name}/
"""

        # Add file structure
        def add_file_structure(node, indent=""):
            result = ""
            # Handle case where node is a dict or doesn't have expected attributes
            if isinstance(node, dict):
                if 'name' in node:
                    result += f"{indent}{node['name']}"
                    if 'children' in node and node['children']:
                        result += "/\n"
                        for child in node['children']:
                            result += add_file_structure(child, indent + "├── ")
                    else:
                        size = node.get('size', 0)
                        result += f" ({size} bytes)\n"
                else:
                    # Handle empty dict case
                    result += f"{indent}(file structure not available)\n"
            elif hasattr(node, 'name'):
                result += f"{indent}{node.name}"
                if hasattr(node, 'children') and node.children:
                    result += "/\n"
                    for child in node.children:
                        result += add_file_structure(child, indent + "├── ")
                else:
                    result += f" ({node.size} bytes)\n"
            else:
                result += f"{indent}(invalid file structure)\n"
            return result

        readme_content += add_file_structure(project.file_structure)

        readme_content += """
## 技术栈

- **编程语言**: Python
- **框架/库**: """

        if project.dependencies:
            readme_content += ", ".join(project.dependencies)
        else:
            readme_content += "无外部依赖"

        readme_content += """

## 开发说明

此项目由 AI Code Flow 系统自动生成，包含：
- ✅ 完整的可运行代码
- ✅ 清晰的代码结构
- ✅ 适当的注释和文档
- ✅ 语法正确性验证

## 许可证

此项目为 AI 生成代码，遵循相应开源许可证。

---

*Generated by AI Code Flow - 让 AI 帮你写代码*
"""

        return readme_content

    def generate_documentation_package(self, user_request: str, phases_data: Dict, project: GeneratedProject) -> Dict[str, str]:
        """
        Generate complete documentation package.

        Args:
            user_request: Original user request
            phases_data: Data from all phases
            project: Generated project

        Returns:
            Dictionary mapping filename to content
        """
        try:
            docs = {}

            # Generate spec.md
            docs["spec.md"] = self.generate_spec_markdown(user_request, phases_data)

            # Generate plan.md
            docs["plan.md"] = self.generate_plan_markdown(user_request, phases_data, project)

            # Generate README.md
            docs["README.md"] = self.generate_readme_markdown(project)

            logger.info(f"Generated documentation package with {len(docs)} files")
            return docs

        except Exception as e:
            logger.error(f"Failed to generate documentation package: {e}")
            # Return minimal documentation on error
            return {
                "README.md": f"# {project.project_name}\n\nAI generated project.\n\nError generating full documentation: {e}"
            }

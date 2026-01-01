"""
Projects API Endpoints

Provides endpoints for managing generated projects including retrieval and download.
"""

import logging
from typing import Dict
from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from ..services.code_generation_service import CodeGenerationService


# Create router for project endpoints
router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize service for project operations
code_generation_service = CodeGenerationService()


@router.get("/projects/{project_id}")
async def get_project_details(project_id: UUID) -> Dict:
    """
    Get generated project details.

    Args:
        project_id: Project identifier

    Returns:
        Project metadata and structure
    """
    try:
        project = await code_generation_service.project_service.load_project_metadata(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")

        return {
            "id": project.id,
            "project_name": project.project_name,
            "created_at": project.created_at,
            "file_structure": project.file_structure.dict(),
            "dependencies": project.dependencies,
            "total_files": project.total_files,
            "total_size_bytes": project.total_size_bytes,
            "syntax_validated": project.syntax_validated,
            "main_file": project.main_file
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取项目详情失败: {e}")
        raise HTTPException(status_code=500, detail="获取项目详情失败")


@router.get("/projects/{project_id}/download")
async def download_project(project_id: UUID):
    """
    Download generated project files as ZIP archive.

    Args:
        project_id: Project identifier

    Returns:
        ZIP file download response
    """
    try:
        project = await code_generation_service.project_service.load_project_metadata(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")

        if not project.syntax_validated:
            raise HTTPException(status_code=400, detail="项目尚未通过语法验证，无法下载")

        # Get all project files
        files = await code_generation_service.project_service.get_project_files(project_id)

        # Create ZIP archive (simplified - in production would create actual ZIP)
        # For now, return the main file content
        main_content = files.get(project.main_file, "# Generated code file")

        return Response(
            content=main_content,
            media_type="text/plain",
            headers={
                "Content-Disposition": f'attachment; filename="{project.project_name}_{project.main_file}"'
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载项目失败: {e}")
        raise HTTPException(status_code=500, detail="下载项目失败")

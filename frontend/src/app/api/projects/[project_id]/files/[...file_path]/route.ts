import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';
import { config } from '../../../../../../../env.config';

const PROJECTS_ROOT = config.system.projectsRoot;

// Get individual file content
export async function GET(
  request: NextRequest,
  { params }: { params: { project_id: string; file_path: string[] } }
): Promise<NextResponse> {
  try {
    const projectId = params.project_id;
    const filePathParts = params.file_path;
    const filePath = filePathParts.join('/');

    // Decode URL-encoded file path
    const decodedFilePath = decodeURIComponent(filePath);

    const projectDir = path.join(PROJECTS_ROOT, projectId);
    const fullFilePath = path.join(projectDir, decodedFilePath);

    // Security check: ensure the file is within the project directory
    const resolvedPath = path.resolve(fullFilePath);
    const resolvedProjectDir = path.resolve(projectDir);

    if (!resolvedPath.startsWith(resolvedProjectDir)) {
      return NextResponse.json({ error: '无效的文件路径' }, { status: 400 });
    }

    // Check if file exists
    try {
      await fs.access(fullFilePath);
    } catch {
      return NextResponse.json({ error: '文件不存在' }, { status: 404 });
    }

    // Read file content
    const content = await fs.readFile(fullFilePath, 'utf-8');

    // Determine content type based on file extension
    const ext = path.extname(decodedFilePath).toLowerCase();
    let contentType = 'text/plain';

    switch (ext) {
      case '.py':
        contentType = 'text/x-python';
        break;
      case '.md':
        contentType = 'text/markdown';
        break;
      case '.json':
        contentType = 'application/json';
        break;
      case '.txt':
        contentType = 'text/plain';
        break;
      default:
        contentType = 'text/plain';
    }

    return new NextResponse(content, {
      headers: {
        'Content-Type': contentType,
        'Cache-Control': 'public, max-age=3600', // Cache for 1 hour
      },
    });

  } catch (error) {
    console.error('Error serving file:', error);
    return NextResponse.json({ error: '文件读取失败' }, { status: 500 });
  }
}

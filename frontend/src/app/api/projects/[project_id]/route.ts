import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';
import { config } from '../../../../../env.config';

const PROJECTS_ROOT = config.system.projectsRoot;

// Get project directory structure
export async function GET(
  request: NextRequest,
  { params }: { params: { project_id: string } }
): Promise<NextResponse> {
  try {
    const projectId = params.project_id;
    const projectDir = path.join(PROJECTS_ROOT, projectId);

    // Check if project directory exists
    try {
      await fs.access(projectDir);
    } catch {
      return NextResponse.json({ error: '项目不存在' }, { status: 404 });
    }

    // Build directory tree
    const root = await buildDirectoryTree(projectDir, projectId);

    return NextResponse.json({
      project_id: projectId,
      root,
      total_files: countFiles(root),
      generated_at: new Date().toISOString()
    });

  } catch (error) {
    console.error('Error getting project structure:', error);
    return NextResponse.json({ error: '获取项目结构失败' }, { status: 500 });
  }
}

// Recursive function to build directory tree
async function buildDirectoryTree(dirPath: string, projectId: string): Promise<any> {
  const stats = await fs.stat(dirPath);
  const relativePath = path.relative(path.join(PROJECTS_ROOT, projectId), dirPath);

  const node = {
    type: 'directory',
    name: path.basename(dirPath),
    path: relativePath || '',
    children: [] as any[]
  };

  if (stats.isDirectory()) {
    const entries = await fs.readdir(dirPath);

    for (const entry of entries) {
      const entryPath = path.join(dirPath, entry);
      const entryStats = await fs.stat(entryPath);

      if (entryStats.isDirectory()) {
        // Recursively build subdirectory
        const childNode = await buildDirectoryTree(entryPath, projectId);
        node.children.push(childNode);
      } else {
        // Add file node
        const relativeFilePath = path.relative(path.join(PROJECTS_ROOT, projectId), entryPath);
        node.children.push({
          type: 'file',
          name: entry,
          path: relativeFilePath,
          size_bytes: entryStats.size,
          created_at: entryStats.birthtime.toISOString()
        });
      }
    }
  }

  return node;
}

// Count total files in tree
function countFiles(node: any): number {
  if (node.type === 'file') {
    return 1;
  }

  let count = 0;
  for (const child of node.children || []) {
    count += countFiles(child);
  }
  return count;
}

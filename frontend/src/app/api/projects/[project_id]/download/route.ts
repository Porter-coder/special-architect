import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';
import archiver from 'archiver';

const PROJECTS_ROOT = path.join(process.cwd(), '..', 'projects');

// Download project as ZIP file
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

    // Create a readable stream for the ZIP archive
    const archive = archiver('zip', {
      zlib: { level: 9 } // Maximum compression
    });

    // Handle archive errors
    archive.on('error', (err) => {
      console.error('Archive error:', err);
      throw err;
    });

    // Add the entire project directory to the archive
    archive.directory(projectDir, projectId);

    // Finalize the archive (this returns a Promise)
    await archive.finalize();

    // Convert to readable stream
    const readable = archive;

    // Set response headers for ZIP download
    const response = new NextResponse(readable as any, {
      headers: {
        'Content-Type': 'application/zip',
        'Content-Disposition': `attachment; filename="${projectId}.zip"`,
        'Cache-Control': 'no-cache',
      },
    });

    return response;

  } catch (error) {
    console.error('Error creating project archive:', error);
    return NextResponse.json({ error: '项目打包失败' }, { status: 500 });
  }
}

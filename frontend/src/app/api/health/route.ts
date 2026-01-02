import { NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';
import { config } from '../../../../env.config';
import { minimaxClient } from '../../../lib/minimax';

export async function GET() {
  try {
    const health = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      checks: {
        memory: getMemoryUsage()
      }
    };

    // Determine overall health status
    const allHealthy = Object.values(health.checks).every(check =>
      typeof check === 'object' && 'healthy' in check ? check.healthy : true
    );

    health.status = allHealthy ? 'healthy' : 'unhealthy';

    const statusCode = allHealthy ? 200 : 503;

    return NextResponse.json(health, { status: statusCode });
  } catch (error) {
    console.error('Health check failed:', error);
    return NextResponse.json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: 'Health check failed'
    }, { status: 503 });
  }
}

async function checkFilesystem(): Promise<{ healthy: boolean; writable: boolean; projects: number }> {
  try {
    // Resolve projects root relative to the frontend directory
    const frontendDir = path.resolve(__dirname, '../../../..');
    const projectsRoot = path.resolve(frontendDir, config.system.projectsRoot);
    console.log('Health check: checking filesystem at', projectsRoot);

    // Check if projects root exists and is writable
    await fs.access(projectsRoot);

    // Try to create a test file
    const testFile = path.join(projectsRoot, '.health-check');
    await fs.writeFile(testFile, 'test', 'utf-8');
    await fs.unlink(testFile);

    // Count existing projects
    let projectsCount = 0;
    try {
      const entries = await fs.readdir(projectsRoot);
      projectsCount = entries.filter(entry => !entry.startsWith('.')).length;
    } catch {
      // Ignore if we can't read directory
    }

    return {
      healthy: true,
      writable: true,
      projects: projectsCount
    };
  } catch (error) {
    return {
      healthy: false,
      writable: false,
      projects: 0
    };
  }
}

async function checkMinimax(): Promise<{ healthy: boolean; response_time?: number }> {
  try {
    const startTime = Date.now();
    const isConnected = await minimaxClient.testConnection();
    const responseTime = Date.now() - startTime;

    return {
      healthy: isConnected,
      response_time: responseTime
    };
  } catch (error) {
    return {
      healthy: false
    };
  }
}

function getMemoryUsage(): { used: number; total: number; percentage: number } {
  const memUsage = process.memoryUsage();
  const used = memUsage.heapUsed;
  const total = memUsage.heapTotal;
  const percentage = (used / total) * 100;

  return {
    used: Math.round(used / 1024 / 1024), // MB
    total: Math.round(total / 1024 / 1024), // MB
    percentage: Math.round(percentage * 100) / 100
  };
}

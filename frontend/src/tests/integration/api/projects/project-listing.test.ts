/**
 * Integration Tests: Librarian API - Project Directory Listing
 *
 * Tests the project structure endpoint that serves directory trees.
 */

// Mock dependencies before imports
jest.mock('fs/promises');
jest.mock('path');

import { NextRequest } from 'next/server';
import { GET } from '../../../../app/api/projects/[project_id]/route';
import fs from 'fs/promises';
import path from 'path';

const mockedFs = fs as jest.Mocked<typeof fs>;
const mockedPath = path as jest.Mocked<typeof path>;

describe('GET /api/projects/[project_id]', () => {
  beforeEach(() => {
    jest.clearAllMocks();

    // Default path mocks
    mockedPath.join.mockImplementation((...args) => args.join('/'));
    mockedPath.relative.mockImplementation((from, to) => to.replace(from + '/', ''));
    mockedPath.basename.mockImplementation((path) => path.split('/').pop() || '');
  });

  it('should return 404 for non-existent project', async () => {
    mockFs.access.mockRejectedValue(new Error('Directory not found'));

    const request = new NextRequest('http://localhost:3000/api/projects/non-existent-id');
    const response = await GET(request, { params: { project_id: 'non-existent-id' } });

    expect(response.status).toBe(404);
    const data = await response.json();
    expect(data.error).toContain('项目不存在');
  });

  it('should return project directory structure', async () => {
    // Mock existing directory
    mockFs.access.mockResolvedValue(undefined);

    // Mock root directory stats
    const mockRootStats = { isDirectory: () => true };
    mockFs.stat
      .mockResolvedValueOnce(mockRootStats) // root dir
      .mockResolvedValueOnce({ isDirectory: () => true }) // main.py
      .mockResolvedValueOnce({ isDirectory: () => false, size: 1024, birthtime: new Date() }); // main.py file

    mockFs.readdir.mockResolvedValue(['main.py']);

    const request = new NextRequest('http://localhost:3000/api/projects/test-project-id');
    const response = await GET(request, { params: { project_id: 'test-project-id' } });

    expect(response.status).toBe(200);
    const data = await response.json();

    expect(data).toHaveProperty('project_id', 'test-project-id');
    expect(data).toHaveProperty('root');
    expect(data).toHaveProperty('total_files');
    expect(data).toHaveProperty('generated_at');
    expect(data.root.type).toBe('directory');
    expect(data.total_files).toBeGreaterThanOrEqual(0);
  });

  it('should handle nested directory structures', async () => {
    mockFs.access.mockResolvedValue(undefined);

    // Mock nested structure: root -> src/ -> main.py
    const mockRootStats = { isDirectory: () => true };
    const mockSrcStats = { isDirectory: () => true };
    const mockFileStats = {
      isDirectory: () => false,
      size: 2048,
      birthtime: new Date('2026-01-02T10:00:00Z')
    };

    mockFs.stat
      .mockResolvedValueOnce(mockRootStats) // root
      .mockResolvedValueOnce(mockSrcStats)   // src dir
      .mockResolvedValueOnce(mockFileStats); // main.py

    mockFs.readdir
      .mockResolvedValueOnce(['src'])        // root contents
      .mockResolvedValueOnce(['main.py']);   // src contents

    const request = new NextRequest('http://localhost:3000/api/projects/nested-project');
    const response = await GET(request, { params: { project_id: 'nested-project' } });

    expect(response.status).toBe(200);
    const data = await response.json();

    expect(data.root.children).toHaveLength(1);
    expect(data.root.children[0].type).toBe('directory');
    expect(data.root.children[0].name).toBe('src');
    expect(data.root.children[0].children).toHaveLength(1);
    expect(data.root.children[0].children[0].type).toBe('file');
    expect(data.root.children[0].children[0].name).toBe('main.py');
  });

  it('should handle files with different extensions', async () => {
    mockFs.access.mockResolvedValue(undefined);

    const mockRootStats = { isDirectory: () => true };
    const mockPyFileStats = { isDirectory: () => false, size: 1024, birthtime: new Date() };
    const mockMdFileStats = { isDirectory: () => false, size: 512, birthtime: new Date() };

    mockFs.stat
      .mockResolvedValueOnce(mockRootStats)
      .mockResolvedValueOnce(mockPyFileStats)
      .mockResolvedValueOnce(mockMdFileStats);

    mockFs.readdir.mockResolvedValue(['main.py', 'README.md']);

    const request = new NextRequest('http://localhost:3000/api/projects/multi-file-project');
    const response = await GET(request, { params: { project_id: 'multi-file-project' } });

    expect(response.status).toBe(200);
    const data = await response.json();

    expect(data.root.children).toHaveLength(2);

    const pyFile = data.root.children.find((f: any) => f.name === 'main.py');
    const mdFile = data.root.children.find((f: any) => f.name === 'README.md');

    expect(pyFile.type).toBe('file');
    expect(pyFile.size_bytes).toBe(1024);
    expect(mdFile.type).toBe('file');
    expect(mdFile.size_bytes).toBe(512);
  });

  it('should handle filesystem errors gracefully', async () => {
    mockFs.access.mockResolvedValue(undefined);
    mockFs.stat.mockRejectedValue(new Error('Permission denied'));

    const request = new NextRequest('http://localhost:3000/api/projects/error-project');
    const response = await GET(request, { params: { project_id: 'error-project' } });

    expect(response.status).toBe(500);
    const data = await response.json();
    expect(data.error).toContain('获取项目结构失败');
  });
});

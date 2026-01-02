/**
 * Integration Tests: Librarian API - File Content Serving
 *
 * Tests the individual file serving endpoint.
 */

// Mock dependencies before imports
jest.mock('fs/promises');
jest.mock('path');

import { NextRequest } from 'next/server';
import { GET } from '../../../../app/api/projects/[project_id]/files/[...file_path]/route';
import fs from 'fs/promises';
import path from 'path';

const mockedFs = fs as jest.Mocked<typeof fs>;
const mockedPath = path as jest.Mocked<typeof path>;

describe('GET /api/projects/[project_id]/files/[...file_path]', () => {
  beforeEach(() => {
    jest.clearAllMocks();

    // Default path mocks
    mockedPath.join.mockImplementation((...args) => args.join('/'));
    mockedPath.resolve.mockImplementation((path) => path);
    mockedPath.extname.mockImplementation((path) => path.substring(path.lastIndexOf('.')));
  });

  it('should return 404 for non-existent project', async () => {
    mockFs.access.mockRejectedValue(new Error('File not found'));

    const request = new NextRequest('http://localhost:3000/api/projects/non-existent/files/main.py');
    const response = await GET(request, {
      params: { project_id: 'non-existent', file_path: ['main.py'] }
    });

    expect(response.status).toBe(404);
    const data = await response.json();
    expect(data.error).toContain('文件不存在');
  });

  it('should return file content with correct content type', async () => {
    mockFs.access.mockResolvedValue(undefined);
    mockFs.readFile.mockResolvedValue('print("Hello World")');

    const request = new NextRequest('http://localhost:3000/api/projects/test-project/files/main.py');
    const response = await GET(request, {
      params: { project_id: 'test-project', file_path: ['main.py'] }
    });

    expect(response.status).toBe(200);
    const content = await response.text();
    expect(content).toBe('print("Hello World")');

    expect(response.headers.get('content-type')).toBe('text/x-python');
    expect(response.headers.get('cache-control')).toBe('public, max-age=3600');
  });

  it('should handle different file types', async () => {
    mockFs.access.mockResolvedValue(undefined);

    const testCases = [
      { file: 'README.md', content: '# Hello', expectedType: 'text/markdown' },
      { file: 'config.json', content: '{"key": "value"}', expectedType: 'application/json' },
      { file: 'data.txt', content: 'Plain text', expectedType: 'text/plain' }
    ];

    for (const testCase of testCases) {
      mockFs.readFile.mockResolvedValue(testCase.content);

      const request = new NextRequest(`http://localhost:3000/api/projects/test/files/${testCase.file}`);
      const response = await GET(request, {
        params: { project_id: 'test', file_path: [testCase.file] }
      });

      expect(response.status).toBe(200);
      expect(response.headers.get('content-type')).toBe(testCase.expectedType);
    }
  });

  it('should handle nested file paths', async () => {
    mockFs.access.mockResolvedValue(undefined);
    mockFs.readFile.mockResolvedValue('nested file content');

    const request = new NextRequest('http://localhost:3000/api/projects/test/files/src/utils/helpers.py');
    const response = await GET(request, {
      params: { project_id: 'test', file_path: ['src', 'utils', 'helpers.py'] }
    });

    expect(response.status).toBe(200);
    const content = await response.text();
    expect(content).toBe('nested file content');
  });

  it('should handle URL-encoded file paths', async () => {
    mockFs.access.mockResolvedValue(undefined);
    mockFs.readFile.mockResolvedValue('encoded content');

    // Simulate URL encoding of "src/main.py"
    const request = new NextRequest('http://localhost:3000/api/projects/test/files/src%2Fmain.py');
    const response = await GET(request, {
      params: { project_id: 'test', file_path: ['src%2Fmain.py'] }
    });

    expect(response.status).toBe(200);
    const content = await response.text();
    expect(content).toBe('encoded content');
  });

  it('should prevent directory traversal attacks', async () => {
    const request = new NextRequest('http://localhost:3000/api/projects/test/files/../../../etc/passwd');
    const response = await GET(request, {
      params: { project_id: 'test', file_path: ['..', '..', 'etc', 'passwd'] }
    });

    expect(response.status).toBe(400);
    const data = await response.json();
    expect(data.error).toContain('无效的文件路径');
  });

  it('should handle filesystem read errors', async () => {
    mockFs.access.mockResolvedValue(undefined);
    mockFs.readFile.mockRejectedValue(new Error('Permission denied'));

    const request = new NextRequest('http://localhost:3000/api/projects/test/files/main.py');
    const response = await GET(request, {
      params: { project_id: 'test', file_path: ['main.py'] }
    });

    expect(response.status).toBe(500);
    const data = await response.json();
    expect(data.error).toContain('文件读取失败');
  });
});

// Direct API test without Next.js framework
const fs = require('fs/promises');
const path = require('path');

// Simulate NextRequest
class MockNextRequest {
  constructor(url, options = {}) {
    this.url = url;
    this.method = options.method || 'GET';
    this.body = options.body;
    this.headers = new Map();
    if (options.headers) {
      Object.entries(options.headers).forEach(([k, v]) => this.headers.set(k, v));
    }
  }

  async json() {
    return JSON.parse(this.body);
  }
}

// Mock NextResponse
class MockNextResponse {
  constructor(body, options = {}) {
    this.body = body;
    this.status = options.status || 200;
    this.headers = new Map();
    if (options.headers) {
      Object.entries(options.headers).forEach(([k, v]) => this.headers.set(k, v));
    }
  }

  static json(data, options = {}) {
    return new MockNextResponse(JSON.stringify(data), {
      ...options,
      headers: { 'content-type': 'application/json', ...options.headers }
    });
  }
}

// Mock the Next.js globals
global.NextRequest = MockNextRequest;
global.NextResponse = MockNextResponse;

// Import the POST function
const { POST } = require('./app/api/generate/route.ts');

// Test the API
async function testAPI() {
  console.log('Testing API directly...');

  const request = new MockNextRequest('http://localhost:3000/api/generate', {
    method: 'POST',
    body: JSON.stringify({ prompt: 'Create a simple calculator app' }),
    headers: { 'content-type': 'application/json' }
  });

  try {
    const response = await POST(request);
    console.log('Response status:', response.status);
    console.log('Response body:', response.body);

    // Wait a bit for async generation to complete
    console.log('Waiting for generation to complete...');
    await new Promise(resolve => setTimeout(resolve, 5000));

    // Check if files were created
    const projectsDir = path.join(__dirname, '../projects');
    console.log('Checking projects directory:', projectsDir);

    const entries = await fs.readdir(projectsDir, { withFileTypes: true });
    console.log('Projects directory contents:', entries.map(e => e.name));

    // Look for any new directories
    for (const entry of entries) {
      if (entry.isDirectory() && !entry.name.includes('.')) {
        console.log(`Checking project directory: ${entry.name}`);
        try {
          const projectFiles = await fs.readdir(path.join(projectsDir, entry.name));
          console.log(`Project ${entry.name} files:`, projectFiles);
        } catch (e) {
          console.log(`Could not read project ${entry.name}:`, e.message);
        }
      }
    }

  } catch (error) {
    console.error('API test failed:', error);
  }
}

testAPI();


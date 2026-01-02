// Test script for generation API
const https = require('https');

async function testGeneration() {
  try {
    const projectId = 'test-' + Date.now();
    const response = await fetch('http://localhost:3000/api/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt: 'Create a simple calculator app',
        projectId: projectId,
      })
    });

    const result = await response.json();
    console.log('API Response:', result);

    if (response.ok) {
      console.log('Generation started successfully');

      // Wait a bit for generation to complete
      setTimeout(async () => {
        // Check if files were created
        const fs = require('fs');
        const path = require('path');
        const projectDir = path.join(__dirname, 'projects', projectId);

        if (fs.existsSync(projectDir)) {
          const files = fs.readdirSync(projectDir);
          console.log('Generated files:', files);

          files.forEach(file => {
            const filePath = path.join(projectDir, file);
            const content = fs.readFileSync(filePath, 'utf-8');
            console.log(`\n--- ${file} ---`);
            console.log(content.substring(0, 200) + (content.length > 200 ? '...' : ''));
          });
        } else {
          console.log('Project directory not found');
        }
      }, 5000);
    }
  } catch (error) {
    console.error('Test failed:', error);
  }
}

testGeneration();

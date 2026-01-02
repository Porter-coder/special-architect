// Test the new parser logic
const { parseGeneratedCode } = require('./lib/parser');

console.log('Testing new parser logic...\n');

// Test 1: AI output with file headers
const test1 = `
README.md
# My Project

This is a test project.

spec.md
# Specification

Project specs here.

main.py
print("Hello World")

requirements.txt
flask
`;

console.log('Test 1 - File headers:');
const result1 = parseGeneratedCode(test1);
console.log('Files found:', Object.keys(result1));
Object.entries(result1).forEach(([name, content]) => {
  console.log(`\n${name}:`);
  console.log(content.substring(0, 100) + (content.length > 100 ? '...' : ''));
});

// Test 2: Empty content (should get defaults)
const test2 = '';

console.log('\n\nTest 2 - Empty content (should get defaults):');
const result2 = parseGeneratedCode(test2);
console.log('Files found:', Object.keys(result2));
Object.keys(result2).forEach(name => {
  console.log(`${name}: ${result2[name].length} chars`);
});

console.log('\nParser tests complete!');

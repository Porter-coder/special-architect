// Test the parser directly
const fs = require('fs');
const path = require('path');

// Simple test content in the format the parser expects
const testContent = `main.py
def add(x, y):
    """Add two numbers"""
    return x + y

def main():
    """Main function"""
    print("Simple Calculator")
    print("Operations: +, -, *, /")

    try:
        num1 = float(input("Enter first number: "))
        operation = input("Enter operation (+, -, *, /): ")
        num2 = float(input("Enter second number: "))

        if operation == '+':
            result = add(num1, num2)
        elif operation == '-':
            result = num1 - num2
        elif operation == '*':
            result = num1 * num2
        elif operation == '/':
            if num2 == 0:
                result = "Error: Division by zero"
            else:
                result = num1 / num2
        else:
            result = "Invalid operation"

        print(f"Result: {result}")

    except ValueError:
        print("Invalid input. Please enter numbers.")

if __name__ == "__main__":
    main()

README.md
# Simple Calculator

A command-line calculator application built with Python.

## Features

- Basic arithmetic operations: addition, subtraction, multiplication, division
- Error handling for division by zero
- User-friendly command line interface
- Input validation

## Installation

No external dependencies required. Python 3.x is recommended.

## Usage

Run the calculator:

\`\`\`bash
python main.py
\`\`\`

Follow the prompts to enter numbers and select operations.

## Example

\`\`\`
Simple Calculator
Operations: +, -, *, /:
Enter first number: 10
Enter operation (+, -, *, /): +
Enter second number: 5
Result: 15.0
\`\`\`

requirements.txt
# No external dependencies required
# Uses only Python standard library
`;

console.log('Testing parser with sample content...');
console.log('Content length:', testContent.length);

// Simulate what the parser does
const files = {};
const lines = testContent.split('\n');
let currentFile = null;
let currentContent = [];

for (let i = 0; i < lines.length; i++) {
  const line = lines[i];
  const trimmedLine = line.trim();

  // Check for file headers
  if (trimmedLine && (trimmedLine === 'main.py' || trimmedLine === 'README.md' || trimmedLine === 'requirements.txt')) {
    // Save previous file if exists
    if (currentFile && currentContent.length > 0) {
      files[currentFile] = currentContent.join('\n').trim();
    }

    // Start new file
    currentFile = trimmedLine;
    currentContent = [];
    console.log('Found file header:', currentFile);
    continue;
  }

  // Add line to current file content
  if (currentFile) {
    currentContent.push(line);
  }
}

// Save the last file
if (currentFile && currentContent.length > 0) {
  files[currentFile] = currentContent.join('\n').trim();
}

console.log('Parsed files:', Object.keys(files));
console.log('main.py exists:', !!files['main.py']);
console.log('README.md exists:', !!files['README.md']);
console.log('requirements.txt exists:', !!files['requirements.txt']);

console.log('\nmain.py preview:');
console.log(files['main.py']?.substring(0, 100) + '...');

console.log('\nREADME.md preview:');
console.log(files['README.md']?.substring(0, 100) + '...');

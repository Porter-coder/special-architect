# Simple Calculator - Technical Specification

## Overview
Create a command-line calculator application that performs basic arithmetic operations.

## Functional Requirements
- Support four basic arithmetic operations: addition, subtraction, multiplication, division
- Handle division by zero error gracefully
- Provide user-friendly command line interface with clear prompts
- Validate user input and provide helpful error messages

## Technical Requirements
- Python 3.x compatibility
- Command-line interface (CLI) application
- No external dependencies (standard library only)
- Cross-platform compatibility (Windows, macOS, Linux)

## User Interface Requirements
- Clear welcome message and instructions
- Prompt for first number input
- Prompt for operation selection (+, -, *, /)
- Prompt for second number input
- Display result clearly
- Handle invalid inputs gracefully

## Error Handling
- Division by zero: Display clear error message
- Invalid number input: Prompt user to enter valid numbers
- Invalid operation: Display available operations and prompt again

## Performance Requirements
- Fast calculation response (< 100ms)
- Minimal memory usage
- No significant CPU overhead plan.md
# Simple Calculator - Implementation Plan

## Architecture Design
Use procedural programming paradigm to create a simple command-line calculator application.

## Code Structure
- **Math Operations Module**: Define functions for each arithmetic operation (add, subtract, multiply, divide)
- **Main Function**: Handle user interaction, input validation, and program flow
- **Error Handling**: Graceful error management for invalid inputs and edge cases

## Implementation Phases

### Phase 1: Core Functions
1. Implement add(x, y) function
2. Implement subtract(x, y) function
3. Implement multiply(x, y) function
4. Implement divide(x, y) function with zero division check

### Phase 2: User Interface
1. Create main() function with welcome message
2. Add input prompts for first number
3. Add operation selection prompt
4. Add input prompts for second number
5. Implement operation routing logic
6. Add result display

### Phase 3: Error Handling & Validation
1. Add try-except blocks for ValueError on number conversion
2. Add validation for operation selection
3. Implement graceful error messages
4. Add input retry logic

### Phase 4: Polish & Testing
1. Add comprehensive docstrings
2. Test all operations manually
3. Test error conditions
4. Add final polish and comments

## File Structure
- main.py: Complete calculator implementation
- README.md: Usage instructions and documentation
- requirements.txt: Dependencies (none required)
- spec.md: Technical specifications
- plan.md: This implementation plan

## Quality Assurance
- All functions must be fully implemented (no placeholders)
- Code must run without syntax errors
- User experience must be intuitive and error-resistant
- Code must follow Python best practices main.py
def add(x, y):
    """Add two numbers"""
    return x + y

def subtract(x, y):
    """Subtract y from x"""
    return x - y

def multiply(x, y):
    """Multiply two numbers"""
    return x * y

def divide(x, y):
    """Divide x by y"""
    if y == 0:
        return "Error: Division by zero"
    return x / y

def main():
    """Main calculator function"""
    print("Simple Calculator")
    print("Operations: +, -, *, /")

    try:
        num1 = float(input("Enter first number: "))
        operation = input("Enter operation (+, -, *, /): ")
        num2 = float(input("Enter second number: ")

        if operation == '+':
            result = add(num1, num2)
        elif operation == '-':
            result = subtract(num1, num2)
        elif operation == '*':
            result = multiply(num1, num2)
        elif operation == '/':
            result = divide(num1, num2)
        else:
            result = "Invalid operation"

        print(f"Result: {result}")

    except ValueError:
        print("Invalid input. Please enter numbers.")

if __name__ == "__main__":
    main()
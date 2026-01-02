"""
Simple Calculator Application
=============================
A basic calculator supporting addition, subtraction, multiplication,
and division operations with history tracking.
"""

import sys


class CalculatorHistory:
    """Manages the history of calculation results."""

    def __init__(self, max_history=10):
        self.history = []
        self.max_history = max_history

    def add_result(self, expression, result):
        """Add a calculation result to history."""
        self.history.append({"expression": expression, "result": result})
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def get_history(self):
        """Return the full history list."""
        return self.history.copy()

    def clear_history(self):
        """Clear all history records."""
        self.history = []


class Calculator:
    """Performs basic arithmetic operations."""

    def add(self, a, b):
        """Add two numbers."""
        return a + b

    def subtract(self, a, b):
        """Subtract b from a."""
        return a - b

    def multiply(self, a, b):
        """Multiply two numbers."""
        return a * b

    def divide(self, a, b):
        """Divide a by b. Raises ValueError if b is zero."""
        if b == 0:
            raise ValueError("Division by zero is not allowed")
        return a / b

    def calculate(self, a, operator, b):
        """Perform calculation based on operator."""
        operators = {
            "+": self.add,
            "-": self.subtract,
            "*": self.multiply,
            "/": self.divide
        }
        if operator not in operators:
            raise ValueError(f"Unknown operator: {operator}")
        return operators[operator](a, b)


def get_float_input(prompt):
    """Get a floating point number from user input."""
    while True:
        try:
            value = float(input(prompt))
            return value
        except ValueError:
            print("Invalid input. Please enter a valid number.")


def get_operator_input():
    """Get a valid operator from user input."""
    valid_operators = ["+", "-", "*", "/"]
    while True:
        operator = input("Enter operator (+, -, *, /): ").strip()
        if operator in valid_operators:
            return operator
        print("Invalid operator. Please enter +, -, *, or /.")


def display_menu():
    """Display the main menu."""
    print("\n" + "=" * 40)
    print("       Simple Calculator")
    print("=" * 40)
    print("1. Addition (+)")
    print("2. Subtraction (-)")
    print("3. Multiplication (*)")
    print("4. Division (/)")
    print("5. View History")
    print("6. Clear History")
    print("7. Use Result in Next Calculation")
    print("0. Exit")
    print("=" * 40)


def display_history(history):
    """Display the calculation history."""
    if not history:
        print("\nNo history records available.")
        return

    print("\n" + "-" * 40)
    print("       Calculation History")
    print("-" * 40)
    for i, record in enumerate(history, 1):
        print(f"{i}. {record['expression']} = {record['result']}")
    print("-" * 40)


def perform_calculation(calc, history, operator_name, operator_symbol):
    """Perform a single calculation."""
    print(f"\n--- {operator_name} ---")
    a = get_float_input("Enter first number: ")

    if history and history.history:
        use_last = input("Use last result as first number? (y/n): ").lower()
        if use_last == 'y':
            last_result = history.history[-1]['result']
            print(f"Using last result: {last_result}")
            a = last_result

    b = get_float_input("Enter second number: ")

    try:
        result = calc.calculate(a, operator_symbol, b)
        expression = f"{a} {operator_symbol} {b}"
        history.add_result(expression, result)
        print(f"\nResult: {expression} = {result}")
        return result
    except ValueError as e:
        print(f"Error: {e}")
        return None


def main():
    """Main application entry point."""
    calc = Calculator()
    history = CalculatorHistory(max_history=10)
    last_result = None

    print("=" * 40)
    print("       Welcome to Simple Calculator")
    print("=" * 40)
    print("Supports: +, -, *, / operations")
    print("Features: History tracking, decimal support")

    while True:
        display_menu()
        choice = input("\nEnter your choice (0-7): ").strip()

        if choice == "0":
            print("\nThank you for using Simple Calculator. Goodbye!")
            break

        elif choice == "1":
            result = perform_calculation(calc, history, "Addition", "+")
            if result is not None:
                last_result = result

        elif choice == "2":
            result = perform_calculation(calc, history, "Subtraction", "-")
            if result is not None:
                last_result = result

        elif choice == "3":
            result = perform_calculation(calc, history, "Multiplication", "*")
            if result is not None:
                last_result = result

        elif choice == "4":
            result = perform_calculation(calc, history, "Division", "/")
            if result is not None:
                last_result = result

        elif choice == "5":
            display_history(history.get_history())

        elif choice == "6":
            history.clear_history()
            print("\nHistory has been cleared.")

        elif choice == "7":
            if last_result is not None:
                print(f"\nLast result: {last_result}")
                operator = get_operator_input()
                b = get_float_input("Enter next number: ")
                try:
                    result = calc.calculate(last_result, operator, b)
                    expression = f"{last_result} {operator} {b}"
                    history.add_result(expression, result)
                    print(f"\nResult: {expression} = {result}")
                    last_result = result
                except ValueError as e:
                    print(f"Error: {e}")
            else:
                print("\nNo previous result available. Perform a calculation first.")

        else:
            print("\nInvalid choice. Please enter a number from 0 to 7.")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
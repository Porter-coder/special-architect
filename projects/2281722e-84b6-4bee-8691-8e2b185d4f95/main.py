#!/usr/bin/env python3
"""
Calculator Software - A comprehensive calculator with basic arithmetic,
scientific calculations, base conversion, and statistical functions.

Features:
- Basic arithmetic operations (addition, subtraction, multiplication, division)
- Scientific calculations (trigonometric, logarithmic, power, roots, factorial)
- Base conversion (binary, octal, decimal, hexadecimal)
- Statistical calculations (mean, median, mode, standard deviation)
"""

import sys
import math
import statistics


class Calculator:
    """Main calculator class providing all calculation functionalities."""

    # Constants for trigonometric mode
    DEGREE = "degree"
    RADIAN = "radian"

    def __init__(self):
        """Initialize calculator with default settings."""
        self.trig_mode = self.DEGREE
        self.history = []

    def set_trig_mode(self, mode):
        """Set trigonometric calculation mode (degrees or radians)."""
        if mode in [self.DEGREE, self.RADIAN]:
            self.trig_mode = mode
            return True
        return False

    def get_trig_mode(self):
        """Return current trigonometric mode."""
        return self.trig_mode

    def _convert_trig_angle(self, angle):
        """Convert angle to radians if current mode is degrees."""
        if self.trig_mode == self.DEGREE:
            return math.radians(angle)
        return angle

    def add(self, a, b):
        """Add two numbers."""
        result = a + b
        self._add_to_history(f"{a} + {b} = {result}")
        return result

    def subtract(self, a, b):
        """Subtract second number from first."""
        result = a - b
        self._add_to_history(f"{a} - {b} = {result}")
        return result

    def multiply(self, a, b):
        """Multiply two numbers."""
        result = a * b
        self._add_to_history(f"{a} * {b} = {result}")
        return result

    def divide(self, a, b):
        """Divide first number by second (handles both float and integer division)."""
        if b == 0:
            raise ValueError("Division by zero is not allowed")
        result = a / b
        self._add_to_history(f"{a} / {b} = {result}")
        return result

    def integer_divide(self, a, b):
        """Integer division (floor division)."""
        if b == 0:
            raise ValueError("Division by zero is not allowed")
        result = a // b
        self._add_to_history(f"{a} // {b} = {result}")
        return result

    def modulo(self, a, b):
        """Return remainder of division."""
        if b == 0:
            raise ValueError("Division by zero is not allowed")
        result = a % b
        self._add_to_history(f"{a} % {b} = {result}")
        return result

    def power(self, base, exponent):
        """Calculate base raised to exponent power."""
        result = base ** exponent
        self._add_to_history(f"{base} ^ {exponent} = {result}")
        return result

    def sqrt(self, n):
        """Calculate square root."""
        if n < 0:
            raise ValueError("Cannot calculate square root of negative number")
        result = math.sqrt(n)
        self._add_to_history(f"sqrt({n}) = {result}")
        return result

    def factorial(self, n):
        """Calculate factorial of a non-negative integer."""
        if n < 0:
            raise ValueError("Factorial is not defined for negative numbers")
        if not isinstance(n, int):
            raise ValueError("Factorial requires an integer input")
        result = math.factorial(n)
        self._add_to_history(f"{n}! = {result}")
        return result

    def absolute(self, n):
        """Calculate absolute value."""
        result = abs(n)
        self._add_to_history(f"|{n}| = {result}")
        return result

    def sin(self, angle):
        """Calculate sine of angle."""
        rad = self._convert_trig_angle(angle)
        result = math.sin(rad)
        self._add_to_history(f"sin({angle}) = {result}")
        return result

    def cos(self, angle):
        """Calculate cosine of angle."""
        rad = self._convert_trig_angle(angle)
        result = math.cos(rad)
        self._add_to_history(f"cos({angle}) = {result}")
        return result

    def tan(self, angle):
        """Calculate tangent of angle."""
        rad = self._convert_trig_angle(angle)
        result = math.tan(rad)
        self._add_to_history(f"tan({angle}) = {result}")
        return result

    def log_base10(self, n):
        """Calculate base-10 logarithm."""
        if n <= 0:
            raise ValueError("Logarithm is not defined for non-positive numbers")
        result = math.log10(n)
        self._add_to_history(f"log10({n}) = {result}")
        return result

    def natural_log(self, n):
        """Calculate natural logarithm (ln)."""
        if n <= 0:
            raise ValueError("Natural log is not defined for non-positive numbers")
        result = math.log(n)
        self._add_to_history(f"ln({n}) = {result}")
        return result

    def log_base(self, n, base):
        """Calculate logarithm with arbitrary base."""
        if n <= 0:
            raise ValueError("Logarithm is not defined for non-positive numbers")
        if base <= 0 or base == 1:
            raise ValueError("Base must be positive and not equal to 1")
        result = math.log(n, base)
        self._add_to_history(f"log_{base}({n}) = {result}")
        return result

    # Base conversion functions
    def dec_to_bin(self, n):
        """Convert decimal integer to binary string."""
        if n < 0:
            raise ValueError("Negative numbers not supported for binary conversion")
        result = bin(n)[2:]
        self._add_to_history(f"dec_to_bin({n}) = {result}")
        return result

    def dec_to_oct(self, n):
        """Convert decimal integer to octal string."""
        if n < 0:
            raise ValueError("Negative numbers not supported for octal conversion")
        result = oct(n)[2:]
        self._add_to_history(f"dec_to_oct({n}) = {result}")
        return result

    def dec_to_hex(self, n):
        """Convert decimal integer to hexadecimal string."""
        if n < 0:
            raise ValueError("Negative numbers not supported for hex conversion")
        result = hex(n)[2:].upper()
        self._add_to_history(f"dec_to_hex({n}) = {result}")
        return result

    def bin_to_dec(self, s):
        """Convert binary string to decimal integer."""
        try:
            result = int(s, 2)
            self._add_to_history(f"bin_to_dec({s}) = {result}")
            return result
        except ValueError:
            raise ValueError(f"Invalid binary string: {s}")

    def oct_to_dec(self, s):
        """Convert octal string to decimal integer."""
        try:
            result = int(s, 8)
            self._add_to_history(f"oct_to_dec({s}) = {result}")
            return result
        except ValueError:
            raise ValueError(f"Invalid octal string: {s}")

    def hex_to_dec(self, s):
        """Convert hexadecimal string to decimal integer."""
        try:
            result = int(s, 16)
            self._add_to_history(f"hex_to_dec({s}) = {result}")
            return result
        except ValueError:
            raise ValueError(f"Invalid hexadecimal string: {s}")

    # Statistical functions
    def mean(self, data):
        """Calculate arithmetic mean of a list of numbers."""
        if not data:
            raise ValueError("Cannot calculate mean of empty list")
        result = statistics.mean(data)
        self._add_to_history(f"mean({data}) = {result}")
        return result

    def geometric_mean(self, data):
        """Calculate geometric mean of a list of numbers."""
        if not data:
            raise ValueError("Cannot calculate geometric mean of empty list")
        if any(x <= 0 for x in data):
            raise ValueError("Geometric mean requires all positive numbers")
        result = statistics.geometric_mean(data)
        self._add_to_history(f"geometric_mean({data}) = {result}")
        return result

    def median(self, data):
        """Calculate median of a list of numbers."""
        if not data:
            raise ValueError("Cannot calculate median of empty list")
        result = statistics.median(data)
        self._add_to_history(f"median({data}) = {result}")
        return result

    def mode(self, data):
        """Calculate mode of a list of numbers."""
        if not data:
            raise ValueError("Cannot calculate mode of empty list")
        try:
            result = statistics.mode(data)
            self._add_to_history(f"mode({data}) = {result}")
            return result
        except statistics.StatisticsError:
            raise ValueError("No unique mode found in the data")

    def standard_deviation(self, data):
        """Calculate standard deviation of a list of numbers."""
        if len(data) < 2:
            raise ValueError("Need at least 2 data points for standard deviation")
        result = statistics.stdev(data)
        self._add_to_history(f"stdev({data}) = {result}")
        return result

    def variance(self, data):
        """Calculate variance of a list of numbers."""
        if len(data) < 2:
            raise ValueError("Need at least 2 data points for variance")
        result = statistics.variance(data)
        self._add_to_history(f"variance({data}) = {result}")
        return result

    def _add_to_history(self, entry):
        """Add an entry to calculation history."""
        self.history.append(entry)
        if len(self.history) > 100:
            self.history.pop(0)

    def get_history(self):
        """Return calculation history."""
        return self.history.copy()

    def clear_history(self):
        """Clear calculation history."""
        self.history = []


def print_menu():
    """Print the main menu options."""
    print("\n" + "=" * 50)
    print("           CALCULATOR MENU")
    print("=" * 50)
    print("1.  Basic Arithmetic Operations")
    print("2.  Scientific Calculations")
    print("3.  Base Conversion")
    print("4.  Statistical Calculations")
    print("5.  View Calculation History")
    print("6.  Clear History")
    print("7.  Exit")
    print("=" * 50)


def print_basic_menu():
    """Print basic arithmetic menu."""
    print("\n--- Basic Arithmetic ---")
    print("1. Addition (+)")
    print("2. Subtraction (-)")
    print("3. Multiplication (*)")
    print("4. Division (/)")
    print("5. Integer Division (//)")
    print("6. Modulo (%)")
    print("7. Back to Main Menu")


def print_scientific_menu():
    """Print scientific calculations menu."""
    mode = "Degrees" if calc.get_trig_mode() == Calculator.DEGREE else "Radians"
    print(f"\n--- Scientific Calculations (Mode: {mode}) ---")
    print("1. Power (^)")
    print("2. Square Root")
    print("3. Factorial")
    print("4. Absolute Value")
    print("5. Sine")
    print("6. Cosine")
    print("7. Tangent")
    print("8. Logarithm (base 10)")
    print("9. Natural Logarithm (ln)")
    print("10. Logarithm (custom base)")
    print("11. Switch Angle Mode (Degree/Radian)")
    print("12. Back to Main Menu")


def print_base_menu():
    """Print base conversion menu."""
    print("\n--- Base Conversion ---")
    print("1. Decimal -> Binary")
    print("2. Decimal -> Octal")
    print("3. Decimal -> Hexadecimal")
    print("4. Binary -> Decimal")
    print("5. Octal -> Decimal")
    print("6. Hexadecimal -> Decimal")
    print("7. Back to Main Menu")


def print_stats_menu():
    """Print statistical calculations menu."""
    print("\n--- Statistical Calculations ---")
    print("1. Arithmetic Mean")
    print("2. Geometric Mean")
    print("3. Median")
    print("4. Mode")
    print("5. Standard Deviation")
    print("6. Variance")
    print("7. Back to Main Menu")


def get_number(prompt):
    """Get a floating-point number from user input."""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a valid number.")


def get_integer(prompt):
    """Get an integer from user input."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a valid integer.")


def get_numbers_list(prompt, count):
    """Get a list of numbers from user input."""
    numbers = []
    for i in range(count):
        num = get_number(f"{prompt} [{i+1}/{count}]: ")
        numbers.append(num)
    return numbers


def handle_basic_operations():
    """Handle basic arithmetic operations."""
    while True:
        print_basic_menu()
        choice = input("Enter your choice (1-7): ").strip()

        if choice == "7":
            break

        try:
            if choice == "1":
                a = get_number("Enter first number: ")
                b = get_number("Enter second number: ")
                print(f"Result: {a} + {b} = {calc.add(a, b)}")

            elif choice == "2":
                a = get_number("Enter first number: ")
                b = get_number("Enter second number: ")
                print(f"Result: {a} - {b} = {calc.subtract(a, b)}")

            elif choice == "3":
                a = get_number("Enter first number: ")
                b = get_number("Enter second number: ")
                print(f"Result: {a} * {b} = {calc.multiply(a, b)}")

            elif choice == "4":
                a = get_number("Enter first number: ")
                b = get_number("Enter second number: ")
                print(f"Result: {a} / {b} = {calc.divide(a, b)}")

            elif choice == "5":
                a = get_number("Enter first number: ")
                b = get_number("Enter second number: ")
                print(f"Result: {a} // {b} = {calc.integer_divide(a, b)}")

            elif choice == "6":
                a = get_number("Enter first number: ")
                b = get_number("Enter second number: ")
                print(f"Result: {a} % {b} = {calc.modulo(a, b)}")

            else:
                print("Invalid choice. Please try again.")

        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


def handle_scientific_operations():
    """Handle scientific calculations."""
    while True:
        print_scientific_menu()
        choice = input("Enter your choice (1-12): ").strip()

        if choice == "12":
            break

        try:
            if choice == "1":
                base = get_number("Enter base: ")
                exponent = get_number("Enter exponent: ")
                print(f"Result: {base} ^ {exponent} = {calc.power(base, exponent)}")

            elif choice == "2":
                n = get_number("Enter number: ")
                print(f"Result: sqrt({n}) = {calc.sqrt(n)}")

            elif choice == "3":
                n = get_integer("Enter non-negative integer: ")
                print(f"Result: {n}! = {calc.factorial(n)}")

            elif choice == "4":
                n = get_number("Enter number: ")
                print(f"Result: |{n}| = {calc.absolute(n)}")

            elif choice == "5":
                angle = get_number("Enter angle: ")
                print(f"Result: sin({angle}) = {calc.sin(angle)}")

            elif choice == "6":
                angle = get_number("Enter angle: ")
                print(f"Result: cos({angle}) = {calc.cos(angle)}")

            elif choice == "7":
                angle = get_number("Enter angle: ")
                print(f"Result: tan({angle}) = {calc.tan(angle)}")

            elif choice == "8":
                n = get_number("Enter positive number: ")
                print(f"Result: log10({n}) = {calc.log_base10(n)}")

            elif choice == "9":
                n = get_number("Enter positive number: ")
                print(f"Result: ln({n}) = {calc.natural_log(n)}")

            elif choice == "10":
                n = get_number("Enter positive number: ")
                base = get_number("Enter base (positive, not 1): ")
                print(f"Result: log_{base}({n}) = {calc.log_base(n, base)}")

            elif choice == "11":
                new_mode = Calculator.RADIAN if calc.get_trig_mode() == Calculator.DEGREE else Calculator.DEGREE
                calc.set_trig_mode(new_mode)
                mode_name = "Radians" if new_mode == Calculator.RADIAN else "Degrees"
                print(f"Angle mode switched to: {mode_name}")

            else:
                print("Invalid choice. Please try again.")

        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


def handle_base_conversion():
    """Handle base conversion operations."""
    while True:
        print_base_menu()
        choice = input("Enter your choice (1-7): ").strip()

        if choice == "7":
            break

        try:
            if choice == "1":
                n = get_integer("Enter decimal number: ")
                print(f"Result: {n} in binary = {calc.dec_to_bin(n)}")

            elif choice == "2":
                n = get_integer("Enter decimal number: ")
                print(f"Result: {n} in octal = {calc.dec_to_oct(n)}")

            elif choice == "3":
                n = get_integer("Enter decimal number: ")
                print(f"Result: {n} in hexadecimal = {calc.dec_to_hex(n)}")

            elif choice == "4":
                s = input("Enter binary string: ").strip()
                print(f"Result: {s} in decimal = {calc.bin_to_dec(s)}")

            elif choice == "5":
                s = input("Enter octal string: ").strip()
                print(f"Result: {s} in decimal = {calc.oct_to_dec(s)}")

            elif choice == "6":
                s = input("Enter hexadecimal string: ").strip()
                print(f"Result: {s} in decimal = {calc.hex_to_dec(s)}")

            else:
                print("Invalid choice. Please try again.")

        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


def handle_statistical_operations():
    """Handle statistical calculations."""
    while True:
        print_stats_menu()
        choice = input("Enter your choice (1-7): ").strip()

        if choice == "7":
            break

        try:
            count = get_integer("How many numbers do you want to enter? ")
            if count < 1:
                print("Please enter at least 1 number.")
                continue

            data = get_numbers_list("Enter number", count)

            if choice == "1":
                print(f"Result: Mean of {data} = {calc.mean(data)}")

            elif choice == "2":
                print(f"Result: Geometric mean of {data} = {calc.geometric_mean(data)}")

            elif choice == "3":
                print(f"Result: Median of {data} = {calc.median(data)}")

            elif choice == "4":
                print(f"Result: Mode of {data} = {calc.mode(data)}")

            elif choice == "5":
                print(f"Result: Standard deviation of {data} = {calc.standard_deviation(data)}")

            elif choice == "6":
                print(f"Result: Variance of {data} = {calc.variance(data)}")

            else:
                print("Invalid choice. Please try again.")

        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


def show_history():
    """Display calculation history."""
    history = calc.get_history()
    if not history:
        print("\nNo calculation history available.")
    else:
        print("\n--- Calculation History ---")
        for i, entry in enumerate(history, 1):
            print(f"{i}. {entry}")
    print("-" * 30)


def main():
    """Main application entry point."""
    global calc
    calc = Calculator()

    print("\n" + "=" * 50)
    print("      WELCOME TO PYTHON CALCULATOR")
    print("=" * 50)
    print("A comprehensive calculator with basic arithmetic,")
    print("scientific calculations, base conversion, and")
    print("statistical functions.")
    print("=" * 50)

    while True:
        print_menu()
        choice = input("Enter your choice (1-7): ").strip()

        if choice == "7":
            print("\nThank you for using Python Calculator!")
            print("Goodbye!")
            break

        elif choice == "1":
            handle_basic_operations()

        elif choice == "2":
            handle_scientific_operations()

        elif choice == "3":
            handle_base_conversion()

        elif choice == "4":
            handle_statistical_operations()

        elif choice == "5":
            show_history()

        elif choice == "6":
            calc.clear_history()
            print("\nHistory has been cleared.")

        else:
            print("\nInvalid choice. Please enter a number between 1 and 7.")


if __name__ == "__main__":
    main()
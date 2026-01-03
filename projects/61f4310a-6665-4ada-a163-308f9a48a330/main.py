"""
Simple Calculator Application
A basic calculator with arithmetic operations, expression evaluation, and history.
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext
import math
import re
import os

# Calculator Operations Class
class Calculator:
    """Handles all calculation logic and expression parsing."""
    
    def __init__(self):
        self.decimal_precision = 10
        self.history = []
    
    def add(self, a, b):
        """Addition operation."""
        return a + b
    
    def subtract(self, a, b):
        """Subtraction operation."""
        return a - b
    
    def multiply(self, a, b):
        """Multiplication operation."""
        return a * b
    
    def divide(self, a, b):
        """Division operation."""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    
    def modulus(self, a, b):
        """Modulus operation."""
        if b == 0:
            raise ValueError("Cannot calculate modulus with zero")
        return a % b
    
    def power(self, a, b):
        """Power operation."""
        return a ** b
    
    def square_root(self, a):
        """Square root operation."""
        if a < 0:
            raise ValueError("Cannot calculate square root of negative number")
        return math.sqrt(a)
    
    def percentage(self, a):
        """Percentage operation."""
        return a / 100
    
    def evaluate_expression(self, expression):
        """
        Evaluate a mathematical expression with proper operator precedence.
        Supports: +, -, *, /, %, **, sqrt(), parentheses, and percentages.
        """
        if not expression or expression.strip() == "":
            raise ValueError("Empty expression")
        
        # Clean up the expression
        expr = expression.strip()
        expr = expr.replace(' ', '')
        
        # Check for balanced parentheses
        if expr.count('(') != expr.count(')'):
            raise ValueError("Unbalanced parentheses")
        
        # Replace percentage symbols with /100
        expr = expr.replace('%', '/100')
        
        # Replace sqrt() with math.sqrt() for evaluation
        expr = re.sub(r'sqrt\(([^)]+)\)', r'math.sqrt(\1)', expr)
        
        # Replace ^ with ** for power operation
        expr = expr.replace('^', '**')
        
        try:
            # Use eval with math module available
            result = eval(expr, {"__builtins__": {}, "math": math})
            
            # Round to prevent floating point precision issues
            if isinstance(result, float):
                result = round(result, self.decimal_precision)
                # Remove trailing zeros
                if result.is_integer():
                    result = int(result)
            
            return result
        except ZeroDivisionError:
            raise ValueError("Cannot divide by zero")
        except SyntaxError:
            raise ValueError("Invalid expression format")
        except Exception as e:
            raise ValueError(f"Evaluation error: {str(e)}")
    
    def add_to_history(self, expression, result):
        """Add a calculation to history."""
        entry = f"{expression} = {result}"
        self.history.append(entry)
        # Keep only last 50 entries
        if len(self.history) > 50:
            self.history = self.history[-50:]
    
    def get_history(self):
        """Return history as a string."""
        return "\n".join(self.history[-20:])
    
    def clear_history(self):
        """Clear calculation history."""
        self.history = []


# GUI Calculator Application
class CalculatorApp:
    """Graphical Calculator Application using tkinter."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Calculator")
        self.root.geometry("400x550")
        self.root.resizable(True, True)
        
        # Set minimum size
        self.root.minsize(300, 450)
        
        # Initialize calculator
        self.calculator = Calculator()
        
        # Current expression being built
        self.current_expression = ""
        
        # Track if we just calculated (for chaining operations)
        self.just_calculated = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        # Main frame
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Display screen
        self.display_var = tk.StringVar()
        self.display_var.set("0")
        
        display_frame = tk.Frame(main_frame)
        display_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.display = tk.Entry(
            display_frame,
            textvariable=self.display_var,
            font=('Arial', 24),
            justify='right',
            state='readonly',
            readonlybackground='white',
            fg='black'
        )
        self.display.pack(fill=tk.X)
        
        # Button frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.BOTH, expand=True)
        
        # Button configuration
        button_config = {
            'font': ('Arial', 14, 'bold'),
            'width': 5,
            'height': 2,
            'padx': 5,
            'pady': 5
        }
        
        # Button layout
        buttons = [
            ('C', 0, 0, 'orange'),
            ('(', 0, 1, 'lightblue'),
            (')', 0, 2, 'lightblue'),
            ('/', 0, 3, 'lightblue'),
            ('7', 1, 0, 'lightgray'),
            ('8', 1, 1, 'lightgray'),
            ('9', 1, 2, 'lightgray'),
            ('*', 1, 3, 'lightblue'),
            ('4', 2, 0, 'lightgray'),
            ('5', 2, 1, 'lightgray'),
            ('6', 2, 2, 'lightgray'),
            ('-', 2, 3, 'lightblue'),
            ('1', 3, 0, 'lightgray'),
            ('2', 3, 1, 'lightgray'),
            ('3', 3, 2, 'lightgray'),
            ('+', 3, 3, 'lightblue'),
            ('0', 4, 0, 'lightgray'),
            ('.', 4, 1, 'lightgray'),
            ('%', 4, 2, 'lightblue'),
            ('=', 4, 3, 'green'),
            ('sqrt', 5, 0, 'lightblue'),
            ('^', 5, 1, 'lightblue'),
            ('del', 5, 2, 'orange'),
            ('hist', 5, 3, 'purple'),
        ]
        
        # Create and place buttons
        for btn_text, row, col, color in buttons:
            btn = tk.Button(
                button_frame,
                text=btn_text,
                **button_config,
                bg=color,
                command=lambda t=btn_text: self.on_button_click(t)
            )
            btn.grid(row=row, column=col, sticky='nsew', padx=2, pady=2)
        
        # Configure grid weights
        for i in range(6):
            button_frame.rowconfigure(i, weight=1)
        for i in range(4):
            button_frame.columnconfigure(i, weight=1)
        
        # History display area
        history_frame = tk.LabelFrame(main_frame, text="History", padx=5, pady=5)
        history_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.history_text = scrolledtext.ScrolledText(
            history_frame,
            height=6,
            font=('Arial', 10),
            state='disabled'
        )
        self.history_text.pack(fill=tk.BOTH, expand=True)
    
    def on_button_click(self, button_text):
        """Handle button clicks."""
        if button_text == 'C':
            self.clear_display()
        elif button_text == 'del':
            self.delete_last()
        elif button_text == '=':
            self.calculate()
        elif button_text == 'hist':
            self.show_history()
        elif button_text == 'sqrt':
            self.add_to_expression('sqrt(')
        else:
            self.add_to_expression(button_text)
    
    def add_to_expression(self, value):
        """Add a value to the current expression."""
        if self.just_calculated:
            # Start new expression after calculation
            if value in '+-*/^%':
                # Chain operation with previous result
                result = self.display_var.get()
                if result != "Error":
                    self.current_expression = result + value
                else:
                    self.current_expression = value
            else:
                self.current_expression = value
            self.just_calculated = False
        else:
            self.current_expression += value
        
        self.update_display()
    
    def update_display(self):
        """Update the display with current expression."""
        if self.current_expression:
            # Format for display (replace special characters)
            display_text = self.current_expression
            display_text = display_text.replace('*', '×')
            display_text = display_text.replace('/', '÷')
            self.display_var.set(display_text)
        else:
            self.display_var.set("0")
    
    def clear_display(self):
        """Clear the display and reset state."""
        self.current_expression = ""
        self.just_calculated = False
        self.display_var.set("0")
    
    def delete_last(self):
        """Delete the last character from the expression."""
        if self.current_expression:
            self.current_expression = self.current_expression[:-1]
            self.update_display()
    
    def calculate(self):
        """Evaluate the current expression."""
        if not self.current_expression:
            return
        
        try:
            # Store original expression for history
            original_expr = self.current_expression
            
            # Evaluate the expression
            result = self.calculator.evaluate_expression(self.current_expression)
            
            # Add to history
            self.calculator.add_to_history(original_expr, result)
            
            # Update display
            self.display_var.set(str(result))
            self.current_expression = str(result)
            self.just_calculated = True
            
            # Update history display
            self.update_history_display()
            
        except ValueError as e:
            self.display_var.set("Error")
            self.current_expression = ""
            self.just_calculated = False
            messagebox.showerror("Error", str(e))
        except Exception as e:
            self.display_var.set("Error")
            self.current_expression = ""
            self.just_calculated = False
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
    
    def show_history(self):
        """Show the calculation history."""
        history = self.calculator.get_history()
        if history:
            self.history_text.config(state='normal')
            self.history_text.delete(1.0, tk.END)
            self.history_text.insert(tk.END, "Recent Calculations:\n" + history)
            self.history_text.config(state='disabled')
        else:
            messagebox.showinfo("History", "No calculation history yet.")
    
    def update_history_display(self):
        """Update the history text area."""
        history = self.calculator.get_history()
        if history:
            self.history_text.config(state='normal')
            self.history_text.delete(1.0, tk.END)
            self.history_text.insert(tk.END, history)
            self.history_text.config(state='disabled')


# CLI Interface (Alternative Mode)
class CLICalculator:
    """Command-line interface for the calculator."""
    
    def __init__(self):
        self.calculator = Calculator()
    
    def display_menu(self):
        """Display the main menu."""
        print("\n" + "=" * 40)
        print("        SIMPLE CALCULATOR")
        print("=" * 40)
        print("1.  Basic Calculator")
        print("2.  View History")
        print("3.  Clear History")
        print("4.  Exit")
        print("-" * 40)
    
    def get_expression(self):
        """Get expression from user input."""
        print("\nEnter expression (or 'back' to return to menu)")
        print("Examples: 2+3*4, sqrt(16), 100%, 2^3")
        print("Operators: + - * / % ^ sqrt()")
        expression = input("Expression: ").strip()
        return expression
    
    def run_basic_calculator(self):
        """Run the basic calculator loop."""
        print("\n--- Basic Calculator Mode ---")
        print("Type your mathematical expression and press Enter.")
        print("Enter 'back' to return to the main menu.")
        
        while True:
            expression = self.get_expression()
            
            if expression.lower() == 'back':
                break
            
            if not expression:
                print("Please enter an expression.")
                continue
            
            try:
                result = self.calculator.evaluate_expression(expression)
                self.calculator.add_to_history(expression, result)
                print(f"Result: {result}")
            except ValueError as e:
                print(f"Error: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")
    
    def view_history(self):
        """View calculation history."""
        history = self.calculator.get_history()
        if history:
            print("\n--- Calculation History ---")
            print(history)
        else:
            print("\nNo calculation history yet.")
    
    def clear_history(self):
        """Clear the history."""
        self.calculator.clear_history()
        print("\nHistory cleared.")
    
    def run(self):
        """Run the CLI calculator."""
        while True:
            self.display_menu()
            choice = input("Select an option (1-4): ").strip()
            
            if choice == '1':
                self.run_basic_calculator()
            elif choice == '2':
                self.view_history()
            elif choice == '3':
                self.clear_history()
            elif choice == '4':
                print("\nThank you for using Simple Calculator. Goodbye!")
                break
            else:
                print("\nInvalid option. Please select 1-4.")


# Main Entry Point
def main():
    """Main entry point for the calculator application."""
    print("=" * 50)
    print("         SIMPLE CALCULATOR APPLICATION")
    print("=" * 50)
    print()
    print("This calculator supports:")
    print("  - Basic operations: +, -, *, /")
    print("  - Extended operations: %, ^ (power), sqrt()")
    print("  - Complex expressions with parentheses")
    print("  - Calculation history")
    print()
    
    # Ask user for mode preference
    print("Select interface mode:")
    print("  1. GUI Mode (Graphical User Interface)")
    print("  2. CLI Mode (Command Line Interface)")
    print()
    
    while True:
        choice = input("Enter 1 or 2: ").strip()
        
        if choice == '1':
            print("\nStarting GUI Calculator...")
            print("Use the window to interact with the calculator.")
            print("Close the window to exit.")
            
            # Create tkinter root and start application
            root = tk.Tk()
            app = CalculatorApp(root)
            root.mainloop()
            break
        
        elif choice == '2':
            print("\nStarting CLI Calculator...")
            cli = CLICalculator()
            cli.run()
            break
        
        else:
            print("Invalid choice. Please enter 1 or 2.")


if __name__ == "__main__":
    main()
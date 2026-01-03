"""
Simple Calculator Application
A feature-rich calculator built with Python tkinter.
Supports basic arithmetic, extended operations, expression parsing,
memory functions, and continuous calculations.
"""

import tkinter as tk
from tkinter import messagebox
import math


class Calculator:
    """Main calculator class handling all operations and UI."""

    def __init__(self, root):
        """Initialize the calculator with default values."""
        self.root = root
        self.root.title("Simple Calculator")
        self.root.geometry("400x550")
        self.root.resizable(False, False)

        # Core calculator state
        self.current_input = "0"
        self.expression = ""
        self.memory = [0.0, 0.0, 0.0, 0.0]  # 4 memory slots
        self.current_memory_slot = 0
        self.last_operator = ""
        self.waiting_for_operand = False

        # Configure UI styles
        self.setup_styles()
        self.create_widgets()
        self.bind_keys()

    def setup_styles(self):
        """Configure button styles and colors."""
        self.root.configure(bg="#2c3e50")
        
    def create_widgets(self):
        """Create all UI components."""
        # Display screen
        self.display_frame = tk.Frame(self.root, bg="#2c3e50")
        self.display_frame.pack(fill=tk.X, padx=10, pady=10)

        self.expression_label = tk.Label(
            self.display_frame,
            text="",
            font=("Arial", 12),
            bg="#2c3e50",
            fg="#7f8c8d",
            anchor="e"
        )
        self.expression_label.pack(fill=tk.X)

        self.result_label = tk.Label(
            self.display_frame,
            text="0",
            font=("Arial", 32, "bold"),
            bg="#2c3e50",
            fg="#ecf0f1",
            anchor="e"
        )
        self.result_label.pack(fill=tk.X)

        # Memory display
        self.memory_label = tk.Label(
            self.root,
            text="M: [0.0, 0.0, 0.0, 0.0]",
            font=("Arial", 10),
            bg="#2c3e50",
            fg="#3498db",
            anchor="w"
        )
        self.memory_label.pack(fill=tk.X, padx=15, pady=(0, 5))

        # Button frame
        self.button_frame = tk.Frame(self.root, bg="#2c3e50")
        self.button_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Button layout: 7 rows x 4 columns
        buttons = [
            # Row 1: Memory functions
            ["MC", "MR", "M+", "M-"],
            # Row 2: Clear functions
            ["AC", "DEL", "(", ")"],
            # Row 3: Extended math
            ["%", "√", "x²", "1/x"],
            # Row 4: Numbers and operations
            ["7", "8", "9", "÷"],
            # Row 5: Numbers and operations
            ["4", "5", "6", "×"],
            # Row 6: Numbers and operations
            ["1", "2", "3", "-"],
            # Row 7: Zero, decimal, equals
            ["0", ".", "=", "+"],
        ]

        for row_idx, row in enumerate(buttons):
            for col_idx, btn_text in enumerate(row):
                self.create_button(btn_text, row_idx, col_idx)

    def create_button(self, text, row, col):
        """Create a single calculator button."""
        # Determine button style based on text
        bg_color, fg_color, font_size = self.get_button_style(text)

        btn = tk.Button(
            self.button_frame,
            text=text,
            font=("Arial", 16, "bold"),
            bg=bg_color,
            fg=fg_color,
            bd=0,
            relief=tk.FLAT,
            command=lambda: self.on_button_click(text),
            activebackground=self.get_active_color(bg_color),
            activeforeground=fg_color
        )

        # Grid layout with padding
        btn.grid(
            row=row,
            column=col,
            sticky="nsew",
            padx=3,
            pady=3,
            ipadx=10,
            ipady=10
        )

        # Configure grid weights for responsiveness
        self.button_frame.grid_rowconfigure(row, weight=1)
        self.button_frame.grid_columnconfigure(col, weight=1)

    def get_button_style(self, text):
        """Get color and style for button based on its function."""
        if text in ["MC", "MR", "M+", "M-"]:
            return "#3498db", "white", 14
        elif text in ["AC", "DEL"]:
            return "#e74c3c", "white", 14
        elif text in ["+", "-", "×", "÷", "="]:
            return "#f39c12", "white", 16
        elif text in ["%", "√", "x²", "1/x", "(", ")"]:
            return "#9b59b6", "white", 14
        else:
            return "#34495e", "white", 16

    def get_active_color(self, color):
        """Get slightly lighter color for button press effect."""
        color_map = {
            "#3498db": "#5dade2",
            "#e74c3c": "#ec7063",
            "#f39c12": "#f5b041",
            "#9b59b6": "#af7ac5",
            "#34495e": "#5d6d7e",
        }
        return color_map.get(color, color)

    def on_button_click(self, button):
        """Handle button click events."""
        if button in "0123456789":
            self.input_digit(button)
        elif button == ".":
            self.input_decimal()
        elif button in ["+", "-", "×", "÷"]:
            self.input_operator(button)
        elif button == "=":
            self.calculate()
        elif button == "AC":
            self.clear_all()
        elif button == "DEL":
            self.delete_last()
        elif button == "%":
            self.percentage()
        elif button == "√":
            self.square_root()
        elif button == "x²":
            self.square()
        elif button == "1/x":
            self.reciprocal()
        elif button == "M+":
            self.memory_add()
        elif button == "M-":
            self.memory_subtract()
        elif button == "MR":
            self.memory_recall()
        elif button == "MC":
            self.memory_clear()
        elif button == "(":
            self.input_parenthesis("(")
        elif button == ")":
            self.input_parenthesis(")")

        self.update_display()

    def input_digit(self, digit):
        """Handle digit input."""
        if self.waiting_for_operand:
            self.current_input = digit
            self.waiting_for_operand = False
        else:
            if self.current_input == "0":
                self.current_input = digit
            else:
                # Limit input length to prevent overflow
                if len(self.current_input) < 15:
                    self.current_input += digit

    def input_decimal(self):
        """Handle decimal point input."""
        if self.waiting_for_operand:
            self.current_input = "0."
            self.waiting_for_operand = False
        elif "." not in self.current_input:
            if self.current_input == "":
                self.current_input = "0."
            else:
                self.current_input += "."

    def input_operator(self, op):
        """Handle operator input (+, -, ×, ÷)."""
        # Map display operators to Python operators
        op_map = {"×": "*", "÷": "/"}
        py_op = op_map.get(op, op)

        if self.expression:
            # If there's a pending expression, calculate it first
            try:
                result = self.evaluate_expression(self.expression)
                self.current_input = str(result)
                self.expression = self.current_input + " " + py_op + " "
            except Exception:
                self.expression = self.current_input + " " + py_op + " "
        else:
            self.expression = self.current_input + " " + py_op + " "

        self.waiting_for_operand = True
        self.last_operator = py_op

    def input_parenthesis(self, paren):
        """Handle parenthesis input."""
        if paren == "(":
            self.expression += "("
        else:
            self.expression += ")"

    def calculate(self):
        """Perform the calculation."""
        if not self.expression:
            return

        full_expression = self.expression + self.current_input

        try:
            result = self.evaluate_expression(full_expression)
            self.current_input = str(result)
            self.expression = ""
            self.waiting_for_operand = True
        except Exception as e:
            messagebox.showerror("Error", f"Invalid expression: {str(e)}")
            self.current_input = "0"
            self.expression = ""
            self.waiting_for_operand = True

    def evaluate_expression(self, expr):
        """Safely evaluate a mathematical expression."""
        # Replace display operators with Python operators
        expr = expr.replace("×", "*")
        expr = expr.replace("÷", "/")

        # Handle implicit multiplication (e.g., "2(3+1)" -> "2*(3+1)")
        import re
        expr = re.sub(r'(\d|\))(\()', r'\1*(', expr)

        # Evaluate the expression safely
        result = eval(expr, {"__builtins__": {}}, {"math": math})
        
        # Handle floating point precision
        if isinstance(result, float):
            if result.is_integer():
                return int(result)
            # Round to reasonable precision
            return round(result, 10)
        
        return result

    def percentage(self):
        """Convert current value to percentage."""
        try:
            value = float(self.current_input)
            result = value / 100
            self.current_input = str(result)
            self.waiting_for_operand = True
        except ValueError:
            pass

    def square_root(self):
        """Calculate square root of current value."""
        try:
            value = float(self.current_input)
            if value < 0:
                messagebox.showerror("Error", "Cannot calculate square root of negative number")
                return
            result = math.sqrt(value)
            self.current_input = str(result)
            self.waiting_for_operand = True
        except ValueError:
            pass

    def square(self        """Calculate square of current value."""
        try:
            value = float(self.current_input)
            result = value ** 2
            self.current_input = str(result)
            self.waiting_for_operand = True
        except ValueError:
            pass

    def reciprocal(self):
        """Calculate reciprocal (1/x) of current value."""
        try:
            value = float(self.current_input)
            if value == 0:
                messagebox.showerror("Error", "Cannot divide by zero")
                return
            result = 1 / value
            self.current_input = str(result)
            self.waiting_for_operand = True
        except ValueError:
            pass

    def memory_add(self):
        """Add current value to memory."""
        try:
            value = float(self.current_input)
            self.memory[self.current_memory_slot] += value
            self.update_memory_display()
        except ValueError:
            pass

    def memory_subtract(self):
        """Subtract current value from memory."""
        try:
            value = float(self.current_input)
            self.memory[self.current_memory_slot] -= value
            self.update_memory_display()
        except ValueError:
            pass

    def memory_recall(self):
        """Recall value from memory."""
        try:
            value = self.memory[self.current_memory_slot]
            self.current_input = str(value)
            self.waiting_for_operand = True
        except (ValueError, IndexError):
            pass

    def memory_clear(self):
        """Clear current memory slot."""
        self.memory[self.current_memory_slot] = 0.0
        self.update_memory_display()

    def clear_all(self):
        """Clear all calculator state."""
        self.current_input = "0"
        self.expression = ""
        self.last_operator = ""
        self.waiting_for_operand = False

    def delete_last(self):
        """Delete last character from input."""
        if self.waiting_for_operand:
            return

        if len(self.current_input) > 1:
            self.current_input = self.current_input[:-1]
        else:
            self.current_input = "0"

    def update_display(self):
        """Update the display labels."""
        # Format expression for display
        display_expr = self.expression.replace("*", "×").replace("/", "÷")
        
        self.expression_label.config(text=display_expr)
        self.result_label.config(text=self.current_input)

    def update_memory_display(self):
        """Update the memory display label."""
        mem_str = ", ".join([f"{m:.2f}" for m in self.memory])
        self.memory_label.config(text=f"M{self.current_memory_slot + 1}: [{mem_str}]")

    def bind_keys(self):
        """Bind keyboard keys to calculator functions."""
        self.root.bind("<Key>", self.handle_keypress)

    def handle_keypress(self, event):
        """Handle keyboard input."""
        key = event.char

        if key in "0123456789":
            self.input_digit(key)
        elif key == ".":
            self.input_decimal()
        elif key in "+-*/":
            op_map = {"+": "+", "-": "-", "*": "×", "/": "÷"}
            self.input_operator(op_map[key])
        elif key == "\r":  # Enter key
            self.calculate()
        elif key == "\x08":  # Backspace
            self.delete_last()
        elif key == "\x1b":  # Escape
            self.clear_all()
        elif key == "%":
            self.percentage()

        self.update_display()


class CalculatorCLI:
    """Command-line interface for the calculator."""

    def __init__(self):
        """Initialize the CLI calculator."""
        self.current_value = 0.0
        self.expression = ""
        self.memory = [0.0] * 4
        self.current_memory_slot = 0

    def run(self):
        """Run the interactive CLI loop."""
        print("=" * 50)
        print("      Simple Calculator - Command Line Mode")
        print("=" * 50)
        print("\nAvailable commands:")
        print("  Number keys: Enter numbers")
        print("  +, -, *, /: Basic operations")
        print("  = or Enter: Calculate result")
        print("  AC: Clear all")
        print("  DEL: Delete last character")
        print("  %: Percentage")
        print("  SQRT: Square root")
        print("  POW: Power (enter base, then POW, then exponent)")
        print("  RECIP: Reciprocal (1/x)")
        print("  M+: Add to memory")
        print("  M-: Subtract from memory")
        print("  MR: Recall from memory")
        print("  MC: Clear memory")
        print("  MS: Select memory slot (1-4)")
        print("  QUIT: Exit calculator")
        print("\n" + "-" * 50)

        while True:
            try:
                print(f"\nCurrent: {self.current_value}")
                print(f"Expression: {self.expression}")
                print(f"Memory: {self.memory}")
                print(f"Active Memory Slot: {self.current_memory_slot + 1}")

                user_input = input("\nEnter expression or command: ").strip()

                if user_input.upper() == "QUIT":
                    print("Goodbye!")
                    break
                elif user_input.upper() == "AC":
                    self.current_value = 0.0
                    self.expression = ""
                    print("Calculator cleared!")
                elif user_input.upper() == "DEL":
                    expr_str = str(self.current_value)
                    if len(expr_str) > 1:
                        self.current_value = float(expr_str[:-1])
                    else:
                        self.current_value = 0.0
                    print("Last character deleted!")
                elif user_input.upper() == "MR":
                    self.current_value = self.memory[self.current_memory_slot]
                    print(f"Recalled from memory: {self.current_value}")
                elif user_input.upper() == "MC":
                    self.memory[self.current_memory_slot] = 0.0
                    print(f"Memory slot {self.current_memory_slot + 1} cleared!")
                elif user_input.upper() == "M+":
                    self.memory[self.current_memory_slot] += self.current_value
                    print(f"Added to memory. Current memory: {self.memory[self.current_memory_slot]}")
                elif user_input.upper() == "M-":
                    self.memory[self.current_memory_slot] -= self.current_value
                    print(f"Subtracted from memory. Current memory: {self.memory[self.current_memory_slot]}")
                elif user_input.upper() == "SQRT":
                    if self.current_value < 0:
                        print("Error: Cannot calculate square root of negative number!")
                    else:
                        self.current_value = math.sqrt(self.current_value)
                        print(f"Square root: {self.current_value}")
                elif user_input.upper() == "RECIP":
                    if self.current_value == 0:
                        print("Error: Cannot calculate reciprocal of zero!")
                    else:
                        self.current_value = 1 / self.current_value
                        print(f"Reciprocal: {self.current_value}")
                elif user_input.upper() == "=" or user_input == "":
                    if self.expression:
                        result = self.evaluate(self.expression + str(self.current_value))
                        print(f"Result: {result}")
                        self.current_value = result
                        self.expression = ""
                else:
                    # Try to evaluate as expression
                    try:
                        result = self.evaluate(user_input)
                        self.current_value = result
                        self.expression = ""
                        print(f"Result: {result}")
                    except Exception as e:
                        print(f"Error: {str(e)}")

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {str(e)}")

    def evaluate(self, expr):
        """Safely evaluate a mathematical expression."""
        expr = expr.replace("×", "*")
        expr = expr.replace("÷", "/")
        return eval(expr, {"__builtins__": {}}, {"math": math})


def main():
    """Main entry point for the calculator application."""
    print("=" * 60)
    print("          SIMPLE CALCULATOR APPLICATION")
    print("=" * 60)
    print("\nSelect mode:")
    print("  1. GUI Mode (Graphical User Interface)")
    print("  2. CLI Mode (Command Line Interface)")
    print("\nEnter your choice (1 or 2): ", end="")

    choice = input().strip()

    if choice == "1":
        print("\nStarting Calculator in GUI mode...")
        print("A window will open with the calculator interface.")
        print("\nFeatures available:")
        print("  - Basic operations: +, -, ×, ÷")
        print("  - Extended operations: %, √, x², 1/x")
        print("  - Parentheses support")
        print("  - Memory functions: M+, M-, MR, MC")
        print("  - Keyboard support enabled")
        print("\nPress ESC to clear, Backspace to delete, Enter to calculate")

        root = tk.Tk()
        app = Calculator(root)
        root.mainloop()
    elif choice == "2":
        print("\nStarting Calculator in CLI mode...")
        cli = CalculatorCLI()
        cli.run()
    else:
        print("\nInvalid choice. Starting GUI mode by default...")
        root = tk.Tk()
        app = Calculator(root)
        root.mainloop()


if __name__ == "__main__":
    main()
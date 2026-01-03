"""
Simple Calculator Application
A fully functional calculator with basic and extended operations.
Supports arithmetic operations, percentage, square root, parentheses,
and calculation history.
"""

import tkinter as tk
from tkinter import messagebox
import math


class Calculator:
    """Main calculator class handling all operations and state management."""
    
    def __init__(self):
        """Initialize calculator with default values."""
        self.current_input = "0"
        self.expression = ""
        self.history = []
        self.max_display_length = 25
    
    def clear_all(self):
        """Clear all input and reset to default state."""
        self.current_input = "0"
        self.expression = ""
    
    def clear_entry(self):
        """Clear the current entry only."""
        self.current_input = "0"
    
    def delete_last(self):
        """Delete the last character from current input."""
        if len(self.current_input) == 1:
            self.current_input = "0"
        else:
            self.current_input = self.current_input[:-1]
    
    def toggle_sign(self):
        """Toggle between positive and negative."""
        if self.current_input != "0":
            if self.current_input.startswith("-"):
                self.current_input = self.current_input[1:]
            else:
                self.current_input = "-" + self.current_input
    
    def add_digit(self, digit):
        """Add a digit to the current input."""
        if self.current_input == "0":
            self.current_input = digit
        elif len(self.current_input) < self.max_display_length:
            self.current_input += digit
    
    def add_decimal(self):
        """Add decimal point if not already present."""
        if "." not in self.current_input:
            self.current_input += "."
    
    def add_operator(self, operator):
        """Add an operator to the expression."""
        if self.expression:
            self.expression += self.current_input
        self.expression += operator
        self.current_input = "0"
    
    def add_parenthesis(self, paren):
        """Add opening or closing parenthesis."""
        self.expression += paren
    
    def percentage(self):
        """Convert current input to percentage."""
        try:
            value = float(self.current_input) / 100
            self.current_input = str(value)
        except ValueError:
            return "Error"
    
    def square_root(self):
        """Calculate square root of current input."""
        try:
            value = float(self.current_input)
            if value < 0:
                return "Error"
            result = math.sqrt(value)
            self.current_input = str(result)
        except ValueError:
            return "Error"
    
    def calculate(self):
        """Evaluate the current expression."""
        try:
            full_expression = self.expression + self.current_input
            # Security: validate expression contains only safe characters
            if not self._is_safe_expression(full_expression):
                return "Error"
            
            # Evaluate the expression
            result = eval(full_expression)
            
            # Round to reasonable decimal places
            if isinstance(result, float):
                result = round(result, 10)
                # Remove trailing zeros
                if result == int(result):
                    result = int(result)
            
            # Save to history
            expr = f"{full_expression} = {result}"
            self.history.append(expr)
            if len(self.history) > 10:
                self.history.pop(0)
            
            self.expression = ""
            self.current_input = str(result)
            return str(result)
            
        except ZeroDivisionError:
            return "Error"
        except SyntaxError:
            return "Error"
        except Exception:
            return "Error"
    
    def _is_safe_expression(self, expr):
        """Check if expression contains only safe characters."""
        safe_chars = "0123456789+-*/(). "
        return all(c in safe_chars for c in expr)
    
    def get_display(self):
        """Get the current display value."""
        return self.current_input
    
    def get_expression(self):
        """Get the current expression being built."""
        return self.expression
    
    def get_history(self):
        """Get calculation history."""
        return self.history[-10:]


class CalculatorGUI:
    """Graphical user interface for the calculator."""
    
    def __init__(self, root):
        """Initialize the calculator GUI."""
        self.root = root
        self.root.title("Calculator")
        self.root.geometry("350x500")
        self.root.resizable(False, False)
        
        self.calc = Calculator()
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up all UI components."""
        # Main display
        self.display_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.display_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.expression_label = tk.Label(
            self.display_frame, text="", font=("Arial", 10),
            bg="#f0f0f0", fg="#666666", anchor="e"
        )
        self.expression_label.pack(fill=tk.X, padx=5)
        
        self.result_label = tk.Label(
            self.display_frame, text="0", font=("Arial", 28, "bold"),
            bg="#f0f0f0", fg="#333333", anchor="e"
        )
        self.result_label.pack(fill=tk.X, padx=5, pady=5)
        
        # Button frame
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure grid
        for i in range(6):
            self.button_frame.rowconfigure(i, weight=1)
        for i in range(4):
            self.button_frame.columnconfigure(i, weight=1)
        
        # Button layout
        buttons = [
            ("C", 0, 0, "#ff6b6b"), ("←", 0, 1, "#4ecdc4"),
            ("+/-", 0, 2, "#4ecdc4"), ("/", 0, 3, "#45b7d1"),
            ("(", 1, 0, "#96ceb4"), (")", 1, 1, "#96ceb4"),
            ("%", 1, 2, "#96ceb4"), ("*", 1, 3, "#45b7d1"),
            ("7", 2, 0, "#e8e8e8"), ("8", 2, 1, "#e8e8e8"),
            ("9", 2, 2, "#e8e8e8"), ("-", 2, 3, "#45b7d1"),
            ("4", 3, 0, "#e8e8e8"), ("5", 3, 1, "#e8e8e8"),
            ("6", 3, 2, "#e8e8e8"), ("+", 3, 3, "#45b7d1"),
            ("1", 4, 0, "#e8e8e8"), ("2", 4, 1, "#e8e8e8"),
            ("3", 4, 2, "#e8e8e8"), ("=", 4, 3, "#45b7d1"),
            ("0", 5, 0, "#e8e8e8", 2), (".", 5, 2, "#e8e8e8"),
            ("√", 5, 3, "#96ceb4"),
        ]
        
        for btn in buttons:
            text = btn[0]
            row = btn[1]
            col = btn[2]
            colspan = btn[4] if len(btn) > 4 else 1
            bg_color = btn[3] if len(btn) > 3 else "#e8e8e8"
            
            button = tk.Button(
                self.button_frame, text=text,
                font=("Arial", 14, "bold"),
                bg=bg_color, fg="#333333" if bg_color == "#e8e8e8" else "white",
                relief=tk.FLAT, bd=0,
                command=lambda t=text: self._on_button_click(t)
            )
            button.grid(row=row, column=col, columnspan=colspan,
                       sticky="nsew", padx=2, pady=2)
        
        # History button
        history_btn = tk.Button(
            self.root, text="Show History", font=("Arial", 10),
            command=self._show_history
        )
        history_btn.pack(fill=tk.X, padx=5, pady=2)
    
    def _on_button_click(self, button):
        """Handle button click events."""
        if button == "C":
            self.calc.clear_all()
        elif button == "CE":
            self.calc.clear_entry()
        elif button == "←":
            self.calc.delete_last()
        elif button == "+/-":
            self.calc.toggle_sign()
        elif button == "%":
            result = self.calc.percentage()
            if result == "Error":
                messagebox.showerror("Error", "Invalid operation")
                self.calc.clear_all()
        elif button == "√":
            result = self.calc.square_root()
            if result == "Error":
                messagebox.showerror("Error", "Cannot calculate square root of negative number")
                self.calc.clear_all()
        elif button == "=":
            result = self.calc.calculate()
            if result == "Error":
                messagebox.showerror("Error", "Invalid expression")
                self.calc.clear_all()
        elif button == "(" or button == ")":
            self.calc.add_parenthesis(button)
        elif button in "+-*/":
            self.calc.add_operator(button)
        elif button == ".":
            self.calc.add_decimal()
        elif button.isdigit():
            self.calc.add_digit(button)
        
        self._update_display()
    
    def _update_display(self):
        """Update the display labels."""
        self.expression_label.config(text=self.calc.get_expression())
        self.result_label.config(text=self.calc.get_display())
    
    def _show_history(self):
        """Show calculation history."""
        history = self.calc.get_history()
        if not history:
            messagebox.showinfo("History", "No calculations yet")
        else:
            history_text = "\n".join(history)
            messagebox.showinfo("Calculation History", history_text)


def main():
    """Main entry point for the calculator application."""
    print("=== Simple Calculator Application ===")
    print("Starting Calculator...")
    print("\nFeatures:")
    print("- Basic operations: +, -, *, /")
    print("- Parentheses: ( )")
    print("- Percentage: %")
    print("- Square root: √")
    print("- Sign toggle: +/-")
    print("- Clear: C")
    print("- Backspace: ←")
    print("\nA GUI window will open for interaction.")
    print("=" * 35)
    
    # Create main window
    root = tk.Tk()
    
    # Set icon (using default tk icon)
    root.configure(bg="#ffffff")
    
    # Create calculator GUI
    app = CalculatorGUI(root)
    
    # Run the application
    root.mainloop()


if __name__ == "__main__":
    main()
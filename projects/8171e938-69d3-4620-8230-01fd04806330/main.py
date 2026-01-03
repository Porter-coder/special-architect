"""
Simple Calculator Application
A basic calculator with support for arithmetic operations, extended functions,
and continuous calculation capabilities.
"""

import tkinter as tk
from tkinter import messagebox
import math


class Calculator:
    """Main calculator class handling all operations and UI interactions."""

    def __init__(self, root):
        """Initialize the calculator with default state."""
        self.root = root
        self.root.title("Simple Calculator")
        self.root.geometry("400x500")
        self.root.resizable(True, True)
        
        # Calculator state
        self.current_input = ""
        self.expression = ""
        self.last_result = None
        self.should_clear = False
        
        # Configure grid weight for responsive layout
        for i in range(13):
            self.root.grid_rowconfigure(i, weight=1)
        for i in range(4):
            self.root.grid_columnconfigure(i, weight=1)
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create all calculator UI components."""
        # Display screen
        self.display_var = tk.StringVar()
        self.display_var.set("0")
        
        display_frame = tk.Frame(self.root, bg="#333333")
        display_frame.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=2, pady=2)
        
        self.display = tk.Label(
            display_frame,
            textvariable=self.display_var,
            font=("Arial", 24, "bold"),
            bg="#333333",
            fg="white",
            anchor="e",
            padx=10
        )
        self.display.pack(expand=True, fill="both")
        
        # Secondary display for expression
        self.expression_var = tk.StringVar()
        self.expression_var.set("")
        
        expr_frame = tk.Frame(self.root, bg="#333333")
        expr_frame.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=2, pady=(0, 2))
        
        self.expr_display = tk.Label(
            expr_frame,
            textvariable=self.expression_var,
            font=("Arial", 12),
            bg="#333333",
            fg="#AAAAAA",
            anchor="e",
            padx=10
        )
        self.expr_display.pack(expand=True, fill="both")
        
        # Button layout configuration
        buttons = [
            # Row 1
            ("C", 2, 0, "#FF6666"), ("DEL", 2, 1, "#FFAA66"), ("(", 2, 2, "#66AAFF"), (")", 2, 3, "#66AAFF"),
            # Row 2
            ("7", 3, 0, "#444444"), ("8", 3, 1, "#444444"), ("9", 3, 2, "#444444"), ("/", 3, 3, "#FFAA00"),
            # Row 3
            ("4", 4, 0, "#444444"), ("5", 4, 1, "#444444"), ("6", 4, 2, "#444444"), ("*", 4, 3, "#FFAA00"),
            # Row 4
            ("1", 5, 0, "#444444"), ("2", 5, 1, "#444444"), ("3", 5, 2, "#444444"), ("-", 5, 3, "#FFAA00"),
            # Row 5
            ("0", 6, 0, "#444444"), (".", 6, 1, "#444444"), ("=", 6, 2, "#00CC00"), ("+", 6, 3, "#FFAA00"),
            # Row 6 - Extended operations
            ("%", 7, 0, "#666666"), ("x^2", 7, 1, "#666666"), ("sqrt", 7, 2, "#666666"), ("^", 7, 3, "#666666"),
            # Row 7
            ("+/-", 8, 0, "#666666"), ("MC", 8, 1, "#666666"), ("MR", 8, 2, "#666666"), ("M+", 8, 3, "#666666"),
        ]
        
        for btn_text, row, col, color in buttons:
            btn = tk.Button(
                self.root,
                text=btn_text,
                font=("Arial", 14, "bold"),
                bg=color,
                fg="white",
                borderwidth=0,
                command=lambda t=btn_text: self.on_button_click(t)
            )
            btn.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)
        
        # History display area
        history_frame = tk.Frame(self.root, bg="#222222")
        history_frame.grid(row=9, column=0, columnspan=4, sticky="nsew", padx=2, pady=(5, 2))
        
        tk.Label(history_frame, text="History:", font=("Arial", 10, "bold"),
                 bg="#222222", fg="white").pack(anchor="w", padx=5)
        
        self.history_text = tk.Text(history_frame, height=3, font=("Arial", 10),
                                     bg="#222222", fg="#AAAAAA", state="disabled")
        self.history_text.pack(expand=True, fill="both", padx=2, pady=2)
        
        # Clear history button
        btn_frame = tk.Frame(self.root, bg="#333333")
        btn_frame.grid(row=12, column=0, columnspan=4, sticky="nsew", padx=2, pady=2)
        
        clear_hist_btn = tk.Button(btn_frame, text="Clear History", font=("Arial", 10),
                                    bg="#666666", fg="white", borderwidth=0,
                                    command=self.clear_history)
        clear_hist_btn.pack(side="right", padx=5, pady=2)
        
        # Memory variable
        self.memory_value = 0.0
        self.history_list = []
        
    def on_button_click(self, button_text):
        """Handle button click events."""
        if self.should_clear and button_text not in ("C", "DEL"):
            self.current_input = ""
            self.should_clear = False
        
        if button_text == "C":
            self.clear_all()
        elif button_text == "DEL":
            self.delete_last()
        elif button_text == "=":
            self.calculate()
        elif button_text == "+/-":
            self.toggle_sign()
        elif button_text == "%":
            self.apply_percentage()
        elif button_text == "x^2":
            self.apply_power(2)
        elif button_text == "sqrt":
            self.apply_square_root()
        elif button_text == "MC":
            self.memory_clear()
        elif button_text == "MR":
            self.memory_recall()
        elif button_text == "M+":
            self.memory_add()
        elif button_text in "+-*/^":
            self.add_operator(button_text)
        elif button_text in "0123456789.":
            self.add_number(button_text)
        else:
            self.add_to_input(button_text)
        
        self.update_display()
    
    def clear_all(self):
        """Clear all input and reset calculator state."""
        self.current_input = ""
        self.expression = ""
        self.last_result = None
        self.should_clear = False
    
    def delete_last(self):
        """Delete the last character from current input."""
        if self.current_input:
            self.current_input = self.current_input[:-1]
    
    def add_number(self, number):
        """Add a number to the current input."""
        if number == ".":
            if "." in self.current_input:
                return
            if self.current_input == "":
                self.current_input = "0"
        self.current_input += number
    
    def add_operator(self, operator):
        """Add an operator to the expression."""
        if self.current_input:
            self.expression += self.current_input
            self.current_input = ""
        
        op_map = {"x^2": "**2", "sqrt": "**0.5"}
        actual_op = op_map.get(operator, operator)
        
        self.expression += actual_op
    
    def add_to_input(self, char):
        """Add characters like parentheses to input."""
        if char in "()":
            self.current_input += char
        else:
            self.current_input += char
    
    def toggle_sign(self):
        """Toggle the sign of the current number."""
        if self.current_input:
            if self.current_input.startswith("-"):
                self.current_input = self.current_input[1:]
            else:
                self.current_input = "-" + self.current_input
    
    def apply_percentage(self):
        """Convert current number to percentage."""
        if self.current_input:
            try:
                value = float(self.current_input)
                self.current_input = str(value / 100)
            except ValueError:
                pass
    
    def apply_power(self, power):
        """Apply power operation to current number."""
        if self.current_input:
            try:
                value = float(self.current_input)
                self.expression += str(value) + "**" + str(power)
                self.current_input = ""
            except ValueError:
                pass
    
    def apply_square_root(self):
        """Apply square root operation."""
        if self.current_input:
            try:
                value = float(self.current_input)
                if value < 0:
                    messagebox.showerror("Error", "Cannot calculate square root of negative number")
                    return
                self.expression += str(value) + "**0.5"
                self.current_input = ""
            except ValueError:
                pass
    
    def memory_clear(self):
        """Clear memory value."""
        self.memory_value = 0.0
    
    def memory_recall(self):
        """Recall memory value to current input."""
        self.current_input = str(self.memory_value)
    
    def memory_add(self):
        """Add current value to memory."""
        try:
            value = float(self.current_input) if self.current_input else 0.0
            self.memory_value += value
        except ValueError:
            pass
    
    def calculate(self):
        """Evaluate the current expression."""
        # Combine expression and current input
        full_expr = self.expression + self.current_input
        
        if not full_expr:
            return
        
        try:
            # Replace x^2 with **2 for evaluation
            full_expr = full_expr.replace("x^2", "**2")
            
            # Handle sqrt by replacing with **0.5
            # This is a simple approach - in production, use proper parsing
            
            result = eval(full_expr)
            
            # Round to reasonable precision
            if isinstance(result, float):
                if result == int(result):
                    result = int(result)
                else:
                    result = round(result, 10)
            
            # Save to history
            expr_display = full_expr.replace("**", "^").replace("*", "x")
            self.add_to_history(expr_display, str(result))
            
            self.last_result = result
            self.current_input = str(result)
            self.expression = ""
            self.should_clear = True
            
        except ZeroDivisionError:
            messagebox.showerror("Error", "Division by zero is not allowed")
            self.current_input = ""
        except SyntaxError:
            messagebox.showerror("Error", "Invalid expression")
            self.current_input = ""
        except Exception as e:
            messagebox.showerror("Error", f"Calculation error: {str(e)}")
            self.current_input = ""
    
    def add_to_history(self, expression, result):
        """Add calculation to history."""
        entry = f"{expression} = {result}"
        self.history_list.insert(0, entry)
        
        # Keep only last 10 entries
        if len(self.history_list) > 10:
            self.history_list = self.history_list[:10]
        
        self.update_history_display()
    
    def update_history_display(self):
        """Update the history display text."""
        self.history_text.config(state="normal")
        self.history_text.delete(1.0, tk.END)
        
        for entry in self.history_list:
            self.history_text.insert(tk.END, entry + "\n")
        
        self.history_text.config(state="disabled")
    
    def clear_history(self):
        """Clear calculation history."""
        self.history_list = []
        self.update_history_display()
    
    def update_display(self):
        """Update the display with current input."""
        display_text = self.current_input if self.current_input else "0"
        
        # Handle display for negative zero
        if display_text == "-0":
            display_text = "0"
        
        self.display_var.set(display_text)
        
        # Show expression in secondary display
        expr_text = self.expression.replace("**", "^").replace("*", "x")
        self.expression_var.set(expr_text)


def main():
    """Main entry point for the calculator application."""
    root = tk.Tk()
    
    # Set minimum window size
    root.minsize(320, 400)
    
    # Create calculator instance
    calculator = Calculator(root)
    
    # Demo message
    print("=" * 50)
    print("  Simple Calculator Application Started")
    print("=" * 50)
    print("")
    print("Calculator Features:")
    print("  - Basic operations: +, -, x, /")
    print("  - Extended operations: %, x^2, sqrt, ^")
    print("  - Parentheses support: ( )")
    print("  - Memory functions: MC, MR, M+")
    print("  - Expression history")
    print("  - Continuous calculation")
    print("")
    print("Usage:")
    print("  - Click buttons to enter numbers and operators")
    print("  - Press = to calculate the result")
    print("  - Use C to clear all, DEL to delete last character")
    print("  - Use +/- to toggle sign, % for percentage")
    print("")
    print("The calculator window should now be open.")
    print("=" * 50)
    
    # Start the tkinter main loop
    root.mainloop()


if __name__ == "__main__":
    main()
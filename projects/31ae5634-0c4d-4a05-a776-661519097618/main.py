"""
Simple Calculator - A basic calculator with arithmetic, advanced operations,
memory functions, and edit capabilities.

Features:
- Basic arithmetic: +, -, *, /
- Advanced operations: power, square root, modulo, percentage
- Memory functions: M+, M-, MR, MC
- Edit functions: undo, redo, AC, DEL
"""

import math
from typing import Optional, List, Union

Number = Union[int, float]


class Calculator:
    """Core calculator engine handling all operations and state management."""
    
    def __init__(self):
        self.current_value: Number = 0
        self.memory: Number = 0
        self.history: List[Number] = []
        self.history_index: int = -1
        self.last_operation: Optional[str] = None
        self.last_operand: Optional[Number] = None
    
    def clear_all(self) -> None:
        """Reset all calculator state."""
        self.current_value = 0
        self.last_operation = None
        self.last_operand = None
        self.history = []
        self.history_index = -1
    
    def delete_last(self) -> None:
        """Delete the last character of current input."""
        if self.current_value != 0:
            str_val = str(self.current_value)
            if len(str_val) > 1:
                if '.' in str_val:
                    self.current_value = float(str_val[:-1])
                else:
                    self.current_value = int(str_val[:-1])
            else:
                self.current_value = 0
    
    def save_to_history(self) -> None:
        """Save current state to history for undo/redo."""
        self.history = self.history[:self.history_index + 1]
        self.history.append(self.current_value)
        self.history_index = len(self.history) - 1
    
    def undo(self) -> bool:
        """Undo the last operation."""
        if self.history_index > 0:
            self.history_index -= 1
            self.current_value = self.history[self.history_index]
            return True
        elif self.history_index == 0:
            self.history_index = -1
            self.current_value = 0
            return True
        return False
    
    def redo(self) -> bool:
        """Redo the last undone operation."""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.current_value = self.history[self.history_index]
            return True
        return False
    
    def add(self, operand: Number) -> Number:
        """Addition operation."""
        self.save_to_history()
        self.current_value = self.current_value + operand
        self.last_operation = '+'
        self.last_operand = operand
        return self.current_value
    
    def subtract(self, operand: Number) -> Number:
        """Subtraction operation."""
        self.save_to_history()
        self.current_value = self.current_value - operand
        self.last_operation = '-'
        self.last_operand = operand
        return self.current_value
    
    def multiply(self, operand: Number) -> Number:
        """Multiplication operation."""
        self.save_to_history()
        self.current_value = self.current_value * operand
        self.last_operation = '*'
        self.last_operand = operand
        return self.current_value
    
    def divide(self, operand: Number) -> Optional[Number]:
        """Division operation."""
        if operand == 0:
            print("Error: Division by zero!")
            return None
        self.save_to_history()
        self.current_value = self.current_value / operand
        self.last_operation = '/'
        self.last_operand = operand
        return self.current_value
    
    def power(self, exponent: Number) -> Number:
        """Power/exponentiation operation."""
        self.save_to_history()
        self.current_value = self.current_value ** exponent
        self.last_operation = '^'
        self.last_operand = exponent
        return self.current_value
    
    def square_root(self) -> Optional[Number]:
        """Square root operation."""
        if self.current_value < 0:
            print("Error: Cannot take square root of negative number!")
            return None
        self.save_to_history()
        self.current_value = math.sqrt(self.current_value)
        self.last_operation = 'sqrt'
        return self.current_value
    
    def modulo(self, operand: Number) -> Number:
        """Modulo/remainder operation."""
        self.save_to_history()
        self.current_value = self.current_value % operand
        self.last_operation = '%'
        self.last_operand = operand
        return self.current_value
    
    def percentage(self) -> Number:
        """Percentage calculation."""
        self.save_to_history()
        self.current_value = self.current_value / 100
        self.last_operation = '%'
        return self.current_value
    
    def memory_add(self) -> None:
        """Add current value to memory (M+)."""
        self.memory = self.memory + self.current_value
        print(f"Memory: {self.memory}")
    
    def memory_subtract(self) -> None:
        """Subtract current value from memory (M-)."""
        self.memory = self.memory - self.current_value
        print(f"Memory: {self.memory}")
    
    def memory_recall(self) -> Number:
        """Recall value from memory (MR)."""
        self.current_value = self.memory
        return self.current_value
    
    def memory_clear(self) -> None:
        """Clear memory (MC)."""
        self.memory = 0
    
    def set_value(self, value: Number) -> None:
        """Set current value directly."""
        self.current_value = value
    
    def get_display(self) -> str:
        """Get current value formatted for display."""
        if isinstance(self.current_value, float):
            if self.current_value.is_integer():
                return str(int(self.current_value))
        return str(self.current_value)


def get_number_input(prompt: str) -> Number:
    """Get a numeric input from user with validation."""
    while True:
        try:
            value = float(input(prompt))
            if value.is_integer():
                return int(value)
            return value
        except ValueError:
            print("Invalid input! Please enter a valid number.")


def print_menu() -> None:
    """Print the main menu."""
    print("\n" + "=" * 50)
    print("           SIMPLE CALCULATOR")
    print("=" * 50)
    print("  Basic Operations:")
    print("    1.  Add (+)")
    print("    2.  Subtract (-)")
    print("    3.  Multiply (*)")
    print("    4.  Divide (/)")
    print()
    print("  Advanced Operations:")
    print("    5.  Power (^)")
    print("    6.  Square Root (sqrt)")
    print("    7.  Modulo (%)")
    print("    8.  Percentage (%)")
    print()
    print("  Memory Functions:")
    print("    9.  M+ (Memory Add)")
    print("    10. M- (Memory Subtract)")
    print("    11. MR (Memory Recall)")
    print("    12. MC (Memory Clear)")
    print()
    print("  Edit Functions:")
    print("    13. Undo")
    print("    14. Redo")
    print("    15. AC (All Clear)")
    print("    16. DEL (Delete Last)")
    print()
    print("  Other:")
    print("    17. Set Current Value")
    print("    18. Show Current Value")
    print("    19. Show Memory")
    print("    0.  Exit")
    print("=" * 50)


def main():
    """Main function to run the calculator application."""
    calc = Calculator()
    
    print("\n" + "=" * 50)
    print("      WELCOME TO SIMPLE CALCULATOR")
    print("=" * 50)
    print("  Current Value: 0")
    print("  Memory: 0")
    print("=" * 50)
    
    while True:
        print_menu()
        choice = input("\nEnter your choice (0-19): ").strip()
        
        if choice == '0':
            print("\nThank you for using Simple Calculator!")
            print("Goodbye!")
            break
        
        try:
            choice_num = int(choice)
        except ValueError:
            print("\nInvalid choice! Please enter a number from 0 to 19.")
            continue
        
        if choice_num < 0 or choice_num > 19:
            print("\nInvalid choice! Please enter a number from 0 to 19.")
            continue
        
        print()
        
        if choice_num == 1:
            operand = get_number_input("Enter number to add: ")
            result = calc.add(operand)
            print(f"Result: {calc.get_display()}")
        
        elif choice_num == 2:
            operand = get_number_input("Enter number to subtract: ")
            result = calc.subtract(operand)
            print(f"Result: {calc.get_display()}")
        
        elif choice_num == 3:
            operand = get_number_input("Enter number to multiply: ")
            result = calc.multiply(operand)
            print(f"Result: {calc.get_display()}")
        
        elif choice_num == 4:
            operand = get_number_input("Enter number to divide: ")
            result = calc.divide(operand)
            if result is not None:
                print(f"Result: {calc.get_display()}")
        
        elif choice_num == 5:
            exponent = get_number_input("Enter exponent: ")
            result = calc.power(exponent)
            print(f"Result: {calc.get_display()}")
        
        elif choice_num == 6:
            result = calc.square_root()
            if result is not None:
                print(f"Result: {calc.get_display()}")
        
        elif choice_num == 7:
            operand = get_number_input("Enter number for modulo: ")
            result = calc.modulo(operand)
            print(f"Result: {calc.get_display()}")
        
        elif choice_num == 8:
            result = calc.percentage()
            print(f"Result: {calc.get_display()}")
        
        elif choice_num == 9:
            calc.memory_add()
            print(f"Current Value: {calc.get_display()}")
        
        elif choice_num == 10:
            calc.memory_subtract()
            print(f"Current Value: {calc.get_display()}")
        
        elif choice_num == 11:
            result = calc.memory_recall()
            print(f"Recalled from Memory: {calc.get_display()}")
        
        elif choice_num == 12:
            calc.memory_clear()
            print("Memory cleared!")
        
        elif choice_num == 13:
            if calc.undo():
                print(f"Undone! Current Value: {calc.get_display()}")
            else:
                print("Nothing to undo!")
        
        elif choice_num == 14:
            if calc.redo():
                print(f"Redone! Current Value: {calc.get_display()}")
            else:
                print("Nothing to redo!")
        
        elif choice_num == 15:
            calc.clear_all()
            print("All cleared! Current Value: 0")
        
        elif choice_num == 16:
            calc.delete_last()
            print(f"Current Value: {calc.get_display()}")
        
        elif choice_num == 17:
            value = get_number_input("Enter value: ")
            calc.set_value(value)
            print(f"Current Value set to: {calc.get_display()}")
        
        elif choice_num == 18:
            print(f"Current Value: {calc.get_display()}")
            print(f"Last Operation: {calc.last_operation}")
            print(f"Last Operand: {calc.last_operand}")
        
        elif choice_num == 19:
            print(f"Memory: {calc.memory}")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
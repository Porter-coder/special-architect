"""
Sudoku Solver - Backtracking Algorithm Implementation

This module provides a complete Sudoku puzzle solver using the classic
backtracking algorithm. It includes board parsing, validation, solving,
and display functionality for standard 9x9 Sudoku puzzles.
"""

# Module constants for Sudoku dimensions
EMPTY = 0
SIZE = 9
BOX_SIZE = 3

def parse_board_from_string(board_string):
    """
    Parse a Sudoku board from a string representation.

    The input string should contain 81 digits (0-9) where 0 represents
    an empty cell. Characters other than digits are ignored.

    Args:
        board_string: A string containing the board data

    Returns:
        A 9x9 list of lists representing the board

    Raises:
        ValueError: If the string does not contain enough valid digits
    """
    digits = [int(c) for c in board_string if c.isdigit()]
    if len(digits) < 81:
        raise ValueError(
            f"Insufficient data: need 81 digits, got {len(digits)}"
        )
    board = []
    for i in range(SIZE):
        row = digits[i * SIZE:(i + 1) * SIZE]
        board.append(row)
    return board

def is_valid_move(board, row, col, num):
    """
    Check if placing 'num' at (row, col) is a valid Sudoku move.

    This function verifies that the number does not violate Sudoku rules
    by checking the entire row, entire column, and the 3x3 box.

    Args:
        board: The current board state (9x9 list)
        row: Row index (0-8)
        col: Column index (0-8)
        num: Number to place (1-9)

    Returns:
        True if the move is valid, False otherwise
    """
    # Check row - ensure no duplicate in the same row
    if num in board[row]:
        return False

    # Check column - ensure no duplicate in the same column
    for r in range(SIZE):
        if board[r][col] == num:
            return False

    # Check 3x3 box - ensure no duplicate in the local box
    box_row_start = (row // BOX_SIZE) * BOX_SIZE
    box_col_start = (col // BOX_SIZE) * BOX_SIZE

    for r in range(box_row_start, box_row_start + BOX_SIZE):
        for c in range(box_col_start, box_col_start + BOX_SIZE):
            if board[r][c] == num:
                return False

    return True

def find_empty_cell(board):
    """
    Find the first empty cell in the Sudoku board.

    An empty cell is represented by 0. This function scans the board
    row by row from top to bottom.

    Args:
        board: The current board state (9x9 list)

    Returns:
        A tuple (row, col) of the empty cell, or None if board is full
    """
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                return (row, col)
    return None

def solve_sudoku(board):
    """
    Solve the Sudoku puzzle using backtracking algorithm.

    This is the main solver function that recursively tries all possible
    numbers for each empty cell, backtracking when a path leads to failure.

    Args:
        board: The Sudoku board to solve (modified in-place)

    Returns:
        True if a solution is found, False otherwise
    """
    # Find the next empty cell
    empty = find_empty_cell(board)

    # Base case: no empty cells means puzzle is solved
    if empty is None:
        return True

    row, col = empty

    # Try numbers 1 through 9
    for num in range(1, SIZE + 1):
        if is_valid_move(board, row, col, num):
            # Place the number
            board[row][col] = num

            # Recursively attempt to solve the rest
            if solve_sudoku(board):
                return True

            # Backtrack: remove the number if it didn't lead to solution
            board[row][col] = EMPTY

    # No valid number found, trigger backtracking
    return False

def print_board(board):
    """
    Print the Sudoku board in a formatted, human-readable style.

    The board is displayed with grid lines separating the 3x3 boxes
    for easy visualization.

    Args:
        board: The Sudoku board to display (9x9 list)
    """
    print("\n" + " " * 4 + "=" * 37)

    for i in range(SIZE):
        line = " |"
        for j in range(SIZE):
            cell_val = board[i][j]
            if cell_val == EMPTY:
                line += " . "
            else:
                line += f" {cell_val} "

            # Add vertical divider after every 3 columns
            if (j + 1) % BOX_SIZE == 0 and j < SIZE - 1:
                line += "|"
        print(f" {i + 1} |{line}")

        # Add horizontal divider after every 3 rows
        if (i + 1) % BOX_SIZE == 0 and i < SIZE - 1:
            print(" " * 4 + "-" * 37)

    print(" " * 4 + "=" * 37 + "\n")

def validate_initial_board(board):
    """
    Validate that the initial board configuration is valid.

    Checks that no pre-filled numbers violate Sudoku rules.

    Args:
        board: The initial Sudoku board (9x9 list)

    Returns:
        True if the board is valid, False otherwise
    """
    for row in range(SIZE):
        for col in range(SIZE):
            num = board[row][col]
            if num != EMPTY:
                # Temporarily remove the number to check validity
                board[row][col] = EMPTY
                if not is_valid_move(board, row, col, num):
                    board[row][col] = num
                    return False
                board[row][col] = num
    return True

def solve_from_string(board_string):
    """
    Convenience function to solve a Sudoku from string input.

    Args:
        board_string: String containing 81 digits (0-9)

    Returns:
        Solved board as 9x9 list, or None if no solution exists
    """
    board = parse_board_from_string(board_string)

    if not validate_initial_board(board):
        return None

    if solve_sudoku(board):
        return board

    return None

# Sample puzzle for demonstration
# 0 represents an empty cell
SAMPLE_PUZZLE = (
    "530070000"
    "600195000"
    "098000060"
    "800060003"
    "400803001"
    "700020006"
    "060000280"
    "000419005"
    "000080079"
)

def main():
    """
    Main function demonstrating the Sudoku solver.

    This function runs a complete demonstration showing how the
    backtracking algorithm solves a Sudoku puzzle.
    """
    print("=" * 50)
    print("       SUDOKU SOLVER - BACKTRACKING ALGORITHM")
    print("=" * 50)
    print("\nThis solver uses recursive backtracking to find solutions.")
    print("The algorithm tries each number 1-9 in empty cells and")
    print("backtracks when a path leads to a dead end.\n")

    # Display the puzzle
    print("ORIGINAL PUZZLE:")
    puzzle = parse_board_from_string(SAMPLE_PUZZLE)
    print_board(puzzle)

    # Solve the puzzle
    print("SOLVING...\n")

    if solve_sudoku(puzzle):
        print("SOLUTION FOUND:")
        print_board(puzzle)
        print("The puzzle was solved successfully using backtracking!")
    else:
        print("No solution exists for this puzzle.")

    print("\nAdditional puzzle examples:\n")

    # Second example: different difficulty
    puzzle2_str = (
        "000000000"
        "000003085"
        "002015800"
        "000107000"
        "305000900"
        "040000072"
        "000013000"
        "000019040"
        "000000078"
    )

    print("Example 2 - Original:")
    puzzle2 = parse_board_from_string(puzzle2_str)
    print_board(puzzle2)

    print("Example 2 - Solved:")
    if solve_sudoku(puzzle2):
        print_board(puzzle2)
    else:
        print("No solution found.\n")

    print("=" * 50)
    print("Thank you for using the Sudoku Solver!")
    print("=" * 50)

if __name__ == "__main__":
    main()
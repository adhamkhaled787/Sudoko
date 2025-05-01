import random
import json
import copy

def is_valid(board, row, col, num):
    # Check row
    for i in range(9):
        if board[row][i] == num:
            return False
    
    # Check column
    for i in range(9):
        if board[i][col] == num:
            return False
    
    # Check 3x3 box
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
                
    return True

def find_empty(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                return i, j
    return None

def is_solvable(board):
    board_copy = copy.deepcopy(board)
    return _solve_backtrack(board_copy)

def _solve_backtrack(board):
    empty = find_empty(board)
    if not empty:
        return True
    
    row, col = empty
    # Try numbers in a random order to get different solutions
    numbers = list(range(1, 10))
    random.shuffle(numbers)
    
    for num in numbers:
        if is_valid(board, row, col, num):
            board[row][col] = num
            if _solve_backtrack(board):
                return True
            board[row][col] = 0
    
    return False

def generate_full_solved_board():
    """Generate a completely filled, valid Sudoku board"""
    board = [[0 for _ in range(9)] for _ in range(9)]
    _solve_backtrack(board)  # This will fill the entire board
    return board

def generate_random_solvable_board(seed_cells=17, max_attempts=1000, difficulty='medium'):
    """Generate a Sudoku puzzle with the specified difficulty"""
    # Set seed cells based on difficulty
    if difficulty == 'easy':
        seed_cells = 35  # More filled cells = easier
    elif difficulty == 'medium':
        seed_cells = 25
    elif difficulty == 'hard':
        seed_cells = 17  # Fewer filled cells = harder
    else:
        seed_cells = 25  # Default to medium
    
    print(f"Generating {difficulty} board with {seed_cells} filled cells...")
    
    # Generate a fully solved board
    solved_board = generate_full_solved_board()
    
    # Create a puzzle by removing numbers while ensuring it remains solvable
    board = copy.deepcopy(solved_board)
    cells_to_remove = 81 - seed_cells
    
    # Get all positions in a random order
    all_positions = [(i, j) for i in range(9) for j in range(9)]
    random.shuffle(all_positions)
    
    # Remove cells while ensuring the puzzle remains solvable
    removed = 0
    for row, col in all_positions:
        if removed >= cells_to_remove:
            break
            
        temp = board[row][col]
        board[row][col] = 0
        
        # Make a copy of the board for validation
        board_copy = copy.deepcopy(board)
        
        # Check if the board still has a unique solution
        if is_solvable(board_copy):
            removed += 1
        else:
            # If removing this cell creates multiple solutions, put it back
            board[row][col] = temp
    
    # Save the generated board
    with open("sudoku_board.json", "w") as f:
        json.dump(board, f)
    
    return board

def print_board(board):
    for i in range(9):
        row_str = ""
        for j in range(9):
            cell = str(board[i][j]) if board[i][j] != 0 else "."
            row_str += cell + " "
            if j % 3 == 2 and j != 8:
                row_str += "| "
        print(row_str.strip())
        if i % 3 == 2 and i != 8:
            print("-" * 21)



import random
import copy

def is_valid(board, row, col, num):
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False

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
    for num in range(1, 10):
        if is_valid(board, row, col, num):
            board[row][col] = num
            if _solve_backtrack(board):
                return True
            board[row][col] = 0
    return False

def generate_random_solvable_board(seed_cells=17, max_attempts=1000):
    for _ in range(max_attempts):
        board = [[0 for _ in range(9)] for _ in range(9)]
        filled = 0
        attempts = 0

        while filled < seed_cells and attempts < 100:
            row, col = random.randint(0, 8), random.randint(0, 8)
            if board[row][col] == 0:
                num = random.randint(1, 9)
                if is_valid(board, row, col, num):
                    board[row][col] = num
                    filled += 1
            attempts += 1

        if is_solvable(board):
            return board  # ✅ Return the first solvable board
    raise ValueError("Failed to generate a solvable board in time.")

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


# Example usage
board = generate_random_solvable_board(seed_cells=20)
print_board(board)

import json
from generator import generate_random_solvable_board
from arc import create_domains_from_board, get_neighbors, ac3, variables
from gui import run_gui

# ------------------------------------------
# Add these new imports
from arc import backtrack  # Add this function in arc.py (shown below)
# ------------------------------------------

# Step 1: Generate and save board
board = generate_random_solvable_board(seed_cells=30)
with open("sudoku_board.json", "w") as f:
    json.dump(board, f)

# Step 2: Keep original copy for GUI display
original_board = [row[:] for row in board]

# Step 3: AC-3 constraint propagation
domains = create_domains_from_board(board)
neighbors = get_neighbors()
ac3(domains, neighbors)

# Step 4: If board is incomplete, use backtracking
if not all(len(domains[var]) == 1 for var in variables):
    print("AC-3 incomplete. Starting backtracking to finish solving.")
    domains = backtrack(domains, neighbors)
    if domains is None:
        raise ValueError("No solution found with backtracking.")

# Step 5: Update board with final values
for var in variables:
    if len(domains[var]) == 1:
        i, j = var
        board[i][j] = next(iter(domains[var]))

# Step 6: Launch GUI with original and updated board
run_gui(board, original_board)

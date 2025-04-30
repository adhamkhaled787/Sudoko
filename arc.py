# Sudoku board representation for CSP
from typing import List, Set, Dict, Tuple

# Define the size of the Sudoku board (9x9)
BOARD_SIZE = 9
SUBGRID_SIZE = 3

# Define the domain for each cell (1-9)
DOMAIN = set(range(1, 10))

# Create a list to represent the board
# Each cell is represented by its row and column indices
def create_board() -> List[List[int]]:
    return [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

# Get all variables (cells) in the board
def get_variables(board: List[List[int]]) -> List[Tuple[int, int]]:
    return [(i, j) for i in range(BOARD_SIZE) for j in range(BOARD_SIZE)]

# Get the domain for a specific cell
def get_domain(board: List[List[int]], row: int, col: int) -> Set[int]:
    if board[row][col] != 0:
        return {board[row][col]}
    return DOMAIN.copy()

# Get all constraints (peers) for a given cell
def get_constraints(row: int, col: int) -> List[Tuple[int, int]]:
    constraints = set()
    
    # Add row constraints
    for j in range(BOARD_SIZE):
        if j != col:
            constraints.add((row, j))
    
    # Add column constraints
    for i in range(BOARD_SIZE):
        if i != row:
            constraints.add((i, col))
    
    # Add subgrid constraints
    subgrid_row = (row // SUBGRID_SIZE) * SUBGRID_SIZE
    subgrid_col = (col // SUBGRID_SIZE) * SUBGRID_SIZE
    for i in range(subgrid_row, subgrid_row + SUBGRID_SIZE):
        for j in range(subgrid_col, subgrid_col + SUBGRID_SIZE):
            if i != row or j != col:
                constraints.add((i, j))
    
    return list(constraints)

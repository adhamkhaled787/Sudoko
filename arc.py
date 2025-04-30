from generator import generate_random_solvable_board,print_board
from collections import deque
import sys

sys.stdout = open("ac3_debug_output.txt", "w")
# Get a board from the generator
board = generate_random_solvable_board(seed_cells=30)
print_board(board)

variables = [(i, j) for i in range(9) for j in range(9)]

def create_domains_from_board(board):
    domains = {}
    for var in variables:
        i, j = var
        if board[i][j] != 0:
            domains[var] = {board[i][j]}
        else:
            domains[var] = set(range(1, 10))
    return domains

def get_neighbors():
    neighbors = {}
    for var in variables:
        row, col = var
        related = set()

        # Row and column neighbors
        for i in range(9):
            if i != col:
                related.add((row, i))
            if i != row:
                related.add((i, col))

        # Box neighbors
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(start_row, start_row + 3):
            for c in range(start_col, start_col + 3):
                if (r, c) != var:
                    related.add((r, c))

        neighbors[var] = related
    return neighbors

def ac3(domains, neighbors):
    queue = deque([(xi, xj) for xi in variables for xj in neighbors[xi]])
    while queue:
        xi, xj = queue.popleft()
        if revise(domains, xi, xj):
            if not domains[xi]:
                return False  # Domain wiped out
            for xk in neighbors[xi] - {xj}:
                queue.append((xk, xi))
    return True

def revise(domains, xi, xj):
    revised = False
    print(f"\nRevising domains for {xi} and {xj}:")
    print(f"Before revision:")
    print(f"  Domain of {xi}: {domains[xi]}")
    print(f"  Domain of {xj}: {domains[xj]}")
    
    # Process the domain reduction
    for x in set(domains[xi]):
        if not any(x != y for y in domains[xj]):
            domains[xi].remove(x)
            print(f"  Removed {x} from domain of {xi} because it has no support in {xj}.")
            revised = True
    
    if revised:
        print(f"After revision:")
        print(f"  Domain of {xi}: {domains[xi]}")
        print(f"  Domain of {xj}: {domains[xj]}")
    else:
        print(f"No revision needed for {xi} and {xj}.")
    
    return revised
domains = create_domains_from_board(board)
neighbors = get_neighbors()
print(domains)
result = ac3(domains, neighbors)
print("\nAC-3 Result:")
print("Consistent" if result else "Inconsistent")

# Optional: show reduced domains
print("\nReduced Domains for Unfilled Cells:")
for var in variables:
     print(f"Cell {var}: {domains[var]}")
     if len(domains[var]) == 1:
        i, j = var
        board[i][j] = next(iter(domains[var])) 
print_board(board)
   
        
sys.stdout.close()
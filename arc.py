from collections import deque

variables = [(i, j) for i in range(9) for j in range(9)]

import logging

# Configure logging to write to a file
logging.basicConfig(
    filename="ac3_steps_log.txt",
    filemode="w",
    level=logging.INFO,
    format="%(message)s"
)


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

        for i in range(9):
            if i != col:
                related.add((row, i))
            if i != row:
                related.add((i, col))

        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(start_row, start_row + 3):
            for c in range(start_col, start_col + 3):
                if (r, c) != var:
                    related.add((r, c))

        neighbors[var] = related
    return neighbors
def ac3(domains, neighbors):
    queue = deque([(xi, xj) for xi in variables for xj in neighbors[xi]])
    logging.info("Starting AC-3 Algorithm\n" + "-"*30)
    log_board_state(domains, "Initial Board from Domains")

    changes_made = True
    while changes_made:
        changes_made = False
        while queue:
            xi, xj = queue.popleft()
            if revise(domains, xi, xj):
                changes_made = True
                if not domains[xi]:
                    logging.info(f"Failure: domain of {xi} wiped out.\n")
                    return False
                for xk in neighbors[xi] - {xj}:
                    queue.append((xk, xi))

        # After each full iteration of arc consistency
        if changes_made:
            log_board_state(domains, "Board After AC-3 Iteration")

    logging.info("AC-3 completed successfully.\n")
    log_board_state(domains, "Final Board After AC-3")
    return True


def revise(domains, xi, xj):
    revised = False
    removed = []

    for x in set(domains[xi]):
        if not any(x != y for y in domains[xj]):
            old_domain = domains[xi]
            domains[xi].remove(x)
            removed.append(x)
            revised = True

    if revised:
        log_msg = f"Revising arc ( {xi} , {xj} ): \n current domain of {xi} :{old_domain}\n current domain of {xj} :{domains[xj]} \n removed values {removed} from {xi}\n updated domain of {xi}: {domains[xi]}"
        logging.info(log_msg)
    else:
        logging.info(f"Revising arc ( {xi} , {xj} ): no changes")

    return revised

def log_board_state(domains, label="Current Board State"):
    board_view = [["." for _ in range(9)] for _ in range(9)]
    for (i, j), values in domains.items():
        if len(values) == 1:
            board_view[i][j] = str(next(iter(values)))
        else:
            board_view[i][j] = "."

    logging.info(f"\n{label}:")
    for i in range(9):
        row_str = ""
        for j in range(9):
            row_str += board_view[i][j] + " "
            if j % 3 == 2 and j != 8:
                row_str += "| "
        logging.info(row_str.strip())
        if i % 3 == 2 and i != 8:
            logging.info("-" * 21)
    logging.info("")  # blank line


def is_complete(domains):
    return all(len(domains[var]) == 1 for var in variables)

def select_unassigned_variable(domains):
    # Minimum Remaining Values (MRV) heuristic
    return min((var for var in variables if len(domains[var]) > 1),
               key=lambda var: len(domains[var]))

def backtrack(domains, neighbors):
    if is_complete(domains):
        return domains

    var = select_unassigned_variable(domains)
    for value in sorted(domains[var]):
        new_domains = {v: set(d) for v, d in domains.items()}
        new_domains[var] = {value}

        if ac3(new_domains, neighbors):
            result = backtrack(new_domains, neighbors)
            if result:
                return result

    return None

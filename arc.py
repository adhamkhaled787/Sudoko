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

# Global counters for tracking pruning statistics
REVISION_COUNT = 0
DOMAINS_PRUNED = 0
TOTAL_CONSTRAINT_CHECKS = 0

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
    # Reset global counters
    global REVISION_COUNT, DOMAINS_PRUNED, TOTAL_CONSTRAINT_CHECKS
    REVISION_COUNT = 0
    DOMAINS_PRUNED = 0
    TOTAL_CONSTRAINT_CHECKS = 0
    
    # Initial queue of all arcs
    queue = deque([(xi, xj) for xi in variables for xj in neighbors[xi]])
    logging.info("Starting AC-3 Algorithm\n" + "-"*30)
    log_board_state(domains, "Initial Board from Domains")

    iterations = 0
    
    # Continue until no more changes are made
    while queue:
        iterations += 1
        revisions_this_iteration = 0
        domains_pruned_this_iteration = 0
        
        # Process current queue
        queue_size = len(queue)
        for _ in range(queue_size):
            xi, xj = queue.popleft()
            REVISION_COUNT += 1
            revisions_this_iteration += 1
            
            domains_pruned_before = DOMAINS_PRUNED
            if revise(domains, xi, xj):
                domains_pruned_this_iteration += (DOMAINS_PRUNED - domains_pruned_before)
                
                if not domains[xi]:
                    logging.info(f"Failure: domain of {xi} wiped out.\n")
                    return False
                
                # Add affected neighbors back to queue for next iteration
                for xk in neighbors[xi] - {xj}:
                    if (xk, xi) not in queue:
                        queue.append((xk, xi))
        
        # Log statistics for this iteration
        logging.info(f"\nIteration {iterations} Stats:")
        logging.info(f"  - Revisions: {revisions_this_iteration}")
        logging.info(f"  - Domains pruned: {domains_pruned_this_iteration}")
        if domains_pruned_this_iteration > 0:
            log_board_state(domains, f"Board After AC-3 Iteration {iterations}")
        logging.info("")

    # Log final statistics
    logging.info("\n" + "="*50)
    logging.info("AC-3 SUMMARY STATISTICS")
    logging.info("="*50)
    logging.info(f"Total iterations: {iterations}")
    logging.info(f"Total revisions: {REVISION_COUNT}")
    logging.info(f"Total domains pruned: {DOMAINS_PRUNED}")
    logging.info(f"Total constraint checks: {TOTAL_CONSTRAINT_CHECKS}")
    logging.info(f"Average domains pruned per revision: {DOMAINS_PRUNED/REVISION_COUNT if REVISION_COUNT else 0:.2f}")
    logging.info("="*50 + "\n")
    
    logging.info("AC-3 completed successfully.\n")
    log_board_state(domains, "Final Board After AC-3")
    return True


def revise(domains, xi, xj):
    global DOMAINS_PRUNED, TOTAL_CONSTRAINT_CHECKS
    revised = False
    removed = []

    for x in set(domains[xi]):
        TOTAL_CONSTRAINT_CHECKS += 1
        # Check if there's no value in domain of xj that satisfies the constraint
        if not any(x != y for y in domains[xj]):
            old_domain = set(domains[xi])  # Make a copy to avoid modification during iteration
            domains[xi].remove(x)
            removed.append(x)
            revised = True
            DOMAINS_PRUNED += 1

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
    # Track backtracking statistics
    backtrack_stats = {
        "nodes_visited": 0,
        "backtracks": 0,
    }
    
    result = _backtrack(domains, neighbors, backtrack_stats)
    
    # Log backtracking statistics
    logging.info("\n" + "="*50)
    logging.info("BACKTRACKING STATISTICS")
    logging.info("="*50)
    logging.info(f"Nodes visited: {backtrack_stats['nodes_visited']}")
    logging.info(f"Backtracks: {backtrack_stats['backtracks']}")
    logging.info("="*50 + "\n")
    
    return result

def _backtrack(domains, neighbors, stats):
    stats["nodes_visited"] += 1
    
    if is_complete(domains):
        return domains

    var = select_unassigned_variable(domains)
    for value in sorted(domains[var]):
        new_domains = {v: set(d) for v, d in domains.items()}
        new_domains[var] = {value}

        if ac3(new_domains, neighbors):
            result = _backtrack(new_domains, neighbors, stats)
            if result:
                return result
    
    stats["backtracks"] += 1
    return None

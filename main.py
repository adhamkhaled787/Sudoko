import json
import time
import tkinter as tk
from tkinter import ttk
from generator import generate_random_solvable_board
from arc import create_domains_from_board, get_neighbors, ac3, variables, backtrack
from gui import run_gui, select_difficulty
from user_input_mode import start_user_input_mode
from interactive_mode import start_interactive_mode

def random_puzzle_mode():
    """Mode 1: Randomly generated puzzles with selectable difficulty."""
    # Track times for each phase
    solve_times = {}
    
    # Step 0: Ask user for difficulty level
    difficulty = select_difficulty()
    
    # Step 1: Generate and save board based on difficulty
    start_time = time.time()
    try:
        board = generate_random_solvable_board(difficulty=difficulty)
        solve_times["Board Generation"] = time.time() - start_time
    except ValueError as e:
        print(f"Error: {e}")
        print("Trying again with default settings...")
        board = generate_random_solvable_board(seed_cells=25, max_attempts=2000)
        solve_times["Board Generation"] = time.time() - start_time
    
    with open("sudoku_board.json", "w") as f:
        json.dump(board, f)

    # Step 2: Keep original copy for GUI display
    original_board = [row[:] for row in board]

    # Step 3: AC-3 constraint propagation
    start_time = time.time()
    domains = create_domains_from_board(board)
    neighbors = get_neighbors()
    ac3(domains, neighbors)
    solve_times["AC-3 Constraint Propagation"] = time.time() - start_time

    # Step 4: If board is incomplete, use backtracking
    if not all(len(domains[var]) == 1 for var in variables):
        print("AC-3 incomplete. Starting backtracking to finish solving.")
        start_time = time.time()
        domains = backtrack(domains, neighbors)
        solve_times["Backtracking"] = time.time() - start_time
        if domains is None:
            raise ValueError("No solution found with backtracking.")

    # Step 5: Update board with final values
    for var in variables:
        if len(domains[var]) == 1:
            i, j = var
            board[i][j] = next(iter(domains[var]))

    # Step 6: Calculate total solving time
    solve_times["Total Solving Time"] = sum(solve_times.values())
    
    # Step 7: Launch GUI with original and updated board plus timing info
    run_gui(board, original_board, solve_times)

def show_mode_selection():
    """Display a window for the user to select the operation mode."""
    root = tk.Tk()
    root.title("Sudoku Solver - Mode Selection")
    
    # Configure the window
    frame = ttk.Frame(root, padding=20)
    frame.pack(fill=tk.BOTH, expand=True)
    
    # Title
    title = ttk.Label(frame, text="Select Mode", font=("Arial", 16, "bold"))
    title.pack(pady=10)
    
    # Mode selection variable
    selected_mode = tk.IntVar(value=1)
    
    # Mode options
    mode1_rb = ttk.Radiobutton(
        frame, 
        text="Mode 1: Random Puzzles (Solver Demo)", 
        variable=selected_mode, 
        value=1
    )
    mode1_rb.pack(anchor=tk.W, pady=5)
    
    mode2_rb = ttk.Radiobutton(
        frame, 
        text="Mode 2: Enter Your Own Puzzle", 
        variable=selected_mode, 
        value=2
    )
    mode2_rb.pack(anchor=tk.W, pady=5)
    
    mode3_rb = ttk.Radiobutton(
        frame, 
        text="Mode 3: Interactive Gameplay", 
        variable=selected_mode, 
        value=3
    )
    mode3_rb.pack(anchor=tk.W, pady=5)
    
    # Description text
    desc_frame = ttk.LabelFrame(frame, text="Mode Description", padding=10)
    desc_frame.pack(fill=tk.X, pady=10)
    
    description = ttk.Label(
        desc_frame,
        text="Mode 1: The program generates and solves Sudoku puzzles.\n"
             "Mode 2: Enter your own Sudoku puzzle to be solved.\n"
             "Mode 3: Play Sudoku interactively with validation and hints.",
        justify=tk.LEFT
    )
    description.pack(anchor=tk.W)
    
    # Start button
    def start_selected_mode():
        mode = selected_mode.get()
        root.destroy()
        if mode == 1:
            random_puzzle_mode()
        elif mode == 2:
            start_user_input_mode()
        elif mode == 3:
            start_interactive_mode()
    
    start_btn = ttk.Button(frame, text="Start", command=start_selected_mode)
    start_btn.pack(pady=15)
    
    # Center the window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

def main():
    """Main program entry point."""
    show_mode_selection()

if __name__ == "__main__":
    main()

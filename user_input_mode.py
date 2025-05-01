import tkinter as tk
from tkinter import ttk, messagebox
import json
import time
from arc import create_domains_from_board, get_neighbors, ac3, variables, backtrack
from gui import run_gui

def create_empty_board():
    """Create an empty 9x9 Sudoku board."""
    return [[0 for _ in range(9)] for _ in range(9)]

class SudokuInputGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Input")
        self.root.resizable(False, False)
        
        # Main container
        main_frame = ttk.Frame(root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, 
                                text="Enter Your Sudoku Puzzle", 
                                font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Instructions
        instructions = ttk.Label(main_frame, 
                                text="Enter numbers 1-9 in cells. Leave cells blank for empty spaces.",
                                font=("Arial", 10))
        instructions.pack(pady=(0, 5))
        
        # Cell counter display
        self.cell_count_var = tk.StringVar(value="Filled cells: 0/17 minimum")
        self.cell_count_label = ttk.Label(main_frame, 
                                textvariable=self.cell_count_var,
                                font=("Arial", 10, "bold"),
                                foreground="red")
        self.cell_count_label.pack(pady=(0, 10))
        
        # Create the input grid
        self.create_input_grid(main_frame)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=15)
        
        # Clear button
        clear_btn = ttk.Button(button_frame, text="Clear Board", command=self.clear_board)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Solve button
        solve_btn = ttk.Button(button_frame, text="Solve", command=self.solve_board)
        solve_btn.pack(side=tk.LEFT, padx=5)
        
        # Center the window
        self.center_window()
    
    def create_input_grid(self, parent):
        """Create the 9x9 grid of input fields."""
        grid_frame = ttk.Frame(parent)
        grid_frame.pack(pady=10)
        
        # Store entry widgets in a 9x9 grid
        self.entries = []
        
        for i in range(9):
            row_entries = []
            for j in range(9):
                # Use custom validation to only allow single digits
                vcmd = (self.root.register(self.validate_input), '%P', '%W')
                entry = ttk.Entry(grid_frame, width=3, font=("Arial", 14), 
                                 justify='center', validate="key", validatecommand=vcmd)
                
                # Visual styling for box borders
                padx = (1, 1)
                pady = (1, 1)
                if j % 3 == 2 and j < 8:
                    padx = (1, 4)  # Add extra padding after every 3rd column
                if i % 3 == 2 and i < 8:
                    pady = (1, 4)  # Add extra padding after every 3rd row
                
                entry.grid(row=i, column=j, padx=padx, pady=pady)
                row_entries.append(entry)
            self.entries.append(row_entries)
        
        # Initial count update
        self.update_cell_count()
    
    def validate_input(self, new_value, widget_name):
        """Validate input to ensure only valid digits or empty."""
        if new_value == "":
            # Schedule an update after the current event completes
            self.root.after(10, self.update_cell_count)
            return True
        if new_value.isdigit() and 1 <= int(new_value) <= 9 and len(new_value) == 1:
            # Schedule an update after the current event completes
            self.root.after(10, self.update_cell_count)
            return True
        return False
    
    def update_cell_count(self):
        """Update the cell counter display."""
        board = self.get_board_from_entries()
        filled_cells = sum(1 for row in board for cell in row if cell > 0)
        
        # Update the display
        color = "green" if filled_cells >= 17 else "red"
        self.cell_count_var.set(f"Filled cells: {filled_cells}/17 minimum")
        
        # Update label color
        self.cell_count_label.configure(foreground=color)
    
    def clear_board(self):
        """Clear all entries in the grid."""
        for row in self.entries:
            for entry in row:
                entry.delete(0, tk.END)
        
        # Update cell count after clearing
        self.update_cell_count()
    
    def get_board_from_entries(self):
        """Extract the Sudoku board from entry widgets."""
        board = []
        for row in self.entries:
            board_row = []
            for entry in row:
                value = entry.get().strip()
                if value and value.isdigit():
                    board_row.append(int(value))
                else:
                    board_row.append(0)  # Empty cell
            board.append(board_row)
        return board
    
    def is_valid_sudoku(self, board):
        """Check if the input board is valid (no duplicate numbers)."""
        # Check rows
        for row in board:
            seen = set()
            for cell in row:
                if cell != 0 and cell in seen:
                    return False
                if cell != 0:
                    seen.add(cell)
        
        # Check columns
        for j in range(9):
            seen = set()
            for i in range(9):
                cell = board[i][j]
                if cell != 0 and cell in seen:
                    return False
                if cell != 0:
                    seen.add(cell)
        
        # Check 3x3 boxes
        for box_row in range(0, 9, 3):
            for box_col in range(0, 9, 3):
                seen = set()
                for i in range(box_row, box_row + 3):
                    for j in range(box_col, box_col + 3):
                        cell = board[i][j]
                        if cell != 0 and cell in seen:
                            return False
                        if cell != 0:
                            seen.add(cell)
        
        return True
    
    def solve_board(self):
        """Solve the user-provided Sudoku board."""
        board = self.get_board_from_entries()
        
        # Count filled cells
        filled_cells = sum(1 for row in board for cell in row if cell > 0)
        
        # Check minimum required cells (17 is mathematically proven minimum for unique solution)
        if filled_cells < 17:
            messagebox.showerror("Insufficient Clues", 
                                 f"You need to fill at least 17 cells for a valid Sudoku puzzle.\nCurrently filled: {filled_cells}")
            return
        
        # Validate the board
        if not self.is_valid_sudoku(board):
            messagebox.showerror("Invalid Board", 
                                 "The board contains duplicate numbers in a row, column, or 3x3 box.")
            return
        
        # Track times for solving phases
        solve_times = {}
        
        # Save the original board (for display)
        original_board = [row[:] for row in board]
        
        # Step 1: Save the board
        with open("sudoku_board.json", "w") as f:
            json.dump(board, f)
        
        # Step 2: AC-3 constraint propagation
        start_time = time.time()
        domains = create_domains_from_board(board)
        neighbors = get_neighbors()
        ac3(domains, neighbors)
        solve_times["AC-3 Constraint Propagation"] = time.time() - start_time
        
        # Step 3: If board is incomplete, use backtracking
        backtracking_used = False
        if not all(len(domains[var]) == 1 for var in variables):
            print("AC-3 incomplete. Starting backtracking to finish solving.")
            backtracking_used = True
            start_time = time.time()
            domains = backtrack(domains, neighbors)
            solve_times["Backtracking"] = time.time() - start_time
            if domains is None:
                messagebox.showerror("Unsolvable", 
                                     "This Sudoku puzzle has no solution.")
                return
        
        # Step 4: Update board with final values
        for var in variables:
            if len(domains[var]) == 1:
                i, j = var
                board[i][j] = next(iter(domains[var]))
        
        # Step 5: Calculate total solving time
        solve_times["Total Solving Time"] = sum(solve_times.values())
        
        # Close the input window
        self.root.destroy()
        
        # Step 6: Display the solved board
        run_gui(board, original_board, solve_times)
    
    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

def start_user_input_mode():
    """Start the user input mode."""
    root = tk.Tk()
    app = SudokuInputGUI(root)
    root.mainloop()

if __name__ == "__main__":
    start_user_input_mode() 
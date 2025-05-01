import tkinter as tk
from tkinter import ttk, messagebox
import json
import copy
from generator import generate_random_solvable_board

class SimpleSudokuGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Sudoku Game")
        self.root.resizable(False, False)
        
        # Initialize game state
        self.difficulty = "medium"  # Default difficulty
        self.selected_cell = None
        self.user_board = None
        self.solution_board = None
        self.original_board = None
        
        # Create main UI
        self.create_main_ui()
    
    def create_main_ui(self):
        """Create the main user interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, 
                                text="Interactive Sudoku Game", 
                                font=("Arial", 16, "bold"))
        title_label.pack(pady=5)
        
        # Top controls frame
        top_controls = ttk.Frame(main_frame)
        top_controls.pack(fill=tk.X, pady=5)
        
        # Difficulty selection
        diff_frame = ttk.LabelFrame(top_controls, text="Difficulty", padding=5)
        diff_frame.pack(side=tk.LEFT, padx=5)
        
        self.difficulty_var = tk.StringVar(value=self.difficulty)
        
        easy_rb = ttk.Radiobutton(diff_frame, text="Easy", value="easy", 
                                 variable=self.difficulty_var)
        medium_rb = ttk.Radiobutton(diff_frame, text="Medium", value="medium", 
                                   variable=self.difficulty_var)
        hard_rb = ttk.Radiobutton(diff_frame, text="Hard", value="hard", 
                                 variable=self.difficulty_var)
        
        easy_rb.pack(anchor=tk.W)
        medium_rb.pack(anchor=tk.W)
        hard_rb.pack(anchor=tk.W)
        
        # Game controls frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=5)
        
        # New Game button
        new_game_btn = ttk.Button(controls_frame, text="New Game", 
                                 command=self.start_new_game)
        new_game_btn.pack(side=tk.LEFT, padx=5)
        
        # Solve button
        solve_btn = ttk.Button(controls_frame, text="Show Solution", 
                              command=self.show_solution)
        solve_btn.pack(side=tk.LEFT, padx=5)
        
        # Reset button
        reset_btn = ttk.Button(controls_frame, text="Reset", 
                              command=self.reset_game)
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        # Create the game board canvas
        self.create_board_canvas(main_frame)
        
        # Create number input pad
        self.create_number_pad(main_frame)
        
        # Status bar
        self.status_var = tk.StringVar(value="Select a difficulty and click 'New Game' to start")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              font=("Arial", 10), anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=5)
        
        # Center the window
        self.center_window()
    
    def create_board_canvas(self, parent):
        """Create the Sudoku board canvas."""
        board_frame = ttk.Frame(parent)
        board_frame.pack(pady=10)
        
        # Canvas for drawing the board
        canvas_size = 450  # Size in pixels
        self.canvas = tk.Canvas(board_frame, width=canvas_size, height=canvas_size, 
                               bg="white", highlightthickness=1, highlightbackground="black")
        self.canvas.pack()
        
        # Bind mouse click event to the canvas
        self.canvas.bind("<Button-1>", self.on_cell_click)
        
        # Cell size
        self.cell_size = canvas_size // 9
        
        # Initialize the board (empty)
        self.draw_empty_board()
    
    def draw_empty_board(self):
        """Draw an empty Sudoku board grid."""
        self.canvas.delete("all")  # Clear canvas
        
        # Draw grid lines
        for i in range(10):
            # Thicker lines for 3x3 box borders
            line_width = 2 if i % 3 == 0 else 1
            
            # Vertical lines
            self.canvas.create_line(
                i * self.cell_size, 0, 
                i * self.cell_size, 9 * self.cell_size, 
                width=line_width
            )
            
            # Horizontal lines
            self.canvas.create_line(
                0, i * self.cell_size, 
                9 * self.cell_size, i * self.cell_size, 
                width=line_width
            )
    
    def create_number_pad(self, parent):
        """Create number input pad."""
        numpad_frame = ttk.LabelFrame(parent, text="Number Pad", padding=5)
        numpad_frame.pack(pady=5)
        
        # Create buttons for numbers 1-9
        buttons_frame = ttk.Frame(numpad_frame)
        buttons_frame.pack()
        
        for i in range(1, 10):
            btn = ttk.Button(buttons_frame, text=str(i), width=3,
                           command=lambda num=i: self.input_number(num))
            btn.grid(row=(i-1)//3, column=(i-1)%3, padx=2, pady=2)
        
        # Clear cell button
        clear_btn = ttk.Button(numpad_frame, text="Clear Cell", 
                              command=lambda: self.input_number(0))
        clear_btn.pack(pady=5)
    
    def on_cell_click(self, event):
        """Handle cell click event."""
        if not self.user_board:
            self.status_var.set("Start a new game first!")
            return
        
        # Get row and column from click coordinates
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        
        # Check if it's a fixed cell (original clue)
        if self.original_board[row][col] != 0:
            self.status_var.set("Cannot modify given numbers!")
            self.selected_cell = None
            self.draw_board()
            return
        
        # Update selected cell
        self.selected_cell = (row, col)
        self.draw_board()
        self.status_var.set(f"Selected cell: Row {row+1}, Column {col+1}")
    
    def input_number(self, number):
        """Input a number into the selected cell."""
        if not self.user_board:
            self.status_var.set("Start a new game first!")
            return
            
        if not self.selected_cell:
            self.status_var.set("Select a cell first!")
            return
        
        row, col = self.selected_cell
        
        # Clear the cell if number is 0
        if number == 0:
            self.user_board[row][col] = 0
            self.draw_board()
            self.status_var.set(f"Cleared cell at Row {row+1}, Column {col+1}")
            return
        
        # Check if the input violates Sudoku constraints
        if self.is_valid_move(row, col, number):
            self.user_board[row][col] = number
            self.status_var.set(f"Placed {number} at Row {row+1}, Column {col+1}")
        else:
            self.status_var.set(f"Invalid move! {number} violates Sudoku constraints")
        
        self.draw_board()
        
        # Check if the board is solved
        if self.is_board_solved():
            messagebox.showinfo("Congratulations!", "You solved the puzzle!")
    
    def is_valid_move(self, row, col, number):
        """Check if placing a number at (row, col) is valid."""
        # Make a temporary board with the number placed
        temp_board = copy.deepcopy(self.user_board)
        temp_board[row][col] = number
        
        # Check row
        if not self.is_valid_row(temp_board, row):
            return False
        
        # Check column
        if not self.is_valid_column(temp_board, col):
            return False
        
        # Check 3x3 box
        if not self.is_valid_box(temp_board, row - row % 3, col - col % 3):
            return False
        
        return True
    
    def is_valid_row(self, board, row):
        """Check if a row has no duplicate numbers."""
        seen = set()
        for num in board[row]:
            if num != 0 and num in seen:
                return False
            if num != 0:
                seen.add(num)
        return True
    
    def is_valid_column(self, board, col):
        """Check if a column has no duplicate numbers."""
        seen = set()
        for row in range(9):
            num = board[row][col]
            if num != 0 and num in seen:
                return False
            if num != 0:
                seen.add(num)
        return True
    
    def is_valid_box(self, board, start_row, start_col):
        """Check if a 3x3 box has no duplicate numbers."""
        seen = set()
        for row in range(start_row, start_row + 3):
            for col in range(start_col, start_col + 3):
                num = board[row][col]
                if num != 0 and num in seen:
                    return False
                if num != 0:
                    seen.add(num)
        return True
    
    def is_board_solved(self):
        """Check if the board is correctly solved."""
        # Check if the board is complete
        for row in range(9):
            for col in range(9):
                if self.user_board[row][col] == 0:
                    return False
        
        # Check if the board matches the solution
        for row in range(9):
            for col in range(9):
                if self.user_board[row][col] != self.solution_board[row][col]:
                    return False
        
        return True
    
    def draw_board(self):
        """Draw the current state of the board."""
        self.draw_empty_board()
        
        if not self.user_board:
            return
        
        for row in range(9):
            for col in range(9):
                value = self.user_board[row][col]
                if value != 0:
                    # Determine text color based on whether it's a fixed cell
                    color = "black" if self.original_board[row][col] != 0 else "blue"
                    
                    # Draw cell background if it's the selected cell
                    if self.selected_cell == (row, col):
                        self.canvas.create_rectangle(
                            col * self.cell_size, row * self.cell_size,
                            (col + 1) * self.cell_size, (row + 1) * self.cell_size,
                            fill="lightblue", outline=""
                        )
                    
                    # Draw the number
                    x = col * self.cell_size + self.cell_size // 2
                    y = row * self.cell_size + self.cell_size // 2
                    self.canvas.create_text(
                        x, y, text=str(value),
                        font=("Arial", 16, "bold"), fill=color
                    )
                elif self.selected_cell == (row, col):
                    # Draw background for empty selected cell
                    self.canvas.create_rectangle(
                        col * self.cell_size, row * self.cell_size,
                        (col + 1) * self.cell_size, (row + 1) * self.cell_size,
                        fill="lightblue", outline=""
                    )
    
    def start_new_game(self):
        """Start a new game."""
        difficulty = self.difficulty_var.get()
        self.difficulty = difficulty
        
        # Reset game state
        self.selected_cell = None
        
        # Generate new board
        self.status_var.set(f"Generating new {difficulty} game...")
        self.root.update()  # Force UI update
        
        # Generate a new board
        board = generate_random_solvable_board(difficulty=difficulty)
        
        # Save original board
        self.original_board = copy.deepcopy(board)
        
        # Create user board (the board the user will interact with)
        self.user_board = copy.deepcopy(board)
        
        # Find solution (we'll need this for hints and checking)
        from arc import create_domains_from_board, get_neighbors, ac3, variables, backtrack
        domains = create_domains_from_board(board)
        neighbors = get_neighbors()
        ac3(domains, neighbors)
        
        if not all(len(domains[var]) == 1 for var in variables):
            domains = backtrack(domains, neighbors)
        
        # Convert domains to solution board
        self.solution_board = copy.deepcopy(board)
        for var in variables:
            if len(domains[var]) == 1:
                i, j = var
                self.solution_board[i][j] = next(iter(domains[var]))
        
        # Draw the board
        self.draw_board()
        
        self.status_var.set(f"New {difficulty} game started. Good luck!")
    
    def show_solution(self):
        """Show the solution."""
        if not self.user_board:
            self.status_var.set("Start a new game first!")
            return
        
        if messagebox.askyesno("Show Solution", 
                              "Are you sure you want to see the solution?"):
            self.user_board = copy.deepcopy(self.solution_board)
            self.draw_board()
            self.status_var.set("Solution displayed.")
    
    def reset_game(self):
        """Reset the game to the original state."""
        if not self.user_board:
            self.status_var.set("Start a new game first!")
            return
        
        if messagebox.askyesno("Reset Game", 
                              "Are you sure you want to reset the game?"):
            self.user_board = copy.deepcopy(self.original_board)
            self.selected_cell = None
            self.draw_board()
            self.status_var.set("Game reset to initial state.")
    
    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

def start_interactive_mode():
    """Start the interactive Sudoku game mode."""
    root = tk.Tk()
    app = SimpleSudokuGame(root)
    root.mainloop()

if __name__ == "__main__":
    start_interactive_mode() 
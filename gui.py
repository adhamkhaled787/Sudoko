import tkinter as tk
from tkinter import ttk, messagebox
import time

def draw_board(canvas_frame, board, original_board):
    for i in range(9):
        for j in range(9):
            cell_value = board[i][j]
            is_original = original_board[i][j] != 0
            color = "black" if is_original else ("blue" if cell_value != 0 else "gray")
            text = str(cell_value) if cell_value != 0 else ""
            label = tk.Label(canvas_frame, text=text, width=4, height=2, font=("Arial", 16),
                             borderwidth=1, relief="solid", fg=color)
            label.grid(row=i, column=j)
            if i % 3 == 0 and i != 0:
                label.grid(row=i, column=j, pady=(5, 0))
            if j % 3 == 0 and j != 0:
                label.grid(row=i, column=j, padx=(5, 0))

def run_gui(board, original_board, solve_times=None):
    root = tk.Tk()
    root.title("Sudoku Solver")
    
    # Main container
    main_frame = ttk.Frame(root, padding=10)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Canvas for the board
    canvas_frame = ttk.Frame(main_frame)
    canvas_frame.pack(pady=10)
    
    # Draw the board
    draw_board(canvas_frame, board, original_board)
    
    # Display solving times if available
    if solve_times:
        time_frame = ttk.LabelFrame(main_frame, text="Solving Performance", padding=10)
        time_frame.pack(fill=tk.X, pady=10)
        
        for phase, time_taken in solve_times.items():
            time_label = ttk.Label(time_frame, 
                                   text=f"{phase}: {time_taken:.6f} seconds")
            time_label.pack(anchor=tk.W)
    
    # Exit button
    exit_btn = ttk.Button(main_frame, text="Exit", command=root.destroy)
    exit_btn.pack(pady=10)
    
    # Center the window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

# Initial difficulty selection window
def select_difficulty():
    root = tk.Tk()
    root.title("Sudoku - Select Difficulty")
    
    frame = ttk.Frame(root, padding=20)
    frame.pack()
    
    label = ttk.Label(frame, text="Select Difficulty Level:", font=("Arial", 12))
    label.pack(pady=10)
    
    difficulty = tk.StringVar()
    difficulty.set("medium")  # Default difficulty
    
    # Create radio buttons for difficulty levels
    easy_rb = ttk.Radiobutton(frame, text="Easy", variable=difficulty, value="easy")
    easy_rb.pack(anchor=tk.W, pady=5)
    
    medium_rb = ttk.Radiobutton(frame, text="Medium", variable=difficulty, value="medium")
    medium_rb.pack(anchor=tk.W, pady=5)
    
    hard_rb = ttk.Radiobutton(frame, text="Hard", variable=difficulty, value="hard")
    hard_rb.pack(anchor=tk.W, pady=5)
    
    # OK button
    def on_ok():
        root.destroy()
    
    ok_btn = ttk.Button(frame, text="Start Game", command=on_ok)
    ok_btn.pack(pady=10)
    
    # Center the window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()
    return difficulty.get()

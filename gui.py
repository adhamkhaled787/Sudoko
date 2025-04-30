import tkinter as tk

def draw_board(root, board, original_board):
    for i in range(9):
        for j in range(9):
            cell_value = board[i][j]
            is_original = original_board[i][j] != 0
            color = "black" if is_original else ("blue" if cell_value != 0 else "gray")
            text = str(cell_value) if cell_value != 0 else ""
            label = tk.Label(root, text=text, width=4, height=2, font=("Arial", 16),
                             borderwidth=1, relief="solid", fg=color)
            label.grid(row=i, column=j)
            if i % 3 == 0 and i != 0:
                label.grid(row=i, column=j, pady=(5, 0))
            if j % 3 == 0 and j != 0:
                label.grid(row=i, column=j, padx=(5, 0))

def run_gui(board, original_board):
    root = tk.Tk()
    root.title("Sudoku AC-3 Visualizer")
    draw_board(root, board, original_board)
    root.mainloop()

import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import copy

class Sudoku:
    def __init__(self, level):
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.solution = []
        self.hints_used = 0
        self.level = level
        self.generate_full_board()
        self.solution = copy.deepcopy(self.board)
        self.remove_cells()

    def generate_full_board(self):
        self.fill_board()

    def fill_board(self):
        empty = self.find_empty()
        if not empty:
            return True
        row, col = empty
        numbers = list(range(1, 10))
        random.shuffle(numbers)
        for num in numbers:
            if self.is_valid(num, row, col):
                self.board[row][col] = num
                if self.fill_board():
                    return True
                self.board[row][col] = 0
        return False

    def is_valid(self, num, row, col):
        for i in range(9):
            if self.board[row][i] == num or self.board[i][col] == num:
                return False
        box_x, box_y = col // 3, row // 3
        for i in range(box_y * 3, box_y * 3 + 3):
            for j in range(box_x * 3, box_x * 3 + 3):
                if self.board[i][j] == num:
                    return False
        return True

    def find_empty(self):
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    return (i, j)
        return None

    def remove_cells(self):
        if self.level == 'easy':
            removals = 30
        elif self.level == 'medium':
            removals = 45
        else:
            removals = 60

        while removals > 0:
            i, j = random.randint(0, 8), random.randint(0, 8)
            if self.board[i][j] != 0:
                self.board[i][j] = 0
                removals -= 1


class SudokuApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Welcome to the Sudoku Game")
        self.master.configure(bg='#fcecd1')  # Skin tone background
        self.entries = [[None for _ in range(9)] for _ in range(9)]
        self.sudoku = None
        self.level = None
        self.selected_cell = None  # Track selected cell
        self.create_level_selector()

    def create_level_selector(self):
        for widget in self.master.winfo_children():
            widget.destroy()

        self.master.configure(bg='#fcecd1')

        label = tk.Label(self.master, text="Select Difficulty Level:", bg='#fcecd1', font=("Arial", 16))
        label.grid(row=0, column=0, columnspan=3, pady=20)

        button_style = {"width": 10, "font": ("Arial", 14), "bg": "#8B4513", "fg": "white"}

        tk.Button(self.master, text="Easy", command=lambda: self.start_game("easy"), **button_style).grid(row=1, column=0, padx=10, pady=10)
        tk.Button(self.master, text="Medium", command=lambda: self.start_game("medium"), **button_style).grid(row=1, column=1, padx=10, pady=10)
        tk.Button(self.master, text="Hard", command=lambda: self.start_game("hard"), **button_style).grid(row=1, column=2, padx=10, pady=10)

    def start_game(self, level):
        self.level = level
        self.sudoku = Sudoku(level)
        self.clear_widgets()
        self.draw_grid()

    def clear_widgets(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def draw_grid(self):
        self.master.configure(bg='#fff5e1')  # lighter skin tone
        vcmd = (self.master.register(self.validate_input), '%P')
        for i in range(9):
            for j in range(9):
                entry = tk.Entry(self.master, width=2, font=('Arial', 18), justify='center',
                                 validate='key', validatecommand=vcmd)
                entry.grid(row=i, column=j, padx=2, pady=2)
                entry.bind("<Button-1>", lambda event, r=i, c=j: self.set_selected_cell(r, c))
                if self.sudoku.board[i][j] != 0:
                    entry.insert(0, str(self.sudoku.board[i][j]))
                    entry.config(state='readonly', disabledforeground='black')
                self.entries[i][j] = entry

        # Buttons
        button_style = {"font": ("Arial", 12), "bg": "#8B4513", "fg": "white", "width": 8, "padx": 5, "pady": 5}
        tk.Button(self.master, text="Hint", command=self.give_hint, **button_style).grid(row=10, column=0, columnspan=3, pady=10)
        tk.Button(self.master, text="Check", command=self.check_solution, **button_style).grid(row=10, column=3, columnspan=3, pady=10)
        tk.Button(self.master, text="Quit", command=self.master.quit, **button_style).grid(row=10, column=6, columnspan=3, pady=10)

    def set_selected_cell(self, row, col):
        self.selected_cell = (row, col)

    def validate_input(self, value):
        return value == "" or (value.isdigit() and 1 <= int(value) <= 9)

    def give_hint(self):
        if self.sudoku.hints_used >= 3:
            messagebox.showinfo("Hint", "You have used all 3 hints.")
            return

        if self.selected_cell is None:
            messagebox.showinfo("Hint", "Select a cell first.")
            return

        row, col = self.selected_cell
        if self.entries[row][col].get() != "":
            messagebox.showinfo("Hint", "Select an empty cell.")
            return

        correct_value = self.sudoku.solution[row][col]

        # Generate math problem
        num1 = random.randint(1, correct_value - 1)
        num2 = correct_value - num1
        user_answer = simpledialog.askinteger("Solve to Get a Hint", f"What is {num1} + {num2}?")

        if user_answer != correct_value:
            messagebox.showerror("Wrong", "Incorrect answer! No hint for now.")
            return

        self.entries[row][col].insert(0, str(correct_value))
        self.entries[row][col].config(state='readonly', disabledforeground='blue')
        self.sudoku.hints_used += 1

        if self.sudoku.hints_used == 3:
            messagebox.showinfo("Hint", "You have used all 3 hints.")

    def check_solution(self):
        board = [[0 for _ in range(9)] for _ in range(9)]

        # Gather inputs
        for i in range(9):
            for j in range(9):
                val = self.entries[i][j].get()
                if val == "":
                    messagebox.showerror("Incomplete", f"Cell ({i+1},{j+1}) is empty.")
                    return
                try:
                    num = int(val)
                    if num < 1 or num > 9:
                        raise ValueError
                    board[i][j] = num
                except ValueError:
                    messagebox.showerror("Invalid Input", f"Invalid number at ({i+1},{j+1}). Only 1-9 allowed.")
                    return

        # Validate board
        def is_valid_board(b):
            for i in range(9):
                row = set()
                col = set()
                for j in range(9):
                    if b[i][j] in row or b[j][i] in col:
                        return False
                    row.add(b[i][j])
                    col.add(b[j][i])

            for box_row in range(3):
                for box_col in range(3):
                    nums = set()
                    for i in range(box_row * 3, box_row * 3 + 3):
                        for j in range(box_col * 3, box_col * 3 + 3):
                            if b[i][j] in nums:
                                return False
                            nums.add(b[i][j])
            return True

        if not is_valid_board(board):
            messagebox.showerror("Incorrect", "Board has duplicate in row, column, or box.")
            return

        # Match solution
        for i in range(9):
            for j in range(9):
                if board[i][j] != self.sudoku.solution[i][j]:
                    messagebox.showerror("Incorrect", "Some entries are incorrect.")
                    return

        messagebox.showinfo("Correct", "Congratulations! You solved the Sudoku.")


if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuApp(root)
    root.mainloop() 

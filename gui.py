import tkinter as tk
from tkinter import font
from PIL import ImageTk, Image

from quarto import *
import agents

class QuartoGUI(tk.Tk):
    def __init__(self, game):
        super().__init__()
        self.title("Quarto Game")
        self._cells = {}
        self._game = game
        self._photos = []

        self.load_photos()
        self._create_menu()
        self._create_board_display()
        self._create_board_grid()
        self._create_piece_grid()

    def load_photos(self):
        image_paths = [f"images/{i}.png" for i in range(16)]

        for image_path in image_paths:
            img = Image.open(image_path)
            img = img.resize((int(0.75*img.width),int(0.75*img.height)))  # Resize the image using PIL

            photo = ImageTk.PhotoImage(img)
            self._photos.append(photo)

    def _create_menu(self):
        menu_bar = tk.Menu(master=self)
        self.config(menu=menu_bar)
        file_menu = tk.Menu(master=menu_bar)
        file_menu.add_command(label="Play Again", command=self.reset_board)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

    def _create_board_display(self):
        display_frame = tk.Frame(master=self)
        display_frame.pack(fill=tk.X)
        self.display = tk.Label(
            master=display_frame,
            text="Ready?",
            font=font.Font(size=28, weight="bold"),
        )
        self.display.pack()

    def _create_board_grid(self):
        grid_frame = tk.Frame(master=self)
        grid_frame.pack(padx=5, pady=20, side=tk.LEFT)
        display1 = tk.Label(
            master=grid_frame,
            text="Board",
            font=font.Font(size=10, weight="bold"),
        )
        for row in range(4):
            self.rowconfigure(row, weight=1, minsize=50)
            self.columnconfigure(row, weight=1, minsize=75)
            for col in range(4):
                button = tk.Button(
                    master=grid_frame,
                    text="",
                    font=font.Font(size=36, weight="bold"),
                    fg="black",
                    width=3,
                    height=2,
                    highlightbackground="lightblue",
                )
                self._cells[button] = (row, col)
                button.bind("<ButtonPress-1>", self.play)
                button.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
    
    def _create_piece_grid(self):
        grid_frame = tk.Frame(master=self)
        grid_frame.pack(padx=5, pady=20, side=tk.LEFT)
        
        for row in range(4):
            self.rowconfigure(row, weight=1, minsize=50)
            self.columnconfigure(row, weight=1, minsize=75)
            for col in range(4):
                button = tk.Button(
                    master=grid_frame,
                    image=self._photos[4*row+col]
                )
                self._cells[button] = (row, col)
                button.bind("<ButtonPress-1>", self.play)
                button.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

    def play(self, event):
        """Handle a player's move."""
        clicked_btn = event.widget
        # row, col = self._cells[clicked_btn]
        # move = Move(row, col, self._game.current_player.label)
        # if self._game.is_valid_move(move):
        #     self._update_button(clicked_btn)
        #     self._game.process_move(move)
        #     if self._game.is_tied():
        #         self._update_display(msg="Tied game!", color="red")
        #     elif self._game.has_winner():
        #         self._highlight_cells()
        #         msg = f'Player "{self._game.current_player.label}" won!'
        #         color = self._game.current_player.color
        #         self._update_display(msg, color)
        #     else:
        #         self._game.toggle_player()
        #         msg = f"{self._game.current_player.label}'s turn"
        #         self._update_display(msg)

    def _update_button(self, clicked_btn):
        clicked_btn.config(text=self._game.current_player.label)
        clicked_btn.config(fg=self._game.current_player.color)

    def _update_display(self, msg, color="black"):
        self.display["text"] = msg
        self.display["fg"] = color

    def _highlight_cells(self):
        for button, coordinates in self._cells.items():
            if coordinates in self._game.winner_combo:
                button.config(highlightbackground="red")

    def reset_board(self):
        """Reset the game's board to play again."""
        self._game.reset_game()
        self._update_display(msg="Ready?")
        for button in self._cells.keys():
            button.config(highlightbackground="lightblue")
            button.config(text="")
            button.config(fg="black")

def main():
    """Create the game's board and run its main loop."""
    game = QuartoGame("Player 1", agents.HumanPlayer(), "Player 2", agents.HumanPlayer(), gui_mode=True, bin_mode=False)
    gui = QuartoGUI(game)
    gui.mainloop()

if __name__ == "__main__":
    main()
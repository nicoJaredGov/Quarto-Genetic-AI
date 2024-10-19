import tkinter as tk
from tkinter import font
from PIL import ImageTk, Image
import time

from quarto import *
import quarto_agents 

class QuartoGUI(tk.Tk):
    def __init__(self, game):
        super().__init__()
        self.title("Quarto Game")
        self._cells = {}
        self.takenCells = set()
        self._pieces = {}
        self.takenPieces = set()
        self._game = game
        self._photos = []
        self.moveTurnEnabled = False

        self.load_photos()
        self._create_menu()
        self._create_board_display()
        self._create_board_grid()
        self._create_piece_grid()

    def load_photos(self):
        image_paths = [f"images/{i}.png" for i in range(17)]
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
        display_frame.pack(fill=tk.X, padx=100)
        self.display = tk.Label(
            master=display_frame,
            text="Ready?",
            font=font.Font(size=28, weight="bold"),
        )
        self.display2 = tk.Label(
            master=display_frame,
            text="Player 1's turn",
            font=font.Font(size=18, weight="bold")
        )
        self.currentButton = tk.Button(
            master=display_frame,
            fg="black",
            width=100,
            height=100,
            text="Current",
            font= ('Helvetica 12 bold'),
            image=self._photos[16],
            compound='center'
        )
        self.startButton = tk.Button(
            master=display_frame,
            fg="black",
            width=10,
            height=5,
            text="Start",
            font= ('Helvetica 12 bold'),
        )
        self.display.pack()
        self.display2.pack()
        self.currentButton.pack(side=tk.LEFT)
        self.startButton.pack(side=tk.RIGHT)
        self.startButton.bind("<ButtonPress-1>", self.play)

    def _create_board_grid(self):
        grid_frame = tk.Frame(master=self, background="black", padx=20, pady=20)
        grid_frame.pack(padx=50, pady=50, side=tk.LEFT)
        for row in range(4):
            for col in range(4):
                button = tk.Button(
                    master=grid_frame,
                    fg="black",
                    width=100,
                    height=100,
                    text=4*row+col,
                    font= ('Helvetica 12 bold'),
                    image=self._photos[16],
                    compound='center',
                    bd=0
                )
                self._cells[(row,col)] = button
                button.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")
    
    def _create_piece_grid(self):
        grid_frame = tk.Frame(master=self, background="#876c3e")
        grid_frame.pack(padx=50, pady=20, side=tk.LEFT)
        
        for row in range(4):
            self.rowconfigure(row, weight=1, minsize=50)
            self.columnconfigure(row, weight=1, minsize=75)
            for col in range(4):
                button = tk.Button(
                    master=grid_frame,
                    text=str(4*row+col),
                    font= ('Helvetica 15 bold'),
                    image=self._photos[4*row+col],
                    compound= tk.RIGHT,
                    relief=tk.FLAT,
                    bd=0,
                )
                self._pieces[(row,col)] = button
                button.grid(row=row, column=col, padx=5, pady=5)

    def makeMove(self, position, nextPiece):
        #validation checks
        if position not in range(16):
            self.display2['text'] = "This position does not exist"
            return False
        if nextPiece not in range(16):
            self.display2['text'] = "This piece does not exist"
            return False
        if position not in self._game.availablePositions:
            self.display2['text'] = "This cell is unavailable"
            return False
        if nextPiece not in self._game.availablePieces:
            self.display2['text'] = "This piece is not available"
            return False
        
        #add to move history
        self._game.moveHistory.append((position,nextPiece))
        
        #place piece on board and update game state
        self.update_cell(position)
        row, col = qutil.get2dCoords(position)
        self._game.board[row][col] = self._game.currentPiece
        self._game.availablePositions.remove(position)

        #set next player's piece
        self.update_current(nextPiece)
        self._game.currentPiece = nextPiece
        self._game.availablePieces.remove(self._game.currentPiece)

        if self._game.gui_mode: print("Move successful")
        return True   
    
    def play(self, event):
        turn = True #player 1 - True, player 2 - False
        self.display['text'] = "Player 1's turn"

        # first move
        self.display2['text'] = "Pick the first piece"
        first_move = self._game.player1.makeFirstMove(self._game.getGameState())
        self._game.makeFirstMove(first_move)
        self.update_current(first_move)
        turn = False 
     
        if self._game.gui_mode: self._game.showGameState()

        # subsequent moves
        for i in range(len(self._game.availablePositions)-1):
            if self._game.gui_mode: self._game.showPlayerName(turn)

            # player 1
            if turn:
                self.display['text'] = "Player 1's turn"
                self.display2['text'] = "Agent is playing..."

                for i in range(3):
                    position, nextPiece = self._game.player1.makeMove(self._game.getGameState())
                    validMove = self.makeMove(position, nextPiece)
                    if validMove:
                        break
                    elif i==2:
                        print("Three invalid moves made - game ended")
                        return
            # player 2
            else:
                self.display['text'] = "Player 2's turn"
                self.display2['text'] = "Agent is playing..."

                for i in range(3):
                    position, nextPiece = self._game.player2.makeMove(self._game.getGameState())
                    validMove = self.makeMove(position, nextPiece)
                    if validMove:
                        break
                    elif i==2:
                        print("Three invalid moves made - game ended")
                        return

            if self._game.gui_mode: self._game.showGameState()

            if (qutil.isGameOver(self._game.board)):
                if turn: 
                    self.display['text'] = "Player 1 Won!"
                    self.display2['text'] = ""
                else: 
                    self.display['text'] = "Player 2 Won!"
                    self.display2['text'] = ""
                return
            turn = not turn

        # Place last piece and set nextPiece to nothing
        if self._game.gui_mode: self._game.showPlayerName(turn)
        self._game.makeLastMove()

        if self._game.gui_mode: self._game.showGameState()

        if (qutil.isGameOver(self._game.board)):
            if turn: 
                self.display['text'] = "Player 1 Won!"
                self.display2['text'] = ""
            else: 
                self.display['text'] = "Player 2 Won!"
                self.display2['text'] = ""
            return
        else:
            self.display['text'] = "DRAW!"
            self.display2['text'] = ""
        
    def update_current(self, piece):
        target = self.currentButton
        target.configure(image=self._photos[piece], bg="#876c3e", text="")
        piece = self._pieces[qutil.get2dCoords(piece)]
        piece.configure(state=tk.DISABLED)
        self.takenPieces.add(piece)

    def update_cell(self, position):
        piece = self._game.currentPiece
        target = self._cells[qutil.get2dCoords(position)]
        target.configure(image=self._photos[piece], bg="#876c3e", text="")
        self.takenCells.add(target)
        self.currentButton.configure(image=self._photos[16], text="current")

    def _update_display(self, msg, color="black"):
        self.display["text"] = msg
        self.display["fg"] = color

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
    game = QuartoGame(quarto_agents.HumanPlayer(), quarto_agents.RandomAgent(), gui_mode=True, bin_mode=False)
    gui = QuartoGUI(game)
    gui.mainloop()

if __name__ == "__main__":
    main()
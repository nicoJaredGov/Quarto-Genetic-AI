import numpy as np
import quarto_util as qutil

class QuartoGame:
    def __init__(self, gui_mode=True):

        #additional config
        self.gui_mode = gui_mode
        #game state
        self.board = np.full((4,4), 16)
        self.currentPiece = 16 #set to nothing upon starting
        self.availablePieces = set(range(16))
        self.availablePositions = set(range(16))

    #experimental method to allow any board to be loaded and simulated from that point
    #NOTE 1 First move function has to be called again to set the current player's piece to place
    #NOTE 2 There is obviously no game history. Only history after the board is loaded can be recorded.
    def setBoard(self, board_encoding=None):
        #no board encoding passed, therefore clear board
        if board_encoding is None:
            self.board = np.full((4,4), 16)
            self.availablePieces = set(range(16))
            self.availablePositions = set(range(16))
            
        else:
            board_array = [int(board_encoding[i]+board_encoding[i+1]) for i in range(0,len(board_encoding),2)]

            #determine available positions
            self.availablePositions = set([i for i, e in enumerate(board_array) if e == 16])

            #determine which pieces are still available
            self.availablePieces = set(board_array)
            if 16 in self.availablePieces:
                self.availablePieces.remove(16)
            self.availablePieces = set(range(16)) - self.availablePieces
  
            self.board = np.reshape(board_array, (4,4))
    
    def encodeBoard(self):
        return qutil.encodeBoard(self.board)
    
    def showBoard(self):
        if self.gui_mode:
            for i in range(4):
                print("._____._____._____._____.")
                line = ""
                for j in range(4):
                    piece = str(self.board[i][j])
                    if piece == "16":
                        piece = "  "

                    if len(piece) == 2:
                        if j == 3:
                            line += "|  "+piece+" |"
                        else:
                            line += "|  "+piece+" "
                    else:
                        if j == 3:
                            line += "|  "+piece+"  |"
                        else:
                            line += "|  "+piece+"  "
                print(line)
            print("._____._____._____._____.")
        else:
            print(self.board)
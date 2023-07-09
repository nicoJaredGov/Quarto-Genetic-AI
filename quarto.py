import numpy as np
import quarto_util as qutil

class QuartoGame:
    def __init__(self, gui_mode=True):
        self.board = np.full((4,4), 16)
        self.gui_mode = gui_mode

    def setBoard(self, board_encoding=None):
        #no board encoding passed, therefore clear board
        if board_encoding is None:
            self.board = np.full((4,4), 16)
        else:
            self.board = qutil.decodeBoard(board_encoding)
    
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
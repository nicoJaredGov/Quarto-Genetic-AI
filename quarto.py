import numpy as np
import quarto_util as util

class QuartoGame:
    def __init__(self):
        self.board = np.full((4,4), 16)

    def setBoard(self, board_encoding=None):
        #no board encoding passed, therefore clear board
        if board_encoding is None:
            self.board = [[16]*4]*4
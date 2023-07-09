import numpy as np
import quarto_util as util

'''
----------------------
QUARTO SIMULATOR GUIDE
----------------------
Bit representation (from left to right):
1st bit - 0=dark 1=light
2nd bit - 0=round 1=square
3rd bit - 0=short 1=tall
4th bit - 0=hollow 1=solid

Piece Representation:
VALUE   |   BINARY  |
0           0000        
1           0001
2           0010
3           0011

4           0100
5           0101
6           0110
7           0111

8           1000
9           1001
10          1010
11          1011

12          1100
13          1101
14          1110
15          1111

16          empty cell
'''

class QuartoGame:
    def __init__(self):
        self.board = np.full((4,4), 16)

    def setBoard(self, board_encoding=None):
        #no board encoding passed, therefore clear board
        if board_encoding is None:
            self.board = [[16]*4]*4
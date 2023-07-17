import numpy as np
import quarto_util as qutil
import quarto_agents as qagents

class QuartoGame:
    def __init__(self, agent1: qagents.GenericQuartoAgent, agent2: qagents.GenericQuartoAgent, gui_mode=True):
        '''
        agent1:
            Agent initialized for player 1. 
        agent2:
            Agent initialized for player 2.
        gui_mode:
            Show graphical board if true.
        '''

        #additional config
        self.checkAgentsValid(agent1, agent2)
        self.player1 = agent1
        self.player2 = agent2
        self.gui_mode = gui_mode

        #game state
        self.board = np.full((4,4), 16)
        self.currentPiece = 16 #set to nothing upon starting
        self.availablePieces = set(range(16))
        self.availablePositions = set(range(16))

    def checkAgentsValid(self, agent1, agent2):
        assert agent1 is not None and issubclass(type(agent1), qagents.GenericQuartoAgent), "Agent 1 is not initialized correctly."
        assert agent2 is not None and issubclass(type(agent1), qagents.GenericQuartoAgent), "Agent 2 is not initialized correctly."

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
            print("._____._____._____._____.\n")
        else:
            print(self.board)

    def showGameInformation(self):
        print("current player: ")
        print("current piece to place: ", self.currentPiece)
        print("available pieces: ", self.availablePieces)
        print("available positions: ", self.availablePositions)
        print("\n")

    "This function is ONLY for the first move of the game (the first player's first move)"
    def makeFirstMove(self, nextPiece):
        self.currentPiece = nextPiece
        self.availablePieces.remove(self.currentPiece)
        print("First move successful")
    
    "This function is for every move after than the first one"
    def makeMove(self, position, nextPiece):
        #checks
        if position not in self.availablePositions:
            print("This cell is not empty")
            return
        if nextPiece not in self.availablePieces:
            print("This piece has already been placed or will be placed now")
            return
        
        #place piece on board and update game state
        row, col = qutil.get2dCoords(position)
        self.board[row][col] = self.currentPiece
        self.availablePositions.remove(position)

        #set next player's piece
        self.currentPiece = nextPiece
        self.availablePieces.remove(self.currentPiece)
        
        print("Move successful")

    def evaluateBoard(self):
        #NOTE: for testing only
        if len(self.availablePositions) == 0:
            return True #won
        else:
            return False #lost
        
    def play(self):
        #first move
        first_move = self.player1.makeFirstMove()
        self.makeFirstMove(first_move)
        turn = False #player 1 - True, player 2 - False

        self.showBoard()
        self.showGameInformation()

        #subsequent moves
        while True:
            #player 1
            if turn:
                position, nextPiece = self.player1.makeMove()
            #player 2
            else: 
                position, nextPiece = self.player2.makeMove()

            self.makeMove(position, nextPiece)
            if (self.evaluateBoard()):
                if turn: print("Player 1 won!")
                else: print("Player 2 won!")
                return
            
            turn = not turn

            self.showBoard()
            self.showGameInformation()
    
    #pick random piece from available pieces
    def pickRandomPiece(self):
        return np.random.choice(list(self.availablePieces))
    
    def playRandomFirst(self):
        #player 1's choice of next piece is randomly chosen
        self.makeFirstMove(self.pickRandomPiece())
        turn = False #player 1 - True, player 2 - False

        self.showBoard()
        self.showGameInformation()

        #subsequent moves
        while True:
            #player 1
            if turn:
                position, nextPiece = self.player1.makeMove()
            #player 2
            else: 
                position, nextPiece = self.player2.makeMove()

            self.makeMove(position, nextPiece)
            if (self.evaluateBoard()):
                if turn: print("Player 1 won!")
                else: print("Player 2 won!")
                return
            
            turn = not turn

            self.showBoard()
            self.showGameInformation()

import numpy as np
import quarto_util as qutil
import quarto_agents as qagents

class QuartoGame:
    def __init__(self, name1, agent1: qagents.GenericQuartoAgent, name2, agent2: qagents.GenericQuartoAgent, gui_mode=True, bin_mode=False):
        '''
        agent1:
            Agent initialized for player 1. 
        agent2:
            Agent initialized for player 2.
        gui_mode:
            Show graphical board if true.
        '''

        # additional configuration
        self.checkAgentsValid(agent1, agent2)
        self.player1 = agent1
        self.player2 = agent2
        self.player1Name = name1
        self.player2Name = name2
        self.gui_mode = gui_mode #show graphical view of board
        self.bin_mode = bin_mode #if terminal view is shown, replace integer piece representation with binary representation

        # game state
        self.board = np.full((4,4), 16)
        self.currentPiece = 16 #set to nothing upon starting
        self.availablePieces = set(range(16))
        self.availablePositions = set(range(16))
        self.moveHistory = list()

    def checkAgentsValid(self, agent1, agent2):
        assert agent1 is not None and issubclass(type(agent1), qagents.GenericQuartoAgent), "Agent 1 is not initialized correctly."
        assert agent2 is not None and issubclass(type(agent1), qagents.GenericQuartoAgent), "Agent 2 is not initialized correctly."

    def resetGame(self):
        self.board = np.full((4,4), 16)
        self.currentPiece = 16 #set to nothing upon starting
        self.availablePieces = set(range(16))
        self.availablePositions = set(range(16))
        self.moveHistory = list()

    # Experimental method to allow any board to be loaded and simulated from that point
    # NOTE There is no game history as a result. Only history after the board is loaded can be recorded.
    def setBoard(self, board_encoding):
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

    def showPlayerName(self, turn):
        #turn
        #True = player 1
        #False = player 2
        if turn:
            print(f"\n ------{self.player1Name}'s Turn---------\n")
        else:
            print(f"\n ------{self.player2Name}'s Turn---------\n")   

    def showBoard(self):
        if self.bin_mode:
            for i in range(4):
                print(".______.______.______.______.")
                line = ""
                for j in range(4):
                    piece = str(self.board[i][j])
                    if piece == "16":
                        piece = f"({qutil.getLinearCoords(i,j)})"
                    else:
                        piece = f"{self.board[i][j]:04b}"

                    if len(piece) == 4:
                        if j == 3:
                            line += "| "+piece+" |"
                        else:
                            line += "| "+piece+" "
                    else:
                        if j == 3:
                            line += "| "+piece+"  |"
                        else:
                            line += "| "+piece+"  "
                print(line)
            print(".______.______.______.______.\n")
        else:
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

    def showGameInformation(self):
        print("current piece to place: ", self.currentPiece)
        print("available pieces: ", self.availablePieces)
        print("available positions: ", self.availablePositions)
        print("\nmove history: ", self.moveHistory)
        print("\n")

    def showGameState(self):
        self.showBoard()
        self.showGameInformation()
        
    def getGameState(self):
        return (
            self.board,
            self.currentPiece,
            self.availablePieces,
            self.availablePositions
            )
    
    # This method is ONLY for the first move of the game (the first player's first move)
    def makeFirstMove(self, nextPiece):
        self.currentPiece = nextPiece
        self.availablePieces.remove(self.currentPiece)
        self.moveHistory.append((None,nextPiece))
        if self.gui_mode: print("First move successful")
    
    # This method is for every move after than the first one
    def makeMove(self, position, nextPiece):
        #validation checks
        if position not in range(16):
            print("This position does not exist\n")
            return
        if nextPiece not in range(16):
            print("This piece does not exist\n")
            return
        if position not in self.availablePositions:
            print("This cell is unavailable\n")
            return False
        if nextPiece not in self.availablePieces:
            print("This piece has already been placed or will be placed now\n")
            return False
        
        #add to move history
        self.moveHistory.append((position,nextPiece))
        
        #place piece on board and update game state
        row, col = qutil.get2dCoords(position)
        self.board[row][col] = self.currentPiece
        self.availablePositions.remove(position)

        #set next player's piece
        self.currentPiece = nextPiece
        self.availablePieces.remove(self.currentPiece)
        
        if self.gui_mode: print("Move successful")
        return True
    
    # This method is for automatically placing the last piece in the last position
    def makeLastMove(self):
        #get last available position and place final piece there
        lastPosition = self.availablePositions.pop()
        row, col = qutil.get2dCoords(lastPosition)
        self.board[row][col] = self.currentPiece
        self.moveHistory.append((lastPosition,None))
        if self.gui_mode: print("Last move successful")

    # Pick random piece from available pieces
    def pickRandomPiece(self):
        return np.random.choice(list(self.availablePieces))
        
    def play(self):
        turn = True # player 1 - True, player 2 - False
        if self.gui_mode: self.showPlayerName(turn)

        # first move
        first_move = self.player1.makeFirstMove(self.getGameState())
        self.makeFirstMove(first_move)
        turn = False 

        if self.gui_mode: self.showGameState()

        # subsequent moves
        for i in range(len(self.availablePositions)-1):
            if self.gui_mode: self.showPlayerName(turn)

            # player 1
            if turn:
                for i in range(3):
                    position, nextPiece = self.player1.makeMove(self.getGameState())
                    validMove = self.makeMove(position, nextPiece)
                    if validMove: break
                    elif i==2:
                        print("Three invalid moves made - game ended")
                        return
            # player 2
            else: 
                for i in range(3):
                    position, nextPiece = self.player2.makeMove(self.getGameState())
                    validMove = self.makeMove(position, nextPiece)
                    if validMove: break
                    elif i==2:
                        print("Three invalid moves made - game ended")
                        return

            if self.gui_mode: self.showGameState()

            if (qutil.isGameOver(self.board)):
                if turn: print(f"\nPlayer 1 ({self.player1Name}) won!")
                else: print(f"\nPlayer 2 ({self.player2Name}) won!")
                return
            turn = not turn

        # Place last piece and set nextPiece to nothing
        if self.gui_mode: self.showPlayerName(turn)
        self.makeLastMove()

        if self.gui_mode: self.showGameState()
        
        if (qutil.isGameOver(self.board)):
            if turn: print(f"\nPlayer 1 ({self.player1Name}) won!")
            else: print(f"\nPlayer 2 ({self.player2Name}) won!")
            return
        else:
            print("\nDraw!")
            
        
    
    def playRandomFirst(self):      
        turn = True #player 1 - True, player 2 - False
        if self.gui_mode: self.showPlayerName(turn)

        #player 1's choice of next piece is randomly chosen
        self.makeFirstMove(self.pickRandomPiece())
        turn = False

        if self.gui_mode: self.showGameState()

        # subsequent moves
        for i in range(len(self.availablePositions)-1):
            if self.gui_mode: self.showPlayerName(turn)

            # player 1
            if turn:
                for i in range(3):
                    position, nextPiece = self.player1.makeMove(self.getGameState())
                    validMove = self.makeMove(position, nextPiece)
                    if validMove: break
                    elif i==2:
                        print("Three invalid moves made - game ended")
                        return
            # player 2
            else: 
                for i in range(3):
                    position, nextPiece = self.player2.makeMove(self.getGameState())
                    validMove = self.makeMove(position, nextPiece)
                    if validMove: break
                    elif i==2:
                        print("Three invalid moves made - game ended")
                        return

            if self.gui_mode: self.showGameState()

            if (qutil.isGameOver(self.board)):
                if turn: print(f"\nPlayer 1 ({self.player1Name}) won!")
                else: print(f"\nPlayer 2 ({self.player2Name}) won!")
                return
            turn = not turn

        # Place last piece and set nextPiece to nothing
        if self.gui_mode: self.showPlayerName(turn)
        self.makeLastMove()

        if self.gui_mode: self.showGameState()

        if (qutil.isGameOver(self.board)):
            if turn: print(f"\nPlayer 1 ({self.player1Name}) won!")
            else: print(f"\nPlayer 2 ({self.player2Name}) won!")
            return
        else:
            print("\nDraw!")
        
        

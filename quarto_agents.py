from abc import ABC, abstractmethod
from typing import Any
from numpy import random
import numpy as np
import itertools
import quarto_util as qutil

class GenericQuartoAgent(ABC):
    
    @abstractmethod
    def makeFirstMove(self, quartoGameState) -> int:
        pass

    @abstractmethod
    def makeMove(self, quartoGameState) -> Any:
        pass

class HumanPlayer(GenericQuartoAgent):

    def makeFirstMove(self, quartoGameState):
        nextPiece = int(input("Pick your opponent's first piece: "))
        return nextPiece
    
    def makeMove(self, quartoGameState):
        position = int(input("Cell: "))
        nextPiece = int(input("Your opponent's next piece: "))
        return position, nextPiece

class RandomQuartoAgent(GenericQuartoAgent):

    def makeFirstMove(self, quartoGameState):
        nextPiece = random.choice(list(quartoGameState[2]))
        return nextPiece
    
    def makeMove(self, quartoGameState):
        position = random.choice(list(quartoGameState[3]))
        nextPiece = random.choice(list(quartoGameState[2]))
        print(f"Random agent placed piece at cell {position} and nextPiece is {nextPiece}")
        return position, nextPiece
   
# NegaMax with Alpha-Beta pruning   
class NegamaxAgent(GenericQuartoAgent):

    def __init__(self, depth) -> None:
        super().__init__()
        self.depth = depth

    # Only used in debugging
    def makeFirstMove(self, quartoGameState):
        nextPiece = int(input("Pick your opponent's first piece: "))
        return nextPiece
    
    def makeMove(self, quartoGameState):
        #print("\nSTATE RECEIVED: ", quartoGameState)
        maxScore, (position, nextPiece) = self.alphaBeta(quartoGameState, self.depth, -1000, 1000)
        print(f"Negamax agent placed piece at cell {position} and nextPiece is {nextPiece}")
        print("maxEval: ",maxScore)
        return position, nextPiece
    
    def alphaBeta(self, quartoGameState, depth, alpha, beta):
        board, currentPiece, availableNextPieces, availablePositions = quartoGameState

        if qutil.isGameOver(board):
            return -np.inf, (16,16)
        if depth == 0 or len(availablePositions) == 0:
            return self.evaluation(board), (16,16)
        
        if len(availableNextPieces) == 0:
            availableNextPieces.add(16)

        maxScore = -np.inf
        bestMove = (16,16)

        for move in itertools.product(availablePositions, availableNextPieces):
            print("\ndepth:", depth,"move:", move)
            #simulate move
            row, col = qutil.get2dCoords(move[0])
            board[row][col] = currentPiece
            availablePositions.remove(move[0])
            availableNextPieces.remove(move[1])
            nextGameState = (board, move[1], availableNextPieces, availablePositions)

            #call for next turn
            cur = -self.alphaBeta(nextGameState, depth-1, -beta, -alpha)[0]
            if cur >= maxScore:
                maxScore = cur
                bestMove = move
            alpha = max(alpha, maxScore)
            
            #undo simulated move
            board[row][col] = 16
            availablePositions.add(move[0])
            availableNextPieces.add(move[1])

            print(f"score: {cur}  a: {alpha}  b: {beta}")
            if alpha > beta:
                availableNextPieces.discard(16)
                return alpha, bestMove

        availableNextPieces.discard(16)        
        return maxScore, bestMove
    
    #counts how many lines of three pieces with an identical property
    def evaluation(self, board):
        #can check in transposition table here

        tempLine = None
        numLines = 0

        for i in range(4):
            #check horizontal lines
            tempLine = list(board[i])
            if np.count_nonzero(board[i] == 16) == 1:
                tempLine.remove(16)
                if qutil.matchingPropertyExists(tempLine):
                    numLines += 1
            
            tempLine = list(board[:,i])
            #check vertical lines
            if np.count_nonzero(board[:,i] == 16) == 1:
                tempLine.remove(16)
                if qutil.matchingPropertyExists(tempLine):
                    numLines += 1

        #check obtuse diagonal line
        tempLine = list(np.diag(board))
        if np.count_nonzero(np.diag(board) == 16) == 1:
            tempLine.remove(16)
            if qutil.matchingPropertyExists(tempLine):
                    numLines += 1
            
        #check acute diagonal line:
        tempLine = list(np.diag(board[::-1]))
        if np.count_nonzero(np.diag(board[::-1]) == 16) == 1:
            tempLine.remove(16)
            if qutil.matchingPropertyExists(tempLine):
                    numLines += 1
        
        #no winning line found
        return numLines
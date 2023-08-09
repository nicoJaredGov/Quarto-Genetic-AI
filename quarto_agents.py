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
   
#NegaMax with Alpha-Beta pruning   
class NegamaxAgent(GenericQuartoAgent):

    def makeFirstMove(self, quartoGameState):
        nextPiece = random.choice(list(quartoGameState[2]))
        return nextPiece
    
    def makeMove(self, quartoGameState):
        position = random.choice(list(quartoGameState[3]))
        nextPiece = random.choice(list(quartoGameState[2]))
        print(f"Random agent placed piece at cell {position} and nextPiece is {nextPiece}")
        return position, nextPiece
    
    def alphaBeta(self, quartoGameState, depth, alpha, beta):
        board, currentPiece, availableNextPieces, availablePositions = quartoGameState

        if depth == 0 or qutil.isGameOver(board) or len(availablePositions) == 0:
            return self.evaluation(board)
        
        score = -np.inf
        for move in itertools.product(availablePositions, availableNextPieces):
            #simulate move
            row, col = qutil.get2dCoords(move[0])
            board[row][col] = currentPiece
            availablePositions.remove(move[0])
            availableNextPieces.remove(currentPiece)
            nextGameState = (board, move[1], availableNextPieces, availablePositions)

            #call for next turn
            cur = -self.alphaBeta(nextGameState, depth-1, -beta, -alpha)
            if cur > score:
                score = cur
            if score > alpha:
                alpha = score
            
            #undo simulated move
            board[row][col] = 16
            availablePositions.add(move[0])
            availableNextPieces.add(currentPiece)

            if alpha >= beta:
                return alpha
                
        return score
    
    def evaluation(self, boardArray):
        #can check in transposition table here
        return 1
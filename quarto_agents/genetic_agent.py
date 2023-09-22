from quarto_agents.generic_quarto_agent import GenericQuartoAgent
import quarto_util as qutil
import numpy as np
from bigtree.node.node import Node

class GeneticMinmaxAgent(GenericQuartoAgent):

    def __init__(self, maxGenerations, crossoverRate, mutationRate, initialPopulationSize, maxPopulationSize) -> None:
        super().__init__()

        #hyperparameters
        self.maxGenerations = maxGenerations
        self.crossoverRate = crossoverRate
        self.mutationRate = mutationRate
        self.initialPopulationSize = initialPopulationSize
        self.maxPopulationSize = maxPopulationSize


    # Only used in debugging
    def makeFirstMove(self, quartoGameState):
        nextPiece = int(input("Pick your opponent's first piece: "))
        return nextPiece
    
    def makeMove(self, quartoGameState):
        maxScore, (position, nextPiece) = 16, (16,16)

        #initialize reservation tree
        currentBoardEncoding = qutil.encodeBoard(quartoGameState[0], quartoGameState[1])
        self.reservationTree = ReservationTree(currentBoardEncoding)

        print(f"Genetic agent placed piece at cell {position} and nextPiece is {nextPiece}")
        print("maxEval: ",maxScore)
        return position, nextPiece
    
    def createChromosomes(self, quartoGameState):
        positions = set(range(16))
        pieces = set(range(16)) 

    # Counts how many lines of three pieces with an identical property
    def evaluation(self, board):
        tempLine = None
        numLines = 0

        for i in range(4):
            # check horizontal lines
            tempLine = list(board[i])
            if np.count_nonzero(board[i] == 16) == 1:
                tempLine.remove(16)
                if qutil.matchingPropertyExists(tempLine):
                    numLines += 1
            
            tempLine = list(board[:,i])
            # check vertical lines
            if np.count_nonzero(board[:,i] == 16) == 1:
                tempLine.remove(16)
                if qutil.matchingPropertyExists(tempLine):
                    numLines += 1

        # check obtuse diagonal line
        tempLine = list(np.diag(board))
        if np.count_nonzero(np.diag(board) == 16) == 1:
            tempLine.remove(16)
            if qutil.matchingPropertyExists(tempLine):
                    numLines += 1
            
        # check acute diagonal line:
        tempLine = list(np.diag(board[::-1]))
        if np.count_nonzero(np.diag(board[::-1]) == 16) == 1:
            tempLine.remove(16)
            if qutil.matchingPropertyExists(tempLine):
                    numLines += 1
        
        # no winning line found
        return numLines

class ReservationTree():

     def __init__(self, rootEncoding) -> None:
          self.nodes = list()
          rootNode = Node(rootEncoding, value=-10)
          self.nodes.append(rootNode)

          


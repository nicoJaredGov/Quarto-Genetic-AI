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
        print(f"Genetic agent placed piece at cell {position} and nextPiece is {nextPiece}")
        print("maxEval: ",maxScore)
        return position, nextPiece
    
    #Each move consists of 4 consecutive characters in the chromosome - 2 for place and 2 for next piece
    #movePath is defined as a list of tuples which represent moves
    def encodeChromosome(self, movePath):
        encoding = ""

        for move in movePath:
            movePos = move[0]
            movePiece = move[1]

            if movePos <= 9:
                encoding += "0"+str(movePos)
            else:
                encoding += str(movePos)
        
            if movePiece <= 9:
                encoding += "0"+str(movePiece)
            else:
                encoding += str(movePiece)
            
        return encoding

    def decodeChromosome(self, chromosome):
        movePath = [(int(chromosome[i]+chromosome[i+1]),int(chromosome[i+2]+chromosome[i+3])) for i in range(0,len(chromosome)-3,4)]

        return movePath
    
    def createChromosome(self, quartoGameState):
        pass
         
    def generateSolution(self, quartoGameState):
        board, currentPiece, availableNextPieces, availablePositions = quartoGameState
        currentBoardEncoding = qutil.encodeBoard(board, currentPiece)

        #initialize reservation tree
        self.reservationTree = ReservationTree(currentBoardEncoding)
        
        #randomize initial population
        currentPopulation = []


        
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

          


from quarto_agents.generic_quarto_agent import GenericQuartoAgent
import quarto_util as qutil
import numpy as np
from bigtree.node.node import Node
from copy import deepcopy
from random import sample

class GeneticMinmaxAgent(GenericQuartoAgent):

    def __init__(self, maxGenerations=2, crossoverRate=0.5, mutationRate=0.1, initialPopulationSize=3, maxPopulationSize=10) -> None:
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
        board, currentPiece, availableNextPieces, availablePositions = quartoGameState
        tempNextPieces = availableNextPieces.copy()
        tempPositions = availablePositions.copy()
        tempBoard = deepcopy(board)
        tempCurrentPiece = currentPiece

        myTurn = True
        newChromosome = list()
        evaluation = 0
        while len(tempPositions) > 0:
            if len(tempNextPieces) == 0:
                tempNextPieces.add(16)

            #generate random move
            randomPos = sample(tempPositions, 1)[0]
            randomPiece = sample(tempNextPieces, 1)[0]
            tempPositions.remove(randomPos)
            tempNextPieces.remove(randomPiece)

            #add random move to new chromosome
            newChromosome.append((randomPos, randomPiece))

            #update temporary board and temporary piece
            row, col = qutil.get2dCoords(randomPos)
            tempBoard[row][col] = tempCurrentPiece
            tempCurrentPiece = randomPiece

            if qutil.isGameOver(tempBoard):
                if myTurn: evaluation = 10
                else: evaluation = -10
                break

            myTurn = not myTurn

        return self.encodeChromosome(newChromosome), evaluation

    #one-point crossover
    def crossover(self, chromosomeA, chromosomeB):
        if len(chromosomeA) <= len(chromosomeB):
            numMoves = len(chromosomeA) // 4
            point = 4 * (numMoves // 2)
            return chromosomeA[:point] + chromosomeB[point:]
        else:
            numMoves = len(chromosomeB) // 4
            point = 4 * (numMoves // 2)
            return chromosomeA[:point] + chromosomeB[point:]
    
    def mutation(self, chromosome):
        pass

    def generateSolution(self, quartoGameState):
        #initialize reservation tree
        self.reservationTree = ReservationTree()
        
        #randomize initial population
        fitness = dict()
        for i in range(self.initialPopulationSize):
            chromosome, leafEvaluation = self.createChromosome(quartoGameState)
            fitness[chromosome] = 0
            self.reservationTree.addPath(chromosome, leafEvaluation)

class ReservationTree():

    def __init__(self) -> None:
        self.rootNode = Node("root", value=-10, move=(16,16))

    def showTree(self):
        self.rootNode.show(attr_list=["value"])

    #updates node values using minmax along a path from leaf to root
    def minmax(self, leaf):

        #determine if MIN or MAX
        maxTurn = (len(leaf.name)/4) % 2 == 0

        #recurrently update node values
        current = leaf
        while current.parent != None:
            current = current.parent
            maxTurn = not maxTurn
            
            if maxTurn:
                current.value = np.max([i.value for i in current.children])
            else:
                current.value = np.min([i.value for i in current.children])
            
    #Given a chromosome, finds the last node in the tree where it exists
    def findChromosomeNode(self, encoding):
        currentRoot = self.rootNode
        lastIndex = 0

        for i in range(4,len(encoding)+1,4):
            stop = True

            for node in currentRoot.children:
                if node.name == encoding[:i]:
                    currentRoot = node
                    lastIndex = i
                    stop = False
                    break
            
            if stop: break
            
        return currentRoot, lastIndex
    
    #adds a new path of nodes from a chromosome encoding
    def addPath(self, encoding, leafEvaluation):
        
        current, lastIndex = self.findChromosomeNode(encoding)
        movePath = [(int(encoding[i]+encoding[i+1]),int(encoding[i+2]+encoding[i+3])) for i in range(lastIndex,len(encoding)-3,4)]

        for m in range(0,len(movePath)):
            if m == len(movePath)-1: #leaf node
                current = Node(encoding[0:lastIndex+4*(m+1)], value=leafEvaluation, parent=current)
                self.minmax(current)
            else:
                current = Node(encoding[0:lastIndex+4*(m+1)], value=-10, parent=current)

          


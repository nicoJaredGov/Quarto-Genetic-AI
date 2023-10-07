from quarto_agents.generic_quarto_agent import GenericQuartoAgent
import quarto_util as qutil
import numpy as np
from bigtree.node.node import Node
from copy import deepcopy
from random import sample

class GeneticMinmaxAgent(GenericQuartoAgent):

    def __init__(self, searchDepth=3, maxGenerations=2, crossoverRate=0.4, mutationRate=0.8, initialPopulationSize=3, maxPopulationSize=10) -> None:
        super().__init__()

        #hyperparameters
        self.searchDepth = searchDepth
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
        (position, nextPiece), eval = self.generateSolution(quartoGameState)
        print(f"Genetic agent placed piece at cell {position} and nextPiece is {nextPiece}")
        print("maxEval: ", eval)
        return position, nextPiece
    
    # Counts how many lines of three pieces with an identical property
    def lineEvaluation(self, board, turn: bool):
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
        
        if turn:
            return numLines
        else:
            return -numLines
    
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
        isGameOver = False
        newChromosome = list()
        evaluation = 0
        for _ in range(self.searchDepth):
            if len(tempPositions) <= 0:
                break
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

            #case when either play wins at a given state
            if qutil.isGameOver(tempBoard):
                isGameOver = True
                if myTurn: evaluation = 10
                else: evaluation = -10
                break

            myTurn = not myTurn

        #case when no player has won
        if not isGameOver:
            evaluation = self.lineEvaluation(tempBoard, not myTurn)

        return self.encodeChromosome(newChromosome), evaluation

    #one-point crossover
    def crossover(self, chromosomeA, chromosomeB):
        if len(chromosomeA) <= len(chromosomeB):
            numMoves = len(chromosomeA) // 4
        else:
            numMoves = len(chromosomeB) // 4

        point = np.random.randint(1,numMoves)
        return chromosomeA[:4*point] + chromosomeB[4*point:]
    
    def mutation(self, chromosome, quartoGameState):
        numMoves = len(chromosome) // 2
        mutationPoint = np.random.randint(numMoves)

        if mutationPoint % 2 == 0: #move position
            mutation = sample(quartoGameState[3], 1)[0] 
        else: #move nextPiece
            mutation = sample(quartoGameState[2], 1)[0]

        move = ""
        if mutation <= 9:
            move += "0"+str(mutation)
        else:
            move += str(mutation)

        mutatedChromosome = chromosome[:2*mutationPoint] + move + chromosome[2*mutationPoint+2:]
        
        return mutatedChromosome
    
    def isValidChromosome(self, chromosome, quartoGameState):
        #check if chromosome is valid
        positions = [int(chromosome[i:i+2]) for i in range(0,len(chromosome),4)] + list(set(range(16)) - quartoGameState[3])
        nextPieces = [int(chromosome[i:i+2]) for i in range(2,len(chromosome),4)] + list(set(range(16)) - quartoGameState[2])
        if len(set(positions)) < len(positions):
            return False
        if len(set(nextPieces)) < len(nextPieces):
            return False
        
        return True
        
    #evaluate chromosome leaf node
    def evaluate(self, chromosome, quartoGameState):
        movePath = [(int(chromosome[i]+chromosome[i+1]),int(chromosome[i+2]+chromosome[i+3])) for i in range(0,len(chromosome)-3,4)]

        tempBoard = deepcopy(quartoGameState[0])
        tempCurrentPiece = quartoGameState[1]
        evaluation = 0

        #update temporary board and temporary piece
        for move in movePath:
            row, col = qutil.get2dCoords(move[0])
            tempBoard[row][col] = tempCurrentPiece
            tempCurrentPiece = move[1]
        
        if qutil.isGameOver(tempBoard):
            if len(movePath) % 2 == 0: evaluation = -10
            else: evaluation = 10
        else:
            evaluation = self.lineEvaluation(tempBoard, len(movePath) % 2 != 0)
    
        return evaluation

    #main Genetic Minimax implementation
    def generateSolution(self, quartoGameState):
        #initialize reservation tree
        self.reservationTree = ReservationTree()
        
        #randomize initial population
        fitness = dict()
        for _ in range(self.initialPopulationSize):
            chromosome, leafEvaluation = self.createChromosome(quartoGameState)
            fitness[chromosome] = 0
            self.reservationTree.addPath(chromosome, leafEvaluation)
        
        #print("initial: ", fitness, len(fitness))
        bestChromosome = ""
        finalEvaluation = -1
        for _ in range(self.maxGenerations):
            #perform crossover and mutation
            parents = fitness.keys()

            for _ in range(self.maxPopulationSize - len(parents)):
                #random parent selection
                a, b = sample(parents, 2)
                
                #random mutation
                if np.random.sample() < self.mutationRate:
                    mutatedChild = self.mutation(a, quartoGameState)

                    if len(mutatedChild) < 4*self.searchDepth:
                        continue

                    if self.isValidChromosome(mutatedChild, quartoGameState):
                        fitness[mutatedChild] = 0
                        leafEvaluation = self.evaluate(mutatedChild, quartoGameState)
                        self.reservationTree.addPath(mutatedChild, leafEvaluation)

                    continue

                if a == b: continue
                
                #crossover
                if np.random.sample() < self.crossoverRate:
                    crossoverChild = self.crossover(a, b)
                    
                    if len(crossoverChild) < 4*self.searchDepth:
                        continue

                    if self.isValidChromosome(crossoverChild, quartoGameState):
                        fitness[crossoverChild] = 0
                        leafEvaluation = self.evaluate(crossoverChild, quartoGameState)
                        self.reservationTree.addPath(crossoverChild, leafEvaluation)

            #update fitness for all chromosomes in this generation
            for c in fitness.keys():
                fitness[c] = self.reservationTree.computeFitness(c)
            
            print(len(fitness))
            #set next generation's initial population as the top N chromosomes of this generation
            tempCounter = 0
            tempFitness = fitness.copy()
            fitness.clear()
            for chromosome, fitnessValue in reversed(sorted(tempFitness.items(),key=lambda x: x[1])):
                fitness[chromosome] = fitnessValue
                tempCounter += 1
                if tempCounter >= self.initialPopulationSize:
                    break

                #get best chromosome
                if tempCounter == 1:
                    bestChromosome = chromosome
                    finalEvaluation = fitnessValue

        #print("new fitness ", fitness)
        #self.reservationTree.showTree()
        bestMove = (int(bestChromosome[0]+bestChromosome[1]),int(bestChromosome[2]+bestChromosome[3]))
        return bestMove, finalEvaluation

class ReservationTree():

    def __init__(self) -> None:
        self.rootNode = Node("root", value=-10)
        self.leafNodes = dict()

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
                self.leafNodes[encoding] = current
            else:
                current = Node(encoding[0:lastIndex+4*(m+1)], value=-10, parent=current)

    def computeFitness(self, encoding):
        currNode = self.leafNodes[encoding]
        leafValue = currNode.value # type: ignore

        while currNode is not None:
            if currNode.parent.value == leafValue: # type: ignore
                currNode = currNode.parent
                if currNode == self.rootNode: 
                    break
            else:
                break
            
        return self.rootNode.max_depth - currNode.depth + 1 # type: ignore


          


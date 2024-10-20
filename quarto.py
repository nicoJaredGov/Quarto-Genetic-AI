import numpy as np
import quarto_util as qutil
import quarto_agents.generic_quarto_agent as qagents
from datetime import datetime
import time


class QuartoGame:
    def __init__(
        self,
        agent1: qagents.GenericQuartoAgent,
        agent2: qagents.GenericQuartoAgent,
        player1Name="Player 1",
        player2Name="Player 2",
        gui_mode=False,
        bin_mode=False,
        log_stats=False,
        numRetriesAllowed=3,
    ):

        # additional configuration
        self.checkAgentsValid(agent1, agent2)
        self.player1 = agent1
        self.player2 = agent2
        self.setPlayerNames(player1Name, player2Name)
        self.gui_mode = gui_mode  # show graphical view of board
        self.bin_mode = bin_mode  # if terminal view is shown, replace integer piece representation with binary representation
        self.log_stats = log_stats
        self.numRetriesAllowed = numRetriesAllowed

        # game state
        self.moveHistory = list()
        self.resetGame()
        if log_stats:
            self.resetStats()

    def checkAgentsValid(self, agent1, agent2):
        assert agent1 is not None and issubclass(
            type(agent1), qagents.GenericQuartoAgent
        ), "Agent 1 is not initialized correctly."
        assert agent2 is not None and issubclass(
            type(agent1), qagents.GenericQuartoAgent
        ), "Agent 2 is not initialized correctly."

    def resetGame(self):
        self.board = np.full((4, 4), 16)
        self.currentPiece = 16  # set to nothing upon starting
        self.availablePieces = set(range(16))
        self.availablePositions = set(range(16))
        self.moveHistory.clear()

    def resetStats(self):
        self.agent1_cumulative_time = 0
        self.agent2_cumulative_time = 0
        self.numMoves1 = 0
        self.numMoves2 = 0

    def encodeBoard(self):
        return qutil.encodeBoard(self.board, self.currentPiece)

    def setPlayerNames(self, name1, name2):
        self.player1Name = self.player1.name if self.player1.name is not None else name1
        self.player2Name = self.player2.name if self.player2.name is not None else name2

    def __showPlayerName(self, isPlayerOneTurn):
        if isPlayerOneTurn:
            print(f"\n ------{self.player1Name}'s Turn---------\n")
        else:
            print(f"\n ------{self.player2Name}'s Turn---------\n")

    def __getPieceToShow(self, i, j):
        piece = str(self.board[i][j])
        if self.bin_mode:
            if piece == "16":
                piece = f"({qutil.getLinearCoords(i,j)})"
            else:
                piece = f"{self.board[i][j]:04b}"
        else:
            if piece == "16":
                piece = "  "

        return piece

    def showBoard(self):
        border = ".______.______.______.______." if self.bin_mode else ".____.____.____.____."
        for i in range(4):
            print(border)
            line = ""
            for j in range(4):
                piece = self.__getPieceToShow(i, j)

                if len(piece) == 2 or len(piece) == 4:
                    if j == 3:
                        line += "| " + piece + " |"
                    else:
                        line += "| " + piece + " "
                else:
                    if j == 3:
                        line += "| " + piece + "  |"
                    else:
                        line += "| " + piece + "  "
            print(line)
        print(border + "\n")

    def showGameInformation(self):
        print(
            "current piece to place: ",
            self.currentPiece,
            "\navailable pieces: ",
            self.availablePieces,
            "\navailable positions: ",
            self.availablePositions,
            "\nmove history: ",
            self.moveHistory,
            "\n",
        )

    def showGameState(self):
        self.showBoard()
        self.showGameInformation()

    def getGameState(self):
        return (
            self.encodeBoard(),
            self.availablePieces.copy(),
            self.availablePositions.copy(),
        )

    def makeFirstMove(self, nextPiece):
        self.currentPiece = nextPiece
        self.availablePieces.remove(self.currentPiece)
        self.moveHistory.append((None, nextPiece))
        if self.gui_mode:
            print("First move successful")

    def isValidMove(self, position, nextPiece):
        if position not in range(16):
            print("This position does not exist\n")
            return False
        if nextPiece not in range(16):
            print("This piece does not exist\n")
            return False
        if position not in self.availablePositions:
            print("This cell is unavailable\n")
            return False
        if nextPiece not in self.availablePieces:
            print("This piece has already been placed or will be placed now\n")
            return False
        return True

    def __makeMove(self, position, nextPiece):
        self.moveHistory.append((position, nextPiece))
        row, col = qutil.get2dCoords(position)
        self.board[row][col] = self.currentPiece
        self.availablePositions.remove(position)

        self.currentPiece = nextPiece
        self.availablePieces.remove(self.currentPiece)

        if self.gui_mode:
            print("Move successful")

    def makeLastMove(self):
        lastPosition = self.availablePositions.pop()
        row, col = qutil.get2dCoords(lastPosition)
        self.board[row][col] = self.currentPiece
        self.moveHistory.append((lastPosition, None))

        if self.gui_mode:
            print("Last move successful")

    def __logMoveTime(self, isPlayerOneTurn, startTime, endTime):
        if isPlayerOneTurn:
            self.agent1_cumulative_time += endTime - startTime
            self.numMoves1 += 1
        else:
            self.agent2_cumulative_time += endTime - startTime
            self.numMoves2 += 1

    def tryMakeMove(self, isPlayerOneTurn):
        for i in range(self.numRetriesAllowed):
            position, nextPiece = None, None

            startTime = time.time()
            if isPlayerOneTurn:
                position, nextPiece = self.player1.makeMove(self.getGameState(), self.gui_mode)
            else:
                position, nextPiece = self.player2.makeMove(self.getGameState(), self.gui_mode)
            endTime = time.time()

            if self.isValidMove(position, nextPiece):
                self.__makeMove(position, nextPiece)
                if self.log_stats:
                    self.__logMoveTime(isPlayerOneTurn, startTime, endTime)
                    self.detailedLogFile.write(
                        f"{position},{nextPiece},{round(endTime - startTime,4)}\n"
                    )
                return True
            elif i == self.numRetriesAllowed - 1:
                print(f"{self.numRetriesAllowed} invalid moves made - game ended")
                return False

    def isGameOver(self, isPlayerOneTurn):
        identifier = 1 if isPlayerOneTurn else 2
        playerName = self.player1Name if isPlayerOneTurn else self.player2Name

        if qutil.isGameOver(self.board):
            if self.log_stats:
                self.detailedLogFile.write(f"{identifier}\n")
            print(f"\nPlayer {identifier} ({playerName}) won!")
            return True

    def pickRandomAvailablePiece(self):
        return int(np.random.choice(list(self.availablePieces)))

    def play(self, randomizeFirstMove=True):
        isPlayerOneTurn = True
        if self.gui_mode:
            self.__showPlayerName(isPlayerOneTurn)

        # first move
        if randomizeFirstMove:
            self.makeFirstMove(self.pickRandomAvailablePiece())
        else:
            first_move = self.player1.makeFirstMove(self.getGameState(), self.gui_mode)
            self.makeFirstMove(first_move)
        isPlayerOneTurn = False
        if self.gui_mode:
            self.showGameState()

        # subsequent moves
        for _ in range(len(self.availablePositions) - 1):
            if self.gui_mode:
                self.__showPlayerName(isPlayerOneTurn)
            if not self.tryMakeMove(isPlayerOneTurn):
                return -1 if isPlayerOneTurn else -2
            if self.gui_mode:
                self.showGameState()

            if self.isGameOver(isPlayerOneTurn):
                return 1 if isPlayerOneTurn else 2

            isPlayerOneTurn = not isPlayerOneTurn

        # Place last piece and set nextPiece to nothing
        if self.gui_mode:
            self.__showPlayerName(isPlayerOneTurn)
        self.makeLastMove()

        if self.gui_mode:
            self.showGameState()

        if self.isGameOver(isPlayerOneTurn):
            return 1 if isPlayerOneTurn else 2
        else:
            print("\nDraw!")
            return 0

    def __playWithLogs(self, randomizeFirstMove=True):
        isPlayerOneTurn = True
        if self.gui_mode:
            self.__showPlayerName(isPlayerOneTurn)

        # first move
        if randomizeFirstMove:
            self.makeFirstMove(self.pickRandomAvailablePiece())
        else:
            first_move = self.player1.makeFirstMove(self.getGameState(), self.gui_mode)
            self.makeFirstMove(first_move)
        isPlayerOneTurn = False
        self.detailedLogFile.write(str(self.moveHistory[-1]) + "\n")
        if self.gui_mode:
            self.showGameState()

        # subsequent moves
        for _ in range(len(self.availablePositions) - 1):
            if self.gui_mode:
                self.__showPlayerName(isPlayerOneTurn)
            self.detailedLogFile.write(self.encodeBoard() + ",")

            if not self.tryMakeMove(isPlayerOneTurn):
                if isPlayerOneTurn:
                    self.detailedLogFile.write("-1\n")
                    return -1
                else:
                    self.detailedLogFile.write("-2\n")
                    return -2

            if self.gui_mode:
                self.showGameState()

            if self.isGameOver(isPlayerOneTurn):
                return 1 if isPlayerOneTurn else 2

            isPlayerOneTurn = not isPlayerOneTurn

        # Place last piece and set nextPiece to nothing
        if self.gui_mode:
            self.__showPlayerName(isPlayerOneTurn)
        self.detailedLogFile.write(
            f"{self.encodeBoard()},{list(self.availablePositions)[0]},None,None\n"
        )
        self.makeLastMove()

        if self.gui_mode:
            self.showGameState()
        self.detailedLogFile.write(self.encodeBoard() + "\n")

        if self.isGameOver(isPlayerOneTurn):
            return 1 if isPlayerOneTurn else 2
        else:
            self.detailedLogFile.write("0\n")
            print("\nDraw!")
            return 0

    def playMultipleGames(self, numTimes):
        self.log_stats = True
        self.resetStats()

        player1wins = 0
        player2wins = 0
        draws = 0

        today = datetime.now()
        curr_datetime = f"{today.date()} {today.hour}_{today.minute}_{today.second} {self.player1Name}_{self.player2Name}"
        logFile = open("experiment_results/runs/" + curr_datetime + ".txt", mode="a")
        logFile.write(f"{self.player1Name},{self.player2Name},{numTimes}\n")
        logFile.write(
            "result,player1cumulativeTime,player2cumulativeTime,player1numMoves,player2numMoves\n"
        )

        self.detailedLogFile = open("experiment_results/logs/" + curr_datetime + ".txt", mode="a")
        self.detailedLogFile.write(f"{self.player1Name},{self.player2Name},{numTimes}\n")

        for _ in range(numTimes):
            result = self.__playWithLogs()

            if result == 1:
                player1wins += 1
            elif result == 2:
                player2wins += 1
            elif result == 0:
                draws += 1
            else:
                print("Invalid move return. Table not updated.")

            logFile.write(
                f"{result},{round(self.agent1_cumulative_time,4)},{round(self.agent2_cumulative_time,4)},{self.numMoves1},{self.numMoves2}\n"
            )
            self.resetGame()
            self.resetStats()

        logFile.close()
        self.detailedLogFile.close()

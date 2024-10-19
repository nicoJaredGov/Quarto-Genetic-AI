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
    ):

        # additional configuration
        self.checkAgentsValid(agent1, agent2)
        self.player1 = agent1
        self.player2 = agent2
        self.setPlayerNames(player1Name, player2Name)
        self.gui_mode = gui_mode  # show graphical view of board
        self.bin_mode = bin_mode  # if terminal view is shown, replace integer piece representation with binary representation

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

    def showPlayerName(self, turn):
        # turn
        # True = player 1
        # False = player 2
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
                            line += "| " + piece + " |"
                        else:
                            line += "| " + piece + " "
                    else:
                        if j == 3:
                            line += "| " + piece + "  |"
                        else:
                            line += "| " + piece + "  "
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
                            line += "|  " + piece + " |"
                        else:
                            line += "|  " + piece + " "
                    else:
                        if j == 3:
                            line += "|  " + piece + "  |"
                        else:
                            line += "|  " + piece + "  "
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
            self.encodeBoard(),
            self.availablePieces.copy(),
            self.availablePositions.copy(),
        )

    # This method is ONLY for the first move of the game (the first player's first move)
    def makeFirstMove(self, nextPiece):
        self.currentPiece = nextPiece
        self.availablePieces.remove(self.currentPiece)
        self.moveHistory.append((None, nextPiece))
        if self.gui_mode:
            print("First move successful")

    # This method is for every move after than the first one
    def makeMove(self, position, nextPiece):
        # validation checks
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

        # add to move history
        self.moveHistory.append((position, nextPiece))

        # place piece on board and update game state
        row, col = qutil.get2dCoords(position)
        self.board[row][col] = self.currentPiece
        self.availablePositions.remove(position)

        # set next player's piece
        self.currentPiece = nextPiece
        self.availablePieces.remove(self.currentPiece)

        if self.gui_mode:
            print("Move successful")
        return True

    # This method is for automatically placing the last piece in the last position
    def makeLastMove(self):
        # get last available position and place final piece there
        lastPosition = self.availablePositions.pop()
        row, col = qutil.get2dCoords(lastPosition)
        self.board[row][col] = self.currentPiece
        self.moveHistory.append((lastPosition, None))
        if self.gui_mode:
            print("Last move successful")

    # Pick random piece from available pieces
    def pickRandomPiece(self):
        return np.random.choice(list(self.availablePieces))

    def play(self):
        turn = True  # player 1 - True, player 2 - False
        if self.gui_mode:
            self.showPlayerName(turn)

        # first move
        first_move = self.player1.makeFirstMove(self.getGameState(), self.gui_mode)
        self.makeFirstMove(first_move)
        turn = False

        if self.gui_mode:
            self.showGameState()

        # subsequent moves
        for i in range(len(self.availablePositions) - 1):
            if self.gui_mode:
                self.showPlayerName(turn)

            # player 1
            if turn:
                for i in range(3):
                    position, nextPiece = self.player1.makeMove(
                        self.getGameState(), self.gui_mode
                    )
                    validMove = self.makeMove(position, nextPiece)
                    if validMove:
                        break
                    elif i == 2:
                        print("Three invalid moves made - game ended")
                        return -1  # player 1 made three invalid moves
            # player 2
            else:
                for i in range(3):
                    position, nextPiece = self.player2.makeMove(
                        self.getGameState(), self.gui_mode
                    )
                    validMove = self.makeMove(position, nextPiece)
                    if validMove:
                        break
                    elif i == 2:
                        print("Three invalid moves made - game ended")
                        return -2  # player 2 made three invalid moves

            if self.gui_mode:
                self.showGameState()

            if qutil.isGameOver(self.board):
                if turn:
                    print(f"\nPlayer 1 ({self.player1Name}) won!")
                    return 1  # player 1 has won
                else:
                    print(f"\nPlayer 2 ({self.player2Name}) won!")
                    return 2  # player 2 has won

            turn = not turn

        # Place last piece and set nextPiece to nothing
        if self.gui_mode:
            self.showPlayerName(turn)
        self.makeLastMove()

        if self.gui_mode:
            self.showGameState()

        if qutil.isGameOver(self.board):
            if turn:
                print(f"\nPlayer 1 ({self.player1Name}) won!")
                return 1
            else:
                print(f"\nPlayer 2 ({self.player2Name}) won!")
                return 2
            return
        else:
            print("\nDraw!")
            return 0

    def playRandomFirst(self):
        turn = True  # player 1 - True, player 2 - False
        if self.gui_mode:
            self.showPlayerName(turn)

        # player 1's choice of next piece is randomly chosen
        self.makeFirstMove(self.pickRandomPiece())
        turn = False

        if self.gui_mode:
            self.showGameState()

        # subsequent moves
        for _ in range(len(self.availablePositions) - 1):
            if self.gui_mode:
                self.showPlayerName(turn)
            start_time, end_time = 0, 0

            # player 1
            if turn:
                for j in range(3):
                    start_time = time.time()
                    position, nextPiece = self.player1.makeMove(
                        self.getGameState(), self.gui_mode
                    )
                    end_time = time.time()
                    validMove = self.makeMove(position, nextPiece)
                    if validMove:
                        break
                    elif j == 2:
                        print("Three invalid moves made - game ended")
                        return -1  # player 1 made three invalid moves
                self.agent1_cumulative_time += end_time - start_time
                self.numMoves1 += 1

            # player 2
            else:
                for j in range(3):
                    start_time = time.time()
                    position, nextPiece = self.player2.makeMove(
                        self.getGameState(), self.gui_mode
                    )
                    end_time = time.time()
                    validMove = self.makeMove(position, nextPiece)
                    if validMove:
                        break
                    elif j == 2:
                        print("Three invalid moves made - game ended")
                        return -2  # player 2 made three invalid moves
                self.agent2_cumulative_time += end_time - start_time
                self.numMoves2 += 1

            if self.gui_mode:
                self.showGameState()

            if qutil.isGameOver(self.board):
                if turn:
                    print(f"\nPlayer 1 ({self.player1Name}) won!")
                    return 1  # player 1 has won
                else:
                    print(f"\nPlayer 2 ({self.player2Name}) won!")
                    return 2  # player 2 has won

            turn = not turn

        # Place last piece and set nextPiece to nothing
        if self.gui_mode:
            self.showPlayerName(turn)
        self.makeLastMove()

        if self.gui_mode:
            self.showGameState()

        if qutil.isGameOver(self.board):
            if turn:
                print(f"\nPlayer 1 ({self.player1Name}) won!")
                return 1
            else:
                print(f"\nPlayer 2 ({self.player2Name}) won!")
                return 2
        else:
            print("\nDraw!")
            return 0

    def __playLogged(self):
        turn = True  # player 1 - True, player 2 - False
        if self.gui_mode:
            self.showPlayerName(turn)

        # player 1's choice of next piece is randomly chosen
        self.makeFirstMove(self.pickRandomPiece())
        turn = False
        self.detailedLogFile.write(str(self.moveHistory[-1]) + "\n")

        if self.gui_mode:
            self.showGameState()

        # subsequent moves
        for _ in range(len(self.availablePositions) - 1):
            if self.gui_mode:
                self.showPlayerName(turn)
            self.detailedLogFile.write(self.encodeBoard() + ",")
            position, nextPiece = (16, 16)
            start_time, end_time = 0, 0

            # player 1
            if turn:
                for j in range(3):
                    start_time = time.time()
                    position, nextPiece = self.player1.makeMove(
                        self.getGameState(), self.gui_mode
                    )
                    end_time = time.time()
                    validMove = self.makeMove(position, nextPiece)
                    if validMove:
                        break
                    elif j == 2:
                        self.detailedLogFile.write("-1\n")
                        print("Three invalid moves made - game ended")
                        return -1  # player 1 made three invalid moves
                self.agent1_cumulative_time += end_time - start_time
                self.numMoves1 += 1

            # player 2
            else:
                for j in range(3):
                    start_time = time.time()
                    position, nextPiece = self.player2.makeMove(
                        self.getGameState(), self.gui_mode
                    )
                    end_time = time.time()
                    validMove = self.makeMove(position, nextPiece)
                    if validMove:
                        break
                    elif j == 2:
                        self.detailedLogFile.write("-2\n")
                        print("Three invalid moves made - game ended")
                        return -2  # player 2 made three invalid moves
                self.agent2_cumulative_time += end_time - start_time
                self.numMoves2 += 1

            if self.gui_mode:
                self.showGameState()
            self.detailedLogFile.write(
                f"{position},{nextPiece},{round(end_time - start_time,4)}\n"
            )

            if qutil.isGameOver(self.board):
                self.detailedLogFile.write(self.encodeBoard() + "\n")
                if turn:
                    self.detailedLogFile.write("1\n")
                    print(f"\nPlayer 1 ({self.player1Name}) won!")
                    return 1  # player 1 has won
                else:
                    self.detailedLogFile.write("2\n")
                    print(f"\nPlayer 2 ({self.player2Name}) won!")
                    return 2  # player 2 has won

            turn = not turn

        # Place last piece and set nextPiece to nothing
        if self.gui_mode:
            self.showPlayerName(turn)
        self.detailedLogFile.write(
            f"{self.encodeBoard()},{list(self.availablePositions)[0]},None,None\n"
        )
        self.makeLastMove()

        if self.gui_mode:
            self.showGameState()
        self.detailedLogFile.write(self.encodeBoard() + "\n")

        if qutil.isGameOver(self.board):
            if turn:
                self.detailedLogFile.write("1\n")
                print(f"\nPlayer 1 ({self.player1Name}) won!")
                return 1
            else:
                self.detailedLogFile.write("2\n")
                print(f"\nPlayer 2 ({self.player2Name}) won!")
                return 2
        else:
            self.detailedLogFile.write("0\n")
            print("\nDraw!")
            return 0

    def runMultiple(self, num_times):
        player1wins = 0
        player2wins = 0
        draws = 0

        # create a new log file for these runs
        today = datetime.now()
        curr_datetime = f"{today.date()} {today.hour}_{today.minute}_{today.second} {self.player1Name}_{self.player2Name}"
        logFile = open("experiment_results/runs/" + curr_datetime + ".txt", mode="a")
        logFile.write(f"{self.player1Name},{self.player2Name},{num_times}\n")
        logFile.write(
            f"result,player1cumulativeTime,player2cumulativeTime,player1numMoves,player2numMoves\n"
        )

        # create a detailed log file for the runs
        self.detailedLogFile = open(
            "experiment_results/logs/" + curr_datetime + ".txt", mode="a"
        )
        self.detailedLogFile.write(
            f"{self.player1Name},{self.player2Name},{num_times}\n"
        )

        for _ in range(num_times):
            result = self.__playLogged()

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

        logFile.close()
        self.detailedLogFile.close()

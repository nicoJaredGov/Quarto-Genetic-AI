from quarto import *
import quarto_agents as qagents
import quarto_util as qutil
import pandas as pd

#Given two agents, make them play against each other for a specified number of games
def runMultiple(agent1: qagents.GenericQuartoAgent, agent2: qagents.GenericQuartoAgent, agent1Name, agent2Name, num_times=1):
    game = QuartoGame(agent1, agent2, gui_mode=False, player1Name=agent1Name, player2Name=agent2Name, bin_mode=False)

    for i in range(num_times):
        result = game.playRandomFirst()
        print(result)
        game.resetGame()


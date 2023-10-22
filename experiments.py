from quarto import *
import quarto_agents as qagents
import quarto_util as qutil
import pandas as pd
from datetime import datetime
import time

#Given two agents, make them play against each other for a specified number of games
def runMultiple(tableName: str, agent1: qagents.GenericQuartoAgent, agent2: qagents.GenericQuartoAgent, agent1Name, agent2Name, num_times=1):
    game = QuartoGame(agent1, agent2, gui_mode=False, player1Name=agent1Name, player2Name=agent2Name, bin_mode=False)

    player1wins = 0
    player2wins = 0
    draws = 0

    #create a new log file for these runs
    today = datetime.now()
    curr_datetime = f"{today.date()} {today.hour}_{today.minute}_{today.second}"
    logFile = open("experiment_results/runs/" + curr_datetime + ".txt", mode="a")
    logFile.write(agent1Name+","+agent2Name+"\n")

    for i in range(num_times):
        start_time = time.time()
        result = game.playRandomFirst()
        end_time = time.time()

        if result == 1:
            player1wins += 1
        elif result == 2:
            player2wins += 1
        elif result == 0:
            draws +=1
        else:
            print("Invalid move return. Table not updated.")    
        
        logFile.write(f"{result},{round(end_time-start_time,4)}\n")
        game.resetGame()
    

    #update the stats table after all runs
    updateAgentStats(tableName, agent1Name, (player1wins,player2wins,draws))
    updateAgentStats(tableName, agent2Name, (player2wins,player1wins,draws))
    logFile.write(f"{player1wins},{player2wins},{draws}")
    logFile.close()

#Used to create a pandas dataframe to store results for agents - linked to the name of an agent
def createAgentTable(tableName: str):
    df = pd.DataFrame(columns=['agentName', 'wins', 'losses', 'draws'])

    # Set data types for each column
    df['agentName'] = df['agentName'].astype('str')
    df['wins'] = df['wins'].astype('int8')
    df['losses'] = df['losses'].astype('int8')
    df['draws'] = df['draws'].astype('int8')     

    df.to_pickle(f'experiment_results/{tableName}.pkl')

#Update an agent's stats after a game has been played - updatedRecord is in the form of a triplet (win, loss, draw) where 1 denotes the update for that and zero everywhere else
def updateAgentStats(tableName: str, agentName: str, updatedRecord):
    df = pd.read_pickle(f'experiment_results/{tableName}.pkl')
    if agentName in df.agentName.values:
        df.loc[df['agentName'] == agentName, ['wins', 'losses', 'draws']] += updatedRecord
    else:
        record = {
            'agentName': agentName,
            'wins': updatedRecord[0],
            'losses': updatedRecord[1],
            'draws': updatedRecord[2]
        }
        df = df.append(record, ignore_index=True)    

    df['agentName'] = df['agentName'].astype('str')
    df['wins'] = df['wins'].astype('int8')
    df['losses'] = df['losses'].astype('int8')
    df['draws'] = df['draws'].astype('int8')  

    df.to_pickle(f'experiment_results/{tableName}.pkl')

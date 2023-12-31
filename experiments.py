from quarto import *
import quarto_agents as qagents
import multiprocessing as mp
import os
import pandas as pd

#listens for messages on the q, writes to file.
def mpListener(filename, q):
    with open(filename, 'w') as f:
        while 1:
            m = q.get()
            if m == 'kill':
                break
            f.write(str(m) + '\n')
            f.flush()

def batchRunInstance(num_times, agent1, agent2, q):
    game = QuartoGame(agent1, agent2, gui_mode=False, bin_mode=False)

    for _ in range(num_times):
        result = game.playRandomFirst()
        q.put(f"{result},{round(game.agent1_cumulative_time,4)},{round(game.agent2_cumulative_time,4)},{game.numMoves1},{game.numMoves2}")
        game.resetGame()

#multiprocessing batch running of games between two agents
def mpBatchRun(agent1: qagents.GenericQuartoAgent, agent2: qagents.GenericQuartoAgent, gamesPerCPU: int, cpu_count: int):
    assert cpu_count <= mp.cpu_count(), f"Higher than available cpu_count {mp.cpu_count()}"

    #create a new log file for these runs
    today = datetime.now()
    filename = f"experiment_results/final/{today.date()} {today.hour}_{today.minute}_{today.second} {agent1.name}_{agent2.name}.txt"

    #must use Manager queue here, or will not work
    manager = mp.Manager()
    q = manager.Queue()    
    pool = mp.Pool(cpu_count+1)

    q.put(f"{agent1.name},{agent2.name},{gamesPerCPU*cpu_count}")
    q.put(f"result,player1cumulativeTime,player2cumulativeTime,player1numMoves,player2numMoves")

    #put listener to work first
    watcher = pool.apply_async(mpListener, (filename, q))

    #fire off workers
    jobs = []
    for i in range(cpu_count):
        job = pool.apply_async(batchRunInstance, (gamesPerCPU, agent1, agent2, q))
        jobs.append(job)

    # collect results from the workers through the pool result queue
    for job in jobs: 
        job.get()

    #now we are done, kill the listener
    q.put('kill')
    pool.close()
    pool.join()

def negamax_tests():
    #search window and depth values
    negamax_search = [16]
    negamax_depths = [5]

    #experiment control agent
    geneticminmax = qagents.GeneticMinmaxAgent(searchDepth=3, maxGenerations=2, initialPopulationSize=5000, maxPopulationSize=6000)
    geneticminmax.setName("ControlGenetic-3")

    for s in negamax_search:
        for d in negamax_depths:
            negamax_agent = qagents.NegamaxAgent(depth=d, searchWindow=s)

            start_time = time.time()
            #half the runs as player 1
            mpBatchRun(negamax_agent, geneticminmax, 12, 4)
            end_time = time.time()
            print("Batch run time: ", round(end_time - start_time,4))

            #half the runs as player 2
            mpBatchRun(geneticminmax, negamax_agent, 12, 4)

def genetic_tests():
    #hyperparameters
    genetic_depths = [2]
    genetic_gens = [1,2,3,5,10]
    initial_population, max_population = 4000, 7000

    #experiment control agent
    negamax_agent = qagents.NegamaxAgent(depth=3, searchWindow=16)
    negamax_agent.setName("ControlNegamax-3")

    for g in genetic_gens:
        for d in genetic_depths:
            geneticminmax = qagents.GeneticMinmaxAgent(searchDepth=d, maxGenerations=g, initialPopulationSize=initial_population, maxPopulationSize=max_population)

            start_time = time.time()
            #half the runs as player 1
            mpBatchRun(geneticminmax, negamax_agent, 13, 4)
            end_time = time.time()
            print("Batch run time: ", round(end_time - start_time,4))

            #half the runs as player 2
            mpBatchRun(negamax_agent, geneticminmax, 13, 4)

def vs_tests():
    #history neg - (3,16), (3,32)
    #history gen - (2,2,4000,7000), (2,10,4000,7000)

    #hyperparameters
    negamax_params = [(3,32)]
    genetic_params = [(3,2,8000,12000)]

    for p in range(len(negamax_params)):
        negamax_param = negamax_params[p]
        negamax_agent = qagents.NegamaxAgent(depth=negamax_param[0], searchWindow=negamax_param[1])

        genetic_param = genetic_params[p]
        d, g, initial_population, max_population = genetic_param
        geneticminmax = qagents.GeneticMinmaxAgent(searchDepth=d, maxGenerations=g, initialPopulationSize=initial_population, maxPopulationSize=max_population)

        start_time = time.time()
        #half the runs as player 1
        mpBatchRun(geneticminmax, negamax_agent, 5, 4)
        end_time = time.time()
        print("Batch run time: ", round(end_time - start_time,4))

        #half the runs as player 2
        mpBatchRun(negamax_agent, geneticminmax, 5, 4)

#Opens up all files in the directory and summarizes data in graphs and tables
def create_table(path_to_dir: str):
    #create agent stats table
    today = datetime.now()
    table_path = f"experiment_results/agent_stats/{today.date()} {today.hour}_{today.minute}_{today.second}"
    qutil.createAgentStatsTable(table_path)

    #load data for each file into the table
    for filename in os.listdir(path_to_dir):
        agents, df = qutil.readRunFile(path_to_dir+"/"+filename)
        print(agents)

        #summarize result data
        resultCounts = df.result.value_counts()
        if 0 in resultCounts: totalDraws = resultCounts[0]
        else: totalDraws = 0
        if 1 in resultCounts: player1Wins = resultCounts[1]
        else: player1Wins = 0
        if 2 in resultCounts: player2Wins = resultCounts[2]
        else: player2Wins = 0

        #aggregrate time data
        df['player1avgTime'] = df['player1cumulativeTime'] / df['player1numMoves']
        df['player2avgTime'] = df['player2cumulativeTime'] / df['player2numMoves']

        #['wins', 'losses', 'draws', 'cumulativeGameTime', 'cumulativeAvgMoveTime', 'numGamesPlayed']
        agent1Update = [
            player1Wins,
            player2Wins,
            totalDraws,
            df['player1cumulativeTime'].sum(),
            df['player1avgTime'].sum(),
            df.shape[0]
        ]

        agent2Update = [
            player2Wins,
            player1Wins,
            totalDraws,
            df['player2cumulativeTime'].sum(),
            df['player2avgTime'].sum(),
            df.shape[0]
        ]
        qutil.updateAgentStats(table_path, agents[0], agent1Update)
        qutil.updateAgentStats(table_path, agents[1], agent2Update)

    #aggregate table data
    agent_stats = pd.read_pickle(f'{table_path}.pkl')
    agent_stats['winRate'] = agent_stats['wins'] / agent_stats['numGamesPlayed']
    agent_stats['lossRate'] = agent_stats['losses'] / agent_stats['numGamesPlayed']
    agent_stats['avgGameTime'] = agent_stats['cumulativeGameTime'] / agent_stats['numGamesPlayed']
    agent_stats['avgMoveTime'] = agent_stats['cumulativeAvgMoveTime'] / agent_stats['numGamesPlayed']
    agent_stats.to_pickle(f'{table_path}.pkl')

def main():
    #RUN YOUR TESTS HERE
    geneticminmax = qagents.GeneticMinmaxAgent(searchDepth=3, maxGenerations=3, initialPopulationSize=10000, maxPopulationSize=12000)
    # negamax= qagents.NegamaxAgent(depth=3, searchWindow=32)
    #game = QuartoGame(negamax, geneticminmax, gui_mode=True, bin_mode=False)
    game = QuartoGame(qagents.NegamaxAgent(depth=3, searchWindow=32), geneticminmax, gui_mode=True, bin_mode=False)
    game.playRandomFirst()
    
    #negamax_tests()
    #genetic_tests()
    #vs_tests()
    #create_table('experiment_results/final/')
    pass
          
if __name__ == "__main__":
    main()
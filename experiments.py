from quarto import *
import quarto_agents as qagents
import multiprocessing as mp

def mpListener(filename, q):
    '''listens for messages on the q, writes to file. '''

    with open(filename, 'a') as f:
        while 1:
            m = q.get()
            if m == 'kill':
                break
            f.write(str(m) + '\n')
            f.flush()

def batchRunInstance(num_times, agent1, agent2, q):
    player1wins = 0
    player2wins = 0
    draws = 0
    game = QuartoGame(agent1, agent2, gui_mode=False, bin_mode=False)

    for _ in range(num_times):
        game.agent1_cumulative_time = 0
        game.agent2_cumulative_time = 0
        game.numMoves1 = 0
        game.numMoves2 = 0
        result = game.playRandomFirst()

        if result == 1:
            player1wins += 1
        elif result == 2:
            player2wins += 1
        elif result == 0:
            draws +=1
        else:
            print("Invalid move return. Table not updated.")    
        
        q.put(f"{result},{round(game.agent1_cumulative_time,4)},{round(game.agent2_cumulative_time,4)},{game.numMoves1},{game.numMoves2}\n")
        game.resetGame()

#multiprocessing batch running of games between two agents
def mpBatchRun(agent1: qagents.GenericQuartoAgent, agent2: qagents.GenericQuartoAgent, gamesPerCPU: int):
    cpu_count = mp.cpu_count()

    #create a new log file for these runs
    today = datetime.now()
    filename = f"experiment_results/runs/{today.date()} {today.hour}_{today.minute}_{today.second} {agent1.name}_{agent2.name}.txt"
    logFile = open(filename, mode="a")
    logFile.write(f"{agent1.name},{agent2.name},{gamesPerCPU*cpu_count}\n")
    logFile.write(f"result,player1cumulativeTime,player2cumulativeTime,player1numMoves,player2numMoves\n")

    #must use Manager queue here, or will not work
    manager = mp.Manager()
    q = manager.Queue()    
    pool = mp.Pool(cpu_count)

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
    logFile.close()

def main():
    'negamax tests'
    num_runs = 100

    #search window and depth values
    negamax_search = [16]
    negamax_depths = [4]

    #experiment control agent
    geneticminmax = qagents.GeneticMinmaxAgent(searchDepth=3, maxGenerations=3, initialPopulationSize=4000, maxPopulationSize=5000)

    for s in negamax_search:
        for d in negamax_depths:
            negamax_agent = qagents.NegamaxAgent(depth=d, searchWindow=s)

            #half the runs as player 1
            mpBatchRun(negamax_agent, geneticminmax, 3)

            #half the runs as player 2
            mpBatchRun(geneticminmax, negamax_agent, 3)
            
if __name__ == "__main__":
    main()


# geneticminmax = qagents.GeneticMinmaxAgentTest(searchDepth=3, maxGenerations=3, initialPopulationSize=4000, maxPopulationSize=5000)
# negamax= qagents.NegamaxAgent(depth=3, searchWindow=32)
# game = QuartoGame(negamax, geneticminmax, gui_mode=True, bin_mode=False)
# game.playRandomFirst()
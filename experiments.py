from quarto import *
import quarto_agents as qagents
import multiprocessing as mp

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
    filename = f"experiment_results/runs/{today.date()} {today.hour}_{today.minute}_{today.second} {agent1.name}_{agent2.name}.txt"

    #must use Manager queue here, or will not work
    manager = mp.Manager()
    q = manager.Queue()    
    pool = mp.Pool(cpu_count)

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

def main():
    'negamax tests'
    num_runs = 100

    #search window and depth values
    negamax_search = [16]
    negamax_depths = [2, 3]

    #experiment control agent
    geneticminmax = qagents.GeneticMinmaxAgent(searchDepth=3, maxGenerations=3, initialPopulationSize=4000, maxPopulationSize=5000)

    for s in negamax_search:
        for d in negamax_depths:
            negamax_agent = qagents.NegamaxAgent(depth=d, searchWindow=s)

            start_time = time.time()
            #half the runs as player 1
            mpBatchRun(negamax_agent, geneticminmax, 3, 16)
            end_time = time.time()
            print("Batch run time: ", round(end_time - start_time,4))

            #half the runs as player 2
            mpBatchRun(geneticminmax, negamax_agent, 3, 16)
            
if __name__ == "__main__":
    main()


# geneticminmax = qagents.GeneticMinmaxAgentTest(searchDepth=3, maxGenerations=3, initialPopulationSize=4000, maxPopulationSize=5000)
# negamax= qagents.NegamaxAgent(depth=4, searchWindow=16)
# game = QuartoGame(negamax, geneticminmax, gui_mode=False, bin_mode=False)
# game.run
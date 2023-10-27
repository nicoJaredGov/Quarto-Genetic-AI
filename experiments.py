from quarto import *
import quarto_agents as qagents

'negamax tests'
num_runs = 10

#search window and depth values
negamax_search = [16]
negamax_depths = [2]

#experiment control agent
geneticminmax = qagents.GeneticMinmaxAgent(searchDepth=3, maxGenerations=2, initialPopulationSize=3000, maxPopulationSize=6000)

for s in negamax_search:
    for d in negamax_depths:
        negamax_agent = qagents.NegamaxAgent(depth=d, searchWindow=s)

        #half the runs as player 1
        game = QuartoGame(negamax_agent, geneticminmax, gui_mode=False, bin_mode=False)
        game.runMultiple(num_runs//2)

        #half the runs as player 2
        game = QuartoGame(geneticminmax, negamax_agent, gui_mode=False, bin_mode=False)
        game.runMultiple(num_runs//2)




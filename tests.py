from quarto import *
import quarto_agents as qagents

game3 = QuartoGame(qagents.HumanPlayer(), qagents.HumanPlayer())
game3.playRandomFirst()
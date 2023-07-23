from quarto import *
import quarto_agents as qagents

game3 = QuartoGame(qagents.HumanPlayer(), qagents.HumanPlayer(), gui_mode=True, bin_mode=True)
game3.playRandomFirst()
from quarto_agents.generic_quarto_agent import GenericQuartoAgent
from numpy import random

class RandomAgent(GenericQuartoAgent):
    def __init__(self) -> None:
        super().__init__()
        super().setName("Random Agent")

    def makeFirstMove(self, quartoGameState, gui_mode=False):
        nextPiece = int(random.choice(list(quartoGameState[1])))
        return nextPiece
    
    def makeMove(self, quartoGameState, gui_mode=False):
        position = int(random.choice(list(quartoGameState[2])))
        nextPiece = int(random.choice(list(quartoGameState[1])))
        if gui_mode: print(f"Random agent placed piece at cell {position} and nextPiece is {nextPiece}")
        return position, nextPiece
from quarto_agents.generic_quarto_agent import GenericQuartoAgent

class HumanPlayer(GenericQuartoAgent):

    def __init__(self) -> None:
        super().__init__()
        super().setName("Human Player")

    def setName(self, name) -> None:
        return super().setName(name)

    def makeFirstMove(self, quartoGameState):
        nextPiece = int(input("Pick your opponent's first piece: "))
        return nextPiece
    
    def makeMove(self, quartoGameState):
        position = int(input("Cell: "))
        nextPiece = int(input("Your opponent's next piece: "))
        return position, nextPiece
from abc import ABC, abstractmethod
from typing import Any

class GenericQuartoAgent(ABC):
    
    @abstractmethod
    def makeFirstMove(self) -> int:
        pass

    @abstractmethod
    def makeMove(self) -> Any:
        pass

class HumanPlayer(GenericQuartoAgent):

    def makeFirstMove(self):
        nextPiece = int(input("Pick your opponent's first piece: "))
        return nextPiece
    
    def makeMove(self):
        position = int(input("Place the next piece here: "))
        nextPiece = int(input("Your opponent's next piece: "))
        return position, nextPiece
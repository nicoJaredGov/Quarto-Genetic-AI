from abc import ABC, abstractmethod
from typing import Any

class GenericQuartoAgent(ABC):

    @abstractmethod
    def makeFirstMove(self, quartoGameState) -> int:
        pass

    @abstractmethod
    def makeMove(self, quartoGameState) -> Any:
        pass

    def setName(self, name) -> None:
        self.name = name
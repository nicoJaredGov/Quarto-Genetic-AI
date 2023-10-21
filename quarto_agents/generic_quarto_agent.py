from abc import ABC, abstractmethod
from typing import Any

class GenericQuartoAgent(ABC):

    @abstractmethod
    def makeFirstMove(self, quartoGameState, gui_mode) -> int:
        pass

    @abstractmethod
    def makeMove(self, quartoGameState, gui_mode) -> Any:
        pass

    def setName(self, name) -> None:
        self.name = name
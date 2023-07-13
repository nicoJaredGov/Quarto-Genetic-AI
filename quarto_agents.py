from abc import ABC, abstractmethod

class GenericQuartoAgent(ABC):
    
    @abstractmethod
    def makeFirstMove(self):
        pass

    @abstractmethod
    def makeMove(self):
        pass
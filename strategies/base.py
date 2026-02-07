from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    """
    Abstract Base Class for all strategies.
    Ensures that every strategy implements the required methods.
    """
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Takes raw market data and returns a DataFrame with signals.
        1 = Buy, -1 = Sell, 0 = Hold
        """
        pass

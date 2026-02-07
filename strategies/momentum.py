import pandas as pd
import numpy as np
from strategies.base import BaseStrategy

class MomentumStrategy(BaseStrategy):
    def __init__(self, short_window=50, long_window=200):
        super().__init__("MomentumStrategy")
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generates Buy (1) and Sell (-1) signals based on SMA Crossover.
        """
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0.0

        # Vectorized calculation
        signals['short_mavg'] = data['close'].rolling(window=self.short_window, min_periods=1, center=False).mean()
        signals['long_mavg'] = data['close'].rolling(window=self.long_window, min_periods=1, center=False).mean()

        # Create signal
        # 1 when short > long, 0 otherwise (Logic can be customized)
        # We only want to trade on the *crossover*, but for this simple engine let's just emit state
        # The Portfolio "Accountant" handles the state (holding vs not holding).
        
        # Signal = 1 (Buy/Hold Long), -1 (Sell/Short) or 0 (Neutral)
        # If short > long, we want to be Long (1).
        # If short < long, we want to be out (0) or Short (-1). Let's say we just exit (signal -1 to close).
        
        signals['signal'] = np.where(signals['short_mavg'] > signals['long_mavg'], 1.0, -1.0)
        
        # .diff() to detect changes if we wanted only triggers
        # But our simple engine receives the target state (1 or -1) in each step or we can optimize
        
        return signals[['signal']]

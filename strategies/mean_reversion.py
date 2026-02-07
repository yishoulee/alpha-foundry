import pandas as pd
import numpy as np
from strategies.base import BaseStrategy

class MeanReversionStrategy(BaseStrategy):
    def __init__(self, window=20, num_std=2):
        super().__init__("MeanReversionStrategy")
        self.window = window
        self.num_std = num_std

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generates signals based on Bollinger Bands.
        Buy when price < lower band (Expecting reversion up)
        Sell when price > upper band (Expecting reversion down)
        """
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0.0

        rolling_mean = data['close'].rolling(window=self.window).mean()
        rolling_std = data['close'].rolling(window=self.window).std()
        
        upper_band = rolling_mean + (rolling_std * self.num_std)
        lower_band = rolling_mean - (rolling_std * self.num_std)

        # Vectorized signal generation
        # Initialize with 0
        s = np.zeros(len(data))
        
        # We need to maintain state because we hold until exit condition
        # This is harder to fully vectorize pure logic without state loop if exit is conditional
        # But for simple "Buy if below lower, Sell if above upper", we can try:
        
        # 1: Price < Lower (Oversold -> Buy)
        # -1: Price > Upper (Overbought -> Sell)
        # 0: In between? Usually hold previous position?
        
        # Let's simplify: 
        # Buy (1) if Close < Lower
        # Sell (-1) if Close > Upper
        # Else 0 (Hold whatever we have? Or Neutral?)
        # For our simple engine, let's treat it as signals to change state.
        
        signals['lower_band'] = lower_band
        signals['upper_band'] = upper_band
        
        # Logic:
        # If today close < lower_band -> Enter Long (1)
        # If today close > upper_band -> Exit/Short (-1)
        # Otherwise -> 0 (No new signal)
        
        signals['signal'] = np.where(data['close'] < lower_band, 1.0, 
                                     np.where(data['close'] > upper_band, -1.0, 0.0))

        # Because strict vectorization of "hold previous state if 0" requires a loop or ffill, 
        # we can use pandas fillna if we treat 0 as NaN (but 0 might mean "Close Position" too)
        
        # Let's say 0 means "Do nothing / Keep status quo"
        # We can implement a forward fill to propagate positions
        # Replace 0 with NaN for ffill, then fill with 0 (start flat)
        positions = signals['signal'].replace(to_replace=0, value=np.nan).ffill()
        signals['signal'] = positions.fillna(0)

        return signals[['signal']]

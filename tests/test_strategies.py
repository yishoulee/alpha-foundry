import unittest
import pandas as pd
import numpy as np
from strategies.mean_reversion import MeanReversionStrategy
from strategies.momentum import MomentumStrategy

class TestStrategies(unittest.TestCase):
    def setUp(self):
        # Create dummy data
        dates = pd.date_range(start="2020-01-01", periods=100)
        self.data = pd.DataFrame(index=dates)
        # Create a simple sine wave for predictable mean reversion
        x = np.linspace(0, 4*np.pi, 100)
        self.data['close'] = 100 + 10 * np.sin(x) 
        # Mean around 100, amplitude 10 (90 to 110)

    def test_mean_reversion_strategy(self):
        strategy = MeanReversionStrategy(window=10, num_std=1) # Narrow bands for testing
        signals = strategy.generate_signals(self.data)
        
        # Check output structure
        self.assertIsInstance(signals, pd.DataFrame)
        self.assertIn('signal', signals.columns)
        self.assertEqual(len(signals), 100)
        
        # Check logic roughly
        # The strategy fills nan with 0 then uses ffill. 
        # We expect 1s, -1s and 0s.
        unique_signals = signals['signal'].unique()
        self.assertTrue(np.all(np.isin(unique_signals, [0, 1, -1])))
        
        # Specific check: 
        # Find a point where price is very low (should buy/long -> 1)
        # Sine wave minimum is at 3pi/2 approx.
        # Check if we have some 1s
        self.assertTrue((signals['signal'] == 1).any())
        self.assertTrue((signals['signal'] == -1).any())

    def test_momentum_strategy(self):
        # Create trending data
        dates = pd.date_range(start="2020-01-01", periods=100)
        trend_data = pd.DataFrame(index=dates)
        trend_data['close'] = np.linspace(100, 200, 100) # Steady uptrend
        
        strategy = MomentumStrategy(short_window=5, long_window=10)
        signals = strategy.generate_signals(trend_data)
        
        # After enough periods, short MA > long MA -> Signal 1
        # First 10 periods will be unstable/NaN (handled as 0 or diff by rolling)
        
        # Check later periods
        tail_signals = signals['signal'].tail(20)
        # Should be all 1.0 because strictly uptrending
        self.assertTrue(all(tail_signals == 1.0))
        
        # Create downtrend
        trend_data['close'] = np.linspace(200, 100, 100)
        signals_down = strategy.generate_signals(trend_data)
        tail_signals_down = signals_down['signal'].tail(20)
        self.assertTrue(all(tail_signals_down == -1.0))

if __name__ == '__main__':
    unittest.main()

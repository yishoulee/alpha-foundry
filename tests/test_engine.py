import unittest
from unittest.mock import MagicMock, ANY
import pandas as pd
from core.engine import BacktestEngine

class TestEngine(unittest.TestCase):
    def setUp(self):
        self.mock_loader = MagicMock()
        self.mock_portfolio = MagicMock()
        self.mock_strategy = MagicMock()
        self.engine = BacktestEngine(self.mock_loader, self.mock_portfolio, self.mock_strategy)

    def test_run(self):
        # Setup data
        dates = pd.date_range(start="2020-01-01", periods=5)
        data = pd.DataFrame({'close': [100, 101, 102, 103, 104]}, index=dates)
        
        # Setup strategy return
        signals = pd.DataFrame({'signal': [1, 0, 0, -1, 0]}, index=dates)
        self.mock_strategy.generate_signals.return_value = signals
        
        # Run engine
        self.engine.run(data)
        
        # Verify strategy called
        self.mock_strategy.generate_signals.assert_called_once_with(data)
        
        # Verify portfolio processed signals 5 times
        self.assertEqual(self.mock_portfolio.process_signal.call_count, 5)
        
        # Check arguments of last call
        # Price 104, Signal 0, Date ...
        args, _ = self.mock_portfolio.process_signal.call_args
        self.assertEqual(args[0], 104) # Price
        self.assertEqual(args[1], 0)   # Signal
        # args[2] is date

    def test_get_results(self):
        # Mock portfolio equity curve
        equity_df = pd.DataFrame({
            'equity': [10000, 10100, 10200, 9900, 10050]
        }, index=pd.date_range("2020-01-01", periods=5))
        self.mock_portfolio.get_equity_curve_df.return_value = equity_df
        self.mock_portfolio.initial_capital = 10000.0
        
        results = self.engine.get_results()
        
        self.assertIn('Total Return', results)
        self.assertIn('Sharpe Ratio', results)
        self.assertIn('Max Drawdown', results)
        self.assertIn('Final Equity', results)
        
        # Expect roughly 0.5% return (10000 -> 10050)
        self.assertAlmostEqual(results['Total Return'], 0.005)

if __name__ == '__main__':
    unittest.main()

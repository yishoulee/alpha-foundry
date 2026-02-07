import unittest
import numpy as np
import pandas as pd
from utils.metrics import calculate_sharpe_ratio, calculate_drawdown

class TestMetrics(unittest.TestCase):
    def test_sharpe_ratio(self):
        # 1. Simple Case: Constant return > 0
        returns = pd.Series([0.01, 0.01, 0.01, 0.01])
        # Std dev is 0, so should handle div by zero or return 0? 
        # My impl checks std != 0 else returns 0
        self.assertEqual(calculate_sharpe_ratio(returns), 0.0)

        # 2. Case with variance
        returns = pd.Series([0.01, 0.02, 0.03, -0.01])
        sharpe = calculate_sharpe_ratio(returns)
        self.assertTrue(sharpe > 0)

    def test_max_drawdown(self):
        # Equity curve: 100 -> 110 -> 99 -> 120
        # Peak 110. Drawdown to 99 is (99-110)/110 = -11/110 = -0.1 (-10%)
        equity = np.array([100, 110, 99, 120])
        dd = calculate_drawdown(equity)
        self.assertAlmostEqual(dd, -0.1)

    def test_no_drawdown(self):
        equity = np.array([100, 110, 120, 130])
        dd = calculate_drawdown(equity)
        self.assertEqual(dd, 0.0)

if __name__ == '__main__':
    unittest.main()

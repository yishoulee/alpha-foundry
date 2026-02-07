import unittest
import pandas as pd
from core.portfolio import Portfolio

class TestPortfolio(unittest.TestCase):
    def setUp(self):
        self.portfolio = Portfolio(initial_capital=10000.0, transaction_cost=0.001, slippage=0.0)

    def test_initialization(self):
        self.assertEqual(self.portfolio.current_capital, 10000.0)
        self.assertEqual(self.portfolio.positions, 0)
        self.assertEqual(len(self.portfolio.equity_curve), 0)

    def test_process_signal_buy(self):
        # Signal 1: Buy
        price = 100.0
        date = pd.Timestamp("2020-01-01")
        
        # Process BUY
        self.portfolio.process_signal(price, 1, date)
        
        # Should have converted capital to positions
        self.assertEqual(self.portfolio.current_capital, 0)
        self.assertTrue(self.portfolio.positions > 0)
        
        # Check calculation:
        # Cost per share = 100 * (1 + 0.001) = 100.1
        # Shares = 10000 / 100.1 = 99.9000999
        expected_shares = 10000.0 / (100.0 * 1.001)
        self.assertAlmostEqual(self.portfolio.positions, expected_shares)
        
        # Check equity curve update
        # Equity = 0 + shares * current_price (100)
        # Initial equity = 10000. Cost of trade (comm) reduces equity slightly immediately?
        # Value of pos = 99.900... * 100 = 9990.0099
        # Equity = 9990.01 roughly (loss of ~10 due to commission)
        self.assertEqual(len(self.portfolio.equity_curve), 1)
        equity_entry = self.portfolio.equity_curve[0]
        self.assertEqual(equity_entry['date'], date)
        self.assertAlmostEqual(equity_entry['equity'], expected_shares * 100.0)

    def test_process_signal_sell(self):
        # Setup: Buy first
        price_buy = 100.0
        date_buy = pd.Timestamp("2020-01-01")
        self.portfolio.process_signal(price_buy, 1, date_buy)
        
        shares_held = self.portfolio.positions
        
        # Now Sell at profit
        price_sell = 110.0
        date_sell = pd.Timestamp("2020-01-02")
        self.portfolio.process_signal(price_sell, -1, date_sell)
        
        # Should have closed position
        self.assertEqual(self.portfolio.positions, 0)
        self.assertTrue(self.portfolio.current_capital > 10000.0) # Profit made
        
        # Calculation:
        # Revenue = Shares * 110 * (1 - 0.001)
        expected_revenue = shares_held * 110.0 * 0.999
        self.assertAlmostEqual(self.portfolio.current_capital, expected_revenue)
        
        self.assertEqual(len(self.portfolio.equity_curve), 2)
        self.assertAlmostEqual(self.portfolio.equity_curve[-1]['equity'], expected_revenue)

    def test_process_signal_hold(self):
        # Buy first
        price = 100.0
        self.portfolio.process_signal(price, 1, pd.Timestamp("2020-01-01"))
        positions_before = self.portfolio.positions
        
        # Signal 0: Hold (no change in position tokens)
        price_next = 105.0 
        self.portfolio.process_signal(price_next, 0, pd.Timestamp("2020-01-02"))
        
        self.assertEqual(self.portfolio.positions, positions_before)
        # Equity should increase due to price increase
        equity = self.portfolio.equity_curve[-1]['equity']
        self.assertAlmostEqual(equity, positions_before * price_next)

    def test_get_equity_curve_df(self):
        self.portfolio.process_signal(100, 1, pd.Timestamp("2020-01-01"))
        df = self.portfolio.get_equity_curve_df()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.index[0], pd.Timestamp("2020-01-01"))

if __name__ == '__main__':
    unittest.main()

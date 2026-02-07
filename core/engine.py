import pandas as pd
import time
from core.data_loader import DataLoader
from core.portfolio import Portfolio
from strategies.base import BaseStrategy
from utils.logger import setup_logger
from utils.metrics import calculate_sharpe_ratio, calculate_drawdown

logger = setup_logger("BacktestEngine")

class BacktestEngine:
    def __init__(self, data_loader: DataLoader, portfolio: Portfolio, strategy: BaseStrategy):
        self.data_loader = data_loader
        self.portfolio = portfolio
        self.strategy = strategy
        self.execution_metrics = {}

    def run(self, data: pd.DataFrame):
        logger.info(f"Starting backtest for strategy: {self.strategy.name}")
        start_time = time.time()
        
        # 1. Generate Signals
        signal_start = time.time()
        signals_df = self.strategy.generate_signals(data)
        signal_duration = time.time() - signal_start
        
        # 2. Iterate through time (simplified loop for the portfolio tracking)
        # Note: In a fully vectorized engine, we would calculate PnL using pandas directly.
        # But loop is easier to understand for "The Accountant" logic initially.
        
        combined = data.join(signals_df, how='inner')
        loop_start = time.time()
        
        for date, row in combined.iterrows():
            price = row['close']
            signal = row.get('signal', 0)
            self.portfolio.process_signal(price, signal, date)
            
        loop_duration = time.time() - loop_start
        total_duration = time.time() - start_time
        
        num_bars = len(data)
        self.execution_metrics = {
             "Total Duration": total_duration,
             "Signal Gen Time": signal_duration,
             "Backtest Loop Time": loop_duration,
             "bars_processed": num_bars,
             "bars_per_sec": num_bars / total_duration if total_duration > 0 else 0
        }
            
        logger.info(f"Backtest completed in {total_duration:.4f}s ({self.execution_metrics['bars_per_sec']:,.0f} bars/sec)")

    def get_results(self):
        equity_df = self.portfolio.get_equity_curve_df()
        if equity_df.empty:
            return {}
            
        returns = equity_df['equity'].pct_change().dropna()
        sharpe = calculate_sharpe_ratio(returns)
        drawdown = calculate_drawdown(equity_df['equity'].values)
        total_return = (equity_df['equity'].iloc[-1] / self.portfolio.initial_capital) - 1
        
        return {
            "Total Return": total_return,
            "Sharpe Ratio": sharpe,
            "Max Drawdown": drawdown,
            "Final Equity": equity_df['equity'].iloc[-1]
        }

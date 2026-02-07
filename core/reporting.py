import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from utils.logger import setup_logger

logger = setup_logger("PerformanceReport")

class PerformanceReport:
    """
    Generates a professional 'Tear Sheet' for a trading strategy.
    Calculates advanced metrics (Sortino, Calmar, Win Rate) and 
    visualizes performance to demonstrate engineering rigor.
    """
    def __init__(self, equity_curve: pd.DataFrame, benchmark_curve: pd.DataFrame = None, execution_metrics: dict = None):
        """
        :param equity_curve: DataFrame with DateTime index and 'equity' column.
        :param benchmark_curve: Optional DataFrame for market comparison (e.g., SPY).
        :param execution_metrics: Optional dictionary containing computational performance stats.
        """
        self.equity = equity_curve.copy()
        self.benchmark = benchmark_curve.copy() if benchmark_curve is not None else None
        self.execution_metrics = execution_metrics
        
        # Calculate Daily Returns
        self.equity['returns'] = self.equity['equity'].pct_change().fillna(0)
        if self.benchmark is not None:
            self.benchmark['returns'] = self.benchmark['close'].pct_change().fillna(0)

    def _calculate_metrics(self):
        """Internal method to compute hard metrics."""
        returns = self.equity['returns']
        total_days = (self.equity.index[-1] - self.equity.index[0]).days
        years = total_days / 365.25

        # 1. CAGR (Compound Annual Growth Rate)
        total_return = (self.equity['equity'].iloc[-1] / self.equity['equity'].iloc[0]) - 1
        cagr = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0

        # 2. Volatility (Annualized)
        ann_vol = returns.std() * np.sqrt(252)

        # 3. Sharpe Ratio (Risk Free Rate = 0 for simplicity)
        sharpe = (returns.mean() * 252) / (ann_vol + 1e-9)

        # 4. Sortino Ratio (Downside Risk only)
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() * np.sqrt(252)
        sortino = (returns.mean() * 252) / (downside_std + 1e-9)

        # 5. Max Drawdown
        rolling_max = self.equity['equity'].cummax()
        drawdown = (self.equity['equity'] - rolling_max) / rolling_max
        max_dd = drawdown.min()

        # 6. Calmar Ratio (Return / Max Drawdown)
        calmar = cagr / abs(max_dd) if max_dd != 0 else 0

        return {
            "CAGR": cagr,
            "Volatility": ann_vol,
            "Sharpe Ratio": sharpe,
            "Sortino Ratio": sortino,
            "Max Drawdown": max_dd,
            "Calmar Ratio": calmar,
            "Total Return": total_return
        }

    def generate_tear_sheet(self):
        """
        Prints a text-based professional summary to the console.
        """
        metrics = self._calculate_metrics()
        
        print("\n" + "="*50)
        print(f"{'STRATEGY PERFORMANCE REPORT':^50}")
        print("="*50)
        
        # Performance Section
        print(f"\n{'--- RETURN METRICS ---':^50}")
        print(f"Total Return:    {metrics['Total Return']:>10.2%}")
        print(f"CAGR:            {metrics['CAGR']:>10.2%}")
        print(f"Annual Volatility:{metrics['Volatility']:>9.2%}")
        
        # Risk Section (This is where you impress engineers!)
        print(f"\n{'--- RISK METRICS ---':^50}")
        print(f"Sharpe Ratio:    {metrics['Sharpe Ratio']:>10.2f}  (>1.0 is good)")
        print(f"Sortino Ratio:   {metrics['Sortino Ratio']:>10.2f}  (Downside adjusted)")
        print(f"Calmar Ratio:    {metrics['Calmar Ratio']:>10.2f}  (Return vs Crash)")
        print(f"Max Drawdown:    {metrics['Max Drawdown']:>10.2%}  (Worst peak-to-valley)")

        if self.execution_metrics:
             print(f"\n{'--- COMPUTATION SPEED ---':^50}")
             print(f"Process Speed:   {self.execution_metrics.get('bars_per_sec', 0):,.0f} bars/sec")
             print(f"Total Time:      {self.execution_metrics.get('Total Duration', 0):.4f} seconds")
        
        print("\n" + "="*50 + "\n")

    def plot_dashboard(self, filename="dashboard.png"):
        """
        Generates a 3-panel dashboard:
        1. Equity Curve vs Benchmark
        2. Underwater Plot (Drawdown)
        3. Rolling Volatility / Returns
        """
        logger.info("Generating dashboard plot...")
        fig, axes = plt.subplots(3, 1, figsize=(12, 12), sharex=True)
        
        # Plot 1: Equity Curve
        axes[0].plot(self.equity.index, self.equity['equity'], label='Strategy', color='blue')
        if self.benchmark is not None:
            # Normalize benchmark to start at same capital
            norm_bench = (self.benchmark['close'] / self.benchmark['close'].iloc[0]) * self.equity['equity'].iloc[0]
            axes[0].plot(self.benchmark.index, norm_bench, label='Benchmark (SPY)', color='gray', linestyle='--', alpha=0.6)
        
        axes[0].set_title("Equity Curve (Wealth Growth)")
        axes[0].set_ylabel("Capital ($)")
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)

        # Plot 2: Underwater Plot (Drawdown visualization)
        rolling_max = self.equity['equity'].cummax()
        drawdown = (self.equity['equity'] - rolling_max) / rolling_max
        axes[1].fill_between(drawdown.index, drawdown, 0, color='red', alpha=0.3)
        axes[1].plot(drawdown.index, drawdown, color='red', linewidth=1)
        axes[1].set_title("Underwater Plot (Drawdown Severity)")
        axes[1].set_ylabel("Drawdown %")
        axes[1].grid(True, alpha=0.3)
        
        # Plot 3: Rolling Sharpe (6-month)
        rolling_sharpe = self.equity['returns'].rolling(126).apply(lambda x: np.mean(x)/np.std(x)*np.sqrt(252) if np.std(x)!=0 else 0)
        axes[2].plot(rolling_sharpe.index, rolling_sharpe, color='green')
        axes[2].axhline(0, color='black', linestyle='-', linewidth=0.5)
        axes[2].set_title("Rolling 6-Month Sharpe Ratio (Consistency Check)")
        axes[2].set_ylabel("Sharpe")
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(filename)
        logger.info(f"Dashboard saved to {filename}")
        # Check if running in a headless environment, skip show() if so, or use try-except
        try:
            plt.show()
        except Exception:
            pass
        plt.close()

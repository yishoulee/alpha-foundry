import matplotlib.pyplot as plt
import pandas as pd
import os
from utils.logger import setup_logger

logger = setup_logger("Visualizer")

class Visualizer:
    def __init__(self, output_dir="results"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def plot_equity_curve(self, strategy_equity: pd.Series, benchmark_equity: pd.Series, title: str, filename: str = None):
        """
        Plots the strategy equity curve against a benchmark.
        """
        logger.info(f"Generating plot: {title}")
        
        plt.figure(figsize=(12, 6))
        
        # Ensure indices match logic or align them
        # We assume they share the same datetime index
        
        plt.plot(strategy_equity.index, strategy_equity.values, label='Strategy Equity', linewidth=2)
        
        if benchmark_equity is not None:
            plt.plot(benchmark_equity.index, benchmark_equity.values, label='Benchmark (Buy & Hold)', linestyle='--', alpha=0.7, color='gray')
            
        plt.title(title)
        plt.xlabel('Date')
        plt.ylabel('Equity ($)')
        plt.legend(loc='upper left')
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)
        
        # Formatting Y-axis to currency might be nice, but simple layout is fine for now
        
        if filename:
            path = os.path.join(self.output_dir, filename)
            plt.savefig(path)
            logger.info(f"Plot saved to {path}")
        else:
            plt.show()
            
        plt.close()

    def plot_signals(self, data: pd.DataFrame, signals: pd.DataFrame, title: str, filename: str = None):
        """
        Plots price data with buy/sell markers.
        """
        # (Optional implementation for future extension)
        pass

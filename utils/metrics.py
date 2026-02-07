import numpy as np
import pandas as pd

def calculate_sharpe_ratio(returns, risk_free_rate=0.0):
    """
    Calculates the Sharpe Ratio for a series of returns.
    """
    if len(returns) == 0:
        return 0.0
    
    excess_returns = returns - risk_free_rate
    return np.mean(excess_returns) / np.std(excess_returns) if np.std(excess_returns) != 0 else 0.0

def calculate_drawdown(equity_curve):
    """
    Calculates the maximum drawdown of an equity curve.
    """
    running_max = np.maximum.accumulate(equity_curve)
    drawdown = (equity_curve - running_max) / running_max
    return drawdown.min()

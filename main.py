import sys
from core.data_loader import DataLoader
from core.portfolio import Portfolio
from core.engine import BacktestEngine
from strategies.momentum import MomentumStrategy
from strategies.mean_reversion import MeanReversionStrategy
from utils.logger import setup_logger
from core.reporting import PerformanceReport

from utils.visualization import Visualizer

logger = setup_logger("Main")

def main():
    logger.info("Initializing Alpha Foundry...")
    viz = Visualizer()
    initial_capital = 100000

    # 1. Load Data
    loader = DataLoader()
    ticker = "0050.TW" # Yuanta Taiwan Top 50 ETF
    try:
        logger.info(f"Attempting to fetch real data for {ticker}...")
        data = loader.fetch_data(ticker, start="2020-01-01")
        
        if data.empty:
            logger.warning("Real data fetch returned empty. Falling back to dummy data.")
            data = loader.generate_dummy_data(days=500)
            
    except Exception as e:
        logger.error(f"Failed to load real data: {e}")
        logger.info("Falling back to dummy data...")
        data = loader.generate_dummy_data(days=500)

    # 2. Configure Strategy
    # Strategy 1: Momentum
    strategy_mom = MomentumStrategy(short_window=20, long_window=50)
    
    # Strategy 2: Mean Reversion
    strategy_mr = MeanReversionStrategy(window=20, num_std=2)

    # Calculate Benchmark (Buy & Hold)
    # Align benchmark with data index
    benchmark_equity = (data['close'] / data['close'].iloc[0]) * initial_capital

    # 3. Setup Portfolio/Accountant and Run Momentum
    # Config: 0.1425% Comm + 0.3% Tax (Approx 0.2% avg per leg) | 0.05% Slippage
    portfolio_mom = Portfolio(initial_capital=initial_capital, transaction_cost=0.002, slippage=0.0005)
    engine_mom = BacktestEngine(loader, portfolio_mom, strategy_mom)
    
    logger.info("Running Momentum Strategy...")
    engine_mom.run(data)
    results_mom = engine_mom.get_results()
    
    print("\n" + "="*30)
    print("MOMENTUM RESULTS")
    print("="*30)
    for k, v in results_mom.items():
        print(f"{k}: {v:,.4f}")
    print("="*30 + "\n")
    
    # Visualize Momentum
    equity_mom = portfolio_mom.get_equity_curve_df()
    if not equity_mom.empty:
         viz.plot_equity_curve(
             equity_mom['equity'], 
             benchmark_equity, 
             f"Momentum Strategy vs {ticker} (Buy & Hold)", 
             "momentum_performance.png"
         )
         
         # Generate Professional Report
         logger.info("Generating Professional Report for Momentum Strategy...")
         # Create a benchmark dataframe explicitly for the report
         benchmark_df = data[['close']]
         report_mom = PerformanceReport(equity_mom, benchmark_curve=benchmark_df, execution_metrics=engine_mom.execution_metrics)
         report_mom.generate_tear_sheet()
         report_mom.plot_dashboard(filename="results/momentum_dashboard.png")

    # 4. Run Mean Reversion
    portfolio_mr = Portfolio(initial_capital=initial_capital, transaction_cost=0.002, slippage=0.0005)
    engine_mr = BacktestEngine(loader, portfolio_mr, strategy_mr)
    
    logger.info("Running Mean Reversion Strategy...")
    engine_mr.run(data)
    results_mr = engine_mr.get_results()
    
    print("\n" + "="*30)
    print("MEAN REVERSION RESULTS")
    print("="*30)
    for k, v in results_mr.items():
        print(f"{k}: {v:,.4f}")
    print("="*30 + "\n")
    
    # Visualize Mean Reversion
    equity_mr = portfolio_mr.get_equity_curve_df()
    if not equity_mr.empty:
         viz.plot_equity_curve(
             equity_mr['equity'], 
             benchmark_equity, 
             f"Mean Reversion Strategy vs {ticker} (Buy & Hold)", 
             "mean_reversion_performance.png"
         )
         
         # Generate Professional Report
         logger.info("Generating Professional Report for Mean Reversion Strategy...")
         # Create a benchmark dataframe explicitly for the report
         benchmark_df = data[['close']]
         report_mr = PerformanceReport(equity_mr, benchmark_curve=benchmark_df, execution_metrics=engine_mr.execution_metrics)
         report_mr.generate_tear_sheet()
         report_mr.plot_dashboard(filename="results/mean_reversion_dashboard.png")


if __name__ == "__main__":
    main()

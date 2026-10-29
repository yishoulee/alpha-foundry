# Alpha Foundry: Modular Quantitative Research Framework

A modular, object-oriented backtesting engine designed to demonstrate **clean architecture**, **system design principles**, and **financial data integrity**. This project provides infrastructure for testing trading strategies against real-world and synthetic datasets.

---

## Project Structure

```text
alpha-foundry/
├── core/
│   ├── engine.py        # The Backtester loop
│   ├── data_loader.py   # Data ingestion (YFinance / Synthetic)
│   ├── portfolio.py     # State management, Fees, & Slippage logic
│   └── reporting.py     # Professional Tearsheet generation
├── strategies/
│   ├── base.py          # Abstract Base Class (Interface)
│   ├── momentum.py      # Moving Average Crossover Strategy
│   └── mean_reversion.py # Bollinger Band Mean Reversion
├── tests/               # Unit Tests
│   ├── test_data_loader.py
│   ├── test_engine.py
│   ├── test_metrics.py
│   ├── test_portfolio.py
│   └── test_strategies.py
├── utils/
│   ├── visualization.py # Matplotlib plotting wrappers
│   ├── metrics.py       # Financial math calculations
│   └── logger.py        # Standardized logging configuration
├── results/             # Auto-generated dashboards (.png)
├── main.py              # Entry point implementation
├── Makefile             # Command runner (install, run, test)
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

---

## Usage

The project includes a `Makefile` for standard engineering workflows.

### 1. Install Dependencies
```bash
make install
```

### 2. Run the Engine
Attempts to download **Yuanta Taiwan Top 50 ETF (0050.TW)** data, then generates metrics and dashboards. If the download fails or returns empty data, `main.py` automatically uses 500 synthetic bars. Check the run logs to establish the data source; a completed run alone does not confirm real-market data.
```bash
make run
```

### 3. Run Unit Tests
Runs unit tests for data handling, strategies, portfolio accounting, metrics, and engine orchestration. These tests do not include a performance regression benchmark.
```bash
make test
```

### 4. Clean Workspace
```bash
make clean
```

---

## Sample Output (Tear Sheet)

The following historical example illustrates the report format. Its data source, workload size, hardware, software versions, and timing repetitions are not documented with this example, so the figures are **unverified example values**, not reproducible performance claims:

```text
==================================================
           STRATEGY PERFORMANCE REPORT            
==================================================

              --- RETURN METRICS ---              
Total Return:       192.23%
CAGR:                19.23%
Annual Volatility:   15.81%

               --- RISK METRICS ---               
Sharpe Ratio:          1.23  (>1.0 is good)
Sortino Ratio:         1.40  (Downside adjusted)
Calmar Ratio:          0.72  (Return vs Crash)
Max Drawdown:       -26.86%  (Worst peak-to-valley)

               --- COMPUTATION SPEED ---          
Process Speed:       52,490 bars/sec
Total Time:          0.0245 seconds
```

`Process Speed` is `len(data) / Total Duration` from `BacktestEngine.run()`: signal generation, the data/signal join, and sequential portfolio processing. It excludes downloads, result calculations, reporting, and plotting; it is not a signal-only or fully vectorized-engine benchmark. The numerator counts input rows, which may differ from rows processed if a strategy changes the index before the inner join.

See the [performance audit](docs/performance-audit-2026-10-29.md) for source findings, controlled synthetic measurements, and execution limitations. The historical 52,490 bars/sec figure remains unverified.

The system also saves visual Dashboards to the `results/` folder:
*   `momentum_dashboard.png`
*   `mean_reversion_dashboard.png`

---


## Key Concepts & Implementation Details

This project bridges the gap between "notebook research" and "software engineering best practices" by implementing the following concepts:

### 1. Software Engineering Principles
*   **Separation of Concerns**: The system is modular. The *Strategy* doesn't know about the *Accountant*. The *Engine* doesn't know the math behind the *Signals*.
    *   *Implementation*: 
        *   `core/portfolio.py`: Handles money, positions, and cost simulation (The Accountant).
        *   `core/engine.py`: Orchestrates the event loop (The Manager).
        *   `strategies/`: Pure logic modules (The Quants).
*   **Strategy Design Pattern**: Allows strategies to be swapped interchangeably without changing the engine code.
    *   *Implementation*: `strategies/base.py` defines the abstract interface that `MomentumStrategy` and `MeanReversionStrategy` must implement.
*   **Vectorized Signal Generation**: The momentum and mean-reversion strategies use Pandas rolling operations and NumPy array operations to generate signals.
    *   *Implementation*: `strategies/momentum.py` uses `.rolling()` and `np.where()`; `strategies/mean_reversion.py` also uses forward filling. Portfolio accounting in `core/engine.py` remains sequential via `iterrows()` and `Portfolio.process_signal()`.

### 2. Quantitative Finance Realism
*   **Realistic Execution Simulation**: A backtest is useless if it ignores costs.
    *   *Implementation*: `core/portfolio.py` implements **Slippage** (bid-ask spread impact) and **Transaction Costs** (commissions + tax) on every trade.
*   **Risk Management & Metrics**: Focuses on risk-adjusted returns, not just total profit.
    *   *Implementation*: `core/reporting.py` calculates **Sharpe Ratio**, **Sortino Ratio**, **Calmar Ratio**, and **Max Drawdown**.
*   **Visualizing Risk ("The Underwater Plot")**: Instead of just showing wealth growth, we visualize the *pain* of drawdowns.
    *   *Implementation*: `core/reporting.py` generates 3-panel dashboards (Equity, Drawdown, Rolling Sharpe) automatically.

### 3. Data Engineering
*   **Data Abstraction Layer**: The strategy shouldn't care if data comes from a CSV, an API, or a random number generator.
    *   *Implementation*: `core/data_loader.py` supports **Yahoo Finance (`yfinance`)** and synthetic random-return price paths. `main.py` selects synthetic data when fetching raises an exception or returns empty data.
*   **Execution Timing**: The engine records signal-generation time, portfolio-loop time, and combined elapsed time for each run.
    *   *Implementation*: `core/engine.py` uses `time.time()` and the tear sheet reports input bars per combined elapsed second. This instrumentation does not establish high-frequency scalability or a guaranteed throughput threshold.

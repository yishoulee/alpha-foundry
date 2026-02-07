# Alpha Foundry: Modular Quantitative Research Framework

A robust, object-oriented backtesting engine designed to demonstrate **clean architecture**, **system design principles**, and **financial data integrity**. This project provides a scalable infrastructure for testing trading strategies against real-world and synthetic datasets.

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
├── tests/               # Unit & Integration Tests
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
Runs the simulation on **Yuanta Taiwan Top 50 ETF (0050.TW)**, generates metrics, and saves dashboards.
```bash
make run
```

### 3. Run Unit Tests
Ensures calculation accuracy for financial metrics.
```bash
make test
```

### 4. Clean Workspace
```bash
make clean
```

---

## Sample Output (Tear Sheet)

When running `make run`, the system produces a report used by professional desks:

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
*   **Vectorization**: Avoids slow Python loops (`for i in range(len(data))`) in favor of NumPy/Pandas array operations for signal generation.
    *   *Implementation*: `strategies/momentum.py` uses `.rolling()` and `np.where()` to process 10 years of data in milliseconds.

### 2. Quantitative Finance Realism
*   **Realistic Execution Simulation**: A backtest is useless if it ignores costs.
    *   *Implementation*: `core/portfolio.py` implements **Slippage** (bid-ask spread impact) and **Transaction Costs** (commissions + tax) on every trade.
*   **Risk Management & Metrics**: Focuses on risk-adjusted returns, not just total profit.
    *   *Implementation*: `core/reporting.py` calculates **Sharpe Ratio**, **Sortino Ratio**, **Calmar Ratio**, and **Max Drawdown**.
*   **Visualizing Risk ("The Underwater Plot")**: Instead of just showing wealth growth, we visualize the *pain* of drawdowns.
    *   *Implementation*: `core/reporting.py` generates 3-panel dashboards (Equity, Drawdown, Rolling Sharpe) automatically.

### 3. Data Engineering
*   **Data Abstraction Layer**: The strategy shouldn't care if data comes from a CSV, an API, or a random number generator.
    *   *Implementation*: `core/data_loader.py` handles fetching from **Yahoo Finance (`yfinance`)** dynamically, with automatic fallback to **Geometric Brownian Motion** (synthetic data) if the internet is down.
*   **Computational Performance Monitoring**: System tracks execution speed to ensure strategies scale to high-frequency environments.
    *   *Implementation*: `core/engine.py` captures execution timing and the tear sheet reports `Process Speed (bars/sec)`.

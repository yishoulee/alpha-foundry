import pandas as pd
from utils.logger import setup_logger

logger = setup_logger("Portfolio")

class Portfolio:
    def __init__(self, initial_capital=10000.0, transaction_cost=0.001, slippage=0.0005):
        """
        :param initial_capital: Starting cash.
        :param transaction_cost: Commission fee per trade (percentage, e.g., 0.001 = 0.1%).
        :param slippage: Slippage impact per trade (percentage, e.g., 0.0005 = 0.05%).
                         Simulates value lost due to bid-ask spread and market impact.
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = 0
        self.transaction_cost = transaction_cost
        self.slippage = slippage
        self.equity_curve = []
        self.holdings = [] # Time series of holdings

    def process_signal(self, price: float, signal: int, date):
        """
        updates portfolio state based on signal.
        signal: 1 (Buy), -1 (Sell), 0 (Hold)
        Assuming simple strategy: All-in / All-out for demonstration
        """
        trade_executed = False
        
        # If signal is Buy and we are not long
        if signal == 1 and self.positions == 0:
            # Execution Price (Higher due to slippage)
            exec_price = price * (1 + self.slippage)
            
            # Max shares we can buy
            # Cost = Shares * Price * (1 + Comm) -> Shares = Cash / (Price * (1 + Comm))
            # Here we use exec_price
            cost_per_share = exec_price * (1 + self.transaction_cost)
            
            self.positions = self.current_capital / cost_per_share
            self.current_capital = 0 # All cash in positions
            trade_executed = True
            logger.info(f"BUY at {date} | Price: {price:.2f} | ExecPrice: {exec_price:.2f} | Shares: {self.positions:.4f}")

        # If signal is Sell and we are long
        elif signal == -1 and self.positions > 0:
            # Execution Price (Lower due to slippage)
            exec_price = price * (1 - self.slippage)
            
            # Revenue = Shares * Price * (1 - Comm)
            revenue = self.positions * exec_price * (1 - self.transaction_cost)
            
            self.current_capital = revenue
            self.positions = 0
            trade_executed = True
            logger.info(f"SELL at {date} | Price: {price:.2f} | ExecPrice: {exec_price:.2f} | Revenue: {revenue:.2f}")

        # Update equity
        # Value positions at current market price (mid), not slippage price (which is for execution only)
        equity = self.current_capital + (self.positions * price)
        self.equity_curve.append({'date': date, 'equity': equity})
        
        return equity
    
    def get_equity_curve_df(self):
        df = pd.DataFrame(self.equity_curve)
        if not df.empty:
            df.set_index('date', inplace=True)
        return df

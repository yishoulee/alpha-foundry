import pandas as pd
import numpy as np
import os
import yfinance as yf
from utils.logger import setup_logger

logger = setup_logger("DataLoader")

class DataLoader:
    def __init__(self):
        pass

    def load_csv(self, filepath: str) -> pd.DataFrame:
        """
        Loads market data from a CSV file.
        df expected to have date, open, high, low, close, volume
        """
        if not os.path.exists(filepath):
            logger.error(f"File not found: {filepath}")
            raise FileNotFoundError(f"File not found: {filepath}")
        
        logger.info(f"Loading data from {filepath}")
        df = pd.read_csv(filepath, parse_dates=True, index_col=0)
        
        # Basic validation
        required_columns = ['close']
        for col in required_columns:
            if col not in df.columns and col.capitalize() not in df.columns:
                 # Try to normalize columns to lowercase
                 df.columns = [c.lower() for c in df.columns]
        
        if 'close' not in df.columns:
             raise ValueError("Data must contain a 'close' column")
             
        return df

    def fetch_data(self, ticker: str, start: str = "2020-01-01", end: str = None) -> pd.DataFrame:
        """
        Fetches historical data from Yahoo Finance.
        """
        logger.info(f"Fetching data for {ticker} from {start} to {end or 'now'}...")
        
        try:
            df = yf.download(ticker, start=start, end=end, progress=False)
            
            if df.empty:
                logger.warning(f"No data found for {ticker}")
                return pd.DataFrame()

            # Normalize columns
            # YFinance returns: Open, High, Low, Close, Adj Close, Volume
            # We want: open, high, low, close, volume
            
            # Handle MultiIndex columns if they exist (yfinance sometimes does this)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df.columns = [c.lower() for c in df.columns]
            
            # Rename 'adj close' to 'close' if we prefer adjusted, or verify we have 'close'
            # Usually for backtesting, Adj Close is better for returns, but 'Close' is actual price.
            # Let's map 'adj close' to 'close' if available, otherwise 'close'
            if 'adj close' in df.columns:
                df['close'] = df['adj close']
                
            required = ['open', 'high', 'low', 'close', 'volume']
            missing = [c for c in required if c not in df.columns]
            
            if missing:
                logger.error(f"Missing columns in downloaded data: {missing}")
                return pd.DataFrame()
                
            return df[required]
            
        except Exception as e:
            logger.error(f"Failed to download data for {ticker}: {e}")
            raise e


    def generate_dummy_data(self, days=1000) -> pd.DataFrame:
        """
        Generates synthetic data for testing.
        Uses vectorized numpy operations for efficiently generating 
        geometric Brownian motion-like paths.
        """
        logger.info("Generating dummy data")
        
        # 1. Generate Dates
        dates = pd.date_range(start="2020-01-01", periods=days, freq='D')
        
        # 2. Generate Geometric Brownian Motion (Vectorized)
        # Returns ~ N(0, 0.01)
        returns = np.random.normal(0, 0.01, days)
        
        # Calculate price path: P_t = P_0 * prod(1 + r_t)
        price_path = 100 * (1 + returns).cumprod()
        
        # 3. Construct DataFrame
        df = pd.DataFrame(index=dates)
        df['close'] = price_path
        
        # Add noise for Open, High, Low
        # Open is close + noise
        df['open'] = price_path * (1 + np.random.normal(0, 0.005, days))
        
        # High is max of open/close * (1 + positive noise)
        df['high'] = df[['open', 'close']].max(axis=1) * (1 + np.abs(np.random.normal(0, 0.005, days)))
        
        # Low is min of open/close * (1 - positive noise)
        df['low'] = df[['open', 'close']].min(axis=1) * (1 - np.abs(np.random.normal(0, 0.005, days)))
        
        df['volume'] = np.random.randint(100, 10000, days)
        
        return df

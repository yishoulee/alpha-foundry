import unittest
import pandas as pd
import numpy as np
import os
import tempfile
from unittest.mock import patch, MagicMock
from core.data_loader import DataLoader

class TestDataLoader(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader()

    def test_generate_dummy_data(self):
        days = 100
        df = self.loader.generate_dummy_data(days=days)
        
        # Check shape
        self.assertEqual(len(df), days)
        # Check columns
        self.assertIn('close', df.columns)
        # Check index is datetime
        self.assertTrue(isinstance(df.index, pd.DatetimeIndex))
        # Check data is not empty
        self.assertFalse(df.empty)

    @patch('core.data_loader.yf.download')
    def test_fetch_data_success(self, mock_download):
        # Mock the yfinance download response
        dates = pd.date_range(start="2020-01-01", periods=5)
        mock_df = pd.DataFrame({
            'Open': [100]*5,
            'High': [110]*5,
            'Low': [90]*5,
            'Close': [105]*5,
            'Volume': [1000]*5
        }, index=dates)
        mock_download.return_value = mock_df

        df = self.loader.fetch_data("AAPL", start="2020-01-01", end="2020-01-05")
        
        # Verify call arguments
        mock_download.assert_called_once()
        
        # Verify columns normalized to lowercase
        self.assertIn('close', df.columns)
        self.assertIn('open', df.columns)
        
        # Verify content matches
        self.assertEqual(len(df), 5)
        self.assertEqual(df['close'].iloc[0], 105)

    @patch('core.data_loader.yf.download')
    def test_fetch_data_empty(self, mock_download):
        mock_download.return_value = pd.DataFrame()
        df = self.loader.fetch_data("UNKNOWN")
        self.assertTrue(df.empty)

    def test_load_csv(self):
        # Create a temp csv file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Date,Open,High,Low,Close,Volume\n")
            f.write("2020-01-01,100,105,95,102,1000\n")
            f.write("2020-01-02,102,107,100,106,1200\n")
            temp_path = f.name
            
        try:
            df = self.loader.load_csv(temp_path)
            self.assertEqual(len(df), 2)
            self.assertIn('close', df.columns)
            self.assertEqual(df.index[0].year, 2020)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_load_csv_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            self.loader.load_csv("non_existent_file.csv")

if __name__ == '__main__':
    unittest.main()

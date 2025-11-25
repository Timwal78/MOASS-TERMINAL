"""
Data Fetcher - Utility for fetching market data
"""

import yfinance as yf
from typing import Dict

class DataFetcher:
    
    def get_price(self, ticker: str) -> Dict:
        """Get current price data"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d")
            
            if not hist.empty:
                return {
                    "ticker": ticker,
                    "price": float(hist['Close'].iloc[-1]),
                    "change": float(hist['Close'].iloc[-1] - hist['Open'].iloc[0]),
                    "change_pct": float((hist['Close'].iloc[-1] - hist['Open'].iloc[0]) / hist['Open'].iloc[0] * 100)
                }
            return {"ticker": ticker, "price": 0, "change": 0, "change_pct": 0}
        except:
            return {"ticker": ticker, "price": 0, "change": 0, "change_pct": 0}
    
    def get_short_interest(self, ticker: str) -> Dict:
        """Get short interest data"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                "ticker": ticker,
                "short_percent_float": info.get('shortPercentOfFloat', 0) * 100,
                "shares_short": info.get('sharesShort', 0),
                "short_ratio": info.get('shortRatio', 0)
            }
        except:
            return {"ticker": ticker, "short_percent_float": 0, "shares_short": 0, "short_ratio": 0}

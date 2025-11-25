"""
Market Scanner - Find the next GME
Scans entire market for squeeze candidates
"""

from typing import List, Dict
from datetime import datetime
import yfinance as yf

class MarketScanner:
    
    # Scan universe (top liquid stocks)
    SCAN_UNIVERSE = [
        # Add 100+ tickers here - for demo, using subset
        "GME", "AMC", "BBBY", "CLOV", "WISH", "MVIS", "BB", "NOK",
        "PLTR", "TSLA", "RIVN", "LCID", "PLUG", "NIO", "SOFI"
    ]
    
    def __init__(self):
        self.scan_results = []
        self.last_scan = None
    
    def scan_market(self, limit: int = 10, min_score: float = 60.0) -> List[Dict]:
        """
        Scan market for squeeze candidates
        Returns top N results above min_score
        """
        results = []
        
        for ticker in self.SCAN_UNIVERSE:
            try:
                score_data = self._analyze_ticker_for_scan(ticker)
                if score_data['score'] >= min_score:
                    results.append(score_data)
            except:
                continue
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        self.scan_results = results[:limit]
        self.last_scan = datetime.now()
        
        return self.scan_results
    
    def analyze_ticker(self, ticker: str) -> Dict:
        """
        Detailed analysis of single ticker
        Compares to GME pre-squeeze setup
        """
        return self._analyze_ticker_detailed(ticker)
    
    def refresh_scan(self):
        """Trigger full market rescan"""
        return self.scan_market(limit=50, min_score=50.0)
    
    # ==========================================
    # PRIVATE METHODS
    # ==========================================
    
    def _analyze_ticker_for_scan(self, ticker: str) -> Dict:
        """Quick analysis for scanner"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get metrics
            short_pct = info.get('shortPercentOfFloat', 0) * 100 if info.get('shortPercentOfFloat') else 0
            float_shares = info.get('floatShares', 1e9)
            avg_volume = info.get('averageVolume', 0)
            shares_short = info.get('sharesShort', 0)
            
            # Calculate score components
            si_score = min(100, short_pct * 2.5)  # Max at 40% SI
            float_score = 100 if float_shares < 50e6 else 50 if float_shares < 100e6 else 25
            dtc = shares_short / avg_volume if avg_volume > 0 else 0
            dtc_score = min(100, dtc * 20)  # Max at 5 DTC
            
            # Overall score
            score = (si_score * 0.5) + (float_score * 0.25) + (dtc_score * 0.25)
            
            # GME similarity (simple heuristic)
            gme_similarity = min(100, short_pct * 1.5 + float_score * 0.3)
            
            # Generate alerts
            alerts = []
            if short_pct > 30:
                alerts.append(f"SI: {short_pct:.1f}% - EXTREMELY HIGH")
            if float_shares < 50e6:
                alerts.append(f"Float: {float_shares/1e6:.1f}M - VERY LOW")
            if dtc > 3:
                alerts.append(f"Days to Cover: {dtc:.1f} - HIGH")
            
            return {
                "ticker": ticker,
                "score": round(score, 1),
                "gme_similarity": round(gme_similarity, 1),
                "metrics": {
                    "short_interest": round(short_pct, 1),
                    "float": float_shares,
                    "days_to_cover": round(dtc, 2),
                    "avg_volume": avg_volume
                },
                "alerts": alerts
            }
        except:
            return {
                "ticker": ticker,
                "score": 0,
                "gme_similarity": 0,
                "metrics": {},
                "alerts": []
            }
    
    def _analyze_ticker_detailed(self, ticker: str) -> Dict:
        """Detailed analysis with GME comparison"""
        quick_analysis = self._analyze_ticker_for_scan(ticker)
        
        # Add more detailed metrics
        quick_analysis['gme_comparison'] = {
            "setup_similarity": quick_analysis['gme_similarity'],
            "key_factors": [
                {"factor": "Short Interest", "match": "High" if quick_analysis['metrics'].get('short_interest', 0) > 20 else "Low"},
                {"factor": "Float Size", "match": "Similar" if quick_analysis['metrics'].get('float', 1e9) < 100e6 else "Different"},
                {"factor": "Community Interest", "match": "Growing"}
            ]
        }
        
        return quick_analysis

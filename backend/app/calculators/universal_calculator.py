"""
Universal Squeeze Calculator
Works for ANY ticker - generic squeeze metrics
"""

from datetime import datetime
from typing import Dict
import yfinance as yf

class UniversalCalculator:
    
    def calculate_probability(self, ticker: str) -> Dict:
        """
        Calculate squeeze probability for any ticker
        Uses generic metrics: SI, FTDs, gamma, volume
        """
        now = datetime.now()
        
        # Get metrics
        metrics = self.get_metrics(ticker)
        
        # Calculate component scores
        si_score = self._score_short_interest(metrics['short_interest'])
        ftd_score = self._score_ftds(metrics['ftd_volume'])
        gamma_score = self._score_gamma(metrics['gamma_exposure'])
        volume_score = self._score_volume(metrics['volume_ratio'])
        price_score = self._score_price_action(metrics['price_change_30d'])
        
        # Weighted probability
        weights = {
            'short': 0.30,
            'ftd': 0.25,
            'gamma': 0.20,
            'volume': 0.15,
            'price': 0.10
        }
        
        probability = (
            si_score * weights['short'] +
            ftd_score * weights['ftd'] +
            gamma_score * weights['gamma'] +
            volume_score * weights['volume'] +
            price_score * weights['price']
        )
        
        confidence = "HIGH" if probability >= 70 else "MODERATE" if probability >= 50 else "LOW"
        
        return {
            "ticker": ticker,
            "probability": round(probability, 1),
            "confidence": confidence,
            "breakdown": {
                "short_interest": round(si_score, 1),
                "ftd_accumulation": round(ftd_score, 1),
                "options_gamma": round(gamma_score, 1),
                "volume_volatility": round(volume_score, 1),
                "price_action": round(price_score, 1)
            },
            "active_cycles": [],
            "upcoming_convergences": [],
            "timestamp": now.isoformat()
        }
    
    def get_metrics(self, ticker: str) -> Dict:
        """Get raw squeeze metrics for ticker"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="3mo")
            
            # Extract metrics
            short_pct = info.get('shortPercentOfFloat', 0) * 100 if info.get('shortPercentOfFloat') else 0
            shares_short = info.get('sharesShort', 0)
            float_shares = info.get('floatShares', 1)
            avg_volume = info.get('averageVolume', 0)
            current_price = hist['Close'].iloc[-1] if not hist.empty else 0
            
            # Calculate volume ratio
            recent_volume = hist['Volume'].tail(5).mean() if not hist.empty else 0
            volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1.0
            
            # Calculate 30-day price change
            price_30d_ago = hist['Close'].iloc[0] if not hist.empty else current_price
            price_change = ((current_price - price_30d_ago) / price_30d_ago * 100) if price_30d_ago > 0 else 0
            
            # Days to cover
            dtc = (shares_short / avg_volume) if avg_volume > 0 else 0
            
            return {
                "short_interest": short_pct,
                "shares_short": shares_short,
                "float_shares": float_shares,
                "days_to_cover": dtc,
                "borrow_rate": 0,  # TODO: Fetch from external source
                "ftd_volume": 0,  # TODO: Fetch from SEC
                "gamma_exposure": 0,  # TODO: Calculate from options chain
                "volume_ratio": volume_ratio,
                "price_change_30d": price_change,
                "current_price": current_price
            }
        except:
            return self._default_metrics()
    
    def compare_tickers(self, ticker1: str, ticker2: str) -> Dict:
        """Compare squeeze metrics between two tickers"""
        metrics1 = self.get_metrics(ticker1)
        metrics2 = self.get_metrics(ticker2)
        prob1 = self.calculate_probability(ticker1)
        prob2 = self.calculate_probability(ticker2)
        
        return {
            "ticker1": ticker1,
            "ticker2": ticker2,
            "comparison": {
                "probability": {
                    ticker1: prob1['probability'],
                    ticker2: prob2['probability'],
                    "winner": ticker1 if prob1['probability'] > prob2['probability'] else ticker2
                },
                "short_interest": {
                    ticker1: metrics1['short_interest'],
                    ticker2: metrics2['short_interest'],
                    "winner": ticker1 if metrics1['short_interest'] > metrics2['short_interest'] else ticker2
                },
                "days_to_cover": {
                    ticker1: metrics1['days_to_cover'],
                    ticker2: metrics2['days_to_cover'],
                    "winner": ticker1 if metrics1['days_to_cover'] > metrics2['days_to_cover'] else ticker2
                }
            }
        }
    
    # ==========================================
    # SCORING FUNCTIONS
    # ==========================================
    
    def _score_short_interest(self, si_pct: float) -> float:
        """Score short interest (0-100)"""
        if si_pct >= 40:
            return 100
        elif si_pct >= 30:
            return 90
        elif si_pct >= 20:
            return 75
        elif si_pct >= 15:
            return 60
        elif si_pct >= 10:
            return 40
        else:
            return 20
    
    def _score_ftds(self, ftd_volume: float) -> float:
        """Score FTD accumulation (0-100)"""
        # TODO: Implement real FTD scoring
        return 50.0
    
    def _score_gamma(self, gamma_exposure: float) -> float:
        """Score gamma exposure (0-100)"""
        # TODO: Implement real gamma scoring
        return 50.0
    
    def _score_volume(self, volume_ratio: float) -> float:
        """Score volume increase (0-100)"""
        if volume_ratio >= 3.0:
            return 100
        elif volume_ratio >= 2.0:
            return 80
        elif volume_ratio >= 1.5:
            return 60
        elif volume_ratio >= 1.2:
            return 40
        else:
            return 20
    
    def _score_price_action(self, price_change: float) -> float:
        """Score price momentum (0-100)"""
        if price_change >= 50:
            return 100
        elif price_change >= 30:
            return 80
        elif price_change >= 15:
            return 60
        elif price_change >= 5:
            return 40
        elif price_change >= 0:
            return 30
        else:
            return 10
    
    def _default_metrics(self) -> Dict:
        """Return default metrics if fetch fails"""
        return {
            "short_interest": 0,
            "shares_short": 0,
            "float_shares": 0,
            "days_to_cover": 0,
            "borrow_rate": 0,
            "ftd_volume": 0,
            "gamma_exposure": 0,
            "volume_ratio": 1.0,
            "price_change_30d": 0,
            "current_price": 0
        }

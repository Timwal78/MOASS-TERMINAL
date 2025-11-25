"""
GME/AMC Specialist Calculator
Uses custom cycles: 214d pattern, T+35, 147-day, warrants, basket theory
"""

from datetime import datetime, timedelta
from typing import Dict, List
import yfinance as yf

class GMESpecialistCalculator:
    
    # Key dates
    ORIGIN_DATE = datetime(2024, 4, 25)  # Apr 25, 2024 - Pattern origin
    FIRST_REPEAT = datetime(2025, 11, 25)  # Nov 25, 2025 - First 214d repeat
    MOASS_2021 = datetime(2021, 1, 28)  # Jan 28, 2021 - Original MOASS
    
    # GME Warrants
    WARRANT_STRIKE = 32.00
    WARRANT_EXPIRATION = datetime(2026, 10, 30)
    TOTAL_WARRANTS = 59_000_000
    
    # Cycle lengths
    BASE_CYCLE_DAYS = 214
    COMPRESSION_RATIO = 0.64  # 7-4-1 fractal
    
    def __init__(self):
        self.cycle_data = {}
    
    def calculate_probability(self, ticker: str) -> Dict:
        """
        Calculate MOASS probability for GME/AMC
        Returns 0-100% with detailed breakdown
        """
        now = datetime.now()
        
        # Get current price
        price = self._get_current_price(ticker)
        
        # Calculate cycle scores
        cycle_score = self._calculate_cycle_convergence(now)
        warrant_score = self._calculate_warrant_proximity(price) if ticker == "GME" else 0
        ftd_score = self._estimate_ftd_pressure(ticker, now)
        gamma_score = self._estimate_gamma_exposure(ticker)
        short_score = self._estimate_short_pressure(ticker)
        sentiment_score = self._estimate_sentiment(ticker)
        
        # Weighted probability
        if ticker == "GME":
            weights = {
                'cycle': 0.30,
                'warrant': 0.15,
                'ftd': 0.20,
                'gamma': 0.15,
                'short': 0.10,
                'sentiment': 0.10
            }
            probability = (
                cycle_score * weights['cycle'] +
                warrant_score * weights['warrant'] +
                ftd_score * weights['ftd'] +
                gamma_score * weights['gamma'] +
                short_score * weights['short'] +
                sentiment_score * weights['sentiment']
            )
        else:  # AMC
            weights = {
                'cycle': 0.35,
                'ftd': 0.25,
                'gamma': 0.15,
                'short': 0.15,
                'sentiment': 0.10
            }
            probability = (
                cycle_score * weights['cycle'] +
                ftd_score * weights['ftd'] +
                gamma_score * weights['gamma'] +
                short_score * weights['short'] +
                sentiment_score * weights['sentiment']
            )
        
        # Determine confidence level
        if probability >= 70:
            confidence = "HIGH"
        elif probability >= 50:
            confidence = "MODERATE"
        else:
            confidence = "LOW"
        
        return {
            "ticker": ticker,
            "probability": round(probability, 1),
            "confidence": confidence,
            "breakdown": {
                "cycle_convergence": round(cycle_score, 1),
                "warrant_proximity": round(warrant_score, 1) if ticker == "GME" else None,
                "ftd_accumulation": round(ftd_score, 1),
                "options_gamma": round(gamma_score, 1),
                "short_interest": round(short_score, 1),
                "sentiment": round(sentiment_score, 1)
            },
            "active_cycles": self._get_active_cycles(now),
            "upcoming_convergences": self._get_upcoming_convergences(now),
            "timestamp": now.isoformat()
        }
    
    def get_upcoming_cycles(self, ticker: str) -> List[Dict]:
        """Get all upcoming cycle dates"""
        now = datetime.now()
        cycles = []
        
        # 214-day accelerating pattern
        pattern_cycles = self._calculate_214d_cycles()
        cycles.extend(pattern_cycles)
        
        # T+35 FTD cycles
        ftd_cycles = self._calculate_ftd35_cycles(now, days_ahead=90)
        cycles.extend(ftd_cycles)
        
        # 147-day cycles
        cycle_147 = self._calculate_147_cycles(now, days_ahead=180)
        cycles.extend(cycle_147)
        
        # OPEX dates
        opex_dates = self._calculate_opex_dates(now, quarters_ahead=4)
        cycles.extend(opex_dates)
        
        # Sort by date
        cycles.sort(key=lambda x: x['date'])
        
        return cycles
    
    def get_warrant_status(self) -> Dict:
        """Get GME warrant status"""
        price = self._get_current_price("GME")
        now = datetime.now()
        
        distance_to_itm = max(0, self.WARRANT_STRIKE - price)
        percent_to_itm = (distance_to_itm / price * 100) if price > 0 else 0
        days_to_expiration = (self.WARRANT_EXPIRATION - now).days
        
        # Estimate hedge ratio
        if price >= self.WARRANT_STRIKE:
            hedge_ratio = 0.70
        elif price >= 30:
            hedge_ratio = 0.40
        elif price >= 28:
            hedge_ratio = 0.20
        else:
            hedge_ratio = 0.05
        
        shares_to_hedge = int(self.TOTAL_WARRANTS * hedge_ratio)
        
        return {
            "current_price": round(price, 2),
            "strike_price": self.WARRANT_STRIKE,
            "distance_to_itm": round(distance_to_itm, 2),
            "percent_to_itm": round(percent_to_itm, 1),
            "days_to_expiration": days_to_expiration,
            "total_warrants": self.TOTAL_WARRANTS,
            "hedge_ratio": hedge_ratio,
            "shares_to_hedge": shares_to_hedge,
            "status": "ITM" if price >= self.WARRANT_STRIKE else "OTM"
        }
    
    def update_cycle_data(self, data: Dict):
        """Update cycle data from Pine Script webhook"""
        ticker = data['ticker']
        if ticker not in self.cycle_data:
            self.cycle_data[ticker] = []
        self.cycle_data[ticker].append(data)
    
    # ==========================================
    # PRIVATE HELPER METHODS
    # ==========================================
    
    def _get_current_price(self, ticker: str) -> float:
        """Get current stock price"""
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period="1d")
            if not data.empty:
                return float(data['Close'].iloc[-1])
            return 0.0
        except:
            # Fallback prices for demo
            return 20.50 if ticker == "GME" else 4.50
    
    def _calculate_cycle_convergence(self, now: datetime) -> float:
        """
        Calculate cycle convergence score (0-100)
        Higher when multiple cycles align
        """
        active_count = 0
        upcoming_count = 0
        
        # Check 214d pattern
        days_from_origin = (now - self.ORIGIN_DATE).days
        if self._is_214d_active(days_from_origin):
            active_count += 2  # Weight this heavily
        
        # Check if 214d cycle within 7 days
        next_214d = self._get_next_214d_date(days_from_origin)
        if next_214d and (next_214d - now).days <= 7:
            upcoming_count += 1
        
        # Check T+35
        ftd_position = days_from_origin % 35
        if ftd_position == 0:
            active_count += 1
        elif ftd_position >= 30:
            upcoming_count += 1
        
        # Check 147-day
        days_from_moass = (now - self.MOASS_2021).days
        c147_position = days_from_moass % 147
        if c147_position <= 3:
            active_count += 1
        elif c147_position >= 140:
            upcoming_count += 1
        
        # Check OPEX (3rd Friday of Mar/Jun/Sep/Dec)
        if self._is_opex_week(now):
            active_count += 1
        
        # Calculate score
        score = (active_count * 20) + (upcoming_count * 10)
        return min(100, score)
    
    def _is_214d_active(self, days_from_origin: int) -> bool:
        """Check if 214d pattern cycle is active"""
        current_length = self.BASE_CYCLE_DAYS
        total_days = 0
        
        for cycle_num in range(10):
            if cycle_num > 0:
                current_length = current_length * self.COMPRESSION_RATIO
            
            cycle_days = round(current_length)
            
            if total_days <= days_from_origin < total_days + cycle_days:
                # Check if within 3-day window of completion
                position_in_cycle = days_from_origin - total_days
                return position_in_cycle >= cycle_days - 3
            
            total_days += cycle_days
            
            if total_days > days_from_origin + 365:
                break
        
        return False
    
    def _get_next_214d_date(self, days_from_origin: int) -> datetime:
        """Get next 214d cycle completion date"""
        current_length = self.BASE_CYCLE_DAYS
        total_days = 0
        
        for cycle_num in range(10):
            if cycle_num > 0:
                current_length = current_length * self.COMPRESSION_RATIO
            
            cycle_days = round(current_length)
            total_days += cycle_days
            
            if total_days > days_from_origin:
                return self.ORIGIN_DATE + timedelta(days=total_days)
        
        return None
    
    def _calculate_214d_cycles(self) -> List[Dict]:
        """Calculate all 214d pattern cycles"""
        cycles = []
        now = datetime.now()
        
        current_length = self.BASE_CYCLE_DAYS
        current_date = self.ORIGIN_DATE
        
        for i in range(10):
            if i > 0:
                current_length = current_length * self.COMPRESSION_RATIO
            
            days = round(current_length)
            current_date = current_date + timedelta(days=days)
            
            if current_date > now and current_date < now + timedelta(days=365):
                cycles.append({
                    "type": "214d_pattern",
                    "name": f"214d Cycle #{i+1}",
                    "date": current_date,
                    "days_until": (current_date - now).days,
                    "cycle_length": days
                })
        
        return cycles
    
    def _calculate_ftd35_cycles(self, now: datetime, days_ahead: int) -> List[Dict]:
        """Calculate upcoming T+35 FTD cycles"""
        cycles = []
        days_from_origin = (now - self.ORIGIN_DATE).days
        
        current_position = days_from_origin % 35
        days_to_next = 35 - current_position if current_position != 0 else 0
        
        for i in range(days_ahead // 35 + 1):
            next_date = now + timedelta(days=days_to_next + (i * 35))
            if next_date < now + timedelta(days=days_ahead):
                cycles.append({
                    "type": "ftd35",
                    "name": "T+35 FTD Settlement",
                    "date": next_date,
                    "days_until": (next_date - now).days
                })
        
        return cycles
    
    def _calculate_147_cycles(self, now: datetime, days_ahead: int) -> List[Dict]:
        """Calculate upcoming 147-day cycles"""
        cycles = []
        days_from_moass = (now - self.MOASS_2021).days
        
        current_position = days_from_moass % 147
        days_to_next = 147 - current_position if current_position != 0 else 0
        
        for i in range(days_ahead // 147 + 1):
            next_date = now + timedelta(days=days_to_next + (i * 147))
            if next_date < now + timedelta(days=days_ahead):
                cycles.append({
                    "type": "147day",
                    "name": "147-Day Major Cycle",
                    "date": next_date,
                    "days_until": (next_date - now).days
                })
        
        return cycles
    
    def _calculate_opex_dates(self, now: datetime, quarters_ahead: int) -> List[Dict]:
        """Calculate upcoming quarterly OPEX dates"""
        cycles = []
        opex_months = [3, 6, 9, 12]
        
        for year_offset in range(2):
            for month in opex_months:
                year = now.year + year_offset
                opex_date = self._get_third_friday(year, month)
                
                if opex_date > now and opex_date < now + timedelta(days=quarters_ahead * 90):
                    cycles.append({
                        "type": "opex",
                        "name": "Quarterly OPEX",
                        "date": opex_date,
                        "days_until": (opex_date - now).days
                    })
        
        return cycles
    
    def _get_third_friday(self, year: int, month: int) -> datetime:
        """Get third Friday of month"""
        date = datetime(year, month, 1)
        fridays = 0
        
        while fridays < 3:
            if date.weekday() == 4:  # Friday
                fridays += 1
            if fridays < 3:
                date = date + timedelta(days=1)
        
        return date
    
    def _is_opex_week(self, date: datetime) -> bool:
        """Check if date is in OPEX week"""
        if date.month not in [3, 6, 9, 12]:
            return False
        
        third_friday = self._get_third_friday(date.year, date.month)
        days_diff = abs((date - third_friday).days)
        
        return days_diff <= 3
    
    def _calculate_warrant_proximity(self, price: float) -> float:
        """Calculate warrant proximity score (0-100)"""
        if price >= self.WARRANT_STRIKE:
            return 100.0
        
        distance = self.WARRANT_STRIKE - price
        percent_away = (distance / self.WARRANT_STRIKE) * 100
        
        # Score decreases as we get further from strike
        score = max(0, 100 - (percent_away * 2))
        return score
    
    def _estimate_ftd_pressure(self, ticker: str, now: datetime) -> float:
        """Estimate FTD accumulation pressure (0-100)"""
        # TODO: Fetch real FTD data from SEC
        # For now, use cycle-based estimation
        
        days_from_origin = (now - self.ORIGIN_DATE).days
        ftd_position = days_from_origin % 35
        
        # Pressure builds as we approach T+35
        if ftd_position < 5:
            return 90.0
        elif ftd_position < 10:
            return 70.0
        elif ftd_position > 30:
            return 80.0
        else:
            return 50.0
    
    def _estimate_gamma_exposure(self, ticker: str) -> float:
        """Estimate options gamma exposure (0-100)"""
        # TODO: Implement real gamma calculation from options chain
        # For now, return moderate score
        return 65.0
    
    def _estimate_short_pressure(self, ticker: str) -> float:
        """Estimate short interest pressure (0-100)"""
        # TODO: Fetch real short interest from FINRA
        # For now, return high score for GME/AMC
        return 75.0 if ticker == "GME" else 70.0
    
    def _estimate_sentiment(self, ticker: str) -> float:
        """Estimate social sentiment (0-100)"""
        # TODO: Implement Reddit/Twitter sentiment analysis
        # For now, return bullish score
        return 80.0
    
    def _get_active_cycles(self, now: datetime) -> List[Dict]:
        """Get currently active cycles"""
        active = []
        
        # Check 214d pattern
        days_from_origin = (now - self.ORIGIN_DATE).days
        if self._is_214d_active(days_from_origin):
            active.append({
                "type": "214d_pattern",
                "status": "ACTIVE NOW",
                "name": "214-Day Accelerating Pattern"
            })
        
        # Check T+35
        ftd_position = days_from_origin % 35
        if ftd_position == 0:
            active.append({
                "type": "ftd35",
                "status": "ACTIVE NOW",
                "name": "T+35 FTD Settlement"
            })
        
        # Check 147-day
        days_from_moass = (now - self.MOASS_2021).days
        c147_position = days_from_moass % 147
        if c147_position <= 3:
            active.append({
                "type": "147day",
                "status": "ACTIVE NOW",
                "name": "147-Day Major Cycle"
            })
        
        # Check OPEX
        if self._is_opex_week(now):
            active.append({
                "type": "opex",
                "status": "ACTIVE NOW",
                "name": "Quarterly OPEX"
            })
        
        return active
    
    def _get_upcoming_convergences(self, now: datetime) -> List[Dict]:
        """Detect upcoming cycle convergences"""
        convergences = []
        
        # Get all cycles
        all_cycles = self.get_upcoming_cycles("GME")
        
        # Group by date (within 3-day window)
        date_groups = {}
        for cycle in all_cycles:
            cycle_date = cycle['date']
            date_key = cycle_date.strftime('%Y-%m-%d')
            
            # Find if any existing group is within 3 days
            found_group = False
            for group_key in list(date_groups.keys()):
                group_date = datetime.strptime(group_key, '%Y-%m-%d')
                if abs((cycle_date - group_date).days) <= 3:
                    date_groups[group_key].append(cycle)
                    found_group = True
                    break
            
            if not found_group:
                date_groups[date_key] = [cycle]
        
        # Find convergences (2+ cycles)
        for date_key, cycles in date_groups.items():
            if len(cycles) >= 2:
                convergences.append({
                    "date": date_key,
                    "days_until": cycles[0]['days_until'],
                    "cycle_count": len(cycles),
                    "cycles": [c['name'] for c in cycles],
                    "pressure": "MEGA" if len(cycles) >= 3 else "HIGH"
                })
        
        return sorted(convergences, key=lambda x: x['days_until'])[:5]

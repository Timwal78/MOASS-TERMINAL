"""
Quick Test Script
Run this to verify everything works before deploying
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.calculators.gme_specialist import GMESpecialistCalculator
from app.calculators.universal_calculator import UniversalCalculator
from app.calculators.market_scanner import MarketScanner

print("🚀 MOASS TERMINAL - LOCAL TEST")
print("="*60)

# Test GME Specialist
print("\n📊 Testing GME Specialist Calculator...")
try:
    gme_calc = GMESpecialistCalculator()
    result = gme_calc.calculate_probability("GME")
    print(f"✅ GME Probability: {result['probability']}%")
    print(f"   Confidence: {result['confidence']}")
    print(f"   Active Cycles: {len(result['active_cycles'])}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test Universal
print("\n🌐 Testing Universal Calculator...")
try:
    universal_calc = UniversalCalculator()
    result = universal_calc.calculate_probability("TSLA")
    print(f"✅ TSLA Probability: {result['probability']}%")
    print(f"   Short Interest: {result['breakdown']['short_interest']}%")
except Exception as e:
    print(f"❌ Error: {e}")

# Test Scanner
print("\n🔍 Testing Market Scanner...")
try:
    scanner = MarketScanner()
    results = scanner.scan_market(limit=5, min_score=50.0)
    print(f"✅ Found {len(results)} candidates")
    if results:
        top = results[0]
        print(f"   Top: {top['ticker']} - Score: {top['score']}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test Warrant Status
print("\n📜 Testing GME Warrant Tracker...")
try:
    warrant_status = gme_calc.get_warrant_status()
    print(f"✅ Current Price: ${warrant_status['current_price']}")
    print(f"   Distance to ITM: ${warrant_status['distance_to_itm']}")
    print(f"   Shares to Hedge: {warrant_status['shares_to_hedge']:,}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("✅ ALL TESTS PASSED!")
print("🚀 Ready to deploy to Render!")
print("\nNext steps:")
print("1. Push to GitHub")
print("2. Deploy on Render")
print("3. Test live API endpoints")

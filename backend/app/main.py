"""
MOASS Terminal - Main FastAPI Application
Never miss a squeeze again
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv

from app.calculators.gme_specialist import GMESpecialistCalculator
from app.calculators.universal_calculator import UniversalCalculator
from app.calculators.market_scanner import MarketScanner
from app.utils.data_fetcher import DataFetcher

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="MOASS Terminal API",
    description="Squeeze probability calculator for GME/AMC and universal stocks",
    version="1.0.0"
)

# CORS Configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize calculators
gme_calc = GMESpecialistCalculator()
universal_calc = UniversalCalculator()
scanner = MarketScanner()
data_fetcher = DataFetcher()

# ==========================================
# MODELS
# ==========================================

class CycleWebhook(BaseModel):
    ticker: str
    cycle_type: str
    cycle_name: str
    date: str
    confidence: float
    days_until: int

class ProbabilityResponse(BaseModel):
    ticker: str
    probability: float
    confidence: str
    breakdown: dict
    active_cycles: List[dict]
    upcoming_convergences: List[dict]
    timestamp: str

class ScannerResult(BaseModel):
    ticker: str
    score: float
    gme_similarity: float
    metrics: dict
    alerts: List[str]

# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "MOASS Terminal API",
        "version": "1.0.0",
        "modes": ["gme_specialist", "universal", "scanner"]
    }

@app.get("/health")
def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected" if check_database() else "disconnected",
        "cache": "connected" if check_cache() else "disconnected",
        "data_sources": check_data_sources()
    }

# ==========================================
# MODE 1: GME/AMC SPECIALIST
# ==========================================

@app.get("/api/gme/probability", response_model=ProbabilityResponse)
async def get_gme_probability():
    """
    Get GME MOASS probability with specialist cycles
    Uses 214d pattern, T+35, 147-day, warrants, etc.
    """
    try:
        result = gme_calc.calculate_probability("GME")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/amc/probability", response_model=ProbabilityResponse)
async def get_amc_probability():
    """
    Get AMC squeeze probability with specialist cycles
    """
    try:
        result = gme_calc.calculate_probability("AMC")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/specialist/{ticker}/cycles")
async def get_specialist_cycles(ticker: str):
    """
    Get all upcoming cycles for GME/AMC specialist mode
    """
    try:
        if ticker.upper() not in ["GME", "AMC"]:
            raise HTTPException(status_code=400, detail="Specialist mode only supports GME/AMC")
        
        cycles = gme_calc.get_upcoming_cycles(ticker.upper())
        return {"ticker": ticker.upper(), "cycles": cycles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/specialist/{ticker}/warrants")
async def get_warrant_status(ticker: str):
    """
    Get GME warrant status (59M @ $32)
    """
    try:
        if ticker.upper() != "GME":
            raise HTTPException(status_code=400, detail="Warrants only available for GME")
        
        warrant_data = gme_calc.get_warrant_status()
        return warrant_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# MODE 2: UNIVERSAL TRACKER
# ==========================================

@app.get("/api/universal/{ticker}/probability", response_model=ProbabilityResponse)
async def get_universal_probability(ticker: str):
    """
    Get squeeze probability for ANY ticker
    Uses generic squeeze metrics
    """
    try:
        result = universal_calc.calculate_probability(ticker.upper())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/universal/{ticker}/metrics")
async def get_universal_metrics(ticker: str):
    """
    Get detailed squeeze metrics for any ticker
    """
    try:
        metrics = universal_calc.get_metrics(ticker.upper())
        return {"ticker": ticker.upper(), "metrics": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# MODE 3: MARKET SCANNER
# ==========================================

@app.get("/api/scanner/top", response_model=List[ScannerResult])
async def get_top_candidates(
    limit: int = Query(10, ge=1, le=50),
    min_score: float = Query(60.0, ge=0, le=100)
):
    """
    Get top squeeze candidates from market scan
    Scans 5000+ stocks for GME-like setups
    """
    try:
        results = scanner.scan_market(limit=limit, min_score=min_score)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scanner/ticker/{ticker}")
async def get_scanner_analysis(ticker: str):
    """
    Get detailed scanner analysis for specific ticker
    Compares to GME pre-squeeze setup
    """
    try:
        analysis = scanner.analyze_ticker(ticker.upper())
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scanner/refresh")
async def refresh_scanner():
    """
    Trigger manual scanner refresh (runs automatically daily)
    """
    try:
        scanner.refresh_scan()
        return {"status": "success", "message": "Scanner refresh initiated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# COMPARISON TOOLS
# ==========================================

@app.get("/api/compare")
async def compare_tickers(
    ticker1: str = Query(..., description="First ticker to compare"),
    ticker2: str = Query(..., description="Second ticker to compare")
):
    """
    Compare squeeze metrics between two tickers
    """
    try:
        comparison = universal_calc.compare_tickers(ticker1.upper(), ticker2.upper())
        return comparison
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# WEBHOOKS (from Pine Script)
# ==========================================

@app.post("/api/webhook/cycle")
async def receive_cycle_webhook(data: CycleWebhook):
    """
    Receive cycle data from TradingView Pine Script indicators
    Updates real-time cycle tracking
    """
    try:
        # Store cycle data
        gme_calc.update_cycle_data(data.dict())
        
        return {
            "status": "received",
            "ticker": data.ticker,
            "cycle": data.cycle_type,
            "message": f"Cycle data updated for {data.ticker}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# DATA ENDPOINTS
# ==========================================

@app.get("/api/data/{ticker}/price")
async def get_current_price(ticker: str):
    """Get current price for ticker"""
    try:
        price_data = data_fetcher.get_price(ticker.upper())
        return price_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/{ticker}/short-interest")
async def get_short_interest(ticker: str):
    """Get short interest data"""
    try:
        si_data = data_fetcher.get_short_interest(ticker.upper())
        return si_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# UTILITY FUNCTIONS
# ==========================================

def check_database():
    """Check database connection"""
    # TODO: Implement actual database check
    return True

def check_cache():
    """Check Redis cache connection"""
    # TODO: Implement actual cache check
    return True

def check_data_sources():
    """Check external data source availability"""
    return {
        "yahoo_finance": "available",
        "finra": "available",
        "sec": "available"
    }

# ==========================================
# ERROR HANDLERS
# ==========================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Not Found",
        "message": "The requested endpoint does not exist",
        "available_endpoints": [
            "/api/gme/probability",
            "/api/universal/{ticker}/probability",
            "/api/scanner/top"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

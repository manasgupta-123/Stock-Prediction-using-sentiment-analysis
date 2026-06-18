"""
main.py
FastAPI entry point for Quant Sentinel AI.

Runs all 6 agents concurrently using asyncio.gather() and returns
aggregated results to the React frontend.

Usage:
    uvicorn main:app --reload --port 8000
"""

import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from agents.technical   import run_technical_agent
from agents.fundamental import run_fundamental_agent
from agents.sentiment   import run_sentiment_agent
from agents.prediction  import run_prediction_agent
from agents.analyst     import run_analyst_agent
from agents.risk        import run_risk_agent

app = FastAPI(
    title="Quant Sentinel AI",
    description="Multi-agent AI stock assistant for Indian markets (NSE/BSE)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_methods=["GET"],
    allow_headers=["*"],
)

# --- Agent weights (must sum to 1.0) ---
WEIGHTS = {
    "technical":   0.20,
    "fundamental": 0.20,
    "sentiment":   0.15,
    "prediction":  0.20,
    "analyst":     0.15,
    "risk":        0.10,
}

BUY_THRESHOLD  = 65
HOLD_THRESHOLD = 45


@app.get("/")
async def root():
    return {"status": "ok", "message": "Quant Sentinel AI backend running"}


@app.get("/analyse")
async def analyse(symbol: str):
    """
    Run all 6 AI agents concurrently for a given NSE/BSE symbol.

    Query param:
        symbol  - e.g. RELIANCE, TCS, INFY

    Returns:
        JSON object with agent outputs + Decision Engine result
    """
    symbol = symbol.upper().strip()
    if not symbol:
        raise HTTPException(status_code=400, detail="symbol is required")

    try:
        # Run all agents in parallel
        tech, fund, sent, pred, anl, risk = await asyncio.gather(
            run_technical_agent(symbol),
            run_fundamental_agent(symbol),
            run_sentiment_agent(symbol),
            run_prediction_agent(symbol),
            run_analyst_agent(symbol),
            run_risk_agent(symbol),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

    # Decision Engine — weighted aggregation
    total = round(
        tech["score"]  * WEIGHTS["technical"]   +
        fund["score"]  * WEIGHTS["fundamental"] +
        sent["score"]  * WEIGHTS["sentiment"]   +
        pred["score"]  * WEIGHTS["prediction"]  +
        anl["score"]   * WEIGHTS["analyst"]     +
        risk["score"]  * WEIGHTS["risk"]
    )
    recommendation = "BUY" if total >= BUY_THRESHOLD else "HOLD" if total >= HOLD_THRESHOLD else "SELL"

    return {
        "symbol":        symbol,
        "technical":     tech,
        "fundamental":   fund,
        "sentiment":     sent,
        "prediction":    pred,
        "analyst":       anl,
        "risk":          risk,
        "total":         total,
        "recommendation": recommendation,
        "weights":       WEIGHTS,
    }

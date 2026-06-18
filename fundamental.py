"""
agents/fundamental.py
Fundamental Analysis Agent

Extracts and evaluates key financial ratios:
  - P/E ratio (Price-to-Earnings)
  - ROE (Return on Equity)
  - Debt-to-Equity ratio
  - EPS (Earnings Per Share)

Benchmarks are calibrated for Indian market (NSE/BSE) norms.
Data source: Yahoo Finance via yfinance
"""

import asyncio
import yfinance as yf


# Indian market benchmarks
PE_ATTRACTIVE_THRESHOLD   = 25.0
ROE_STRONG_THRESHOLD      = 20.0
DEBT_LOW_THRESHOLD        = 1.0


async def run_fundamental_agent(symbol: str) -> dict:
    """
    Fetch fundamental ratios from Yahoo Finance and score them against
    Indian market benchmarks.

    Returns:
        dict with keys: pe, roe, debt, eps, score, outlook
    """
    loop = asyncio.get_event_loop()

    def _fetch():
        ticker = yf.Ticker(f"{symbol}.NS")
        info   = ticker.info
        return info

    info = await loop.run_in_executor(None, _fetch)

    pe   = round(float(info.get("trailingPE",          25.0)), 2)
    roe  = round(float(info.get("returnOnEquity",      0.15)) * 100, 2)
    debt = round(float(info.get("debtToEquity",        50.0)) / 100, 2)
    eps  = round(float(info.get("trailingEps",         50.0)), 2)

    score = round(
        ((80 if pe   < PE_ATTRACTIVE_THRESHOLD else 40) +
         (85 if roe  > ROE_STRONG_THRESHOLD    else 50) +
         (80 if debt < DEBT_LOW_THRESHOLD       else 35)) / 3
    )

    outlook = "Strong" if score > 65 else "Moderate" if score > 45 else "Weak"

    return {
        "pe":      pe,
        "roe":     roe,
        "debt":    debt,
        "eps":     eps,
        "score":   score,
        "outlook": outlook,
    }

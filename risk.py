"""
agents/risk.py
Risk Management Agent

Calculates:
  - Volatility  : annualised standard deviation of daily returns
  - Beta        : correlation with Nifty 50 index (^NSEI)
  - Stop loss   : current price × 0.93 (−7% threshold)
  - Risk level  : Low / Medium / High based on volatility
  - Score       : inverse risk metric (high risk → lower score)
"""

import asyncio
import numpy as np
import yfinance as yf


STOP_LOSS_FACTOR = 0.93   # −7% from current price


async def run_risk_agent(symbol: str) -> dict:
    """
    Compute volatility, beta, and stop-loss for the given symbol.

    Returns:
        dict with keys: volatility, beta, stopLoss, score, level
    """
    loop = asyncio.get_event_loop()

    def _fetch():
        import pandas as pd
        stock_data = yf.download(f"{symbol}.NS", period="1y", auto_adjust=True)["Close"]
        nifty_data = yf.download("^NSEI",        period="1y", auto_adjust=True)["Close"]

        stock_ret = stock_data.pct_change().dropna()
        nifty_ret = nifty_data.pct_change().dropna()

        # Align on common dates
        common = stock_ret.index.intersection(nifty_ret.index)
        s = stock_ret.loc[common]
        n = nifty_ret.loc[common]

        volatility = round(float(s.std() * np.sqrt(252) * 100), 2)

        cov      = np.cov(s, n)[0][1]
        var_nifty = float(n.var())
        beta     = round(cov / var_nifty if var_nifty != 0 else 1.0, 2)

        current_price = float(stock_data.iloc[-1])
        stop_loss     = round(current_price * STOP_LOSS_FACTOR, 2)

        return volatility, beta, stop_loss, current_price

    volatility, beta, stop_loss, _ = await loop.run_in_executor(None, _fetch)

    score = round(100 - volatility * 15 - (15 if beta > 1.2 else 5))
    score = max(0, min(100, score))
    level = "High" if volatility > 2.5 else "Medium" if volatility > 1.5 else "Low"

    return {
        "volatility": volatility,
        "beta":       beta,
        "stopLoss":   stop_loss,
        "score":      score,
        "level":      level,
    }

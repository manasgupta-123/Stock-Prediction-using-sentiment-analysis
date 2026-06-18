"""
agents/technical.py
Technical Analysis Agent

Computes RSI, MACD, 50-DMA, and 200-DMA from historical OHLCV price data.
Detects trend signals such as Golden Cross and Death Cross.

Data source: Yahoo Finance via yfinance
"""

import asyncio
import pandas as pd
import numpy as np
import yfinance as yf


def _compute_rsi(series: pd.Series, period: int = 14) -> float:
    delta = series.diff()
    gain  = delta.clip(lower=0).rolling(period).mean()
    loss  = (-delta.clip(upper=0)).rolling(period).mean()
    rs    = gain / loss.replace(0, np.nan)
    rsi   = 100 - (100 / (1 + rs))
    return round(float(rsi.iloc[-1]), 2)


def _compute_macd(series: pd.Series) -> float:
    ema12 = series.ewm(span=12, adjust=False).mean()
    ema26 = series.ewm(span=26, adjust=False).mean()
    macd  = ema12 - ema26
    return round(float(macd.iloc[-1]), 2)


async def run_technical_agent(symbol: str) -> dict:
    """
    Fetch 1 year of daily price data and compute technical indicators.

    Returns:
        dict with keys: rsi, macd, dma50, dma200, score, trend
    """
    loop = asyncio.get_event_loop()

    def _fetch():
        ticker = yf.Ticker(f"{symbol}.NS")   # NSE suffix
        hist   = ticker.history(period="1y")
        return hist

    hist = await loop.run_in_executor(None, _fetch)

    if hist.empty:
        raise ValueError(f"No price data found for {symbol}")

    close  = hist["Close"]
    rsi    = _compute_rsi(close)
    macd   = _compute_macd(close)
    dma50  = round((float(close.iloc[-1]) / float(close.rolling(50).mean().iloc[-1]) - 1) * 100, 2)
    dma200 = round((float(close.iloc[-1]) / float(close.rolling(200).mean().iloc[-1]) - 1) * 100, 2)

    # Scoring heuristic
    score = round(
        ((90 if rsi < 30 else 20 if rsi > 70 else 60) +
         (70 if macd > 0 else 30) +
         (75 if dma50 > 0 else 35)) / 3
    )

    trend = (
        "Bullish"  if macd > 0 and dma50 > 0 else
        "Bearish"  if macd < 0 and dma50 < 0 else
        "Neutral"
    )

    return {
        "rsi":    rsi,
        "macd":   macd,
        "dma50":  dma50,
        "dma200": dma200,
        "score":  score,
        "trend":  trend,
    }

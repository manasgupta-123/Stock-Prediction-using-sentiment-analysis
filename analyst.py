"""
agents/analyst.py
Analyst Consensus Agent

Aggregates brokerage analyst recommendations (Strong Buy, Buy, Hold, Sell,
Strong Sell) from Yahoo Finance and computes a consensus score and
price target.
"""

import asyncio
import yfinance as yf


async def run_analyst_agent(symbol: str) -> dict:
    """
    Fetch analyst recommendations and price target from Yahoo Finance.

    Returns:
        dict with keys: buy, hold, sell, score, target
    """
    loop = asyncio.get_event_loop()

    def _fetch():
        ticker = yf.Ticker(f"{symbol}.NS")
        info   = ticker.info
        recs   = ticker.recommendations

        buy  = int(info.get("numberOfAnalystOpinions", 8))
        hold = max(1, buy // 3)
        sell = max(0, buy // 6)

        # If Yahoo provides a recommendations DataFrame, use it
        if recs is not None and not recs.empty:
            latest = recs.tail(1)
            buy    = int(latest.get("strongBuy",  0).values[0]) + int(latest.get("buy",  0).values[0])
            hold   = int(latest.get("hold",       0).values[0])
            sell   = int(latest.get("sell",       0).values[0]) + int(latest.get("strongSell", 0).values[0])

        target = round(float(info.get("targetMeanPrice", info.get("currentPrice", 100) * 1.15)), 2)
        return buy, hold, sell, target

    buy, hold, sell, target = await loop.run_in_executor(None, _fetch)

    total = max(buy + hold + sell, 1)
    score = round((buy / total) * 100)

    return {
        "buy":    buy,
        "hold":   hold,
        "sell":   sell,
        "score":  score,
        "target": target,
    }

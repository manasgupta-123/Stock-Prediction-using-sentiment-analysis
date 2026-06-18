# API Reference

Base URL: `http://localhost:8000`

---

## GET `/`

Health check.

**Response:**
```json
{ "status": "ok", "message": "Quant Sentinel AI backend running" }
```

---

## GET `/analyse`

Run all 6 AI agents for a given NSE/BSE stock symbol.

**Query parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `symbol` | string | yes | NSE stock symbol e.g. `RELIANCE`, `TCS` |

**Example request:**
```
GET /analyse?symbol=RELIANCE
```

**Example response:**
```json
{
  "symbol": "RELIANCE",
  "technical": {
    "rsi": 54.2,
    "macd": 1.8,
    "dma50": 2.1,
    "dma200": -0.3,
    "score": 65,
    "trend": "Bullish"
  },
  "fundamental": {
    "pe": 22.4,
    "roe": 18.7,
    "debt": 0.6,
    "eps": 98.5,
    "score": 72,
    "outlook": "Strong"
  },
  "sentiment": {
    "positive": 48.0,
    "negative": 18.0,
    "neutral": 34.0,
    "score": 60,
    "newsCount": 24
  },
  "prediction": {
    "days": ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"],
    "prices": [2861.0, 2874.5, 2889.0, 2901.0, 2915.0],
    "score": 58,
    "confidence": 74.3
  },
  "analyst": {
    "buy": 9,
    "hold": 3,
    "sell": 1,
    "score": 69,
    "target": 3100.0
  },
  "risk": {
    "volatility": 1.8,
    "beta": 1.05,
    "stopLoss": 2648.0,
    "score": 68,
    "level": "Medium"
  },
  "total": 65,
  "recommendation": "BUY",
  "weights": {
    "technical": 0.20,
    "fundamental": 0.20,
    "sentiment": 0.15,
    "prediction": 0.20,
    "analyst": 0.15,
    "risk": 0.10
  }
}
```

**Decision Engine thresholds:**

| Score | Recommendation |
|---|---|
| ≥ 65 | BUY |
| 45 – 64 | HOLD |
| < 45 | SELL |

**Error responses:**

| Code | Meaning |
|---|---|
| 400 | Missing or empty symbol parameter |
| 500 | Agent execution failed (data fetch error, model error) |

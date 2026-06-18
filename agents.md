# AI Agents

Each agent is an independent async module in `backend/agents/`. All agents accept a stock `symbol` string and return a dict containing a `score` (0–100) plus agent-specific fields.

---

## 1. Technical Agent (`technical.py`)

Computes classic technical indicators from 1 year of daily OHLCV data.

| Indicator | Description |
|---|---|
| RSI (14-day) | Relative Strength Index — oversold <30, overbought >70 |
| MACD | 12/26 EMA crossover — positive = bullish momentum |
| 50-DMA | % deviation of current price from 50-day moving average |
| 200-DMA | % deviation from 200-day moving average |

**Golden Cross** is flagged when the 50-DMA crosses above the 200-DMA.
**Death Cross** is flagged when the 50-DMA crosses below the 200-DMA.

**Score formula:**
```
score = mean(rsi_score, macd_score, dma50_score)
  rsi_score  = 90 if RSI<30 else 20 if RSI>70 else 60
  macd_score = 70 if MACD>0 else 30
  dma50_score = 75 if above 50-DMA else 35
```

---

## 2. Fundamental Agent (`fundamental.py`)

Evaluates financial ratios against Indian market benchmarks.

| Ratio | Benchmark | Source |
|---|---|---|
| P/E ratio | < 25 = attractive | Yahoo Finance `trailingPE` |
| ROE | > 20% = strong | Yahoo Finance `returnOnEquity` |
| Debt/Equity | < 1 = low leverage | Yahoo Finance `debtToEquity` |
| EPS | higher = better | Yahoo Finance `trailingEps` |

---

## 3. Sentiment Agent (`sentiment.py`)

Uses **FinBERT** (`ProsusAI/finbert`) to classify financial news headlines into positive, neutral, or negative sentiment.

**Pipeline:**
1. Fetch headlines from RSS feeds (Economic Times, Business Insider)
2. Filter by stock symbol name
3. Run FinBERT classification on each headline
4. Aggregate percentages

**Score formula:**
```
score = positive_pct × 0.9 + neutral_pct × 0.5
```

---

## 4. Prediction Agent (`prediction.py`)

Implements a **Bidirectional LSTM with Attention Mechanism** for short-term price forecasting.

**Model architecture:**
```
Input (60-day sequence) →
Bi-LSTM (64 units, 2 layers) →
Attention Layer →
Fully Connected →
Output (5-day forecast)
```

**Training:**
- Uses 1 year of daily closing prices
- Normalised with MinMaxScaler
- 60-day lookback window
- Trained for 20 epochs per request (persist weights in production)

**Confidence** is derived from the final training loss.

---

## 5. Analyst Consensus Agent (`analyst.py`)

Aggregates brokerage analyst ratings from Yahoo Finance.

Combines Strong Buy + Buy into the `buy` count, and Strong Sell + Sell into `sell`.

**Score formula:**
```
score = (buy_count / total_ratings) × 100
```

Also surfaces the analyst **mean price target** as an upside/downside signal.

---

## 6. Risk Management Agent (`risk.py`)

Quantifies downside risk using volatility and market correlation.

| Metric | Formula |
|---|---|
| Volatility (σ) | Annualised std dev of daily returns × √252 |
| Beta | Covariance(stock, Nifty50) / Variance(Nifty50) |
| Stop loss | Current price × 0.93 (−7% threshold) |

**Risk level:**
- Low: σ < 1.5%
- Medium: 1.5% ≤ σ < 2.5%
- High: σ ≥ 2.5%

**Score formula** (higher score = lower risk):
```
score = 100 − volatility × 15 − (15 if beta > 1.2 else 5)
```

# 📈 Quant Sentinel AI

**An AI-powered multi-agent stock analysis assistant for Indian markets (NSE/BSE)**

> Minor Project — Bachelor of Technology (ECE), Jaypee Institute of Information Technology, Noida (2026)
> Submitted by: Shreyans Kalantagdiya · Sarthak Sharma · Sresth Yadav
> Guided by: Prof. Megha Agarwal

---

## 🧠 Overview

Quant Sentinel AI is a decision-support system that runs **6 specialized AI agents in parallel** to analyse stocks and produce explainable BUY / HOLD / SELL recommendations. It is designed specifically for the Indian stock market (NSE/BSE) and prioritises transparency, modularity, and retail investor accessibility.

Traditional trading tools rely on a single lens — usually technical indicators or historical price alone. Quant Sentinel integrates:

- Real-time sentiment from financial news (via FinBERT)
- Short-term price prediction via Bidirectional LSTM with attention
- Technical indicators (RSI, MACD, DMA crossovers)
- Fundamental ratios benchmarked to Indian market norms
- Analyst consensus aggregation
- Volatility-aware risk management

All agent outputs are combined in a **centralized Decision Engine** using weighted scoring to produce a single, interpretable recommendation.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   React Frontend                    │
│         (Dashboard · Charts · Agent Cards)          │
└──────────────────────┬──────────────────────────────┘
                       │ REST API (JSON)
┌──────────────────────▼──────────────────────────────┐
│              FastAPI Backend (AsyncIO)              │
│         Orchestrates all agents in parallel         │
└──┬──────┬──────┬──────┬──────┬──────┬──────────────┘
   │      │      │      │      │      │
   ▼      ▼      ▼      ▼      ▼      ▼
 Tech  Fund  Sent  Pred  Anl  Risk    ← 6 Agents
Agent Agent Agent Agent Agent Agent
   │      │      │      │      │      │
   └──────┴──────┴──────┴──────┴──────┘
                       │
          ┌────────────▼────────────┐
          │     Decision Engine     │
          │   Weighted Aggregation  │
          │   BUY / HOLD / SELL     │
          └─────────────────────────┘
```

---

## 🤖 The 6 AI Agents

| Agent | Responsibility | Weight |
|---|---|---|
| **Technical** | RSI, MACD, 50/200-DMA, trend signals | 20% |
| **Fundamental** | P/E, ROE, Debt/Equity, EPS vs benchmarks | 20% |
| **Sentiment** | FinBERT NLP on financial RSS news | 15% |
| **Prediction** | Bi-LSTM + attention, 5-day price forecast | 20% |
| **Analyst Consensus** | Brokerage Buy/Hold/Sell aggregation | 15% |
| **Risk Management** | Volatility, Beta, stop-loss, position sizing | 10% |

---

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- Python 3.10+
- pip / virtualenv

### Frontend setup

```bash
cd frontend
npm install
npm run dev
```

### Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open `http://localhost:5173` — the frontend proxies API calls to `http://localhost:8000`.

---

## 📁 Project Structure

```
quant-sentinel-ai/
├── README.md
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── data/
│       │   └── stocks.js           # Stock constants & mock data generator
│       ├── utils/
│       │   └── scoring.js          # Decision engine & score helpers
│       ├── hooks/
│       │   └── useAgentAnalysis.js # Async analysis hook
│       └── components/
│           ├── Dashboard.jsx       # Main layout & tab controller
│           ├── StockPicker.jsx     # Stock selection grid
│           ├── SummaryBar.jsx      # Score + recommendation header
│           ├── OverviewTab.jsx     # Score grid + reasoning bars
│           ├── AgentsTab.jsx       # 6 agent cards
│           ├── PredictionTab.jsx   # Forecast chart + risk table
│           ├── AgentCard.jsx       # Reusable agent card wrapper
│           ├── ScoreRing.jsx       # SVG circular score indicator
│           ├── MiniBarChart.jsx    # Inline bar chart
│           ├── SentimentBar.jsx    # Pos/Neu/Neg colour bar
│           └── Metric.jsx          # Label + value + sub display
├── backend/
│   ├── requirements.txt
│   ├── main.py                     # FastAPI entry point
│   └── agents/
│       ├── technical.py
│       ├── fundamental.py
│       ├── sentiment.py
│       ├── prediction.py
│       ├── analyst.py
│       └── risk.py
└── docs/
    ├── architecture.md
    ├── agents.md
    └── api.md
```

---

## 🔧 Tech Stack

**Frontend**
- React 18 + Vite
- Tailwind CSS
- Recharts (data visualisation)
- Framer Motion (animations)

**Backend**
- FastAPI + Uvicorn
- AsyncIO (parallel agent execution)
- PyTorch + HuggingFace Transformers (FinBERT, Bi-LSTM)
- Pandas, NumPy, Scikit-learn

**Data Sources**
- Yahoo Finance API (OHLCV price data)
- Financial RSS feeds (news for sentiment)
- NSE/BSE macroeconomic indicators

---

## 📊 Decision Engine

Each agent returns a score from 0–100. The Decision Engine combines them:

```
Final Score = Σ (agent_score × agent_weight)

BUY  → Final Score ≥ 65
HOLD → Final Score 45–64
SELL → Final Score < 45
```

Weights can be tuned in `src/utils/scoring.js` (frontend) or `backend/main.py`.

---

## ⚠️ Disclaimer

Quant Sentinel AI is a **decision-support tool only**. It does not execute trades automatically. All recommendations require human review. This is not financial advice. Past model performance does not guarantee future accuracy.

---

## 👥 Team

| Member | Contribution |
|---|---|
| Shreyans Kalantagdiya | NLP-based sentiment analysis (FinBERT integration) |
| Sarthak Sharma | LSTM price prediction model |
| Sresth Yadav | Retrieval-Augmented Generation (RAG) mechanism |

---

## 📄 License

This project was developed as an academic minor project at JIIT Noida. Not licensed for commercial use.

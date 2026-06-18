# System Architecture

## Overview

Quant Sentinel AI follows a **multi-agent, microservice-inspired architecture** with a React frontend, FastAPI backend, and six independent AI agents executed concurrently.

## Component diagram

```
┌──────────────────────────────────────────┐
│            React Frontend (Vite)         │
│                                          │
│  StockPicker → Dashboard → SummaryBar    │
│  OverviewTab | AgentsTab | PredictionTab │
└──────────────────┬───────────────────────┘
                   │  GET /analyse?symbol=RELIANCE
                   │  ← JSON response
┌──────────────────▼───────────────────────┐
│         FastAPI Backend (Uvicorn)        │
│         main.py · asyncio.gather()       │
└──┬──────┬──────┬──────┬──────┬──────────┘
   │      │      │      │      │
   ▼      ▼      ▼      ▼      ▼ ▼
 tech  fund  sent  pred  anl  risk  ← agents/
   │      │      │      │      │      │
   └──────┴──────┴──────┴──────┴──────┘
                   │
        ┌──────────▼──────────┐
        │   Decision Engine   │
        │ Weighted Aggregation│
        │  BUY / HOLD / SELL  │
        └─────────────────────┘
```

## Data flow

1. User selects a stock symbol in the React UI.
2. Frontend calls `GET /analyse?symbol=<SYMBOL>`.
3. FastAPI runs all 6 agents in parallel via `asyncio.gather()`.
4. Each agent independently fetches data (Yahoo Finance, RSS feeds) and returns a score 0–100.
5. The Decision Engine computes a weighted total score and derives a recommendation.
6. Response JSON is returned to the frontend and rendered across three tabs.

## Asynchronous execution

All agents are `async def` coroutines. `asyncio.gather()` schedules them concurrently on the same event loop, reducing total latency to approximately the slowest single agent rather than the sum of all agents.

Heavy synchronous work (model inference, data fetching) is offloaded to a thread pool via `asyncio.get_event_loop().run_in_executor(None, ...)`.

## Scalability

- Each agent is an independent module — new agents can be added without touching existing ones.
- Weights in `main.py` are easily configurable.
- The frontend hook `useAgentAnalysis.js` abstracts the API call, making it trivial to swap mock data for real API responses.

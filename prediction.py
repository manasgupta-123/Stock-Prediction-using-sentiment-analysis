"""
agents/prediction.py
Prediction Agent — Bidirectional LSTM with Attention

Implements a Bi-LSTM model with an attention mechanism for short-term
(5-day) stock price forecasting.

Architecture:
  Input  → Bi-LSTM (64 units) → Attention → Dense → Price output

Training uses the last 60 days of OHLCV data, normalised with MinMaxScaler.
Model is trained fresh per request in this reference implementation;
in production, persist weights to disk and fine-tune periodically.
"""

import asyncio
import numpy as np
import torch
import torch.nn as nn
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler


LOOKBACK     = 60   # days of history fed into the model
FORECAST     = 5    # days to predict
HIDDEN_SIZE  = 64
NUM_LAYERS   = 2
EPOCHS       = 20
LR           = 0.001


class AttentionLayer(nn.Module):
    def __init__(self, hidden_size: int):
        super().__init__()
        self.attn = nn.Linear(hidden_size * 2, 1)

    def forward(self, lstm_out):
        weights = torch.softmax(self.attn(lstm_out), dim=1)
        return (weights * lstm_out).sum(dim=1)


class BiLSTMWithAttention(nn.Module):
    def __init__(self, input_size=1, hidden_size=HIDDEN_SIZE, num_layers=NUM_LAYERS, forecast=FORECAST):
        super().__init__()
        self.lstm      = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, bidirectional=True)
        self.attention = AttentionLayer(hidden_size)
        self.fc        = nn.Linear(hidden_size * 2, forecast)

    def forward(self, x):
        out, _ = self.lstm(x)
        context = self.attention(out)
        return self.fc(context)


def _train_and_predict(symbol: str) -> tuple[list[float], float]:
    ticker = yf.Ticker(f"{symbol}.NS")
    hist   = ticker.history(period="1y")["Close"].values.reshape(-1, 1)

    if len(hist) < LOOKBACK + FORECAST:
        raise ValueError(f"Insufficient data for {symbol}")

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(hist)

    # Build sequences
    X, y = [], []
    for i in range(len(scaled) - LOOKBACK - FORECAST):
        X.append(scaled[i : i + LOOKBACK])
        y.append(scaled[i + LOOKBACK : i + LOOKBACK + FORECAST].flatten())

    X = torch.tensor(np.array(X), dtype=torch.float32)
    y = torch.tensor(np.array(y), dtype=torch.float32)

    model     = BiLSTMWithAttention()
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    criterion = nn.MSELoss()

    model.train()
    for _ in range(EPOCHS):
        optimizer.zero_grad()
        loss = criterion(model(X), y)
        loss.backward()
        optimizer.step()

    # Predict next 5 days
    model.eval()
    with torch.no_grad():
        last_seq = torch.tensor(scaled[-LOOKBACK:].reshape(1, LOOKBACK, 1), dtype=torch.float32)
        pred_scaled = model(last_seq).numpy().reshape(-1, 1)

    predictions = scaler.inverse_transform(pred_scaled).flatten().tolist()
    confidence  = round(max(0, min(100, 100 - float(loss.item()) * 200)), 1)

    return [round(p, 2) for p in predictions], confidence


async def run_prediction_agent(symbol: str) -> dict:
    """
    Train Bi-LSTM on historical prices and forecast the next 5 days.

    Returns:
        dict with keys: days, prices, score, confidence
    """
    loop        = asyncio.get_event_loop()
    prices, conf = await loop.run_in_executor(None, _train_and_predict, symbol)

    ticker = yf.Ticker(f"{symbol}.NS")
    current_price = ticker.history(period="5d")["Close"].iloc[-1]
    score = round(((prices[-1] - current_price) / current_price) * 1000 + 55)

    return {
        "days":       ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"],
        "prices":     prices,
        "score":      max(0, min(100, score)),
        "confidence": conf,
    }

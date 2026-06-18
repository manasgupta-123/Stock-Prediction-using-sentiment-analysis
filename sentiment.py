"""
agents/sentiment.py
Sentiment Analysis Agent

Collects financial news headlines from RSS feeds and classifies each
headline using FinBERT (a BERT model fine-tuned on financial text).

Model: ProsusAI/finbert (via HuggingFace Transformers)
News source: Google Finance RSS, Economic Times RSS

Output: percentage breakdown of positive / neutral / negative sentiment.
"""

import asyncio
import feedparser
from transformers import pipeline

# Lazy-load the FinBERT pipeline — heavy model, loaded once on first call
_finbert = None

RSS_FEEDS = [
    "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms",
    "https://feeds.feedburner.com/businessinsider",
]


def _get_finbert():
    global _finbert
    if _finbert is None:
        _finbert = pipeline(
            "text-classification",
            model="ProsusAI/finbert",
            tokenizer="ProsusAI/finbert",
        )
    return _finbert


def _fetch_headlines(symbol: str, max_articles: int = 20) -> list[str]:
    """Fetch headlines from RSS feeds and filter by symbol name."""
    headlines = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.get("title", "")
            if symbol.lower() in title.lower() or not headlines:
                headlines.append(title)
            if len(headlines) >= max_articles:
                break
    return headlines[:max_articles]


async def run_sentiment_agent(symbol: str) -> dict:
    """
    Fetch news headlines, run FinBERT classification, return sentiment scores.

    Returns:
        dict with keys: positive, negative, neutral, score, newsCount
    """
    loop = asyncio.get_event_loop()

    headlines = await loop.run_in_executor(None, _fetch_headlines, symbol)
    if not headlines:
        # Fallback if no relevant news found
        return {"positive": 40.0, "negative": 20.0, "neutral": 40.0, "score": 56, "newsCount": 0}

    classifier = await loop.run_in_executor(None, _get_finbert)
    results    = await loop.run_in_executor(None, classifier, headlines)

    counts = {"positive": 0, "negative": 0, "neutral": 0}
    for r in results:
        label = r["label"].lower()
        if label in counts:
            counts[label] += 1

    total    = len(results)
    positive = round(counts["positive"] / total * 100, 2)
    negative = round(counts["negative"] / total * 100, 2)
    neutral  = round(100 - positive - negative, 2)
    score    = round(positive * 0.9 + neutral * 0.5)

    return {
        "positive":  positive,
        "negative":  negative,
        "neutral":   neutral,
        "score":     score,
        "newsCount": total,
    }

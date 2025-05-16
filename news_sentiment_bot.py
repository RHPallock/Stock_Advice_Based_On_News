#!/usr/bin/env python3
# news_sentiment_bot.py
"""
Simple CLI software that fetches the latest news about a ticker (default: NVIDIA),
classifies each headline with FinBERT, rolls the sentiment into a score, and
prints a naive BUY / HOLD / SELL recommendation.

Usage (after installing requirements):

    python3 news_sentiment_bot.py                 # defaults: NVDA, 1‑day window
    python3 news_sentiment_bot.py --ticker AAPL   # different ticker
    python3 news_sentiment_bot.py --days 3        # 3‑day look‑back window
    python3 news_sentiment_bot.py --alpha 0.4     # change EMA decay
    python3 news_sentiment_bot.py --pos 0.3 --neg -0.3  # custom thresholds

Requirements (create requirements.txt):
    python-dotenv
    newsapi-python
    transformers
    torch
    pandas
    tqdm

Set your NewsAPI key once in a .env file in the same folder:
    NEWSAPI_KEY=your_long_key_string

Scheduling suggestion (Linux/macOS):
    */30 * * * *  /usr/bin/python /path/to/news_sentiment_bot.py --ticker NVDA >> ~/nvda_bot.log 2>&1

Note on execution errors (apt_pkg / command-not-found):
    If you see a "ModuleNotFoundError: apt_pkg" when running the script directly on
    some Ubuntu systems, it usually means the system is trying to execute the file
    without an interpreter. Either run it explicitly with Python:

        python3 news_sentiment_bot.py

    or make the file executable once:

        chmod +x news_sentiment_bot.py
        ./news_sentiment_bot.py

    Installing the system package python3-apt can silence the command‑not‑found
    traceback entirely:

        sudo apt update && sudo apt install -y python3-apt

"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path
from typing import List

import pandas as pd
from dotenv import load_dotenv
from newsapi import NewsApiClient
from tqdm import tqdm
from transformers import pipeline

# ---------------------------------------------------------------------------
# Constants & helpers
# ---------------------------------------------------------------------------
DEFAULT_ALPHA = 0.4  # exponential‑weighted moving average decay
DEFAULT_POS_THRESH = 0.25
DEFAULT_NEG_THRESH = -0.25


def debug(msg: str, verbose: bool):
    if verbose:
        print(f"[debug] {msg}", file=sys.stderr)


# ---------------------------------------------------------------------------
# 1. Fetch headlines
# ---------------------------------------------------------------------------

def fetch_headlines(api_key: str, query: str, start: dt.datetime, end: dt.datetime, verbose: bool) -> pd.DataFrame:
    client = NewsApiClient(api_key=api_key)
    debug("Contacting NewsAPI …", verbose)
    response = client.get_everything(
        q=query,
        language="en",
        sort_by="publishedAt",
        from_param=start.strftime("%Y-%m-%d"),
        to=end.strftime("%Y-%m-%d"),
        page_size=100,
    )
    articles = response.get("articles", [])
    debug(f"Fetched {len(articles)} articles", verbose)
    if not articles:
        return pd.DataFrame(columns=["publishedAt", "title", "description"])
    return pd.DataFrame(articles)[["publishedAt", "title", "description"]]


# ---------------------------------------------------------------------------
# 2. Classify sentiment
# ---------------------------------------------------------------------------

def classify_sentiment(df: pd.DataFrame, verbose: bool) -> pd.DataFrame:
    if df.empty:
        return df
    clf = pipeline(
        "text-classification",
        model="ProsusAI/finbert",
        truncation=True,
        device=-1,  # use CPU; change to 0 for GPU
    )
    label2num = {"positive": 1, "neutral": 0, "negative": -1}
    sentiments: List[int] = []
    for title in tqdm(df["title"], desc="Classifying", disable=not verbose):
        label = clf(title)[0]["label"].lower()
        sentiments.append(label2num[label])
    df = df.copy()
    df["sentiment"] = sentiments
    return df


# ---------------------------------------------------------------------------
# 3. Compute score & decision
# ---------------------------------------------------------------------------

def compute_decision(df: pd.DataFrame, alpha: float, pos_thr: float, neg_thr: float):
    if df.empty:
        return None, "NO_DATA"
    score = df["sentiment"].ewm(alpha=alpha).mean().iloc[-1]
    if score >= pos_thr:
        decision = "BUY"
    elif score <= neg_thr:
        decision = "SELL"
    else:
        decision = "HOLD"
    return float(score), decision


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="News‑driven sentiment bot using FinBERT")
    parser.add_argument("--ticker", default="NVDA", help="Ticker symbol, e.g., NVDA")
    parser.add_argument("--days", type=int, default=1, help="Look‑back window in days")
    parser.add_argument("--alpha", type=float, default=DEFAULT_ALPHA, help="EMA decay parameter")
    parser.add_argument("--pos", type=float, default=DEFAULT_POS_THRESH, help="Positive threshold (BUY)")
    parser.add_argument("--neg", type=float, default=DEFAULT_NEG_THRESH, help="Negative threshold (SELL)")
    parser.add_argument("--verbose", action="store_true", help="Print debug info & progress bars")
    args = parser.parse_args()

    # Load API key
    load_dotenv()
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        sys.exit("ERROR: NEWSAPI_KEY not found. Create a .env file or set env var.")

    today = dt.datetime.utcnow()
    start = today - dt.timedelta(days=args.days)
    query = f"({args.ticker} OR {args.ticker.upper()})"

    # 1. Fetch
    df = fetch_headlines(api_key, query, start, today, args.verbose)

    # 2. Sentiment
    if not df.empty:
        df = classify_sentiment(df, args.verbose)

    # 3. Decision
    score, decision = compute_decision(df, args.alpha, args.pos, args.neg)

    # 4. Output JSON to stdout
    output = {
        "ticker": args.ticker.upper(),
        "timestamp_utc": today.isoformat(timespec="seconds"),
        "n_headlines": int(df.shape[0]),
        "score": score,
        "decision": decision,
    }
    print(json.dumps(output, indent=2))

    # Optional: Save raw data & scored headlines
    out_dir = Path("data")
    out_dir.mkdir(exist_ok=True)
    if not df.empty:
        df.to_csv(out_dir / f"{args.ticker.upper()}_{today.date()}.csv", index=False)


if __name__ == "__main__":
    main()

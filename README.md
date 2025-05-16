# Stock Analysis based on sentiment analysis

*A lightweight, fully‑open‑source CLI that fuses real‑time news with FinBERT sentiment analysis to spit out a **BUY / HOLD / SELL** call for any stock ticker.*


## ✨ Key Features

| Feature | Details |
| --- | --- |
| **Real‑time headlines** | Pulls news via [NewsAPI.org](https://newsapi.org) |
| **FinBERT sentiment** | Uses *ProsusAI/finbert* to classify each headline |
| **Rolling score** | Exponential‑weighted mean turns raw labels into a single sentiment number |
| **Actionable output** | Prints structured JSON with the score and a naïve BUY / HOLD / SELL decision |
| **One‑file design** | Everything—including I/O, CLI, logging—lives in `news_sentiment_bot.py` |
| **Cron‑ready** | Designed to run headless every X minutes |

## 🚀 Quick Start

```bash
git clone https://github.com/RHPallock/Stock_Analysis.git
cd Stock_Analysis
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
echo "NEWSAPI_KEY=<your-key>" > .env
python news_sentiment_bot.py
```



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

## Instructions:
Install all the packages from the requirements.txt.
    Run pip install requirements.txt
    
You will also need a .env file that contains NewAPI key.
For the NewsAPI key, you will need to sign up in: https://newsapi.org/
Once signed up:
1. Create a notepad file
2. Write "NEWSAPI_KEY=Your_API_Key" without the double quotes. Put your key in "Your_API_Key"
3. Save it as .env (Choose file type as all_files)
4. Keep it in the same directory folder


Usage (after installing requirements):

    python3 news_sentiment_bot.py                 # defaults: NVDA, 1‑day window
    python3 news_sentiment_bot.py --ticker AAPL   # different ticker
    python3 news_sentiment_bot.py --days 3        # 3‑day look‑back window
    python3 news_sentiment_bot.py --alpha 0.4     # change EMA decay
    python3 news_sentiment_bot.py --pos 0.3 --neg -0.3  # custom thresholds





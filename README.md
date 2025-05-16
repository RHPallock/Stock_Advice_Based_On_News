Requirements:
    1. python-dotenv
    2. newsapi-python
    3. transformers
    4. torch
    5. pandas
    6. tqdm

You will need a .env file that contains NewAPI key. Please follow the instructions.
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

import yfinance as yf
import pandas as pd
from textblob import TextBlob
import numpy as np
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator

# --- CONFIG ---
tickers = ["NVDA", "AAPL", "GOOGL", "IBM", "CRWD"]
weights = {'F': 0.25, 'T': 0.25, 'S': 0.25, 'A': 0.25}

# --- DATA COLLECTION ---
def get_fundamentals(ticker):
    data = yf.Ticker(ticker).info
    F = (
        (data.get('revenueGrowth') or 0.1) * 0.3 +
        (data.get('profitMargins') or 0.1) * 0.3 +
        ((1 - data.get('debtToEquity', 100) / 100) if data.get('debtToEquity') else 0.5) * 0.2 +
        (data.get('earningsQuarterlyGrowth') or 0.1) * 0.2
    )
    return np.clip(F, 0, 1)

def get_technicals(ticker):
    df = yf.download(ticker, period="6mo", interval="1d")

    # Ensure Close is always a 1D Series
    close = df['Close']
    if isinstance(close, pd.DataFrame):
        close = close.squeeze()

    ema50 = float(EMAIndicator(close, 50).ema_indicator().iloc[-1])
    ema200 = float(EMAIndicator(close, 200).ema_indicator().iloc[-1])
    rsi = float(RSIIndicator(close, 14).rsi().iloc[-1])

    cmf = ((close - close.shift(1)) * df['Volume']).sum() / df['Volume'].sum()

    if isinstance(cmf, pd.Series):
        cmf = cmf.dropna()
        cmf = cmf.iloc[-1] if not cmf.empty else 0.0

    cmf = float(cmf)

    T = (ema50 / ema200 if ema50 < ema200 else 1) * 0.25 \
        + (rsi / 100) * 0.25 \
        + (cmf if cmf > 0 else 0) * 0.5

    return np.clip(T, 0, 1)



def get_sentiment(news_headlines):
    scores = [TextBlob(headline).sentiment.polarity for headline in news_headlines]
    return np.clip((np.mean(scores) + 1) / 2, 0, 1)

def get_ai_score(ticker):
    # Placeholder: in real use, integrate patents, R&D, AI revenue
    return np.random.uniform(0.4, 1)

# --- MAIN POWER SCORE ---
def compute_power_score(ticker, news_headlines=[]):
    F = get_fundamentals(ticker)
    T = get_technicals(ticker)
    S = get_sentiment(news_headlines)
    A = get_ai_score(ticker)
    return weights['F'] * F + weights['T'] * T + weights['S'] * S + weights['A'] * A

# --- RUN ---
def main():
    results = []
    for ticker in tickers:
        score = compute_power_score(ticker, news_headlines=["AI breakthrough by " + ticker])
        results.append({'Ticker': ticker, 'PowerScore': score})

    df_results = pd.DataFrame(results).sort_values(by='PowerScore', ascending=False)
    print(df_results)


if __name__ == "__main__":
    main()

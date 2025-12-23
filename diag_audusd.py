import yfinance as yf
import pandas as pd
import numpy as np

def calculate_macd(df):
    fast, slow, signal = 12, 26, 9
    exp1 = df['Close'].ewm(span=fast, adjust=False).mean()
    exp2 = df['Close'].ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    df['MACD_Line'] = macd
    df['Signal_Line'] = signal_line
    df['Histogram'] = histogram
    return df

def calculate_ema(df, period=200):
    df[f'EMA_{period}'] = df['Close'].ewm(span=period, adjust=False).mean()
    return df

def calculate_rsi(df, period=14):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

symbol = "AUDUSD=X"
print(f"Checking {symbol}...")

# Entry (1H)
entry_df = yf.Ticker(symbol).history(period="30d", interval="1h")
entry_df = calculate_macd(entry_df)
entry_df = calculate_ema(entry_df, 200)
entry_df = calculate_rsi(entry_df, 14)

e_last = entry_df.iloc[-2]
print(f"1H Close: {e_last['Close']}")
print(f"1H EMA 200: {e_last['EMA_200']}")
print(f"1H RSI: {e_last['RSI']}")
print(f"1H MACD Line: {e_last['MACD_Line']}")
print(f"1H Signal Line: {e_last['Signal_Line']}")
print(f"1H Histogram: {e_last['Histogram']}")

is_above_ema = e_last['Close'] > e_last['EMA_200']
rsi_bullish = e_last['RSI'] > 50
macd_bullish = e_last['MACD_Line'] > 0 and e_last['Signal_Line'] > 0

print(f"Filter - Above EMA 200: {is_above_ema}")
print(f"Filter - RSI > 50: {rsi_bullish}")
print(f"Filter - MACD Bullish (Both > 0): {macd_bullish}")

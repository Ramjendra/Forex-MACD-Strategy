import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

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

symbol = "GBPUSD=X"
print(f"Checking {symbol} at {datetime.now()}...")

# Daily Trend
daily_df = yf.Ticker(symbol).history(period="2y", interval="1d")
daily_df = calculate_macd(daily_df)
daily_df = calculate_ema(daily_df, 200)
t_last = daily_df.iloc[-2]

# 4H Momentum (from 1H)
h1_raw = yf.Ticker(symbol).history(period="1y", interval="1h")
h1_raw.index = pd.to_datetime(h1_raw.index)
mom_df = h1_raw.resample('4h').agg({
    'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
}).dropna()
mom_df = calculate_macd(mom_df)
m_last = mom_df.iloc[-2]

# 1H Entry
entry_df = yf.Ticker(symbol).history(period="30d", interval="1h")
entry_df = calculate_macd(entry_df)
entry_df = calculate_ema(entry_df, 200)
entry_df = calculate_rsi(entry_df, 14)
e_last = entry_df.iloc[-2]

print(f"\n--- Daily Trend ---")
print(f"Daily MACD Line: {t_last['MACD_Line']:.5f}")
print(f"Daily Close: {t_last['Close']:.5f}")
print(f"Daily EMA 200: {t_last['EMA_200']:.5f}")
trend_bullish = t_last['MACD_Line'] > 0 and t_last['Close'] > t_last['EMA_200']
print(f"Trend Bullish: {trend_bullish}")

print(f"\n--- 4H Momentum ---")
print(f"4H Histogram: {m_last['Histogram']:.5f}")
mom_bullish = m_last['Histogram'] > 0
print(f"Momentum Bullish: {mom_bullish}")

print(f"\n--- 1H Entry ---")
print(f"1H Close: {e_last['Close']:.5f}")
print(f"1H EMA 200: {e_last['EMA_200']:.5f}")
print(f"1H RSI: {e_last['RSI']:.2f}")
print(f"1H MACD Line: {e_last['MACD_Line']:.5f}")
print(f"1H Signal Line: {e_last['Signal_Line']:.5f}")
print(f"1H Histogram: {e_last['Histogram']:.5f}")

is_above_ema = e_last['Close'] > e_last['EMA_200']
rsi_bullish = e_last['RSI'] > 50
macd_bullish = e_last['MACD_Line'] > 0 and e_last['Signal_Line'] > 0

print(f"\n--- Filters ---")
print(f"Above 1H EMA 200: {is_above_ema}")
print(f"RSI > 50: {rsi_bullish}")
print(f"MACD Bullish (Both > 0): {macd_bullish}")

overall_bullish = trend_bullish and mom_bullish and is_above_ema and rsi_bullish and macd_bullish
print(f"\nOVERALL BULLISH ALIGNMENT: {overall_bullish}")

import yfinance as yf
import pandas as pd
import numpy as np

def calculate_macd(df):
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=9, adjust=False).mean()
    histogram = macd - signal_line
    df['MACD_Line'] = macd
    df['Signal_Line'] = signal_line
    df['Histogram'] = histogram
    return df

def diag_usdcad():
    symbol = "USDCAD=X"
    print(f"Checking {symbol} 1H conditions...")
    df = yf.Ticker(symbol).history(period="5d", interval="1h")
    df = calculate_macd(df)
    
    last = df.iloc[-2]
    prev = df.iloc[-3]
    
    print(f"Last Candle Time: {last.name}")
    print(f"Last Histogram: {last['Histogram']:.6f}")
    print(f"Prev Histogram: {prev['Histogram']:.6f}")
    
    if last['Histogram'] < 0 and prev['Histogram'] >= 0:
        print("Trigger Condition: SELL_CROSS (True)")
    elif last['Histogram'] < 0 and prev['Histogram'] < 0:
        print("Trigger Condition: Already Bearish (No Signal Triggered)")
    else:
        print("Trigger Condition: Not Bearish")

if __name__ == "__main__":
    diag_usdcad()

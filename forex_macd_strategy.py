#!/usr/bin/env python3
"""
MACD Multi-Timeframe Strategy for Major Forex Pairs
Daily (Trend) + 4H (Momentum) + 1H (Entry)
"""

import json
import time
import sys
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


try:
    import yfinance as yf
    import pandas as pd
    import numpy as np
    from trade_screenshot import capture_trade_screenshot
except ImportError:
    print("❌ Error: Required libraries not installed (yfinance, pandas, numpy, pillow)")
    sys.exit(1)

# ================= CONFIGURATION =================
BASE_DIR = Path(__file__).parent
SIGNALS_FILE = BASE_DIR / "forex_macd_signals.json"
HISTORY_FILE = BASE_DIR / "signal_history.json"
CONFIG = {
    "instruments": [
        {"name": "US Oil (WTI)", "symbol": "CL=F", "pip_size": 0.01, "flag": "🛢️", "category": "Metals/Energy"},
        {"name": "MCX Crude Oil", "symbol": "CL=F", "pip_size": 0.01, "flag": "🇮🇳🛢️", "category": "Intraday IndianMarket"},
        {"name": "MCX Natural Gas", "symbol": "NG=F", "pip_size": 0.1, "flag": "🇮🇳🔥", "category": "Intraday IndianMarket"},
        {"name": "MCX Copper", "symbol": "HG=F", "pip_size": 0.05, "flag": "🇮🇳🧱", "category": "Intraday IndianMarket"},
        {"name": "Gold", "symbol": "GC=F", "pip_size": 0.1, "flag": "🥇", "category": "Metals/Energy"},
        {"name": "Silver", "symbol": "SI=F", "pip_size": 0.005, "flag": "🥈", "category": "Metals/Energy"},
        {"name": "Brent Crude Oil", "symbol": "BZ=F", "pip_size": 0.01, "flag": "🇬🇧🛢️", "category": "Metals/Energy"},
        {"name": "Natural Gas", "symbol": "NG=F", "pip_size": 0.001, "flag": "🔥", "category": "Metals/Energy"},
        {"name": "Platinum", "symbol": "PL=F", "pip_size": 0.1, "flag": "💍", "category": "Metals/Energy"},
        {"name": "Palladium", "symbol": "PA=F", "pip_size": 0.1, "flag": "💎", "category": "Metals/Energy"},

        {"name": "EUR/USD", "symbol": "EURUSD=X", "pip_size": 0.0001, "flag": "🇪🇺🇺🇸", "category": "Forex"},
        {"name": "USD/JPY", "symbol": "USDJPY=X", "pip_size": 0.01, "flag": "🇺🇸🇯🇵", "category": "Forex"},
        {"name": "AUD/USD", "symbol": "AUDUSD=X", "pip_size": 0.0001, "flag": "🇦🇺🇺🇸", "category": "Forex"},
        {"name": "USD/CHF", "symbol": "USDCHF=X", "pip_size": 0.0001, "flag": "🇺🇸🇨🇭", "category": "Forex"},
        {"name": "NZD/USD", "symbol": "NZDUSD=X", "pip_size": 0.0001, "flag": "🇳🇿🇺🇸", "category": "Forex"},
        {"name": "USD/CAD", "symbol": "USDCAD=X", "pip_size": 0.0001, "flag": "🇺🇸🇨🇦", "category": "Forex"},
        {"name": "EUR/GBP", "symbol": "EURGBP=X", "pip_size": 0.0001, "flag": "🇪🇺🇬🇧", "category": "Forex"},
        {"name": "EUR/JPY", "symbol": "EURJPY=X", "pip_size": 0.01, "flag": "🇪🇺🇯🇵", "category": "Forex"},
        {"name": "GBP/JPY", "symbol": "GBPJPY=X", "pip_size": 0.01, "flag": "🇬🇧🇯🇵", "category": "Forex"},
        {"name": "AUD/JPY", "symbol": "AUDJPY=X", "pip_size": 0.01, "flag": "🇦🇺🇯🇵", "category": "Forex"},
        {"name": "NZD/JPY", "symbol": "NZDJPY=X", "pip_size": 0.01, "flag": "🇳🇿🇯🇵", "category": "Forex"},
        {"name": "GBP/CHF", "symbol": "GBPCHF=X", "pip_size": 0.0001, "flag": "🇬🇧🇨🇭", "category": "Forex"},
        {"name": "EUR/CAD", "symbol": "EURCAD=X", "pip_size": 0.0001, "flag": "🇪🇺🇨🇦", "category": "Forex"},
        {"name": "AUD/CAD", "symbol": "AUDCAD=X", "pip_size": 0.0001, "flag": "🇦🇺🇨🇦", "category": "Forex"},
        {"name": "CAD/JPY", "symbol": "CADJPY=X", "pip_size": 0.01, "flag": "🇨🇦🇯🇵", "category": "Forex"},
        {"name": "CHF/JPY", "symbol": "CHFJPY=X", "pip_size": 0.01, "flag": "🇨🇭🇯🇵", "category": "Forex"},

        {"name": "Bitcoin", "symbol": "BTC-USD", "pip_size": 1.0, "flag": "₿", "category": "Crypto Scalping"},
        {"name": "Ethereum", "symbol": "ETH-USD", "pip_size": 0.1, "flag": "Ξ", "category": "Crypto Scalping"},
        {"name": "Solana", "symbol": "SOL-USD", "pip_size": 0.01, "flag": "☀️", "category": "Crypto Scalping"},
        {"name": "Ripple", "symbol": "XRP-USD", "pip_size": 0.0001, "flag": "💧", "category": "Crypto Scalping"},
        {"name": "Cardano", "symbol": "ADA-USD", "pip_size": 0.0001, "flag": "₳", "category": "Crypto Scalping"},
        {"name": "Dogecoin", "symbol": "DOGE-USD", "pip_size": 0.00001, "flag": "🐕", "category": "Crypto Scalping"},
        {"name": "Polkadot", "symbol": "DOT-USD", "pip_size": 0.01, "flag": "⚫", "category": "Crypto Scalping"},
        {"name": "Nifty 50", "symbol": "^NSEI", "pip_size": 0.05, "flag": "🇮🇳", "category": "Intraday IndianMarket"},
        {"name": "Bank Nifty", "symbol": "^NSEBANK", "pip_size": 0.05, "flag": "🇮🇳🏦", "category": "Intraday IndianMarket"},
        {"name": "Sensex", "symbol": "^BSESN", "pip_size": 0.05, "flag": "🇮🇳📈", "category": "Intraday IndianMarket"}
    ],
    "macd": {
        "fast": 12,
        "slow": 26,
        "signal": 9
    },
    "risk": {
        "sl_atr_multiplier": 1.5,      # Dynamic SL based on ATR
        "tp_ratios": [1.5, 3.0, 5.0],  # TP1, TP2, TP3
        "trailing_sl": {
            "active": True,
            "move_to_breakeven_at_tp1": True,
            "move_to_tp1_at_tp2": True
        }
    }
}

# Global dictionary to track active signals
ACTIVE_SIGNALS_FILE = BASE_DIR / "active_signals.json"

def load_active_signals():
    global ACTIVE_SIGNALS
    ACTIVE_SIGNALS = {}
    
    # 1. Try loading from dedicated persistence file
    if ACTIVE_SIGNALS_FILE.exists():
        try:
            with open(ACTIVE_SIGNALS_FILE, 'r') as f:
                ACTIVE_SIGNALS = json.load(f)
            print(f"📂 Loaded {len(ACTIVE_SIGNALS)} active signals from {ACTIVE_SIGNALS_FILE.name}")
            return
        except Exception as e:
            print(f"⚠️ Failed to load from {ACTIVE_SIGNALS_FILE.name}: {e}")

    # 2. Fallback: Try loading from the last signals output file
    try:
        if SIGNALS_FILE.exists():
            with open(SIGNALS_FILE, 'r') as f:
                data = json.load(f)
                for inst in data.get('data', []):
                    if inst.get('signal'):
                        ACTIVE_SIGNALS[inst['instrument']] = inst['signal']
            if ACTIVE_SIGNALS:
                print(f"✅ Recovered {len(ACTIVE_SIGNALS)} active signals from {SIGNALS_FILE.name}")
                save_active_signals() # Save to the new persistence file
    except Exception as e:
        print(f"⚠️ Error recovering signals from {SIGNALS_FILE.name}: {e}")

def save_active_signals():
    try:
        with open(ACTIVE_SIGNALS_FILE, 'w') as f:
            json.dump(ACTIVE_SIGNALS, f, indent=2, default=str)
    except Exception as e:
        print(f"❌ Failed to save active signals: {e}")

# Initial load
load_active_signals()


# ================= DATA & INDICATORS =================
def fetch_data(symbol: str, interval: str, period: str) -> pd.DataFrame:
    """Fetch data from Yahoo Finance with retries."""
    for attempt in range(3):
        try:
            # Use a custom session with a user-agent to avoid rate limits
            import requests
            session = requests.Session()
            session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
            
            ticker = yf.Ticker(symbol, session=session)
            df = ticker.history(period=period, interval=interval)
            if not df.empty:
                return df
            print(f"  ⚠️ Empty data for {symbol} ({interval}) on attempt {attempt+1}")
        except Exception as e:
            print(f"  ❌ Error fetching {symbol} ({interval}) on attempt {attempt+1}: {e}")
        time.sleep(2) # Wait before retry
    return pd.DataFrame()

def calculate_macd(df: pd.DataFrame) -> pd.DataFrame:
    fast = CONFIG['macd']['fast']
    slow = CONFIG['macd']['slow']
    signal = CONFIG['macd']['signal']
    
    exp1 = df['Close'].ewm(span=fast, adjust=False).mean()
    exp2 = df['Close'].ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    
    df['MACD_Line'] = macd
    df['Signal_Line'] = signal_line
    df['Histogram'] = histogram
    return df

def calculate_ema(df: pd.DataFrame, period: int = 200) -> pd.DataFrame:
    df[f'EMA_{period}'] = df['Close'].ewm(span=period, adjust=False).mean()
    return df

def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    high_low = df['High'] - df['Low']
    high_close = (df['High'] - df['Close'].shift()).abs()
    low_close = (df['Low'] - df['Close'].shift()).abs()
    
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    df['ATR'] = true_range.rolling(window=period).mean()
    return df

def log_signal_event(instrument, event_type, price, signal_data=None):
    """Log signal events to a persistent history file."""
    try:
        history = []
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
        
        event = {
            "instrument": instrument,
            "event": event_type,
            "price": price,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "category": signal_data.get('category', 'Other') if signal_data else 'Other'
        }
        
        if signal_data:
            event["entry_price"] = signal_data.get('entry_price')
            event["entry_time"] = signal_data.get('time')
            event["type"] = signal_data.get('type')
            event["initial_sl"] = signal_data.get('sl')

        history.append(event)
        
        # Keep only last 100 events
        history = history[-100:]
        
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
            
    except Exception as e:
        print(f"  ❌ Error logging event: {e}")

# ================= STRATEGY LOGIC =================
def analyze_instrument(instrument: Dict) -> Dict:
    symbol = instrument['symbol']
    name = instrument['name']
    
    print(f"\n📊 Analyzing {name} ({symbol})...")
    
    category = instrument.get('category', 'Forex')
    
    # 1. Fetch Data based on Category
    if category in ["Intraday IndianMarket", "Cryptos"]:
        # Intraday: 4H Trend (from 1H), 1H Momentum, 15m Entry
        trend_df_raw = fetch_data(symbol, "1h", "1y")
        mom_df = trend_df_raw.copy()
        entry_df = fetch_data(symbol, "15m", "30d")
        
        if trend_df_raw.empty or entry_df.empty:
            print("  ⚠️ Insufficient data")
            return None
            
        # Resample 1H to 4H for Trend
        trend_df_raw.index = pd.to_datetime(trend_df_raw.index)
        trend_df = trend_df_raw.resample('4h').agg({
            'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
        }).dropna()
        
        trend_label = "4H Trend"
        mom_label = "1H MOM"
        entry_label = "15m Entry"
    elif category == "Crypto Scalping":
        # Scalping: 4H Trend (from 1H), 1H Momentum, 15m Entry
        trend_df_raw = fetch_data(symbol, "1h", "1y")
        mom_df = trend_df_raw.copy()
        entry_df = fetch_data(symbol, "15m", "30d")
        
        if trend_df_raw.empty or entry_df.empty:
            print("  ⚠️ Insufficient data for scalping")
            return None
            
        # Resample 1H to 4H for Trend
        trend_df_raw.index = pd.to_datetime(trend_df_raw.index)
        trend_df = trend_df_raw.resample('4h').agg({
            'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
        }).dropna()
        
        trend_label = "4H Trend"
        mom_label = "1H MOM"
        entry_label = "15m Entry"
    else:
        # Standard: Daily Trend, 4H Momentum (from 1H), 1H Entry
        trend_df = fetch_data(symbol, "1d", "2y")
        mom_df_raw = fetch_data(symbol, "1h", "1y")
        entry_df = fetch_data(symbol, "1h", "30d")
        
        if trend_df.empty or entry_df.empty:
            print("  ⚠️ Insufficient data")
            return None
            
        # Resample 1H to 4H for Momentum
        mom_df_raw.index = pd.to_datetime(mom_df_raw.index)
        mom_df = mom_df_raw.resample('4h').agg({
            'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
        }).dropna()
        
        trend_label = "Daily"
        mom_label = "4H MOM"
        entry_label = "1H Entry"

    # 2. Calculate Indicators
    trend_macd = calculate_macd(trend_df)
    trend_macd = calculate_ema(trend_macd, 200)
    
    mom_macd = calculate_macd(mom_df)
    
    entry_macd = calculate_macd(entry_df)
    entry_macd = calculate_ema(entry_macd, 200)
    entry_macd = calculate_rsi(entry_macd, 14)
    entry_macd = calculate_atr(entry_macd, 14)
    
    # Get latest CLOSED values (Strict Confirmation)
    t_last = trend_macd.iloc[-2]
    m_last = mom_macd.iloc[-2]
    m_prev = mom_macd.iloc[-3]
    e_last = entry_macd.iloc[-2]
    e_prev = entry_macd.iloc[-3]
    
    # Get LATEST price for display
    latest_price = entry_macd.iloc[-1]['Close']
    prev_price = entry_macd.iloc[-2]['Close']
    
    # Price Sanity Check: Ignore spikes > 5% in a single candle (unless it's Crypto)
    if category != "Crypto Scalping":
        price_change = abs(latest_price - prev_price) / prev_price
        if price_change > 0.05:
            print(f"  ⚠️ Ignoring extreme price spike for {name}: {prev_price} -> {latest_price} ({price_change:.2%})")
            latest_price = prev_price

    
    # Special handling for MCX Instruments (Convert USD to INR with unit factors)
    current_price = latest_price
    if name.startswith("MCX"):
        try:
            usdinr_df = fetch_data("USDINR=X", "1d", "5d")
            if not usdinr_df.empty:
                rate = usdinr_df['Close'].iloc[-1]
                
                if name in ["MCX Gold", "MCX Gold Mini"]:
                    # Convert Ounce to 10g: (Price / 31.1035) * 10
                    current_price = (latest_price / 31.1035) * 10 * rate
                elif name == "MCX Silver":
                    # Convert Ounce to 1kg: Price * 32.1507
                    current_price = latest_price * 32.1507 * rate
                elif name == "MCX Copper":
                    # Convert lb to 1kg: Price * 2.20462 * Premium (approx 2.6%)
                    current_price = latest_price * 2.20462 * rate * 1.026
                else:
                    # Crude Oil and Natural Gas: Direct conversion
                    current_price = latest_price * rate
                
                print(f"  💱 Converted {name}: ${latest_price:.2f} -> ₹{current_price:.2f} (Rate: {rate:.2f})")
        except Exception as e:
            print(f"  ⚠️ Conversion failed for {name}: {e}")
    
    # 3. Apply Rules
    # Trend: MACD Line > 0 AND Price > EMA 200 (Relaxed for BTC/ETH)
    trend_ema_200 = t_last.get('EMA_200', None)
    if name in ["Bitcoin", "Ethereum"]:
        trend_bullish = t_last['MACD_Line'] > 0
        trend_bearish = t_last['MACD_Line'] < 0
    else:
        trend_bullish = t_last['MACD_Line'] > 0 and (trend_ema_200 is None or t_last['Close'] > trend_ema_200)
        trend_bearish = t_last['MACD_Line'] < 0 and (trend_ema_200 is None or t_last['Close'] < trend_ema_200)
    
    trend_bias = "BULLISH" if trend_bullish else ("BEARISH" if trend_bearish else "NEUTRAL")
    
    # Momentum: Histogram > 0 AND Histogram is increasing (Relaxed for BTC/ETH)
    if name in ["Bitcoin", "Ethereum"]:
        mom_bullish = m_last['Histogram'] > 0
        mom_bearish = m_last['Histogram'] < 0
    else:
        mom_bullish = m_last['Histogram'] > 0 and m_last['Histogram'] > m_prev['Histogram']
        mom_bearish = m_last['Histogram'] < 0 and m_last['Histogram'] < m_prev['Histogram']
    
    mom_bias = "BULLISH" if mom_bullish else ("BEARISH" if mom_bearish else "NEUTRAL")
    
    # Entry Signal
    e_signal = "NEUTRAL"
    
    # Filters
    ema_200 = e_last.get('EMA_200', None)
    rsi = e_last.get('RSI', None)
    atr = e_last.get('ATR', 0)
    
    is_above_ema = True if ema_200 is None or e_last['Close'] > ema_200 else False
    is_below_ema = True if ema_200 is None or e_last['Close'] < ema_200 else False
    
    # Relaxed RSI for BTC/ETH
    if name in ["Bitcoin", "Ethereum"]:
        rsi_bullish = True if rsi is None or rsi > 45 else False
        rsi_bearish = True if rsi is None or rsi < 55 else False
    else:
        rsi_bullish = True if rsi is None or rsi > 50 else False
        rsi_bearish = True if rsi is None or rsi < 50 else False
    
    # Stricter MACD: Both lines must be on the same side of zero (Relaxed for BTC/ETH)
    if name in ["Bitcoin", "Ethereum"]:
        macd_bullish = e_last['MACD_Line'] > 0
        macd_bearish = e_last['MACD_Line'] < 0
    else:
        macd_bullish = e_last['MACD_Line'] > 0 and e_last['Signal_Line'] > 0
        macd_bearish = e_last['MACD_Line'] < 0 and e_last['Signal_Line'] < 0

    if e_prev['Histogram'] < 0 and e_last['Histogram'] > 0:
        e_signal = "BUY_CROSS"
    elif e_prev['Histogram'] > 0 and e_last['Histogram'] < 0:
        e_signal = "SELL_CROSS"
    elif e_last['Histogram'] > 0:
        e_signal = "BULLISH_MOM"
    else:
        e_signal = "BEARISH_MOM"

    # 4. Check for active signal and validate
    # current_price is already set above
    active_signal = ACTIVE_SIGNALS.get(name)
    
    # Check if active signal hit SL or TP
    if active_signal:
        # Entry price remains fixed at signal generation
        
        # Initialize TP hits if not present (migration)
        if 'tp_hits' not in active_signal or 'tp1' not in active_signal:
            active_signal['tp_hits'] = active_signal.get('tp_hits', [False, False, False])
            active_signal['current_sl'] = active_signal.get('current_sl', active_signal['sl'])
            
            # Calculate TPs for existing signals based on entry and SL distance
            sl_dist = abs(active_signal['entry_price'] - active_signal['sl'])
            if active_signal['type'] == 'BUY':
                active_signal['tp1'] = active_signal['entry_price'] + (sl_dist * CONFIG['risk']['tp_ratios'][0])
                active_signal['tp2'] = active_signal['entry_price'] + (sl_dist * CONFIG['risk']['tp_ratios'][1])
                active_signal['tp3'] = active_signal['entry_price'] + (sl_dist * CONFIG['risk']['tp_ratios'][2])
            else:
                active_signal['tp1'] = active_signal['entry_price'] - (sl_dist * CONFIG['risk']['tp_ratios'][0])
                active_signal['tp2'] = active_signal['entry_price'] - (sl_dist * CONFIG['risk']['tp_ratios'][1])
                active_signal['tp3'] = active_signal['entry_price'] - (sl_dist * CONFIG['risk']['tp_ratios'][2])
            
        current_sl = active_signal['current_sl']
        
        if active_signal['type'] == 'BUY':
            # Check SL
            if current_price <= current_sl:
                event_type = "TRAIL_SL_HIT" if active_signal['current_sl'] != active_signal['sl'] else "SL_HIT"
                print(f"  🛑 {name}: BUY signal hit {event_type} @ {current_price}")
                log_signal_event(name, event_type, current_price, active_signal)
                active_signal['sl_hit'] = True
                active_signal['exit_price'] = current_price
                active_signal['exit_time'] = datetime.now().isoformat()
                # Capture Screenshot before popping
                if os.environ.get("ENABLE_SCREENSHOTS", "True").lower() == "true":
                    try:
                        date_str = datetime.now().strftime("%Y-%m-%d")
                        folder = BASE_DIR / "past_trades" / date_str
                        filename = f"{name.replace('/', '_')}_{event_type}_{datetime.now().strftime('%H%M%S')}.png"
                        
                        # Create a temporary result dict for the screenshot
                        temp_res = {
                            "instrument": name,
                            "flag": instrument.get('flag', ''),
                            "ltp": current_price,
                            "daily": {"bias": trend_bias},
                            "h4": {"bias": mom_bias},
                            "h1": {"status": e_signal},
                            "signal": active_signal
                        }
                        capture_trade_screenshot(temp_res, event_type, str(folder / filename))
                    except Exception as e:
                        print(f"  ⚠️ Screenshot failed: {e}")

                # Remove immediately from ACTIVE_SIGNALS
                ACTIVE_SIGNALS.pop(name, None)
                save_active_signals()
                active_signal = None
            else:
                # Check TPs and Trailing SL
                # TP1
                if not active_signal['tp_hits'][0] and current_price >= active_signal['tp1']:
                    print(f"  🎯 {name}: BUY signal hit TP1")
                    active_signal['tp_hits'][0] = True
                    log_signal_event(name, "TP1_HIT", current_price, active_signal)
                    if CONFIG['risk']['trailing_sl']['move_to_breakeven_at_tp1']:
                        active_signal['current_sl'] = active_signal['entry_price']
                        print(f"  🛡️ {name}: SL moved to Breakeven")
                        save_active_signals()
                
                # TP2
                if not active_signal['tp_hits'][1] and current_price >= active_signal['tp2']:
                    print(f"  🎯 {name}: BUY signal hit TP2")
                    active_signal['tp_hits'][1] = True
                    log_signal_event(name, "TP2_HIT", current_price, active_signal)
                    if CONFIG['risk']['trailing_sl']['move_to_tp1_at_tp2']:
                        active_signal['current_sl'] = active_signal['tp1']
                        print(f"  🛡️ {name}: SL moved to TP1")
                        save_active_signals()
                        
                # TP3
                if not active_signal['tp_hits'][2] and current_price >= active_signal['tp3']:
                    print(f"  🚀 {name}: BUY signal hit TP3 (Full Exit)")
                    log_signal_event(name, "TP3_HIT", current_price, active_signal)
                    
                    # Capture Screenshot
                    if os.environ.get("ENABLE_SCREENSHOTS", "True").lower() == "true":
                        try:
                            date_str = datetime.now().strftime("%Y-%m-%d")
                            folder = BASE_DIR / "past_trades" / date_str
                            filename = f"{name.replace('/', '_')}_TP3_HIT_{datetime.now().strftime('%H%M%S')}.png"
                            temp_res = {
                                "instrument": name,
                                "flag": instrument.get('flag', ''),
                                "ltp": current_price,
                                "daily": {"bias": trend_bias},
                                "h4": {"bias": mom_bias},
                                "h1": {"status": e_signal},
                                "signal": active_signal
                            }
                            capture_trade_screenshot(temp_res, "TP3 HIT", str(folder / filename))
                        except Exception as e:
                            print(f"  ⚠️ Screenshot failed: {e}")

                    ACTIVE_SIGNALS.pop(name, None)
                    active_signal = None
            
        elif active_signal['type'] == 'SELL':
            # Check SL
            if current_price >= current_sl:
                event_type = "TRAIL_SL_HIT" if active_signal['current_sl'] != active_signal['sl'] else "SL_HIT"
                print(f"  🛑 {name}: SELL signal hit {event_type} @ {current_price}")
                log_signal_event(name, event_type, current_price, active_signal)
                active_signal['sl_hit'] = True
                active_signal['exit_price'] = current_price
                active_signal['exit_time'] = datetime.now().isoformat()
                # Capture Screenshot
                if os.environ.get("ENABLE_SCREENSHOTS", "True").lower() == "true":
                    try:
                        date_str = datetime.now().strftime("%Y-%m-%d")
                        folder = BASE_DIR / "past_trades" / date_str
                        filename = f"{name.replace('/', '_')}_{event_type}_{datetime.now().strftime('%H%M%S')}.png"
                        temp_res = {
                            "instrument": name,
                            "flag": instrument.get('flag', ''),
                            "ltp": current_price,
                            "daily": {"bias": trend_bias},
                            "h4": {"bias": mom_bias},
                            "h1": {"status": e_signal},
                            "signal": active_signal
                        }
                        capture_trade_screenshot(temp_res, event_type, str(folder / filename))
                    except Exception as e:
                        print(f"  ⚠️ Screenshot failed: {e}")

                # Remove immediately from ACTIVE_SIGNALS
                ACTIVE_SIGNALS.pop(name, None)
                save_active_signals()
                active_signal = None
            else:
                # Check TPs and Trailing SL
                # TP1
                if not active_signal['tp_hits'][0] and current_price <= active_signal['tp1']:
                    print(f"  🎯 {name}: SELL signal hit TP1")
                    active_signal['tp_hits'][0] = True
                    log_signal_event(name, "TP1_HIT", current_price, active_signal)
                    if CONFIG['risk']['trailing_sl']['move_to_breakeven_at_tp1']:
                        active_signal['current_sl'] = active_signal['entry_price']
                        print(f"  🛡️ {name}: SL moved to Breakeven")
                        save_active_signals()
                
                # TP2
                if not active_signal['tp_hits'][1] and current_price <= active_signal['tp2']:
                    print(f"  🎯 {name}: SELL signal hit TP2")
                    active_signal['tp_hits'][1] = True
                    log_signal_event(name, "TP2_HIT", current_price, active_signal)
                    if CONFIG['risk']['trailing_sl']['move_to_tp1_at_tp2']:
                        active_signal['current_sl'] = active_signal['tp1']
                        print(f"  🛡️ {name}: SL moved to TP1")
                        save_active_signals()
                        
                # TP3
                if not active_signal['tp_hits'][2] and current_price <= active_signal['tp3']:
                    print(f"  🚀 {name}: SELL signal hit TP3 (Full Exit)")
                    log_signal_event(name, "TP3_HIT", current_price, active_signal)
                    
                    # Capture Screenshot
                    if os.environ.get("ENABLE_SCREENSHOTS", "True").lower() == "true":
                        try:
                            date_str = datetime.now().strftime("%Y-%m-%d")
                            folder = BASE_DIR / "past_trades" / date_str
                            filename = f"{name.replace('/', '_')}_TP3_HIT_{datetime.now().strftime('%H%M%S')}.png"
                            temp_res = {
                                "instrument": name,
                                "flag": instrument.get('flag', ''),
                                "ltp": current_price,
                                "daily": {"bias": trend_bias},
                                "h4": {"bias": mom_bias},
                                "h1": {"status": e_signal},
                                "signal": active_signal
                            }
                            capture_trade_screenshot(temp_res, "TP3 HIT", str(folder / filename))
                        except Exception as e:
                            print(f"  ⚠️ Screenshot failed: {e}")

                    ACTIVE_SIGNALS.pop(name, None)
                    active_signal = None
    
    # Generate new signal if no active signal
    final_signal = active_signal
    status = "WAITING"
    
    if not active_signal:
        if trend_bias == "BULLISH" and mom_bias == "BULLISH" and is_above_ema and rsi_bullish and macd_bullish:
            status = "LOOKING_FOR_BUY"
            # Trigger on fresh cross OR if momentum just started building from a negative histogram
            if e_signal == "BUY_CROSS" or (e_signal == "BULLISH_MOM" and e_prev['Histogram'] <= 0): 
                entry = current_price # Use real-time price for entry
                
                # Dynamic SL based on ATR
                sl_dist = atr * CONFIG['risk']['sl_atr_multiplier']
                if sl_dist == 0: # Fallback
                    sl_dist = 30 * instrument['pip_size']
                
                sl = entry - sl_dist
                
                tp1 = entry + (sl_dist * CONFIG['risk']['tp_ratios'][0])
                tp2 = entry + (sl_dist * CONFIG['risk']['tp_ratios'][1])
                tp3 = entry + (sl_dist * CONFIG['risk']['tp_ratios'][2])
                
                final_signal = {
                    "type": "BUY",
                    "entry_price": entry,
                    "sl": sl,
                    "current_sl": sl,
                    "tp1": tp1,
                    "tp2": tp2,
                    "tp3": tp3,
                    "tp_hits": [False, False, False],
                    "time": datetime.now().isoformat(),
                    "candle_time": e_last.name.isoformat(),
                    "category": category
                }
                ACTIVE_SIGNALS[name] = final_signal
                save_active_signals()
                status = "ACTIVE_BUY"
                print(f"  🆕 {name}: NEW BUY SIGNAL @ {entry:.5f}")
                log_signal_event(name, "ENTRY", entry, final_signal)
                
        elif trend_bias == "BEARISH" and mom_bias == "BEARISH" and is_below_ema and rsi_bearish and macd_bearish:
            status = "LOOKING_FOR_SELL"
            # Trigger on fresh cross OR if momentum just started building from a positive histogram
            if e_signal == "SELL_CROSS" or (e_signal == "BEARISH_MOM" and e_prev['Histogram'] >= 0):
                entry = current_price # Use real-time price for entry
                
                # Dynamic SL based on ATR
                sl_dist = atr * CONFIG['risk']['sl_atr_multiplier']
                if sl_dist == 0: # Fallback
                    sl_dist = 30 * instrument['pip_size']
                    
                sl = entry + sl_dist
                
                tp1 = entry - (sl_dist * CONFIG['risk']['tp_ratios'][0])
                tp2 = entry - (sl_dist * CONFIG['risk']['tp_ratios'][1])
                tp3 = entry - (sl_dist * CONFIG['risk']['tp_ratios'][2])
                
                final_signal = {
                    "type": "SELL",
                    "entry_price": entry,
                    "sl": sl,
                    "current_sl": sl,
                    "tp1": tp1,
                    "tp2": tp2,
                    "tp3": tp3,
                    "tp_hits": [False, False, False],
                    "time": datetime.now().isoformat(),
                    "candle_time": e_last.name.isoformat(),
                    "category": category
                }
                ACTIVE_SIGNALS[name] = final_signal
                save_active_signals()
                status = "ACTIVE_SELL"
                print(f"  🆕 {name}: NEW SELL SIGNAL @ {entry:.5f}")
                log_signal_event(name, "ENTRY", entry, final_signal)
        else:
            status = "CONFLICT (Trend/MOM/Filter Mismatch)"
            
        # Check for reverse signal (close existing opposite position)
        if active_signal:
            if active_signal['type'] == 'BUY' and (trend_bias == "BEARISH" and mom_bias == "BEARISH"):
                if e_signal == "SELL_CROSS":
                    print(f"  🔄 {name}: REVERSE SIGNAL - Closing BUY")
                    ACTIVE_SIGNALS.pop(name, None)
                    save_active_signals()
                    final_signal = None
            elif active_signal['type'] == 'SELL' and (trend_bias == "BULLISH" and mom_bias == "BULLISH"):
                if e_signal == "BUY_CROSS":
                    print(f"  🔄 {name}: REVERSE SIGNAL - Closing SELL")
                    ACTIVE_SIGNALS.pop(name, None)
                    save_active_signals()
                    final_signal = None
    else:
        # Active signal exists, maintain status
        status = f"ACTIVE_{active_signal['type']}"

    return {
        "instrument": name,
        "flag": instrument.get('flag', ''),
        "ltp": current_price,
        "daily": {
            "macd_line": t_last['MACD_Line'],
            "bias": trend_bias,
            "label": trend_label
        },
        "h4": {
            "histogram": m_last['Histogram'],
            "bias": mom_bias,
            "label": mom_label
        },
        "h1": {
            "histogram": e_last['Histogram'],
            "status": e_signal,
            "close": e_last['Close'],
            "label": entry_label,
            "ema_200": float(ema_200) if ema_200 is not None else None,
            "rsi": float(rsi) if rsi is not None else None
        },
        "overall_status": status,
        "signal": final_signal,
        "category": instrument.get('category', 'Other'),
        "timestamp": datetime.now().isoformat()
    }

def main():
    print("=" * 60)
    print("💱 BIASBUSTER MARKET DASHBOARD STRATEGY")
    print("=" * 60)
    
    while True:
        try:
            start_time = time.time()
            print(f"\n🔄 Running analysis {datetime.now().strftime('%H:%M:%S')}...")
            
            # Sequential analysis
            results = []
            for instrument in CONFIG['instruments']:
                try:
                    res = analyze_instrument(instrument)
                    if res:
                        results.append(res)
                except Exception as e:
                    print(f"  ❌ Error analyzing {instrument.get('name', 'Unknown')}: {e}")
            
            for res in results:
                print(f"  👉 {res['instrument']}: {res['overall_status']}")
                if res['signal']:
                    print(f"     ✅ SIGNAL: {res['signal']['type']} @ {res['signal']['entry_price']:.5f}")
            
            # Save to JSON
            output = {
                "last_updated": datetime.now().isoformat(),
                "backend_heartbeat": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data": results
            }
            
            # Save to JSON in the same directory as the script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(script_dir, "forex_macd_signals.json")
            
            with open(json_path, "w") as f:
                json.dump(output, f, indent=2, default=str)
                
            duration = time.time() - start_time
            print(f"💾 Saved to {json_path} (Cycle time: {duration:.2f}s)")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            
        if os.environ.get("RUN_ONCE", "False").lower() == "true":
            print("✅ Single run complete. Exiting...")
            break
            
        print("⏳ Waiting 60s (1 min)...")
        time.sleep(60)

if __name__ == "__main__":
    main()

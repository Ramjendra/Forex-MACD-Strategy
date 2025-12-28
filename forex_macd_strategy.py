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
import pytz


try:
    import yfinance as yf
    import pandas as pd
    import numpy as np
    from trade_screenshot import capture_trade_screenshot
    from retail_sentiment import RetailSentimentAnalyzer
    from telegram_alerts import TelegramAlerts
    from opening_range_tracker import (
        update_opening_range, check_orb_breakout, get_orb_status,
        is_orb_window, cleanup_old_data as cleanup_old_orb
    )
    from premarket_analysis import get_premarket_sentiment, is_premarket_data_fresh
except ImportError as e:
    print(f"❌ Error: Required libraries not installed: {e}")
    print("   Make sure yfinance, pandas, numpy, pillow are installed")
    sys.exit(1)

# ================= NSE FUTURES HELPER FUNCTIONS =================
import calendar
from datetime import timedelta

def get_nse_expiry_date(year, month):
    """Get last Thursday of the month (NSE futures expiry day)"""
    # Get last day of month
    last_day = calendar.monthrange(year, month)[1]
    last_date = datetime(year, month, last_day)
    
    # Find last Thursday (Thursday = 3 in weekday())
    days_to_thursday = (last_date.weekday() - 3) % 7
    expiry_date = last_date - timedelta(days=days_to_thursday)
    return expiry_date

def get_current_nse_contract():
    """
    Get current month contract or next month if 1 day before expiry.
    Returns: (contract_month, contract_year, expiry_date)
    """
    now = datetime.now()
    current_expiry = get_nse_expiry_date(now.year, now.month)
    
    # If today is 1 day before expiry or later, use next month
    rollover_date = current_expiry - timedelta(days=1)
    
    if now.date() >= rollover_date.date():
        # Move to next month
        if now.month == 12:
            next_month = 1
            next_year = now.year + 1
        else:
            next_month = now.month + 1
            next_year = now.year
        
        expiry = get_nse_expiry_date(next_year, next_month)
        contract_month = expiry.strftime("%b").upper()  # JAN, FEB, etc.
        contract_year = expiry.strftime("%y")  # 25, 26, etc.
        return contract_month, contract_year, expiry
    else:
        contract_month = current_expiry.strftime("%b").upper()
        contract_year = current_expiry.strftime("%y")
        return contract_month, contract_year, current_expiry

def get_nse_future_symbol(base_name):
    """
    Get Yahoo Finance symbol for NSE futures with current contract.
    Returns: (symbol, expiry_date, contract_month, contract_year)
    """
    month, year, expiry = get_current_nse_contract()
    
    # Using NSE indices as proxies since Yahoo Finance futures data may be limited
    # For actual futures trading, you'd use broker APIs
    if base_name == "NIFTY":
        symbol = f"^NSEI"  # Nifty 50 index
    elif base_name == "BANKNIFTY":
        symbol = f"^NSEBANK"  # Bank Nifty index
    else:
        symbol = f"{base_name}{year}{month}.NS"
    
    return symbol, expiry, month, year

# ================= CONFIGURATION =================
BASE_DIR = Path(__file__).parent
SIGNALS_FILE = BASE_DIR / "forex_macd_signals.json"
HISTORY_FILE = BASE_DIR / "signal_history.json"
CONFIG = {
    "instruments": [
        {"name": "US Oil (WTI)", "symbol": "CL=F", "pip_size": 0.01, "flag": "🛢️", "category": "Metals/Energy"},
        {"name": "MCX Crude Oil", "symbol": "CL=F", "pip_size": 0.01, "flag": "🇮🇳🛢️", "category": "Indian Indices & Commodities"},
        {"name": "MCX Natural Gas", "symbol": "NG=F", "pip_size": 0.1, "flag": "🇮🇳🔥", "category": "Indian Indices & Commodities"},
        {"name": "MCX Copper", "symbol": "HG=F", "pip_size": 0.05, "flag": "🇮🇳🧱", "category": "Indian Indices & Commodities"},
        {"name": "MCX Gold Mini", "symbol": "GC=F", "pip_size": 0.1, "flag": "🇮🇳🥇", "category": "Indian Indices & Commodities"},
        {"name": "MCX Silver Mini", "symbol": "SI=F", "pip_size": 0.005, "flag": "🇮🇳🥈", "category": "Indian Indices & Commodities"},
        {"name": "MCX Lead", "symbol": "PB=F", "pip_size": 0.05, "flag": "🇮🇳⚙️", "category": "Indian Indices & Commodities"},
        {"name": "MCX Zinc", "symbol": "ZN=F", "pip_size": 0.05, "flag": "🇮🇳🔩", "category": "Indian Indices & Commodities"},
        {"name": "Gold", "symbol": "GC=F", "pip_size": 0.1, "flag": "🥇", "category": "Metals/Energy"},
        {"name": "Silver", "symbol": "SI=F", "pip_size": 0.005, "flag": "🥈", "category": "Metals/Energy"},
        {"name": "Brent Crude Oil", "symbol": "BZ=F", "pip_size": 0.01, "flag": "🇬🇧🛢️", "category": "Metals/Energy"},
        {"name": "Natural Gas", "symbol": "NG=F", "pip_size": 0.001, "flag": "🔥", "category": "Metals/Energy"},
        {"name": "Platinum", "symbol": "PL=F", "pip_size": 0.1, "flag": "💍", "category": "Metals/Energy"},
        {"name": "Palladium", "symbol": "PA=F", "pip_size": 0.1, "flag": "💎", "category": "Metals/Energy"},

        # World Indices
        {"name": "S&P 500", "symbol": "^GSPC", "pip_size": 0.01, "flag": "🇺🇸📊", "category": "World Index"},
        {"name": "Dow Jones", "symbol": "^DJI", "pip_size": 0.01, "flag": "🇺🇸📈", "category": "World Index"},
        {"name": "NASDAQ", "symbol": "^IXIC", "pip_size": 0.01, "flag": "🇺🇸💻", "category": "World Index"},

        {"name": "EUR/USD", "symbol": "EURUSD=X", "pip_size": 0.0001, "flag": "🇪🇺🇺🇸", "category": "Forex"},
        {"name": "GBP/USD", "symbol": "GBPUSD=X", "pip_size": 0.0001, "flag": "🇬🇧🇺🇸", "category": "Forex"},
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

        {"name": "Nifty 50", "symbol": "^NSEI", "pip_size": 0.05, "flag": "🇮🇳", "category": "Indian Indices & Commodities"},
        {"name": "Bank Nifty", "symbol": "^NSEBANK", "pip_size": 0.05, "flag": "🇮🇳🏦", "category": "Indian Indices & Commodities"},
        {"name": "Sensex", "symbol": "^BSESN", "pip_size": 0.05, "flag": "🇮🇳📈", "category": "Indian Indices & Commodities"},
        
        # Top 10 Nifty 50 Stocks
        {"name": "Reliance", "symbol": "RELIANCE.NS", "pip_size": 0.05, "flag": "🇮🇳🏭", "category": "Indian Stocks"},
        {"name": "TCS", "symbol": "TCS.NS", "pip_size": 0.05, "flag": "🇮🇳💻", "category": "Indian Stocks"},
        {"name": "HDFC Bank", "symbol": "HDFCBANK.NS", "pip_size": 0.05, "flag": "🇮🇳🏦", "category": "Indian Stocks"},
        {"name": "Infosys", "symbol": "INFY.NS", "pip_size": 0.05, "flag": "🇮🇳💼", "category": "Indian Stocks"},
        {"name": "ICICI Bank", "symbol": "ICICIBANK.NS", "pip_size": 0.05, "flag": "🇮🇳🏛️", "category": "Indian Stocks"},
        {"name": "Hindustan Unilever", "symbol": "HINDUNILVR.NS", "pip_size": 0.05, "flag": "🇮🇳🧴", "category": "Indian Stocks"},
        {"name": "ITC", "symbol": "ITC.NS", "pip_size": 0.05, "flag": "🇮🇳🚬", "category": "Indian Stocks"},
        {"name": "SBI", "symbol": "SBIN.NS", "pip_size": 0.05, "flag": "🇮🇳🏢", "category": "Indian Stocks"},
        {"name": "Bharti Airtel", "symbol": "BHARTIARTL.NS", "pip_size": 0.05, "flag": "🇮🇳📱", "category": "Indian Stocks"},
        {"name": "Kotak Bank", "symbol": "KOTAKBANK.NS", "pip_size": 0.05, "flag": "🇮🇳💳", "category": "Indian Stocks"},
        {"name": "Axis Bank", "symbol": "AXISBANK.NS", "pip_size": 0.05, "flag": "🇮🇳🏦", "category": "Indian Stocks"},
        {"name": "Larsen & Toubro", "symbol": "LT.NS", "pip_size": 0.05, "flag": "🇮🇳🏗️", "category": "Indian Stocks"},
        {"name": "Asian Paints", "symbol": "ASIANPAINT.NS", "pip_size": 0.05, "flag": "🇮🇳🎨", "category": "Indian Stocks"},
        {"name": "Maruti Suzuki", "symbol": "MARUTI.NS", "pip_size": 0.05, "flag": "🇮🇳🚗", "category": "Indian Stocks"},
        {"name": "HCL Tech", "symbol": "HCLTECH.NS", "pip_size": 0.05, "flag": "🇮🇳💻", "category": "Indian Stocks"},
        {"name": "Bajaj Finance", "symbol": "BAJFINANCE.NS", "pip_size": 0.05, "flag": "🇮🇳💰", "category": "Indian Stocks"},
        {"name": "Wipro", "symbol": "WIPRO.NS", "pip_size": 0.05, "flag": "🇮🇳💼", "category": "Indian Stocks"},
        {"name": "Sun Pharma", "symbol": "SUNPHARMA.NS", "pip_size": 0.05, "flag": "🇮🇳💊", "category": "Indian Stocks"},
        {"name": "Titan", "symbol": "TITAN.NS", "pip_size": 0.05, "flag": "🇮🇳⌚", "category": "Indian Stocks"},
        {"name": "Nestle India", "symbol": "NESTLEIND.NS", "pip_size": 0.05, "flag": "🇮🇳🍫", "category": "Indian Stocks"},
        {"name": "UltraTech Cement", "symbol": "ULTRACEMCO.NS", "pip_size": 0.05, "flag": "🇮🇳🏗️", "category": "Indian Stocks"},
        {"name": "Tech Mahindra", "symbol": "TECHM.NS", "pip_size": 0.05, "flag": "🇮🇳💻", "category": "Indian Stocks"},
        {"name": "Mahindra & Mahindra", "symbol": "M&M.NS", "pip_size": 0.05, "flag": "🇮🇳🚜", "category": "Indian Stocks"},
        {"name": "Power Grid", "symbol": "POWERGRID.NS", "pip_size": 0.05, "flag": "🇮🇳⚡", "category": "Indian Stocks"},
        {"name": "NTPC", "symbol": "NTPC.NS", "pip_size": 0.05, "flag": "🇮🇳⚡", "category": "Indian Stocks"},
        {"name": "Bajaj Auto", "symbol": "BAJAJ-AUTO.NS", "pip_size": 0.05, "flag": "🇮🇳🏍️", "category": "Indian Stocks"},
        {"name": "Tata Steel", "symbol": "TATASTEEL.NS", "pip_size": 0.05, "flag": "🇮🇳🏭", "category": "Indian Stocks"},
        {"name": "Adani Ports", "symbol": "ADANIPORTS.NS", "pip_size": 0.05, "flag": "🇮🇳🚢", "category": "Indian Stocks"},
        {"name": "JSW Steel", "symbol": "JSWSTEEL.NS", "pip_size": 0.05, "flag": "🇮🇳🏭", "category": "Indian Stocks"},
        {"name": "Tata Motors", "symbol": "TATAMOTORS.NS", "pip_size": 0.05, "flag": "🇮��🚗", "category": "Indian Stocks"},
        {"name": "IndusInd Bank", "symbol": "INDUSINDBK.NS", "pip_size": 0.05, "flag": "🇮🇳🏦", "category": "Indian Stocks"},
        {"name": "Coal India", "symbol": "COALINDIA.NS", "pip_size": 0.05, "flag": "🇮🇳⛏️", "category": "Indian Stocks"},
        {"name": "Grasim", "symbol": "GRASIM.NS", "pip_size": 0.05, "flag": "🇮🇳🏭", "category": "Indian Stocks"},
        {"name": "Cipla", "symbol": "CIPLA.NS", "pip_size": 0.05, "flag": "🇮🇳��", "category": "Indian Stocks"},
        {"name": "Eicher Motors", "symbol": "EICHERMOT.NS", "pip_size": 0.05, "flag": "🇮🇳🏍️", "category": "Indian Stocks"},
        {"name": "Hero MotoCorp", "symbol": "HEROMOTOCO.NS", "pip_size": 0.05, "flag": "🇮🇳🏍️", "category": "Indian Stocks"},
        {"name": "ONGC", "symbol": "ONGC.NS", "pip_size": 0.05, "flag": "🇮🇳🛢️", "category": "Indian Stocks"},
        {"name": "Britannia", "symbol": "BRITANNIA.NS", "pip_size": 0.05, "flag": "🇮🇳🍪", "category": "Indian Stocks"},
        {"name": "Shree Cement", "symbol": "SHREECEM.NS", "pip_size": 0.05, "flag": "🇮🇳🏗️", "category": "Indian Stocks"},
        {"name": "Divi's Labs", "symbol": "DIVISLAB.NS", "pip_size": 0.05, "flag": "🇮🇳💊", "category": "Indian Stocks"},
        {"name": "Bajaj Finserv", "symbol": "BAJAJFINSV.NS", "pip_size": 0.05, "flag": "🇮🇳💰", "category": "Indian Stocks"},
        {"name": "Hindalco", "symbol": "HINDALCO.NS", "pip_size": 0.05, "flag": "🇮🇳🏭", "category": "Indian Stocks"},
        {"name": "UPL", "symbol": "UPL.NS", "pip_size": 0.05, "flag": "🇮🇳🌾", "category": "Indian Stocks"},
        {"name": "Tata Consumer", "symbol": "TATACONSUM.NS", "pip_size": 0.05, "flag": "🇮🇳☕", "category": "Indian Stocks"},
        {"name": "Dr Reddy's", "symbol": "DRREDDY.NS", "pip_size": 0.05, "flag": "🇳💊", "category": "Indian Stocks"},
        {"name": "Apollo Hospitals", "symbol": "APOLLOHOSP.NS", "pip_size": 0.05, "flag": "🇮🇳🏥", "category": "Indian Stocks"},
        {"name": "Adani Enterprises", "symbol": "ADANIENT.NS", "pip_size": 0.05, "flag": "🇮🇳🏭", "category": "Indian Stocks"},
        {"name": "SBI Life", "symbol": "SBILIFE.NS", "pip_size": 0.05, "flag": "🇮🇳💼", "category": "Indian Stocks"},
        {"name": "HDFC Life", "symbol": "HDFCLIFE.NS", "pip_size": 0.05, "flag": "🇮🇳💼", "category": "Indian Stocks"},
        {"name": "BPCL", "symbol": "BPCL.NS", "pip_size": 0.05, "flag": "🇮🇳⛽", "category": "Indian Stocks"},

        # Cryptocurrencies
        {"name": "Bitcoin", "symbol": "BTC-USD", "pip_size": 1.0, "flag": "₿", "category": "Crypto Scalping"},
        {"name": "Ethereum", "symbol": "ETH-USD", "pip_size": 0.1, "flag": "Ξ", "category": "Crypto Scalping"},
        {"name": "BNB", "symbol": "BNB-USD", "pip_size": 0.1, "flag": "🔶", "category": "Crypto Scalping"},
        {"name": "XRP", "symbol": "XRP-USD", "pip_size": 0.0001, "flag": "💧", "category": "Crypto Scalping"},
        {"name": "Cardano", "symbol": "ADA-USD", "pip_size": 0.0001, "flag": "🔷", "category": "Crypto Scalping"},
        {"name": "Solana", "symbol": "SOL-USD", "pip_size": 0.01, "flag": "◎", "category": "Crypto Scalping"},
        {"name": "Polkadot", "symbol": "DOT-USD", "pip_size": 0.01, "flag": "⚫", "category": "Crypto Scalping"},
        {"name": "Dogecoin", "symbol": "DOGE-USD", "pip_size": 0.00001, "flag": "🐕", "category": "Crypto Scalping"},
        {"name": "Avalanche", "symbol": "AVAX-USD", "pip_size": 0.01, "flag": "🔺", "category": "Crypto Scalping"},
        {"name": "Chainlink", "symbol": "LINK-USD", "pip_size": 0.01, "flag": "🔗", "category": "Crypto Scalping"},
        
        # NSE Futures (Auto-Rollover)
        {"name": "Nifty Future", "symbol": "DYNAMIC", "pip_size": 0.05, "flag": "🇮🇳📈", "category": "NSE Live", "base_symbol": "NIFTY"},
        {"name": "Bank Nifty Future", "symbol": "DYNAMIC", "pip_size": 0.05, "flag": "🇮🇳🏦", "category": "NSE Live", "base_symbol": "BANKNIFTY"},
        
        # Indian Indices (Spot)
        {"name": "Nifty IT Index", "symbol": "^CNXIT", "pip_size": 0.05, "flag": "🇮🇳💻", "category": "Indian Indices & Commodities"},
        {"name": "Bank Nifty Index", "symbol": "^NSEBANK", "pip_size": 0.05, "flag": "🇮🇳🏦", "category": "Indian Indices & Commodities"},
        
        # Currency (Forex)
        {"name": "USD/INR", "symbol": "USDINR=X", "pip_size": 0.0025, "flag": "🇺🇸🇮🇳", "category": "Forex"}
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
    },
    "nse_specific": {
        "sl_atr_multiplier": 2.5,      # Safer SL for 3-4 day swing trades
        "volume_multiplier": 1.2,       # Volume must be 1.2x average for signal
        "volume_lookback": 20,          # Days to calculate average volume
        "orb_enabled": True,            # Enable Opening Range Breakout
        "orb_duration_minutes": 15,     # Track 9:15-9:30 AM (15 minutes)
        "premarket_filter": True,       # Use global cues for first hour
        "first_hour_end": "10:15"       # Pre-market filter active till 10:15 AM IST
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

# Initialize sentiment analyzer
print("📊 Loading retail sentiment data...")
sentiment_analyzer = RetailSentimentAnalyzer()
try:
    sentiment_analyzer.load_manual_sentiment()
    print("✅ Sentiment data loaded successfully")
except Exception as e:
    print(f"⚠️  Sentiment data not available: {e}")
    print("   Run './morning_routine.sh' to update sentiment data")

# Initialize Telegram alerts
print("📱 Initializing Telegram alerts...")
telegram_alerts = None
try:
    telegram_alerts = TelegramAlerts()
    print("✅ Telegram alerts enabled")
except Exception as e:
    print(f"⚠️  Telegram alerts disabled: {e}")
    telegram_alerts = None

# Initialize pre-market analysis
print("🌍 Loading pre-market global cues...")
premarket_data = None
try:
    if is_premarket_data_fresh():
        premarket_data = get_premarket_sentiment()
        print(f"✅ Pre-market sentiment: {premarket_data.get('overall_sentiment', 'UNKNOWN')}")
    else:
        print("⚠️  Pre-market data is stale. Run 'python3 premarket_analysis.py' to update")
except Exception as e:
    print(f"⚠️  Pre-market analysis unavailable: {e}")

# Cleanup old ORB data
try:
    cleanup_old_orb(days_to_keep=7)
except Exception as e:
    print(f"⚠️  ORB cleanup failed: {e}")


# ================= DATA & INDICATORS =================
def fetch_data(symbol: str, interval: str, period: str) -> pd.DataFrame:
    """Fetch data from Yahoo Finance with retries."""
    for attempt in range(3):
        try:
            ticker = yf.Ticker(symbol)
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

def check_volume_confirmation(df: pd.DataFrame, lookback: int = 20, multiplier: float = 1.2) -> tuple:
    """
    Check if current volume is above average for NSE instruments.
    Returns: (is_confirmed, current_volume, avg_volume, ratio)
    """
    if 'Volume' not in df.columns or df['Volume'].sum() == 0:
        return True, 0, 0, 0  # Skip volume check if no data
    
    avg_volume = df['Volume'].tail(lookback).mean()
    current_volume = df['Volume'].iloc[-1]
    
    if avg_volume == 0:
        return True, current_volume, avg_volume, 0
    
    ratio = current_volume / avg_volume
    is_confirmed = ratio >= multiplier
    
    return is_confirmed, current_volume, avg_volume, ratio

def log_signal_event(instrument, event_type, price, signal_data=None, trade_metrics=None):
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
        
        # Add trade metrics if provided (for TP/SL hits)
        if trade_metrics:
            event.update(trade_metrics)

        history.append(event)
        
        # Keep only last 100 events
        history = history[-100:]
        
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
            
    except Exception as e:
        print(f"  ❌ Error logging event: {e}")

def calculate_lifecycle_status(signal, has_reentry=False):
    """Calculate the lifecycle status of a signal based on its current state."""
    if not signal:
        return None
    
    # Check signal age (within 1 hour = "New Signal")
    try:
        signal_time = datetime.fromisoformat(signal['time'])
        age_hours = (datetime.now() - signal_time).total_seconds() / 3600
        
        if age_hours < 1:
            return "New Signal"
    except:
        pass
    
    # Check for reentry opportunity
    if has_reentry:
        return "Reentry Opportunity"
    
    # Check for partial TP hits
    tp_hits = signal.get('tp_hits', [False, False, False])
    if any(tp_hits):
        return "Partial TP Hit"
    
    # Check for trailing SL active
    current_sl = signal.get('current_sl')
    initial_sl = signal.get('sl')
    if current_sl is not None and initial_sl is not None and current_sl != initial_sl:
        return "Trailing SL Active"
    
    # Default active state
    return "Active"

def calculate_trade_metrics(instrument_name, entry_price, exit_price, signal_type, entry_time, exit_time, sl_price, pip_size):
    """Calculate comprehensive trade metrics for history"""
    
    # P/L in points/pips
    if signal_type == 'BUY':
        pnl_points = (exit_price - entry_price) / pip_size
    else:
        pnl_points = (entry_price - exit_price) / pip_size
    
    # P/L percentage
    if signal_type == 'BUY':
        pnl_percent = ((exit_price - entry_price) / entry_price) * 100
    else:
        pnl_percent = ((entry_price - exit_price) / entry_price) * 100
    
    # Trade duration
    try:
        entry_dt = datetime.fromisoformat(entry_time) if isinstance(entry_time, str) else entry_time
        exit_dt = datetime.fromisoformat(exit_time) if isinstance(exit_time, str) else exit_time
        duration_seconds = (exit_dt - entry_dt).total_seconds()
        duration_hours = int(duration_seconds // 3600)
        duration_mins = int((duration_seconds % 3600) // 60)
        duration = f"{duration_hours}h {duration_mins}m"
    except:
        duration = "N/A"
    
    # Risk-Reward calculation
    sl_distance = abs(entry_price - sl_price)
    rr_planned = 1.5  # Default from CONFIG
    
    if sl_distance > 0:
        actual_profit = abs(exit_price - entry_price)
        rr_achieved = actual_profit / sl_distance
    else:
        rr_achieved = 0
    
    return {
        "pnl_points": round(pnl_points, 1),
        "pnl_percent": round(pnl_percent, 2),
        "duration": duration,
        "rr_planned": rr_planned,
        "rr_achieved": round(rr_achieved, 2)
    }

# ================= STRATEGY LOGIC =================
def analyze_instrument(instrument: Dict) -> Dict:
    symbol = instrument['symbol']
    name = instrument['name']
    
    # Handle NSE Futures with dynamic contract rollover
    contract_info = None
    if instrument.get('category') == 'NSE Live':
        base_symbol = instrument.get('base_symbol')
        symbol, expiry, month, year = get_nse_future_symbol(base_symbol)
        contract_info = {
            "contract": f"{month} {year}",
            "expiry": expiry.strftime("%d-%b-%Y"),
            "days_to_expiry": (expiry - datetime.now()).days
        }
        print(f"\n📊 Analyzing {name} ({symbol})...")
        print(f"  📅 Contract: {month} {year} | Expiry: {expiry.strftime('%d-%b-%Y')} | Days: {contract_info['days_to_expiry']}")
    else:
        print(f"\n📊 Analyzing {name} ({symbol})...")
    
    category = instrument.get('category', 'Forex')
    
    # Standardized Timeframes for all categories:
    # Trend: 1D
    # Momentum: 4H (resampled from 1H)
    # Entry: 1H (default) OR 15m (for Stock Scalping)
    
    trend_df = fetch_data(symbol, "1d", "2y")
    mom_df_raw = fetch_data(symbol, "1h", "1y")
    
    # Use 15-min entry for Stock Scalping, 1-hour for everything else
    if category == "Stock Scalping":
        entry_df = fetch_data(symbol, "15m", "30d")
        entry_label = "15m Entry"
    else:
        entry_df = fetch_data(symbol, "1h", "30d")
        entry_label = "1H Entry"
    
    if trend_df.empty or entry_df.empty or mom_df_raw.empty:
        print(f"  ⚠️ Insufficient data for {name}")
        return None
        
    # Resample 1H to 4H for Momentum
    mom_df_raw.index = pd.to_datetime(mom_df_raw.index)
    mom_df = mom_df_raw.resample('4h').agg({
        'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
    }).dropna()
    
    trend_label = "1D Trend"
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
                elif name in ["MCX Silver", "MCX Silver Mini"]:
                    # Convert Ounce to 1kg: Price * 32.1507
                    current_price = latest_price * 32.1507 * rate
                elif name == "MCX Copper":
                    # Convert lb to 1kg: Price * 2.20462 * Premium (approx 2.6%)
                    current_price = latest_price * 2.20462 * rate * 1.026
                elif name == "MCX Lead":
                    # Convert lb to 1kg: Price * 2.20462
                    current_price = latest_price * 2.20462 * rate
                elif name == "MCX Zinc":
                    # Convert lb to 1kg: Price * 2.20462
                    current_price = latest_price * 2.20462 * rate
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
                # Send Telegram alert
                if telegram_alerts:
                    try:
                        is_trailing = active_signal['current_sl'] != active_signal['sl']
                        telegram_alerts.send_sl_hit_alert(name, active_signal, current_price, is_trailing)
                    except Exception as e:
                        print(f"  ⚠️ Telegram alert failed: {e}")
                # Calculate trade metrics
                metrics = calculate_trade_metrics(
                    name, active_signal['entry_price'], current_price, 'BUY',
                    active_signal['time'], datetime.now().isoformat(),
                    active_signal['sl'], instrument['pip_size']
                )
                log_signal_event(name, event_type, current_price, active_signal, metrics)
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
                    # Send Telegram alert
                    if telegram_alerts:
                        try:
                            telegram_alerts.send_tp_hit_alert(name, 1, active_signal, current_price)
                        except Exception as e:
                            print(f"  ⚠️ Telegram alert failed: {e}")
                    if CONFIG['risk']['trailing_sl']['move_to_breakeven_at_tp1']:
                        active_signal['current_sl'] = active_signal['entry_price']
                        active_signal['lifecycle_status'] = "Trailing SL Active"
                        print(f"  🛡️ {name}: SL moved to Breakeven")
                        save_active_signals()
                    else:
                        active_signal['lifecycle_status'] = "Partial TP Hit"
                        save_active_signals()
                
                # TP2
                if not active_signal['tp_hits'][1] and current_price >= active_signal['tp2']:
                    print(f"  🎯 {name}: BUY signal hit TP2")
                    active_signal['tp_hits'][1] = True
                    log_signal_event(name, "TP2_HIT", current_price, active_signal)
                    # Send Telegram alert
                    if telegram_alerts:
                        try:
                            telegram_alerts.send_tp_hit_alert(name, 2, active_signal, current_price)
                        except Exception as e:
                            print(f"  ⚠️ Telegram alert failed: {e}")
                    if CONFIG['risk']['trailing_sl']['move_to_tp1_at_tp2']:
                        active_signal['current_sl'] = active_signal['tp1']
                        active_signal['lifecycle_status'] = "Trailing SL Active"
                        print(f"  🛡️ {name}: SL moved to TP1")
                        save_active_signals()
                    else:
                        active_signal['lifecycle_status'] = "Partial TP Hit"
                        save_active_signals()
                        
                # TP3
                if not active_signal['tp_hits'][2] and current_price >= active_signal['tp3']:
                    print(f"  🚀 {name}: BUY signal hit TP3 (Full Exit)")
                    # Calculate trade metrics
                    metrics = calculate_trade_metrics(
                        name, active_signal['entry_price'], current_price, 'BUY',
                        active_signal['time'], datetime.now().isoformat(),
                        active_signal['sl'], instrument['pip_size']
                    )
                    log_signal_event(name, "TP3_HIT", current_price, active_signal, metrics)
                    # Send Telegram alert
                    if telegram_alerts:
                        try:
                            telegram_alerts.send_tp_hit_alert(name, 3, active_signal, current_price)
                        except Exception as e:
                            print(f"  ⚠️ Telegram alert failed: {e}")
                    
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
                # Send Telegram alert
                if telegram_alerts:
                    try:
                        is_trailing = active_signal['current_sl'] != active_signal['sl']
                        telegram_alerts.send_sl_hit_alert(name, active_signal, current_price, is_trailing)
                    except Exception as e:
                        print(f"  ⚠️ Telegram alert failed: {e}")
                # Calculate trade metrics
                metrics = calculate_trade_metrics(
                    name, active_signal['entry_price'], current_price, 'SELL',
                    active_signal['time'], datetime.now().isoformat(),
                    active_signal['sl'], instrument['pip_size']
                )
                log_signal_event(name, event_type, current_price, active_signal, metrics)
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
                    # Send Telegram alert
                    if telegram_alerts:
                        try:
                            telegram_alerts.send_tp_hit_alert(name, 1, active_signal, current_price)
                        except Exception as e:
                            print(f"  ⚠️ Telegram alert failed: {e}")
                    if CONFIG['risk']['trailing_sl']['move_to_breakeven_at_tp1']:
                        active_signal['current_sl'] = active_signal['entry_price']
                        active_signal['lifecycle_status'] = "Trailing SL Active"
                        print(f"  🛡️ {name}: SL moved to Breakeven")
                        save_active_signals()
                    else:
                        active_signal['lifecycle_status'] = "Partial TP Hit"
                        save_active_signals()
                
                # TP2
                if not active_signal['tp_hits'][1] and current_price <= active_signal['tp2']:
                    print(f"  🎯 {name}: SELL signal hit TP2")
                    active_signal['tp_hits'][1] = True
                    log_signal_event(name, "TP2_HIT", current_price, active_signal)
                    # Send Telegram alert
                    if telegram_alerts:
                        try:
                            telegram_alerts.send_tp_hit_alert(name, 2, active_signal, current_price)
                        except Exception as e:
                            print(f"  ⚠️ Telegram alert failed: {e}")
                    if CONFIG['risk']['trailing_sl']['move_to_tp1_at_tp2']:
                        active_signal['current_sl'] = active_signal['tp1']
                        active_signal['lifecycle_status'] = "Trailing SL Active"
                        print(f"  🛡️ {name}: SL moved to TP1")
                        save_active_signals()
                    else:
                        active_signal['lifecycle_status'] = "Partial TP Hit"
                        save_active_signals()
                        
                # TP3
                if not active_signal['tp_hits'][2] and current_price <= active_signal['tp3']:
                    print(f"  🚀 {name}: SELL signal hit TP3 (Full Exit)")
                    # Calculate trade metrics
                    metrics = calculate_trade_metrics(
                        name, active_signal['entry_price'], current_price, 'SELL',
                        active_signal['time'], datetime.now().isoformat(),
                        active_signal['sl'], instrument['pip_size']
                    )
                    log_signal_event(name, "TP3_HIT", current_price, active_signal, metrics)
                    # Send Telegram alert
                    if telegram_alerts:
                        try:
                            telegram_alerts.send_tp_hit_alert(name, 3, active_signal, current_price)
                        except Exception as e:
                            print(f"  ⚠️ Telegram alert failed: {e}")
                    
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
    
    # ================= RE-ENTRY DETECTION (ENHANCED WITH FIBONACCI) =================
    # Per-category reentry detection with Fibonacci levels and strength scoring
    re_entry_opportunity = None
    
    # Enable reentry only for Forex category
    REENTRY_ENABLED_CATEGORIES = ['Forex']
    
    if active_signal and category in REENTRY_ENABLED_CATEGORIES:
        entry_price = active_signal['entry_price']
        signal_type = active_signal['type']
        current_sl = active_signal.get('current_sl', active_signal['sl'])
        
        # Calculate pullback from entry
        pullback_pips = abs(current_price - entry_price) / instrument['pip_size']
        
        # Only proceed if pullback is within 5-25 pips range
        if 5 <= pullback_pips <= 25:
            # Calculate swing high/low from recent 20 candles for Fibonacci
            lookback = min(20, len(entry_macd))
            recent_candles = entry_macd.iloc[-lookback:]
            
            # Fibonacci retracement levels
            fib_levels = {
                '23.6%': 0.236,
                '38.2%': 0.382,
                '50.0%': 0.500,
                '61.8%': 0.618
            }
            
            # For SELL positions
            if signal_type == 'SELL':
                # Check if price pulled back UP (against our sell)
                if current_price > entry_price:
                    # Find swing high and low for Fibonacci calculation
                    swing_high = recent_candles['High'].max()
                    swing_low = entry_price  # Entry is our reference low
                    fib_range = swing_high - swing_low
                    
                    # Calculate Fibonacci retracement levels
                    fib_prices = {
                        level: swing_low + (fib_range * ratio)
                        for level, ratio in fib_levels.items()
                    }
                    
                    # Find closest Fibonacci level to current price
                    closest_fib = min(fib_prices.items(), key=lambda x: abs(x[1] - current_price))
                    fib_level_name, fib_price = closest_fib
                    fib_distance_pips = abs(current_price - fib_price) / instrument['pip_size']
                    
                    # Check for rejection at current candle
                    recent_high = e_last['High']
                    recent_close = e_last['Close']
                    recent_low = e_last['Low']
                    candle_body = abs(recent_close - e_last['Open'])
                    upper_wick = recent_high - max(recent_close, e_last['Open'])
                    
                    # Rejection criteria: upper wick > 2x body AND histogram negative
                    is_rejection = (upper_wick > 2 * candle_body) and (e_last['Histogram'] < 0)
                    
                    # Near Fibonacci level (within 3 pips)
                    near_fib = fib_distance_pips <= 3
                    
                    if is_rejection or near_fib:
                        # Calculate strength score (0-100)
                        strength = 0
                        
                        # Fibonacci alignment (30 points)
                        if fib_distance_pips <= 1:
                            strength += 30
                        elif fib_distance_pips <= 3:
                            strength += 20
                        elif fib_distance_pips <= 5:
                            strength += 10
                        
                        # Histogram strength (25 points)
                        hist_strength = abs(e_last['Histogram'])
                        if hist_strength > 0.5:
                            strength += 25
                        elif hist_strength > 0.2:
                            strength += 15
                        elif hist_strength > 0:
                            strength += 5
                        
                        # RSI confirmation (20 points)
                        rsi_val = e_last.get('RSI', 50)
                        if rsi_val < 40:  # Oversold on pullback = good for sell reentry
                            strength += 20
                        elif rsi_val < 50:
                            strength += 10
                        
                        # Rejection candle quality (25 points)
                        if upper_wick > 3 * candle_body:
                            strength += 25
                        elif upper_wick > 2 * candle_body:
                            strength += 15
                        elif upper_wick > candle_body:
                            strength += 5
                        
                        # Calculate risk-reward ratio
                        # Risk: Distance from current price to current SL
                        # Reward: Distance from current price to TP1
                        risk_distance = abs(current_price - current_sl)
                        reward_distance = abs(active_signal.get('tp1', entry_price) - current_price)
                        risk_reward_ratio = reward_distance / risk_distance if risk_distance > 0 else 0
                        
                        # Only show if strength >= 40 and R:R >= 1.5
                        if strength >= 40 and risk_reward_ratio >= 1.5:
                            re_entry_opportunity = {
                                "type": "ADD_TO_SELL",
                                "strength": int(strength),
                                "reason": f"Price at {fib_level_name} Fib ({pullback_pips:.1f} pips pullback)",
                                "suggested_entry": round(current_price, 5),
                                "rejection_zone": f"{fib_price - (2 * instrument['pip_size']):.5f} - {fib_price + (2 * instrument['pip_size']):.5f}",
                                "fib_level": fib_level_name,
                                "fib_price": round(fib_price, 5),
                                "confirmation": f"Histogram: {e_last['Histogram']:.3f} | RSI: {rsi_val:.1f} | Wick: {upper_wick:.5f}",
                                "risk_reward": f"1:{risk_reward_ratio:.1f}"
                            }
                            print(f"  🔄 {name}: RE-ENTRY [{strength}%] - {re_entry_opportunity['reason']} | R:R {re_entry_opportunity['risk_reward']}")
                            # Send Telegram alert
                            if telegram_alerts:
                                try:
                                    telegram_alerts.send_reentry_alert(name, re_entry_opportunity, active_signal)
                                except Exception as e:
                                    print(f"  ⚠️ Telegram alert failed: {e}")
            
            # For BUY positions  
            elif signal_type == 'BUY':
                # Check if price pulled back DOWN (against our buy)
                if current_price < entry_price:
                    # Find swing high and low for Fibonacci calculation
                    swing_low = recent_candles['Low'].min()
                    swing_high = entry_price  # Entry is our reference high
                    fib_range = swing_high - swing_low
                    
                    # Calculate Fibonacci retracement levels (from high to low)
                    fib_prices = {
                        level: swing_high - (fib_range * ratio)
                        for level, ratio in fib_levels.items()
                    }
                    
                    # Find closest Fibonacci level to current price
                    closest_fib = min(fib_prices.items(), key=lambda x: abs(x[1] - current_price))
                    fib_level_name, fib_price = closest_fib
                    fib_distance_pips = abs(current_price - fib_price) / instrument['pip_size']
                    
                    # Check for rejection at current candle
                    recent_low = e_last['Low']
                    recent_close = e_last['Close']
                    recent_high = e_last['High']
                    candle_body = abs(recent_close - e_last['Open'])
                    lower_wick = min(recent_close, e_last['Open']) - recent_low
                    
                    # Rejection criteria: lower wick > 2x body AND histogram positive
                    is_rejection = (lower_wick > 2 * candle_body) and (e_last['Histogram'] > 0)
                    
                    # Near Fibonacci level (within 3 pips)
                    near_fib = fib_distance_pips <= 3
                    
                    if is_rejection or near_fib:
                        # Calculate strength score (0-100)
                        strength = 0
                        
                        # Fibonacci alignment (30 points)
                        if fib_distance_pips <= 1:
                            strength += 30
                        elif fib_distance_pips <= 3:
                            strength += 20
                        elif fib_distance_pips <= 5:
                            strength += 10
                        
                        # Histogram strength (25 points)
                        hist_strength = abs(e_last['Histogram'])
                        if hist_strength > 0.5:
                            strength += 25
                        elif hist_strength > 0.2:
                            strength += 15
                        elif hist_strength > 0:
                            strength += 5
                        
                        # RSI confirmation (20 points)
                        rsi_val = e_last.get('RSI', 50)
                        if rsi_val > 60:  # Overbought on pullback = good for buy reentry
                            strength += 20
                        elif rsi_val > 50:
                            strength += 10
                        
                        # Rejection candle quality (25 points)
                        if lower_wick > 3 * candle_body:
                            strength += 25
                        elif lower_wick > 2 * candle_body:
                            strength += 15
                        elif lower_wick > candle_body:
                            strength += 5
                        
                        # Calculate risk-reward ratio
                        risk_distance = abs(current_price - current_sl)
                        reward_distance = abs(active_signal.get('tp1', entry_price) - current_price)
                        risk_reward_ratio = reward_distance / risk_distance if risk_distance > 0 else 0
                        
                        # Only show if strength >= 40 and R:R >= 1.5
                        if strength >= 40 and risk_reward_ratio >= 1.5:
                            re_entry_opportunity = {
                                "type": "ADD_TO_BUY",
                                "strength": int(strength),
                                "reason": f"Price at {fib_level_name} Fib ({pullback_pips:.1f} pips pullback)",
                                "suggested_entry": round(current_price, 5),
                                "rejection_zone": f"{fib_price - (2 * instrument['pip_size']):.5f} - {fib_price + (2 * instrument['pip_size']):.5f}",
                                "fib_level": fib_level_name,
                                "fib_price": round(fib_price, 5),
                                "confirmation": f"Histogram: {e_last['Histogram']:.3f} | RSI: {rsi_val:.1f} | Wick: {lower_wick:.5f}",
                                "risk_reward": f"1:{risk_reward_ratio:.1f}"
                            }
                            print(f"  🔄 {name}: RE-ENTRY [{strength}%] - {re_entry_opportunity['reason']} | R:R {re_entry_opportunity['risk_reward']}")
                            # Send Telegram alert
                            if telegram_alerts:
                                try:
                                    telegram_alerts.send_reentry_alert(name, re_entry_opportunity, active_signal)
                                except Exception as e:
                                    print(f"  ⚠️ Telegram alert failed: {e}")
    
    
    # Generate new signal if no active signal
    final_signal = active_signal
    status = "WAITING"
    
    # Indian Market Hours Check
    can_generate_signal = True
    ist = pytz.timezone('Asia/Kolkata')
    current_time_ist = datetime.now(ist)
    current_hour = current_time_ist.hour
    current_minute = current_time_ist.minute
    
    # MCX Market Hours: 9:00 AM to 11:55 PM (09:00 to 23:55)
    if name.startswith("MCX"):
        if current_hour < 9 or (current_hour == 23 and current_minute > 55) or current_hour >= 24:
            can_generate_signal = False
            print(f"  ⏰ {name}: Outside MCX market hours (Current: {current_time_ist.strftime('%H:%M IST')}). Skipping signal generation.")
    
    # NSE Equity Futures Market Hours: 9:15 AM to 3:30 PM (09:15 to 15:30)
    elif name in ["Nifty 50", "Bank Nifty", "Sensex"] or category == "Indian Stocks":
        if current_hour < 9 or (current_hour == 9 and current_minute < 15) or current_hour > 15 or (current_hour == 15 and current_minute > 30):
            can_generate_signal = False
            print(f"  ⏰ {name}: Outside NSE market hours (Current: {current_time_ist.strftime('%H:%M IST')}). Skipping signal generation.")
    
    if not active_signal and can_generate_signal:
        if trend_bias == "BULLISH" and mom_bias == "BULLISH" and is_above_ema and rsi_bullish and macd_bullish:
            status = "LOOKING_FOR_BUY"
            # Trigger on fresh cross OR if momentum just started building from a negative histogram
            if e_signal == "BUY_CROSS" or (e_signal == "BULLISH_MOM" and e_prev['Histogram'] <= 0):
                # Define entry, sl_dist, and tp_ratios BEFORE using them
                entry = current_price  # Use real-time price for entry
                
                # Dynamic SL based on ATR
                # NSE Live: 2.5x ATR (safer for 3-4 day swing trades)
                # Stock Scalping: 1.0x ATR (tighter for intraday)
                # Others: 1.5x ATR (standard)
                if category == "NSE Live":
                    sl_multiplier = CONFIG['nse_specific']['sl_atr_multiplier']  # 2.5x for swing trades
                    tp_ratios = CONFIG['risk']['tp_ratios']
                elif category == "Stock Scalping":
                    sl_multiplier = 1.0  # Tighter SL for scalping
                    tp_ratios = [1.0, 2.0, 3.0]  # 1:1, 1:2, 1:3 for scalping
                elif category in ["Crypto Scalping", "Crypto"]:
                    sl_multiplier = 2.5  # Wider SL for crypto volatility
                    tp_ratios = CONFIG['risk']['tp_ratios']
                else:
                    sl_multiplier = CONFIG['risk']['sl_atr_multiplier']
                    tp_ratios = CONFIG['risk']['tp_ratios']
                
                sl_dist = atr * sl_multiplier
                if sl_dist == 0:  # Fallback
                    sl_dist = 30 * instrument['pip_size']
                
                # ========== NSE LIVE SPECIFIC FILTERS ==========
                can_generate_nse_signal = True
                
                if category == "NSE Live":
                    # 1. Volume Filter (1.2x average)
                    if CONFIG['nse_specific']['volume_multiplier'] > 0:
                        vol_confirmed, curr_vol, avg_vol, vol_ratio = check_volume_confirmation(
                            entry_df, 
                            CONFIG['nse_specific']['volume_lookback'],
                            CONFIG['nse_specific']['volume_multiplier']
                        )
                        if not vol_confirmed:
                            can_generate_nse_signal = False
                            print(f"  ⚠️ {name}: Volume too low ({vol_ratio:.2f}x avg) - BUY signal skipped")
                        else:
                            print(f"  ✅ {name}: Volume confirmed ({vol_ratio:.2f}x avg)")
                    
                    # 2. Opening Range Breakout (ORB) Filter
                    if can_generate_nse_signal and CONFIG['nse_specific']['orb_enabled']:
                        # Update ORB data if in ORB window
                        if is_orb_window(current_time_ist):
                            update_opening_range(name, current_price)
                        
                        # Check ORB breakout alignment
                        orb_status = get_orb_status(name)
                        if orb_status:
                            orb_breakout = check_orb_breakout(name, current_price, "BUY")
                            if orb_breakout == "AGAINST":
                                can_generate_nse_signal = False
                                print(f"  ⚠️ {name}: ORB breakout is BEARISH - BUY signal skipped")
                            elif orb_breakout == "WITH":
                                print(f"  ✅ {name}: ORB breakout aligned (BULLISH)")
                            else:
                                print(f"  ℹ️ {name}: ORB window active or no breakout yet")
                    
                    # 3. Pre-Market Sentiment Filter (First hour only: 9:15-10:15 AM)
                    if can_generate_nse_signal and CONFIG['nse_specific']['premarket_filter']:
                        first_hour_end = CONFIG['nse_specific']['first_hour_end'].split(':')
                        first_hour_end_time = int(first_hour_end[0]) * 60 + int(first_hour_end[1])
                        current_time_minutes = current_hour * 60 + current_minute
                        
                        # Only apply filter in first hour (9:15 - 10:15 AM)
                        if current_time_minutes <= first_hour_end_time:
                            if premarket_data and 'overall_sentiment' in premarket_data:
                                sentiment = premarket_data['overall_sentiment']
                                if sentiment == "BEARISH":
                                    can_generate_nse_signal = False
                                    print(f"  ⚠️ {name}: Pre-market sentiment is BEARISH - BUY signal skipped")
                                else:
                                    print(f"  ✅ {name}: Pre-market sentiment aligned ({sentiment})")
                            else:
                                print(f"  ℹ️ {name}: Pre-market data not available")
                
                # Generate signal only if all filters pass
                if can_generate_nse_signal:
                    sl = entry - sl_dist
                    
                    tp1 = entry + (sl_dist * tp_ratios[0])
                    tp2 = entry + (sl_dist * tp_ratios[1])
                    tp3 = entry + (sl_dist * tp_ratios[2])
                    
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
                        "category": category,
                        "lifecycle_status": "New Signal"
                    }
                    ACTIVE_SIGNALS[name] = final_signal
                    save_active_signals()
                    status = "ACTIVE_BUY"
                    print(f"  🆕 {name}: NEW BUY SIGNAL @ {entry:.5f}")
                    log_signal_event(name, "ENTRY", entry, final_signal)
                    # Send Telegram alert
                    if telegram_alerts:
                        try:
                            telegram_alerts.send_new_signal_alert(name, final_signal)
                        except Exception as e:
                            print(f"  ⚠️ Telegram alert failed: {e}")
                else:
                    status = "FILTERS_FAILED"
                
        elif trend_bias == "BEARISH" and mom_bias == "BEARISH" and is_below_ema and rsi_bearish and macd_bearish:
            status = "LOOKING_FOR_SELL"
            # Trigger on fresh cross OR if momentum just started building from a positive histogram
            if e_signal == "SELL_CROSS" or (e_signal == "BEARISH_MOM" and e_prev['Histogram'] >= 0):
                entry = current_price # Use real-time price for entry
                
                # Dynamic SL based on ATR
                # NSE Live: 2.5x ATR (safer for 3-4 day swing trades)
                # Stock Scalping: 1.0x ATR (tighter for intraday)
                # Others: 1.5x ATR (standard)
                if category == "NSE Live":
                    sl_multiplier = CONFIG['nse_specific']['sl_atr_multiplier']  # 2.5x for swing trades
                    tp_ratios = CONFIG['risk']['tp_ratios']
                elif category == "Stock Scalping":
                    sl_multiplier = 1.0  # Tighter SL for scalping
                    tp_ratios = [1.0, 2.0, 3.0]  # 1:1, 1:2, 1:3 for scalping
                elif category in ["Crypto Scalping", "Crypto"]:
                    sl_multiplier = 2.5  # Wider SL for crypto volatility
                    tp_ratios = CONFIG['risk']['tp_ratios']
                else:
                    sl_multiplier = CONFIG['risk']['sl_atr_multiplier']
                    tp_ratios = CONFIG['risk']['tp_ratios']
                
                sl_dist = atr * sl_multiplier
                if sl_dist == 0: # Fallback
                    sl_dist = 30 * instrument['pip_size']
                
                # ========== NSE LIVE SPECIFIC FILTERS ==========
                can_generate_nse_signal = True
                
                if category == "NSE Live":
                    # 1. Volume Filter (1.2x average)
                    if CONFIG['nse_specific']['volume_multiplier'] > 0:
                        vol_confirmed, curr_vol, avg_vol, vol_ratio = check_volume_confirmation(
                            entry_df, 
                            CONFIG['nse_specific']['volume_lookback'],
                            CONFIG['nse_specific']['volume_multiplier']
                        )
                        if not vol_confirmed:
                            can_generate_nse_signal = False
                            print(f"  ⚠️ {name}: Volume too low ({vol_ratio:.2f}x avg) - SELL signal skipped")
                        else:
                            print(f"  ✅ {name}: Volume confirmed ({vol_ratio:.2f}x avg)")
                    
                    # 2. Opening Range Breakout (ORB) Filter
                    if can_generate_nse_signal and CONFIG['nse_specific']['orb_enabled']:
                        # Update ORB data if in ORB window
                        if is_orb_window(current_time_ist):
                            update_opening_range(name, current_price)
                        
                        # Check ORB breakout alignment
                        orb_status = get_orb_status(name)
                        if orb_status:
                            orb_breakout = check_orb_breakout(name, current_price, "SELL")
                            if orb_breakout == "AGAINST":
                                can_generate_nse_signal = False
                                print(f"  ⚠️ {name}: ORB breakout is BULLISH - SELL signal skipped")
                            elif orb_breakout == "WITH":
                                print(f"  ✅ {name}: ORB breakout aligned (BEARISH)")
                            else:
                                print(f"  ℹ️ {name}: ORB window active or no breakout yet")
                    
                    # 3. Pre-Market Sentiment Filter (First hour only: 9:15-10:15 AM)
                    if can_generate_nse_signal and CONFIG['nse_specific']['premarket_filter']:
                        first_hour_end = CONFIG['nse_specific']['first_hour_end'].split(':')
                        first_hour_end_time = int(first_hour_end[0]) * 60 + int(first_hour_end[1])
                        current_time_minutes = current_hour * 60 + current_minute
                        
                        # Only apply filter in first hour (9:15 - 10:15 AM)
                        if current_time_minutes <= first_hour_end_time:
                            if premarket_data and 'overall_sentiment' in premarket_data:
                                sentiment = premarket_data['overall_sentiment']
                                if sentiment == "BULLISH":
                                    can_generate_nse_signal = False
                                    print(f"  ⚠️ {name}: Pre-market sentiment is BULLISH - SELL signal skipped")
                                else:
                                    print(f"  ✅ {name}: Pre-market sentiment aligned ({sentiment})")
                            else:
                                print(f"  ℹ️ {name}: Pre-market data not available")
                
                # Generate signal only if all filters pass
                if can_generate_nse_signal:
                    sl = entry + sl_dist
                    
                    tp1 = entry - (sl_dist * tp_ratios[0])
                    tp2 = entry - (sl_dist * tp_ratios[1])
                    tp3 = entry - (sl_dist * tp_ratios[2])
                    
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
                        "category": category,
                        "lifecycle_status": "New Signal"
                    }
                    ACTIVE_SIGNALS[name] = final_signal
                    save_active_signals()
                    status = "ACTIVE_SELL"
                    print(f"  🆕 {name}: NEW SELL SIGNAL @ {entry:.5f}")
                    log_signal_event(name, "ENTRY", entry, final_signal)
                    # Send Telegram alert
                    if telegram_alerts:
                        try:
                            telegram_alerts.send_new_signal_alert(name, final_signal)
                        except Exception as e:
                            print(f"  ⚠️ Telegram alert failed: {e}")
                else:
                    status = "FILTERS_FAILED"
        else:
            status = "CONFLICT (Trend/MOM/Filter Mismatch)"
    elif not can_generate_signal and not active_signal:
        # Indian market instrument outside market hours (only for new signals)
        status = "OUTSIDE_MARKET_HOURS"
            
    # Maintain status for active signals
    if active_signal:
        status = f"ACTIVE_{active_signal['type']}"
            
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
        "re_entry": re_entry_opportunity,  # Re-entry detection
        "category": instrument.get('category', 'Other'),
        "contract_info": contract_info,  # NSE futures contract details
        "timestamp": datetime.now().isoformat(),
        "sparkline": entry_df['Close'].tail(24).tolist()  # Last 24 1H candles for mini chart
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
            
            # Enrich results with sentiment analysis
            for res in results:
                # Add sentiment data if available
                try:
                    sentiment = sentiment_analyzer.get_sentiment_signal(res['instrument'])
                    if sentiment:
                        res['retail_sentiment'] = sentiment
                        
                        # Add alignment indicator if there's an active signal
                        if res.get('signal'):
                            signal_type = res['signal']['type']
                            contrarian_bias = sentiment['contrarian_bias']
                            
                            if contrarian_bias != 'NONE':
                                aligned = signal_type == contrarian_bias
                                res['sentiment_aligned'] = aligned
                                res['sentiment_confirmation'] = "✅ STRONG" if aligned else "⚠️ WEAK"
                except Exception:
                    pass  # Silently skip if sentiment not available
                
                print(f"  👉 {res['instrument']}: {res['overall_status']}")
                if res['signal']:
                    signal_str = f"     ✅ SIGNAL: {res['signal']['type']} @ {res['signal']['entry_price']:.5f}"
                    # Add sentiment confirmation if available
                    if res.get('sentiment_confirmation'):
                        signal_str += f" | Sentiment: {res['sentiment_confirmation']}"
                    print(signal_str)
            
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

#!/usr/bin/env python3
"""
Generate Mock Data for NSE Live Tab
Creates realistic signals for Nifty Future and Bank Nifty Future
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

# File paths
BASE_DIR = Path(__file__).parent
SIGNALS_FILE = BASE_DIR / "forex_macd_signals.json"

def generate_nse_mock_data():
    """Generate mock signals for NSE Live instruments"""
    
    # Load existing signals
    with open(SIGNALS_FILE, 'r') as f:
        data = json.load(f)
    
    # Current time
    now = datetime.now()
    
    # Mock data for Nifty Future - ACTIVE BUY SIGNAL
    nifty_mock = {
        "instrument": "Nifty Future",
        "flag": "🇮🇳📈",
        "ltp": 26285.50,  # Current price above entry
        "daily": {
            "macd_line": 125.45,
            "bias": "BULLISH",
            "label": "1D Trend"
        },
        "h4": {
            "histogram": 45.32,
            "bias": "BULLISH",
            "label": "4H MOM"
        },
        "h1": {
            "histogram": 15.67,
            "status": "BULLISH_MOM",
            "close": 26285.50,
            "label": "1H Entry",
            "ema_200": 25950.25,
            "rsi": 62.5
        },
        "overall_status": "ACTIVE_BUY",
        "signal": {
            "type": "BUY",
            "entry_price": 26150.00,
            "sl": 26050.00,
            "current_sl": 26150.00,  # Moved to breakeven after TP1
            "tp1": 26300.00,
            "tp2": 26450.00,
            "tp3": 26650.00,
            "tp_hits": [True, False, False],  # TP1 hit
            "time": (now - timedelta(hours=3)).isoformat(),
            "candle_time": (now - timedelta(hours=3)).isoformat(),
            "category": "NSE Live",
            "lifecycle_status": "Trailing SL Active"
        },
        "re_entry": None,
        "category": "NSE Live",
        "contract_info": {
            "contract": "JAN 26",
            "expiry": "29-Jan-2026",
            "days_to_expiry": 34
        },
        "timestamp": now.isoformat()
    }
    
    # Mock data for Bank Nifty Future - ACTIVE SELL SIGNAL with REENTRY
    banknifty_mock = {
        "instrument": "Bank Nifty Future",
        "flag": "🇮🇳🏦",
        "ltp": 58950.25,  # Price pulled back to reentry zone
        "daily": {
            "macd_line": -85.32,
            "bias": "BEARISH",
            "label": "1D Trend"
        },
        "h4": {
            "histogram": -35.67,
            "bias": "BEARISH",
            "label": "4H MOM"
        },
        "h1": {
            "histogram": -12.45,
            "status": "BEARISH_MOM",
            "close": 58950.25,
            "label": "1H Entry",
            "ema_200": 59250.75,
            "rsi": 42.3
        },
        "overall_status": "ACTIVE_SELL",
        "signal": {
            "type": "SELL",
            "entry_price": 59200.00,
            "sl": 59450.00,
            "current_sl": 59200.00,  # Moved to breakeven
            "tp1": 58825.00,
            "tp2": 58450.00,
            "tp3": 57950.00,
            "tp_hits": [True, False, False],  # TP1 hit
            "time": (now - timedelta(hours=5)).isoformat(),
            "candle_time": (now - timedelta(hours=5)).isoformat(),
            "category": "NSE Live",
            "lifecycle_status": "Reentry Opportunity"
        },
        "re_entry": {
            "type": "ADD_TO_SELL",
            "strength": 85,
            "reason": "Price at 61.8% Fib (175 points pullback)",
            "suggested_entry": 58975.00,
            "rejection_zone": "58900 - 59050",
            "fib_level": "61.8%",
            "fib_price": 58975.00,
            "confirmation": "Histogram: -12.45 | RSI: 42.3 | Strong Bearish",
            "risk_reward": "1:3.2"
        },
        "category": "NSE Live",
        "contract_info": {
            "contract": "JAN 26",
            "expiry": "29-Jan-2026",
            "days_to_expiry": 34
        },
        "timestamp": now.isoformat()
    }
    
    # Find and replace NSE Live instruments in the data
    updated = False
    for i, item in enumerate(data['data']):
        if item['instrument'] == 'Nifty Future':
            data['data'][i] = nifty_mock
            print(f"✅ Updated Nifty Future with ACTIVE BUY signal")
            updated = True
        elif item['instrument'] == 'Bank Nifty Future':
            data['data'][i] = banknifty_mock
            print(f"✅ Updated Bank Nifty Future with ACTIVE SELL signal + REENTRY")
            updated = True
    
    # If not found, append them
    if not updated:
        data['data'].append(nifty_mock)
        data['data'].append(banknifty_mock)
        print(f"✅ Added Nifty Future and Bank Nifty Future mock data")
    
    # Update timestamp
    data['last_updated'] = now.isoformat()
    data['backend_heartbeat'] = now.strftime("%Y-%m-%d %H:%M:%S")
    
    # Save back to file
    with open(SIGNALS_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n💾 Mock data saved to {SIGNALS_FILE}")
    print(f"\n📊 NSE Live Mock Data Summary:")
    print(f"   🔹 Nifty Future:")
    print(f"      - Status: ACTIVE BUY @ 26,150.00")
    print(f"      - Current Price: 26,285.50 (+135.50 points)")
    print(f"      - TP1 Hit ✅ | SL at Breakeven")
    print(f"      - Next Target: TP2 @ 26,450.00")
    print(f"\n   🔹 Bank Nifty Future:")
    print(f"      - Status: ACTIVE SELL @ 59,200.00")
    print(f"      - Current Price: 58,950.25 (+249.75 points profit)")
    print(f"      - TP1 Hit ✅ | SL at Breakeven")
    print(f"      - REENTRY OPPORTUNITY at 58,975.00 (61.8% Fib)")
    print(f"      - Next Target: TP2 @ 58,450.00")

if __name__ == "__main__":
    print("=" * 60)
    print("🇮🇳 NSE LIVE MOCK DATA GENERATOR")
    print("=" * 60)
    generate_nse_mock_data()
    print("\n✅ Done! Refresh your dashboard to see the mock signals.")
    print("=" * 60)

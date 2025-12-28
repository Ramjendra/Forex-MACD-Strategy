#!/usr/bin/env python3
"""
Test Alert System - Injects a mock signal to trigger browser alert
"""
import json
import os
from datetime import datetime

# Path to signals file
SIGNALS_FILE = "/home/ramram/Desktop/SELF_LEARNING/Medical RAG/documents/Signal/Forex_MACD_Strategy/forex_macd_signals.json"

def inject_mock_signal():
    """Inject a new mock signal to test the alert system"""
    
    # Read current signals
    with open(SIGNALS_FILE, 'r') as f:
        data = json.load(f)
    
    # Create a new mock signal
    mock_signal = {
        "instrument": "TEST/ALERT",
        "flag": "🔔",
        "ltp": 1.2345,
        "daily": {"macd_line": 0.01, "bias": "BULLISH", "label": "1D Trend"},
        "h4": {"histogram": 0.005, "bias": "BULLISH", "label": "4H MOM"},
        "h1": {"histogram": 0.002, "status": "BULLISH_MOM", "close": 1.2345, "label": "1H Entry", "ema_200": 1.23, "rsi": 55},
        "overall_status": "ACTIVE_BUY",
        "signal": {
            "type": "BUY",
            "entry_price": 1.2345,
            "sl": 1.2300,
            "current_sl": 1.2300,
            "tp1": 1.2400,
            "tp2": 1.2450,
            "tp3": 1.2500,
            "tp_hits": [False, False, False],
            "time": datetime.now().isoformat(),
            "candle_time": datetime.now().isoformat(),
            "category": "Forex"
        },
        "re_entry": None,
        "category": "Forex",
        "contract_info": None,
        "timestamp": datetime.now().isoformat()
    }
    
    # Insert at the beginning
    data['data'].insert(0, mock_signal)
    data['last_updated'] = datetime.now().isoformat()
    data['backend_heartbeat'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Save back
    with open(SIGNALS_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    print("✅ Mock signal injected: TEST/ALERT BUY")
    print("   Entry: 1.2345, SL: 1.2300, TP1: 1.2400")
    print("\n📢 Refresh the dashboard to see the alert!")
    print("   URL: http://localhost:8003/forex_macd_dashboard.html")
    print("\n⚠️ Make sure you have clicked 'Alerts On' button first!")


def remove_mock_signal():
    """Remove the mock signal"""
    # Read current signals
    with open(SIGNALS_FILE, 'r') as f:
        data = json.load(f)
    
    # Filter out test signals
    data['data'] = [d for d in data['data'] if d['instrument'] != 'TEST/ALERT']
    data['last_updated'] = datetime.now().isoformat()
    
    # Save back
    with open(SIGNALS_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    print("✅ Mock signal removed")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'remove':
        remove_mock_signal()
    else:
        inject_mock_signal()

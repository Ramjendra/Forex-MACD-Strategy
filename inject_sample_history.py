import json
from datetime import datetime, timedelta
from pathlib import Path

HISTORY_FILE = Path("/home/ramram/Desktop/SELF_LEARNING/Medical RAG/documents/Signal/Forex_MACD_Strategy/signal_history.json")

def inject_sample_history():
    now = datetime.now()
    
    # Sample Trades
    history = [
        # Trade 1: Gold (TP3 Hit)
        {
            "instrument": "Gold",
            "event": "ENTRY",
            "price": 2050.50,
            "time": (now - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S"),
            "category": "Metals/Energy",
            "entry_price": 2050.50,
            "entry_time": (now - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S"),
            "type": "BUY",
            "initial_sl": 2045.00
        },
        {
            "instrument": "Gold",
            "event": "TP1_HIT",
            "price": 2058.75,
            "time": (now - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S"),
            "category": "Metals/Energy",
            "entry_price": 2050.50,
            "entry_time": (now - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S"),
            "type": "BUY",
            "initial_sl": 2045.00
        },
        {
            "instrument": "Gold",
            "event": "TP2_HIT",
            "price": 2067.00,
            "time": (now - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S"),
            "category": "Metals/Energy",
            "entry_price": 2050.50,
            "entry_time": (now - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S"),
            "type": "BUY",
            "initial_sl": 2045.00
        },
        {
            "instrument": "Gold",
            "event": "TP3_HIT",
            "price": 2078.00,
            "time": (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "category": "Metals/Energy",
            "entry_price": 2050.50,
            "entry_time": (now - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S"),
            "type": "BUY",
            "initial_sl": 2045.00
        },
        
        # Trade 2: EUR/USD (SL Hit)
        {
            "instrument": "EUR/USD",
            "event": "ENTRY",
            "price": 1.08500,
            "time": (now - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S"),
            "category": "Forex",
            "entry_price": 1.08500,
            "entry_time": (now - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S"),
            "type": "SELL",
            "initial_sl": 1.08800
        },
        {
            "instrument": "EUR/USD",
            "event": "SL_HIT",
            "price": 1.08805,
            "time": (now - timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
            "category": "Forex",
            "entry_price": 1.08500,
            "entry_time": (now - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S"),
            "type": "SELL",
            "initial_sl": 1.08800
        },
        
        # Trade 3: Bitcoin (Trail SL Hit after TP1)
        {
            "instrument": "Bitcoin",
            "event": "ENTRY",
            "price": 64000.0,
            "time": (now - timedelta(hours=10)).strftime("%Y-%m-%d %H:%M:%S"),
            "category": "Crypto Scalping",
            "entry_price": 64000.0,
            "entry_time": (now - timedelta(hours=10)).strftime("%Y-%m-%d %H:%M:%S"),
            "type": "BUY",
            "initial_sl": 63000.0
        },
        {
            "instrument": "Bitcoin",
            "event": "TP1_HIT",
            "price": 65500.0,
            "time": (now - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"),
            "category": "Crypto Scalping",
            "entry_price": 64000.0,
            "entry_time": (now - timedelta(hours=10)).strftime("%Y-%m-%d %H:%M:%S"),
            "type": "BUY",
            "initial_sl": 63000.0
        },
        {
            "instrument": "Bitcoin",
            "event": "TRAIL_SL_HIT",
            "price": 64000.0,
            "time": (now - timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S"),
            "category": "Crypto Scalping",
            "entry_price": 64000.0,
            "entry_time": (now - timedelta(hours=10)).strftime("%Y-%m-%d %H:%M:%S"),
            "type": "BUY",
            "initial_sl": 63000.0
        },
        
        # Trade 4: USD/JPY (Active/Recent Entry)
        {
            "instrument": "USD/JPY",
            "event": "ENTRY",
            "price": 148.50,
            "time": (now - timedelta(minutes=45)).strftime("%Y-%m-%d %H:%M:%S"),
            "category": "Forex",
            "entry_price": 148.50,
            "entry_time": (now - timedelta(minutes=45)).strftime("%Y-%m-%d %H:%M:%S"),
            "type": "BUY",
            "initial_sl": 147.80
        }
    ]
    
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)
    
    print(f"✅ Successfully injected {len(history)} sample history events into {HISTORY_FILE}")

if __name__ == "__main__":
    inject_sample_history()

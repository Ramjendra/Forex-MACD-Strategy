import json
from datetime import datetime
from pathlib import Path

HISTORY_FILE = Path("/home/ramram/Desktop/SELF_LEARNING/Medical RAG/documents/Signal/Forex_MACD_Strategy/signal_history.json")

def inject_mock_history():
    event = {
        "instrument": "Mock BTC Signal",
        "event": "ENTRY",
        "price": 65000.0,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "category": "Cryptos",
        "entry_price": 65000.0,
        "type": "BUY"
    }
    
    history = [event]
    
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)
    
    print(f"Successfully injected mock history into {HISTORY_FILE}")

if __name__ == "__main__":
    inject_mock_history()

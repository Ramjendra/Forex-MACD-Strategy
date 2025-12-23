import json
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path("/home/ramram/Desktop/SELF_LEARNING/Medical RAG/documents/Signal/Forex_MACD_Strategy")
SIGNALS_FILE = BASE_DIR / "forex_macd_signals.json"
HISTORY_FILE = BASE_DIR / "signal_history.json"

def create_mock_instrument(name, symbol, category, flag, status, signal_type=None):
    now = datetime.now()
    ltp = 1.0850 if "EUR" in symbol else (2350.0 if "GC" in symbol else (65000.0 if "BTC" in symbol else 24500.0))
    # Vary LTP slightly from entry price if it's an active signal
    entry_price = ltp
    if signal_type:
        if signal_type == "BUY":
            ltp = entry_price * 1.002 # LTP is higher for Buy
        else:
            ltp = entry_price * 0.998 # LTP is lower for Sell

    inst = {
        "instrument": name,
        "symbol": symbol,
        "flag": flag,
        "ltp": ltp,
        "category": category,
        "daily": {"macd_line": 0.001, "bias": "BULLISH", "label": "Daily"},
        "h4": {"histogram": 0.0005, "bias": "BULLISH", "label": "4H MOM"},
        "h1": {
            "histogram": 0.0002, 
            "status": "BUY_CROSS" if signal_type == "BUY" else "SELL_CROSS" if signal_type == "SELL" else "NEUTRAL",
            "close": ltp,
            "label": "15m Entry" if category == "Intraday IndianMarket" else "1H Entry",
            "ema_200": ltp * 0.99,
            "rsi": 65.0
        },
        "overall_status": status,
        "timestamp": now.isoformat()
    }
    
    if signal_type:
        inst["signal"] = {
            "type": signal_type,
            "entry_price": entry_price,
            "sl": entry_price * (0.99 if signal_type == "BUY" else 1.01),
            "current_sl": entry_price * (0.99 if signal_type == "BUY" else 1.01),
            "tp1": entry_price * (1.01 if signal_type == "BUY" else 0.99),
            "tp2": entry_price * (1.02 if signal_type == "BUY" else 0.98),
            "tp3": entry_price * (1.03 if signal_type == "BUY" else 0.97),
            "tp3": ltp * (1.03 if signal_type == "BUY" else 0.97),
            "tp_hits": [True, False, False] if name == "EUR/USD" else [False, False, False],
            "sl_hit": True if name == "GBP/USD" else False,
            "time": now.isoformat(),
            "category": category
        }
    else:
        inst["signal"] = None
        
    return inst

def inject_all_mock_data():
    # 1. Signals Data
    data = {
        "last_updated": datetime.now().isoformat(),
        "data": [
            # Active Forex
            create_mock_instrument("EUR/USD", "EURUSD=X", "Forex", "🇪🇺🇺🇸", "ACTIVE_BUY", "BUY"),
            create_mock_instrument("GBP/USD", "GBPUSD=X", "Forex", "🇬🇧🇺🇸", "ACTIVE_SELL", "SELL"),
            # Pending Forex
            create_mock_instrument("USD/JPY", "USDJPY=X", "Forex", "🇺🇸🇯🇵", "LOOKING_FOR_BUY"),
            create_mock_instrument("AUD/USD", "AUDUSD=X", "Forex", "🇦🇺🇺🇸", "WAITING"),
            
            # Active Metals/Energy
            create_mock_instrument("Gold", "GC=F", "Metals/Energy", "🥇", "ACTIVE_SELL", "SELL"),
            create_mock_instrument("US Oil (WTI)", "CL=F", "Metals/Energy", "🛢️", "ACTIVE_BUY", "BUY"),
            # Pending Metals/Energy
            create_mock_instrument("Silver", "SI=F", "Metals/Energy", "🥈", "CONFLICT (Trend/MOM/Filter Mismatch)"),
            
            # Active Cryptos
            create_mock_instrument("Bitcoin", "BTC-USD", "Cryptos", "₿", "ACTIVE_BUY", "BUY"),
            # Pending Cryptos
            create_mock_instrument("Ethereum", "ETH-USD", "Cryptos", "Ξ", "LOOKING_FOR_SELL"),
            
            # Active Indian Market
            create_mock_instrument("Nifty 50", "^NSEI", "Intraday IndianMarket", "🇮🇳", "ACTIVE_BUY", "BUY"),
            create_mock_instrument("Bank Nifty", "^NSEBANK", "Intraday IndianMarket", "🇮🇳🏦", "ACTIVE_SELL", "SELL"),
            # Pending Indian Market
            create_mock_instrument("Sensex", "^BSESN", "Intraday IndianMarket", "🇮🇳📈", "WAITING")
        ]
    }
    
    with open(SIGNALS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

    # 2. History Data (Cleared as requested)
    history = []
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)
        
    print("Successfully injected mock data into all tabs and cleared history.")

if __name__ == "__main__":
    inject_all_mock_data()

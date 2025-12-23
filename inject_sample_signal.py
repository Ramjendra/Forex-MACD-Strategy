import json
import os
from datetime import datetime

json_path = "forex_macd_signals.json"

if os.path.exists(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Inject a sample signal into the first instrument
    if data['data']:
        data['data'][0]['signal'] = {
            "type": "BUY",
            "entry_price": 58.0,
            "sl": 57.0,
            "current_sl": 57.5,
            "tp1": 59.5,
            "tp2": 61.0,
            "tp3": 63.0,
            "tp_hits": [True, False, False],
            "time": datetime.now().isoformat(),
            "candle_time": datetime.now().isoformat(),
            "category": data['data'][0]['category']
        }
        data['data'][0]['overall_status'] = "ACTIVE_BUY"
        
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)
        print("✅ Injected sample signal into forex_macd_signals.json")
else:
    print("❌ forex_macd_signals.json not found")

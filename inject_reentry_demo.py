#!/usr/bin/env python3
"""
Inject Mock Reentry Opportunities for Dashboard Demo
"""

import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
SIGNALS_FILE = BASE_DIR / "forex_macd_signals.json"

def inject_reentry_demo():
    """Add mock reentry opportunities to demonstrate dashboard display"""
    
    # Load current signals
    with open(SIGNALS_FILE, 'r') as f:
        data = json.load(f)
    
    print("🔄 Injecting Mock Reentry Opportunities...\n")
    
    # Find instruments with active signals
    instruments_with_signals = [inst for inst in data['data'] if inst.get('signal')]
    
    if len(instruments_with_signals) == 0:
        print("⚠️  No instruments with active signals found!")
        print("Creating mock signals for first 3 Forex instruments...\n")
        
        # Find first 3 Forex instruments
        forex_instruments = [inst for inst in data['data'] if inst.get('category') == 'Forex'][:3]
        
        for idx, inst in enumerate(forex_instruments):
            signal_type = "BUY" if idx % 2 == 0 else "SELL"
            ltp = inst.get('ltp', 100.0)
            
            # Create mock signal
            inst['signal'] = {
                "type": signal_type,
                "entry_price": ltp,
                "sl": ltp * 0.99 if signal_type == "BUY" else ltp * 1.01,
                "tp1": ltp * 1.015 if signal_type == "BUY" else ltp * 0.985,
                "tp2": ltp * 1.03 if signal_type == "BUY" else ltp * 0.97,
                "tp3": ltp * 1.05 if signal_type == "BUY" else ltp * 0.95,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            instruments_with_signals.append(inst)
            print(f"📝 Created mock {signal_type} signal for {inst['instrument']}")
    
    print(f"\n✅ Found {len(instruments_with_signals)} instruments with signals\n")
    
    # Add reentry opportunities to first 3 instruments with signals
    reentry_count = 0
    
    for idx, inst in enumerate(instruments_with_signals[:3]):
        instrument_name = inst['instrument']
        signal_type = inst['signal']['type']
        ltp = inst.get('ltp', 100.0)
        
        # Add reentry opportunity based on index
        if idx == 0:
            # High strength reentry
            inst['re_entry'] = {
                "type": f"ADD_TO_{signal_type}",
                "strength": 88,
                "reason": "Price at 61.8% Fib (15.2 pips pullback)",
                "suggested_entry": round(ltp * 0.998, 5),
                "rejection_zone": f"{round(ltp * 0.9975, 5)} - {round(ltp * 0.9985, 5)}",
                "fib_level": "61.8%",
                "fib_price": round(ltp * 0.998, 5),
                "confirmation": "Histogram: 0.052 | RSI: 62.3 | Wick: 0.00035",
                "risk_reward": "1:3.2"
            }
            print(f"✅ {instrument_name}: HIGH STRENGTH (88%) - {signal_type} Reentry")
            print(f"   📍 Fibonacci: 61.8% @ {inst['re_entry']['suggested_entry']}")
            print(f"   💰 R:R Ratio: 1:3.2\n")
            
        elif idx == 1:
            # Medium strength reentry
            inst['re_entry'] = {
                "type": f"ADD_TO_{signal_type}",
                "strength": 65,
                "reason": "Price at 50.0% Fib (10.5 pips pullback)",
                "suggested_entry": round(ltp * 0.999, 5),
                "rejection_zone": f"{round(ltp * 0.9985, 5)} - {round(ltp * 0.9995, 5)}",
                "fib_level": "50.0%",
                "fib_price": round(ltp * 0.999, 5),
                "confirmation": "Histogram: 0.038 | RSI: 55.8 | Wick: 0.00022",
                "risk_reward": "1:2.5"
            }
            print(f"✅ {instrument_name}: MEDIUM STRENGTH (65%) - {signal_type} Reentry")
            print(f"   📍 Fibonacci: 50.0% @ {inst['re_entry']['suggested_entry']}")
            print(f"   💰 R:R Ratio: 1:2.5\n")
            
        elif idx == 2:
            # Lower strength reentry
            inst['re_entry'] = {
                "type": f"ADD_TO_{signal_type}",
                "strength": 52,
                "reason": "Price at 38.2% Fib (7.3 pips pullback)",
                "suggested_entry": round(ltp * 1.001, 5),
                "rejection_zone": f"{round(ltp * 1.0005, 5)} - {round(ltp * 1.0015, 5)}",
                "fib_level": "38.2%",
                "fib_price": round(ltp * 1.001, 5),
                "confirmation": "Histogram: 0.025 | RSI: 48.2 | Wick: 0.00015",
                "risk_reward": "1:1.8"
            }
            print(f"✅ {instrument_name}: MODERATE STRENGTH (52%) - {signal_type} Reentry")
            print(f"   📍 Fibonacci: 38.2% @ {inst['re_entry']['suggested_entry']}")
            print(f"   💰 R:R Ratio: 1:1.8\n")
        
        reentry_count += 1
    
    # Save updated data
    with open(SIGNALS_FILE, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"💾 Saved {reentry_count} mock reentry opportunities to {SIGNALS_FILE.name}")
    print(f"\n📊 View on dashboard: http://localhost:8003")
    print(f"   The reentry cards will appear in the 'Forex Live Signal' tab")
    print(f"\n🎨 Dashboard Features:")
    print(f"   • Color-coded strength badges (Green=High, Yellow=Medium, Gray=Low)")
    print(f"   • Fibonacci retracement levels")
    print(f"   • Risk:Reward ratios")
    print(f"   • Confirmation indicators (Histogram, RSI, Wick)")
    print(f"   • Suggested entry prices and rejection zones")
    
    # Verify the data was saved
    print(f"\n🔍 Verification:")
    with open(SIGNALS_FILE, 'r') as f:
        verify_data = json.load(f)
    reentry_instruments = [inst['instrument'] for inst in verify_data['data'] if inst.get('re_entry')]
    print(f"   Instruments with reentry: {', '.join(reentry_instruments)}")

if __name__ == "__main__":
    inject_reentry_demo()

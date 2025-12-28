#!/usr/bin/env python3
"""
Inject Mock Reentry Opportunity for Testing Dashboard Display
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
SIGNALS_FILE = BASE_DIR / "forex_macd_signals.json"

def inject_mock_reentry():
    """Add a mock reentry opportunity to an existing signal for testing"""
    
    # Load current signals
    with open(SIGNALS_FILE, 'r') as f:
        data = json.load(f)
    
    # Find USD/CHF (has active SELL signal)
    for inst in data['data']:
        if inst['instrument'] == 'USD/CHF' and inst.get('signal'):
            print(f"✅ Found {inst['instrument']} with active {inst['signal']['type']} signal")
            
            # Inject mock reentry opportunity
            inst['re_entry'] = {
                "type": "ADD_TO_SELL",
                "strength": 85,
                "reason": "Price at 50.0% Fib (12.3 pips pullback)",
                "suggested_entry": 0.78850,
                "rejection_zone": "0.78830 - 0.78870",
                "fib_level": "50.0%",
                "fib_price": 0.78850,
                "confirmation": "Histogram: -0.045 | RSI: 38.5 | Wick: 0.00025",
                "risk_reward": "1:2.8"
            }
            
            print(f"🔄 Injected HIGH STRENGTH (85%) reentry opportunity")
            print(f"   Fibonacci: 50.0% @ 0.78850")
            print(f"   R:R Ratio: 1:2.8")
            break
    
    # Find Silver (has active BUY signal)
    for inst in data['data']:
        if inst['instrument'] == 'Silver' and inst.get('signal'):
            print(f"\n✅ Found {inst['instrument']} with active {inst['signal']['type']} signal")
            
            # Inject mock reentry opportunity
            inst['re_entry'] = {
                "type": "ADD_TO_BUY",
                "strength": 62,
                "reason": "Price at 38.2% Fib (8.7 pips pullback)",
                "suggested_entry": 71.450,
                "rejection_zone": "71.440 - 71.460",
                "fib_level": "38.2%",
                "fib_price": 71.452,
                "confirmation": "Histogram: 0.032 | RSI: 55.2 | Wick: 0.015",
                "risk_reward": "1:2.1"
            }
            
            print(f"🔄 Injected MEDIUM STRENGTH (62%) reentry opportunity")
            print(f"   Fibonacci: 38.2% @ 71.452")
            print(f"   R:R Ratio: 1:2.1")
            break
    
    # Save updated data
    with open(SIGNALS_FILE, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"\n💾 Saved mock reentry opportunities to {SIGNALS_FILE.name}")
    print(f"\n📊 Open dashboard to view: http://localhost:5000")
    print(f"   Navigate to 'Forex Live Signal' tab")
    print(f"\n🔍 Monitor with: ./monitor_reentry.sh")

if __name__ == "__main__":
    inject_mock_reentry()

#!/usr/bin/env python3
"""
Inject Mock Signals with All Lifecycle States for Dashboard Review
"""

import json
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).parent
SIGNALS_FILE = BASE_DIR / "forex_macd_signals.json"

def inject_lifecycle_demo():
    """Add mock signals demonstrating all 5 lifecycle states"""
    
    # Load current signals
    with open(SIGNALS_FILE, 'r') as f:
        data = json.load(f)
    
    print("🔄 Injecting Mock Signals with All Lifecycle States...\n")
    
    # Find first 5 Forex instruments
    forex_instruments = [inst for inst in data['data'] if inst.get('category') == 'Forex'][:5]
    
    lifecycle_demos = [
        {
            "name": "New Signal",
            "lifecycle_status": "New Signal",
            "signal_type": "BUY",
            "time_offset_hours": 0.5,  # 30 minutes ago
            "tp_hits": [False, False, False],
            "has_reentry": False,
            "trailing": False
        },
        {
            "name": "Reentry Opportunity",
            "lifecycle_status": "Reentry Opportunity",
            "signal_type": "SELL",
            "time_offset_hours": 5,
            "tp_hits": [False, False, False],
            "has_reentry": True,
            "trailing": False
        },
        {
            "name": "Partial TP Hit",
            "lifecycle_status": "Partial TP Hit",
            "signal_type": "BUY",
            "time_offset_hours": 12,
            "tp_hits": [True, False, False],
            "has_reentry": False,
            "trailing": False
        },
        {
            "name": "Trailing SL Active",
            "lifecycle_status": "Trailing SL Active",
            "signal_type": "SELL",
            "time_offset_hours": 24,
            "tp_hits": [True, True, False],
            "has_reentry": False,
            "trailing": True
        },
        {
            "name": "Active",
            "lifecycle_status": "Active",
            "signal_type": "BUY",
            "time_offset_hours": 48,
            "tp_hits": [False, False, False],
            "has_reentry": False,
            "trailing": False
        }
    ]
    
    for idx, (inst, demo) in enumerate(zip(forex_instruments, lifecycle_demos)):
        instrument_name = inst['instrument']
        ltp = inst.get('ltp', 100.0)
        signal_type = demo['signal_type']
        
        # Calculate signal time
        signal_time = datetime.now() - timedelta(hours=demo['time_offset_hours'])
        
        # Create mock signal
        if signal_type == "BUY":
            entry = ltp * 0.998
            sl = ltp * 0.995
            current_sl = ltp * 0.998 if demo['trailing'] else sl  # Breakeven if trailing
            tp1 = ltp * 1.015
            tp2 = ltp * 1.03
            tp3 = ltp * 1.05
        else:
            entry = ltp * 1.002
            sl = ltp * 1.005
            current_sl = ltp * 1.002 if demo['trailing'] else sl  # Breakeven if trailing
            tp1 = ltp * 0.985
            tp2 = ltp * 0.97
            tp3 = ltp * 0.95
        
        inst['signal'] = {
            "type": signal_type,
            "entry_price": entry,
            "sl": sl,
            "current_sl": current_sl,
            "tp1": tp1,
            "tp2": tp2,
            "tp3": tp3,
            "tp_hits": demo['tp_hits'],
            "time": signal_time.isoformat(),
            "candle_time": signal_time.isoformat(),
            "category": "Forex",
            "lifecycle_status": demo['lifecycle_status']
        }
        
        # Add reentry if needed
        if demo['has_reentry']:
            inst['re_entry'] = {
                "type": f"ADD_TO_{signal_type}",
                "strength": 75,
                "reason": "Price at 50.0% Fib (12.5 pips pullback)",
                "suggested_entry": round(ltp * 0.999, 5),
                "rejection_zone": f"{round(ltp * 0.9985, 5)} - {round(ltp * 0.9995, 5)}",
                "fib_level": "50.0%",
                "fib_price": round(ltp * 0.999, 5),
                "confirmation": "Histogram: -0.042 | RSI: 45.2 | Wick: 0.00028",
                "risk_reward": "1:2.8"
            }
        else:
            inst['re_entry'] = None
        
        print(f"✅ {instrument_name}: {demo['lifecycle_status']}")
        print(f"   Type: {signal_type} | Entry: {entry:.5f}")
        print(f"   TP Hits: {demo['tp_hits']} | Trailing: {demo['trailing']}")
        print(f"   Age: {demo['time_offset_hours']} hours ago\n")
    
    # Save updated data
    with open(SIGNALS_FILE, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"💾 Saved {len(lifecycle_demos)} mock signals to {SIGNALS_FILE.name}")
    print(f"\n📊 View on dashboard: http://localhost:8003")
    print(f"   Navigate to 'Forex Live Signal' tab to see all lifecycle states")
    print(f"\n🎨 Lifecycle States Demonstrated:")
    print(f"   🟢 New Signal - Detected 30 minutes ago")
    print(f"   🔁 Reentry Opportunity - Has active reentry setup")
    print(f"   🟡 Partial TP Hit - TP1 hit")
    print(f"   🔵 Trailing SL Active - TP1 & TP2 hit, SL at breakeven")
    print(f"   ⚪ Active - Standard active signal")
    
    print(f"\n⚠️  Note: Strategy is currently paused. Resume with: kill -CONT 156697")

if __name__ == "__main__":
    inject_lifecycle_demo()

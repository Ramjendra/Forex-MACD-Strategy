#!/usr/bin/env python3
"""
Generate Mock Signal History with P/L Metrics for Testing Professional UI
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
import random

BASE_DIR = Path(__file__).parent
HISTORY_FILE = BASE_DIR / "signal_history.json"

def generate_mock_history():
    """Generate comprehensive mock history with all P/L metrics"""
    
    instruments = [
        ("EUR/USD", 0.0001),
        ("USD/JPY", 0.01),
        ("GBP/USD", 0.0001),
        ("AUD/USD", 0.0001),
        ("USD/CAD", 0.0001),
        ("NZD/USD", 0.0001),
        ("EUR/GBP", 0.0001),
        ("Gold", 0.1),
        ("Silver", 0.005),
        ("US Oil (WTI)", 0.01)
    ]
    
    events = ["TP1_HIT", "TP2_HIT", "TP3_HIT", "SL_HIT", "TRAIL_SL_HIT"]
    types = ["BUY", "SELL"]
    
    history = []
    
    # Generate 30 mock trades
    for i in range(30):
        inst_name, pip_size = random.choice(instruments)
        signal_type = random.choice(types)
        event = random.choice(events)
        
        # Generate times
        entry_time = datetime.now() - timedelta(days=random.randint(1, 30), hours=random.randint(0, 23))
        exit_time = entry_time + timedelta(hours=random.randint(1, 48))
        
        # Generate prices
        base_price = random.uniform(1.0, 150.0)
        entry_price = base_price
        
        # Calculate exit price based on event
        if event.startswith("TP"):
            # Profitable trade
            if signal_type == "BUY":
                exit_price = entry_price + (random.uniform(20, 100) * pip_size)
            else:
                exit_price = entry_price - (random.uniform(20, 100) * pip_size)
        else:
            # Loss
            if signal_type == "BUY":
                exit_price = entry_price - (random.uniform(10, 50) * pip_size)
            else:
                exit_price = entry_price + (random.uniform(10, 50) * pip_size)
        
        # Calculate P/L
        if signal_type == "BUY":
            pnl_points = (exit_price - entry_price) / pip_size
        else:
            pnl_points = (entry_price - exit_price) / pip_size
        
        pnl_percent = ((exit_price - entry_price) / entry_price * 100) if signal_type == "BUY" else ((entry_price - exit_price) / entry_price * 100)
        
        # Calculate duration
        duration_seconds = (exit_time - entry_time).total_seconds()
        duration_hours = int(duration_seconds // 3600)
        duration_mins = int((duration_seconds % 3600) // 60)
        duration = f"{duration_hours}h {duration_mins}m"
        
        # Calculate R:R
        sl_distance = random.uniform(10, 30) * pip_size
        rr_planned = 1.5
        rr_achieved = abs(pnl_points * pip_size / sl_distance) if sl_distance > 0 else 0
        
        trade = {
            "instrument": inst_name,
            "event": event,
            "price": exit_price,
            "time": exit_time.strftime("%Y-%m-%d %H:%M:%S"),
            "category": "Forex" if "/" in inst_name else "Metals/Energy",
            "entry_price": entry_price,
            "entry_time": entry_time.isoformat(),
            "type": signal_type,
            "initial_sl": entry_price - sl_distance if signal_type == "BUY" else entry_price + sl_distance,
            "pnl_points": round(pnl_points, 1),
            "pnl_percent": round(pnl_percent, 2),
            "duration": duration,
            "rr_planned": rr_planned,
            "rr_achieved": round(rr_achieved, 2)
        }
        
        history.append(trade)
    
    # Sort by time (most recent first)
    history.sort(key=lambda x: x['time'], reverse=True)
    
    # Save to file
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)
    
    print(f"✅ Generated {len(history)} mock trades with P/L metrics")
    print(f"💾 Saved to {HISTORY_FILE}")
    
    # Print summary
    wins = len([t for t in history if t['event'].startswith('TP')])
    losses = len([t for t in history if 'SL' in t['event']])
    win_rate = (wins / len(history) * 100) if history else 0
    net_pnl = sum(t['pnl_points'] for t in history)
    
    print(f"\n📊 Summary:")
    print(f"   Total Trades: {len(history)}")
    print(f"   Wins: {wins} | Losses: {losses}")
    print(f"   Win Rate: {win_rate:.1f}%")
    print(f"   Net P/L: {net_pnl:+.1f} pips")

if __name__ == "__main__":
    generate_mock_history()

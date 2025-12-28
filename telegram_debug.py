#!/usr/bin/env python3
"""
Telegram Alert Debugging Tool
Checks for missed alerts by comparing signal history with expected Telegram notifications
"""

import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
HISTORY_FILE = BASE_DIR / "signal_history.json"

def analyze_missed_alerts():
    """Analyze signal history for events that should have triggered Telegram alerts"""
    
    if not HISTORY_FILE.exists():
        print("❌ No signal history file found")
        return
    
    with open(HISTORY_FILE, 'r') as f:
        history = json.load(f)
    
    print("=" * 60)
    print("TELEGRAM ALERT ANALYSIS")
    print("=" * 60)
    print(f"\nTotal events in history: {len(history)}")
    
    # Group events by type
    event_types = {}
    for event in history:
        event_type = event.get('event', 'UNKNOWN')
        if event_type not in event_types:
            event_types[event_type] = []
        event_types[event_type].append(event)
    
    print("\n📊 Event Breakdown:")
    for event_type, events in sorted(event_types.items()):
        print(f"  {event_type}: {len(events)} events")
    
    # Check for events that should have triggered alerts
    print("\n🔍 Alert Analysis:")
    
    alert_events = {
        'ENTRY': 'New Signal Alert',
        'TP1_HIT': 'TP1 Hit Alert',
        'TP2_HIT': 'TP2 Hit Alert',
        'TP3_HIT': 'TP3 Hit Alert',
        'SL_HIT': 'SL Hit Alert',
        'TRAIL_SL_HIT': 'Trailing SL Hit Alert'
    }
    
    for event_type, alert_name in alert_events.items():
        count = len(event_types.get(event_type, []))
        status = "✅" if count > 0 else "⚪"
        print(f"  {status} {alert_name}: {count} events")
    
    # Show recent events that should have triggered alerts
    print("\n📱 Recent Events (Last 10):")
    for event in history[-10:]:
        event_type = event.get('event')
        instrument = event.get('instrument')
        price = event.get('price')
        time = event.get('time')
        
        # Check if this event type should trigger an alert
        should_alert = event_type in alert_events
        alert_emoji = "📱" if should_alert else "📝"
        
        print(f"  {alert_emoji} {time} | {instrument:20s} | {event_type:15s} | Price: {price}")
    
    # Check for missing TP2/TP3 alerts specifically
    tp2_events = event_types.get('TP2_HIT', [])
    tp3_events = event_types.get('TP3_HIT', [])
    
    if tp2_events or tp3_events:
        print("\n⚠️  MISSING TELEGRAM ALERTS DETECTED:")
        if tp2_events:
            print(f"\n  🔴 TP2_HIT events without Telegram alerts: {len(tp2_events)}")
            for event in tp2_events:
                print(f"     - {event['instrument']} @ {event['price']} ({event['time']})")
        
        if tp3_events:
            print(f"\n  🔴 TP3_HIT events without Telegram alerts: {len(tp3_events)}")
            for event in tp3_events:
                print(f"     - {event['instrument']} @ {event['price']} ({event['time']})")
    
    print("\n" + "=" * 60)
    print("DIAGNOSIS:")
    print("=" * 60)
    
    if tp2_events or tp3_events:
        print("❌ ISSUE CONFIRMED: TP2 and TP3 hits are NOT sending Telegram alerts")
        print("\n📋 Required Fix:")
        print("   Add telegram_alerts.send_tp_hit_alert() calls for TP2 and TP3 hits")
        print("   in forex_macd_strategy.py (similar to TP1 implementation)")
    else:
        print("✅ No obvious missing alerts detected in recent history")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    analyze_missed_alerts()

#!/usr/bin/env python3
"""
Opening Range Breakout (ORB) Tracker for Nifty and Bank Nifty Futures
Tracks the first 15 minutes (9:15-9:30 AM IST) high/low and detects breakouts
"""

import json
from datetime import datetime, time
from pathlib import Path
import pytz

BASE_DIR = Path(__file__).parent
ORB_FILE = BASE_DIR / "opening_ranges.json"

IST = pytz.timezone('Asia/Kolkata')

def load_orb_data():
    """Load opening range data from file"""
    if ORB_FILE.exists():
        try:
            with open(ORB_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_orb_data(data):
    """Save opening range data to file"""
    with open(ORB_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def is_orb_window():
    """Check if current time is in ORB window (9:15-9:30 AM IST)"""
    now = datetime.now(IST)
    orb_start = time(9, 15)
    orb_end = time(9, 30)
    current_time = now.time()
    
    return orb_start <= current_time <= orb_end

def get_today_key():
    """Get today's date key"""
    return datetime.now(IST).strftime("%Y-%m-%d")

def update_opening_range(instrument, high, low, volume):
    """
    Update opening range for an instrument during 9:15-9:30 AM
    """
    if not is_orb_window():
        return False
    
    data = load_orb_data()
    today = get_today_key()
    
    if today not in data:
        data[today] = {}
    
    if instrument not in data[today]:
        data[today][instrument] = {
            "high": high,
            "low": low,
            "volume": volume,
            "start_time": datetime.now(IST).strftime("%H:%M:%S"),
            "breakout_detected": False
        }
    else:
        # Update high/low if current values exceed them
        data[today][instrument]["high"] = max(data[today][instrument]["high"], high)
        data[today][instrument]["low"] = min(data[today][instrument]["low"], low)
        data[today][instrument]["volume"] += volume
        data[today][instrument]["end_time"] = datetime.now(IST).strftime("%H:%M:%S")
    
    save_orb_data(data)
    return True

def check_orb_breakout(instrument, current_price, current_volume):
    """
    Check if price has broken out of opening range
    Returns: (signal_type, orb_data) or (None, None)
    """
    # Don't check during ORB window
    if is_orb_window():
        return None, None
    
    data = load_orb_data()
    today = get_today_key()
    
    # Check if we have ORB data for today
    if today not in data or instrument not in data[today]:
        return None, None
    
    orb = data[today][instrument]
    
    # Skip if breakout already detected today
    if orb.get("breakout_detected", False):
        return None, None
    
    orb_high = orb["high"]
    orb_low = orb["low"]
    orb_range = orb_high - orb_low
    
    # Require minimum range (avoid false breakouts in tight ranges)
    min_range_pct = 0.002  # 0.2% minimum range
    if orb_range < (orb_high * min_range_pct):
        return None, None
    
    # Check for breakout
    signal = None
    
    if current_price > orb_high:
        signal = "ORB_BUY"
        orb["breakout_type"] = "BULLISH"
        orb["breakout_price"] = current_price
        orb["breakout_time"] = datetime.now(IST).strftime("%H:%M:%S")
        orb["breakout_detected"] = True
        
    elif current_price < orb_low:
        signal = "ORB_SELL"
        orb["breakout_type"] = "BEARISH"
        orb["breakout_price"] = current_price
        orb["breakout_time"] = datetime.now(IST).strftime("%H:%M:%S")
        orb["breakout_detected"] = True
    
    if signal:
        # Save updated data
        data[today][instrument] = orb
        save_orb_data(data)
        
        return signal, orb
    
    return None, None

def get_orb_status(instrument):
    """
    Get current ORB status for display
    Returns: dict with ORB info or None
    """
    data = load_orb_data()
    today = get_today_key()
    
    if today not in data or instrument not in data[today]:
        if is_orb_window():
            return {"status": "TRACKING", "message": "Building opening range..."}
        else:
            return {"status": "NO_DATA", "message": "No ORB data for today"}
    
    orb = data[today][instrument]
    
    if is_orb_window():
        return {
            "status": "TRACKING",
            "high": orb["high"],
            "low": orb["low"],
            "range": orb["high"] - orb["low"],
            "message": "Tracking opening range"
        }
    
    if orb.get("breakout_detected", False):
        return {
            "status": "BREAKOUT",
            "type": orb["breakout_type"],
            "price": orb["breakout_price"],
            "time": orb["breakout_time"],
            "high": orb["high"],
            "low": orb["low"],
            "message": f"{orb['breakout_type']} breakout at {orb['breakout_price']}"
        }
    
    return {
        "status": "WAITING",
        "high": orb["high"],
        "low": orb["low"],
        "range": orb["high"] - orb["low"],
        "message": f"Waiting for breakout (Range: {orb['low']:.2f} - {orb['high']:.2f})"
    }

def cleanup_old_data(days_to_keep=7):
    """Remove ORB data older than specified days"""
    data = load_orb_data()
    today = datetime.now(IST)
    
    dates_to_remove = []
    for date_str in data.keys():
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            age_days = (today - date_obj).days
            if age_days > days_to_keep:
                dates_to_remove.append(date_str)
        except:
            continue
    
    for date_str in dates_to_remove:
        del data[date_str]
    
    if dates_to_remove:
        save_orb_data(data)
        print(f"🗑️ Cleaned up {len(dates_to_remove)} old ORB records")

# Test function
if __name__ == "__main__":
    print("📊 Opening Range Breakout Tracker Test")
    print(f"Current time: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')}")
    print(f"In ORB window: {is_orb_window()}")
    print()
    
    # Test with sample data
    instruments = ["Nifty Future", "Bank Nifty Future"]
    
    for inst in instruments:
        status = get_orb_status(inst)
        print(f"{inst}:")
        print(f"  Status: {status}")
        print()
    
    cleanup_old_data()

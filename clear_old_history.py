#!/usr/bin/env python3
"""
Clear Signal History - Keep only today's signals
Clears all signal history entries before today (2025-12-25)
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

# Today's date
TODAY = datetime(2025, 12, 25)

def clear_old_history(file_path):
    """Clear signal history older than today"""
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return
    
    # Load current history
    with open(file_path, 'r') as f:
        history = json.load(f)
    
    original_count = len(history)
    
    # Filter to keep only today's signals
    filtered_history = []
    for entry in history:
        try:
            # Parse the timestamp
            time_str = entry.get('time', '')
            if time_str:
                entry_date = datetime.fromisoformat(time_str.replace(' IST', ''))
                # Keep if it's today or later
                if entry_date.date() >= TODAY.date():
                    filtered_history.append(entry)
        except Exception as e:
            print(f"⚠️ Error parsing entry: {e}")
            # Keep entries we can't parse (to be safe)
            filtered_history.append(entry)
    
    # Save filtered history
    with open(file_path, 'w') as f:
        json.dump(filtered_history, f, indent=2)
    
    removed_count = original_count - len(filtered_history)
    print(f"✅ {file_path}")
    print(f"   Original: {original_count} entries")
    print(f"   Removed: {removed_count} entries")
    print(f"   Remaining: {len(filtered_history)} entries (today only)")

if __name__ == "__main__":
    print("🧹 Clearing Signal History (keeping only today's signals)")
    print(f"📅 Today: {TODAY.strftime('%Y-%m-%d')}")
    print()
    
    # Local environment
    local_file = Path(__file__).parent / "signal_history.json"
    print("📂 LOCAL ENVIRONMENT:")
    clear_old_history(local_file)
    print()
    
    # Production (HF deployment)
    hf_file = Path(__file__).parent.parent / "hf_deployment" / "signal_history.json"
    print("📂 PRODUCTION (HF) ENVIRONMENT:")
    clear_old_history(hf_file)
    print()
    
    print("✅ Done! Signal history cleared in both environments.")
    print("💡 Only today's signals (2025-12-25) are retained.")

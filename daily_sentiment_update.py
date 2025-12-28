#!/usr/bin/env python3
"""
Daily Retail Sentiment Updater
Run this once per day to update sentiment data from A1Trading
The data will be used throughout the day for all signal analysis
"""

import json
from datetime import datetime, timedelta
import os

SENTIMENT_FILE = "sentiment_data.json"

def check_if_update_needed():
    """Check if sentiment data needs updating (once per day)"""
    if not os.path.exists(SENTIMENT_FILE):
        return True, "No sentiment data file found"
    
    try:
        with open(SENTIMENT_FILE, 'r') as f:
            data = json.load(f)
            last_update = data.get('last_update')
            
            if not last_update:
                return True, "No last_update timestamp found"
            
            # Parse the timestamp
            last_update_dt = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
            now = datetime.now()
            
            # Check if it's been more than 24 hours
            if now - last_update_dt > timedelta(hours=24):
                return True, f"Last update was {(now - last_update_dt).total_seconds() / 3600:.1f} hours ago"
            else:
                hours_ago = (now - last_update_dt).total_seconds() / 3600
                return False, f"Updated {hours_ago:.1f} hours ago (still fresh)"
                
    except Exception as e:
        return True, f"Error reading sentiment file: {e}"

def update_sentiment_data():
    """Interactive update of sentiment data"""
    print("\n" + "="*70)
    print("📊 DAILY RETAIL SENTIMENT UPDATE")
    print("="*70)
    
    # Check if update is needed
    needs_update, reason = check_if_update_needed()
    
    print(f"\n📍 Status: {reason}")
    
    if not needs_update:
        print("\n✅ Sentiment data is still fresh (< 24 hours old)")
        print("   No update needed. Using existing data for today.")
        
        # Display current data
        with open(SENTIMENT_FILE, 'r') as f:
            data = json.load(f)
            print(f"\n📅 Last Updated: {data.get('last_update')}")
            print(f"📊 Instruments: {len(data.get('instruments', {}))}")
        
        response = input("\n⚠️  Force update anyway? (y/N): ").strip().lower()
        if response != 'y':
            print("\n✅ Keeping existing sentiment data")
            return False
    
    print("\n" + "="*70)
    print("📍 Visit: https://www.a1trading.com/retail-sentiment/")
    print("="*70)
    print("\n💡 TIP: Update this once in the morning, use all day!")
    print("\n⚠️  Enter the percentage of traders who are LONG for each pair")
    print("   (SHORT % will be calculated automatically)\n")
    
    instruments = [
        "EUR/USD", "USD/JPY", "GBP/USD", "USD/CHF", "USD/CAD",
        "AUD/USD", "NZD/USD", "EUR/GBP", "EUR/JPY", "GBP/JPY",
        "AUD/JPY", "NZD/JPY", "GBP/CHF", "EUR/CAD", "AUD/CAD"
    ]
    
    sentiment_data = {
        "last_update": datetime.now().isoformat(),
        "source": "A1Trading - Daily Update",
        "valid_until": (datetime.now() + timedelta(hours=24)).isoformat(),
        "instruments": {}
    }
    
    print("Enter sentiment data (or press Enter to skip):\n")
    
    for instrument in instruments:
        try:
            long_input = input(f"{instrument:12} - % LONG: ").strip()
            
            if not long_input:
                continue
            
            long_pct = float(long_input)
            
            if long_pct < 0 or long_pct > 100:
                print(f"  ❌ Invalid percentage. Skipping {instrument}")
                continue
            
            short_pct = 100 - long_pct
            net_position = long_pct - short_pct
            
            sentiment_data["instruments"][instrument] = {
                "long": long_pct,
                "short": short_pct,
                "net_position": net_position
            }
            
            # Show contrarian signal
            if long_pct > 60:
                signal = "🔴 SELL"
            elif short_pct > 60:
                signal = "🟢 BUY"
            else:
                signal = "⚪ NEUTRAL"
            
            print(f"  ✅ {long_pct}% L / {short_pct}% S → {signal}")
            
        except ValueError:
            print(f"  ❌ Invalid input. Skipping {instrument}")
            continue
        except KeyboardInterrupt:
            print("\n\n⚠️  Update cancelled by user")
            return False
    
    # Save to file
    if sentiment_data["instruments"]:
        with open(SENTIMENT_FILE, 'w') as f:
            json.dump(sentiment_data, f, indent=2)
        
        print("\n" + "="*70)
        print(f"✅ SENTIMENT DATA SAVED")
        print("="*70)
        print(f"📊 Updated {len(sentiment_data['instruments'])} instruments")
        print(f"📅 Valid until: {sentiment_data['valid_until'][:19]}")
        print(f"💾 File: {SENTIMENT_FILE}")
        print("\n💡 This data will be used for all signals today!")
        print("="*70)
        
        # Display summary
        print("\n📋 CONTRARIAN SIGNALS SUMMARY:")
        for instrument, data in sentiment_data["instruments"].items():
            if data['long'] > 60:
                signal = "🔴 SELL"
                strength = f"{((data['long'] - 50) / 50 * 100):.0f}%"
            elif data['short'] > 60:
                signal = "🟢 BUY"
                strength = f"{((data['short'] - 50) / 50 * 100):.0f}%"
            else:
                signal = "⚪ NEUTRAL"
                strength = "-"
            
            print(f"  {instrument:12} {data['long']:5.1f}% L / {data['short']:5.1f}% S → {signal:12} ({strength})")
        
        return True
    else:
        print("\n⚠️  No data entered. File not updated.")
        return False

def main():
    """Main entry point"""
    try:
        success = update_sentiment_data()
        
        if success:
            print("\n✅ Daily sentiment update complete!")
            print("   Run your strategy - it will use this data automatically.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()

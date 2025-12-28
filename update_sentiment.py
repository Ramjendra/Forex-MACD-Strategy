#!/usr/bin/env python3
"""
Helper script to update retail sentiment data
You can manually enter data from https://www.a1trading.com/retail-sentiment/
"""

import json
from datetime import datetime

def update_sentiment():
    """Interactive script to update sentiment data"""
    
    print("\n" + "="*60)
    print("📊 RETAIL SENTIMENT DATA UPDATER")
    print("="*60)
    print("\n📍 Visit: https://www.a1trading.com/retail-sentiment/")
    print("   Or use: https://www.myfxbook.com/community/outlook")
    print("\n⚠️  Enter the percentage of traders who are LONG for each pair")
    print("   (SHORT % will be calculated automatically as 100 - LONG %)\n")
    
    instruments = [
        "EUR/USD", "USD/JPY", "GBP/USD", "USD/CHF", "USD/CAD",
        "AUD/USD", "NZD/USD", "EUR/GBP", "EUR/JPY", "GBP/JPY"
    ]
    
    sentiment_data = {
        "last_update": datetime.now().isoformat(),
        "source": "A1Trading / Manual Entry",
        "instruments": {}
    }
    
    print("Enter sentiment data (or press Enter to skip):\n")
    
    for instrument in instruments:
        try:
            long_input = input(f"{instrument} - % LONG: ").strip()
            
            if not long_input:
                print(f"  ⏭️  Skipped {instrument}")
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
            
            print(f"  ✅ {instrument}: {long_pct}% LONG, {short_pct}% SHORT")
            
        except ValueError:
            print(f"  ❌ Invalid input. Skipping {instrument}")
            continue
        except KeyboardInterrupt:
            print("\n\n⚠️  Update cancelled by user")
            return
    
    # Save to file
    if sentiment_data["instruments"]:
        filename = "sentiment_data.json"
        with open(filename, 'w') as f:
            json.dump(sentiment_data, f, indent=2)
        
        print("\n" + "="*60)
        print(f"✅ Sentiment data saved to: {filename}")
        print(f"📊 Updated {len(sentiment_data['instruments'])} instruments")
        print("="*60)
        
        # Display summary
        print("\n📋 SUMMARY:")
        for instrument, data in sentiment_data["instruments"].items():
            if data['long'] > 60:
                signal = "🔴 CONTRARIAN SELL"
            elif data['short'] > 60:
                signal = "🟢 CONTRARIAN BUY"
            else:
                signal = "⚪ NEUTRAL"
            
            print(f"  {instrument}: {data['long']:.1f}% L / {data['short']:.1f}% S - {signal}")
    else:
        print("\n⚠️  No data entered. File not updated.")


if __name__ == "__main__":
    try:
        update_sentiment()
    except Exception as e:
        print(f"\n❌ Error: {e}")

#!/usr/bin/env python3
"""Quick test to see if NSE Live instruments can be analyzed"""
import sys
sys.path.insert(0, '/home/ramram/Desktop/SELF_LEARNING/Medical RAG/documents/Signal/Forex_MACD_Strategy')

from forex_macd_strategy import analyze_instrument, CONFIG

# Find NSE Live instruments
nse_instruments = [inst for inst in CONFIG['instruments'] if inst.get('category') == 'NSE Live']

print(f"Found {len(nse_instruments)} NSE Live instruments")

for inst in nse_instruments:
    print(f"\n{'='*60}")
    print(f"Testing: {inst['name']}")
    print(f"{'='*60}")
    try:
        result = analyze_instrument(inst)
        if result:
            print(f"✅ SUCCESS: {result['instrument']}")
            print(f"   Category: {result.get('category')}")
            print(f"   LTP: {result.get('ltp')}")
            print(f"   Status: {result.get('overall_status')}")
        else:
            print(f"❌ FAILED: analyze_instrument returned None")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

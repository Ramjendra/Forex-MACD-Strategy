#!/usr/bin/env python3
"""Quick NSE-only test - generate signals for just NSE Live instruments"""
import sys
import os

# Set environment to run once
os.environ['RUN_ONCE'] = 'True'

# Temporarily modify CONFIG to only include NSE Live
import forex_macd_strategy as strategy

# Backup original config
original_instruments = strategy.CONFIG['instruments'].copy()

# Keep only NSE Live instruments
nse_only = [inst for inst in original_instruments if inst.get('category') == 'NSE Live']
print(f"Testing {len(nse_only)} NSE Live instruments: {[i['name'] for i in nse_only]}")

strategy.CONFIG['instruments'] = nse_only

# Run the strategy
try:
    strategy.main()
    print("\n✅ Strategy completed successfully")
except Exception as e:
    print(f"\n❌ Strategy failed: {e}")
    import traceback
    traceback.print_exc()

# Check results
import json
with open('forex_macd_signals.json', 'r') as f:
    data = json.load(f)

nse_results = [d for d in data['data'] if d.get('category') == 'NSE Live']
print(f"\n📊 Results: {len(nse_results)} NSE Live instruments in JSON")
for inst in nse_results:
    print(f"  ✅ {inst['instrument']}: ₹{inst['ltp']:.2f} - {inst['overall_status']}")

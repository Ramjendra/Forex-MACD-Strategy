#!/usr/bin/env python3
"""Test NSE Live instrument processing"""
import json
from pathlib import Path

# Load config from strategy file
config_file = Path(__file__).parent / "forex_macd_strategy.py"
with open(config_file, 'r') as f:
    content = f.read()

# Find NSE Live instruments in CONFIG
nse_instruments = []
in_config = False
for line in content.split('\n'):
    if '"instruments": [' in line:
        in_config = True
    if in_config and 'NSE Live' in line:
        print(f"Found NSE Live line: {line.strip()}")
        if '"name":' in line:
            name = line.split('"name":')[1].split('"')[1]
            nse_instruments.append(name)

print(f"\n✅ NSE Live instruments in CONFIG: {nse_instruments}")

# Check signals JSON
signals_file = Path(__file__).parent / "forex_macd_signals.json"
if signals_file.exists():
    with open(signals_file, 'r') as f:
        data = json.load(f)
    
    nse_in_json = [d['instrument'] for d in data['data'] if d.get('category') == 'NSE Live']
    print(f"✅ NSE Live instruments in JSON: {nse_in_json}")
    
    all_categories = {}
    for d in data['data']:
        cat = d.get('category', 'Unknown')
        all_categories[cat] = all_categories.get(cat, 0) + 1
    
    print(f"\n📊 All categories in JSON:")
    for cat, count in sorted(all_categories.items()):
        print(f"  {cat}: {count}")
else:
    print("❌ signals JSON file not found")

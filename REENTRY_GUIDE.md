# 🔄 Reentry Logic - Quick Reference Guide

## ✅ System Status

- **Strategy**: ✅ Running (PID: 156697)
- **Server**: ✅ Running (PID: 80131)
- **Reentry Detection**: ✅ Enabled (Forex only)
- **Dashboard**: ✅ Ready at http://localhost:5000

---

## 🚀 Quick Commands

### View Reentry Opportunities
```bash
cd /home/ramram/Desktop/SELF_LEARNING/Medical\ RAG/documents/Signal/Forex_MACD_Strategy
./monitor_reentry.sh
```

### Watch Live Detections
```bash
tail -f forex_strategy.log | grep '🔄'
```

### Test Dashboard Display
```bash
python3 inject_mock_reentry.py
# Then open: http://localhost:5000
# Navigate to: "Forex Live Signal" tab
```

### Filter High-Strength Only (≥70%)
```bash
cat forex_macd_signals.json | jq '.data[] | select(.re_entry.strength >= 70)'
```

---

## 📊 Dashboard Access

**URL**: http://localhost:5000

**Navigation**:
1. Open dashboard in browser
2. Click **"Forex Live Signal"** tab
3. Look for instruments with active signals
4. Reentry panels appear below signal panels (blue dashed border)

**Visual Indicators**:
- 🟢 **Green Badge**: High strength (70-100%)
- 🟡 **Orange Badge**: Medium strength (50-69%)
- ⚪ **Gray Badge**: Low strength (40-49%)

---

## 🎯 Reentry Criteria

### Minimum Requirements
- ✅ Active signal in Forex category
- ✅ Pullback: 5-25 pips from entry
- ✅ Strength score: ≥ 40%
- ✅ Risk-Reward ratio: ≥ 1.5:1

### Strength Scoring (0-100)
- **Fibonacci Alignment** (30%): Distance from Fib level
- **Histogram Strength** (25%): MACD momentum
- **RSI Confirmation** (20%): Oversold/overbought
- **Rejection Candle** (25%): Wick quality

### Fibonacci Levels
- 23.6% (shallow pullback)
- 38.2% (moderate pullback)
- 50.0% (half retracement)
- 61.8% (deep pullback)

---

## 🔧 Configuration

### Enable for Additional Categories
Edit `forex_macd_strategy.py` line 611:
```python
REENTRY_ENABLED_CATEGORIES = ['Forex', 'Metals/Energy']
```

### Adjust Strength Threshold
Edit `forex_macd_strategy.py` line 706 (SELL) or line 802 (BUY):
```python
if strength >= 50 and risk_reward_ratio >= 1.5:  # Changed from 40 to 50
```

### Restart After Changes
```bash
pkill -f forex_macd_strategy.py
nohup python3 forex_macd_strategy.py > forex_strategy.log 2>&1 &
```

---

## 📝 Current Test Data

**Injected Mock Opportunities**:
1. **USD/CHF**: SELL reentry at 50% Fib (85% strength, 1:2.8 R:R)
2. **Silver**: BUY reentry at 38.2% Fib (62% strength, 1:2.1 R:R)

**Remove Test Data**:
```bash
# Strategy will overwrite on next cycle (wait 60 seconds)
# Or restart strategy to clear immediately
```

---

## 🐛 Troubleshooting

### Reentry Not Showing
1. Check category: `cat forex_macd_signals.json | jq '.data[] | select(.signal != null) | .category'`
2. Verify pullback range: 5-25 pips from entry
3. Check strength: Must be ≥ 40%
4. Verify R:R: Must be ≥ 1.5:1

### Dashboard Not Updating
1. Hard refresh: Ctrl+Shift+R (Chrome) or Cmd+Shift+R (Mac)
2. Check server: `ps aux | grep serve_forex_macd`
3. Check strategy: `ps aux | grep forex_macd_strategy`

### No Active Signals
- Wait for market conditions to align
- Check market hours for Indian instruments
- Verify trend/momentum/entry alignment

---

## 📚 Documentation

- **Implementation Plan**: [implementation_plan.md](file:///home/ramram/.gemini/antigravity/brain/512e990b-e800-4050-841a-a30230132264/implementation_plan.md)
- **Walkthrough**: [walkthrough.md](file:///home/ramram/.gemini/antigravity/brain/512e990b-e800-4050-841a-a30230132264/walkthrough.md)
- **Task Checklist**: [task.md](file:///home/ramram/.gemini/antigravity/brain/512e990b-e800-4050-841a-a30230132264/task.md)

---

## 🎉 Next Steps

1. **Test Dashboard**: Open http://localhost:5000 and verify reentry panels
2. **Monitor Live**: Run `./monitor_reentry.sh` periodically
3. **Wait for Real Opportunities**: Let market conditions trigger natural reentries
4. **Adjust Thresholds**: Fine-tune based on performance
5. **Expand Categories**: Enable for Metals/Energy if desired

---

**Last Updated**: 2025-12-24 19:10 IST

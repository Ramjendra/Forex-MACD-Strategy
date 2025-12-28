# 🚀 Nifty/BN Strategy - Quick Reference

## ✅ What's New (Optimized for 3-4 Day Swing Trades)

### 1. Safer Stop Loss
- **NSE Live**: 2.5x ATR (was 1.5x)
- **Benefit**: Withstands overnight gaps and volatility

### 2. Volume Filter
- **Requirement**: Volume >= 1.2x 20-day average
- **Benefit**: Avoids low-liquidity false signals

### 3. Opening Range Breakout (ORB)
- **Tracks**: 9:15-9:30 AM high/low
- **Detects**: Breakouts after 9:30 AM
- **Benefit**: Captures strong directional moves

### 4. Pre-Market Global Cues
- **Sources**: US markets, Asian markets, SGX Nifty, Oil, Dollar
- **Applied**: First hour only (9:15-10:15 AM)
- **Benefit**: Aligns with global sentiment

---

## 📋 Daily Checklist

### Before Market (8:00-9:00 AM)
```bash
cd /home/ramram/Desktop/SELF_LEARNING/Medical\ RAG/documents/Signal/Forex_MACD_Strategy
python3 premarket_analysis.py
```

### Check Strategy Status
```bash
ps aux | grep forex_macd_strategy | grep -v grep
tail -50 strategy.log
```

---

## 🎯 Expected Behavior

### Volume Filter Messages
```
✅ Nifty Future: Volume confirmed (1.45x avg)
⚠️ Bank Nifty Future: Volume too low (0.85x avg) - skipping signal
```

### Pre-Market Filter Messages (9:15-10:15 AM only)
```
✅ Nifty Future: Pre-market sentiment aligned (BULLISH)
⚠️ Bank Nifty Future: Pre-market sentiment BEARISH - skipping BUY
```

### Signal Example with Safer SL
```
🆕 Nifty Future: NEW BUY SIGNAL @ 23450.50
   SL: 23250.00 (200.50 points = 2.5x ATR)
   TP1: 23750.75 | TP2: 24050.50 | TP3: 24450.75
```

---

## 🔧 Configuration

**Location**: `forex_macd_strategy.py` → `CONFIG['nse_specific']`

```python
{
    "sl_atr_multiplier": 2.5,      # Safer SL
    "volume_multiplier": 1.2,       # Volume filter
    "volume_lookback": 20,          # Days for avg volume
    "orb_enabled": True,            # Enable ORB
    "orb_duration_minutes": 15,     # 9:15-9:30 AM
    "premarket_filter": True,       # Use global cues
    "first_hour_end": "10:15"       # Filter till 10:15 AM
}
```

---

## 📊 Files Created

- `opening_range_tracker.py` - ORB detection
- `premarket_analysis.py` - Global cues
- `opening_ranges.json` - Daily ORB data (auto-created)
- `premarket_cues.json` - Cached sentiment (auto-created)

---

## ⚡ Quick Commands

**Restart Strategy:**
```bash
pkill -f "python3 forex_macd_strategy.py"
nohup python3 forex_macd_strategy.py > strategy.log 2>&1 &
```

**Test ORB:**
```bash
python3 opening_range_tracker.py
```

**Test Pre-Market:**
```bash
python3 premarket_analysis.py
```

**Check Config:**
```bash
python3 -c "from forex_macd_strategy import CONFIG; print(CONFIG['nse_specific'])"
```

---

## 🎯 Status: PRODUCTION READY ✅

All features implemented and tested!
Strategy running with PID: 246133

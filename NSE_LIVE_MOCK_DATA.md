# NSE Live Mock Data - Quick Reference

## Generated Mock Signals

### 🔹 Nifty Future (ACTIVE BUY)
- **Contract**: JAN 26 (Expiry: 29-Jan-2026, 34 days remaining)
- **Signal Type**: BUY
- **Entry Price**: 26,150.00
- **Current Price**: 26,285.50 ✅ (+135.50 points profit)
- **Stop Loss**: 26,150.00 (Moved to Breakeven)
- **Take Profits**:
  - TP1: 26,300.00 ✅ **HIT**
  - TP2: 26,450.00 (Next Target)
  - TP3: 26,650.00
- **Status**: Trailing SL Active
- **Trend Analysis**:
  - 1D Trend: BULLISH ✅
  - 4H Momentum: BULLISH ✅
  - 1H Entry: BULLISH_MOM ✅

### 🔹 Bank Nifty Future (ACTIVE SELL + REENTRY)
- **Contract**: JAN 26 (Expiry: 29-Jan-2026, 34 days remaining)
- **Signal Type**: SELL
- **Entry Price**: 59,200.00
- **Current Price**: 58,950.25 ✅ (+249.75 points profit)
- **Stop Loss**: 59,200.00 (Moved to Breakeven)
- **Take Profits**:
  - TP1: 58,825.00 ✅ **HIT**
  - TP2: 58,450.00 (Next Target)
  - TP3: 57,950.00
- **Status**: Reentry Opportunity Available
- **Reentry Details**:
  - Type: ADD_TO_SELL
  - Strength: 85% (High Confidence)
  - Suggested Entry: 58,975.00
  - Rejection Zone: 58,900 - 59,050
  - Fibonacci Level: 61.8% retracement
  - Risk:Reward: 1:3.2
  - Confirmation: Strong bearish momentum (Histogram: -12.45, RSI: 42.3)
- **Trend Analysis**:
  - 1D Trend: BEARISH ✅
  - 4H Momentum: BEARISH ✅
  - 1H Entry: BEARISH_MOM ✅

## How to Use

### Generate Mock Data
```bash
cd /home/ramram/Desktop/SELF_LEARNING/Medical\ RAG/documents/Signal/Forex_MACD_Strategy
python3 generate_nse_mock_data.py
```

### View NSE Live Tab
1. Open your dashboard: http://localhost:8000
2. Click on "🇮🇳 NSE Live" tab
3. You should see both Nifty Future and Bank Nifty Future with active signals

### Reset to Real Data
Simply run the strategy script again to fetch real market data:
```bash
RUN_ONCE=true python3 forex_macd_strategy.py
```

## Mock Data Features

✅ **Realistic Signal Lifecycle**
- Both signals have TP1 hit
- Stop losses moved to breakeven (risk-free trades)
- Showing trailing SL functionality

✅ **Reentry Opportunity**
- Bank Nifty shows a reentry opportunity
- Fibonacci-based pullback (61.8%)
- High confidence (85% strength)
- Clear rejection zone and risk:reward ratio

✅ **Contract Information**
- Current contract: JAN 26
- Expiry date: 29-Jan-2026
- Days to expiry: 34 days
- Auto-rollover logic in place

✅ **Complete Technical Analysis**
- All three timeframes (1D, 4H, 1H) aligned
- MACD indicators showing momentum
- RSI and EMA 200 confirmation
- Real-time price updates

## Dashboard Display

When you view the NSE Live tab, you'll see:

1. **Nifty Future Card** (Green/Bullish)
   - Active BUY signal badge
   - "Trailing SL Active" lifecycle status
   - TP1 marked as hit with checkmark
   - Current profit displayed
   - Breakeven SL highlighted

2. **Bank Nifty Future Card** (Red/Bearish)
   - Active SELL signal badge
   - "Reentry Opportunity" lifecycle status
   - TP1 marked as hit with checkmark
   - Reentry panel with:
     - High strength badge (85%)
     - Suggested entry price
     - Rejection zone
     - Fibonacci level
     - Risk:reward ratio
     - Confirmation details

## Notes

- Mock data is persistent until you run the strategy script again
- Contract information updates automatically based on current date
- All prices and indicators are realistic and aligned
- Perfect for testing dashboard UI and functionality

# Retail Sentiment Integration

## Overview
Integration of retail sentiment analysis from A1Trading and other sources to provide contrarian signals alongside MACD strategy signals.

## Files Created

### 1. `retail_sentiment.py`
Core sentiment analysis module with:
- Manual sentiment data loading
- Contrarian signal generation
- Signal enrichment capabilities
- Support for multiple data sources (A1Trading, MyFxBook, DailyFX)

### 2. `update_sentiment.py`
Interactive helper script to easily update sentiment data from A1Trading website

### 3. `sentiment_data.json`
Data file storing retail positioning percentages

## How to Use

### Step 1: Update Sentiment Data

Visit https://www.a1trading.com/retail-sentiment/ and run:

```bash
python3 update_sentiment.py
```

Enter the percentage of traders who are LONG for each pair (SHORT % is calculated automatically).

### Step 2: View Sentiment Analysis

```bash
python3 retail_sentiment.py
```

This displays contrarian signals based on retail positioning.

### Step 3: Integration with Main Strategy

The sentiment module can enrich your existing signals with:
- Retail positioning data (% long vs % short)
- Contrarian bias (BUY/SELL/NEUTRAL)
- Signal strength (0-100 scale)
- Alignment indicator (whether MACD signal aligns with contrarian sentiment)

## Contrarian Rules

- **>60% retail LONG** → Contrarian SELL signal
- **>60% retail SHORT** → Contrarian BUY signal
- **40-60% balanced** → Neutral sentiment

## Signal Confirmation

When your MACD signal **aligns** with contrarian sentiment:
- ✅ **STRONG** - High probability setup
- ⚠️ **WEAK** - Lower confidence (retail may be right this time)

## Example Output

```
USD/CHF:
  Long: 72.5% | Short: 27.5%
  ⚠️ 72.5% retail traders are LONG - Contrarian SELL signal
  
  Your MACD Signal: SELL
  Sentiment Confirmation: ✅ STRONG (aligned with contrarian bias)
```

## Next Steps

To fully integrate into `forex_macd_strategy.py`:
1. Import the sentiment analyzer
2. Load sentiment data at startup
3. Enrich each signal with sentiment analysis
4. Display sentiment info in dashboard
5. Add sentiment filter option (only take signals aligned with sentiment)

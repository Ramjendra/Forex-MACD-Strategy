#!/bin/bash
# Morning Routine - Run this once each morning
# Updates sentiment data and starts the trading strategy

echo "=================================="
echo "🌅 MORNING TRADING ROUTINE"
echo "=================================="
echo ""

# Step 1: Update sentiment data
echo "📊 Step 1: Updating retail sentiment data..."
echo "   Visit: https://www.a1trading.com/retail-sentiment/"
echo ""
python3 daily_sentiment_update.py

echo ""
echo "=================================="
echo "✅ Morning routine complete!"
echo "=================================="
echo ""
echo "💡 Next steps:"
echo "   1. Your sentiment data is set for the day"
echo "   2. Run your strategy - it will use this data"
echo "   3. No need to update again until tomorrow"
echo ""

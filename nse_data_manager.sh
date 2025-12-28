#!/bin/bash
# NSE Live Data Manager - Toggle between mock and real data

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║       🇮🇳 NSE LIVE DATA MANAGER                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Function to show current status
show_status() {
    echo "📊 Current NSE Live Status:"
    echo ""
    cat forex_macd_signals.json | jq -r '.data[] | select(.category == "NSE Live") | "  \(.instrument): \(.overall_status) | Price: \(.ltp) | Signal: \(.signal.type // "None")"'
    echo ""
}

# Menu
echo "Select an option:"
echo ""
echo "  1) 🎭 Generate Mock Data (Active signals with TP1 hit)"
echo "  2) 📡 Fetch Real Market Data"
echo "  3) 📊 Show Current Status"
echo "  4) 🌐 Open Dashboard"
echo "  5) ❌ Exit"
echo ""
read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        echo ""
        echo "🎭 Generating mock data for NSE Live..."
        python3 generate_nse_mock_data.py
        echo ""
        echo "✅ Mock data generated!"
        echo "🌐 View at: http://localhost:8000 (NSE Live tab)"
        ;;
    2)
        echo ""
        echo "📡 Fetching real market data..."
        RUN_ONCE=true python3 forex_macd_strategy.py 2>&1 | grep -E "Nifty|Bank Nifty|Saved to"
        echo ""
        echo "✅ Real data fetched!"
        echo "🌐 View at: http://localhost:8000 (NSE Live tab)"
        ;;
    3)
        echo ""
        show_status
        ;;
    4)
        echo ""
        echo "🌐 Opening dashboard..."
        if command -v xdg-open &> /dev/null; then
            xdg-open http://localhost:8000
        elif command -v open &> /dev/null; then
            open http://localhost:8000
        else
            echo "Please open: http://localhost:8000"
        fi
        ;;
    5)
        echo ""
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo ""
        echo "❌ Invalid choice. Please run again."
        exit 1
        ;;
esac

echo ""
echo "═══════════════════════════════════════════════════════════"

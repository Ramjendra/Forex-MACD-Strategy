#!/bin/bash
# Enhanced Re-Entry Monitor - Watch for Fibonacci-based reentry opportunities

FOREX_DIR="/home/ramram/Desktop/SELF_LEARNING/Medical RAG/documents/Signal/Forex_MACD_Strategy"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    🔄 FIBONACCI RE-ENTRY OPPORTUNITY MONITOR 🔄       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

cd "$FOREX_DIR"

if [ ! -f "forex_macd_signals.json" ]; then
    echo -e "${RED}✗ No signals file found${NC}"
    exit 1
fi

echo -e "${CYAN}📊 Scanning for Re-Entry Opportunities...${NC}"
echo ""

# Extract re-entry opportunities with enhanced details
OPPORTUNITIES=$(cat forex_macd_signals.json | jq -r '.data[] | select(.re_entry != null) | "\(.instrument)|\(.re_entry.type)|\(.re_entry.strength)|\(.re_entry.suggested_entry)|\(.re_entry.fib_level)|\(.re_entry.risk_reward)|\(.re_entry.reason)"' 2>/dev/null)

if [ -z "$OPPORTUNITIES" ]; then
    echo -e "${YELLOW}⚠ No re-entry opportunities at this time${NC}"
    echo ""
    echo -e "${BLUE}Active Positions Being Monitored:${NC}"
    cat forex_macd_signals.json | jq -r '.data[] | select(.signal != null) | "  \(.instrument): \(.signal.type) @ \(.signal.entry_price) | Current: \(.ltp)"' 2>/dev/null | head -10
    
    if [ -z "$(cat forex_macd_signals.json | jq -r '.data[] | select(.signal != null)' 2>/dev/null)" ]; then
        echo -e "${YELLOW}  No active signals to monitor${NC}"
    fi
else
    echo "$OPPORTUNITIES" | while IFS='|' read -r instrument type strength entry fib_level rr reason; do
        # Color code by strength
        if [ "$strength" -ge 70 ]; then
            STRENGTH_COLOR=$GREEN
            STRENGTH_LABEL="🟢 HIGH"
        elif [ "$strength" -ge 50 ]; then
            STRENGTH_COLOR=$YELLOW
            STRENGTH_LABEL="🟡 MEDIUM"
        else
            STRENGTH_COLOR=$RED
            STRENGTH_LABEL="🔴 LOW"
        fi
        
        # Color code by type
        if [[ "$type" == *"BUY"* ]]; then
            TYPE_COLOR=$GREEN
        else
            TYPE_COLOR=$RED
        fi
        
        echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${CYAN}🎯 $instrument${NC}"
        echo -e "   ${TYPE_COLOR}Type:${NC} $type"
        echo -e "   ${STRENGTH_COLOR}Strength:${NC} $STRENGTH_LABEL ($strength%)"
        echo -e "   ${BLUE}Entry:${NC} $entry"
        echo -e "   ${YELLOW}Fibonacci:${NC} $fib_level"
        echo -e "   ${GREEN}R:R Ratio:${NC} $rr"
        echo -e "   ${CYAN}Reason:${NC} $reason"
        echo ""
    done
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
fi

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    QUICK COMMANDS                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo -e "${CYAN}  Watch live:${NC} tail -f forex_strategy.log | grep '🔄'"
echo -e "${CYAN}  Check specific:${NC} cat forex_macd_signals.json | jq '.data[] | select(.instrument == \"EUR/USD\") | .re_entry'"
echo -e "${CYAN}  High strength only:${NC} cat forex_macd_signals.json | jq '.data[] | select(.re_entry.strength >= 70)'"
echo ""

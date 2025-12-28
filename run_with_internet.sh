#!/bin/bash
# Run Forex MACD Dashboard with Internet Access in Screen
# Includes ngrok tunnel for public access

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

SESSION_NAME="forex-macd-web"
VENV_PATH="$SCRIPT_DIR/../.venv"
NGROK_BIN="$SCRIPT_DIR/../ngrok"
PORT=8003

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if screen is installed
if ! command -v screen &> /dev/null; then
    echo -e "${RED}Error: 'screen' is not installed.${NC}"
    echo "Install it with: sudo apt-get install screen"
    exit 1
fi

# Check if ngrok exists
if [ ! -f "$NGROK_BIN" ]; then
    echo -e "${RED}Error: Ngrok not found at $NGROK_BIN${NC}"
    exit 1
fi

session_exists() {
    screen -list | grep -q "$SESSION_NAME"
}

get_ngrok_url() {
    sleep 3
    curl -s http://localhost:4040/api/tunnels 2>/dev/null | grep -o '"public_url":"https://[^"]*' | head -1 | cut -d'"' -f4
}

case "${1:-start}" in
    start)
        if session_exists; then
            echo -e "${YELLOW}Session '$SESSION_NAME' already exists.${NC}"
            echo "Use '$0 attach' to view it or '$0 stop' to stop it."
            exit 1
        fi
        
        echo -e "${GREEN}Starting Forex MACD Dashboard with Internet Access...${NC}"
        echo ""
        
        # Create screen session
        screen -dmS "$SESSION_NAME" bash -c "
            cd '$SCRIPT_DIR'
            
            # Activate virtual environment
            if [ -d '$VENV_PATH' ]; then
                source '$VENV_PATH/bin/activate'
            fi
            
            # Start strategy
            echo '✓ Starting strategy script...'
            python3 forex_macd_strategy.py &
            STRATEGY_PID=\$!
            
            # Wait for strategy
            sleep 3
            
            # Start server
            echo '✓ Starting web server on port $PORT...'
            python3 serve_forex_macd.py &
            SERVER_PID=\$!
            
            # Wait for server
            sleep 2
            
            # Start ngrok
            echo '✓ Starting ngrok tunnel...'
            '$NGROK_BIN' http $PORT --log=stdout
            
            # If ngrok exits, kill other processes
            kill \$STRATEGY_PID \$SERVER_PID 2>/dev/null || true
        "
        
        echo -e "${GREEN}✓ Session started successfully!${NC}"
        echo ""
        
        # Wait for ngrok to start
        sleep 4
        
        PUBLIC_URL=$(get_ngrok_url)
        
        echo "=========================================="
        echo -e "${BLUE}📊 Dashboard Access:${NC}"
        echo "  Local:    http://localhost:$PORT/forex_macd_dashboard.html"
        
        if [ -n "$PUBLIC_URL" ]; then
            echo -e "  Internet: ${GREEN}$PUBLIC_URL/forex_macd_dashboard.html${NC}"
        else
            echo -e "  Internet: ${YELLOW}Retrieving... (run: $0 url)${NC}"
        fi
        
        echo ""
        echo -e "${BLUE}🎮 Commands:${NC}"
        echo "  View session:   $0 attach"
        echo "  Get URL:        $0 url"
        echo "  Stop session:   $0 stop"
        echo "  Check status:   $0 status"
        echo "=========================================="
        ;;
        
    stop)
        if ! session_exists; then
            echo -e "${RED}Session '$SESSION_NAME' is not running.${NC}"
            exit 1
        fi
        
        echo -e "${GREEN}Stopping session '$SESSION_NAME'...${NC}"
        screen -S "$SESSION_NAME" -X quit
        echo -e "${GREEN}✓ Session stopped${NC}"
        ;;
        
    attach)
        if ! session_exists; then
            echo -e "${RED}Session '$SESSION_NAME' is not running.${NC}"
            echo "Start it with: $0 start"
            exit 1
        fi
        
        echo -e "${BLUE}Attaching to session '$SESSION_NAME'...${NC}"
        echo "Press Ctrl+A then D to detach without stopping"
        sleep 2
        screen -r "$SESSION_NAME"
        ;;
        
    status)
        if session_exists; then
            echo -e "${GREEN}✓ Session '$SESSION_NAME' is running${NC}"
            echo ""
            screen -list | grep "$SESSION_NAME"
            echo ""
            
            PUBLIC_URL=$(get_ngrok_url)
            if [ -n "$PUBLIC_URL" ]; then
                echo "Public URL: $PUBLIC_URL/forex_macd_dashboard.html"
            else
                echo "Local URL: http://localhost:$PORT/forex_macd_dashboard.html"
            fi
        else
            echo -e "${RED}✗ Session '$SESSION_NAME' is not running${NC}"
        fi
        ;;
        
    url)
        if ! session_exists; then
            echo -e "${RED}Session is not running. Start it first with: $0 start${NC}"
            exit 1
        fi
        
        PUBLIC_URL=$(get_ngrok_url)
        
        if [ -n "$PUBLIC_URL" ]; then
            echo "=========================================="
            echo -e "${GREEN}Public Dashboard URL:${NC}"
            echo ""
            echo -e "${BLUE}$PUBLIC_URL/forex_macd_dashboard.html${NC}"
            echo ""
            echo "=========================================="
        else
            echo -e "${RED}Could not retrieve ngrok URL.${NC}"
            echo "The tunnel might still be starting. Wait a moment and try again."
        fi
        ;;
        
    *)
        echo "Usage: $0 {start|stop|attach|status|url}"
        echo ""
        echo "Commands:"
        echo "  start   - Start dashboard with internet access"
        echo "  stop    - Stop the session"
        echo "  attach  - Attach to running session (Ctrl+A D to detach)"
        echo "  status  - Check if session is running"
        echo "  url     - Display public internet URL"
        exit 1
        ;;
esac

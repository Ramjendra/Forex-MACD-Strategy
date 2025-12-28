#!/bin/bash
# Forex MACD Dashboard with Internet Access (Ngrok)
# This script starts the dashboard and creates a public internet URL

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Configuration
VENV_PATH="$SCRIPT_DIR/../.venv"
STRATEGY_SCRIPT="$SCRIPT_DIR/forex_macd_strategy.py"
SERVER_SCRIPT="$SCRIPT_DIR/serve_forex_macd.py"
NGROK_BIN="$SCRIPT_DIR/../ngrok"
LOG_DIR="$SCRIPT_DIR/logs"
STRATEGY_LOG="$LOG_DIR/strategy.log"
SERVER_LOG="$LOG_DIR/server.log"
NGROK_LOG="$LOG_DIR/ngrok.log"
PID_DIR="$SCRIPT_DIR/pids"
STRATEGY_PID="$PID_DIR/strategy.pid"
SERVER_PID="$PID_DIR/server.pid"
NGROK_PID="$PID_DIR/ngrok.pid"
PORT=8003

# Create directories
mkdir -p "$LOG_DIR"
mkdir -p "$PID_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

is_running() {
    local pid_file=$1
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

get_ngrok_url() {
    # Wait a moment for ngrok to initialize
    sleep 3
    
    # Try to get the public URL from ngrok API
    local url=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | grep -o '"public_url":"https://[^"]*' | head -1 | cut -d'"' -f4)
    
    if [ -n "$url" ]; then
        echo "$url"
    else
        echo ""
    fi
}

stop_processes() {
    log "Stopping all services..."
    
    if is_running "$NGROK_PID"; then
        local pid=$(cat "$NGROK_PID")
        log "Stopping ngrok tunnel (PID: $pid)..."
        kill "$pid" 2>/dev/null || true
        rm -f "$NGROK_PID"
    fi
    
    if is_running "$SERVER_PID"; then
        local pid=$(cat "$SERVER_PID")
        log "Stopping server (PID: $pid)..."
        kill "$pid" 2>/dev/null || true
        rm -f "$SERVER_PID"
    fi
    
    if is_running "$STRATEGY_PID"; then
        local pid=$(cat "$STRATEGY_PID")
        log "Stopping strategy (PID: $pid)..."
        kill "$pid" 2>/dev/null || true
        rm -f "$STRATEGY_PID"
    fi
    
    log "✓ All services stopped"
}

start_processes() {
    log "Starting Forex MACD Dashboard with Internet Access..."
    echo ""
    
    # Check if ngrok exists
    if [ ! -f "$NGROK_BIN" ]; then
        error "Ngrok not found at $NGROK_BIN"
        exit 1
    fi
    
    # Activate virtual environment
    if [ -d "$VENV_PATH" ]; then
        log "Activating virtual environment..."
        source "$VENV_PATH/bin/activate"
    else
        warn "Virtual environment not found at $VENV_PATH"
    fi
    
    # Start strategy script
    log "Starting strategy script..."
    nohup python3 "$STRATEGY_SCRIPT" >> "$STRATEGY_LOG" 2>&1 &
    echo $! > "$STRATEGY_PID"
    log "✓ Strategy started (PID: $(cat $STRATEGY_PID))"
    
    # Wait for strategy to initialize
    sleep 2
    
    # Start server
    log "Starting web server on port $PORT..."
    nohup python3 "$SERVER_SCRIPT" >> "$SERVER_LOG" 2>&1 &
    echo $! > "$SERVER_PID"
    log "✓ Server started (PID: $(cat $SERVER_PID))"
    
    # Wait for server to be ready
    sleep 2
    
    # Start ngrok tunnel
    log "Starting ngrok tunnel..."
    nohup "$NGROK_BIN" http $PORT --log=stdout > "$NGROK_LOG" 2>&1 &
    echo $! > "$NGROK_PID"
    log "✓ Ngrok started (PID: $(cat $NGROK_PID))"
    
    # Get public URL
    log "Retrieving public URL..."
    PUBLIC_URL=$(get_ngrok_url)
    
    echo ""
    echo "=========================================="
    echo -e "${GREEN}✓ All services started successfully!${NC}"
    echo "=========================================="
    echo ""
    echo -e "${BLUE}📊 Dashboard Access:${NC}"
    echo -e "  Local:    http://localhost:$PORT/forex_macd_dashboard.html"
    
    if [ -n "$PUBLIC_URL" ]; then
        echo -e "  Internet: ${GREEN}$PUBLIC_URL/forex_macd_dashboard.html${NC}"
        echo ""
        echo -e "${YELLOW}⚠️  Share this URL to access from anywhere!${NC}"
    else
        echo -e "  Internet: ${YELLOW}Retrieving... (check logs or run: $0 url)${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}📁 Log Files:${NC}"
    echo "  Strategy: $STRATEGY_LOG"
    echo "  Server:   $SERVER_LOG"
    echo "  Ngrok:    $NGROK_LOG"
    echo ""
    echo -e "${BLUE}🎮 Management:${NC}"
    echo "  Status:   $0 status"
    echo "  Get URL:  $0 url"
    echo "  Stop:     $0 stop"
    echo "  Restart:  $0 restart"
    echo "=========================================="
}

show_status() {
    echo "Forex MACD Service Status:"
    echo "=========================="
    
    if is_running "$STRATEGY_PID"; then
        echo -e "${GREEN}✓${NC} Strategy: Running (PID: $(cat $STRATEGY_PID))"
    else
        echo -e "${RED}✗${NC} Strategy: Not running"
    fi
    
    if is_running "$SERVER_PID"; then
        echo -e "${GREEN}✓${NC} Server: Running (PID: $(cat $SERVER_PID))"
    else
        echo -e "${RED}✗${NC} Server: Not running"
    fi
    
    if is_running "$NGROK_PID"; then
        echo -e "${GREEN}✓${NC} Ngrok: Running (PID: $(cat $NGROK_PID))"
        
        # Try to get URL
        PUBLIC_URL=$(get_ngrok_url)
        if [ -n "$PUBLIC_URL" ]; then
            echo ""
            echo "Public URL: $PUBLIC_URL/forex_macd_dashboard.html"
        fi
    else
        echo -e "${RED}✗${NC} Ngrok: Not running"
    fi
    
    echo ""
    echo "Local URL: http://localhost:$PORT/forex_macd_dashboard.html"
}

show_url() {
    if ! is_running "$NGROK_PID"; then
        error "Ngrok is not running. Start services first with: $0 start"
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
        error "Could not retrieve ngrok URL. Check if ngrok is running properly."
        echo "View ngrok logs: tail -f $NGROK_LOG"
        exit 1
    fi
}

case "${1:-start}" in
    start)
        if is_running "$STRATEGY_PID" || is_running "$SERVER_PID" || is_running "$NGROK_PID"; then
            warn "Services already running. Use 'restart' to restart."
            show_status
            exit 1
        fi
        start_processes
        ;;
    stop)
        stop_processes
        ;;
    restart)
        stop_processes
        sleep 2
        start_processes
        ;;
    status)
        show_status
        ;;
    url)
        show_url
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|url}"
        echo ""
        echo "Commands:"
        echo "  start   - Start all services (strategy, server, ngrok)"
        echo "  stop    - Stop all services"
        echo "  restart - Restart all services"
        echo "  status  - Show service status"
        echo "  url     - Display public internet URL"
        exit 1
        ;;
esac

#!/bin/bash
# Forex MACD Dashboard Startup Script
# This script starts both the strategy and server processes

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Configuration
VENV_PATH="$SCRIPT_DIR/../.venv"
STRATEGY_SCRIPT="$SCRIPT_DIR/forex_macd_strategy.py"
SERVER_SCRIPT="$SCRIPT_DIR/serve_forex_macd.py"
LOG_DIR="$SCRIPT_DIR/logs"
STRATEGY_LOG="$LOG_DIR/strategy.log"
SERVER_LOG="$LOG_DIR/server.log"
PID_DIR="$SCRIPT_DIR/pids"
STRATEGY_PID="$PID_DIR/strategy.pid"
SERVER_PID="$PID_DIR/server.pid"

# Create directories if they don't exist
mkdir -p "$LOG_DIR"
mkdir -p "$PID_DIR"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check if process is running
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

# Function to stop processes
stop_processes() {
    log "Stopping Forex MACD services..."
    
    if is_running "$STRATEGY_PID"; then
        local pid=$(cat "$STRATEGY_PID")
        log "Stopping strategy process (PID: $pid)..."
        kill "$pid" 2>/dev/null || true
        rm -f "$STRATEGY_PID"
    fi
    
    if is_running "$SERVER_PID"; then
        local pid=$(cat "$SERVER_PID")
        log "Stopping server process (PID: $pid)..."
        kill "$pid" 2>/dev/null || true
        rm -f "$SERVER_PID"
    fi
    
    log "Services stopped"
}

# Function to start processes
start_processes() {
    log "Starting Forex MACD services..."
    
    # Activate virtual environment
    if [ -d "$VENV_PATH" ]; then
        log "Activating virtual environment..."
        source "$VENV_PATH/bin/activate"
    else
        log "WARNING: Virtual environment not found at $VENV_PATH"
    fi
    
    # Start strategy script
    log "Starting strategy script..."
    nohup python3 "$STRATEGY_SCRIPT" >> "$STRATEGY_LOG" 2>&1 &
    echo $! > "$STRATEGY_PID"
    log "Strategy started (PID: $(cat $STRATEGY_PID))"
    
    # Wait a moment for strategy to initialize
    sleep 2
    
    # Start server
    log "Starting web server..."
    nohup python3 "$SERVER_SCRIPT" >> "$SERVER_LOG" 2>&1 &
    echo $! > "$SERVER_PID"
    log "Server started (PID: $(cat $SERVER_PID))"
    
    log "✓ All services started successfully"
    log "✓ Dashboard available at: http://localhost:8003/forex_macd_dashboard.html"
    log "✓ Strategy log: $STRATEGY_LOG"
    log "✓ Server log: $SERVER_LOG"
}

# Function to show status
show_status() {
    echo "Forex MACD Service Status:"
    echo "=========================="
    
    if is_running "$STRATEGY_PID"; then
        echo "✓ Strategy: Running (PID: $(cat $STRATEGY_PID))"
    else
        echo "✗ Strategy: Not running"
    fi
    
    if is_running "$SERVER_PID"; then
        echo "✓ Server: Running (PID: $(cat $SERVER_PID))"
    else
        echo "✗ Server: Not running"
    fi
    
    echo ""
    echo "Log files:"
    echo "  Strategy: $STRATEGY_LOG"
    echo "  Server: $SERVER_LOG"
}

# Main script logic
case "${1:-start}" in
    start)
        if is_running "$STRATEGY_PID" || is_running "$SERVER_PID"; then
            log "Services already running. Use 'restart' to restart."
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
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac

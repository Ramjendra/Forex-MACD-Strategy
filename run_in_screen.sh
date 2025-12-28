#!/bin/bash
# Run Forex MACD Dashboard in Screen Session
# This is an alternative to systemd for simpler background execution

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

SESSION_NAME="forex-macd"
VENV_PATH="$SCRIPT_DIR/../.venv"

# Check if screen is installed
if ! command -v screen &> /dev/null; then
    echo "Error: 'screen' is not installed."
    echo "Install it with: sudo apt-get install screen"
    exit 1
fi

# Function to check if session exists
session_exists() {
    screen -list | grep -q "$SESSION_NAME"
}

case "${1:-start}" in
    start)
        if session_exists; then
            echo "Session '$SESSION_NAME' already exists."
            echo "Use '$0 attach' to view it or '$0 stop' to stop it."
            exit 1
        fi
        
        echo "Starting Forex MACD Dashboard in screen session..."
        
        # Create a new detached screen session
        screen -dmS "$SESSION_NAME" bash -c "
            cd '$SCRIPT_DIR'
            
            # Activate virtual environment if it exists
            if [ -d '$VENV_PATH' ]; then
                source '$VENV_PATH/bin/activate'
            fi
            
            # Start strategy in background
            echo 'Starting strategy script...'
            python3 forex_macd_strategy.py &
            STRATEGY_PID=\$!
            
            # Wait for strategy to initialize
            sleep 3
            
            # Start server
            echo 'Starting web server...'
            python3 serve_forex_macd.py
            
            # If server exits, kill strategy too
            kill \$STRATEGY_PID 2>/dev/null || true
        "
        
        echo "✓ Session started successfully!"
        echo "✓ Dashboard available at: http://localhost:8003/forex_macd_dashboard.html"
        echo ""
        echo "Commands:"
        echo "  View session:   $0 attach"
        echo "  Stop session:   $0 stop"
        echo "  Check status:   $0 status"
        ;;
        
    stop)
        if ! session_exists; then
            echo "Session '$SESSION_NAME' is not running."
            exit 1
        fi
        
        echo "Stopping session '$SESSION_NAME'..."
        screen -S "$SESSION_NAME" -X quit
        echo "✓ Session stopped"
        ;;
        
    attach)
        if ! session_exists; then
            echo "Session '$SESSION_NAME' is not running."
            echo "Start it with: $0 start"
            exit 1
        fi
        
        echo "Attaching to session '$SESSION_NAME'..."
        echo "Press Ctrl+A then D to detach without stopping the session"
        sleep 2
        screen -r "$SESSION_NAME"
        ;;
        
    status)
        if session_exists; then
            echo "✓ Session '$SESSION_NAME' is running"
            echo ""
            screen -list | grep "$SESSION_NAME"
            echo ""
            echo "Dashboard should be available at: http://localhost:8003/forex_macd_dashboard.html"
        else
            echo "✗ Session '$SESSION_NAME' is not running"
        fi
        ;;
        
    *)
        echo "Usage: $0 {start|stop|attach|status}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the dashboard in a detached screen session"
        echo "  stop    - Stop the screen session"
        echo "  attach  - Attach to the running session (Ctrl+A D to detach)"
        echo "  status  - Check if the session is running"
        exit 1
        ;;
esac

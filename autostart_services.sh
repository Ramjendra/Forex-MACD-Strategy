#!/bin/bash
# Auto-start caffeine and services on login

# Start caffeine to prevent sleep/hibernation
caffeine &

# Wait a moment
sleep 2

# Start Forex MACD services
cd /home/ramram/Desktop/SELF_LEARNING/Medical\ RAG/documents/Signal/Forex_MACD_Strategy

# Start strategy
nohup python3 forex_macd_strategy.py >> logs/strategy.log 2>&1 &
sleep 2

# Start server
nohup python3 serve_forex_macd.py >> logs/server.log 2>&1 &
sleep 2

# Start ngrok (if not already running)
if ! pgrep -f "ngrok http 8003" > /dev/null; then
    cd ..
    nohup ./ngrok http 8003 --log=stdout > /dev/null 2>&1 &
fi

echo "✅ All services started!"
echo "🌐 Dashboard: https://1b0afc0da283.ngrok-free.app/forex_macd_dashboard.html"

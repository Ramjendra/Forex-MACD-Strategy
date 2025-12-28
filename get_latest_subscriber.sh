#!/bin/bash
# Quick script to get the latest person who messaged the bot

echo "🔍 Checking for new subscribers..."
echo ""

curl -s "https://api.telegram.org/bot8574181955:AAE7OTQct0ZuCOsodaMj1npU09eywZrPDAQ/getUpdates" | jq -r '.result[-1].message.chat | "✅ Latest User:\n   Chat ID: \(.id)\n   Name: \(.first_name)\n   Username: @\(.username // "none")\n   Type: \(.type)"'

echo ""
echo "📋 Copy the Chat ID above and tell me what signals they want!"

#!/bin/bash

# Quick Telegram Setup Script
# This will configure your Hugging Face Space with Telegram credentials

echo "🚀 Configuring Telegram Alerts for Hugging Face..."
echo ""
echo "Bot Name: BiasBuster Trading Alert"
echo "Bot Username: @bias_buster_trading_bot"
echo "Chat ID: 5105712105"
echo ""

# Navigate to HF deployment
cd /home/ramram/Desktop/SELF_LEARNING/Medical\ RAG/documents/Signal/hf_deployment

echo "📝 Instructions to complete setup:"
echo ""
echo "STEP 1: Have the recipient (Chat ID: 5105712105) do this:"
echo "  1. Open Telegram"
echo "  2. Search for: @bias_buster_trading_bot"
echo "  3. Click 'START' or send any message"
echo "  (This activates the chat so bot can send messages)"
echo ""
echo "STEP 2: Add Secrets to Hugging Face Space:"
echo "  1. Go to: https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE"
echo "  2. Click: Settings → Variables and secrets"
echo "  3. Add these as SECRETS (not variables):"
echo ""
echo "     Name: TELEGRAM_BOT_TOKEN"
echo "     Value: 8574181955:AAE7OTQct0ZuCOsodaMj1npU09eywZrPDAQ"
echo ""
echo "     Name: TELEGRAM_CHAT_ID"
echo "     Value: 5105712105"
echo ""
echo "     Name: TELEGRAM_CATEGORIES"
echo "     Value: 5105712105:NSE Live"
echo ""
echo "STEP 3: Deploy to Hugging Face:"
echo "  Run these commands:"
echo "  cd /home/ramram/Desktop/SELF_LEARNING/Medical\ RAG/documents/Signal/hf_deployment"
echo "  git add ."
echo "  git commit -m 'Add Telegram alerts for NSE Live'"
echo "  git push"
echo ""
echo "✅ After deployment, check HF logs for: '✅ Telegram alerts enabled'"
echo ""

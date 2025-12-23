#!/bin/bash
# Script to sync local Forex MACD Strategy changes to hf_deployment directory

SOURCE_DIR="/home/ramram/Desktop/SELF_LEARNING/Medical RAG/documents/Signal/Forex_MACD_Strategy"
DEST_DIR="/home/ramram/Desktop/SELF_LEARNING/Medical RAG/documents/Signal/hf_deployment"

echo "🔄 Syncing local changes to hf_deployment..."

cp "$SOURCE_DIR/forex_macd_strategy.py" "$DEST_DIR/"
cp "$SOURCE_DIR/forex_macd_dashboard.html" "$DEST_DIR/"
cp "$SOURCE_DIR/forex_macd_signals.json" "$DEST_DIR/"
cp "$SOURCE_DIR/signal_history.json" "$DEST_DIR/"
cp "$SOURCE_DIR/serve_forex_macd.py" "$DEST_DIR/"
cp "$SOURCE_DIR/active_signals.json" "$DEST_DIR/"
cp "$SOURCE_DIR/inject_all_mock_data.py" "$DEST_DIR/"

echo "✅ Sync complete!"
echo "🚀 You can now run 'bash deploy.sh' in $DEST_DIR to push to Hugging Face."

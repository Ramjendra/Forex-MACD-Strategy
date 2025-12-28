#!/bin/bash
# Quick Start Script for Feedback System

echo "======================================"
echo "📧 Feedback System Setup"
echo "======================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found!"
    echo "📝 Creating .env from template..."
    cp .env.template .env
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your email credentials:"
    echo "   1. EMAIL_ADDRESS=your.email@gmail.com"
    echo "   2. EMAIL_PASSWORD=your_app_password"
    echo ""
    echo "📖 See EMAIL_FEEDBACK_SETUP.md for detailed instructions"
    exit 1
fi

# Check if email is configured
if ! grep -q "EMAIL_ADDRESS=.*@" .env; then
    echo "⚠️  EMAIL_ADDRESS not configured in .env"
    echo "📖 See EMAIL_FEEDBACK_SETUP.md for setup instructions"
    exit 1
fi

if ! grep -q "EMAIL_PASSWORD=..*" .env; then
    echo "⚠️  EMAIL_PASSWORD not configured in .env"
    echo "📖 See EMAIL_FEEDBACK_SETUP.md for setup instructions"
    exit 1
fi

echo "✅ Email configuration found"
echo ""

# Install dependencies
echo "📦 Checking dependencies..."
pip3 install -q flask flask-cors python-dotenv 2>/dev/null
echo "✅ Dependencies installed"
echo ""

# Test email system
echo "🧪 Testing email system..."
python3 feedback_collector.py
echo ""

# Ask if user wants to start the API server
read -p "🚀 Start feedback API server? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🌐 Starting feedback API on http://localhost:5001..."
    echo "📧 Feedback will be sent to: biasbuster2026@gmail.com"
    echo ""
    echo "💡 Access feedback form at: http://localhost:5001/feedback.html"
    echo "   Or add a link to your dashboard"
    echo ""
    nohup python3 feedback_api.py > feedback_api.log 2>&1 &
    echo "✅ Feedback API started (PID: $!)"
    echo "📄 Logs: tail -f feedback_api.log"
else
    echo "ℹ️  To start manually: python3 feedback_api.py"
fi

echo ""
echo "======================================"
echo "✅ Setup Complete!"
echo "======================================"

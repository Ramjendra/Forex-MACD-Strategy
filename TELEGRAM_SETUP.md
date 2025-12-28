# 📱 Telegram Alert Setup Guide

## Quick Answer: How to Get Friend's Chat ID

**3 Simple Steps:**

1. **Run the helper script:**
   ```bash
   cd /home/ramram/Desktop/SELF_LEARNING/Medical\ RAG/documents/Signal/Forex_MACD_Strategy
   python3 get_chat_id.py
   ```

2. **Ask your friend to:**
   - Open Telegram
   - Search for your bot (the script will show the bot username)
   - Click "START" or send any message

3. **Copy the Chat ID** that appears in the terminal

---

## Complete Setup Process

### Step 1: Create Telegram Bot (If You Don't Have One)

1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Follow instructions to name your bot
4. **Copy the Bot Token** (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Set Up Environment Variables Locally

Create a `.env` file in the Forex_MACD_Strategy directory:

```bash
cd /home/ramram/Desktop/SELF_LEARNING/Medical\ RAG/documents/Signal/Forex_MACD_Strategy
nano .env
```

Add this content:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_friends_chat_id_here
TELEGRAM_CATEGORIES=your_friends_chat_id:NSE Live
```

### Step 3: Get Friend's Chat ID

Run the helper script:
```bash
python3 get_chat_id.py
```

The script will:
- Connect to your bot
- Show your bot's username
- Wait for messages
- Display the Chat ID when your friend messages the bot

**Ask your friend to:**
1. Search for your bot in Telegram (e.g., `@YourBotName`)
2. Click "START" or send "Hello"
3. Wait for confirmation message

**You'll see output like:**
```
🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉
✅ NEW CHAT ID FOUND!
🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉

👤 Name: John Doe
📝 Username: @johndoe
💬 Message: Hello

🔑 CHAT ID: 123456789
```

### Step 4: Test Locally (Optional but Recommended)

```bash
# Test the connection
python3 test_telegram.py

# Or test with the alerts module
python3 -c "from telegram_alerts import test_telegram_alerts; test_telegram_alerts()"
```

### Step 5: Configure Hugging Face Secrets

1. Go to your HF Space: https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE
2. Click **Settings** → **Variables and secrets**
3. Add these secrets:

| Name | Value | Example |
|------|-------|---------|
| `TELEGRAM_BOT_TOKEN` | Your bot token | `1234567890:ABCdefGHI...` |
| `TELEGRAM_CHAT_ID` | Friend's Chat ID | `123456789` |
| `TELEGRAM_CATEGORIES` | Category filter | `123456789:NSE Live` |

**Important:** Use "Secrets" not "Variables" to keep the bot token private!

### Step 6: Deploy to Hugging Face

```bash
cd /home/ramram/Desktop/SELF_LEARNING/Medical\ RAG/documents/Signal/Forex_MACD_Strategy
./sync_to_hf.sh
```

Or manually:
```bash
cd /home/ramram/Desktop/SELF_LEARNING/Medical\ RAG/documents/Signal/hf_deployment
git add .
git commit -m "Add Telegram alerts for NSE Live signals"
git push
```

---

## Category Filtering Explained

The `TELEGRAM_CATEGORIES` variable controls which signals your friend receives:

**Format:** `{chat_id}:{category1},{category2}`

**Examples:**

```bash
# Only NSE Live signals
TELEGRAM_CATEGORIES=123456789:NSE Live

# Multiple categories
TELEGRAM_CATEGORIES=123456789:NSE Live,Forex

# Multiple friends with different preferences
TELEGRAM_CATEGORIES=123456789:NSE Live;987654321:Forex,Crypto

# Send everything
TELEGRAM_CATEGORIES=123456789:ALL
```

**Available Categories:**
- `NSE Live` - Nifty Future & Bank Nifty Future
- `Forex` - Forex pairs (EUR/USD, GBP/USD, etc.)
- `Crypto` - Bitcoin, Ethereum
- `Indian Stocks` - Nifty 50 stocks
- `Indian Commodities` - MCX Gold, Silver, Crude Oil, etc.
- `ALL` - All signals

---

## Troubleshooting

### "Bot token not found"
- Make sure `.env` file exists in the correct directory
- Check that `TELEGRAM_BOT_TOKEN` is set correctly (no spaces)

### "Failed to connect to bot"
- Verify bot token is correct
- Check internet connection
- Make sure bot wasn't deleted in BotFather

### "Friend doesn't receive messages"
- Verify Chat ID is correct (numeric, no quotes)
- Make sure friend clicked "START" in the bot
- Check HF Space logs for errors
- Verify HF Secrets are set correctly

### "Receiving all signals, not just NSE Live"
- Check `TELEGRAM_CATEGORIES` format
- Make sure Chat ID matches exactly
- Category name is case-sensitive: use `NSE Live` not `nse live`

---

## Testing the Setup

### Test 1: Local Test
```bash
python3 test_telegram.py
```

### Test 2: Send Test Alert
```bash
python3 -c "
from telegram_alerts import TelegramAlerts
alerts = TelegramAlerts()
alerts.send_test_alert(category='NSE Live')
"
```

### Test 3: Check HF Logs
1. Go to HF Space
2. Click "Logs" tab
3. Look for: `📱 Telegram alerts configured for X recipient(s)`

---

## What Alerts Will Friend Receive?

Your friend will get notifications for:

✅ **New NSE Live Signals**
- Nifty Future BUY/SELL
- Bank Nifty Future BUY/SELL
- Entry price, Stop Loss, 3 Take Profit levels

✅ **Trade Updates**
- TP1, TP2, TP3 hit notifications
- Stop Loss hit alerts
- Trailing Stop Loss updates

✅ **Re-entry Opportunities**
- When price retraces to good entry levels
- Fibonacci-based re-entry signals

---

## Next Steps

1. ✅ Run `get_chat_id.py` to get friend's Chat ID
2. ✅ Update `.env` file locally (for testing)
3. ✅ Test alerts locally
4. ✅ Add secrets to Hugging Face
5. ✅ Deploy to HF
6. ✅ Verify friend receives alerts

**Need help?** Check the logs or run the test scripts!

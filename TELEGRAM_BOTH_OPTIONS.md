# Telegram Alerts - Two Setup Options

You have **TWO ways** to send alerts to users. Choose the one that works best for you!

---

## 🎯 Quick Comparison

| Feature | **OPTION 1: Automated** | **OPTION 2: Manual** |
|---------|------------------------|---------------------|
| **User Setup** | Just send /start to bot | Need to get Chat ID |
| **Ease for Users** | ⭐⭐⭐⭐⭐ Very Easy | ⭐⭐ Moderate |
| **Category Selection** | Users choose via bot | You configure manually |
| **Multiple Users** | Unlimited, auto-managed | Manual list in .env |
| **Best For** | Public service, many users | Private, few trusted users |

---

## ✨ OPTION 1: Automated Subscriber System (RECOMMENDED)

**Perfect for:** Multiple users, public service, easy onboarding

### How It Works
1. Users send `/start` to your bot
2. Bot automatically registers them
3. Users choose categories via bot commands
4. System manages everything automatically

### Setup Steps

#### 1. Start the Subscriber Manager

```bash
cd /home/ramram/Desktop/SELF_LEARNING/Medical\ RAG/documents/Signal/Forex_MACD_Strategy
python3 telegram_subscriber.py
```

This will run in the background and listen for new subscribers.

#### 2. Tell Users to Subscribe

Send them this message:
```
🤖 Get NSE Live trading alerts!

1. Open Telegram
2. Search for: @bias_buster_trading_bot
3. Send /start

You'll get instant alerts for Nifty & Bank Nifty Future signals!
```

#### 3. Users Can Manage Their Subscription

**Available Commands:**
- `/start` - Subscribe to NSE Live (default)
- `/status` - Check subscription status
- `/categories` - Change alert categories
- `/stop` - Unsubscribe

**Category Selection:**
Users reply with numbers:
- `1` = NSE Live only
- `2` = Forex only
- `1,2` = NSE Live + Forex
- `6` = ALL categories

#### 4. Deploy to Hugging Face

The system automatically reads from `telegram_subscribers.json`:

```bash
cd /home/ramram/Desktop/SELF_LEARNING/Medical\ RAG/documents/Signal/hf_deployment

# Copy the subscriber manager
cp ../Forex_MACD_Strategy/telegram_subscriber.py .
cp ../Forex_MACD_Strategy/telegram_subscribers.json .

# Deploy
git add .
git commit -m "Add automated Telegram subscriber system"
git push
```

**HF Secrets Needed:**
- `TELEGRAM_BOT_TOKEN` = `8574181955:AAE7OTQct0ZuCOsodaMj1npU09eywZrPDAQ`

That's it! No need for `TELEGRAM_CHAT_ID` or `TELEGRAM_CATEGORIES`.

---

## 🔧 OPTION 2: Manual Chat ID Configuration

**Perfect for:** Few trusted users, private setup, full control

### How It Works
1. You get each user's Chat ID manually
2. You configure them in HF Secrets
3. You control who gets what categories

### Setup Steps

#### 1. Get User's Chat ID

**Method A: Use the helper script**
```bash
cd /home/ramram/Desktop/SELF_LEARNING/Medical\ RAG/documents/Signal/Forex_MACD_Strategy
python3 get_chat_id.py
```

Ask user to send any message to `@bias_buster_trading_bot`. The script will show their Chat ID.

**Method B: Direct from Telegram**
1. User messages the bot
2. Check bot updates: `https://api.telegram.org/bot8574181955:AAE7OTQct0ZuCOsodaMj1npU09eywZrPDAQ/getUpdates`
3. Find `"chat":{"id":123456789}` in the response

#### 2. Configure .env (Local Testing)

Create `/home/ramram/Desktop/SELF_LEARNING/Medical RAG/documents/Signal/Forex_MACD_Strategy/.env`:

```bash
TELEGRAM_BOT_TOKEN=8574181955:AAE7OTQct0ZuCOsodaMj1npU09eywZrPDAQ

# Single user
TELEGRAM_CHAT_ID=5105712105
TELEGRAM_CATEGORIES=5105712105:NSE Live

# Multiple users
# TELEGRAM_CHAT_ID=5105712105,987654321,123456789
# TELEGRAM_CATEGORIES=5105712105:NSE Live;987654321:Forex;123456789:ALL
```

#### 3. Test Locally

```bash
python3 -c "from telegram_alerts import test_telegram_alerts; test_telegram_alerts()"
```

#### 4. Configure Hugging Face Secrets

Go to HF Space → Settings → Variables and secrets

Add these **SECRETS**:

```
Name: TELEGRAM_BOT_TOKEN
Value: 8574181955:AAE7OTQct0ZuCOsodaMj1npU09eywZrPDAQ

Name: TELEGRAM_CHAT_ID
Value: 5105712105

Name: TELEGRAM_CATEGORIES
Value: 5105712105:NSE Live
```

**For multiple users:**
```
Name: TELEGRAM_CHAT_ID
Value: 5105712105,987654321,123456789

Name: TELEGRAM_CATEGORIES
Value: 5105712105:NSE Live;987654321:Forex,Crypto;123456789:ALL
```

#### 5. Deploy

```bash
cd /home/ramram/Desktop/SELF_LEARNING/Medical\ RAG/documents/Signal/hf_deployment
git add .
git commit -m "Add Telegram alerts"
git push
```

---

## 🔄 Can I Use Both Options Together?

**Yes!** The system automatically prioritizes:
1. **First**: Checks for `telegram_subscribers.json` (automated)
2. **Fallback**: Uses `TELEGRAM_CHAT_ID` from .env (manual)

This means:
- If you have subscribers in the JSON file, it uses those
- If JSON file is empty/missing, it falls back to manual configuration
- You can migrate from manual to automated anytime

---

## 📋 Category Names Reference

Use these exact names (case-sensitive):

- `NSE Live` - Nifty Future & Bank Nifty Future
- `Forex` - All forex pairs
- `Crypto` - Bitcoin, Ethereum, etc.
- `Indian Stocks` - Nifty 50 stocks
- `Indian Indices & Commodities` - Nifty 50, Sensex, MCX commodities
- `Metals/Energy` - Gold, Silver, Oil, etc.
- `Crypto Scalping` - Crypto scalping signals
- `ALL` - Everything

---

## 🧪 Testing Both Options

### Test Automated System
```bash
# Start subscriber manager
python3 telegram_subscriber.py

# In another terminal, send test
python3 -c "from telegram_alerts import test_telegram_alerts; test_telegram_alerts()"
```

### Test Manual System
```bash
# Make sure .env has TELEGRAM_CHAT_ID
python3 -c "from telegram_alerts import test_telegram_alerts; test_telegram_alerts()"
```

---

## 🚀 Recommended Setup

**For Your Current Situation:**

Since you have Chat ID `5105712105`, I recommend:

### Quick Start (Manual - 2 minutes)
1. Add secrets to HF (shown above in Option 2)
2. Deploy
3. Done!

### Long-term (Automated - 5 minutes setup, unlimited users)
1. Run `python3 telegram_subscriber.py` locally
2. Have user send `/start` to bot
3. Copy `telegram_subscribers.json` to HF deployment
4. Deploy
5. Users can self-subscribe anytime!

---

## 💡 Pro Tips

1. **Start with Manual** for your first user (fastest)
2. **Switch to Automated** when you get more users
3. **Keep both** - automated for new users, manual for VIPs
4. **Run subscriber manager** in a screen session for 24/7 operation:
   ```bash
   screen -S telegram_bot
   python3 telegram_subscriber.py
   # Press Ctrl+A, then D to detach
   ```

---

## ❓ FAQ

**Q: Which option should I use?**
A: Manual for 1-5 users, Automated for 5+ users or public service.

**Q: Can users change categories themselves?**
A: Only with Option 1 (Automated). Option 2 requires you to update HF Secrets.

**Q: What if subscriber file gets deleted?**
A: System falls back to manual TELEGRAM_CHAT_ID automatically.

**Q: How do I migrate from manual to automated?**
A: Just start running `telegram_subscriber.py` and have users send `/start`. Old manual users keep working.

**Q: Can I remove someone from alerts?**
A: Option 1: User sends `/stop`. Option 2: Remove from TELEGRAM_CHAT_ID.

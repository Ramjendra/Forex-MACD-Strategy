# 📧 Feedback System - Complete Setup Guide

## ✅ What's Been Created

I've set up a complete feedback collection system that sends emails to **biasbuster2026@gmail.com**:

### Files Created:
1. **`feedback_collector.py`** - Email sending logic with beautiful HTML templates
2. **`feedback_api.py`** - Flask API server to handle form submissions
3. **`feedback.html`** - Beautiful feedback form page
4. **`EMAIL_FEEDBACK_SETUP.md`** - Detailed setup instructions
5. **`.env.template`** - Configuration template
6. **`setup_feedback.sh`** - Quick setup script

## 🚀 Quick Start (3 Steps)

### Step 1: Add Your Email Credentials

Edit the `.env` file and add your Gmail credentials:

```bash
nano .env
```

Add these lines (they're already in the file, just fill them in):
```bash
EMAIL_ADDRESS=your.email@gmail.com
EMAIL_PASSWORD=your_16_char_app_password
```

**How to get Gmail App Password:**
1. Go to https://myaccount.google.com/apppasswords
2. Create an app password for "Mail" → "Other (Trading Dashboard)"
3. Copy the 16-character password (no spaces)
4. Paste it as `EMAIL_PASSWORD` in .env

### Step 2: Test the System

```bash
python3 feedback_collector.py
```

This will send a test email to `biasbuster2026@gmail.com`

### Step 3: Start the Feedback API

```bash
python3 feedback_api.py
```

Or run in background:
```bash
nohup python3 feedback_api.py > feedback_api.log 2>&1 &
```

## 📱 How It Works

### User Flow:
1. User clicks **"📧 Feedback"** button on dashboard
2. Opens beautiful feedback form at `feedback.html`
3. Fills out:
   - Name (required)
   - Email (optional)
   - Category (Bug Report, Feature Request, etc.)
   - Rating (1-5 stars)
   - Message (required)
4. Clicks **"Send Feedback"**
5. Email is instantly sent to `biasbuster2026@gmail.com`

### Email Features:
✅ **Beautiful HTML Format** - Professional, branded emails
✅ **Star Ratings** - Visual ⭐⭐⭐⭐⭐ display
✅ **Category Tags** - Organized by feedback type
✅ **Reply-To** - Easy to respond to users
✅ **Local Backup** - Saved in `feedback_log.json`

## 📊 Feedback Categories

- 🐛 **Bug Report** - Report issues
- 💡 **Feature Request** - Suggest improvements
- ⚡ **Performance** - Speed/performance issues
- 🎨 **UI/UX** - Design feedback
- 📈 **Strategy** - Trading strategy feedback
- 💬 **General** - General comments
- 📝 **Other** - Anything else

## 🔧 Integration with Dashboard

To add a feedback button to your dashboard, add this HTML:

```html
<a href="feedback.html" class="feedback-btn" style="
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 15px 25px;
    border-radius: 50px;
    text-decoration: none;
    font-weight: 600;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    z-index: 1000;
">
    📧 Feedback
</a>
```

## 📧 Email Example

When a user submits feedback, you'll receive an email like this:

**Subject:** `📊 Trading Dashboard Feedback - Bug Report`

**Content:**
```
👤 User Information
Name: John Doe
Email: john@example.com
Category: Bug Report
Rating: ⭐⭐⭐⭐⭐
Timestamp: 2025-12-26 12:00:00 IST

💬 Feedback Message
"The TP2 alerts were not working, but now they are fixed! 
Great job on the update."
```

## 🛠️ Management

### Check if API is running:
```bash
ps aux | grep feedback_api
```

### View logs:
```bash
tail -f feedback_api.log
```

### Stop the API:
```bash
pkill -f feedback_api.py
```

### View feedback history:
```bash
cat feedback_log.json | python3 -m json.tool
```

## 📈 Features

### Current Features:
- ✅ Email notifications to biasbuster2026@gmail.com
- ✅ Beautiful HTML emails
- ✅ Star rating system (1-5)
- ✅ Category filtering
- ✅ Local backup storage
- ✅ Reply-To support
- ✅ Responsive design

### Potential Enhancements:
- 📊 Feedback analytics dashboard
- 📧 Auto-reply to users
- 🔔 Slack/Discord integration
- 📱 Mobile app integration
- 🤖 AI-powered feedback analysis

## 🔒 Security

- ✅ Uses Gmail App Passwords (not regular password)
- ✅ .env file not committed to git
- ✅ CORS enabled for API
- ✅ Input validation on forms
- ✅ Local backup of all feedback

## 📞 Support

If you need help:
1. Check `EMAIL_FEEDBACK_SETUP.md` for detailed instructions
2. Run test: `python3 feedback_collector.py`
3. Check logs: `tail -f feedback_api.log`
4. Verify .env configuration

## 🎉 You're All Set!

Once you add your email credentials to `.env`, the system is ready to collect feedback and send it to **biasbuster2026@gmail.com**!

---

**Created by:** Antigravity AI Assistant
**Date:** 2025-12-26
**Purpose:** Collect user feedback for Trading Dashboard improvements

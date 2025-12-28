# Email Configuration Guide

## Setup Instructions

### 1. Configure Email Settings

Add these lines to your `.env` file:

```bash
# Email Configuration for Feedback System
EMAIL_ADDRESS=your.email@gmail.com
EMAIL_PASSWORD=your_app_password_here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_RECIPIENTS=biasbuster2026@gmail.com
```

### 2. Get Gmail App Password

If using Gmail, you need to create an **App Password**:

1. Go to your Google Account: https://myaccount.google.com/
2. Select **Security**
3. Under "How you sign in to Google," select **2-Step Verification** (enable if not already)
4. At the bottom, select **App passwords**
5. Select app: **Mail**
6. Select device: **Other** (Custom name) → Enter "Trading Dashboard"
7. Click **Generate**
8. Copy the 16-character password (remove spaces)
9. Paste it in `.env` as `EMAIL_PASSWORD`

### 3. Start the Feedback API Server

```bash
python3 feedback_api.py
```

The server will run on `http://localhost:5001`

### 4. Test the System

```bash
python3 feedback_collector.py
```

This will send a test email to `biasbuster2026@gmail.com`

## Usage

### From the Dashboard

1. Users click the **"📧 Feedback"** button
2. Fill out the feedback form:
   - Name (required)
   - Email (optional)
   - Category (Bug Report, Feature Request, etc.)
   - Rating (1-5 stars)
   - Message (required)
3. Click **"Send Feedback"**
4. Email is automatically sent to `biasbuster2026@gmail.com`

### Feedback Categories

- 🐛 **Bug Report** - Report issues or bugs
- 💡 **Feature Request** - Suggest new features
- ⚡ **Performance** - Report performance issues
- 🎨 **UI/UX** - Design and usability feedback
- 📈 **Strategy** - Trading strategy feedback
- 💬 **General** - General comments
- 📝 **Other** - Anything else

## Email Format

Feedback emails are sent with:
- **Subject**: `📊 Trading Dashboard Feedback - [Category]`
- **To**: `biasbuster2026@gmail.com`
- **Reply-To**: User's email (if provided)
- **Format**: Beautiful HTML email with all feedback details

## Features

✅ **Beautiful HTML Emails** - Professional, easy-to-read format
✅ **Star Rating System** - Visual 1-5 star ratings
✅ **Category Filtering** - Organized feedback by type
✅ **Local Logging** - Backup storage in `feedback_log.json`
✅ **Reply-To Support** - Easy to respond to users
✅ **Responsive Design** - Works on all devices

## Troubleshooting

### Email Not Sending

1. **Check .env file**: Ensure `EMAIL_ADDRESS` and `EMAIL_PASSWORD` are set
2. **Verify App Password**: Make sure you're using an App Password, not your regular password
3. **Check 2-Step Verification**: Must be enabled for App Passwords
4. **Firewall**: Ensure port 587 is not blocked
5. **Gmail Settings**: Check if "Less secure app access" is needed (not recommended)

### API Not Working

1. **Check if server is running**: `ps aux | grep feedback_api`
2. **Check port 5001**: `netstat -tuln | grep 5001`
3. **Check logs**: Look for error messages in terminal
4. **CORS issues**: Make sure `flask-cors` is installed: `pip install flask-cors`

## Running in Production

### Using nohup

```bash
nohup python3 feedback_api.py > feedback_api.log 2>&1 &
```

### Using screen

```bash
screen -S feedback_api
python3 feedback_api.py
# Press Ctrl+A, then D to detach
```

### Check if running

```bash
ps aux | grep feedback_api
```

### Stop the server

```bash
pkill -f feedback_api.py
```

## File Structure

```
Forex_MACD_Strategy/
├── feedback_collector.py    # Email sending logic
├── feedback_api.py          # Flask API server
├── feedback.html            # Feedback form page
├── feedback_log.json        # Local feedback storage
└── .env                     # Email configuration
```

## Security Notes

⚠️ **Important**:
- Never commit `.env` file to git
- Use App Passwords, not regular passwords
- Keep `EMAIL_PASSWORD` secret
- Regularly rotate App Passwords
- Monitor `feedback_log.json` for spam

## Support

If you encounter issues:
1. Check the logs: `tail -f feedback_api.log`
2. Test email manually: `python3 feedback_collector.py`
3. Verify .env configuration
4. Check Gmail account security settings

#!/usr/bin/env python3
"""
Telegram Subscriber Manager
Automatically registers users who message the bot and allows them to subscribe to categories.
"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SUBSCRIBERS_FILE = Path(__file__).parent / "telegram_subscribers.json"

class SubscriberManager:
    def __init__(self):
        self.bot_token = BOT_TOKEN
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in .env")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.subscribers = self.load_subscribers()
    
    def load_subscribers(self):
        """Load subscribers from JSON file"""
        if SUBSCRIBERS_FILE.exists():
            with open(SUBSCRIBERS_FILE, 'r') as f:
                return json.load(f)
        return {}
    
    def save_subscribers(self):
        """Save subscribers to JSON file"""
        with open(SUBSCRIBERS_FILE, 'w') as f:
            json.dump(self.subscribers, f, indent=2)
    
    def get_updates(self, offset=None):
        """Get new messages from Telegram"""
        url = f"{self.base_url}/getUpdates"
        params = {"timeout": 30, "offset": offset}
        response = requests.get(url, params=params, timeout=35)
        return response.json()
    
    def send_message(self, chat_id, text):
        """Send a message to a chat"""
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    
    def subscribe_user(self, chat_id, name, username, categories=None):
        """Subscribe a user to categories"""
        if categories is None:
            categories = ["NSE Live"]  # Default to NSE Live
        
        chat_id_str = str(chat_id)
        self.subscribers[chat_id_str] = {
            "name": name,
            "username": username,
            "categories": categories,
            "active": True
        }
        self.save_subscribers()
        return True
    
    def unsubscribe_user(self, chat_id):
        """Unsubscribe a user"""
        chat_id_str = str(chat_id)
        if chat_id_str in self.subscribers:
            self.subscribers[chat_id_str]["active"] = False
            self.save_subscribers()
            return True
        return False
    
    def get_active_subscribers(self, category=None):
        """Get all active subscribers, optionally filtered by category"""
        active = {}
        for chat_id, data in self.subscribers.items():
            if data.get("active", True):
                if category is None or category in data.get("categories", []):
                    active[chat_id] = data
        return active
    
    def process_message(self, message):
        """Process incoming message and handle commands"""
        chat = message.get("chat", {})
        chat_id = chat.get("id")
        text = message.get("text", "").strip()
        
        first_name = chat.get("first_name", "")
        last_name = chat.get("last_name", "")
        username = chat.get("username", "")
        name = f"{first_name} {last_name}".strip() or username or "User"
        
        # Handle commands
        if text.startswith("/start"):
            # Auto-subscribe to NSE Live
            self.subscribe_user(chat_id, name, username, ["NSE Live"])
            response = f"""
✅ <b>Welcome to BiasBuster Trading Alerts!</b>

Hi {first_name}! You're now subscribed to <b>NSE Live</b> signals.

You'll receive alerts for:
• Nifty Future BUY/SELL signals
• Bank Nifty Future BUY/SELL signals
• TP/SL hit notifications
• Re-entry opportunities

<b>Commands:</b>
/status - Check your subscription
/categories - Change categories
/stop - Unsubscribe

<b>Your Chat ID:</b> {chat_id}
"""
            self.send_message(chat_id, response)
            return "subscribed"
        
        elif text.startswith("/status"):
            chat_id_str = str(chat_id)
            if chat_id_str in self.subscribers:
                sub = self.subscribers[chat_id_str]
                categories = ", ".join(sub.get("categories", []))
                status = "Active ✅" if sub.get("active", True) else "Inactive ❌"
                response = f"""
📊 <b>Your Subscription Status</b>

<b>Name:</b> {sub.get('name', 'Unknown')}
<b>Status:</b> {status}
<b>Categories:</b> {categories}
<b>Chat ID:</b> {chat_id}

Use /categories to change your subscriptions.
"""
            else:
                response = "You're not subscribed yet. Send /start to subscribe!"
            self.send_message(chat_id, response)
            return "status"
        
        elif text.startswith("/categories"):
            response = """
📋 <b>Available Categories:</b>

Reply with the number to subscribe:

1️⃣ NSE Live (Nifty & Bank Nifty Futures)
2️⃣ Forex (EUR/USD, GBP/USD, etc.)
3️⃣ Crypto (Bitcoin, Ethereum)
4️⃣ Indian Stocks (Nifty 50 stocks)
5️⃣ Commodities (Gold, Silver, Oil)
6️⃣ ALL (All signals)

Example: Reply "1" for NSE Live only
Or "1,2" for NSE Live + Forex
"""
            self.send_message(chat_id, response)
            return "categories_menu"
        
        elif text.startswith("/stop"):
            self.unsubscribe_user(chat_id)
            response = """
👋 <b>Unsubscribed</b>

You won't receive any more alerts.
Send /start anytime to resubscribe.
"""
            self.send_message(chat_id, response)
            return "unsubscribed"
        
        # Handle category selection (numbers)
        elif text.isdigit() or "," in text:
            category_map = {
                "1": "NSE Live",
                "2": "Forex",
                "3": "Crypto",
                "4": "Indian Stocks",
                "5": "Commodities",
                "6": "ALL"
            }
            
            selected = []
            for num in text.replace(" ", "").split(","):
                if num in category_map:
                    selected.append(category_map[num])
            
            if selected:
                self.subscribe_user(chat_id, name, username, selected)
                categories = ", ".join(selected)
                response = f"""
✅ <b>Subscription Updated!</b>

You'll now receive alerts for:
{categories}

Use /status to check your subscription anytime.
"""
                self.send_message(chat_id, response)
                return "updated"
        
        # Default response
        else:
            response = """
👋 Hi! I'm BiasBuster Trading Alert Bot.

<b>Commands:</b>
/start - Subscribe to alerts
/status - Check subscription
/categories - Change categories
/stop - Unsubscribe

Send /start to get started!
"""
            self.send_message(chat_id, response)
            return "help"
    
    def run_listener(self):
        """Run the bot listener to process messages"""
        print("🤖 Starting Telegram Subscriber Bot...")
        print(f"📱 Bot is listening for messages...")
        print(f"💾 Subscribers file: {SUBSCRIBERS_FILE}")
        print("\nPress Ctrl+C to stop\n")
        
        offset = None
        
        try:
            while True:
                result = self.get_updates(offset)
                
                if result.get("ok"):
                    updates = result.get("result", [])
                    
                    for update in updates:
                        offset = update["update_id"] + 1
                        
                        message = update.get("message", {})
                        if message:
                            chat = message.get("chat", {})
                            chat_id = chat.get("id")
                            name = chat.get("first_name", "User")
                            text = message.get("text", "")
                            
                            print(f"📨 Message from {name} ({chat_id}): {text}")
                            action = self.process_message(message)
                            print(f"✅ Action: {action}\n")
        
        except KeyboardInterrupt:
            print("\n\n👋 Stopped listening.")
            print(f"📊 Total subscribers: {len(self.get_active_subscribers())}")


if __name__ == "__main__":
    manager = SubscriberManager()
    manager.run_listener()

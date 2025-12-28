#!/usr/bin/env python3
"""
Telegram Alert System for Trading Signals
Sends instant notifications for new signals, TP hits, SL hits, and trade updates.
"""

import os
import requests
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

class TelegramAlerts:
    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in .env file")
        
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        # OPTION 1: Load from manual TELEGRAM_CHAT_ID (backward compatible)
        # OPTION 2: Load from telegram_subscribers.json (auto-managed)
        self.chat_ids = []
        self.category_preferences = {}
        
        # Try loading from subscribers file first (OPTION 2 - Automated)
        subscribers_file = Path(__file__).parent / "telegram_subscribers.json"
        if subscribers_file.exists():
            try:
                with open(subscribers_file, 'r') as f:
                    subscribers = json.load(f)
                    for chat_id, data in subscribers.items():
                        if data.get("active", True):
                            self.chat_ids.append(chat_id)
                            categories = data.get("categories", [])
                            if categories:
                                self.category_preferences[chat_id] = categories
                print(f"📱 Loaded {len(self.chat_ids)} subscribers from telegram_subscribers.json")
            except Exception as e:
                print(f"⚠️ Error loading subscribers file: {e}")
        
        # Fallback to manual TELEGRAM_CHAT_ID (OPTION 1 - Manual)
        if not self.chat_ids:
            chat_ids_str = TELEGRAM_CHAT_ID
            if not chat_ids_str:
                raise ValueError("No subscribers found. Either:\n"
                               "1. Run telegram_subscriber.py to auto-register users, OR\n"
                               "2. Set TELEGRAM_CHAT_ID in .env file")
            
            # Parse chat IDs (supports comma-separated list)
            self.chat_ids = [cid.strip() for cid in chat_ids_str.split(',')]
            
            # Load manual category preferences
            manual_prefs = self._load_manual_category_preferences()
            if manual_prefs:
                self.category_preferences.update(manual_prefs)
            
            print(f"📱 Telegram alerts configured for {len(self.chat_ids)} recipient(s) (manual)")
        
        if self.category_preferences:
            print(f"🎯 Category filtering enabled for {len(self.category_preferences)} client(s)")
    
    def _load_manual_category_preferences(self):
        """Load category preferences from TELEGRAM_CATEGORIES env variable"""
        categories_config = os.getenv("TELEGRAM_CATEGORIES", "")
        if not categories_config:
            return {}
        
        # Format: chat_id:category1,category2;chat_id2:category3
        # Example: 160134690:Forex,Crypto;987654321:Crypto
        preferences = {}
        try:
            for entry in categories_config.split(';'):
                if ':' in entry:
                    chat_id, categories = entry.split(':', 1)
                    chat_id = chat_id.strip()
                    cat_list = [c.strip() for c in categories.split(',')]
                    preferences[chat_id] = cat_list
        except Exception as e:
            print(f"⚠️ Error parsing TELEGRAM_CATEGORIES: {e}")
        
        return preferences
    
    def _should_send_to_client(self, chat_id, category):
        """Check if this client should receive alerts for this category"""
        # If no preferences set, send to everyone
        if not self.category_preferences:
            return True
        
        # If client has preferences, check if category matches
        if chat_id in self.category_preferences:
            client_categories = self.category_preferences[chat_id]
            # Special case: "ALL" means send everything
            if "ALL" in client_categories:
                return True
            return category in client_categories
        
        # If client not in preferences, send everything (default behavior)
        return True
    
    def send_message(self, message, parse_mode="HTML", category=None):
        """Send a text message to all configured Telegram chat IDs"""
        success_count = 0
        for chat_id in self.chat_ids:
            # Check category filter
            if category and not self._should_send_to_client(chat_id, category):
                continue
            
            try:
                url = f"{self.base_url}/sendMessage"
                payload = {
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": parse_mode
                }
                response = requests.post(url, json=payload, timeout=10)
                response.raise_for_status()
                success_count += 1
            except Exception as e:
                print(f"❌ Failed to send to chat {chat_id}: {e}")
        
        return success_count > 0
    
    def format_price(self, price, instrument):
        """Format price based on instrument type"""
        if price is None:
            return "---"
        if "JPY" in instrument:
            return f"{price:.3f}"
        elif any(x in instrument for x in ["Oil", "Gold", "Bitcoin", "Ethereum", "Nifty", "Sensex"]):
            return f"{price:,.2f}"
        elif "Silver" in instrument:
            return f"{price:.3f}"
        else:
            return f"{price:.5f}"
    
    def send_new_signal_alert(self, instrument, signal):
        """Send alert for new trading signal"""
        signal_type = signal['type']
        entry = signal['entry_price']
        sl = signal['sl']
        tp1 = signal.get('tp1', 0)
        tp2 = signal.get('tp2', 0)
        tp3 = signal.get('tp3', 0)
        category = signal.get('category', 'Unknown')
        
        # Calculate R:R ratio
        sl_dist = abs(entry - sl)
        tp1_dist = abs(entry - tp1)
        rr_ratio = tp1_dist / sl_dist if sl_dist > 0 else 0
        
        # Emoji based on signal type
        emoji = "🟢" if signal_type == "BUY" else "🔴"
        
        message = f"""
{emoji} <b>NEW {signal_type} SIGNAL</b>

<b>Instrument:</b> {instrument}
<b>Category:</b> {category}

<b>Entry:</b> {self.format_price(entry, instrument)}
<b>Stop Loss:</b> {self.format_price(sl, instrument)}

<b>Take Profits:</b>
  TP1 (1.5x): {self.format_price(tp1, instrument)}
  TP2 (3.0x): {self.format_price(tp2, instrument)}
  TP3 (5.0x): {self.format_price(tp3, instrument)}

<b>Risk:Reward:</b> 1:{rr_ratio:.1f}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}

💡 <i>Trade at your own risk. Always use proper risk management.</i>
"""
        return self.send_message(message.strip(), category=category)
    
    def send_tp_hit_alert(self, instrument, tp_level, signal, current_price):
        """Send alert when Take Profit is hit"""
        entry = signal['entry_price']
        signal_type = signal['type']
        
        # Calculate profit
        if signal_type == "BUY":
            profit = current_price - entry
        else:
            profit = entry - current_price
        
        profit_pct = (profit / entry) * 100 if entry > 0 else 0
        
        message = f"""
🎯 <b>TP{tp_level} HIT!</b>

<b>Instrument:</b> {instrument}
<b>Type:</b> {signal_type}

<b>Entry:</b> {self.format_price(entry, instrument)}
<b>Exit:</b> {self.format_price(current_price, instrument)}

<b>Profit:</b> {self.format_price(abs(profit), instrument)} ({profit_pct:+.2f}%)

<b>Status:</b> {"Trailing SL Active" if tp_level == 1 else f"TP{tp_level} reached"}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}

{"🛡️ Stop Loss moved to breakeven" if tp_level == 1 else ""}
"""
        return self.send_message(message.strip())
    
    def send_sl_hit_alert(self, instrument, signal, current_price, is_trailing=False):
        """Send alert when Stop Loss is hit"""
        entry = signal['entry_price']
        signal_type = signal['type']
        
        # Calculate loss
        if signal_type == "BUY":
            loss = entry - current_price
        else:
            loss = current_price - entry
        
        loss_pct = (loss / entry) * 100 if entry > 0 else 0
        
        sl_type = "Trailing SL" if is_trailing else "Stop Loss"
        
        message = f"""
🛑 <b>{sl_type.upper()} HIT</b>

<b>Instrument:</b> {instrument}
<b>Type:</b> {signal_type}

<b>Entry:</b> {self.format_price(entry, instrument)}
<b>Exit:</b> {self.format_price(current_price, instrument)}

<b>Loss:</b> {self.format_price(abs(loss), instrument)} ({loss_pct:.2f}%)

<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}

💭 <i>Every loss is a lesson. Review and improve!</i>
"""
        return self.send_message(message.strip())
    
    def send_reentry_alert(self, instrument, reentry_data, signal):
        """Send alert for re-entry opportunity"""
        strength = reentry_data.get('strength', 0)
        suggested_entry = reentry_data.get('suggested_entry', 0)
        fib_level = reentry_data.get('fib_level', '')
        reason = reentry_data.get('reason', '')
        rr = reentry_data.get('risk_reward', '1:1.5')
        
        # Strength emoji
        if strength >= 70:
            strength_emoji = "🟢"
        elif strength >= 50:
            strength_emoji = "🟡"
        else:
            strength_emoji = "🟠"
        
        message = f"""
🔄 <b>RE-ENTRY OPPORTUNITY</b>

<b>Instrument:</b> {instrument}
<b>Strength:</b> {strength_emoji} {strength}%

<b>Suggested Entry:</b> {self.format_price(suggested_entry, instrument)}
<b>Fibonacci Level:</b> {fib_level}
<b>Risk:Reward:</b> {rr}

<b>Reason:</b> {reason}

<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}

⚠️ <i>Re-entry opportunity detected. Confirm with your analysis.</i>
"""
        return self.send_message(message.strip())
    
    def send_test_alert(self, category=None):
        """Send a test message to verify bot is working"""
        message = """
✅ <b>Telegram Alerts Activated!</b>

Your trading signal alerts are now live.

You will receive notifications for:
  • New BUY/SELL signals
  • TP1, TP2, TP3 hits
  • Stop Loss hits
  • Re-entry opportunities

<b>Status:</b> All systems operational
<b>Time:</b> """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S IST') + """

🚀 <i>Happy Trading!</i>
"""
        return self.send_message(message.strip(), category=category)


# Standalone test function
def test_telegram_alerts():
    """Test the Telegram alerts system"""
    try:
        alerts = TelegramAlerts()
        print("📱 Testing Telegram connection...")
        
        if alerts.send_test_alert():
            print("✅ Test alert sent successfully!")
            print(f"✅ Check your Telegram (Chat ID: {TELEGRAM_CHAT_ID})")
            return True
        else:
            print("❌ Failed to send test alert")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    test_telegram_alerts()

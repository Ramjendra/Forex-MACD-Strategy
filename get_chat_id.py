#!/usr/bin/env python3
"""
Get Telegram Chat ID Helper Script

This script helps you find your friend's Telegram Chat ID.

INSTRUCTIONS:
1. Make sure you have a Telegram Bot Token (from @BotFather)
2. Set TELEGRAM_BOT_TOKEN in .env file or export it
3. Run this script: python3 get_chat_id.py
4. Ask your friend to send ANY message to your bot
5. The script will display their Chat ID
"""

import os
import requests
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    print("❌ Error: TELEGRAM_BOT_TOKEN not found!")
    print("\nPlease either:")
    print("1. Create a .env file with: TELEGRAM_BOT_TOKEN=your_token_here")
    print("2. Or export it: export TELEGRAM_BOT_TOKEN=your_token_here")
    print("\nTo get a bot token:")
    print("1. Open Telegram and search for @BotFather")
    print("2. Send /newbot and follow instructions")
    print("3. Copy the token you receive")
    exit(1)

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def get_bot_info():
    """Get bot information"""
    try:
        response = requests.get(f"{BASE_URL}/getMe", timeout=10)
        response.raise_for_status()
        bot_info = response.json()
        if bot_info.get("ok"):
            bot = bot_info["result"]
            return bot
        return None
    except Exception as e:
        print(f"❌ Error getting bot info: {e}")
        return None

def get_updates(offset=None):
    """Get new messages"""
    try:
        url = f"{BASE_URL}/getUpdates"
        params = {"timeout": 30, "offset": offset}
        response = requests.get(url, params=params, timeout=35)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error getting updates: {e}")
        return None

def main():
    print("=" * 60)
    print("📱 TELEGRAM CHAT ID FINDER")
    print("=" * 60)
    
    # Get bot info
    print("\n🤖 Checking bot connection...")
    bot = get_bot_info()
    
    if not bot:
        print("❌ Failed to connect to bot. Check your token!")
        return
    
    bot_username = bot.get("username", "Unknown")
    bot_name = bot.get("first_name", "Unknown")
    
    print(f"✅ Connected to bot: {bot_name} (@{bot_username})")
    print("\n" + "=" * 60)
    print("📋 INSTRUCTIONS FOR YOUR FRIEND:")
    print("=" * 60)
    print(f"\n1. Open Telegram")
    print(f"2. Search for: @{bot_username}")
    print(f"3. Click 'START' or send any message (like 'Hello')")
    print(f"\n⏳ Waiting for messages...")
    print("   (Press Ctrl+C to stop)\n")
    
    offset = None
    seen_chat_ids = set()
    
    try:
        while True:
            result = get_updates(offset)
            
            if result and result.get("ok"):
                updates = result.get("result", [])
                
                for update in updates:
                    # Update offset to mark as processed
                    offset = update["update_id"] + 1
                    
                    # Get message info
                    message = update.get("message", {})
                    if not message:
                        continue
                    
                    chat = message.get("chat", {})
                    chat_id = chat.get("id")
                    
                    if chat_id and chat_id not in seen_chat_ids:
                        seen_chat_ids.add(chat_id)
                        
                        # Get user info
                        first_name = chat.get("first_name", "Unknown")
                        last_name = chat.get("last_name", "")
                        username = chat.get("username", "")
                        message_text = message.get("text", "")
                        
                        print("\n" + "🎉" * 30)
                        print("✅ NEW CHAT ID FOUND!")
                        print("🎉" * 30)
                        print(f"\n👤 Name: {first_name} {last_name}".strip())
                        if username:
                            print(f"📝 Username: @{username}")
                        print(f"💬 Message: {message_text}")
                        print(f"\n🔑 CHAT ID: {chat_id}")
                        print("\n" + "=" * 60)
                        print("📋 COPY THIS CHAT ID:")
                        print("=" * 60)
                        print(f"\n{chat_id}\n")
                        print("=" * 60)
                        print("\n✅ Save this Chat ID for your Hugging Face setup!")
                        print("   You'll need to add it to HF Secrets as TELEGRAM_CHAT_ID")
                        print("\n💡 To send only NSE Live signals, also set:")
                        print(f"   TELEGRAM_CATEGORIES={chat_id}:NSE Live")
                        print("\n" + "=" * 60)
                        
                        # Send confirmation to user
                        try:
                            confirm_url = f"{BASE_URL}/sendMessage"
                            confirm_payload = {
                                "chat_id": chat_id,
                                "text": f"✅ Chat ID registered!\n\nYour Chat ID: {chat_id}\n\nYou will receive NSE Live trading signals here.",
                                "parse_mode": "HTML"
                            }
                            requests.post(confirm_url, json=confirm_payload, timeout=10)
                            print("✅ Confirmation sent to user")
                        except:
                            pass
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\n👋 Stopped listening for messages.")
        if seen_chat_ids:
            print(f"\n✅ Found {len(seen_chat_ids)} Chat ID(s):")
            for cid in seen_chat_ids:
                print(f"   • {cid}")
        else:
            print("\n⚠️  No messages received.")
            print("   Make sure your friend sent a message to the bot!")

if __name__ == "__main__":
    main()

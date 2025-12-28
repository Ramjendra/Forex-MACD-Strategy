#!/usr/bin/env python3
"""
Test Telegram Bot Connection
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print(f"Bot Token: {BOT_TOKEN}")
print(f"Chat ID: {CHAT_ID}")
print()

# Test 1: Get bot info
print("Test 1: Getting bot info...")
url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
response = requests.get(url)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
print()

# Test 2: Send simple message
print("Test 2: Sending test message...")
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": "Test message from Python"
}
response = requests.post(url, json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

#!/usr/bin/env python3
"""
Test Telegram Alert System
Sends test alerts for all event types to verify functionality
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from telegram_alerts import TelegramAlerts

def test_all_alerts():
    """Test all types of Telegram alerts"""
    
    print("=" * 60)
    print("TELEGRAM ALERT TEST")
    print("=" * 60)
    
    try:
        alerts = TelegramAlerts()
        print(f"✅ Telegram alerts initialized")
        print(f"📱 Sending to {len(alerts.chat_ids)} recipient(s)\n")
    except Exception as e:
        print(f"❌ Failed to initialize Telegram alerts: {e}")
        return False
    
    # Test 1: New Signal Alert
    print("1️⃣ Testing NEW SIGNAL alert...")
    test_signal = {
        "type": "BUY",
        "entry_price": 1.08500,
        "sl": 1.08200,
        "tp1": 1.08950,
        "tp2": 1.09650,
        "tp3": 1.10500,
        "category": "Forex"
    }
    try:
        alerts.send_new_signal_alert("EUR/USD (TEST)", test_signal)
        print("   ✅ New signal alert sent\n")
    except Exception as e:
        print(f"   ❌ Failed: {e}\n")
    
    # Test 2: TP1 Alert
    print("2️⃣ Testing TP1 alert...")
    try:
        alerts.send_tp_hit_alert("EUR/USD (TEST)", 1, test_signal, 1.08950)
        print("   ✅ TP1 alert sent\n")
    except Exception as e:
        print(f"   ❌ Failed: {e}\n")
    
    # Test 3: TP2 Alert (NEWLY FIXED)
    print("3️⃣ Testing TP2 alert (NEWLY FIXED)...")
    try:
        alerts.send_tp_hit_alert("EUR/USD (TEST)", 2, test_signal, 1.09650)
        print("   ✅ TP2 alert sent\n")
    except Exception as e:
        print(f"   ❌ Failed: {e}\n")
    
    # Test 4: TP3 Alert (NEWLY FIXED)
    print("4️⃣ Testing TP3 alert (NEWLY FIXED)...")
    try:
        alerts.send_tp_hit_alert("EUR/USD (TEST)", 3, test_signal, 1.10500)
        print("   ✅ TP3 alert sent\n")
    except Exception as e:
        print(f"   ❌ Failed: {e}\n")
    
    # Test 5: SL Hit Alert
    print("5️⃣ Testing SL HIT alert...")
    try:
        alerts.send_sl_hit_alert("EUR/USD (TEST)", test_signal, 1.08200, is_trailing=False)
        print("   ✅ SL hit alert sent\n")
    except Exception as e:
        print(f"   ❌ Failed: {e}\n")
    
    # Test 6: Trailing SL Hit Alert
    print("6️⃣ Testing TRAILING SL alert...")
    try:
        alerts.send_sl_hit_alert("EUR/USD (TEST)", test_signal, 1.08500, is_trailing=True)
        print("   ✅ Trailing SL alert sent\n")
    except Exception as e:
        print(f"   ❌ Failed: {e}\n")
    
    # Test 7: Re-entry Alert (NEWLY FIXED)
    print("7️⃣ Testing RE-ENTRY alert (NEWLY FIXED)...")
    test_reentry = {
        "type": "ADD_TO_BUY",
        "strength": 75,
        "reason": "Price at 61.8% Fib (25.5 pips pullback)",
        "suggested_entry": 1.08350,
        "fib_level": "61.8%",
        "risk_reward": "1:2.5"
    }
    try:
        alerts.send_reentry_alert("EUR/USD (TEST)", test_reentry, test_signal)
        print("   ✅ Re-entry alert sent\n")
    except Exception as e:
        print(f"   ❌ Failed: {e}\n")
    
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("\n📱 Check your Telegram for 7 test messages:")
    print("   1. New BUY Signal")
    print("   2. TP1 Hit")
    print("   3. TP2 Hit (NEWLY FIXED)")
    print("   4. TP3 Hit (NEWLY FIXED)")
    print("   5. Stop Loss Hit")
    print("   6. Trailing SL Hit")
    print("   7. Re-entry Opportunity (NEWLY FIXED)")
    print("\n⚠️  These are TEST alerts - ignore the EUR/USD (TEST) signals")
    
    return True

if __name__ == "__main__":
    test_all_alerts()

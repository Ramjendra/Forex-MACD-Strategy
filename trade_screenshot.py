import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Optional

def capture_trade_screenshot(res: Dict, event_type: str, output_path: str):
    """
    Generates a high-quality image of a trade closure card using Pillow.
    """
    # Card Dimensions (Smaller to fit 6 per page)
    width, height = 280, 450
    background_color = (18, 24, 38)  # Dark blue/black
    card_color = (26, 34, 54)        # Slightly lighter blue
    text_color = (255, 255, 255)
    accent_color = (59, 130, 246)    # Blue accent
    
    # Colors for status
    buy_color = (34, 197, 94)        # Green
    sell_color = (239, 68, 68)       # Red
    neutral_color = (156, 163, 175)  # Gray
    
    # Create Image
    img = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(img)
    
    # Draw Card Background
    draw.rounded_rectangle([5, 5, width-5, height-5], radius=10, fill=card_color)
    
    # Load Fonts
    try:
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if not os.path.exists(font_path):
            font_path = "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf"
            
        font_title = ImageFont.truetype(font_path, 20)
        font_main = ImageFont.truetype(font_path, 14)
        font_small = ImageFont.truetype(font_path, 11)
        font_status = ImageFont.truetype(font_path, 12)
    except:
        font_title = ImageFont.load_default()
        font_main = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_status = ImageFont.load_default()

    # Header: Instrument
    name = res.get('instrument', 'Unknown')
    draw.text((20, 20), name, font=font_title, fill=text_color)
    
    # LTP
    ltp = res.get('ltp', 0.0)
    draw.text((20, 50), f"LTP: {ltp:.5f}", font=font_main, fill=accent_color)
    
    # Status Badges (Daily, 4H, 1H)
    badge_y = 85
    badges = [
        ("DAILY", res.get('daily', {}).get('bias', 'NEUTRAL')),
        ("4H MOM", res.get('h4', {}).get('bias', 'NEUTRAL')),
        ("1H ENTRY", res.get('h1', {}).get('status', 'NEUTRAL'))
    ]
    
    for i, (label, status) in enumerate(badges):
        x = 20 + (i * 85)
        color = buy_color if "BULLISH" in status or "BUY" in status else (sell_color if "BEARISH" in status or "SELL" in status else neutral_color)
        draw.text((x, badge_y), label, font=font_small, fill=neutral_color)
        draw.text((x, badge_y + 15), status.split('_')[0], font=font_status, fill=color)

    # Active Signal Section
    signal = res.get('signal')
    if signal:
        draw.line([20, 130, width-20, 130], fill=(50, 60, 80), width=1)
        
        sig_type = signal.get('type', 'N/A')
        sig_color = buy_color if sig_type == "BUY" else sell_color
        draw.text((20, 145), "ACTIVE SIGNAL", font=font_main, fill=neutral_color)
        draw.text((width-70, 145), sig_type, font=font_main, fill=sig_color)
        
        # Signal Details
        details_y = 175
        details = [
            ("Entry Price", f"{signal.get('entry_price', 0):.5f}"),
            ("Initial SL", f"{signal.get('sl', 0):.5f}"),
            ("TP 1 (1.5x)", f"{signal.get('tp1', 0):.5f}"),
            ("TP 2 (3.0x)", f"{signal.get('tp2', 0):.5f}"),
            ("TP 3 (5.0x)", f"{signal.get('tp3', 0):.5f}")
        ]
        
        for label, val in details:
            draw.text((20, details_y), label, font=font_small, fill=neutral_color)
            draw.text((width-90, details_y), val, font=font_small, fill=text_color)
            details_y += 20

        # Closure Event
        draw.line([20, 300, width-20, 300], fill=(50, 60, 80), width=1)
        draw.text((20, 315), "CLOSURE EVENT", font=font_main, fill=neutral_color)
        draw.text((width-110, 315), event_type, font=font_main, fill=sig_color)
        
        # Timestamps
        active_time = signal.get('time', 'N/A')
        if 'T' in active_time:
            active_time = datetime.fromisoformat(active_time).strftime("%d/%b/%Y, %H:%M:%S")
            
        close_time = datetime.now().strftime("%d/%b/%Y, %H:%M:%S")
        
        draw.text((20, 350), "Detection Time:", font=font_small, fill=neutral_color)
        draw.text((110, 350), active_time, font=font_small, fill=text_color)
        
        draw.text((20, 375), "Closure Time:", font=font_small, fill=neutral_color)
        draw.text((110, 375), close_time, font=font_small, fill=text_color)

    # Save Image
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    img.save(output_path)
    print(f"✅ Screenshot saved to {output_path}")

if __name__ == "__main__":
    # Test generation
    test_res = {
        "instrument": "USD/CAD",
        "flag": "🇺🇸🇨🇦",
        "ltp": 1.37032,
        "daily": {"bias": "BEARISH"},
        "h4": {"bias": "BEARISH"},
        "h1": {"status": "BEARISH_MOM"},
        "signal": {
            "type": "SELL",
            "entry_price": 1.37063,
            "sl": 1.37245,
            "tp1": 1.36790,
            "tp2": 1.36516,
            "tp3": 1.36152,
            "time": datetime.now().isoformat()
        }
    }
    capture_trade_screenshot(test_res, "TP1 HIT", "test_trade.png")

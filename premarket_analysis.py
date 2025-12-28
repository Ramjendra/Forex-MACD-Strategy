#!/usr/bin/env python3
"""
Pre-Market Global Cues Analysis
Fetches and analyzes global market data before NSE opening to predict market sentiment
"""

import json
import yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path
import pytz

BASE_DIR = Path(__file__).parent
PREMARKET_FILE = BASE_DIR / "premarket_cues.json"

IST = pytz.timezone('Asia/Kolkata')

def fetch_us_markets():
    """Fetch previous day's US market data"""
    try:
        symbols = {
            "^GSPC": "S&P 500",
            "^IXIC": "Nasdaq",
            "^DJI": "Dow Jones"
        }
        
        results = {}
        for symbol, name in symbols.items():
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            
            if len(hist) >= 2:
                prev_close = hist['Close'].iloc[-2]
                last_close = hist['Close'].iloc[-1]
                change_pct = ((last_close - prev_close) / prev_close) * 100
                
                results[name] = {
                    "close": float(last_close),
                    "change_pct": float(change_pct),
                    "sentiment": "BULLISH" if change_pct > 0.5 else ("BEARISH" if change_pct < -0.5 else "NEUTRAL")
                }
        
        return results
    except Exception as e:
        print(f"⚠️ Error fetching US markets: {e}")
        return {}

def fetch_asian_markets():
    """Fetch Asian market data"""
    try:
        symbols = {
            "^N225": "Nikkei 225",
            "^HSI": "Hang Seng"
        }
        
        results = {}
        for symbol, name in symbols.items():
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            
            if len(hist) >= 2:
                prev_close = hist['Close'].iloc[-2]
                last_close = hist['Close'].iloc[-1]
                change_pct = ((last_close - prev_close) / prev_close) * 100
                
                results[name] = {
                    "close": float(last_close),
                    "change_pct": float(change_pct),
                    "sentiment": "BULLISH" if change_pct > 0.5 else ("BEARISH" if change_pct < -0.5 else "NEUTRAL")
                }
        
        return results
    except Exception as e:
        print(f"⚠️ Error fetching Asian markets: {e}")
        return {}

def fetch_sgx_nifty():
    """Fetch SGX Nifty data (using Nifty 50 as proxy)"""
    try:
        ticker = yf.Ticker("^NSEI")
        hist = ticker.history(period="5d")
        
        if len(hist) >= 2:
            prev_close = hist['Close'].iloc[-2]
            last_close = hist['Close'].iloc[-1]
            change_pct = ((last_close - prev_close) / prev_close) * 100
            
            return {
                "close": float(last_close),
                "change_pct": float(change_pct),
                "sentiment": "BULLISH" if change_pct > 0.5 else ("BEARISH" if change_pct < -0.5 else "NEUTRAL")
            }
    except Exception as e:
        print(f"⚠️ Error fetching SGX Nifty: {e}")
        return {}

def fetch_crude_oil():
    """Fetch Crude Oil prices"""
    try:
        ticker = yf.Ticker("CL=F")
        hist = ticker.history(period="5d")
        
        if len(hist) >= 2:
            prev_close = hist['Close'].iloc[-2]
            last_close = hist['Close'].iloc[-1]
            change_pct = ((last_close - prev_close) / prev_close) * 100
            
            return {
                "price": float(last_close),
                "change_pct": float(change_pct),
                "sentiment": "BULLISH" if change_pct > 2 else ("BEARISH" if change_pct < -2 else "NEUTRAL")
            }
    except Exception as e:
        print(f"⚠️ Error fetching Crude Oil: {e}")
        return {}

def fetch_dollar_index():
    """Fetch Dollar Index (DXY)"""
    try:
        ticker = yf.Ticker("DX-Y.NYB")
        hist = ticker.history(period="5d")
        
        if len(hist) >= 2:
            prev_close = hist['Close'].iloc[-2]
            last_close = hist['Close'].iloc[-1]
            change_pct = ((last_close - prev_close) / prev_close) * 100
            
            # For Indian markets, strong dollar is bearish
            return {
                "value": float(last_close),
                "change_pct": float(change_pct),
                "sentiment": "BEARISH" if change_pct > 0.5 else ("BULLISH" if change_pct < -0.5 else "NEUTRAL")
            }
    except Exception as e:
        print(f"⚠️ Error fetching Dollar Index: {e}")
        return {}

def calculate_overall_sentiment(data):
    """Calculate overall market sentiment from all indicators"""
    sentiments = []
    weights = {
        "us_markets": 0.35,
        "asian_markets": 0.25,
        "sgx_nifty": 0.25,
        "crude_oil": 0.10,
        "dollar_index": 0.05
    }
    
    score = 0
    
    # US Markets
    if "us_markets" in data:
        for market, info in data["us_markets"].items():
            if info["sentiment"] == "BULLISH":
                score += weights["us_markets"] / len(data["us_markets"])
            elif info["sentiment"] == "BEARISH":
                score -= weights["us_markets"] / len(data["us_markets"])
    
    # Asian Markets
    if "asian_markets" in data:
        for market, info in data["asian_markets"].items():
            if info["sentiment"] == "BULLISH":
                score += weights["asian_markets"] / len(data["asian_markets"])
            elif info["sentiment"] == "BEARISH":
                score -= weights["asian_markets"] / len(data["asian_markets"])
    
    # SGX Nifty
    if "sgx_nifty" in data and data["sgx_nifty"]:
        if data["sgx_nifty"]["sentiment"] == "BULLISH":
            score += weights["sgx_nifty"]
        elif data["sgx_nifty"]["sentiment"] == "BEARISH":
            score -= weights["sgx_nifty"]
    
    # Crude Oil
    if "crude_oil" in data and data["crude_oil"]:
        if data["crude_oil"]["sentiment"] == "BULLISH":
            score += weights["crude_oil"]
        elif data["crude_oil"]["sentiment"] == "BEARISH":
            score -= weights["crude_oil"]
    
    # Dollar Index
    if "dollar_index" in data and data["dollar_index"]:
        if data["dollar_index"]["sentiment"] == "BULLISH":
            score += weights["dollar_index"]
        elif data["dollar_index"]["sentiment"] == "BEARISH":
            score -= weights["dollar_index"]
    
    # Determine overall sentiment
    if score > 0.15:
        return "BULLISH", score
    elif score < -0.15:
        return "BEARISH", score
    else:
        return "NEUTRAL", score

def fetch_premarket_data():
    """Fetch all pre-market data and save to file"""
    print("🌍 Fetching pre-market global cues...")
    
    data = {
        "timestamp": datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S IST"),
        "us_markets": fetch_us_markets(),
        "asian_markets": fetch_asian_markets(),
        "sgx_nifty": fetch_sgx_nifty(),
        "crude_oil": fetch_crude_oil(),
        "dollar_index": fetch_dollar_index()
    }
    
    # Calculate overall sentiment
    sentiment, score = calculate_overall_sentiment(data)
    data["overall_sentiment"] = sentiment
    data["sentiment_score"] = round(score, 3)
    
    # Save to file
    with open(PREMARKET_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Pre-market analysis complete: {sentiment} (Score: {score:.3f})")
    return data

def load_premarket_data():
    """Load pre-market data from file"""
    if PREMARKET_FILE.exists():
        try:
            with open(PREMARKET_FILE, 'r') as f:
                return json.load(f)
        except:
            return None
    return None

def is_premarket_data_fresh(max_age_hours=24):
    """Check if pre-market data is fresh"""
    data = load_premarket_data()
    if not data or "timestamp" not in data:
        return False
    
    try:
        data_time = datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S IST")
        data_time = IST.localize(data_time)
        age = datetime.now(IST) - data_time
        return age.total_seconds() / 3600 < max_age_hours
    except:
        return False

def get_premarket_sentiment():
    """Get current pre-market sentiment (fetch if stale)"""
    if not is_premarket_data_fresh():
        print("📊 Pre-market data is stale, fetching fresh data...")
        return fetch_premarket_data()
    
    return load_premarket_data()

# Test function
if __name__ == "__main__":
    print("🌍 Pre-Market Global Cues Analysis")
    print("=" * 60)
    
    data = fetch_premarket_data()
    
    print("\n📊 Summary:")
    print(f"Overall Sentiment: {data['overall_sentiment']}")
    print(f"Sentiment Score: {data['sentiment_score']}")
    print(f"\nTimestamp: {data['timestamp']}")
    
    if data.get("us_markets"):
        print("\n🇺🇸 US Markets:")
        for name, info in data["us_markets"].items():
            print(f"  {name}: {info['change_pct']:+.2f}% ({info['sentiment']})")
    
    if data.get("asian_markets"):
        print("\n🌏 Asian Markets:")
        for name, info in data["asian_markets"].items():
            print(f"  {name}: {info['change_pct']:+.2f}% ({info['sentiment']})")
    
    if data.get("sgx_nifty"):
        print(f"\n🇸🇬 SGX Nifty: {data['sgx_nifty']['change_pct']:+.2f}% ({data['sgx_nifty']['sentiment']})")
    
    if data.get("crude_oil"):
        print(f"\n🛢️ Crude Oil: ${data['crude_oil']['price']:.2f} ({data['crude_oil']['change_pct']:+.2f}%)")
    
    if data.get("dollar_index"):
        print(f"\n💵 Dollar Index: {data['dollar_index']['value']:.2f} ({data['dollar_index']['change_pct']:+.2f}%)")

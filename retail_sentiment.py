#!/usr/bin/env python3
"""
Retail Sentiment Analysis Module
Fetches and analyzes retail trader positioning to provide contrarian signals
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from typing import Dict, Optional
import time

class RetailSentimentAnalyzer:
    """Analyzes retail sentiment for contrarian trading signals"""
    
    def __init__(self):
        self.sentiment_data = {}
        self.last_update = None
        
    def fetch_myfxbook_sentiment(self) -> Dict:
        """
        Fetch sentiment data from MyFxBook (alternative source)
        MyFxBook provides free retail sentiment data
        """
        try:
            url = "https://www.myfxbook.com/community/outlook"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                # Parse the HTML to extract sentiment data
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # This is a placeholder - actual parsing would depend on page structure
                # You may need to inspect the page and adjust selectors
                sentiment_data = self._parse_myfxbook_data(soup)
                return sentiment_data
            else:
                print(f"❌ Failed to fetch MyFxBook sentiment: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Error fetching MyFxBook sentiment: {e}")
            return {}
    
    def _parse_myfxbook_data(self, soup) -> Dict:
        """Parse MyFxBook HTML for sentiment data"""
        # Placeholder for actual parsing logic
        # This would need to be customized based on the actual page structure
        return {}
    
    def fetch_dailyfx_sentiment(self) -> Dict:
        """
        Fetch sentiment data from DailyFX (IG Client Sentiment)
        DailyFX provides free sentiment data via their website
        """
        try:
            # DailyFX provides sentiment data that can be accessed
            # This is a placeholder for the actual implementation
            url = "https://www.dailyfx.com/sentiment"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                # Parse sentiment data
                return self._parse_dailyfx_data(response.text)
            else:
                print(f"❌ Failed to fetch DailyFX sentiment: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Error fetching DailyFX sentiment: {e}")
            return {}
    
    def _parse_dailyfx_data(self, html: str) -> Dict:
        """Parse DailyFX HTML for sentiment data"""
        # Placeholder for actual parsing logic
        return {}
    
    def load_manual_sentiment(self, filepath: str = "sentiment_data.json") -> Dict:
        """
        Load manually entered sentiment data from JSON file
        This allows you to manually update sentiment data from A1Trading or other sources
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.sentiment_data = data.get('instruments', {})
                self.last_update = data.get('last_update')
                print(f"✅ Loaded sentiment data from {filepath}")
                print(f"   Last updated: {self.last_update}")
                return self.sentiment_data
        except FileNotFoundError:
            print(f"⚠️  Sentiment file not found: {filepath}")
            print(f"   Creating template file...")
            self._create_template_file(filepath)
            return {}
        except Exception as e:
            print(f"❌ Error loading sentiment data: {e}")
            return {}
    
    def _create_template_file(self, filepath: str):
        """Create a template sentiment data file"""
        template = {
            "last_update": datetime.now().isoformat(),
            "source": "Manual entry from A1Trading or other sources",
            "instructions": "Update the long/short percentages for each instrument",
            "instruments": {
                "EUR/USD": {
                    "long": 50.0,
                    "short": 50.0,
                    "net_position": 0.0
                },
                "USD/JPY": {
                    "long": 50.0,
                    "short": 50.0,
                    "net_position": 0.0
                },
                "GBP/USD": {
                    "long": 50.0,
                    "short": 50.0,
                    "net_position": 0.0
                },
                "USD/CHF": {
                    "long": 50.0,
                    "short": 50.0,
                    "net_position": 0.0
                },
                "USD/CAD": {
                    "long": 50.0,
                    "short": 50.0,
                    "net_position": 0.0
                },
                "AUD/USD": {
                    "long": 50.0,
                    "short": 50.0,
                    "net_position": 0.0
                },
                "NZD/USD": {
                    "long": 50.0,
                    "short": 50.0,
                    "net_position": 0.0
                }
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(template, f, indent=2)
        print(f"✅ Created template file: {filepath}")
    
    def get_sentiment_signal(self, instrument: str) -> Optional[Dict]:
        """
        Get contrarian signal based on retail sentiment
        
        Rules:
        - If retail is >60% long, consider SELL (contrarian)
        - If retail is >60% short, consider BUY (contrarian)
        - If retail is 40-60%, sentiment is neutral
        
        Returns:
            Dict with sentiment analysis or None if no data
        """
        if instrument not in self.sentiment_data:
            return None
        
        sentiment = self.sentiment_data[instrument]
        long_pct = sentiment.get('long', 50.0)
        short_pct = sentiment.get('short', 50.0)
        
        # Calculate contrarian signal strength
        if long_pct > 60:
            signal = "BEARISH"
            strength = min((long_pct - 50) / 50 * 100, 100)  # 0-100 scale
            contrarian_bias = "SELL"
        elif short_pct > 60:
            signal = "BULLISH"
            strength = min((short_pct - 50) / 50 * 100, 100)
            contrarian_bias = "BUY"
        else:
            signal = "NEUTRAL"
            strength = 0
            contrarian_bias = "NONE"
        
        return {
            "instrument": instrument,
            "retail_long": long_pct,
            "retail_short": short_pct,
            "sentiment": signal,
            "strength": round(strength, 1),
            "contrarian_bias": contrarian_bias,
            "interpretation": self._get_interpretation(long_pct, short_pct, contrarian_bias)
        }
    
    def _get_interpretation(self, long_pct: float, short_pct: float, bias: str) -> str:
        """Generate human-readable interpretation"""
        if bias == "SELL":
            return f"⚠️ {long_pct:.1f}% retail traders are LONG - Contrarian SELL signal"
        elif bias == "BUY":
            return f"⚠️ {short_pct:.1f}% retail traders are SHORT - Contrarian BUY signal"
        else:
            return f"ℹ️ Retail sentiment balanced ({long_pct:.1f}% long, {short_pct:.1f}% short)"
    
    def enrich_signal_with_sentiment(self, signal_data: Dict) -> Dict:
        """
        Enrich existing signal data with sentiment analysis
        
        Args:
            signal_data: Signal data from forex_macd_strategy
            
        Returns:
            Enhanced signal data with sentiment information
        """
        instrument = signal_data.get('instrument')
        sentiment = self.get_sentiment_signal(instrument)
        
        if sentiment:
            signal_data['retail_sentiment'] = sentiment
            
            # Add alignment indicator
            signal_type = signal_data.get('signal', {}).get('type')
            if signal_type and sentiment['contrarian_bias'] != 'NONE':
                aligned = signal_type == sentiment['contrarian_bias']
                signal_data['sentiment_aligned'] = aligned
                signal_data['sentiment_confirmation'] = "✅ STRONG" if aligned else "⚠️ WEAK"
        
        return signal_data
    
    def get_all_sentiment_summary(self) -> str:
        """Get a formatted summary of all sentiment data"""
        if not self.sentiment_data:
            return "No sentiment data available"
        
        summary = "\n📊 RETAIL SENTIMENT OVERVIEW\n"
        summary += "=" * 60 + "\n"
        
        for instrument in sorted(self.sentiment_data.keys()):
            sentiment = self.get_sentiment_signal(instrument)
            if sentiment:
                summary += f"\n{instrument}:\n"
                summary += f"  Long: {sentiment['retail_long']:.1f}% | Short: {sentiment['retail_short']:.1f}%\n"
                summary += f"  {sentiment['interpretation']}\n"
        
        summary += "\n" + "=" * 60
        return summary


def main():
    """Test the sentiment analyzer"""
    analyzer = RetailSentimentAnalyzer()
    
    # Load manual sentiment data
    print("\n🔍 Loading sentiment data...")
    analyzer.load_manual_sentiment()
    
    # Display summary
    print(analyzer.get_all_sentiment_summary())
    
    # Test individual instrument
    print("\n\n🎯 Testing USD/CHF sentiment:")
    usdchf_sentiment = analyzer.get_sentiment_signal("USD/CHF")
    if usdchf_sentiment:
        print(json.dumps(usdchf_sentiment, indent=2))


if __name__ == "__main__":
    main()

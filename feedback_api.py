#!/usr/bin/env python3
"""
Feedback API Server
Flask server to handle feedback form submissions
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from feedback_collector import FeedbackCollector
import json
from datetime import datetime
from pathlib import Path

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

BASE_DIR = Path(__file__).parent
FEEDBACK_LOG = BASE_DIR / "feedback_log.json"

# Initialize feedback collector
try:
    feedback_collector = FeedbackCollector()
    print("✅ Feedback collector initialized")
except Exception as e:
    print(f"⚠️ Feedback collector not available: {e}")
    feedback_collector = None

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Handle feedback form submission"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('message'):
            return jsonify({'success': False, 'error': 'Message is required'}), 400
        
        # Add timestamp
        data['timestamp'] = datetime.now().isoformat()
        
        # Log feedback to file
        try:
            feedback_log = []
            if FEEDBACK_LOG.exists():
                with open(FEEDBACK_LOG, 'r') as f:
                    feedback_log = json.load(f)
            
            feedback_log.append(data)
            
            # Keep last 100 feedbacks
            feedback_log = feedback_log[-100:]
            
            with open(FEEDBACK_LOG, 'w') as f:
                json.dump(feedback_log, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to log feedback: {e}")
        
        # Send email
        if feedback_collector:
            try:
                feedback_collector.send_feedback_email(data)
                return jsonify({
                    'success': True,
                    'message': 'Thank you for your feedback! We have received it.'
                })
            except Exception as e:
                print(f"❌ Failed to send feedback email: {e}")
                return jsonify({
                    'success': True,
                    'message': 'Feedback logged locally. Email notification failed.'
                })
        else:
            return jsonify({
                'success': True,
                'message': 'Feedback logged. Email system not configured.'
            })
    
    except Exception as e:
        print(f"❌ Error processing feedback: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/feedback/stats', methods=['GET'])
def get_feedback_stats():
    """Get feedback statistics"""
    try:
        if not FEEDBACK_LOG.exists():
            return jsonify({'total': 0, 'recent': []})
        
        with open(FEEDBACK_LOG, 'r') as f:
            feedback_log = json.load(f)
        
        # Calculate stats
        total = len(feedback_log)
        recent = feedback_log[-10:]  # Last 10 feedbacks
        
        # Calculate average rating
        ratings = [int(f['rating']) for f in feedback_log if f.get('rating', '').isdigit()]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        return jsonify({
            'total': total,
            'average_rating': round(avg_rating, 1),
            'recent_count': len(recent)
        })
    
    except Exception as e:
        print(f"❌ Error getting feedback stats: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Feedback API Server...")
    print("📧 Feedback will be sent to: biasbuster2026@gmail.com")
    print("🌐 Server running on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=False)

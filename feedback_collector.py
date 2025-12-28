#!/usr/bin/env python3
"""
Feedback Collection System
Collects user feedback and sends it via email to biasbuster2026@gmail.com
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

FEEDBACK_EMAIL = "biasbuster2026@gmail.com"
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

class FeedbackCollector:
    def __init__(self):
        self.email_address = EMAIL_ADDRESS
        self.email_password = EMAIL_PASSWORD
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
        self.feedback_recipient = FEEDBACK_EMAIL
        
        if not self.email_address or not self.email_password:
            raise ValueError("EMAIL_ADDRESS and EMAIL_PASSWORD must be set in .env file")
        
        print(f"📧 Feedback system configured to send to: {self.feedback_recipient}")
    
    def send_feedback_email(self, feedback_data):
        """Send feedback email"""
        try:
            # Extract feedback data
            name = feedback_data.get('name', 'Anonymous')
            email = feedback_data.get('email', 'Not provided')
            category = feedback_data.get('category', 'General')
            rating = feedback_data.get('rating', 'Not rated')
            message = feedback_data.get('message', '')
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')
            
            # Create email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"📊 Trading Dashboard Feedback - {category}"
            msg['From'] = self.email_address
            msg['To'] = self.feedback_recipient
            msg['Reply-To'] = email if email != 'Not provided' else self.email_address
            
            # HTML body
            html_body = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 700px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background-color: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .info-section {{ background-color: white; padding: 20px; margin: 15px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    .label {{ font-weight: bold; color: #667eea; display: inline-block; width: 120px; }}
                    .value {{ color: #333; }}
                    .message-box {{ background-color: #fff; padding: 20px; margin: 20px 0; border-left: 4px solid #667eea; border-radius: 5px; font-style: italic; }}
                    .rating {{ font-size: 24px; color: #ffc107; }}
                    .footer {{ margin-top: 20px; padding: 15px; background-color: #e9ecef; border-radius: 5px; font-size: 0.9em; text-align: center; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>📊 New Feedback Received</h1>
                        <p style="margin: 0; font-size: 0.9em;">Trading Dashboard Feedback System</p>
                    </div>
                    <div class="content">
                        <div class="info-section">
                            <h3 style="margin-top: 0; color: #667eea;">👤 User Information</h3>
                            <p><span class="label">Name:</span> <span class="value">{name}</span></p>
                            <p><span class="label">Email:</span> <span class="value">{email}</span></p>
                            <p><span class="label">Category:</span> <span class="value">{category}</span></p>
                            <p><span class="label">Rating:</span> <span class="rating">{'⭐' * int(rating) if str(rating).isdigit() else rating}</span></p>
                            <p><span class="label">Timestamp:</span> <span class="value">{timestamp}</span></p>
                        </div>
                        
                        <div class="info-section">
                            <h3 style="margin-top: 0; color: #667eea;">💬 Feedback Message</h3>
                            <div class="message-box">
                                {message.replace(chr(10), '<br>')}
                            </div>
                        </div>
                        
                        <div class="footer">
                            <p style="margin: 0;">🚀 <strong>Forex MACD Trading Dashboard</strong></p>
                            <p style="margin: 5px 0 0 0; color: #666;">Automated Feedback Collection System</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text version
            text_body = f"""
            NEW FEEDBACK RECEIVED
            =====================
            
            User Information:
            - Name: {name}
            - Email: {email}
            - Category: {category}
            - Rating: {rating}
            - Timestamp: {timestamp}
            
            Feedback Message:
            {message}
            
            ---
            Forex MACD Trading Dashboard
            Automated Feedback Collection System
            """
            
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            
            print(f"✅ Feedback email sent to {self.feedback_recipient}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send feedback email: {e}")
            return False
    
    def send_test_feedback(self):
        """Send a test feedback email"""
        test_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'category': 'System Test',
            'rating': 5,
            'message': 'This is a test feedback message to verify the email system is working correctly.'
        }
        return self.send_feedback_email(test_data)


def test_feedback_system():
    """Test the feedback collection system"""
    try:
        collector = FeedbackCollector()
        print("📧 Testing feedback email system...")
        
        if collector.send_test_feedback():
            print("✅ Test feedback sent successfully!")
            print(f"✅ Check inbox: {FEEDBACK_EMAIL}")
            return True
        else:
            print("❌ Failed to send test feedback")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    test_feedback_system()

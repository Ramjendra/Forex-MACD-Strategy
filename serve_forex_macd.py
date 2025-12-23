#!/usr/bin/env python3
"""
Simple HTTP server to serve the Forex MACD dashboard.
"""

import http.server
import socketserver
import webbrowser
import os
import json
import csv
import io
from pathlib import Path
from datetime import datetime

PORT = int(os.environ.get("PORT", 8003))
BASE_DIR = Path(__file__).parent
VISITORS_FILE = BASE_DIR / "visitors.json"

import time

ACTIVE_USERS = {} # {ip: last_seen_timestamp}

def get_visitor_stats(ip_address=None):
    visitors = set()
    if VISITORS_FILE.exists():
        try:
            with open(VISITORS_FILE, 'r') as f:
                visitors = set(json.load(f))
        except:
            pass
    
    current_time = time.time()
    if ip_address:
        visitors.add(ip_address)
        ACTIVE_USERS[ip_address] = current_time
        with open(VISITORS_FILE, 'w') as f:
            json.dump(list(visitors), f)
            
    # Clean up inactive users (older than 2 minutes)
    inactive = [ip for ip, ts in ACTIVE_USERS.items() if current_time - ts > 120]
    for ip in inactive:
        del ACTIVE_USERS[ip]
        
    return {
        "unique": len(visitors),
        "active": len(ACTIVE_USERS)
    }

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/visitor-count':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            stats = get_visitor_stats()
            self.wfile.write(json.dumps(stats).encode())
            return
            
        if self.path == '/api/download-report':
            history_file = BASE_DIR / "signal_history.json"
            if not history_file.exists():
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"History file not found")
                return

            try:
                with open(history_file, 'r') as f:
                    history = json.load(f)
                
                # Filter for today's events
                today_str = datetime.now().strftime("%Y-%m-%d")
                today_events = [e for e in history if e.get('time', '').startswith(today_str)]
                
                if not today_events:
                    # If no events today, maybe take last 50 events as fallback or just return empty
                    # Let's just return what we have for today
                    pass

                # Create CSV in memory
                output = io.StringIO()
                if today_events:
                    keys = today_events[0].keys()
                    dict_writer = csv.DictWriter(output, fieldnames=keys)
                    dict_writer.writeheader()
                    dict_writer.writerows(today_events)
                
                csv_content = output.getvalue()
                
                self.send_response(200)
                self.send_header('Content-type', 'text/csv')
                self.send_header('Content-Disposition', f'attachment; filename=daily_signal_report_{today_str}.csv')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(csv_content.encode('utf-8'))
                return
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Error generating report: {e}".encode())
                return
            
        if self.path == '/api/heartbeat':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            get_visitor_stats(self.client_address[0])
            self.wfile.write(json.dumps({"status": "alive"}).encode())
            return
            
        if self.path == '/api/past-trades-dates':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            past_trades_dir = BASE_DIR / "past_trades"
            dates = []
            if past_trades_dir.exists():
                dates = sorted([d.name for d in past_trades_dir.iterdir() if d.is_dir()], reverse=True)
            
            self.wfile.write(json.dumps(dates).encode())
            return

        if self.path.startswith('/api/past-trades-images'):
            from urllib.parse import urlparse, parse_qs
            query = parse_qs(urlparse(self.path).query)
            date_str = query.get('date', [None])[0]
            
            if not date_str:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Date parameter missing")
                return
                
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            images_dir = BASE_DIR / "past_trades" / date_str
            images = []
            if images_dir.exists():
                images = sorted([f.name for f in images_dir.iterdir() if f.suffix.lower() in ['.png', '.jpg', '.jpeg']], reverse=True)
            
            self.wfile.write(json.dumps(images).encode())
            return

        # Track visitor for main page
        if self.path == '/':
            self.path = '/forex_macd_dashboard.html'
            
        if self.path.endswith('.html'):
            get_visitor_stats(self.client_address[0])
            
        return super().do_GET()

    def do_POST(self):
        if self.path == '/api/feedback':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            feedback_data = json.loads(post_data.decode('utf-8'))
            
            feedback_file = BASE_DIR / "feedback.json"
            feedbacks = []
            if feedback_file.exists():
                try:
                    with open(feedback_file, 'r') as f:
                        feedbacks = json.load(f)
                except:
                    pass
            
            feedbacks.append({
                "time": Path(__file__).stat().st_mtime, # Using mtime as a simple timestamp
                "ip": self.client_address[0],
                "feedback": feedback_data.get('feedback')
            })
            
            with open(feedback_file, 'w') as f:
                json.dump(feedbacks, f, indent=2)
                
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode())
            return

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

def main():
    os.chdir(BASE_DIR)
    
    # Initialize visitors file if not exists
    if not VISITORS_FILE.exists():
        with open(VISITORS_FILE, 'w') as f:
            json.dump([], f)
    
    Handler = MyHTTPRequestHandler
    
    # Allow address reuse to avoid "Address already in use" errors on restart
    socketserver.TCPServer.allow_reuse_address = True
    
    class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
        pass

    with ThreadingTCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"🚀 Dashboard serving at http://0.0.0.0:{PORT}")
        print(f"\n✓ Server running at: http://localhost:{PORT}")
        print(f"✓ Dashboard URL: http://localhost:{PORT}/forex_macd_dashboard.html")
        print("\n📊 Opening dashboard in browser...")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 60)
        
        # webbrowser.open(f'http://localhost:{PORT}/forex_macd_dashboard.html')
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n✓ Server stopped")

if __name__ == "__main__":
    main()

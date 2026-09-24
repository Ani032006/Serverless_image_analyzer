"""
Web Dashboard Launcher for AWS Serverless AI Image Analyzer
Runs a local web server and automatically opens the interactive visual simulator in your web browser.
"""

import http.server
import socketserver
import webbrowser
import os
import sys
import threading
import time

PORT = 8000
WEB_DIR = os.path.join(os.path.dirname(__file__), 'web')

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

def start_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"\n==============================================================")
        print(f"  SERVERLESS AI IMAGE ANALYZER — INTERACTIVE VISUAL DASHBOARD")
        print(f"==============================================================")
        print(f"  [OK] Local Web Server running at: http://localhost:{PORT}")
        print(f"  [OK] Opening browser automatically...")
        print(f"  [INFO] Press Ctrl+C in terminal to stop server.\n")
        
        # Open web browser after a short delay
        threading.Thread(target=open_browser).start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  [INFO] Web server stopped.")

def open_browser():
    time.sleep(1)
    webbrowser.open(f"http://localhost:{PORT}")

if __name__ == '__main__':
    start_server()

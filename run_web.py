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

DEFAULT_PORT = 8080
WEB_DIR = os.path.join(os.path.dirname(__file__), 'web')

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def find_available_port(start_port=8080):
    import socket
    port = start_port
    while port < start_port + 50:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
        port += 1
    return start_port

def start_server():
    port = find_available_port(DEFAULT_PORT)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"\n==============================================================")
        print(f"  SERVERLESS AI IMAGE ANALYZER — INTERACTIVE VISUAL DASHBOARD")
        print(f"==============================================================")
        print(f"  [OK] Local Web Server running at: http://localhost:{port}")
        print(f"  [OK] Opening browser automatically...")
        print(f"  [INFO] Press Ctrl+C in terminal to stop server.\n")
        
        # Open web browser after a short delay
        threading.Thread(target=open_browser, args=(port,)).start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  [INFO] Web server stopped.")

def open_browser(port):
    time.sleep(1)
    webbrowser.open(f"http://localhost:{port}")

if __name__ == '__main__':
    start_server()

#!/usr/bin/env python3
"""
Serve the Sukha landing page locally.

Usage:
    python serve.py          # Serve on http://localhost:8000
    python serve.py 3000     # Serve on http://localhost:3000

This is needed because the JS uses modern browser features that
work best over HTTP (not file://). Also allows testing on other
devices on your local network.
"""

import http.server
import socketserver
import os
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        super().end_headers()

if __name__ == "__main__":
    os.chdir(DIRECTORY)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving Sukha landing page at http://localhost:{PORT}")
        print(f"Directory: {DIRECTORY}")
        print("Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

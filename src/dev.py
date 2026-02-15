#!/usr/bin/env python3
"""
Development server for local preview.
Serves the public/ directory on http://localhost:8000
"""

import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import sys

# Add src to path to import config
sys.path.insert(0, str(Path(__file__).parent))
from config import DEV_SERVER_HOST, DEV_SERVER_PORT


class CustomHandler(SimpleHTTPRequestHandler):
    """Custom handler to serve from public/ directory."""
    
    def __init__(self, *args, **kwargs):
        # Change to public directory
        public_dir = Path(__file__).parent.parent / "public"
        super().__init__(*args, directory=str(public_dir), **kwargs)
    
    def log_message(self, format, *args):
        """Custom log format."""
        print(f"[{self.log_date_time_string()}] {format % args}")


def serve(port=None, host=None):
    """Run local development server.
    
    Args:
        port: Port number (default from config or DEV_SERVER_PORT env)
        host: Host address (default from config or DEV_SERVER_HOST env)
    """
    port = port or int(os.environ.get("DEV_SERVER_PORT", str(DEV_SERVER_PORT)))
    host = host or os.environ.get("DEV_SERVER_HOST", DEV_SERVER_HOST)
    
    public_dir = Path(__file__).parent.parent / "public"
    
    if not public_dir.exists():
        print("❌ Public directory not found. Run 'python3 src/build.py' first.")
        return False
    
    server = HTTPServer((host, port), CustomHandler)
    print(f"🌐 Server running at http://{host}:{port}")
    print("📂 Serving from:", public_dir)
    print("Press Ctrl+C to stop")
    print()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped")
        return True


if __name__ == "__main__":
    serve()

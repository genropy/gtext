"""HTTP server for live preview of gtext documents."""

import http.server
import json
import socketserver
import threading
import time
from pathlib import Path
from typing import Optional

from gtext.processor import TextProcessor


class PreviewHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler for serving rendered gtext documents."""

    processor: TextProcessor
    source_file: Path
    last_modified: float = 0

    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/":
            # Serve the rendered document
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            html = self.render_document()
            self.wfile.write(html.encode("utf-8"))

        elif self.path == "/api/check":
            # Check if file has been modified
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            current_mtime = self.source_file.stat().st_mtime
            modified = current_mtime > self.last_modified
            if modified:
                self.last_modified = current_mtime

            response = json.dumps({"modified": modified})
            self.wfile.write(response.encode("utf-8"))

        else:
            self.send_error(404)

    def render_document(self) -> str:
        """Render the gtext document to HTML."""
        try:
            # Update last modified time
            self.last_modified = self.source_file.stat().st_mtime

            # Process the gtext file
            content = self.processor.process_string(
                self.source_file.read_text(encoding="utf-8"),
                context={"input_path": self.source_file},
            )

            # Wrap in HTML template
            html = HTML_TEMPLATE.format(
                title=self.source_file.name,
                content=content,
                source_file=self.source_file.name,
            )

            return html

        except Exception as e:
            # Show error in preview
            error_html = ERROR_TEMPLATE.format(source_file=self.source_file.name, error=str(e))
            return error_html

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - gtext Preview</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                "Helvetica Neue", Arial, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            background: #ffffff;
            color: #333;
        }}
        .header {{
            background: #f5f5f5;
            border-bottom: 2px solid #4CAF50;
            padding: 10px 20px;
            margin: -20px -20px 20px -20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 18px;
            color: #4CAF50;
        }}
        .status {{
            font-size: 12px;
            color: #666;
        }}
        .status.watching {{
            color: #4CAF50;
        }}
        pre {{
            background: #f4f4f4;
            border: 1px solid #ddd;
            border-left: 3px solid #4CAF50;
            padding: 10px;
            overflow-x: auto;
        }}
        code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
        }}
        pre code {{
            background: none;
            padding: 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🪄 gtext Preview: {source_file}</h1>
        <div class="status watching">● Live</div>
    </div>
    <div id="content">
{content}
    </div>
    <script>
        // Poll for changes every second
        setInterval(async () => {{
            try {{
                const response = await fetch('/api/check');
                const data = await response.json();
                if (data.modified) {{
                    console.log('File changed, reloading...');
                    location.reload();
                }}
            }} catch (e) {{
                console.error('Error checking for updates:', e);
            }}
        }}, 1000);
    </script>
</body>
</html>
"""

ERROR_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error - gtext Preview</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                "Helvetica Neue", Arial, sans-serif;
            max-width: 900px;
            margin: 50px auto;
            padding: 20px;
        }}
        .error {{
            background: #fee;
            border: 2px solid #f44336;
            border-radius: 5px;
            padding: 20px;
        }}
        .error h1 {{
            color: #f44336;
            margin-top: 0;
        }}
        pre {{
            background: #f4f4f4;
            padding: 10px;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
    <div class="error">
        <h1>Error Processing {source_file}</h1>
        <pre>{error}</pre>
    </div>
    <script>
        // Still poll for changes
        setInterval(async () => {{
            try {{
                const response = await fetch('/api/check');
                const data = await response.json();
                if (data.modified) {{
                    location.reload();
                }}
            }} catch (e) {{
                // Server might be down
            }}
        }}, 1000);
    </script>
</body>
</html>
"""


class PreviewServer:
    """HTTP server for live preview of gtext documents."""

    def __init__(self, source_file: Path, port: int = 8080, host: str = "127.0.0.1"):
        """Initialize the preview server.

        Args:
            source_file: Path to the .gtext source file
            port: Port to serve on (default: 8080)
            host: Host to bind to (default: 127.0.0.1)
        """
        self.source_file = source_file.resolve()
        self.port = port
        self.host = host
        self.processor = TextProcessor()
        self.server: Optional[socketserver.TCPServer] = None
        self.thread: Optional[threading.Thread] = None

    def start(self):
        """Start the preview server."""
        # Configure the handler
        PreviewHandler.processor = self.processor
        PreviewHandler.source_file = self.source_file

        # Create server
        self.server = socketserver.TCPServer((self.host, self.port), PreviewHandler)
        self.server.allow_reuse_address = True

        # Start server in background thread
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

        print("gtext Preview Server")
        print(f"Source: {self.source_file}")
        print(f"URL: http://{self.host}:{self.port}")
        print()
        print("Press Ctrl+C to stop")

    def stop(self):
        """Stop the preview server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()

    def serve_forever(self):
        """Keep the server running until interrupted."""
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.stop()

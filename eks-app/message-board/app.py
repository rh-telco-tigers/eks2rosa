#!/usr/bin/env python3
"""Minimal message board using only stdlib. GET / shows form and messages; POST /message appends to PVC file."""
import os
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

DATA_DIR = os.environ.get("DATA_DIR", "/data")
MESSAGES_FILE = os.path.join(DATA_DIR, "messages.txt")


def read_messages():
    if not os.path.exists(MESSAGES_FILE):
        return []
    with open(MESSAGES_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]


def append_message(msg: str):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(MESSAGES_FILE, "a") as f:
        f.write(msg.strip() + "\n")


HTML_HEAD = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Message board</title>
<style>body{font-family:sans-serif;max-width:600px;margin:2em auto;padding:0 1em;}
  form{margin:1em 0;} input[type=text]{width:100%;padding:8px;}
  button{padding:8px 16px;margin-top:8px;} ul{list-style:none;padding:0;}
  li{padding:8px;margin:4px 0;background:#f0f0f0;border-radius:4px;}</style>
</head>
<body>
  <h1>Message board</h1>
  <p>Messages are stored on a PVC.</p>
  <form method="post" action="/message">
    <input type="text" name="message" placeholder="Your message" required>
    <button type="submit">Send</button>
  </form>
  <h2>Messages</h2>
  <ul>
"""

HTML_TAIL = """
  </ul>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/":
            self.send_error(404)
            return
        messages = read_messages()
        lines = "".join(f"    <li>{m}</li>\n" for m in reversed(messages))
        if not lines:
            lines = "    <li><em>No messages yet.</em></li>\n"
        body = (HTML_HEAD + lines + HTML_TAIL).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/message":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8", errors="ignore")
        params = urllib.parse.parse_qs(raw)
        msg = (params.get("message") or [""])[0].strip()
        if msg:
            append_message(msg)
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()


def main():
    server = HTTPServer(("0.0.0.0", 8080), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()

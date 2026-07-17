#!/usr/bin/env python3
"""本地正文预览服务 · 默认 http://0.0.0.0:8765/preview/"""
from __future__ import annotations

import http.server
import socketserver
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # novel-project/
PORT = 8765


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()


def main():
    with socketserver.ThreadingTCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"Preview: http://127.0.0.1:{PORT}/preview/")
        print(f"Serving: {ROOT}")
        httpd.serve_forever()


if __name__ == "__main__":
    main()

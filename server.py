#!/usr/bin/env python3
"""
本地代理服务器：解决 Electron 里的 CORS 问题
同时 serve 静态文件 + 代理 citycost.cn API 请求
"""
import http.server
import socketserver
import urllib.request
import urllib.error
import json
import os
from urllib.parse import urlparse

PORT = 8765
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)

        # 代理城市 API 请求
        if '/api/' in self.path:
            self.proxy_request()
            return

        return super().do_GET()

    def proxy_request(self):
        parsed = urlparse(self.path)
        target_url = 'https://citycost.cn' + parsed.path

        try:
            req = urllib.request.Request(
                target_url,
                headers={
                    'User-Agent': 'EarthExplorer/1.0',
                    'Accept': 'application/json',
                    'Origin': 'http://localhost:8765',
                    'Access-Control-Request-Headers': 'Content-Type'
                }
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', '*')
                self.send_header('Cache-Control', 'public, max-age=3600')
                self.end_headers()
                self.wfile.write(data)
                print(f"[Proxy] {target_url} -> 200 OK ({len(data)} bytes)")
        except urllib.error.HTTPError as e:
            self.send_error(e.code, f"Upstream error: {e.reason}")
            print(f"[Proxy] {target_url} -> {e.code} {e.reason}")
        except Exception as e:
            self.send_error(502, f"Proxy error: {str(e)}")
            print(f"[Proxy] {target_url} -> ERROR: {e}")

    def end_headers(self):
        # CORS 头（所有响应）
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

print(f"[Server] 静态文件 + API 代理服务器")
print(f"[Server] 目录: {DIRECTORY}")
print(f"[Server] 监听: http://localhost:{PORT}")
print(f"[Server] API 代理: citycost.cn -> /api/")

os.chdir(DIRECTORY)
with socketserver.TCPServer(("", PORT), ProxyHandler) as httpd:
    httpd.serve_forever()

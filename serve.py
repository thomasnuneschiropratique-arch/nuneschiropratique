#!/usr/bin/env python3
"""Serveur de prévisualisation local : python3 serve.py  ->  http://localhost:8788"""
import functools, http.server, os, socketserver, sys

DIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")

class H(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, p):
        r = super().translate_path(p)
        if os.path.isdir(r):
            return os.path.join(r, "index.html")
        if not os.path.exists(r) and not os.path.splitext(r)[1]:
            return os.path.join(DIST, "404.html")
        return r
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()
    def log_message(self, *a):
        pass

port = int(sys.argv[1]) if len(sys.argv) > 1 else 8788
socketserver.TCPServer.allow_reuse_address = True
handler = functools.partial(H, directory=DIST)
print("→ http://localhost:%d" % port)
socketserver.TCPServer(("", port), handler).serve_forever()

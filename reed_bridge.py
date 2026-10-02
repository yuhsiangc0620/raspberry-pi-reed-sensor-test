"""Expose a two-wire reed switch to the browser running on this Raspberry Pi.

Open https://sleep-airline-s3.vercel.app/?reed=1 on the same Pi after starting
this script. The HTTP service listens only on the Pi's loopback interface.
"""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from gpiozero import Button


SITE_ORIGIN = "https://sleep-airline-s3.vercel.app"
reed = Button(17, pull_up=True, bounce_time=0.05)


class ReedHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        if self.headers.get("Origin") == SITE_ORIGIN:
            self.send_header("Access-Control-Allow-Origin", SITE_ORIGIN)
            self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            if self.headers.get("Access-Control-Request-Private-Network") == "true":
                self.send_header("Access-Control-Allow-Private-Network", "true")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Vary", "Origin, Access-Control-Request-Private-Network")
        super().end_headers()

    def do_OPTIONS(self):
        if self.path != "/state":
            self.send_error(404)
            return
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        if self.path != "/state":
            self.send_error(404)
            return
        body = json.dumps({"closed": reed.is_pressed}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # The browser polls frequently; keep the terminal readable.
        pass


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8765), ReedHandler)
    print("Reed bridge running at http://127.0.0.1:8765/state")
    print("Open https://sleep-airline-s3.vercel.app/?reed=1 on this Pi")
    print("Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        reed.close()

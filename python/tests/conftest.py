import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest


class FakeServer:
    """In-memory HTTP file server with Range support and fault injection."""

    def __init__(self):
        self.files = {}           # path -> bytes
        self.support_range = True
        self.fail_next = []       # status codes to return before serving normally
        self.truncate_next = 0    # number of responses to cut short (half the body)
        self.requests = []        # (path, Range header or None)
        self._httpd = ThreadingHTTPServer(("127.0.0.1", 0), self._handler())
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)

    @property
    def url(self) -> str:
        host, port = self._httpd.server_address
        return f"http://{host}:{port}"

    def start(self):
        self._thread.start()

    def stop(self):
        self._httpd.shutdown()
        self._httpd.server_close()

    def _handler(self):
        server = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, *args):
                pass

            def do_GET(self):
                rng = self.headers.get("Range")
                server.requests.append((self.path, rng))
                if server.fail_next:
                    self._send_status(server.fail_next.pop(0))
                    return
                data = server.files.get(self.path)
                if data is None:
                    self._send_status(404)
                    return
                start, status = 0, 200
                if rng and server.support_range:
                    start = int(re.match(r"bytes=(\d+)-", rng).group(1))
                    if start >= len(data):
                        self.send_response(416)
                        self.send_header("Content-Range", f"bytes */{len(data)}")
                        self.send_header("Content-Length", "0")
                        self.end_headers()
                        return
                    status = 206
                body = data[start:]
                self.send_response(status)
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Accept-Ranges", "bytes" if server.support_range else "none")
                if status == 206:
                    self.send_header("Content-Range", f"bytes {start}-{len(data) - 1}/{len(data)}")
                self.end_headers()
                if server.truncate_next:
                    server.truncate_next -= 1
                    self.wfile.write(body[:len(body) // 2])
                    self.wfile.flush()
                    self.close_connection = True
                    return
                self.wfile.write(body)

            def _send_status(self, code):
                self.send_response(code)
                self.send_header("Content-Length", "0")
                self.end_headers()

        return Handler


@pytest.fixture
def server():
    srv = FakeServer()
    srv.start()
    yield srv
    srv.stop()

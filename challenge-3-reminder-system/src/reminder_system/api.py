"""Minimal HTTP API on Python's stdlib (http.server) — zero dependencies.

Endpoints:
    GET  /health              -> {"status":"ok"}
    GET  /reminders           -> all reminders
    POST /reminders/query     -> body {"context": "...", "top_k": 3}
                                 returns only applicable reminders + relevance

Rationale for stdlib over FastAPI/Flask: the brief prioritizes simple,
reproducible local setup. Zero runtime dependencies means `python3 -m` runs
anywhere; swapping to a framework later touches only this file.
"""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Optional

from .retrieval import ReminderService


def make_handler(service: ReminderService):
    class Handler(BaseHTTPRequestHandler):
        server_version = "ReminderSystem/1.0"

        def _send(self, code: int, payload: dict):
            body = json.dumps(payload, indent=2).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):  # noqa: N802
            path = self.path.rstrip("/") or "/"
            if path == "/health":
                self._send(200, {"status": "ok"})
            elif path == "/reminders":
                self._send(200, {"reminders": [r.to_dict() for r in service.list_reminders()]})
            else:
                self._send(404, {"error": "not found", "path": path})

        def do_POST(self):  # noqa: N802
            if self.path.rstrip("/") != "/reminders/query":
                self._send(404, {"error": "not found"})
                return
            try:
                length = int(self.headers.get("Content-Length", 0))
                req = json.loads(self.rfile.read(length) or b"{}")
            except json.JSONDecodeError:
                self._send(400, {"error": "invalid JSON"})
                return
            context = req.get("context")
            if not isinstance(context, str) or not context.strip():
                self._send(422, {"error": "field 'context' must be a non-empty string"})
                return
            top_k = req.get("top_k", 3)
            if not isinstance(top_k, int) or not 1 <= top_k <= 10:
                self._send(422, {"error": "'top_k' must be an integer in [1,10]"})
                return
            hits = service.query(context, top_k=top_k)
            self._send(200, {
                "query": context,
                "count": len(hits),
                "reminders": [h.to_dict() for h in hits],
            })

        def log_message(self, fmt, *args):  # quiet by default
            pass

    return Handler


class ApiServer:
    """Context-managed server usable in tests (port 0 = ephemeral)."""

    def __init__(self, service: ReminderService, host: str = "127.0.0.1",
                 port: int = 8000):
        self.httpd = ThreadingHTTPServer((host, port),
                                         make_handler(service))
        self.url = f"http://{host}:{self.httpd.server_port}"

    def __enter__(self):
        import threading
        self.thread = threading.Thread(target=self.httpd.serve_forever,
                                       daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *exc):
        self.httpd.shutdown()
        self.httpd.server_close()

    def serve_forever(self):
        self.httpd.serve_forever()

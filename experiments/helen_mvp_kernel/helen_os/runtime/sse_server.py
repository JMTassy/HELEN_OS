"""Minimal SSE server — streams HELEN state and Ralph iterations over HTTP.

No Flask. Pure stdlib.

Endpoints:
  GET /state   — kernel state stream (ledger → fold → state_hash)
  GET /ralph   — Ralph iteration stream (sidecar → exploration state)

Usage:
    python -m helen_os.runtime.sse_server --ledger path/to/events.ndjson --port 8765

The surface subscribes; the kernel remains the source of truth.
Ralph explores; HELEN observes.
"""
from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from helen_os.runtime.state_observer import tail
from helen_os.runtime.ralph_observer import tail_ralph

_LEDGER_PATH: Path = Path("ledger/events.ndjson")
_RALPH_SIDECAR: Path = Path("artifacts/ralph_runs.ndjson")
_POLL_INTERVAL: float = 0.25


class _SSEHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args) -> None:
        pass

    def _send_sse_headers(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def do_GET(self) -> None:
        if self.path == "/state":
            self._send_sse_headers()
            try:
                for snapshot in tail(_LEDGER_PATH, poll_interval=_POLL_INTERVAL):
                    self.wfile.write(f"data: {json.dumps(snapshot)}\n\n".encode())
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass

        elif self.path == "/ralph":
            self._send_sse_headers()
            try:
                for record in tail_ralph(_RALPH_SIDECAR, poll_interval=_POLL_INTERVAL):
                    self.wfile.write(f"data: {json.dumps(record)}\n\n".encode())
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass

        else:
            self.send_response(404)
            self.end_headers()


def serve(ledger_path: Path, ralph_sidecar: Path, port: int = 8765) -> None:
    global _LEDGER_PATH, _RALPH_SIDECAR
    _LEDGER_PATH = ledger_path
    _RALPH_SIDECAR = ralph_sidecar
    server = HTTPServer(("127.0.0.1", port), _SSEHandler)
    print(f"HELEN SSE → http://127.0.0.1:{port}/state  (kernel state)")
    print(f"          → http://127.0.0.1:{port}/ralph  (Ralph iterations)")
    print(f"ledger:  {ledger_path}")
    print(f"sidecar: {ralph_sidecar}")
    server.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HELEN SSE observer")
    parser.add_argument("--ledger", default="ledger/events.ndjson")
    parser.add_argument("--ralph-sidecar", default="artifacts/ralph_runs.ndjson")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    serve(Path(args.ledger), Path(args.ralph_sidecar), args.port)

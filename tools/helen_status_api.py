#!/usr/bin/env python3
"""
HELEN Status API — non-sovereign read-only bridge.
Serves /api/status on port 7001 (CORS-open for localhost:7000).

Reads:
  - town/ledger_v1.ndjson  (line count only — no parse, no write)
  - git HEAD, branch, dirty state, ahead count

Does NOT write anything. Does NOT call helen_say.py or any sovereign path.

Usage:
  python3 tools/helen_status_api.py
  python3 tools/helen_status_api.py --port 7001
"""
import os, sys, json, subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

PORT = int(sys.argv[sys.argv.index('--port') + 1]) if '--port' in sys.argv else 7002

SOT = Path(__file__).resolve().parent.parent
LEDGER = SOT / 'town' / 'ledger_v1.ndjson'


def ledger_count() -> int:
    try:
        with open(LEDGER, 'rb') as f:
            return sum(1 for _ in f)
    except Exception:
        return -1


def git_state() -> dict:
    try:
        def run(*args):
            return subprocess.check_output(
                list(args), cwd=SOT, stderr=subprocess.DEVNULL
            ).decode().strip()
        head   = run('git', 'rev-parse', '--short', 'HEAD')
        branch = run('git', 'rev-parse', '--abbrev-ref', 'HEAD')
        dirty  = bool(run('git', 'status', '--porcelain'))
        ahead  = int(run('git', 'rev-list', '--count', 'origin/main..HEAD') or '0')
        return {'head': head, 'branch': branch, 'dirty': dirty, 'ahead': ahead}
    except Exception:
        return {'head': '—', 'branch': '—', 'dirty': False, 'ahead': 0}


class StatusHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # suppress request noise

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if self.path != '/api/status':
            self.send_response(404)
            self.end_headers()
            return

        g = git_state()
        payload = {
            'ledger_count': ledger_count(),
            'branch': g['branch'],
            'commit': g['head'],
            'dirty': g['dirty'],
            'ahead': g['ahead'],
            'operator': 'JM Tassy',
            'mode': 'Building',
            'authority': False,
        }
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)


if __name__ == '__main__':
    server = HTTPServer(('127.0.0.1', PORT), StatusHandler)
    print(f'HELEN status API → http://127.0.0.1:{PORT}/api/status  (SOT: {SOT})')
    print(f'Ledger: {LEDGER} ({"exists" if LEDGER.exists() else "NOT FOUND"})')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nStopped.')

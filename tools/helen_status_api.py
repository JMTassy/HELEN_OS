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
import os, sys, json, subprocess, time
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


def _age_label(path: Path) -> str:
    if not path.exists():
        return None
    h = (time.time() - path.stat().st_mtime) / 3600
    if h < 1:   return f'{int(h*60)}min ago'
    if h < 24:  return f'{int(h)}h ago'
    return f'{int(h/24)}d ago'


def agent_states() -> dict:
    s = {}
    g = git_state()

    # HELEN — git state
    s['helen'] = f'{g["branch"]} · {g["head"]}{"  DIRTY" if g["dirty"] else ""}'

    # HAL — last K8 lint artifact
    k8 = SOT / 'artifacts' / 'k8_trace.ndjson'
    age = _age_label(k8)
    s['hal'] = f'K8 ran {age}' if age else 'idle · no recent gate run'

    # MAYOR — ledger count
    n = ledger_count()
    s['mayor'] = f'{n} ledger entries · authority active' if n > 0 else 'idle · ledger empty'

    # HER — autoresearch tranche receipts
    tr = SOT / 'GOVERNANCE' / 'TRANCHE_RECEIPTS'
    count = len(list(tr.glob('*.md')) + list(tr.glob('*.json'))) if tr.exists() else 0
    s['her'] = f'{count} tranche receipts · E12 halted' if count else 'idle · no active tranche'

    # GOBLIN — proposals in queue
    pd = SOT / 'docs' / 'proposals'
    pc = len(list(pd.glob('*.md'))) if pd.exists() else 0
    s['goblin'] = f'{pc} proposals in queue' if pc else 'heap clear · idle'

    # CHRONOS — epoch state
    lc = ledger_count()
    ep = min(lc // 3, 99) if lc > 0 else 0
    s['chronos'] = f'E{ep:02d} · {lc} events logged' if lc > 0 else 'epoch 0 · no events yet'

    # AURA — temple subsandbox
    aura = SOT / 'temple' / 'subsandbox' / 'aura'
    ac = len(list(aura.glob('*.md'))) if aura.exists() else 0
    s['aura'] = f'{ac} symbolic samples · non-sovereign' if ac else 'grimoire empty'

    # DIRECTOR — video pipeline
    d = SOT / 'oracle_town' / 'skills' / 'video' / 'helen-director'
    s['director'] = 'pipeline ready · 3-shot renderer' if d.exists() else 'idle'

    return s


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
        if self.path == '/api/status':
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
        elif self.path == '/api/agents':
            payload = agent_states()
        else:
            self.send_response(404)
            self.end_headers()
            return

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

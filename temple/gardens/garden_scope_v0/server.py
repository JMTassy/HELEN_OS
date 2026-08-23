#!/usr/bin/env python3
"""
GARDEN_SCOPE server — serves the J-space observation surface (Θ, presentation only).

Reads typed state; serves it. It NEVER mutates Garden state, emits no receipt,
promotes nothing. terminal-browser (or any browser) is the microscope; this is
the slide. Endpoints:
    GET /                 → static/index.html
    GET /static/<f>       → static asset
    GET /api/state        → summary counters projected from the two receipts
    GET /api/events       → the AgentEvent NDJSON bus, parsed to a JSON array
Law: color=projection(typed_state) · ΔX=ΔP=ΔE=ΔA=0 · NO_CLAIM.
Run:  python3 server.py [port]   (default 8787)
"""
import json, sys
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import reducer as R   # the ONE canonical reducer — browser must consume this, not its own

ROOT = Path(__file__).resolve().parent
GARDEN = ROOT.parent / "async_wulmath_chaos_garden_v1"
CHAOS = GARDEN / "ASYNC_WULMATH_CHAOS_GARDEN_V1_RECEIPT.json"
GATE = GARDEN / "HARD_CHIDDUSH_GATE_RECEIPT.json"
EVENTS = ROOT / "traces" / "garden_events.ndjson"
LIVE = ROOT / "traces" / "live_events.ndjson"
MIME = {".html": "text/html", ".css": "text/css", ".js": "text/javascript"}


def state():
    ch = json.loads(CHAOS.read_text()) if CHAOS.exists() else {}
    gt = json.loads(GATE.read_text()) if GATE.exists() else {}
    return {
        "schema": ch.get("schema", "—"),
        "authority_delta": ch.get("authority_delta", gt.get("authority_delta", 0)),
        "claim": ch.get("claim", "NO_CLAIM"),
        "her_gen": ch.get("her_raw_objects"), "hal_gen": ch.get("hal_raw_objects"),
        "distinct": ch.get("distinct_structures"), "dup_rate": ch.get("duplication_rate"),
        "tested": gt.get("objects_tested"), "typed": gt.get("survives"),
        "compost": gt.get("renaming_only_compost"), "evidence": gt.get("evidence_needed"),
    }


def _read_ndjson(path):
    if not path.exists():
        return []
    out = []
    for ln in path.read_text().splitlines():
        ln = ln.strip()
        if ln:
            try: out.append(json.loads(ln))
            except json.JSONDecodeError: pass
    return out


def events(): return _read_ndjson(EVENTS)
def live_events(): return _read_ndjson(LIVE)


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass  # quiet

    def _send(self, code, body, ctype="application/json"):
        b = body if isinstance(body, bytes) else body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        p = self.path.split("?")[0]
        if p == "/" or p == "/index.html":
            return self._send(200, (ROOT / "static/index.html").read_bytes(), "text/html")
        if p == "/mycelium":                         # the living dream→collapse view
            return self._send(200, (ROOT / "static/mycelium.html").read_bytes(), "text/html")
        if p == "/api/state":
            return self._send(200, json.dumps(state()))
        if p == "/api/events":
            return self._send(200, json.dumps(events()))
        if p == "/api/jspace":                       # J_t = R(events) — single reducer
            return self._send(200, json.dumps(R.reduce(events())))
        if p == "/api/live/events":                  # the LIVE goblin trace (browser source)
            return self._send(200, json.dumps(live_events()))
        if p == "/api/live/jspace":                  # J_t = R_live(live trace)
            return self._send(200, json.dumps(R.reduce_live(live_events())))
        if p.startswith("/static/"):
            f = ROOT / p.lstrip("/")
            if f.exists() and f.is_file():
                return self._send(200, f.read_bytes(), MIME.get(f.suffix, "application/octet-stream"))
        return self._send(404, json.dumps({"error": "not found"}))


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8787
    srv = ThreadingHTTPServer(("127.0.0.1", port), H)
    print(f"GARDEN_SCOPE serving J-space (presentation only) → http://localhost:{port}")
    print(f"  events: {len(events())} typed · state: {json.dumps(state())}")
    try: srv.serve_forever()
    except KeyboardInterrupt: print("\n↩ scope closed · nothing persisted · ΔA=0")


if __name__ == "__main__":
    main()

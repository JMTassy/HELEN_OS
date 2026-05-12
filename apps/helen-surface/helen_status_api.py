#!/usr/bin/env python3
"""helen_status_api.py — read-only local state for HELEN 2027 HOME.
Port 7001. Returns git + ledger + skill JSON. Never writes anything.
authority=false  canon=NO_SHIP  class=TOOL
"""
from flask import Flask, jsonify
import subprocess, pathlib, time

app = Flask(__name__)

SOT    = pathlib.Path.home() / "Documents/GitHub/helen_os_v1"
LEDGER = SOT / "town/ledger_v1.ndjson"
SKILLS = SOT / "oracle_town/skills"

def run(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=3, cwd=SOT)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None

@app.route("/api/status")
def status():
    branch      = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    commit      = run(["git", "rev-parse", "--short", "HEAD"])
    dirty_raw   = run(["git", "status", "--porcelain"])
    dirty       = bool(dirty_raw) if dirty_raw is not None else None

    ledger_count = None
    if LEDGER.exists():
        try:
            ledger_count = sum(1 for _ in LEDGER.open("r", encoding="utf-8", errors="ignore"))
        except Exception:
            pass

    skill_count = None
    if SKILLS.exists():
        try:
            skill_count = sum(1 for p in SKILLS.iterdir() if p.is_dir())
        except Exception:
            pass

    return jsonify({
        "branch":       branch,
        "commit":       commit,
        "dirty":        dirty,
        "ledger_count": ledger_count,
        "skill_count":  skill_count,
        "ts":           int(time.time()),
        "authority":    False,
    })

@app.route("/api/health")
def health():
    return jsonify({"ok": True, "authority": False})

@app.after_request
def cors(r):
    r.headers["Access-Control-Allow-Origin"] = "*"
    return r

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=7001, debug=False)

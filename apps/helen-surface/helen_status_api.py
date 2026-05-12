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

@app.route("/api/agents")
def agents():
    """Per-agent situational lines — one real sentence each. authority=false."""
    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"]) or "unknown"
    commit = run(["git", "rev-parse", "--short", "HEAD"]) or "?"
    dirty_raw = run(["git", "status", "--porcelain"])
    dirty_word = "dirty" if dirty_raw else "clean"

    ledger_count = 0
    mayor_count = 0
    if LEDGER.exists():
        try:
            lines = LEDGER.read_text(encoding="utf-8", errors="ignore").splitlines()
            ledger_count = len(lines)
            mayor_count = sum(1 for l in lines if '"mayor"' in l.lower() or '"MAYOR"' in l)
        except Exception:
            pass

    skill_count = 0
    if SKILLS.exists():
        try:
            skill_count = sum(1 for p in SKILLS.iterdir() if p.is_dir())
        except Exception:
            pass

    aura_count = 0
    aura_path = SOT / "temple/subsandbox/aura"
    if aura_path.exists():
        try:
            aura_count = sum(1 for _ in aura_path.iterdir())
        except Exception:
            pass

    goblin_path = SOT / "temple/subsandbox/goblin"
    goblin_count = 0
    if goblin_path.exists():
        try:
            goblin_count = sum(1 for _ in goblin_path.iterdir())
        except Exception:
            pass

    autoresearch_status = "unknown"
    ar_path = SOT / "docs/proposals"
    if ar_path.exists():
        ar_files = sorted(ar_path.glob("AUTORESEARCH*.md"), key=lambda p: p.stat().st_mtime)
        if ar_files:
            autoresearch_status = ar_files[-1].stem.replace("AUTORESEARCH_", "").replace("_", " ")

    return jsonify({
        "helen":    f"branch: {branch} · {commit} · {dirty_word}",
        "her":      f"autoresearch: {autoresearch_status} · E13 blocked",
        "hal":      f"idle · {skill_count} skills indexed · gate: pending",
        "mayor":    f"{mayor_count} ledger entries signed · {ledger_count} total",
        "chronos":  f"ledger: {ledger_count} entries · branch: {branch}",
        "aura":     f"{aura_count} temple artifacts · non-sovereign",
        "goblin":   f"{goblin_count} heap artifacts · recall active",
        "director": "last pipeline: helen-director · 3-shot Kling",
        "authority": False,
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

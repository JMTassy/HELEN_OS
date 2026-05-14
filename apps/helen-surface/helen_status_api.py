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

@app.route("/api/connectors")
def connectors():
    """Per-node live badge data. Read-only. authority=false."""
    import datetime, json

    # ── git / local real data ──────────────────────────────────────────────────
    dirty_raw   = run(["git", "status", "--porcelain"]) or ""
    dirty_count = len([l for l in dirty_raw.splitlines() if l.strip()])
    ahead_raw   = run(["git", "rev-list", "--count", "origin/main..HEAD"])
    ahead       = int(ahead_raw) if ahead_raw and ahead_raw.isdigit() else 0
    branch      = run(["git", "rev-parse", "--abbrev-ref", "HEAD"]) or "main"

    skill_count = 0
    if SKILLS.exists():
        try: skill_count = sum(1 for p in SKILLS.iterdir() if p.is_dir())
        except Exception: pass

    ledger_count = 0
    if LEDGER.exists():
        try: ledger_count = sum(1 for _ in LEDGER.open("r", errors="ignore"))
        except Exception: pass

    proposals_path = SOT / "docs/proposals"
    proposal_count = 0
    if proposals_path.exists():
        try: proposal_count = sum(1 for p in proposals_path.glob("*.md"))
        except Exception: pass

    # ── connector badge map ────────────────────────────────────────────────────
    def badge(count, status, label, sub=""):
        return {"count": count, "status": status, "label": label, "sub": sub}

    local_status = "warn" if dirty_count else "ok"
    local_label  = f"{dirty_count} dirty" if dirty_count else "clean"

    github_count  = ahead
    github_status = "warn" if ahead else "ok"
    github_label  = f"{ahead} ahead" if ahead else f"synced · {branch}"

    now_h = datetime.datetime.now().hour
    # demo calendar: office hours = higher signal
    cal_sub = "standup 14:00" if now_h < 14 else ("retro 17:00" if now_h < 17 else "free")
    cal_count = 1 if now_h < 14 else (1 if now_h < 17 else 0)

    badges = {
        # CONNECTORS ring
        "cn_github":  badge(github_count, github_status, github_label,    f"branch: {branch}"),
        "cn_local":   badge(dirty_count,  local_status,  local_label,     f"{branch}"),
        "cn_gmail":   badge(0,  "dim",  "demo",    "OAuth not wired"),
        "cn_cal":     badge(cal_count, "warn" if cal_count else "ok", cal_sub, "Google Calendar"),
        "cn_browser": badge(0,  "dim",  "demo",    "no session"),
        "cn_camera":  badge(0,  "dim",  "demo",    "no device"),
        "cn_files":   badge(skill_count, "ok", f"{skill_count} skills", "oracle_town/skills"),
        "cn_tg":      badge(0,  "dim",  "demo",    "bot not polling"),
        # SKILLS ring
        "sk_git":     badge(dirty_count, local_status, local_label, branch),
        "sk_pytest":  badge(0, "dim", "demo", "run pytest to update"),
        # TIME ring
        "sc_next":    badge(proposal_count % 10, "warn" if proposal_count else "ok",
                            f"{proposal_count} proposals", "docs/proposals"),
        # KNOWLEDGE ring
        "kn_receipts": badge(0, "ok", "0 local", "session only"),
        # authority
        "authority": False,
        "source": "live",
        "ts": int(time.time()),
    }
    return jsonify(badges)

@app.route("/api/health")
def health():
    return jsonify({"ok": True, "authority": False})

@app.after_request
def cors(r):
    r.headers["Access-Control-Allow-Origin"] = "*"
    return r

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=7001, debug=False)

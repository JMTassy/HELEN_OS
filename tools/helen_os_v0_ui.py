#!/usr/bin/env python3
"""
helen_os_v0_ui.py — NON_SOVEREIGN · NO_CLAIM
HELEN OS V0 — receipt-bound governed execution prototype.
Focus Mode: intent → HER proposal → HAL gate → confirm → action → receipt.
Witness Mode: full proof timeline + ledger tail.
Port: 5003  |  Local-only — no external APIs.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT        = Path(__file__).resolve().parent.parent
VENV_PYTHON = str(ROOT / ".venv" / "bin" / "python")
HELEN_SAY   = str(ROOT / "tools" / "helen_say.py")
LEDGER_PATH = ROOT / "town" / "ledger_v1.ndjson"
PORT        = int(os.environ.get("HELEN_V0_PORT", 5003))

GEMINI_KEY      = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
GEMINI_MODEL    = os.environ.get("HELEN_GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_ENDPOINT = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)

# ── 3 local bounded actions ───────────────────────────────────────────────────

ACTIONS = {
    "create_receipt": {
        "label": "Create Receipt",
        "icon": "📋",
        "desc": "Record an event into the HELEN ledger with a payload hash.",
    },
    "scan_receipts": {
        "label": "Scan Receipts",
        "icon": "🔎",
        "desc": "Read the last N entries from the append-only ledger.",
    },
    "show_status": {
        "label": "Show Status",
        "icon": "📡",
        "desc": "Report kernel state: ledger entry count, HEAD commit, branch.",
    },
}

# ── Local keyword router (works without any API key) ─────────────────────────

def _local_propose(intent: str) -> dict:
    lo = intent.lower()
    if any(w in lo for w in ["receipt", "record", "save", "remember", "note", "log", "create", "write"]):
        action, risk, risk_reason = "create_receipt", "LOW", "Writes only to local ledger — append-only, no side effects."
        param_label, param_value = "message", intent[:200]
        rationale = "Your intent asks to record or save — create_receipt is the minimal bounded write."
    elif any(w in lo for w in ["scan", "search", "find", "list", "read", "check receipts", "history", "past", "ledger"]):
        action, risk, risk_reason = "scan_receipts", "LOW", "Read-only ledger scan — no mutations."
        param_label, param_value = "count", "10"
        rationale = "Your intent asks to inspect past events — scan_receipts reads the append-only ledger."
    else:
        action, risk, risk_reason = "show_status", "LOW", "Read-only status report — no mutations."
        param_label, param_value = "scope", "full"
        rationale = "Default: show the current kernel state so you can see what HELEN knows."

    return {
        "summary": f"{ACTIONS[action]['label']}: {intent[:80]}",
        "action": action,
        "param_label": param_label,
        "param_value": param_value,
        "rationale": rationale,
        "hal_risk": risk,
        "hal_reason": risk_reason,
        "source": "local",
    }


# ── Gemini proposal (used when GEMINI_API_KEY is set) ────────────────────────

_PROPOSAL_SYSTEM = (
    "You are HELEN's proposal engine. Given the user's intent, propose ONE of these actions:\n"
    "  create_receipt — record an event in the local ledger\n"
    "  scan_receipts  — read recent entries from the local ledger\n"
    "  show_status    — report kernel state (ledger count, git HEAD, branch)\n\n"
    "All actions are local-only. No external APIs.\n\n"
    "Return ONLY valid JSON (no markdown fences):\n"
    "{\n"
    '  "summary": "<one sentence describing what you propose>",\n'
    '  "action": "create_receipt|scan_receipts|show_status",\n'
    '  "param_label": "<what the param represents>",\n'
    '  "param_value": "<specific value>",\n'
    '  "rationale": "<one sentence why>",\n'
    '  "hal_risk": "LOW",\n'
    '  "hal_reason": "All actions are local read/write — bounded by design."\n'
    "}"
)


def _strip_fences(text: str) -> str:
    return re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.MULTILINE).strip()


def call_gemini_proposal(intent: str) -> dict:
    if not GEMINI_KEY:
        return _local_propose(intent)
    import urllib.request, urllib.error
    payload = {
        "contents": [{"role": "user", "parts": [{"text": f"User intent: {intent}"}]}],
        "systemInstruction": {"parts": [{"text": _PROPOSAL_SYSTEM}]},
        "generationConfig": {"maxOutputTokens": 400, "temperature": 0.2},
    }
    req = urllib.request.Request(
        f"{GEMINI_ENDPOINT}?key={GEMINI_KEY}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        import urllib.request as _ur
        with _ur.urlopen(req, timeout=10) as r:
            data = json.load(r)
        raw = data["candidates"][0]["content"]["parts"][0]["text"]
        result = json.loads(_strip_fences(raw))
        result["source"] = "gemini"
        if result.get("action") not in ACTIONS:
            raise ValueError("unknown action")
        return result
    except Exception:
        fb = _local_propose(intent)
        fb["source"] = "local_fallback"
        return fb


# ── Bounded action executors ──────────────────────────────────────────────────

def _payload_hash(msg: str) -> str:
    return hashlib.sha256(msg.encode()).hexdigest()[:24]


def exec_create_receipt(param_value: str) -> dict:
    """Write a ledger entry via helen_say.py."""
    msg = param_value.strip() or "HELEN_OS_V0 manual receipt"
    try:
        out = subprocess.check_output(
            [VENV_PYTHON, HELEN_SAY, msg, "--op", "receipt"],
            cwd=str(ROOT), text=True, timeout=15, stderr=subprocess.PIPE,
        )
        rx = re.search(r"R-\d{8}-\d{4}", out)
        receipt_id = rx.group() if rx else "R-?"
        gate_match = re.search(r"Gate=(\S+)", out)
        gate = gate_match.group(1) if gate_match else "?"
        return {
            "ok": True,
            "result": f"Receipt created: {receipt_id}",
            "detail": f"gate={gate}\npayload_hash={_payload_hash(msg)}\nmessage={msg[:200]}",
            "receipt_id": receipt_id,
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "result": "Timeout", "detail": "helen_say.py did not respond in 15s."}
    except Exception as e:
        return {"ok": False, "result": "Error", "detail": str(e)}


def exec_scan_receipts(param_value: str) -> dict:
    """Read last N ledger entries."""
    try:
        n = max(1, min(int(param_value) if param_value.isdigit() else 10, 50))
    except Exception:
        n = 10
    if not LEDGER_PATH.exists():
        return {"ok": False, "result": "Ledger not found", "detail": str(LEDGER_PATH)}
    try:
        lines = LEDGER_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
        entries = []
        for ln in reversed(lines):
            if not ln.strip():
                continue
            try:
                e = json.loads(ln)
                entries.append({
                    "op": e.get("op", "—"),
                    "ts": e.get("ts", ""),
                    "payload_hash": e.get("payload_hash", "")[:20],
                    "cum_hash": e.get("cum_hash", "")[:20],
                })
            except Exception:
                pass
            if len(entries) >= n:
                break
        detail_lines = [
            f"[{e['ts'][:19]}] op={e['op']} hash={e['payload_hash']}"
            for e in entries
        ]
        return {
            "ok": True,
            "result": f"Scanned {len(entries)} ledger entries",
            "detail": "\n".join(detail_lines) or "(empty)",
            "entries": entries,
        }
    except Exception as ex:
        return {"ok": False, "result": "Scan error", "detail": str(ex)}


def exec_show_status(param_value: str) -> dict:
    """Report local kernel state."""
    try:
        ledger_count = 0
        if LEDGER_PATH.exists():
            ledger_count = sum(1 for ln in LEDGER_PATH.read_text().splitlines() if ln.strip())
        try:
            head = subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"], cwd=str(ROOT), text=True, timeout=5
            ).strip()
            branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=str(ROOT), text=True, timeout=5
            ).strip()
            ahead = subprocess.check_output(
                ["git", "rev-list", "--count", "origin/main..HEAD"], cwd=str(ROOT), text=True, timeout=5
            ).strip()
        except Exception:
            head, branch, ahead = "?", "?", "?"
        detail = (
            f"branch       : {branch}\n"
            f"HEAD         : {head}\n"
            f"ahead_origin : {ahead}\n"
            f"ledger_entries: {ledger_count}\n"
            f"ledger_path  : {LEDGER_PATH.name}\n"
            f"kernel_status: NON_SOVEREIGN\n"
            f"timestamp    : {datetime.now(timezone.utc).isoformat()}Z"
        )
        return {
            "ok": True,
            "result": f"Status: branch={branch} HEAD={head} ledger={ledger_count} entries",
            "detail": detail,
        }
    except Exception as ex:
        return {"ok": False, "result": "Status error", "detail": str(ex)}


_EXECUTORS = {
    "create_receipt": exec_create_receipt,
    "scan_receipts": exec_scan_receipts,
    "show_status": exec_show_status,
}


def execute_action(action: str, param_value: str) -> dict:
    fn = _EXECUTORS.get(action)
    if not fn:
        return {"ok": False, "result": f"Unknown action: {action}", "detail": ""}
    result = fn(param_value)
    result["ts"] = datetime.now(timezone.utc).isoformat()
    # Receipt for non-create_receipt actions (create_receipt already receipts itself)
    if action != "create_receipt":
        try:
            msg = f"HELEN_OS_V0 action={action} result={'OK' if result['ok'] else 'ERR'}: {result['result'][:120]}"
            out = subprocess.check_output(
                [VENV_PYTHON, HELEN_SAY, msg, "--op", "receipt"],
                cwd=str(ROOT), text=True, timeout=15, stderr=subprocess.PIPE,
            )
            rx = re.search(r"R-\d{8}-\d{4}", out)
            result["receipt_id"] = rx.group() if rx else "R-?"
        except Exception as e:
            result["receipt_id"] = None
            result["receipt_error"] = str(e)
    return result


def read_ledger_tail(n: int = 12) -> list:
    if not LEDGER_PATH.exists():
        return []
    entries = []
    try:
        lines = LEDGER_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
        for ln in reversed(lines[-100:]):
            if not ln.strip():
                continue
            try:
                e = json.loads(ln)
                entries.append({
                    "ts": e.get("ts", "")[:19],
                    "op": e.get("op", "—"),
                    "hash": e.get("payload_hash", "")[:14],
                    "cum": e.get("cum_hash", "")[:14],
                })
            except Exception:
                pass
            if len(entries) >= n:
                break
    except Exception:
        pass
    return entries


# ── HTML/CSS/JS ───────────────────────────────────────────────────────────────
HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>HELEN OS · V0</title>
<style>
:root{
  --bg:#08080f;--bg2:#0d0d18;--bg3:#111122;
  --border:#1a1a2e;--border2:#252540;
  --gold:#c8a84b;--gold-a:rgba(200,168,75,.14);--gold-b:rgba(200,168,75,.22);
  --green:#4caf82;--green-a:rgba(76,175,130,.12);
  --red:#e05c5c;--red-a:rgba(224,92,92,.12);
  --blue:#5b8def;--blue-a:rgba(91,141,239,.12);
  --amber:#f0a030;--amber-a:rgba(240,160,48,.1);
  --text:#c8c8d8;--dim:#6a6a8a;--faint:#2a2a42;
  --mono:'JetBrains Mono','Fira Code','SF Mono',monospace;
  --r:6px;
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow:hidden}
body{background:var(--bg);color:var(--text);font-family:var(--mono);font-size:13px;display:flex;flex-direction:column}

/* topbar */
#bar{height:46px;flex-shrink:0;display:flex;align-items:center;justify-content:space-between;padding:0 20px;background:var(--bg2);border-bottom:1px solid var(--border)}
.brand{color:var(--gold);font-size:13px;letter-spacing:3px;text-transform:uppercase}
.brand em{color:var(--dim);font-style:normal;font-size:11px;letter-spacing:1px;margin-left:8px}
.toggle{display:flex;gap:2px;background:var(--bg3);border:1px solid var(--border);border-radius:var(--r);padding:2px}
.tbtn{padding:4px 16px;border:none;border-radius:4px;background:transparent;color:var(--dim);cursor:pointer;font-family:var(--mono);font-size:10px;letter-spacing:2px;text-transform:uppercase;transition:all 180ms}
.tbtn.on{background:var(--border2);color:var(--text)}
.pills{display:flex;gap:8px;align-items:center}
.pill{padding:2px 9px;border-radius:10px;font-size:10px;letter-spacing:.5px}
.pill-gate{background:var(--green-a);color:var(--green);border:1px solid rgba(76,175,130,.2)}
.pill-gate.warn{background:var(--amber-a);color:var(--amber);border-color:rgba(240,160,48,.2)}
.pill-gate.block{background:var(--red-a);color:var(--red);border-color:rgba(224,92,92,.2)}
.pill-ledger{background:var(--gold-a);color:var(--gold);border:1px solid rgba(200,168,75,.18)}
.pill-ns{background:var(--blue-a);color:var(--blue);border:1px solid rgba(91,141,239,.18)}

/* layouts */
#focus,#witness{flex:1;display:flex;overflow:hidden}
#witness{display:none}

/* panels */
.pane{display:flex;flex-direction:column;border-right:1px solid var(--border);overflow:hidden}
.pane:last-child{border-right:none}
.ph{height:36px;flex-shrink:0;display:flex;align-items:center;gap:8px;padding:0 14px;border-bottom:1px solid var(--border);font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--dim)}
.dot{width:6px;height:6px;border-radius:50%;flex-shrink:0}
.dg{background:var(--gold)}.dgr{background:var(--green)}.db{background:var(--blue)}
.pb{flex:1;overflow-y:auto;padding:14px}
.pb::-webkit-scrollbar{width:3px}
.pb::-webkit-scrollbar-thumb{background:var(--border2)}

/* intent panel */
#pane-intent{width:260px}
#intent-in{width:100%;background:var(--bg3);border:1px solid var(--border);border-radius:var(--r);color:var(--text);font-family:var(--mono);font-size:12px;padding:10px;resize:none;outline:none;min-height:90px;transition:border-color 180ms;line-height:1.55}
#intent-in:focus{border-color:var(--gold)}
#intent-in::placeholder{color:var(--faint)}
#propose-btn{width:100%;margin-top:9px;padding:9px;background:var(--gold-a);border:1px solid var(--gold);color:var(--gold);font-family:var(--mono);font-size:11px;letter-spacing:1.5px;text-transform:uppercase;cursor:pointer;border-radius:var(--r);transition:all 180ms}
#propose-btn:hover:not(:disabled){background:var(--gold-b)}
#propose-btn:disabled{opacity:.35;cursor:default}
.hint{margin-top:14px;font-size:11px;color:var(--faint);line-height:1.7}
.hint strong{color:var(--dim)}
.action-list{margin-top:16px}
.al-title{font-size:9px;letter-spacing:2px;text-transform:uppercase;color:var(--faint);margin-bottom:8px}
.ai{display:flex;gap:8px;align-items:center;padding:6px 8px;border-radius:4px;margin-bottom:4px;border:1px solid var(--border)}
.ai-icon{font-size:13px}
.ai-name{font-size:11px;color:var(--text);margin-bottom:1px}
.ai-desc{font-size:10px;color:var(--dim)}

/* proposal panel */
#pane-proposal{flex:1}
.card{background:var(--bg3);border:1px solid var(--border);border-radius:var(--r);padding:14px;margin-bottom:10px}
.card.c-pass{border-color:rgba(76,175,130,.35)}
.card.c-warn{border-color:rgba(224,92,92,.35)}
.clabel{font-size:9px;letter-spacing:2px;text-transform:uppercase;color:var(--dim);margin-bottom:5px}
.cval{font-size:12px;color:var(--text);line-height:1.55;margin-bottom:10px}
.action-box{display:flex;align-items:center;gap:9px;background:var(--bg);border:1px solid var(--border);border-radius:4px;padding:8px 10px;margin-bottom:9px}
.ab-icon{font-size:16px}
.ab-name{font-size:12px;color:var(--gold);margin-bottom:2px}
.ab-param{font-size:10px;color:var(--dim);word-break:break-all}
.hal-box{display:flex;align-items:flex-start;gap:7px;padding:7px 10px;border-radius:4px;font-size:11px;margin-bottom:11px;line-height:1.45}
.hal-low{background:var(--green-a);color:var(--green);border:1px solid rgba(76,175,130,.2)}
.hal-med{background:var(--amber-a);color:var(--amber);border:1px solid rgba(240,160,48,.2)}
.hal-hi{background:var(--red-a);color:var(--red);border:1px solid rgba(224,92,92,.2)}
.crows{display:flex;gap:7px}
#confirm-btn{flex:1;padding:9px;background:var(--green-a);border:1px solid var(--green);color:var(--green);font-family:var(--mono);font-size:11px;letter-spacing:1.5px;text-transform:uppercase;cursor:pointer;border-radius:var(--r);transition:all 180ms}
#confirm-btn:hover:not(:disabled){background:rgba(76,175,130,.22)}
#confirm-btn:disabled{opacity:.35;cursor:default}
#reject-btn{padding:9px 14px;background:transparent;border:1px solid var(--border);color:var(--dim);font-family:var(--mono);font-size:10px;cursor:pointer;border-radius:var(--r);transition:all 180ms}
#reject-btn:hover{border-color:var(--red);color:var(--red)}
.result-card{background:var(--bg3);border:1px solid var(--border);border-radius:var(--r);padding:12px;margin-top:10px}
.result-ok{border-color:rgba(76,175,130,.35)}
.result-err{border-color:rgba(224,92,92,.35)}
.result-line{font-size:12px;margin-bottom:7px}
.result-detail{font-size:10px;color:var(--dim);white-space:pre-wrap;word-break:break-all;max-height:160px;overflow-y:auto;background:var(--bg);padding:7px;border-radius:4px;border:1px solid var(--border)}
.receipt-chip{display:inline-flex;align-items:center;gap:6px;margin-top:8px;padding:5px 10px;background:var(--gold-a);border:1px solid rgba(200,168,75,.2);border-radius:4px;font-size:11px;color:var(--gold)}
.receipt-chip strong{font-size:12px}
.empty{color:var(--faint);font-size:12px;line-height:1.8;padding:6px 0}
.spin{animation:sp 1s linear infinite;display:inline-block}
@keyframes sp{to{transform:rotate(360deg)}}
.thinking{color:var(--gold);font-size:12px}

/* witness strip */
#pane-strip{width:280px}
.te{display:flex;gap:9px;margin-bottom:12px;position:relative}
.te:not(:last-child)::before{content:'';position:absolute;left:9px;top:20px;width:1px;height:calc(100% + 2px);background:var(--border)}
.te-dot{width:19px;height:19px;border-radius:50%;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:9px;font-weight:700;border:1px solid;margin-top:1px}
.td-i{background:var(--blue-a);border-color:var(--blue);color:var(--blue)}
.td-p{background:var(--gold-a);border-color:var(--gold);color:var(--gold)}
.td-h{background:var(--green-a);border-color:var(--green);color:var(--green)}
.td-e{background:var(--blue-a);border-color:var(--blue);color:var(--blue)}
.td-r{background:var(--gold-a);border-color:var(--gold);color:var(--gold)}
.td-x{background:var(--red-a);border-color:var(--red);color:var(--red)}
.te-body{flex:1}
.te-type{font-size:9px;letter-spacing:1.5px;text-transform:uppercase;color:var(--dim)}
.te-val{font-size:11px;color:var(--text);margin-top:2px;word-break:break-word;line-height:1.4}
.te-ts{font-size:9px;color:var(--faint);margin-top:2px}

/* witness full layout */
#w-left{flex:1}
#w-right{width:320px;border-left:1px solid var(--border)}
.lr{display:flex;flex-direction:column;gap:3px;padding:7px 10px;border-bottom:1px solid var(--border);font-size:10px}
.lr-op{color:var(--gold)}
.lr-h{color:var(--dim);font-size:9px;word-break:break-all}
.lr-ts{color:var(--faint);font-size:9px}

/* status bar */
#sbar{height:24px;flex-shrink:0;background:var(--bg2);border-top:1px solid var(--border);display:flex;align-items:center;padding:0 16px;gap:16px;font-size:10px;color:var(--faint)}
#sbar span{color:var(--dim)}
</style>
</head>
<body>
<div id="bar">
  <div class="brand">HELEN OS <em>V0</em></div>
  <div class="toggle">
    <button class="tbtn on" id="btn-f" onclick="setMode('focus')">Focus</button>
    <button class="tbtn"    id="btn-w" onclick="setMode('witness')">Witness</button>
  </div>
  <div class="pills">
    <span class="pill pill-gate" id="pill-gate">Gate Clear</span>
    <span class="pill pill-ledger" id="pill-ledger">Ledger</span>
    <span class="pill pill-ns">NON_SOVEREIGN</span>
  </div>
</div>

<!-- FOCUS -->
<div id="focus">
  <!-- Intent -->
  <div class="pane" id="pane-intent">
    <div class="ph"><span class="dot dg"></span>Intent</div>
    <div class="pb">
      <textarea id="intent-in" rows="4"
        placeholder="What do you want HELEN to do?&#10;&#10;e.g. Record this session start&#10;e.g. Scan recent receipts&#10;e.g. Show system status"></textarea>
      <button id="propose-btn" onclick="propose()">▶ Propose</button>
      <div class="hint">
        <strong>HELEN suggests.</strong><br>
        You decide.<br>
        Everything is recorded.<br><br>
        ⌘↵ to propose
      </div>
      <div class="action-list">
        <div class="al-title">Bounded actions</div>
        <div class="ai"><span class="ai-icon">📋</span><div><div class="ai-name">create_receipt</div><div class="ai-desc">Write event to ledger</div></div></div>
        <div class="ai"><span class="ai-icon">🔎</span><div><div class="ai-name">scan_receipts</div><div class="ai-desc">Read ledger tail</div></div></div>
        <div class="ai"><span class="ai-icon">📡</span><div><div class="ai-name">show_status</div><div class="ai-desc">Kernel state report</div></div></div>
      </div>
    </div>
  </div>

  <!-- Proposal + Execution -->
  <div class="pane" id="pane-proposal">
    <div class="ph"><span class="dot dg"></span>Proposal · HAL Gate · Execution</div>
    <div class="pb">
      <div id="prop-area">
        <div class="empty">
          Awaiting intent.<br><br>
          HER will propose one bounded action.<br>
          HAL will assess risk.<br>
          You confirm before anything executes.
        </div>
      </div>
    </div>
  </div>

  <!-- Witness strip -->
  <div class="pane" id="pane-strip">
    <div class="ph"><span class="dot dgr"></span>Witness Strip</div>
    <div class="pb" id="strip-body">
      <div class="empty">No events yet.</div>
    </div>
  </div>
</div>

<!-- WITNESS -->
<div id="witness">
  <div class="pane" id="w-left">
    <div class="ph"><span class="dot dgr"></span>Full Event Timeline</div>
    <div class="pb" id="wt-body">
      <div class="empty">No events yet — run a governed action in Focus Mode.</div>
    </div>
  </div>
  <div class="pane" id="w-right">
    <div class="ph"><span class="dot dg"></span>Ledger Tail</div>
    <div class="pb" style="padding:0" id="ledger-body">
      <div class="empty" style="padding:14px">Loading…</div>
    </div>
  </div>
</div>

<div id="sbar">
  <span id="sb-events">0 events</span>
  <span id="sb-receipts">0 receipts</span>
  <span id="sb-ts">—</span>
</div>

<script>
let mode='focus', events=[], pending=null, busy=false, receiptCount=0;

// ── mode ──────────────────────────────────────────────────────────────────────
function setMode(m){
  mode=m;
  document.getElementById('btn-f').classList.toggle('on',m==='focus');
  document.getElementById('btn-w').classList.toggle('on',m==='witness');
  document.getElementById('focus').style.display=m==='focus'?'flex':'none';
  document.getElementById('witness').style.display=m==='witness'?'flex':'none';
  if(m==='witness'){renderWitness();loadLedger();}
}

// ── propose ───────────────────────────────────────────────────────────────────
async function propose(){
  const intent=document.getElementById('intent-in').value.trim();
  if(!intent||busy)return;
  busy=true; setBusy(true);
  propArea('<div class="thinking"><span class="spin">⟳</span> HER is proposing…</div>');
  pushEv('intent',intent,null);
  try{
    const d=await post('/api/propose',{intent});
    if(d.error){propArea(`<div class="empty" style="color:var(--red)">${esc(d.error)}</div>`);done();return;}
    pending=d; pushEv('proposal',d.summary,d); renderCard(d);
  }catch(e){propArea(`<div class="empty" style="color:var(--red)">Error: ${esc(e.message)}</div>`);done();}
}

// ── render proposal card ──────────────────────────────────────────────────────
function renderCard(p){
  const icons={create_receipt:'📋',scan_receipts:'🔎',show_status:'📡'};
  const halCls=p.hal_risk==='LOW'?'hal-low':p.hal_risk==='HIGH'?'hal-hi':'hal-med';
  const halIcon=p.hal_risk==='LOW'?'✓ LOW':p.hal_risk==='HIGH'?'✗ HIGH':'⚠ MEDIUM';
  const ok=p.hal_risk!=='HIGH';
  propArea(`
    <div class="card ${ok?'c-pass':'c-warn'}">
      <div class="clabel">HER Proposal</div>
      <div class="cval">${esc(p.summary)}</div>
      <div class="action-box">
        <span class="ab-icon">${icons[p.action]||'⚡'}</span>
        <div>
          <div class="ab-name">${esc(p.action)}</div>
          <div class="ab-param">${esc(p.param_label)}: ${esc(p.param_value)}</div>
        </div>
      </div>
      <div class="hal-box ${halCls}">
        <strong>HAL [${halIcon}]</strong>&nbsp;${esc(p.hal_reason)}
      </div>
      <div class="clabel">Rationale</div>
      <div class="cval" style="font-size:11px;color:var(--dim);margin-bottom:13px">${esc(p.rationale)}</div>
      <div class="crows">
        <button id="confirm-btn" onclick="confirmExec()" ${ok?'':'disabled'}>
          ${ok?'✓ Confirm &amp; Execute':'✗ Blocked'}
        </button>
        <button id="reject-btn" onclick="reject()">Reject</button>
      </div>
      ${!ok?'<div style="margin-top:7px;font-size:10px;color:var(--red)">HIGH risk — blocked. Reject and rephrase.</div>':''}
    </div>
    <div id="res-area"></div>
  `);
  setGate(p.hal_risk); done();
}

// ── confirm + execute ─────────────────────────────────────────────────────────
async function confirmExec(){
  if(!pending||busy)return;
  busy=true;
  document.getElementById('confirm-btn').disabled=true;
  document.getElementById('reject-btn').disabled=true;
  const ra=document.getElementById('res-area');
  ra.innerHTML='<div class="thinking" style="margin-top:10px"><span class="spin">⟳</span> Executing…</div>';
  pushEv('hal',`HAL ${pending.hal_risk} → executing`,pending);
  try{
    const d=await post('/api/execute',{action:pending.action,param_value:pending.param_value});
    pushEv('execution',d.result||d.error||'?',d);
    if(d.receipt_id){pushEv('receipt',d.receipt_id,{receipt_id:d.receipt_id});receiptCount++;setLedgerPill(d.receipt_id);}
    renderResult(ra,d); done(); pending=null;
  }catch(e){
    ra.innerHTML=`<div class="result-card result-err"><div class="result-line" style="color:var(--red)">Error: ${esc(e.message)}</div></div>`;
    done();
  }
}

function renderResult(el,d){
  const chip=d.receipt_id
    ?`<div class="receipt-chip">📋 Receipt: <strong>${esc(d.receipt_id)}</strong></div>`
    :(d.receipt_error?`<div style="margin-top:8px;font-size:10px;color:var(--red)">Receipt error: ${esc(d.receipt_error)}</div>`:'');
  el.innerHTML=`
    <div class="result-card ${d.ok?'result-ok':'result-err'}">
      <div class="result-line" style="color:${d.ok?'var(--green)':'var(--red)'}">
        ${d.ok?'✓':'✗'} ${esc(d.result||'?')}
      </div>
      ${d.detail?`<div class="result-detail">${esc(d.detail)}</div>`:''}
      ${chip}
    </div>`;
}

function reject(){
  pending=null;
  pushEv('reject','Operator rejected proposal',null);
  propArea('<div class="empty" style="color:var(--dim)">Rejected.<br><br>Enter a new intent above.</div>');
  setGate('CLEAR');
}

// ── witness strip ─────────────────────────────────────────────────────────────
const DOTS={intent:'td-i',proposal:'td-p',hal:'td-h',execution:'td-e',receipt:'td-r',reject:'td-x'};
const ICONS={intent:'I',proposal:'P',hal:'H',execution:'E',receipt:'R',reject:'✗'};
function renderStrip(){
  const el=document.getElementById('strip-body');
  if(!events.length){el.innerHTML='<div class="empty">No events yet.</div>';return;}
  el.innerHTML=events.slice().reverse().map(e=>`
    <div class="te">
      <div class="te-dot ${DOTS[e.type]||'td-i'}">${ICONS[e.type]||'·'}</div>
      <div class="te-body">
        <div class="te-type">${e.type}</div>
        <div class="te-val">${esc(e.label.length>70?e.label.slice(0,70)+'…':e.label)}</div>
        <div class="te-ts">${e.ts}</div>
      </div>
    </div>`).join('');
}
function renderWitness(){
  const el=document.getElementById('wt-body');
  if(!events.length){el.innerHTML='<div class="empty">No events yet — run a governed action in Focus Mode.</div>';return;}
  el.innerHTML=events.slice().reverse().map(e=>{
    const det=e.data?`<div class="result-detail" style="margin-top:5px;max-height:70px">${esc(JSON.stringify(e.data).slice(0,400))}</div>`:'';
    return `
    <div class="te">
      <div class="te-dot ${DOTS[e.type]||'td-i'}">${ICONS[e.type]||'·'}</div>
      <div class="te-body">
        <div class="te-type">${e.type}</div>
        <div class="te-val">${esc(e.label)}</div>
        ${det}
        <div class="te-ts">${e.ts}</div>
      </div>
    </div>`}).join('');
}
async function loadLedger(){
  try{
    const d=await fetch('/api/ledger').then(r=>r.json());
    const el=document.getElementById('ledger-body');
    if(!d.entries||!d.entries.length){el.innerHTML='<div class="empty" style="padding:14px">Empty.</div>';return;}
    el.innerHTML=d.entries.map(e=>`
      <div class="lr">
        <div class="lr-op">${esc(e.op)}</div>
        <div class="lr-h">hash: ${esc(e.hash)} · cum: ${esc(e.cum)}</div>
        <div class="lr-ts">${esc(e.ts)}</div>
      </div>`).join('');
  }catch(e){document.getElementById('ledger-body').innerHTML='<div class="empty" style="padding:14px;color:var(--red)">Error.</div>';}
}

// ── helpers ───────────────────────────────────────────────────────────────────
function pushEv(type,label,data){
  events.push({type,label,data,ts:new Date().toLocaleTimeString()});
  renderStrip();
  document.getElementById('sb-events').textContent=`${events.length} event${events.length===1?'':'s'}`;
  document.getElementById('sb-receipts').textContent=`${receiptCount} receipt${receiptCount===1?'':'s'}`;
  document.getElementById('sb-ts').textContent=new Date().toLocaleTimeString();
}
function propArea(html){document.getElementById('prop-area').innerHTML=html;}
function setBusy(v){document.getElementById('propose-btn').disabled=v;}
function done(){busy=false;setBusy(false);}
function setGate(risk){
  const p=document.getElementById('pill-gate');
  p.className='pill pill-gate';
  if(risk==='LOW'||risk==='CLEAR'){p.textContent='Gate Clear';}
  else if(risk==='MEDIUM'){p.textContent='Gate Warn';p.classList.add('warn');}
  else if(risk==='HIGH'){p.textContent='Gate Block';p.classList.add('block');}
}
function setLedgerPill(id){document.getElementById('pill-ledger').textContent=id||'Ledger';}
function esc(s){if(s==null)return'';return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
async function post(url,body){const r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});return r.json();}

document.addEventListener('DOMContentLoaded',()=>{
  document.getElementById('intent-in').addEventListener('keydown',e=>{if(e.key==='Enter'&&(e.metaKey||e.ctrlKey))propose();});
});
</script>
</body>
</html>
"""  # noqa: E501


# ── HTTP handler ──────────────────────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # silence access log
        pass

    def _json(self, data: dict, status: int = 200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _html(self, html: str):
        body = html.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._html(HTML)
        elif self.path == "/api/ledger":
            self._json({"entries": read_ledger_tail(12)})
        elif self.path == "/v1/status":
            result = execute_action("show_status", "full")
            self._json({
                "artifact_type": "HELEN_OS_V0_STATUS",
                "authority": "NON_SOVEREIGN",
                "status": "NO_CLAIM",
                "ok": result["ok"],
                "detail": result["detail"],
                "receipt_id": result.get("receipt_id"),
                "ts": result.get("ts", datetime.now(timezone.utc).isoformat()),
            })
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}")

        if self.path == "/api/propose":
            intent = body.get("intent", "").strip()
            if not intent:
                self._json({"error": "No intent."}, 400)
                return
            self._json(call_gemini_proposal(intent))

        elif self.path == "/api/execute":
            action = body.get("action", "")
            param_value = body.get("param_value", "")
            if action not in ACTIONS:
                self._json({"ok": False, "result": f"Unknown action: {action}", "detail": ""})
                return
            self._json(execute_action(action, param_value))

        else:
            self.send_response(404)
            self.end_headers()


def main():
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    has_gemini = bool(GEMINI_KEY)
    print(f"HELEN OS V0  →  http://localhost:{PORT}")
    print(f"proposal engine: {'gemini (' + GEMINI_MODEL + ')' if has_gemini else 'local keyword router'}")
    print(f"status endpoint: http://localhost:{PORT}/v1/status")
    print("NON_SOVEREIGN · Focus + Witness · local-only bounded actions")
    server.serve_forever()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
helen_os_v0_ui.py — NON_SOVEREIGN · NO_CLAIM
HELEN OS V0 — governed AI-native interface.
Focus Mode: intent → proposal → HAL gate → confirm → execute → receipt.
Witness Mode: full timeline proof.
Port: 5003
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENV_PYTHON = str(ROOT / ".venv" / "bin" / "python")
HELEN_SAY = str(ROOT / "tools" / "helen_say.py")
LEDGER_PATH = ROOT / "town" / "ledger_v1.ndjson"
FIREWALL_TOOL = str(ROOT / "tools" / "hyperstition_firewall_v0.py")
PORT = int(os.environ.get("HELEN_V0_PORT", 5003))

GEMINI_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
GEMINI_MODEL = os.environ.get("HELEN_GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

# ── Bounded action registry ────────────────────────────────────────────────────
ALLOWED_ACTIONS = {
    "web_search": {
        "label": "Web Search",
        "description": "Search the web for information",
        "icon": "🔍",
        "param": "query",
    },
    "open_url": {
        "label": "Open URL",
        "description": "Open a URL in the browser",
        "icon": "🌐",
        "param": "url",
    },
    "read_file": {
        "label": "Read File",
        "description": "Read a file from the project",
        "icon": "📄",
        "param": "path",
    },
    "run_firewall": {
        "label": "Hyperstition Firewall",
        "description": "Run symbolic content through HAL_GOBLIN filter",
        "icon": "🛡",
        "param": "text",
    },
    "write_note": {
        "label": "Write Note",
        "description": "Save a note to artifacts/notes/",
        "icon": "📝",
        "param": "content",
    },
}


# ── LLM helpers ───────────────────────────────────────────────────────────────
PROPOSAL_SYSTEM = (
    "You are HELEN's proposal engine. Given the user's intent, you must:\n"
    "1. Identify which single bounded action best serves the intent.\n"
    "2. Propose a specific action with precise parameters.\n"
    "3. Explain why in one sentence.\n"
    "4. Assess HAL risk (LOW/MEDIUM/HIGH).\n\n"
    "Allowed actions: web_search, open_url, read_file, run_firewall, write_note.\n\n"
    "Return ONLY valid JSON — no markdown, no prose:\n"
    "{\n"
    '  "summary": "<one-sentence proposal>",\n'
    '  "action": "<action_key>",\n'
    '  "param_label": "<what the param represents>",\n'
    '  "param_value": "<the specific value>",\n'
    '  "rationale": "<why this action serves the intent>",\n'
    '  "hal_risk": "LOW" | "MEDIUM" | "HIGH",\n'
    '  "hal_reason": "<why this risk level>"\n'
    "}"
)


def _strip_fences(text: str) -> str:
    return re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.MULTILINE).strip()


def call_gemini_proposal(intent: str) -> dict:
    if not GEMINI_KEY:
        return _fallback_proposal(intent)
    payload = {
        "contents": [{"role": "user", "parts": [{"text": f"User intent: {intent}"}]}],
        "systemInstruction": {"parts": [{"text": PROPOSAL_SYSTEM}]},
        "generationConfig": {"maxOutputTokens": 512, "temperature": 0.3},
    }
    req = urllib.request.Request(
        f"{GEMINI_ENDPOINT}?key={GEMINI_KEY}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.load(r)
        raw = data["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(_strip_fences(raw))
    except Exception:
        return _fallback_proposal(intent)


def _fallback_proposal(intent: str) -> dict:
    return {
        "summary": f"Search the web for: {intent[:60]}",
        "action": "web_search",
        "param_label": "query",
        "param_value": intent[:120],
        "rationale": "Web search is the default bounded action for open-ended queries.",
        "hal_risk": "LOW",
        "hal_reason": "Web search is read-only and bounded.",
    }


# ── Bounded execution ─────────────────────────────────────────────────────────
def execute_action(action: str, param_value: str) -> dict:
    ts = datetime.utcnow().isoformat()
    try:
        if action == "web_search":
            q = urllib.parse.quote_plus(param_value[:200])
            result_text = f"Search executed: https://duckduckgo.com/?q={q}"
            detail = f"DuckDuckGo search URL generated for: {param_value[:100]}"
        elif action == "open_url":
            if not param_value.startswith(("http://", "https://")):
                return {"ok": False, "error": "URL must start with http:// or https://", "ts": ts}
            subprocess.Popen(["open", param_value])
            result_text = f"Opened: {param_value}"
            detail = "Browser launched via system open."
        elif action == "read_file":
            p = ROOT / param_value.lstrip("/")
            if not p.resolve().is_relative_to(ROOT):
                return {"ok": False, "error": "Path outside project root — blocked.", "ts": ts}
            if not p.exists():
                return {"ok": False, "error": f"File not found: {param_value}", "ts": ts}
            content = p.read_text(encoding="utf-8", errors="replace")[:2000]
            result_text = f"Read {p.name} ({len(content)} chars)"
            detail = content
        elif action == "run_firewall":
            import tempfile
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
                f.write(param_value)
                tmp = f.name
            try:
                out = subprocess.check_output(
                    [VENV_PYTHON, FIREWALL_TOOL, tmp], text=True, timeout=15
                )
                fw = json.loads(out)
                risk = fw.get("hal_goblin_flags", {}).get("risk_level", "?")
                verdict = fw.get("hal_goblin_flags", {}).get("verdict", "?")
                result_text = f"Firewall: risk={risk} verdict={verdict}"
                detail = json.dumps(fw.get("hal_goblin_flags", {}), indent=2)
            finally:
                Path(tmp).unlink(missing_ok=True)
        elif action == "write_note":
            notes_dir = ROOT / "artifacts" / "notes"
            notes_dir.mkdir(parents=True, exist_ok=True)
            fname = notes_dir / f"note_{int(time.time())}.txt"
            fname.write_text(param_value, encoding="utf-8")
            result_text = f"Note saved: {fname.name}"
            detail = param_value[:500]
        else:
            return {"ok": False, "error": f"Unknown action: {action}", "ts": ts}

        return {"ok": True, "result": result_text, "detail": detail, "ts": ts}

    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "Action timed out.", "ts": ts}
    except Exception as e:
        return {"ok": False, "error": str(e), "ts": ts}


def emit_receipt(msg: str) -> dict:
    try:
        out = subprocess.check_output(
            [VENV_PYTHON, HELEN_SAY, msg, "--op", "receipt"],
            cwd=str(ROOT), text=True, timeout=15, stderr=subprocess.PIPE
        )
        rx = re.search(r"R-\d{8}-\d{4}", out)
        return {"ok": True, "receipt_id": rx.group() if rx else "R-?", "raw": out.strip()}
    except Exception as e:
        return {"ok": False, "error": str(e), "receipt_id": None}


def read_ledger_tail(n: int = 8) -> list:
    if not LEDGER_PATH.exists():
        return []
    try:
        lines = LEDGER_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
        entries = []
        for ln in reversed(lines[-50:]):
            if not ln.strip():
                continue
            try:
                e = json.loads(ln)
                entries.append({
                    "ts": e.get("ts", ""),
                    "op": e.get("op", ""),
                    "hash": e.get("payload_hash", "")[:12],
                    "cum": e.get("cum_hash", "")[:12],
                })
            except Exception:
                pass
            if len(entries) >= n:
                break
        return entries
    except Exception:
        return []


# ── HTML ─────────────────────────────────────────────────────────────────────
HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>HELEN OS V0</title>
<style>
  :root {
    --bg: #0a0a0f;
    --bg-panel: #0f0f1a;
    --bg-card: #13131f;
    --border: #1e1e2e;
    --border-active: #3a3a5c;
    --gold: #c8a84b;
    --gold-dim: rgba(200,168,75,0.15);
    --green: #4caf82;
    --green-dim: rgba(76,175,130,0.12);
    --red: #e05c5c;
    --red-dim: rgba(224,92,92,0.12);
    --blue: #5b8def;
    --blue-dim: rgba(91,141,239,0.12);
    --text: #d0d0e0;
    --text-dim: #7a7a9a;
    --text-faint: #3a3a5a;
    --mono: 'JetBrains Mono', 'Fira Code', 'SF Mono', monospace;
    --radius: 6px;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--mono);
    font-size: 13px;
    height: 100vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }

  /* ── Top bar ── */
  #topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 20px;
    border-bottom: 1px solid var(--border);
    background: var(--bg-panel);
    flex-shrink: 0;
    height: 48px;
  }
  .brand { color: var(--gold); font-size: 14px; letter-spacing: 3px; text-transform: uppercase; }
  .brand span { color: var(--text-dim); font-size: 11px; letter-spacing: 1px; margin-left: 8px; }
  .mode-toggle { display: flex; gap: 2px; background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 2px; }
  .mode-btn {
    padding: 4px 14px; border: none; border-radius: 4px;
    background: transparent; color: var(--text-dim);
    cursor: pointer; font-family: var(--mono); font-size: 11px;
    letter-spacing: 1px; text-transform: uppercase; transition: all 200ms;
  }
  .mode-btn.active { background: var(--border-active); color: var(--text); }
  .status-bar { font-size: 11px; color: var(--text-dim); display: flex; gap: 12px; }
  .pill { padding: 2px 8px; border-radius: 10px; font-size: 10px; letter-spacing: 0.5px; }
  .pill-gate { background: var(--green-dim); color: var(--green); border: 1px solid rgba(76,175,130,0.2); }
  .pill-ledger { background: var(--gold-dim); color: var(--gold); border: 1px solid rgba(200,168,75,0.2); }
  .pill-ns { background: var(--blue-dim); color: var(--blue); border: 1px solid rgba(91,141,239,0.2); }

  /* ── Main layout ── */
  #main { flex: 1; display: flex; overflow: hidden; }

  /* ── Panels ── */
  .panel { border-right: 1px solid var(--border); display: flex; flex-direction: column; overflow: hidden; }
  .panel:last-child { border-right: none; }
  .panel-header {
    padding: 10px 16px; border-bottom: 1px solid var(--border);
    font-size: 10px; letter-spacing: 2px; text-transform: uppercase;
    color: var(--text-dim); flex-shrink: 0;
    display: flex; align-items: center; gap: 8px;
  }
  .panel-header .dot { width: 6px; height: 6px; border-radius: 50%; }
  .dot-gold { background: var(--gold); }
  .dot-green { background: var(--green); }
  .dot-blue { background: var(--blue); }
  .dot-red { background: var(--red); }
  .panel-body { flex: 1; overflow-y: auto; padding: 16px; }
  .panel-body::-webkit-scrollbar { width: 4px; }
  .panel-body::-webkit-scrollbar-track { background: transparent; }
  .panel-body::-webkit-scrollbar-thumb { background: var(--border-active); border-radius: 2px; }

  /* ── FOCUS mode layout ── */
  #focus-layout { display: flex; width: 100%; height: 100%; }
  #panel-intent { width: 280px; }
  #panel-proposal { flex: 1; }
  #panel-witness-strip { width: 300px; border-left: 1px solid var(--border); border-right: none; }

  /* ── WITNESS mode layout ── */
  #witness-layout { display: flex; width: 100%; height: 100%; display: none; }
  #panel-timeline { flex: 1; }
  #panel-ledger { width: 340px; border-left: 1px solid var(--border); }

  /* ── Intent panel ── */
  #intent-input {
    width: 100%; background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--radius); color: var(--text); font-family: var(--mono);
    font-size: 13px; padding: 12px; resize: none; outline: none;
    transition: border-color 200ms; min-height: 80px;
  }
  #intent-input:focus { border-color: var(--gold); }
  #intent-input::placeholder { color: var(--text-faint); }
  #propose-btn {
    width: 100%; margin-top: 10px; padding: 10px;
    background: var(--gold-dim); border: 1px solid var(--gold);
    color: var(--gold); font-family: var(--mono); font-size: 12px;
    letter-spacing: 1px; text-transform: uppercase;
    cursor: pointer; border-radius: var(--radius); transition: all 200ms;
  }
  #propose-btn:hover { background: rgba(200,168,75,0.25); }
  #propose-btn:disabled { opacity: 0.4; cursor: default; }
  .intent-hint { margin-top: 12px; font-size: 11px; color: var(--text-faint); line-height: 1.6; }
  .intent-hint strong { color: var(--text-dim); }

  /* ── Proposal card ── */
  #proposal-area { min-height: 200px; }
  .proposal-card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 16px; margin-bottom: 12px;
  }
  .proposal-card.hal-pass { border-color: rgba(76,175,130,0.4); }
  .proposal-card.hal-warn { border-color: rgba(224,92,92,0.4); }
  .prop-label { font-size: 10px; letter-spacing: 1.5px; color: var(--text-dim); text-transform: uppercase; margin-bottom: 6px; }
  .prop-value { font-size: 13px; color: var(--text); margin-bottom: 12px; line-height: 1.5; }
  .prop-action {
    display: flex; align-items: center; gap: 8px;
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 4px; padding: 8px 12px; margin-bottom: 10px;
  }
  .prop-action-icon { font-size: 16px; }
  .prop-action-name { color: var(--gold); font-size: 12px; letter-spacing: 0.5px; }
  .prop-action-param { color: var(--text-dim); font-size: 11px; margin-top: 2px; word-break: break-all; }
  .hal-verdict {
    display: flex; align-items: center; gap: 8px;
    padding: 8px 12px; border-radius: 4px; font-size: 11px; margin-bottom: 12px;
  }
  .hal-pass-bg { background: var(--green-dim); color: var(--green); border: 1px solid rgba(76,175,130,0.2); }
  .hal-warn-bg { background: var(--red-dim); color: var(--red); border: 1px solid rgba(224,92,92,0.2); }
  .hal-medium-bg { background: rgba(255,165,0,0.1); color: #ffa500; border: 1px solid rgba(255,165,0,0.2); }
  .confirm-row { display: flex; gap: 8px; }
  #confirm-btn {
    flex: 1; padding: 10px; background: var(--green-dim); border: 1px solid var(--green);
    color: var(--green); font-family: var(--mono); font-size: 12px;
    letter-spacing: 1px; text-transform: uppercase; cursor: pointer;
    border-radius: var(--radius); transition: all 200ms;
  }
  #confirm-btn:hover { background: rgba(76,175,130,0.25); }
  #confirm-btn:disabled { opacity: 0.35; cursor: default; }
  #reject-btn {
    padding: 10px 16px; background: transparent; border: 1px solid var(--border);
    color: var(--text-dim); font-family: var(--mono); font-size: 11px;
    cursor: pointer; border-radius: var(--radius); transition: all 200ms;
  }
  #reject-btn:hover { border-color: var(--red); color: var(--red); }

  /* ── Result ── */
  .result-card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 14px; margin-top: 12px;
  }
  .result-ok { border-color: rgba(76,175,130,0.4); }
  .result-err { border-color: rgba(224,92,92,0.4); }
  .result-text { font-size: 12px; color: var(--text); margin-bottom: 8px; }
  .result-detail {
    font-size: 11px; color: var(--text-dim); white-space: pre-wrap;
    word-break: break-all; max-height: 140px; overflow-y: auto;
    background: var(--bg); padding: 8px; border-radius: 4px;
    border: 1px solid var(--border);
  }
  .receipt-line {
    display: flex; align-items: center; gap: 8px;
    margin-top: 8px; padding: 6px 10px;
    background: var(--gold-dim); border: 1px solid rgba(200,168,75,0.2);
    border-radius: 4px; font-size: 11px; color: var(--gold);
  }
  .receipt-id { font-weight: bold; }

  /* ── Witness strip ── */
  .timeline-item {
    display: flex; gap: 10px; margin-bottom: 14px; position: relative;
  }
  .timeline-item:not(:last-child)::before {
    content: ''; position: absolute; left: 10px; top: 22px;
    width: 1px; height: calc(100% + 4px); background: var(--border);
  }
  .tl-dot {
    width: 20px; height: 20px; border-radius: 50%; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 10px; margin-top: 1px; border: 1px solid;
  }
  .tl-dot-intent { background: var(--blue-dim); border-color: var(--blue); color: var(--blue); }
  .tl-dot-proposal { background: var(--gold-dim); border-color: var(--gold); color: var(--gold); }
  .tl-dot-hal { background: var(--green-dim); border-color: var(--green); color: var(--green); }
  .tl-dot-hal-warn { background: var(--red-dim); border-color: var(--red); color: var(--red); }
  .tl-dot-exec { background: var(--blue-dim); border-color: var(--blue); color: var(--blue); }
  .tl-dot-receipt { background: var(--gold-dim); border-color: var(--gold); color: var(--gold); }
  .tl-content { flex: 1; }
  .tl-label { font-size: 10px; letter-spacing: 1px; color: var(--text-dim); text-transform: uppercase; }
  .tl-value { font-size: 12px; color: var(--text); margin-top: 2px; word-break: break-word; line-height: 1.4; }
  .tl-ts { font-size: 10px; color: var(--text-faint); margin-top: 2px; }

  /* ── Witness full view ── */
  #witness-layout { display: none; }
  .ledger-row {
    display: flex; flex-direction: column; gap: 3px;
    padding: 8px 10px; border-bottom: 1px solid var(--border);
    font-size: 11px;
  }
  .ledger-op { color: var(--gold); }
  .ledger-hash { color: var(--text-dim); font-size: 10px; word-break: break-all; }
  .ledger-ts { color: var(--text-faint); font-size: 10px; }

  /* ── Empty / loading states ── */
  .empty-state { color: var(--text-faint); font-size: 12px; padding: 20px 0; line-height: 1.8; }
  .spinner { animation: spin 1s linear infinite; display: inline-block; }
  @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
  .thinking-text { color: var(--gold); font-size: 12px; }

  /* ── Advanced toggle ── */
  #advanced-section { margin-top: 16px; }
  .adv-toggle {
    font-size: 10px; color: var(--text-faint); cursor: pointer; letter-spacing: 1px;
    text-transform: uppercase; user-select: none;
  }
  .adv-toggle:hover { color: var(--text-dim); }
  #adv-content { display: none; margin-top: 10px; }
  #adv-content.open { display: block; }
  .adv-row { margin-bottom: 8px; }
  .adv-label { font-size: 10px; color: var(--text-dim); margin-bottom: 4px; letter-spacing: 0.5px; }
  .adv-input {
    width: 100%; background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 4px; color: var(--text); font-family: var(--mono);
    font-size: 11px; padding: 6px 8px; outline: none;
  }
  .adv-input:focus { border-color: var(--border-active); }
  .adv-btn {
    padding: 5px 12px; background: transparent; border: 1px solid var(--border);
    color: var(--text-dim); font-family: var(--mono); font-size: 10px;
    cursor: pointer; border-radius: 4px; letter-spacing: 0.5px;
  }
  .adv-btn:hover { border-color: var(--border-active); color: var(--text); }
</style>
</head>
<body>
<!-- Top bar -->
<div id="topbar">
  <div class="brand">HELEN OS <span>V0</span></div>
  <div class="mode-toggle">
    <button class="mode-btn active" id="btn-focus" onclick="setMode('focus')">Focus</button>
    <button class="mode-btn" id="btn-witness" onclick="setMode('witness')">Witness</button>
  </div>
  <div class="status-bar">
    <span class="pill pill-gate" id="gate-pill">Gate Clear</span>
    <span class="pill pill-ledger" id="ledger-pill">Ledger</span>
    <span class="pill pill-ns">NON_SOVEREIGN</span>
  </div>
</div>

<!-- FOCUS layout -->
<div id="focus-layout" style="display:flex; flex:1; overflow:hidden;">
  <!-- Panel 1: Intent -->
  <div class="panel" id="panel-intent">
    <div class="panel-header"><span class="dot dot-gold"></span>Intent</div>
    <div class="panel-body">
      <textarea id="intent-input" placeholder="What do you want HELEN to do?&#10;&#10;e.g. Search for recent AI governance papers&#10;e.g. Read the SOUL.md file&#10;e.g. Check this text for hyperstition patterns"></textarea>
      <button id="propose-btn" onclick="propose()">▶ Propose Action</button>
      <div class="intent-hint">
        <strong>HELEN suggests.</strong><br>
        You decide.<br>
        Everything is recorded.<br><br>
        HER proposes · HAL gates · You confirm · Ledger records.
      </div>
      <div id="advanced-section">
        <div class="adv-toggle" onclick="toggleAdv()">⚙ Advanced ▾</div>
        <div id="adv-content">
          <div class="adv-row">
            <div class="adv-label">Direct receipt message</div>
            <input class="adv-input" id="adv-receipt-msg" placeholder="Enter message to receipt directly">
          </div>
          <button class="adv-btn" onclick="advReceipt()">Emit Receipt</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Panel 2: Proposal + Execution -->
  <div class="panel" id="panel-proposal">
    <div class="panel-header"><span class="dot dot-gold"></span>Proposal · HAL Gate · Execution</div>
    <div class="panel-body">
      <div id="proposal-area">
        <div class="empty-state">
          Awaiting intent.<br><br>
          HELEN will propose a bounded action.<br>
          HAL will assess risk.<br>
          You confirm before anything executes.
        </div>
      </div>
    </div>
  </div>

  <!-- Panel 3: Witness strip -->
  <div class="panel" id="panel-witness-strip">
    <div class="panel-header"><span class="dot dot-green"></span>Witness Strip</div>
    <div class="panel-body">
      <div id="witness-strip-content">
        <div class="empty-state">No events yet.<br><br>Timeline appears here after each governed action.</div>
      </div>
    </div>
  </div>
</div>

<!-- WITNESS layout -->
<div id="witness-layout" style="display:none; flex:1; overflow:hidden;">
  <div class="panel" id="panel-timeline" style="flex:1;">
    <div class="panel-header"><span class="dot dot-green"></span>Full Event Timeline</div>
    <div class="panel-body">
      <div id="witness-timeline-content">
        <div class="empty-state">No events in this session yet.<br><br>Switch to Focus Mode and run a governed action to see the timeline.</div>
      </div>
    </div>
  </div>
  <div class="panel" id="panel-ledger" style="width:340px;">
    <div class="panel-header"><span class="dot dot-gold"></span>Ledger Tail</div>
    <div class="panel-body" style="padding:0;" id="ledger-content">
      <div class="empty-state" style="padding:16px;">Loading ledger…</div>
    </div>
  </div>
</div>

<script>
// ── State ─────────────────────────────────────────────────────────────────────
let currentMode = 'focus';
let events = [];
let pendingProposal = null;
let running = false;

// ── Mode switch ───────────────────────────────────────────────────────────────
function setMode(mode) {
  currentMode = mode;
  document.getElementById('btn-focus').classList.toggle('active', mode === 'focus');
  document.getElementById('btn-witness').classList.toggle('active', mode === 'witness');
  document.getElementById('focus-layout').style.display = mode === 'focus' ? 'flex' : 'none';
  document.getElementById('witness-layout').style.display = mode === 'witness' ? 'flex' : 'none';
  if (mode === 'witness') {
    renderWitnessTimeline();
    loadLedger();
  }
}

// ── Propose ───────────────────────────────────────────────────────────────────
async function propose() {
  const intent = document.getElementById('intent-input').value.trim();
  if (!intent || running) return;
  running = true;
  setProposeBtn(false);

  const area = document.getElementById('proposal-area');
  area.innerHTML = '<div class="thinking-text"><span class="spinner">⟳</span> HER is proposing…</div>';
  pushEvent('intent', intent, null);

  try {
    const resp = await fetch('/api/propose', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({intent})
    });
    const data = await resp.json();
    if (data.error) {
      area.innerHTML = `<div class="empty-state" style="color:var(--red)">${data.error}</div>`;
      running = false; setProposeBtn(true); return;
    }
    pendingProposal = data;
    pushEvent('proposal', data.summary, data);
    renderProposalCard(data);
  } catch(e) {
    area.innerHTML = `<div class="empty-state" style="color:var(--red)">Error: ${e.message}</div>`;
    running = false; setProposeBtn(true);
  }
}

function renderProposalCard(p) {
  const halClass = p.hal_risk === 'LOW' ? 'hal-pass-bg' : (p.hal_risk === 'HIGH' ? 'hal-warn-bg' : 'hal-medium-bg');
  const cardClass = p.hal_risk === 'LOW' ? 'hal-pass' : 'hal-warn';
  const halIcon = p.hal_risk === 'LOW' ? '✓' : (p.hal_risk === 'HIGH' ? '✗' : '⚠');
  const confirmEnabled = p.hal_risk !== 'HIGH';

  document.getElementById('proposal-area').innerHTML = `
    <div class="proposal-card ${cardClass}">
      <div class="prop-label">HER Proposal</div>
      <div class="prop-value">${escHtml(p.summary)}</div>

      <div class="prop-action">
        <div class="prop-action-icon">${getActionIcon(p.action)}</div>
        <div>
          <div class="prop-action-name">${escHtml(p.action)}</div>
          <div class="prop-action-param">${escHtml(p.param_label)}: ${escHtml(p.param_value)}</div>
        </div>
      </div>

      <div class="hal-verdict ${halClass}">
        <strong>HAL [${halIcon}] ${p.hal_risk}</strong>
        <span>— ${escHtml(p.hal_reason)}</span>
      </div>

      <div class="prop-label">Rationale</div>
      <div class="prop-value" style="font-size:11px; color:var(--text-dim); margin-bottom:14px">${escHtml(p.rationale)}</div>

      <div class="confirm-row">
        <button id="confirm-btn" onclick="confirmExec()" ${confirmEnabled ? '' : 'disabled'}>
          ${confirmEnabled ? '✓ Confirm & Execute' : '✗ Blocked by HAL'}
        </button>
        <button id="reject-btn" onclick="rejectProposal()">Reject</button>
      </div>
      ${p.hal_risk === 'HIGH' ? '<div style="margin-top:8px; font-size:10px; color:var(--red)">HIGH risk — execution blocked. Reject and rephrase your intent.</div>' : ''}
    </div>
    <div id="result-area"></div>
  `;
  updateGatePill(p.hal_risk);
  running = false;
  setProposeBtn(true);
}

// ── Confirm / Execute ─────────────────────────────────────────────────────────
async function confirmExec() {
  if (!pendingProposal || running) return;
  running = true;
  document.getElementById('confirm-btn').disabled = true;
  document.getElementById('reject-btn').disabled = true;

  const ra = document.getElementById('result-area');
  ra.innerHTML = '<div class="thinking-text" style="margin-top:12px"><span class="spinner">⟳</span> Executing bounded action…</div>';
  pushEvent('hal', `HAL ${pendingProposal.hal_risk} — executing`, pendingProposal);

  try {
    const resp = await fetch('/api/execute', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({action: pendingProposal.action, param_value: pendingProposal.param_value})
    });
    const data = await resp.json();
    pushEvent('execution', data.result || data.error, data);
    renderResult(ra, data);
    updateWitnessStrip();
    if (data.receipt) {
      pushEvent('receipt', data.receipt.receipt_id, data.receipt);
      updateLedgerPill(data.receipt.receipt_id);
    }
  } catch(e) {
    ra.innerHTML = `<div class="result-card result-err"><div class="result-text" style="color:var(--red)">Execution error: ${e.message}</div></div>`;
  }
  running = false;
  pendingProposal = null;
}

function renderResult(container, data) {
  const isOk = data.ok !== false;
  const receiptHtml = data.receipt && data.receipt.ok
    ? `<div class="receipt-line">📋 Receipt: <span class="receipt-id">${escHtml(data.receipt.receipt_id)}</span></div>`
    : (data.receipt ? `<div class="receipt-line" style="color:var(--red)">⚠ Receipt failed: ${escHtml(data.receipt.error || '?')}</div>` : '');
  container.innerHTML = `
    <div class="result-card ${isOk ? 'result-ok' : 'result-err'}">
      <div class="result-text" style="color:${isOk ? 'var(--green)' : 'var(--red)'}">
        ${isOk ? '✓' : '✗'} ${escHtml(data.result || data.error || '?')}
      </div>
      ${data.detail ? `<div class="result-detail">${escHtml(data.detail)}</div>` : ''}
      ${receiptHtml}
    </div>
  `;
}

function rejectProposal() {
  pendingProposal = null;
  pushEvent('reject', 'Operator rejected proposal', null);
  document.getElementById('proposal-area').innerHTML = '<div class="empty-state" style="color:var(--text-dim)">Proposal rejected.<br><br>Enter a new intent above.</div>';
  updateGatePill('CLEAR');
}

// ── Witness strip ─────────────────────────────────────────────────────────────
function updateWitnessStrip() {
  const container = document.getElementById('witness-strip-content');
  if (!events.length) return;
  container.innerHTML = events.slice().reverse().map(ev => {
    const dotClass = {
      intent: 'tl-dot-intent', proposal: 'tl-dot-proposal',
      hal: 'tl-dot-hal', execution: 'tl-dot-exec',
      receipt: 'tl-dot-receipt', reject: 'tl-dot-hal-warn'
    }[ev.type] || 'tl-dot-intent';
    const icons = {intent:'I', proposal:'P', hal:'H', execution:'E', receipt:'R', reject:'✗'};
    return `
      <div class="timeline-item">
        <div class="tl-dot ${dotClass}">${icons[ev.type] || '·'}</div>
        <div class="tl-content">
          <div class="tl-label">${ev.type}</div>
          <div class="tl-value">${escHtml(ev.label.substring(0, 80))}${ev.label.length > 80 ? '…' : ''}</div>
          <div class="tl-ts">${ev.ts}</div>
        </div>
      </div>
    `;
  }).join('');
}

function renderWitnessTimeline() {
  const container = document.getElementById('witness-timeline-content');
  if (!events.length) {
    container.innerHTML = '<div class="empty-state">No events in this session yet.<br><br>Switch to Focus Mode and run a governed action.</div>';
    return;
  }
  container.innerHTML = events.slice().reverse().map(ev => {
    const dotClass = {
      intent: 'tl-dot-intent', proposal: 'tl-dot-proposal',
      hal: 'tl-dot-hal', execution: 'tl-dot-exec',
      receipt: 'tl-dot-receipt', reject: 'tl-dot-hal-warn'
    }[ev.type] || 'tl-dot-intent';
    const icons = {intent:'I', proposal:'P', hal:'H', execution:'E', receipt:'R', reject:'✗'};
    const detail = ev.data ? `<div class="result-detail" style="margin-top:6px; max-height:80px">${escHtml(JSON.stringify(ev.data, null, 2).substring(0, 400))}</div>` : '';
    return `
      <div class="timeline-item">
        <div class="tl-dot ${dotClass}">${icons[ev.type] || '·'}</div>
        <div class="tl-content">
          <div class="tl-label">${ev.type}</div>
          <div class="tl-value">${escHtml(ev.label)}</div>
          ${detail}
          <div class="tl-ts">${ev.ts}</div>
        </div>
      </div>
    `;
  }).join('');
}

async function loadLedger() {
  try {
    const resp = await fetch('/api/ledger');
    const data = await resp.json();
    const container = document.getElementById('ledger-content');
    if (!data.entries || !data.entries.length) {
      container.innerHTML = '<div class="empty-state" style="padding:16px">No ledger entries.</div>';
      return;
    }
    container.innerHTML = data.entries.map(e => `
      <div class="ledger-row">
        <div class="ledger-op">${escHtml(e.op || 'entry')}</div>
        <div class="ledger-hash">payload: ${escHtml(e.hash)} · cum: ${escHtml(e.cum)}</div>
        <div class="ledger-ts">${escHtml(e.ts)}</div>
      </div>
    `).join('');
  } catch(e) {
    document.getElementById('ledger-content').innerHTML = '<div class="empty-state" style="padding:16px; color:var(--red)">Ledger read error.</div>';
  }
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function pushEvent(type, label, data) {
  events.push({type, label, data, ts: new Date().toLocaleTimeString()});
  updateWitnessStrip();
}

function setProposeBtn(enabled) {
  document.getElementById('propose-btn').disabled = !enabled;
}

function updateGatePill(risk) {
  const pill = document.getElementById('gate-pill');
  if (risk === 'LOW' || risk === 'CLEAR') {
    pill.textContent = 'Gate Clear';
    pill.style.background = 'var(--green-dim)';
    pill.style.color = 'var(--green)';
  } else if (risk === 'MEDIUM') {
    pill.textContent = 'Gate Warn';
    pill.style.background = 'rgba(255,165,0,0.1)';
    pill.style.color = '#ffa500';
  } else {
    pill.textContent = 'Gate Block';
    pill.style.background = 'var(--red-dim)';
    pill.style.color = 'var(--red)';
  }
}

function updateLedgerPill(receiptId) {
  document.getElementById('ledger-pill').textContent = receiptId || 'Ledger';
}

function getActionIcon(action) {
  const icons = {web_search:'🔍', open_url:'🌐', read_file:'📄', run_firewall:'🛡', write_note:'📝'};
  return icons[action] || '⚡';
}

function escHtml(s) {
  if (s == null) return '';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function toggleAdv() {
  const el = document.getElementById('adv-content');
  el.classList.toggle('open');
}

async function advReceipt() {
  const msg = document.getElementById('adv-receipt-msg').value.trim();
  if (!msg) return;
  try {
    const resp = await fetch('/api/receipt', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message: msg})
    });
    const data = await resp.json();
    alert(data.receipt_id ? `Receipt: ${data.receipt_id}` : `Error: ${data.error}`);
  } catch(e) { alert(`Error: ${e.message}`); }
}

// Enter to submit
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('intent-input').addEventListener('keydown', e => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) propose();
  });
});
</script>
</body>
</html>
"""


# ── HTTP handler ──────────────────────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_json(self, data: dict, status: int = 200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, html: str):
        body = html.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_html(HTML)
        elif self.path == "/api/ledger":
            self.send_json({"entries": read_ledger_tail(10)})
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}")

        if self.path == "/api/propose":
            intent = body.get("intent", "").strip()
            if not intent:
                self.send_json({"error": "No intent provided."}, 400)
                return
            proposal = call_gemini_proposal(intent)
            self.send_json(proposal)

        elif self.path == "/api/execute":
            action = body.get("action", "")
            param_value = body.get("param_value", "")
            if action not in ALLOWED_ACTIONS:
                self.send_json({"ok": False, "error": f"Action not in allowlist: {action}"})
                return
            result = execute_action(action, param_value)
            # emit receipt
            receipt_msg = (
                f"HELEN_OS_V0 action={action} param={param_value[:80]} "
                f"result={'OK' if result['ok'] else 'ERR'}: {str(result.get('result', result.get('error', '')))[:120]}"
            )
            result["receipt"] = emit_receipt(receipt_msg)
            self.send_json(result)

        elif self.path == "/api/receipt":
            msg = body.get("message", "").strip()
            if not msg:
                self.send_json({"ok": False, "error": "No message."})
                return
            self.send_json(emit_receipt(msg))

        else:
            self.send_response(404)
            self.end_headers()


def main():
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"HELEN OS V0  →  http://localhost:{PORT}")
    print("NON_SOVEREIGN · Focus + Witness · governed execution")
    server.serve_forever()


if __name__ == "__main__":
    main()

"""
helen_semantic_dashboard.py — HELEN OS MVP Dashboard V0
NON_SOVEREIGN · NO_SHIP · PROPOSAL
authority: NONE · mutation_rights: NONE · ledger_effect: NONE

Focus Mode: human actions → 5 semantic verbs
Witness Mode: receipts, proof, API state

Usage:
    .venv/bin/python tools/helen_semantic_dashboard.py
    http://localhost:5003
    http://<local-ip>:5003  (any device on same Wi-Fi)
"""

import sys
import os
import socket
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, request, jsonify, render_template_string

from src.helen_computer_use_api import (
    HELENSession,
    VALID_RELATION_TYPES,
    UnboundedOpenRejected, UnboundedSearchRejected, RelationReceiptMissing,
)
from src.cso_identity_contract import ADMIT, REJECT, QUARANTINE

SESSION = HELENSession(session_id="dashboard")
EVENTS: list[dict] = []


def _log(event_type: str, detail: str, status: str, extra: dict | None = None):
    EVENTS.append({
        "t": time.strftime("%H:%M:%S"),
        "type": event_type,
        "status": status,
        "detail": detail[:80],
        **(extra or {}),
    })
    if len(EVENTS) > 300:
        EVENTS.pop(0)


def _auto_receipt():
    return f"user:{time.strftime('%Y%m%d-%H%M%S')}"


app = Flask(__name__)

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<title>HELEN OS</title>
<style>
:root {
  --bg:#08080f; --panel:#0e1018; --panel2:#12141e; --panel3:#16192a;
  --border:#1c1f2e; --border2:#252840;
  --indigo:#6366f1; --indigo-lo:#4338ca; --indigo-bg:#0f1030;
  --green:#34d399; --green-bg:#052e16;
  --red:#f87171; --red-bg:#2d0a0a;
  --yellow:#fbbf24; --yellow-bg:#2d1f00;
  --purple:#a78bfa; --copper:#d97706;
  --muted:#374151; --muted2:#6b7280; --muted3:#9ca3af;
  --text:#e2e8f0; --text2:#94a3b8; --text3:#cbd5e1;
  --mono:'SF Mono','Fira Code','Consolas',monospace;
  --sans:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,sans-serif;
  --r:10px; --r2:7px;
}
*{box-sizing:border-box;margin:0;padding:0}
html{height:100%}
body{
  background:var(--bg); color:var(--text);
  font-family:var(--sans); font-size:14px;
  min-height:100%; display:flex; flex-direction:column;
  padding-top:env(safe-area-inset-top);
  padding-bottom:env(safe-area-inset-bottom);
}

/* ── HEADER ── */
#hdr{
  background:#080810; border-bottom:1px solid var(--border);
  padding:11px 16px; display:flex; align-items:center;
  justify-content:space-between; position:sticky; top:0; z-index:200;
  flex-shrink:0;
}
.hdr-left{display:flex;align-items:baseline;gap:10px}
.hdr-name{
  font-family:var(--mono);font-weight:700;font-size:17px;
  color:var(--indigo);letter-spacing:.04em;
}
.hdr-version{font-size:10px;color:var(--muted2);letter-spacing:.05em}
.hdr-right{display:flex;align-items:center;gap:8px}
.dot{width:6px;height:6px;border-radius:50%;background:var(--green);box-shadow:0 0 5px var(--green)}
.hdr-rule{font-size:10px;color:var(--muted2);letter-spacing:.03em}

/* ── MODE TOGGLE ── */
#mode-bar{
  background:#080810; border-bottom:1px solid var(--border);
  display:flex; flex-shrink:0;
}
.mode-btn{
  flex:1; padding:9px 8px; text-align:center;
  font-size:12px; font-weight:600; letter-spacing:.04em;
  cursor:pointer; transition:.15s;
  color:var(--muted2); border-bottom:2px solid transparent;
}
.mode-btn.active{color:var(--indigo);border-bottom-color:var(--indigo)}
.mode-btn:hover:not(.active){color:var(--text2)}

/* ── MAIN AREA ── */
#main{flex:1;overflow-y:auto;-webkit-overflow-scrolling:touch}

/* ── FOCUS MODE ── */
#focus{display:block}
#witness{display:none}

/* ── HERO ── */
#hero{padding:20px 16px 0;max-width:560px;margin:0 auto}
.hero-q{
  font-size:20px;font-weight:700;color:var(--text);
  margin-bottom:6px;line-height:1.3;
}
.hero-sub{font-size:13px;color:var(--muted2);margin-bottom:16px;line-height:1.5}

/* ── EXAMPLES ── */
.examples-row{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:20px}
.ex{
  background:var(--panel2);border:1px solid var(--border2);
  border-radius:20px;padding:6px 13px;font-size:11px;
  color:var(--text2);cursor:pointer;transition:.15s;
}
.ex:hover{border-color:var(--indigo);color:var(--indigo)}

/* ── ACTION CARDS ── */
#cards{padding:0 16px 24px;max-width:560px;margin:0 auto}
.action-card{
  background:var(--panel);border:1px solid var(--border);
  border-radius:var(--r);margin-bottom:10px;overflow:hidden;
  transition:.2s;
}
.action-card.open{border-color:var(--indigo)}
.card-head{
  padding:14px 16px;cursor:pointer;
  display:flex;align-items:center;gap:12px;
  user-select:none;
}
.card-icon{
  width:36px;height:36px;border-radius:8px;
  display:flex;align-items:center;justify-content:center;
  font-size:18px;flex-shrink:0;
}
.card-text{flex:1}
.card-label{font-size:14px;font-weight:600;color:var(--text);margin-bottom:2px}
.card-hint{font-size:11px;color:var(--muted2)}
.card-arrow{color:var(--muted);font-size:16px;transition:.2s;flex-shrink:0}
.action-card.open .card-arrow{transform:rotate(90deg);color:var(--indigo)}

.card-body{display:none;padding:0 16px 16px;border-top:1px solid var(--border)}
.action-card.open .card-body{display:block}
.card-body-inner{padding-top:14px}

/* card colour variants */
.c-add .card-icon{background:#1a1040;color:#818cf8}
.c-find .card-icon{background:#0a2020;color:#34d399}
.c-open .card-icon{background:#0a1a30;color:#60a5fa}
.c-render .card-icon{background:#1a0a30;color:#a78bfa}
.c-link .card-icon{background:#1a1000;color:#fbbf24}

/* ── FORMS ── */
.fgroup{margin-bottom:12px}
.flabel{
  font-size:11px;color:var(--muted2);
  margin-bottom:5px;display:flex;align-items:center;gap:6px;
}
.req{background:#2d1f5533;color:#a78bfa;font-size:9px;padding:1px 5px;border-radius:3px}
.opt{color:var(--muted);font-size:10px}
input,select,textarea{
  background:#07070d;border:1px solid var(--border2);
  border-radius:var(--r2);color:var(--text);
  padding:9px 12px;width:100%;
  font-family:var(--sans);font-size:13px;
  -webkit-appearance:none;transition:.15s;
}
input:focus,select:focus{outline:none;border-color:var(--indigo);box-shadow:0 0 0 3px #6366f118}
input::placeholder{color:var(--muted)}
select{
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath fill='%236b7280' d='M4 6l4 4 4-4z'/%3E%3C/svg%3E");
  background-repeat:no-repeat;background-position:right 10px center;
  background-size:16px;padding-right:32px;
}

/* receipt row */
.rcpt-row{position:relative}
.rcpt-row input{padding-right:76px}
.auto-btn{
  position:absolute;right:6px;top:50%;transform:translateY(-50%);
  background:#1c1c35;color:#818cf8;border:1px solid #2d2d55;
  border-radius:5px;padding:3px 9px;font-size:10px;
  cursor:pointer;white-space:nowrap;font-family:var(--sans);
}
.hint-text{font-size:11px;color:var(--muted);margin-top:4px;line-height:1.4}

/* ── BUTTONS ── */
.btn{
  background:var(--indigo);color:#fff;border:none;
  border-radius:var(--r2);padding:11px 20px;
  font-family:var(--sans);font-size:13px;font-weight:600;
  cursor:pointer;width:100%;transition:.15s;margin-top:4px;
}
.btn:hover{background:var(--indigo-lo)}
.btn.ghost{
  background:transparent;border:1px solid var(--border2);color:var(--text2);
}
.btn.ghost:hover{background:var(--panel2);color:var(--text)}
.btn-row{display:flex;gap:8px}
.btn-row .btn{flex:1}

/* ── RESULT ── */
.result{
  margin-top:12px;padding:12px;
  background:var(--panel2);border-radius:8px;
  border:1px solid var(--border);font-size:12px;
}
.result.hidden{display:none}
.badge{
  display:inline-flex;align-items:center;gap:5px;
  padding:3px 10px;border-radius:20px;
  font-size:11px;font-weight:600;margin-bottom:8px;
}
.badge.ok{background:var(--green-bg);color:var(--green)}
.badge.err{background:var(--red-bg);color:var(--red)}
.badge.warn{background:var(--yellow-bg);color:var(--yellow)}
.badge.dim{background:var(--panel);color:var(--muted2)}
.result-line{color:var(--muted2);font-size:11px;margin-top:4px;line-height:1.5}
.result-id{font-family:var(--mono);font-size:10px;color:#a5b4fc;word-break:break-all}

/* ── NODE CARDS ── */
.node-card{
  background:var(--panel2);border:1px solid var(--border);
  border-radius:8px;padding:10px 12px;margin-top:8px;
  display:flex;align-items:center;gap:10px;
}
.nc-icon{
  width:32px;height:32px;border-radius:7px;
  background:var(--indigo-bg);display:flex;align-items:center;
  justify-content:center;font-size:15px;flex-shrink:0;
}
.nc-info{flex:1;min-width:0}
.nc-type{font-size:11px;font-weight:600;color:#a5b4fc;margin-bottom:2px}
.nc-id{font-family:var(--mono);font-size:10px;color:var(--muted2);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.nc-copy{background:none;border:none;color:var(--muted);cursor:pointer;font-size:13px;padding:4px;flex-shrink:0}
.nc-copy:hover{color:var(--text)}

/* ── WITNESS MODE ── */
#witness{padding:16px;max-width:560px;margin:0 auto}
.w-section{margin-bottom:20px}
.w-title{
  font-size:10px;font-weight:700;color:var(--muted2);
  text-transform:uppercase;letter-spacing:.09em;
  margin-bottom:10px;display:flex;align-items:center;gap:6px;
}
.w-title::before{content:'';flex:1;height:1px;background:var(--border)}
.w-box{
  background:var(--panel);border:1px solid var(--border);
  border-radius:var(--r);padding:12px 14px;
}
.w-kv{display:flex;justify-content:space-between;align-items:baseline;padding:5px 0;border-bottom:1px solid var(--border)}
.w-kv:last-child{border-bottom:none}
.w-k{font-size:11px;color:var(--muted2)}
.w-v{font-size:11px;font-family:var(--mono);color:var(--text3);text-align:right;max-width:60%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.w-v.ok{color:var(--green)} .w-v.warn{color:var(--yellow)} .w-v.err{color:var(--red)}

/* log rows */
.log-row{
  padding:7px 0;border-bottom:1px solid var(--border);
  display:grid;grid-template-columns:52px 60px 64px 1fr;
  gap:8px;font-size:11px;align-items:center;
}
.log-t{color:var(--muted);font-family:var(--mono)}
.log-v{
  padding:2px 6px;border-radius:4px;text-align:center;
  font-size:10px;font-weight:700;
  background:#1a1c30;color:#818cf8;
}
.s-ok{color:var(--green)}.s-err{color:var(--red)}.s-warn{color:var(--yellow)}
.log-d{color:var(--muted2);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}

/* ── EMPTY STATE ── */
.empty{text-align:center;padding:30px 20px;color:var(--muted2)}
.empty-i{font-size:32px;opacity:.4;margin-bottom:10px}
.empty-t{font-size:13px;font-weight:600;color:var(--text2);margin-bottom:5px}
.empty-d{font-size:11px;line-height:1.6}

/* ── ns pills ── */
#ns-bar{
  padding:7px 16px;display:flex;flex-wrap:wrap;gap:6px;
  border-bottom:1px solid var(--border);
  background:var(--panel);min-height:36px;align-items:center;
  flex-shrink:0;
}
.ns-pill{
  background:#1a1c30;color:#818cf8;
  padding:2px 10px;border-radius:20px;font-size:11px;
  display:flex;align-items:center;gap:4px;
}
.ns-pill b{color:#e0e7ff}

/* scrollbar */
::-webkit-scrollbar{width:3px}
::-webkit-scrollbar-thumb{background:var(--border)}
</style>
</head>
<body>

<!-- HEADER -->
<div id="hdr">
  <div class="hdr-left">
    <span class="hdr-name">HELEN</span>
    <span class="hdr-version">OS V0</span>
  </div>
  <div class="hdr-right">
    <span class="dot"></span>
    <span class="hdr-rule" id="hdr-status">local · 0 objects</span>
  </div>
</div>

<!-- MODE TOGGLE -->
<div id="mode-bar">
  <div class="mode-btn active" onclick="setMode('focus')">
    ◎ Focus Mode <span style="font-size:10px;opacity:.6;margin-left:4px">what can I do?</span>
  </div>
  <div class="mode-btn" onclick="setMode('witness')">
    ⬡ Witness Mode <span style="font-size:10px;opacity:.6;margin-left:4px">what happened?</span>
  </div>
</div>

<!-- NS BAR -->
<div id="ns-bar">
  <span style="font-size:11px;color:var(--muted)">No objects yet — add something in Focus Mode</span>
</div>

<div id="main">

<!-- FOCUS MODE -->
<div id="focus">

  <div id="hero">
    <div class="hero-q">What do you want HELEN to help you do?</div>
    <div class="hero-sub">HELEN remembers what you give her. Everything is receipted. No receipt → no claim.</div>

    <div class="examples-row">
      <span class="ex" onclick="openCard('add');setExample('file')">📄 Add a file</span>
      <span class="ex" onclick="openCard('add');setExample('pdf')">📑 Add a PDF</span>
      <span class="ex" onclick="openCard('find')">⌕ Search memory</span>
      <span class="ex" onclick="openCard('render')">◈ Open an object</span>
      <span class="ex" onclick="openCard('link')">⇄ Link two objects</span>
    </div>
  </div>

  <div id="cards">

    <!-- ADD -->
    <div class="action-card c-add" id="card-add">
      <div class="card-head" onclick="toggleCard('add')">
        <div class="card-icon">＋</div>
        <div class="card-text">
          <div class="card-label">Add something to HELEN</div>
          <div class="card-hint">File, document, email, video — becomes a receipted semantic object</div>
        </div>
        <span class="card-arrow">›</span>
      </div>
      <div class="card-body">
        <div class="card-body-inner">
          <div class="fgroup">
            <div class="flabel">What are you adding?</div>
            <select id="i-type" onchange="updateHint()">
              <option value="file">File or document (path)</option>
              <option value="mail">Email message</option>
              <option value="media">Video or audio</option>
              <option value="screen">Screen text / region</option>
            </select>
          </div>
          <div class="fgroup">
            <div class="flabel">Path or details <span class="req">required</span></div>
            <input id="i-raw" type="text" placeholder="/path/to/file.pdf">
            <div class="hint-text" id="i-hint">Enter a full file path.</div>
          </div>
          <div class="fgroup">
            <div class="flabel">Receipt <span class="opt">auto-fills if empty</span></div>
            <div class="rcpt-row">
              <input id="i-receipt" type="text" placeholder="auto-generated">
              <button class="auto-btn" onclick="fillReceipt('i-receipt')">auto</button>
            </div>
          </div>
          <button class="btn" onclick="doIngest()">Add to HELEN memory</button>
          <div class="result hidden" id="i-result"></div>
        </div>
      </div>
    </div>

    <!-- FIND -->
    <div class="action-card c-find" id="card-find">
      <div class="card-head" onclick="toggleCard('find')">
        <div class="card-icon">⌕</div>
        <div class="card-text">
          <div class="card-label">Search HELEN's memory</div>
          <div class="card-hint">Filter by category or object type — bounded, deterministic</div>
        </div>
        <span class="card-arrow">›</span>
      </div>
      <div class="card-body">
        <div class="card-body-inner">
          <div class="fgroup">
            <div class="flabel">Category</div>
            <select id="o-ns">
              <option value="">All categories</option>
              <option value="files">Files &amp; documents</option>
              <option value="mail">Email</option>
              <option value="media">Video &amp; audio</option>
              <option value="screen">Screen captures</option>
            </select>
          </div>
          <div class="fgroup">
            <div class="flabel">Object type <span class="opt">optional</span></div>
            <input id="o-type" type="text" placeholder="FILE_PDF · MAIL_MESSAGE · MEDIA_VIDEO">
          </div>
          <div class="fgroup">
            <div class="flabel">Related to <span class="opt">paste object ID</span></div>
            <input id="o-rel" type="text" placeholder="files/abc123…">
          </div>
          <div class="btn-row">
            <button class="btn" onclick="doSearch()">Search</button>
            <button class="btn ghost" onclick="doOpen()">Open view</button>
          </div>
          <div class="result hidden" id="o-result"></div>
        </div>
      </div>
    </div>

    <!-- RENDER / OPEN -->
    <div class="action-card c-open" id="card-render">
      <div class="card-head" onclick="toggleCard('render')">
        <div class="card-icon">◈</div>
        <div class="card-text">
          <div class="card-label">Open a known object</div>
          <div class="card-hint">Render a specific object by its ID — authority always 0</div>
        </div>
        <span class="card-arrow">›</span>
      </div>
      <div class="card-body">
        <div class="card-body-inner">
          <div class="fgroup">
            <div class="flabel">Object ID <span class="req">required</span></div>
            <input id="rnd-id" type="text" placeholder="files/abc123… (copy from memory)">
            <div class="hint-text">Copy an object ID from Witness Mode → Memory, then paste here.</div>
          </div>
          <button class="btn" onclick="doRender()">Open object</button>
          <div class="result hidden" id="rnd-result"></div>
        </div>
      </div>
    </div>

    <!-- LINK -->
    <div class="action-card c-link" id="card-link">
      <div class="card-head" onclick="toggleCard('link')">
        <div class="card-icon">⇄</div>
        <div class="card-text">
          <div class="card-label">Connect two objects</div>
          <div class="card-hint">Declare a receipted relationship — replaces folders and tags</div>
        </div>
        <span class="card-arrow">›</span>
      </div>
      <div class="card-body">
        <div class="card-body-inner">
          <div class="fgroup">
            <div class="flabel">Object A <span class="req">required</span></div>
            <input id="r-a" type="text" placeholder="files/abc123…">
          </div>
          <div class="fgroup">
            <div class="flabel">Relationship</div>
            <select id="r-type">
              {% for rt in relation_types %}
              <option>{{ rt }}</option>
              {% endfor %}
            </select>
          </div>
          <div class="fgroup">
            <div class="flabel">Object B <span class="req">required</span></div>
            <input id="r-b" type="text" placeholder="mail/def456…">
          </div>
          <div class="fgroup">
            <div class="flabel">Receipt <span class="opt">auto-fills if empty</span></div>
            <div class="rcpt-row">
              <input id="r-receipt" type="text" placeholder="auto-generated">
              <button class="auto-btn" onclick="fillReceipt('r-receipt')">auto</button>
            </div>
          </div>
          <button class="btn" onclick="doRelate()">Create connection</button>
          <div class="result hidden" id="r-result"></div>
        </div>
      </div>
    </div>

  </div><!-- #cards -->
</div><!-- #focus -->

<!-- WITNESS MODE -->
<div id="witness">

  <div class="w-section">
    <div class="w-title">System state</div>
    <div class="w-box">
      <div class="w-kv"><span class="w-k">Objects in memory</span><span class="w-v ok" id="w-nodes">0</span></div>
      <div class="w-kv"><span class="w-k">Receipts this session</span><span class="w-v ok" id="w-receipts">0</span></div>
      <div class="w-kv"><span class="w-k">Render calls</span><span class="w-v" id="w-renders">0</span></div>
      <div class="w-kv"><span class="w-k">Graph hash</span><span class="w-v" id="w-hash">—</span></div>
      <div class="w-kv"><span class="w-k">Rule</span><span class="w-v">NO RECEIPT = NO CLAIM</span></div>
    </div>
  </div>

  <div class="w-section">
    <div class="w-title">Memory</div>
    <div id="w-nodes-list">
      <div class="empty">
        <div class="empty-i">◈</div>
        <div class="empty-t">Nothing in memory yet</div>
        <div class="empty-d">Add objects using Focus Mode.</div>
      </div>
    </div>
  </div>

  <div class="w-section">
    <div class="w-title">Event log</div>
    <div id="w-log">
      <div class="empty">
        <div class="empty-i">◎</div>
        <div class="empty-t">No events yet</div>
        <div class="empty-d">Events appear here as HELEN acts.</div>
      </div>
    </div>
  </div>

  <div class="w-section" style="padding-bottom:16px">
    <div class="w-title">Operator notes</div>
    <div class="w-box">
      <div class="w-kv"><span class="w-k">Protocol</span><span class="w-v">HTTP only (not HTTPS)</span></div>
      <div class="w-kv"><span class="w-k">Network</span><span class="w-v">local Wi-Fi only</span></div>
      <div class="w-kv"><span class="w-k">Persistence</span><span class="w-v warn">session memory (restarts clear)</span></div>
      <div class="w-kv"><span class="w-k">K8 status</span><span class="w-v warn">F-010 / F-011 pending</span></div>
    </div>
  </div>

</div><!-- #witness -->
</div><!-- #main -->

<script>
/* ── state ── */
const TYPE_ICONS = {
  FILE_PDF:'📑',FILE_TEXT:'📄',FILE_DOC:'📄',FILE_UNKNOWN:'📁',
  MAIL_MESSAGE:'✉️',MEDIA_VIDEO:'🎬',MEDIA_AUDIO:'🎵',
  MEDIA_IMAGE:'🖼️',SCREEN_REGION:'📸'
};
const TYPE_LABELS = {
  FILE_PDF:'PDF',FILE_TEXT:'Text File',FILE_DOC:'Document',FILE_UNKNOWN:'File',
  MAIL_MESSAGE:'Email',MEDIA_VIDEO:'Video',MEDIA_AUDIO:'Audio',
  MEDIA_IMAGE:'Image',SCREEN_REGION:'Screen'
};
const ST = {ACCEPT:'ok',REJECT:'err',QUARANTINE:'warn',DEGRADE:'warn'};
const SL = {ACCEPT:'Admitted ✓',REJECT:'Rejected',QUARANTINE:'Quarantined',DEGRADE:'Degraded'};

function setMode(m) {
  document.getElementById('focus').style.display = m==='focus'?'block':'none';
  document.getElementById('witness').style.display = m==='witness'?'block':'none';
  document.querySelectorAll('.mode-btn').forEach((b,i) => {
    b.classList.toggle('active', (i===0&&m==='focus')||(i===1&&m==='witness'));
  });
}

function toggleCard(id) {
  const c = document.getElementById('card-'+id);
  c.classList.toggle('open');
}
function openCard(id) {
  document.getElementById('card-'+id).classList.add('open');
}

const HINTS = {
  file:'Enter a full file path. Example: /Users/you/Documents/report.pdf',
  mail:'Email message-id or address. Example: <msg-001@domain.com>',
  media:'Full path to video or audio. Example: /Users/you/Movies/clip.mp4',
  screen:'Paste the text visible on screen, or describe the region.',
};
function updateHint() {
  const t = document.getElementById('i-type').value;
  document.getElementById('i-hint').textContent = HINTS[t]||'';
}

const EXAMPLES = {
  file:'/Users/you/Documents/contract.pdf',
  pdf:'/Users/you/Documents/report.pdf',
  video:'/Users/you/Movies/presentation.mp4',
};
function setExample(k) {
  if(k==='video'){document.getElementById('i-type').value='media';updateHint();}
  document.getElementById('i-raw').value = EXAMPLES[k]||'';
}

function fillReceipt(id) {
  const t = new Date().toISOString().replace(/[:.]/g,'-').slice(0,19);
  document.getElementById(id).value = 'user:'+t;
}
function autoRcpt() {
  return 'user:'+new Date().toISOString().replace(/[:.]/g,'-').slice(0,19);
}

/* ── fetch state ── */
async function fetchState() {
  const d = await (await fetch('/api/state')).json();
  document.getElementById('hdr-status').textContent =
    `local · ${d.node_count} object${d.node_count!==1?'s':''}`;

  // ns bar
  const nsEl = document.getElementById('ns-bar');
  const entries = Object.entries(d.namespaces||{});
  nsEl.innerHTML = entries.length
    ? entries.map(([k,v])=>`<span class="ns-pill">${nsIcon(k)} ${k} <b>${v}</b></span>`).join('')
    : '<span style="font-size:11px;color:var(--muted)">No objects yet — add something in Focus Mode</span>';

  // witness stats
  document.getElementById('w-nodes').textContent = d.node_count;
  document.getElementById('w-receipts').textContent = d.receipt_count;
  document.getElementById('w-renders').textContent = d.render_log_count;
  document.getElementById('w-hash').textContent =
    d.node_count>0 ? (d.graph_hash||'').slice(0,12)+'…' : '—';

  // witness node list
  const nl = document.getElementById('w-nodes-list');
  nl.innerHTML = (d.nodes||[]).length
    ? d.nodes.map(n=>`
      <div class="node-card">
        <div class="nc-icon">${TYPE_ICONS[n.type]||'◈'}</div>
        <div class="nc-info">
          <div class="nc-type">${TYPE_LABELS[n.type]||n.type}</div>
          <div class="nc-id" title="${n.global_id}">${n.global_id}</div>
        </div>
        <button class="nc-copy" onclick="copy('${n.global_id}')" title="Copy ID">⎘</button>
      </div>`).join('')
    : `<div class="empty"><div class="empty-i">◈</div>
       <div class="empty-t">Nothing in memory yet</div>
       <div class="empty-d">Add objects using Focus Mode.</div></div>`;

  // event log
  const lEl = document.getElementById('w-log');
  lEl.innerHTML = (d.events||[]).length
    ? [...d.events].reverse().map(e=>{
        const sc = e.status==='ACCEPT'?'ok':e.status==='REJECT'?'err':'warn';
        return `<div class="log-row">
          <span class="log-t">${e.t}</span>
          <span class="log-v">${e.type}</span>
          <span class="s-${sc}">${SL[e.status]||e.status}</span>
          <span class="log-d">${e.detail||''}</span>
        </div>`;
      }).join('')
    : `<div class="empty"><div class="empty-i">◎</div>
       <div class="empty-t">No events yet</div></div>`;
}

function nsIcon(ns){return{files:'📁',mail:'✉️',media:'🎬',screen:'📸'}[ns]||'◈'}

function showResult(id, status, lines) {
  const el = document.getElementById(id);
  const cls = ST[status]||'dim';
  el.innerHTML = `<div class="badge ${cls}">${SL[status]||status}</div>` +
    lines.map(l=>`<div class="result-line">${l}</div>`).join('');
  el.classList.remove('hidden');
}

function copy(txt) { navigator.clipboard.writeText(txt); }

/* ── actions ── */
async function doIngest() {
  const raw = document.getElementById('i-raw').value.trim();
  if (!raw) { alert('I need a path or details to add.'); return; }
  let receipt = document.getElementById('i-receipt').value.trim() || autoRcpt();
  document.getElementById('i-receipt').value = receipt;

  const type = document.getElementById('i-type').value;
  let signal;
  if (type==='file'||type==='media') { signal = raw; }
  else if (type==='mail') {
    signal = {signal:'MAIL',from_addr:raw,message_id:raw,subject:'(added via dashboard)'};
  } else { signal = {signal:'SCREEN',ocr_text:raw}; }

  const d = await (await fetch('/api/ingest',{
    method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({raw:signal,receipt})
  })).json();

  const lines = [];
  if (d.global_id) lines.push(`Object ID: <span class="result-id">${d.global_id}</span>`);
  if (d.reason && d.status!=='ACCEPT') lines.push(d.reason);
  if (d.status==='ACCEPT') lines.push('Receipt: <span class="result-id">'+receipt+'</span>');
  showResult('i-result', d.status, lines);
  fetchState();
}

async function doSearch() {
  const ns=document.getElementById('o-ns').value;
  const tp=document.getElementById('o-type').value.trim();
  const rel=document.getElementById('o-rel').value.trim();
  if (!ns&&!tp&&!rel) { alert('I need a category, object type, or object ID to search.'); return; }
  const q={};
  if(ns) q.namespace_filter=ns;
  if(tp) q.type_filter=tp;
  if(rel) q.relation_to=rel;
  const d = await (await fetch('/api/search',{
    method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({query:q})
  })).json();
  renderSlice(d,'o-result'); fetchState();
}

async function doOpen() {
  const ns=document.getElementById('o-ns').value;
  const tp=document.getElementById('o-type').value.trim();
  if (!ns&&!tp) { alert('I need at least a category to open a view.'); return; }
  const intent={};
  if(ns) intent.namespace_filter=ns;
  if(tp) intent.type_filter=tp;
  const d = await (await fetch('/api/open',{
    method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({intent})
  })).json();
  renderSlice(d,'o-result'); fetchState();
}

function renderSlice(d, id) {
  const el = document.getElementById(id);
  if (d.error) { showResult(id,'REJECT',[d.error]); return; }
  const nodes = Object.entries(d.nodes||{});
  if (!nodes.length) {
    el.innerHTML='<div class="badge dim">0 results</div><div class="result-line">Nothing matches that filter.</div>';
    el.classList.remove('hidden'); return;
  }
  el.innerHTML=`<div class="badge ok">${nodes.length} result${nodes.length>1?'s':''}</div>`+
    nodes.map(([gid,info])=>`
      <div class="node-card">
        <div class="nc-icon">${TYPE_ICONS[info.type]||'◈'}</div>
        <div class="nc-info">
          <div class="nc-type">${TYPE_LABELS[info.type]||info.type}</div>
          <div class="nc-id">${gid}</div>
        </div>
        <button class="nc-copy" onclick="copy('${gid}')" title="Copy ID">⎘</button>
      </div>`).join('');
  el.classList.remove('hidden');
}

async function doRender() {
  const gid = document.getElementById('rnd-id').value.trim();
  if (!gid) { alert('I need an object ID to open. Copy one from Witness Mode → Memory.'); return; }
  const d = await (await fetch(`/api/render/${encodeURIComponent(gid)}`)).json();
  if (d.error) { showResult('rnd-result','REJECT',[d.error]); return; }
  showResult('rnd-result','ACCEPT',[
    `Authority: ${d.authority}`,
    `Nodes in view: ${d.node_count}`,
    `Session receipt: <span class="result-id">${d.receipt||'—'}</span>`,
  ]);
  fetchState();
}

async function doRelate() {
  const a=document.getElementById('r-a').value.trim();
  const b=document.getElementById('r-b').value.trim();
  const t=document.getElementById('r-type').value;
  if (!a||!b) { alert('I need two object IDs to create a connection. Copy them from Witness Mode → Memory.'); return; }
  let receipt=document.getElementById('r-receipt').value.trim()||autoRcpt();
  document.getElementById('r-receipt').value=receipt;
  const d = await (await fetch('/api/relate',{
    method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({id_a:a,id_b:b,relation_type:t,receipt})
  })).json();
  showResult('r-result',d.status,[d.reason||'',`Receipt: <span class="result-id">${receipt}</span>`]);
  fetchState();
}

fetchState();
setInterval(fetchState, 5000);
</script>
</body>
</html>"""


@app.route("/")
def index():
    return render_template_string(HTML, relation_types=sorted(VALID_RELATION_TYPES))


@app.route("/api/state")
def api_state():
    state = SESSION.state()
    ns: dict[str, int] = {}
    nodes = []
    for gid, node in sorted(SESSION._graph._nodes.items()):
        ns[node.namespace] = ns.get(node.namespace, 0) + 1
        nodes.append({"global_id": gid, "type": node.type,
                       "hash": node.canonical_hash()[:12]})
    return jsonify({
        "node_count": state.node_count,
        "receipt_count": state.receipt_count,
        "render_log_count": state.render_log_count,
        "graph_hash": state.graph_hash,
        "event_count": len(EVENTS),
        "namespaces": ns,
        "nodes": nodes,
        "events": EVENTS[-60:],
    })


@app.route("/api/ingest", methods=["POST"])
def api_ingest():
    b = request.get_json(force=True)
    raw = b.get("raw", "")
    receipt = b.get("receipt", "") or _auto_receipt()
    try:
        r = SESSION.ingest(raw, receipt)
        _log("ingest", str(raw)[:60], r.status, {"global_id": r.global_id})
        return jsonify({"status": r.status, "global_id": r.global_id, "reason": r.reason})
    except Exception as e:
        _log("ingest", str(e)[:60], REJECT)
        return jsonify({"status": REJECT, "reason": str(e)}), 400


@app.route("/api/open", methods=["POST"])
def api_open():
    b = request.get_json(force=True)
    try:
        sl = SESSION.open(b.get("intent", {}))
        _log("open", str(b.get("intent"))[:60], ADMIT)
        return jsonify({"node_count": sl.node_count, "nodes": sl.nodes,
                        "graph_hash": sl.graph_hash})
    except UnboundedOpenRejected as e:
        _log("open", str(e)[:60], REJECT)
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/search", methods=["POST"])
def api_search():
    b = request.get_json(force=True)
    try:
        sl = SESSION.search(b.get("query", {}))
        _log("search", str(b.get("query"))[:60], ADMIT)
        return jsonify({"node_count": sl.node_count, "nodes": sl.nodes,
                        "graph_hash": sl.graph_hash})
    except UnboundedSearchRejected as e:
        _log("search", str(e)[:60], REJECT)
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/relate", methods=["POST"])
def api_relate():
    b = request.get_json(force=True)
    receipt = b.get("receipt", "") or _auto_receipt()
    try:
        r = SESSION.relate(b.get("id_a",""), b.get("id_b",""),
                           b.get("relation_type",""), receipt)
        _log("relate", f"{b.get('id_a','')[:20]}→{b.get('id_b','')[:20]}", r.status)
        return jsonify({"status": r.status, "reason": r.reason})
    except RelationReceiptMissing as e:
        _log("relate", str(e)[:60], REJECT)
        return jsonify({"status": REJECT, "reason": str(e)}), 400
    except Exception as e:
        return jsonify({"status": REJECT, "reason": str(e)}), 500


@app.route("/api/render/<path:global_id>")
def api_render(global_id):
    renderer = request.args.get("renderer", "DEFAULT")
    try:
        env = SESSION.render(global_id, renderer)
        _log("render", global_id, ADMIT)
        return jsonify({"authority": env.authority, "receipt": env.session_receipt,
                        "node_count": env.slice.node_count})
    except KeyError:
        return jsonify({"error": f"{global_id} not found"}), 404


if __name__ == "__main__":
    port = int(os.environ.get("HELEN_SEMANTIC_PORT", 5003))
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "localhost"

    print(f"\nHELEN OS V0 · semantic dashboard")
    print(f"→ http://localhost:{port}  (this machine)")
    print(f"→ http://{local_ip}:{port}  (iPhone / laptop — same Wi-Fi)")
    print(f"→ Focus Mode: human actions  |  Witness Mode: proof")
    print(f"→ NO RECEIPT = NO CLAIM\n")
    app.run(host="0.0.0.0", port=port, debug=False)

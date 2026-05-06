"""
helen_semantic_dashboard.py — Universal device-agnostic semantic OS dashboard
NON_SOVEREIGN · NO_SHIP · PROPOSAL
authority: NONE · mutation_rights: NONE · ledger_effect: NONE

Wraps HELENSession — 5 verbs accessible from any device on the local network.
Responsive HTML. No app install. Open on iMac, iPhone, or laptop at:

    http://localhost:5003
    http://<your-local-ip>:5003

Operator dashboard contract (6 invariants):
  1. Single dashboard — one URL, all devices
  2. Capacity visible — node count, namespace breakdown, graph hash
  3. OS noise exposed — quarantined, rejected items in event log
  4. Operator chooses levers — ingest / open / search / relate from UI
  5. No hidden mutation — all state changes appear in receipt log
  6. No receipt → no ship — ingest and relate require receipt field

Usage:
    .venv/bin/python tools/helen_semantic_dashboard.py
    # find your local IP: ipconfig getifaddr en0
    # open http://<ip>:5003 on iPhone
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

# ── Session + event log ───────────────────────────────────────────────────────

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


# ── Flask ─────────────────────────────────────────────────────────────────────

app = Flask(__name__)

# ── HTML ──────────────────────────────────────────────────────────────────────

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<title>HELEN OS V0</title>
<style>
:root {
  --bg:#080b10; --panel:#101722; --panel-2:#0d121b; --border:#253044;
  --blue:#6ea8fe; --green:#34d399; --red:#f87171;
  --yellow:#fbbf24; --violet:#a78bfa; --muted:#8a94a6;
  --text:#edf3f8; --soft:#c4ceda; --mono:'SF Mono','Fira Code',monospace;
  --safe-top: env(safe-area-inset-top);
  --safe-bottom: env(safe-area-inset-bottom);
}
*{box-sizing:border-box;margin:0;padding:0}
body{background:radial-gradient(circle at top left,#182034 0,#080b10 42%);
     color:var(--text);font-family:var(--mono);font-size:14px;
     padding:env(safe-area-inset-top) env(safe-area-inset-right)
             env(safe-area-inset-bottom) env(safe-area-inset-left)}

header{padding:20px 18px 14px;border-bottom:1px solid var(--border);
       background:rgba(8,11,16,.9);position:sticky;top:0;z-index:100;
       backdrop-filter:blur(16px)}
.kicker{font-size:11px;letter-spacing:.16em;color:var(--blue);font-weight:700;
        text-transform:uppercase;margin-bottom:8px}
h1{font-size:28px;line-height:1.05;letter-spacing:0;margin-bottom:8px}
.prompt{font-size:15px;line-height:1.45;color:var(--soft);max-width:780px}
.law{margin-top:12px;padding:10px 12px;border:1px solid #3a4b66;border-radius:8px;
     color:var(--yellow);background:rgba(251,191,36,.07);font-size:12px}

main{max-width:1120px;margin:0 auto;padding:16px}
.section-title{font-size:12px;letter-spacing:.14em;text-transform:uppercase;
               color:var(--muted);margin:20px 0 10px}
.action-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:10px}
.action-card{background:linear-gradient(180deg,#131d2b,#0d131d);border:1px solid var(--border);
             border-radius:8px;padding:14px;min-height:136px;cursor:pointer;
             display:flex;flex-direction:column;gap:9px;transition:.15s}
.action-card:hover,.action-card.active{border-color:var(--blue);transform:translateY(-1px)}
.action-title{font-size:15px;line-height:1.25;font-weight:700;color:var(--text)}
.action-desc{font-size:12px;line-height:1.4;color:var(--soft)}
.verb{margin-top:auto;font-size:10px;color:var(--muted);text-transform:uppercase}

.workbench{margin-top:12px;background:var(--panel);border:1px solid var(--border);
           border-radius:8px;padding:14px}
.pane{display:none}.pane.active{display:block}
.fgroup{margin-bottom:12px}
.flabel{font-size:10px;color:var(--muted);text-transform:uppercase;
        letter-spacing:.06em;margin-bottom:5px}
input,select,textarea{background:#0a0a10;border:1px solid var(--border);
  border-radius:6px;color:var(--text);padding:9px 11px;width:100%;
  font-family:var(--mono);font-size:13px;-webkit-appearance:none}
input:focus,select:focus{outline:none;border-color:var(--blue)}
button{background:var(--blue);color:#08111f;border:none;border-radius:6px;
       padding:10px 20px;font-family:var(--mono);font-size:13px;
       cursor:pointer;width:100%;font-weight:600;margin-top:4px}
button:active{filter:brightness(.9)}
.btn-row{display:flex;gap:8px}
.btn-row button{flex:1}
.result{margin-top:10px;padding:10px;background:var(--panel);border-radius:6px;
        font-size:11px;min-height:36px;border:1px solid var(--border)}
.ok{color:var(--green)} .err{color:var(--red)} .warn{color:var(--yellow)}
.dim{color:var(--muted)}

.witness-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px}
.witness-card{background:var(--panel-2);border:1px solid var(--border);border-radius:8px;padding:12px}
.witness-label{font-size:10px;text-transform:uppercase;letter-spacing:.12em;color:var(--muted);
               margin-bottom:7px}
.witness-value{font-size:14px;color:var(--text);overflow-wrap:anywhere}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:12px}
.stat-cell{background:var(--panel-2);border:1px solid var(--border);border-radius:8px;
           padding:12px;text-align:center}
.stat-cell .label{font-size:9px;color:var(--muted);text-transform:uppercase;
                  letter-spacing:.08em;margin-bottom:5px}
.stat-cell .value{font-size:22px;font-weight:700}
#ns-strip{margin-top:10px;display:flex;flex-wrap:wrap;gap:6px;min-height:28px}
.ns-pill{background:#172034;color:#bdd0ff;padding:4px 10px;border-radius:999px;font-size:11px}
.advanced{margin-top:12px;border-top:1px solid var(--border);padding-top:12px}
.advanced summary{cursor:pointer;color:var(--muted);font-size:12px}

.node-item{padding:8px 0;border-bottom:1px solid var(--border);display:flex;
           align-items:center;gap:8px}
.node-id{color:#bdd0ff;font-size:11px;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.node-type{color:var(--muted);font-size:10px;flex-shrink:0}
.ev-row{padding:5px 0;border-bottom:1px solid var(--border);
        display:grid;grid-template-columns:56px 56px 1fr;gap:6px;font-size:10px}
.ev-t{color:var(--muted)} .ev-type{color:#bdd0ff}
.scroll{max-height:55vh;overflow-y:auto}
::-webkit-scrollbar{width:3px}
::-webkit-scrollbar-thumb{background:var(--border)}

select{background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath fill='%236b7280' d='M4 6l4 4 4-4z'/%3E%3C/svg%3E");
       background-repeat:no-repeat;background-position:right 10px center;
       background-size:16px;padding-right:32px}

@media (max-width: 900px){
  .action-grid{grid-template-columns:1fr}
  .witness-grid{grid-template-columns:1fr}
  .stats{grid-template-columns:repeat(2,1fr)}
  h1{font-size:24px}
  main{padding:12px}
}
</style>
</head>
<body>

<header>
  <div class="kicker">HELEN OS V0</div>
  <h1>What do you want HELEN to help you do?</h1>
  <div class="prompt">Choose a human action first. The internal verbs still exist, but they stay behind the operator surface.</div>
  <div class="law">NO RECEIPT = NO CLAIM</div>
</header>

<main>
  <div class="section-title">Focus Mode</div>
  <section class="action-grid" aria-label="HELEN action cards">
    <div class="action-card active" data-target="ingest" onclick="switchAction('ingest')">
      <div class="action-title">Add something to HELEN memory</div>
      <div class="action-desc">Register a file, message, media object, or screen signal with a receipt.</div>
      <div class="verb">operator verb: ingest</div>
    </div>
    <div class="action-card" data-target="open" onclick="switchAction('open')">
      <div class="action-title">Open a known object</div>
      <div class="action-desc">Open a bounded slice of memory by namespace, type, or known relation.</div>
      <div class="verb">operator verb: open</div>
    </div>
    <div class="action-card" data-target="search" onclick="switchAction('search')">
      <div class="action-title">Search HELEN memory</div>
      <div class="action-desc">Find matching objects without exposing an unbounded memory surface.</div>
      <div class="verb">operator verb: search</div>
    </div>
    <div class="action-card" data-target="render" onclick="switchAction('render')">
      <div class="action-title">Render a system view</div>
      <div class="action-desc">Generate a receipt-bound view of an admitted object.</div>
      <div class="verb">operator verb: render</div>
    </div>
    <div class="action-card" data-target="relate" onclick="switchAction('relate')">
      <div class="action-title">Connect two objects</div>
      <div class="action-desc">Create a typed relation between two objects with an explicit receipt.</div>
      <div class="verb">operator verb: relate</div>
    </div>
  </section>

  <section class="workbench">
    <div class="pane active" id="pane-ingest">
      <div class="fgroup">
        <div class="flabel">What kind of memory object?</div>
        <select id="i-type">
          <option value="file">File path</option>
          <option value="mail">Mail envelope</option>
          <option value="media">Media metadata</option>
          <option value="screen">Screen region</option>
        </select>
      </div>
      <div class="fgroup">
        <div class="flabel">Path or JSON</div>
        <input id="i-raw" type="text" placeholder="/path/to/file.pdf  or  {...}">
      </div>
      <div class="fgroup">
        <div class="flabel">Receipt</div>
        <input id="i-receipt" type="text" placeholder="user:add-memory:2026-05-06">
      </div>
      <button onclick="doIngest()">Add to HELEN memory</button>
      <div class="result dim" id="i-result">Waiting for an object.</div>
    </div>

    <div class="pane" id="pane-open">
      <div class="fgroup">
        <div class="flabel">Namespace</div>
        <select id="o-ns">
          <option value="">Choose a bounded filter</option>
          <option value="files">files</option>
          <option value="mail">mail</option>
          <option value="media">media</option>
          <option value="screen">screen</option>
        </select>
      </div>
      <div class="fgroup">
        <div class="flabel">Type filter</div>
        <input id="o-type" type="text" placeholder="FILE_PDF · MAIL_THREAD · MEDIA_VIDEO">
      </div>
      <button onclick="doOpen()">Open bounded memory view</button>
      <div class="result scroll" id="o-result"><span class="dim">No bounded view opened yet.</span></div>
    </div>

    <div class="pane" id="pane-search">
      <div class="fgroup">
        <div class="flabel">Namespace</div>
        <select id="s-ns">
          <option value="">Choose a bounded filter</option>
          <option value="files">files</option>
          <option value="mail">mail</option>
          <option value="media">media</option>
          <option value="screen">screen</option>
        </select>
      </div>
      <div class="fgroup">
        <div class="flabel">Type filter</div>
        <input id="s-type" type="text" placeholder="FILE_PDF · MAIL_THREAD · MEDIA_VIDEO">
      </div>
      <div class="fgroup">
        <div class="flabel">Related to global_id</div>
        <input id="s-rel" type="text" placeholder="files/abc123...">
      </div>
      <button onclick="doSearch()">Search HELEN memory</button>
      <div class="result scroll" id="s-result"><span class="dim">No search yet.</span></div>
    </div>

    <div class="pane" id="pane-render">
      <div class="fgroup">
        <div class="flabel">Object global_id</div>
        <input id="v-id" type="text" placeholder="files/abc123...">
      </div>
      <div class="fgroup">
        <div class="flabel">Renderer</div>
        <input id="v-renderer" type="text" value="DEFAULT">
      </div>
      <button onclick="doRender()">Render system view</button>
      <div class="result dim" id="v-result">No render requested yet.</div>
    </div>

    <div class="pane" id="pane-relate">
      <div class="fgroup">
        <div class="flabel">First object global_id</div>
        <input id="r-a" type="text" placeholder="files/abc123...">
      </div>
      <div class="fgroup">
        <div class="flabel">Relation type</div>
        <select id="r-type">
          {% for rt in relation_types %}<option>{{ rt }}</option>{% endfor %}
        </select>
      </div>
      <div class="fgroup">
        <div class="flabel">Second object global_id</div>
        <input id="r-b" type="text" placeholder="mail/def456...">
      </div>
      <div class="fgroup">
        <div class="flabel">Receipt</div>
        <input id="r-receipt" type="text" placeholder="user:connect:2026-05-06">
      </div>
      <button onclick="doRelate()">Connect two objects</button>
      <div class="result dim" id="r-result">No relation created yet.</div>
    </div>
  </section>

  <div class="section-title">Witness Mode</div>
  <section class="witness-grid">
    <div class="witness-card">
      <div class="witness-label">API status</div>
      <div class="witness-value ok" id="api-status">checking...</div>
    </div>
    <div class="witness-card">
      <div class="witness-label">Object count</div>
      <div class="witness-value" id="w-object-count">—</div>
    </div>
    <div class="witness-card">
      <div class="witness-label">Last action</div>
      <div class="witness-value" id="w-last-action">—</div>
    </div>
    <div class="witness-card">
      <div class="witness-label">Last receipt</div>
      <div class="witness-value" id="w-last-receipt">—</div>
    </div>
    <div class="witness-card">
      <div class="witness-label">Last error</div>
      <div class="witness-value err" id="w-last-error">—</div>
    </div>
    <div class="witness-card">
      <div class="witness-label">Graph hash</div>
      <div class="witness-value" id="graph-hash">—</div>
    </div>
  </section>

  <section class="stats">
    <div class="stat-cell"><div class="label">nodes</div>
      <div class="value" id="stat-nodes" style="color:var(--blue)">—</div></div>
    <div class="stat-cell"><div class="label">receipts</div>
      <div class="value" id="stat-receipts" style="color:var(--green)">—</div></div>
    <div class="stat-cell"><div class="label">renders</div>
      <div class="value" id="stat-renders" style="color:var(--violet)">—</div></div>
    <div class="stat-cell"><div class="label">events</div>
      <div class="value" id="stat-events" style="color:var(--yellow)">—</div></div>
  </section>

  <div id="ns-strip"></div>

  <details class="advanced">
    <summary>Operator detail: graph and event log</summary>
    <div class="section-title">Graph</div>
    <div class="scroll" id="node-list"><span class="dim">empty</span></div>
    <div class="section-title">Log</div>
    <div class="scroll" id="event-log"><span class="dim">no events yet</span></div>
  </details>
</main>

<script>
const S = {ACCEPT:'ok', REJECT:'err', QUARANTINE:'warn', DEGRADE:'warn'};

function switchAction(name) {
  document.querySelectorAll('.action-card').forEach(card => {
    card.classList.toggle('active', card.dataset.target === name);
  });
  document.querySelectorAll('.pane').forEach(p => {
    p.classList.toggle('active', p.id === 'pane-'+name);
  });
}

async function fetchState() {
  let d;
  try {
    d = await (await fetch('/api/state')).json();
    document.getElementById('api-status').textContent = 'online';
  } catch (e) {
    document.getElementById('api-status').textContent = 'offline';
    document.getElementById('api-status').className = 'witness-value err';
    return;
  }
  document.getElementById('stat-nodes').textContent = d.node_count;
  document.getElementById('stat-receipts').textContent = d.receipt_count;
  document.getElementById('stat-renders').textContent = d.render_log_count;
  document.getElementById('stat-events').textContent = d.event_count;
  document.getElementById('w-object-count').textContent = d.node_count;
  document.getElementById('w-last-action').textContent = d.last_action || '—';
  document.getElementById('w-last-receipt').textContent = d.last_receipt || '—';
  document.getElementById('w-last-error').textContent = d.last_error || '—';
  document.getElementById('graph-hash').textContent = (d.graph_hash||'').slice(0,18)+'...';

  const ns = document.getElementById('ns-strip');
  ns.innerHTML = Object.entries(d.namespaces||{}).map(([k,v]) =>
    `<span class="ns-pill">${k} <b>${v}</b></span>`
  ).join('') || '<span class="dim" style="font-size:11px">no objects yet</span>';

  // node list
  document.getElementById('node-list').innerHTML = (d.nodes||[]).length
    ? d.nodes.map(n =>
        `<div class="node-item">
          <span class="node-id" title="${n.global_id}">${n.global_id}</span>
          <span class="node-type">${n.type}</span>
        </div>`).join('')
    : '<span class="dim">empty graph</span>';

  // event log
  document.getElementById('event-log').innerHTML = (d.events||[]).length
    ? [...d.events].reverse().map(e => {
        const cls = S[e.status]||'dim';
        return `<div class="ev-row">
          <span class="ev-t">${e.t}</span>
          <span class="${cls}">${e.status}</span>
          <span class="ev-type">${e.type} <span class="dim">${e.detail||''}</span></span>
        </div>`;
      }).join('')
    : '<span class="dim">no events</span>';
}

async function doIngest() {
  let raw = document.getElementById('i-raw').value.trim();
  const receipt = document.getElementById('i-receipt').value.trim();
  const type = document.getElementById('i-type').value;
  let signal;
  if (type==='file') { signal = raw; }
  else {
    try { signal = JSON.parse(raw); } catch { signal = {signal:type.toUpperCase(),data:raw}; }
    if (!signal.signal) signal.signal = type.toUpperCase();
  }
  const d = await (await fetch('/api/ingest',{
    method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({raw:signal,receipt})
  })).json();
  const cls = S[d.status]||'err';
  document.getElementById('i-result').innerHTML =
    `<span class="${cls}">${d.status}</span> <span class="dim">${d.global_id||''}</span><br>`+
    `<span class="dim">${d.reason||''}</span>`;
  fetchState();
}

function renderSlice(d, id) {
  const el = document.getElementById(id);
  if (d.error) { el.innerHTML=`<span class="err">${d.error}</span>`; return; }
  const rows = Object.entries(d.nodes||{}).map(([gid,info]) =>
    `<div class="node-item">
      <span class="node-id">${gid}</span>
      <span class="node-type">${info.type}</span>
    </div>`).join('');
  el.innerHTML = `<div class="ok" style="margin-bottom:6px">${d.node_count} node(s)</div>${rows||'<span class="dim">no matches</span>'}`;
}

async function doOpen() {
  const ns=document.getElementById('o-ns').value;
  const tp=document.getElementById('o-type').value.trim();
  const intent={};
  if(ns) intent.namespace_filter=ns;
  if(tp) intent.type_filter=tp;
  const d = await (await fetch('/api/open',{
    method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({intent})
  })).json();
  renderSlice(d,'o-result'); fetchState();
}

async function doSearch() {
  const ns=document.getElementById('s-ns').value;
  const tp=document.getElementById('s-type').value.trim();
  const rel=document.getElementById('s-rel').value.trim();
  const query={};
  if(ns) query.namespace_filter=ns;
  if(tp) query.type_filter=tp;
  if(rel) query.relation_to=rel;
  const d = await (await fetch('/api/search',{
    method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({query})
  })).json();
  renderSlice(d,'s-result'); fetchState();
}

async function doRender() {
  const gid=document.getElementById('v-id').value.trim();
  const renderer=document.getElementById('v-renderer').value.trim() || 'DEFAULT';
  if(!gid) {
    document.getElementById('v-result').innerHTML='<span class="err">Missing object global_id</span>';
    return;
  }
  const d = await (await fetch(`/api/render/${encodeURIComponent(gid)}?renderer=${encodeURIComponent(renderer)}`)).json();
  const el=document.getElementById('v-result');
  if(d.error) {
    el.innerHTML=`<span class="err">${d.error}</span>`;
  } else {
    el.innerHTML=`<span class="ok">rendered</span><br><span class="dim">authority: ${d.authority}</span><br><span class="dim">receipt: ${d.receipt||'—'}</span>`;
  }
  fetchState();
}

async function doRelate() {
  const a=document.getElementById('r-a').value.trim();
  const b=document.getElementById('r-b').value.trim();
  const t=document.getElementById('r-type').value;
  const r=document.getElementById('r-receipt').value.trim();
  const d = await (await fetch('/api/relate',{
    method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({id_a:a,id_b:b,relation_type:t,receipt:r})
  })).json();
  const cls=S[d.status]||'err';
  document.getElementById('r-result').innerHTML=
    `<span class="${cls}">${d.status}</span> <span class="dim">${d.reason||''}</span>`;
  fetchState();
}

fetchState();
setInterval(fetchState, 6000);
</script>
</body>
</html>"""


# ── Routes ────────────────────────────────────────────────────────────────────

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
    last_event = EVENTS[-1] if EVENTS else {}
    last_error = next((e for e in reversed(EVENTS) if e.get("status") == REJECT), {})
    last_receipt = next((e.get("receipt") for e in reversed(EVENTS) if e.get("receipt")), None)
    return jsonify({
        "node_count": state.node_count,
        "receipt_count": state.receipt_count,
        "render_log_count": state.render_log_count,
        "graph_hash": state.graph_hash,
        "event_count": len(EVENTS),
        "last_action": last_event.get("type"),
        "last_receipt": last_receipt,
        "last_error": last_error.get("detail"),
        "namespaces": ns,
        "nodes": nodes,
        "events": EVENTS[-60:],
    })


@app.route("/api/ingest", methods=["POST"])
def api_ingest():
    b = request.get_json(force=True)
    try:
        r = SESSION.ingest(b.get("raw", ""), b.get("receipt", ""))
        _log("ingest", str(b.get("raw", ""))[:60], r.status,
             {"global_id": r.global_id, "receipt": b.get("receipt", "")})
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
    try:
        r = SESSION.relate(b.get("id_a",""), b.get("id_b",""),
                           b.get("relation_type",""), b.get("receipt",""))
        _log("relate", f"{b.get('id_a','')[:20]}→{b.get('id_b','')[:20]}", r.status,
             {"receipt": b.get("receipt", "")})
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
        _log("render", global_id, ADMIT, {"receipt": env.session_receipt})
        return jsonify({"authority": env.authority, "receipt": env.session_receipt,
                        "node_count": env.slice.node_count})
    except KeyError:
        return jsonify({"error": f"{global_id} not found"}), 404


# ── Entry ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("HELEN_SEMANTIC_PORT", 5003))
    # find local IP for device URL
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "localhost"

    print(f"\nHELEN · semantic dashboard")
    print(f"→ http://localhost:{port}  (this machine)")
    print(f"→ http://{local_ip}:{port}  (iPhone / laptop — same Wi-Fi)")
    print(f"→ 5 verbs: ingest · open · search · render · relate")
    print(f"→ NO RECEIPT = NO CLAIM\n")
    app.run(host="0.0.0.0", port=port, debug=False)

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
<title>HELEN</title>
<style>
:root {
  --bg:#0a0a10; --panel:#111827; --border:#1f2937;
  --indigo:#6366f1; --green:#34d399; --red:#f87171;
  --yellow:#fbbf24; --purple:#a78bfa; --muted:#6b7280;
  --text:#e2e8f0; --mono:'SF Mono','Fira Code',monospace;
  --safe-top: env(safe-area-inset-top);
  --safe-bottom: env(safe-area-inset-bottom);
}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:var(--mono);font-size:13px;
     padding:env(safe-area-inset-top) env(safe-area-inset-right)
             env(safe-area-inset-bottom) env(safe-area-inset-left)}

/* top bar */
#topbar{background:#0d0d1a;border-bottom:1px solid var(--indigo);
        padding:10px 16px;display:flex;align-items:center;justify-content:space-between;
        position:sticky;top:0;z-index:100}
#topbar .logo{color:var(--indigo);font-weight:700;font-size:16px;letter-spacing:.05em}
#topbar .hash{color:var(--muted);font-size:10px}

/* stat strip */
#stats{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--border);
       border-bottom:1px solid var(--border)}
.stat-cell{background:var(--panel);padding:10px 8px;text-align:center}
.stat-cell .label{font-size:9px;color:var(--muted);text-transform:uppercase;
                  letter-spacing:.08em;margin-bottom:4px}
.stat-cell .value{font-size:20px;font-weight:700}

/* namespace strip */
#ns-strip{padding:8px 12px;display:flex;flex-wrap:wrap;gap:6px;
          border-bottom:1px solid var(--border);min-height:36px;background:var(--panel)}
.ns-pill{background:#1e2035;color:#a5b4fc;padding:3px 10px;border-radius:12px;font-size:11px}

/* tabs */
#tabs{display:flex;background:#0d0d1a;border-bottom:1px solid var(--border);
      position:sticky;top:45px;z-index:99}
.tab{flex:1;padding:10px 4px;text-align:center;font-size:11px;color:var(--muted);
     cursor:pointer;border-bottom:2px solid transparent;transition:.15s}
.tab.active{color:var(--indigo);border-bottom-color:var(--indigo)}

/* panes */
.pane{display:none;padding:14px 12px}
.pane.active{display:block}

/* form helpers */
.fgroup{margin-bottom:12px}
.flabel{font-size:10px;color:var(--muted);text-transform:uppercase;
        letter-spacing:.06em;margin-bottom:5px}
input,select,textarea{background:#0a0a10;border:1px solid var(--border);
  border-radius:6px;color:var(--text);padding:9px 11px;width:100%;
  font-family:var(--mono);font-size:13px;-webkit-appearance:none}
input:focus,select:focus{outline:none;border-color:var(--indigo)}
button{background:var(--indigo);color:#fff;border:none;border-radius:6px;
       padding:10px 20px;font-family:var(--mono);font-size:13px;
       cursor:pointer;width:100%;font-weight:600;margin-top:4px}
button:active{background:#4338ca}
.btn-row{display:flex;gap:8px}
.btn-row button{flex:1}

/* result box */
.result{margin-top:10px;padding:10px;background:var(--panel);border-radius:6px;
        font-size:11px;min-height:36px;border:1px solid var(--border)}
.ok{color:var(--green)} .err{color:var(--red)} .warn{color:var(--yellow)}
.dim{color:var(--muted)}

/* node list */
.node-item{padding:8px 0;border-bottom:1px solid var(--border);display:flex;
           align-items:center;gap:8px}
.node-id{color:#a5b4fc;font-size:11px;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.node-type{color:var(--muted);font-size:10px;flex-shrink:0}

/* event row */
.ev-row{padding:5px 0;border-bottom:1px solid var(--border);
        display:grid;grid-template-columns:56px 56px 1fr;gap:6px;font-size:10px}
.ev-t{color:var(--muted)} .ev-type{color:#a5b4fc}

/* scrollable areas */
.scroll{max-height:55vh;overflow-y:auto}

::-webkit-scrollbar{width:3px}
::-webkit-scrollbar-thumb{background:var(--border)}

/* mobile-friendly select arrow */
select{background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath fill='%236b7280' d='M4 6l4 4 4-4z'/%3E%3C/svg%3E");
       background-repeat:no-repeat;background-position:right 10px center;
       background-size:16px;padding-right:32px}
</style>
</head>
<body>

<div id="topbar">
  <span class="logo">HELEN</span>
  <span class="hash" id="graph-hash">—</span>
</div>

<div id="stats">
  <div class="stat-cell"><div class="label">nodes</div>
    <div class="value" id="s-nodes" style="color:var(--indigo)">—</div></div>
  <div class="stat-cell"><div class="label">receipts</div>
    <div class="value" id="s-receipts" style="color:var(--green)">—</div></div>
  <div class="stat-cell"><div class="label">renders</div>
    <div class="value" id="s-renders" style="color:var(--purple)">—</div></div>
  <div class="stat-cell"><div class="label">events</div>
    <div class="value" id="s-events" style="color:var(--yellow)">—</div></div>
</div>

<div id="ns-strip"></div>

<div id="tabs">
  <div class="tab active" onclick="switchTab('ingest')">ingest</div>
  <div class="tab" onclick="switchTab('open')">open</div>
  <div class="tab" onclick="switchTab('relate')">relate</div>
  <div class="tab" onclick="switchTab('graph')">graph</div>
  <div class="tab" onclick="switchTab('log')">log</div>
</div>

<!-- INGEST -->
<div class="pane active" id="pane-ingest">
  <div class="fgroup">
    <div class="flabel">signal type</div>
    <select id="i-type">
      <option value="file">FILE · path</option>
      <option value="mail">MAIL · envelope</option>
      <option value="media">MEDIA · metadata</option>
      <option value="screen">SCREEN · region</option>
    </select>
  </div>
  <div class="fgroup">
    <div class="flabel">raw signal — path or JSON</div>
    <input id="i-raw" type="text" placeholder="/path/to/file.pdf  or  {...}">
  </div>
  <div class="fgroup">
    <div class="flabel">receipt — required</div>
    <input id="i-receipt" type="text" placeholder="user:open:2026-05-06">
  </div>
  <button onclick="doIngest()">ingest</button>
  <div class="result dim" id="i-result">—</div>
</div>

<!-- OPEN / SEARCH -->
<div class="pane" id="pane-open">
  <div class="fgroup">
    <div class="flabel">namespace</div>
    <select id="o-ns">
      <option value="">— all —</option>
      <option value="files">files</option>
      <option value="mail">mail</option>
      <option value="media">media</option>
      <option value="screen">screen</option>
    </select>
  </div>
  <div class="fgroup">
    <div class="flabel">type filter</div>
    <input id="o-type" type="text" placeholder="FILE_PDF · MAIL_THREAD · MEDIA_VIDEO">
  </div>
  <div class="fgroup">
    <div class="flabel">relation to (global_id)</div>
    <input id="o-rel" type="text" placeholder="files/abc123…">
  </div>
  <div class="btn-row">
    <button onclick="doOpen()">open</button>
    <button onclick="doSearch()">search</button>
  </div>
  <div class="result scroll" id="o-result"><span class="dim">—</span></div>
</div>

<!-- RELATE -->
<div class="pane" id="pane-relate">
  <div class="fgroup">
    <div class="flabel">id_a (global_id)</div>
    <input id="r-a" type="text" placeholder="files/abc123…">
  </div>
  <div class="fgroup">
    <div class="flabel">relation type</div>
    <select id="r-type">
      {% for rt in relation_types %}<option>{{ rt }}</option>{% endfor %}
    </select>
  </div>
  <div class="fgroup">
    <div class="flabel">id_b (global_id)</div>
    <input id="r-b" type="text" placeholder="mail/def456…">
  </div>
  <div class="fgroup">
    <div class="flabel">receipt — required</div>
    <input id="r-receipt" type="text" placeholder="user:link:2026-05-06">
  </div>
  <button onclick="doRelate()">relate</button>
  <div class="result dim" id="r-result">—</div>
</div>

<!-- GRAPH -->
<div class="pane" id="pane-graph">
  <div class="scroll" id="node-list"><span class="dim">empty</span></div>
</div>

<!-- LOG -->
<div class="pane" id="pane-log">
  <div class="scroll" id="event-log"><span class="dim">no events yet</span></div>
</div>

<script>
const S = {ACCEPT:'ok', REJECT:'err', QUARANTINE:'warn', DEGRADE:'warn'};

function switchTab(name) {
  document.querySelectorAll('.tab').forEach((t,i) => {
    const names=['ingest','open','relate','graph','log'];
    t.classList.toggle('active', names[i]===name);
  });
  document.querySelectorAll('.pane').forEach(p => {
    p.classList.toggle('active', p.id === 'pane-'+name);
  });
}

async function fetchState() {
  const d = await (await fetch('/api/state')).json();
  document.getElementById('s-nodes').textContent = d.node_count;
  document.getElementById('s-receipts').textContent = d.receipt_count;
  document.getElementById('s-renders').textContent = d.render_log_count;
  document.getElementById('s-events').textContent = d.event_count;
  document.getElementById('graph-hash').textContent = (d.graph_hash||'').slice(0,14)+'…';

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
  const ns=document.getElementById('o-ns').value;
  const tp=document.getElementById('o-type').value.trim();
  const rel=document.getElementById('o-rel').value.trim();
  const query={};
  if(ns) query.namespace_filter=ns;
  if(tp) query.type_filter=tp;
  if(rel) query.relation_to=rel;
  const d = await (await fetch('/api/search',{
    method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({query})
  })).json();
  renderSlice(d,'o-result'); fetchState();
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
    try:
        r = SESSION.ingest(b.get("raw", ""), b.get("receipt", ""))
        _log("ingest", str(b.get("raw", ""))[:60], r.status,
             {"global_id": r.global_id})
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

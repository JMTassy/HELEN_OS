#!/usr/bin/env python3
"""
HELEN OS Dashboard — local, persistent, real data.
Reads actual ledger, kernel state, GOBLIN batches, terminal receipts.

Run:
    python oracle_town/skills/ops/helen_dashboard/server.py
    open http://localhost:7000

authority=NON_SOVEREIGN  canon=NO_SHIP
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

try:
    from flask import Flask, jsonify, request, send_from_directory
except ImportError:
    raise SystemExit("pip install flask")

import sys as _sys
_BRIDGE_DIR = Path(__file__).resolve().parent.parent / "airi_helen_avatar" / "scripts"
_sys.path.insert(0, str(_BRIDGE_DIR))
try:
    from airi_bridge import get_bridge as _get_airi_bridge
    _AIRI_AVAILABLE = True
except ImportError:
    _AIRI_AVAILABLE = False

import uuid as _uuid

SOT = Path(__file__).resolve().parent.parent.parent.parent.parent
_airi = _get_airi_bridge() if _AIRI_AVAILABLE else None
KERNEL_DIR   = SOT / "experiments" / "helen_os_v02"
MEMORY_DIR   = SOT / "oracle_town" / "memory"
LTM_FILE     = MEMORY_DIR / "long_term_memory.jsonl"
RECEIPTS_FILE= MEMORY_DIR / "sovereign_ledger.jsonl"
CONTEXT_FILE = MEMORY_DIR / "active_context.md"
GOBLIN_DIR = SOT / "oracle_town" / "skills" / "ops" / "dan_goblin"
TERMINAL_DIR = SOT / "oracle_town" / "skills" / "ops" / "helen_terminal"
STATIC_DIR = Path(__file__).resolve().parent / "static"

app = Flask(__name__, static_folder=str(STATIC_DIR))


# ── helpers ───────────────────────────────────────────────────────────────────

def _read_ndjson(path: Path, tail: int = 50) -> list[dict]:
    if not path.exists():
        return []
    lines = [l for l in path.read_text().splitlines() if l.strip()]
    return [json.loads(l) for l in lines[-tail:]]


def _read_json(path: Path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


# ── API endpoints ─────────────────────────────────────────────────────────────

@app.route("/api/kernel")
def api_kernel():
    state = _read_json(KERNEL_DIR / "data" / "state.json", {})
    ledger = _read_ndjson(KERNEL_DIR / "data" / "ledger.ndjson", tail=30)
    receipts = list((KERNEL_DIR / "data" / "receipts").glob("*.json")) if (KERNEL_DIR / "data" / "receipts").exists() else []
    return jsonify({
        "state": state,
        "ledger_events": ledger,
        "ledger_count": len(_read_ndjson(KERNEL_DIR / "data" / "ledger.ndjson", tail=10000)),
        "receipt_count": len(receipts),
        "mayor_verdict": "NO_SHIP",
    })


@app.route("/api/goblin")
def api_goblin():
    batches_dir = GOBLIN_DIR / "brainstorm" / "batches"
    receipts_dir = GOBLIN_DIR / "receipts"

    batches = []
    if batches_dir.exists():
        for jsonl in sorted(batches_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]:
            lines = [json.loads(l) for l in jsonl.read_text().splitlines() if l.strip()]
            valid = [e for e in lines if "her_scoring" in e]
            if not valid:
                continue
            scores = sorted(valid, key=lambda e: e["her_scoring"]["score"], reverse=True)
            batches.append({
                "batch_id": jsonl.stem.split("_tranche")[0],
                "file": jsonl.name,
                "epoch_count": len(valid),
                "top_score": scores[0]["her_scoring"]["score"] if scores else 0,
                "top_epoch": scores[0]["epoch_index"] if scores else 0,
                "top_statement": scores[0]["communication_act"]["statement"][:120] if scores else "",
                "hal_pass": sum(1 for e in valid if e["hal_verdict"]["verdict"] == "PASS"),
                "hal_warn": sum(1 for e in valid if e["hal_verdict"]["verdict"] == "WARN"),
                "hal_block": sum(1 for e in valid if e["hal_verdict"]["verdict"] == "BLOCK"),
                "provider": valid[0].get("provider", "unknown") if valid else "unknown",
                "model": valid[0].get("model", "unknown") if valid else "unknown",
            })

    tranche_receipts = []
    if receipts_dir.exists():
        for rf in sorted(receipts_dir.glob("BATCH_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]:
            r = _read_json(rf, {})
            tranche_receipts.append({
                "tranche_id": r.get("tranche_id", rf.stem),
                "batch_id": r.get("batch_id", ""),
                "epochs_run": r.get("epochs_run", 0),
                "reducer_decision": r.get("reducer_decision"),
                "hal_summary": r.get("hal_summary", {}),
                "provider": r.get("provider", "unknown"),
                "backend_signature": r.get("backend_signature", ""),
                "timestamp": r.get("timestamp", ""),
            })

    return jsonify({"batches": batches, "tranche_receipts": tranche_receipts})


@app.route("/api/terminal")
def api_terminal():
    ledger = _read_ndjson(TERMINAL_DIR / "data" / "ledger.ndjson", tail=20)
    receipts_dir = TERMINAL_DIR / "data" / "receipts"
    receipt_count = len(list(receipts_dir.glob("*.json"))) if receipts_dir.exists() else 0
    pending_dir = TERMINAL_DIR / "data" / "pending_edits"
    pending = list(pending_dir.glob("EP-*.json")) if pending_dir.exists() else []
    pending_data = [_read_json(p, {}) for p in sorted(pending, key=lambda x: x.stat().st_mtime, reverse=True)[:5]]
    return jsonify({
        "ledger_events": ledger,
        "receipt_count": receipt_count,
        "pending_edits": [p for p in pending_data if p.get("status") == "PENDING_CONFIRM"],
    })


@app.route("/api/status")
def api_status():
    return jsonify({
        "sot": str(SOT),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "authority": "NON_SOVEREIGN",
        "canon": "NO_SHIP",
        "kernel_version": "v0.3",
        "components": {
            "kernel": (KERNEL_DIR / "data" / "ledger.ndjson").exists(),
            "goblin": (GOBLIN_DIR / "brainstorm" / "batches").exists(),
            "terminal": (TERMINAL_DIR / "data").exists(),
        }
    })


@app.route("/api/semantic")
def api_semantic():
    objects = []

    # Kernel ledger events
    ledger = _read_ndjson(KERNEL_DIR / "data" / "ledger.ndjson", tail=40)
    for e in ledger:
        p = e.get("payload", {})
        subj = p.get("op") or e.get("event_type", "event")
        objects.append({
            "id": e.get("event_id", f"k-{len(objects)}"),
            "type": "EVENT",
            "subject": subj,
            "relations": [e.get("event_type", "")],
            "confidence": 0.90,
            "receipts": 1,
            "timestamp": e.get("timestamp_utc", ""),
            "provenance": "kernel",
            "sovereign": True,
            "hash": (e.get("event_hash") or e.get("payload_hash") or "")[:12],
        })

    # GOBLIN top epochs
    batches_dir = GOBLIN_DIR / "brainstorm" / "batches"
    if batches_dir.exists():
        for jsonl in sorted(batches_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)[:2]:
            lines = [json.loads(l) for l in jsonl.read_text().splitlines() if l.strip()]
            valid = [e for e in lines if "her_scoring" in e]
            top = sorted(valid, key=lambda e: e["her_scoring"]["score"], reverse=True)[:15]
            for e in top:
                stmt = e.get("communication_act", {}).get("statement", "epoch")
                objects.append({
                    "id": f"g-{jsonl.stem[:8]}-{e['epoch_index']}",
                    "type": "EPOCH",
                    "subject": stmt[:70],
                    "relations": ["her_scoring", "hal_verdict"],
                    "confidence": round(e["her_scoring"]["score"], 3),
                    "receipts": 1 if e["hal_verdict"]["verdict"] == "PASS" else 0,
                    "timestamp": e.get("timestamp", ""),
                    "provenance": "goblin",
                    "sovereign": False,
                    "hash": "",
                })

    # Terminal ledger
    terminal_ledger = _read_ndjson(TERMINAL_DIR / "data" / "ledger.ndjson", tail=10)
    for e in terminal_ledger:
        p = e.get("payload", {})
        objects.append({
            "id": e.get("event_id", f"t-{len(objects)}"),
            "type": "ACTION",
            "subject": p.get("action_type", "terminal_action"),
            "relations": ["receipt", "policy"],
            "confidence": 0.95,
            "receipts": 1,
            "timestamp": e.get("timestamp_utc", ""),
            "provenance": "terminal",
            "sovereign": False,
            "hash": (e.get("event_hash") or "")[:12],
        })

    # Edges: temporal within same provenance, top-conf cross links
    edges = []
    by_prov = {}
    for o in objects:
        by_prov.setdefault(o["provenance"], []).append(o)
    for prov, obs in by_prov.items():
        for i in range(len(obs) - 1):
            edges.append({"source": obs[i]["id"], "target": obs[i + 1]["id"], "weight": 0.4})
    top_conf = sorted(objects, key=lambda o: o["confidence"], reverse=True)[:6]
    for i in range(len(top_conf) - 1):
        if top_conf[i]["provenance"] != top_conf[i + 1]["provenance"]:
            edges.append({"source": top_conf[i]["id"], "target": top_conf[i + 1]["id"], "weight": 0.7})

    return jsonify({"objects": objects, "edges": edges[:80]})


SKILLS = [
    {"id": "video_studio",   "label": "Video Studio", "icon": "🎬", "domain": "media",       "status": "ready",
     "description": "Créer vidéos, scripts, storyboards, reels, ads.",
     "actions": ["write_script", "generate_storyboard", "create_voiceover", "export_prompt", "publish_plan"]},
    {"id": "jmt_admin",      "label": "JMT Admin",    "icon": "🧾", "domain": "admin",       "status": "ready",
     "description": "Factures, devis, documents société, suivi administratif.",
     "actions": ["create_invoice", "create_quote", "draft_contract", "admin_report", "document_archive"]},
    {"id": "client_crm",     "label": "Clients",      "icon": "👥", "domain": "crm",         "status": "ready",
     "description": "CRM léger : contacts, opportunités, relances, notes.",
     "actions": ["add_contact", "log_interaction", "set_followup", "build_opportunity", "generate_brief"]},
    {"id": "offer_builder",  "label": "Offers",       "icon": "📦", "domain": "sales",       "status": "ready",
     "description": "Offres commerciales, packs consulting, propositions PDF.",
     "actions": ["build_consulting_pack", "draft_proposal", "create_pitch", "price_offer", "export_pdf_brief"]},
    {"id": "content_engine", "label": "Content",      "icon": "📣", "domain": "content",     "status": "ready",
     "description": "Posts LinkedIn, newsletters, pages de vente, campagnes.",
     "actions": ["write_linkedin_post", "draft_newsletter", "build_landing_page", "write_campaign", "repurpose_content"]},
    {"id": "research_brief", "label": "Research",     "icon": "🧠", "domain": "intelligence","status": "ready",
     "description": "Recherche stratégique, veille, synthèse, benchmark.",
     "actions": ["run_scan", "synthesize_brief", "build_benchmark", "extract_signals", "write_report"]},
    {"id": "calendar_ops",   "label": "Calendar",     "icon": "📅", "domain": "ops",         "status": "ready",
     "description": "Planning, rendez-vous, deadlines, follow-up.",
     "actions": ["log_appointment", "set_deadline", "plan_week", "flag_followup", "review_calendar"]},
    {"id": "sovereign_ledger","label": "Ledger",      "icon": "🏛️", "domain": "governance",  "status": "active",
     "description": "Historique des actions, décisions, preuves, receipts.",
     "actions": ["inspect_receipt", "list_events", "verify_chain", "query_verdict", "export_summary"]},
]

@app.route("/api/context")
def api_context():
    ctx = CONTEXT_FILE.read_text(encoding="utf-8") if CONTEXT_FILE.exists() else ""
    return jsonify({
        "active_context": ctx,
        "memory_file": str(LTM_FILE),
        "ledger_file": str(RECEIPTS_FILE),
        "authority": "NON_SOVEREIGN",
    })


@app.route("/api/memory", methods=["GET"])
def api_memory_get():
    memories = _read_ndjson(LTM_FILE, tail=100)
    memories.sort(key=lambda m: m.get("importance", 0), reverse=True)
    return jsonify({"memories": memories, "count": len(memories), "authority": "NON_SOVEREIGN"})


@app.route("/api/memory", methods=["POST"])
def api_memory_post():
    data = request.get_json(silent=True) or {}
    now = datetime.now(timezone.utc).isoformat()
    entry = {
        "id": data.get("id") or f"mem_{now[:10].replace('-','')}_{_uuid.uuid4().hex[:6]}",
        "type": data.get("type", "fact"),
        "content": data.get("content", ""),
        "importance": float(data.get("importance", 0.7)),
        "tags": data.get("tags", []),
        "source": data.get("source", "manual"),
        "created_at": now,
        "updated_at": now,
    }
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    with LTM_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return jsonify({"ok": True, "id": entry["id"]}), 201


@app.route("/api/ledger", methods=["GET"])
def api_ledger_get():
    receipts = _read_ndjson(RECEIPTS_FILE, tail=50)
    receipts.sort(key=lambda r: r.get("created_at", ""), reverse=True)
    return jsonify({"receipts": receipts, "count": len(receipts), "authority": "NON_SOVEREIGN"})


@app.route("/api/receipt", methods=["POST"])
def api_receipt_post():
    data = request.get_json(silent=True) or {}
    now = datetime.now(timezone.utc).isoformat()
    entry = {
        "id": data.get("id") or f"rcpt_{now[:10].replace('-','')}_{_uuid.uuid4().hex[:6]}",
        "skill_id": data.get("skill_id", "unknown"),
        "action": data.get("action", ""),
        "summary": data.get("summary", ""),
        "status": data.get("status", "draft"),
        "created_at": now,
        "artifacts": data.get("artifacts", []),
    }
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    with RECEIPTS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return jsonify({"ok": True, "id": entry["id"]}), 201


@app.route("/api/skills")
def api_skills():
    return jsonify({"skills": SKILLS, "authority": "NON_SOVEREIGN", "canon": "NO_SHIP"})


@app.route("/api/airi/status")
def api_airi_status():
    if _airi is None:
        return jsonify({"connected": False, "uri": "ws://localhost:6121/ws", "available": False})
    return jsonify({**_airi.status(), "available": True})


@app.route("/api/witness", methods=["POST"])
def api_witness():
    data = request.get_json(silent=True) or {}
    obj_type   = data.get("type", "OBJECT")
    subject    = data.get("subject", "")
    confidence = float(data.get("confidence", 0.0))
    provenance = data.get("provenance", "kernel")
    pushed = False
    if _airi is not None:
        pushed = _airi.push_witness(obj_type, subject, confidence, provenance)
    return jsonify({"pushed": pushed, "connected": _airi.connected if _airi else False})


@app.route("/avatar")
def avatar():
    portrait = SOT / "artifacts" / "video" / "ship_2e_helen_speaks" / "source" / "helen_source.png"
    return send_from_directory(str(portrait.parent), portrait.name)


@app.route("/")
def index():
    return send_from_directory(str(STATIC_DIR), "dashboard.html")


if __name__ == "__main__":
    STATIC_DIR.mkdir(exist_ok=True)
    print("HELEN OS Dashboard → http://localhost:7000")
    print(f"SOT: {SOT}")
    app.run(host="127.0.0.1", port=7700, debug=False)

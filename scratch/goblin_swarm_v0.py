#!/usr/bin/env python3
"""goblin_swarm_v0.py — sequential swarm of local GEMMA4 GOBLINS in ATTACK mode.

NON_SOVEREIGN | authority=false | sovereign=false | canon=false | ledger_effect=none

JM mark 2026-07-06: "launch a swarm of local GEMMA4 GOBLINS".
MAYOR routing: consumption-side, not generation-side — the outbox is starving
on the pen (30 unconsumed vs threshold 5), so goblins ATTACK existing packets
instead of generating new ones. Each unconsumed AR-*.json gets a
GOBLIN_OBJECTION_CARD_V0: strongest NO, weird failure mode, cheap falsifier.
Cards are pen-session material for JM. Cards decide nothing.

Laws: goblin proposes ⊬ admits · ND output is hashed (NO HASH = NO VOICE,
applied locally) · cards land in scratch/ only · ledger sleeps.
"""

import hashlib
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUTBOX = REPO / "temple" / "autoresearch" / "outbox"
RESOLVED = REPO / "temple" / "autoresearch" / "triage" / "resolved"
PEN_LOG = REPO / "temple" / "autoresearch" / "consumption_log.ndjson"
OUT_DIR = REPO / "scratch" / "goblin_objections"
LOG = REPO / "scratch" / "goblin_swarm_v0.log"
MODEL = "gemma4-12b:latest"
OLLAMA = "http://localhost:11434/api/generate"

PROMPT = """You are a GOBLIN in HELEN's warren. Garden layer: authority=false, \
proposals only, you may not admit anything, the ledger sleeps. Your job is ATTACK.

Attack this autoresearch packet as hard as you can. Output STRICT JSON with keys:
"strongest_no" (the best one-paragraph objection to acting on this packet),
"weird_failure_mode" (one strange way acting on it could backfire),
"cheap_falsifier" (one command or check under 5 minutes that could kill or confirm it),
"goblin_verdict_hint" ("ACT"|"REJECT"|"DEFER" — a hint, never a decision).

PACKET:
{packet}

JSON only, no prose around it."""


def log(msg: str) -> None:
    line = f"{datetime.now(timezone.utc).isoformat()} {msg}"
    print(line, flush=True)
    with LOG.open("a") as f:
        f.write(line + "\n")


def marks() -> set:
    got = set()
    if RESOLVED.is_dir():
        for f in RESOLVED.glob("*_marked.json"):
            try:
                got.add(json.loads(f.read_text())["packet_id"])
            except Exception:
                pass
    if PEN_LOG.is_file():
        for ln in PEN_LOG.read_text().splitlines():
            try:
                got.add(json.loads(ln)["packet_id"])
            except Exception:
                pass
    return got


def ask_gemma(prompt: str) -> str:
    body = json.dumps({
        "model": MODEL, "prompt": prompt, "stream": False,
        "options": {"temperature": 0.9, "num_predict": 400},
    }).encode()
    req = urllib.request.Request(OLLAMA, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read())["response"]


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    done_marks = marks()
    packets = sorted(OUTBOX.glob("AR-*.json"))
    todo = []
    for p in packets:
        pid = p.stem
        card = OUT_DIR / f"GOB-{pid}.json"
        if pid in done_marks or card.exists():
            continue
        todo.append(p)
    log(f"SWARM START model={MODEL} unattacked_unconsumed={len(todo)} "
        f"(outbox={len(packets)}, pen-marked={len(done_marks)})")

    ok, fail = 0, 0
    for i, p in enumerate(todo, 1):
        pid = p.stem
        try:
            packet = json.loads(p.read_text())
            compact = json.dumps({k: packet.get(k) for k in
                                  ("packet_id", "finding_type", "summary",
                                   "evidence", "risk_flags", "recommended_action")},
                                 ensure_ascii=False)
            t0 = time.time()
            resp = ask_gemma(PROMPT.format(packet=compact))
            dt = round(time.time() - t0, 1)
            card = {
                "schema": "GOBLIN_OBJECTION_CARD_V0",
                "packet_id": pid,
                "model": MODEL,
                "response_raw": resp,
                "response_sha256": hashlib.sha256(resp.encode()).hexdigest(),
                "elapsed_s": dt,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "authority": False, "sovereign": False, "canon": False,
                "ledger_effect": "none",
                "claim": "ATTACK_ONLY — hint ⊬ decision · goblin ⊬ pen",
            }
            (OUT_DIR / f"GOB-{pid}.json").write_text(
                json.dumps(card, ensure_ascii=False, indent=2))
            ok += 1
            log(f"[{i}/{len(todo)}] GOB-{pid} ok {dt}s")
        except Exception as e:
            fail += 1
            log(f"[{i}/{len(todo)}] GOB-{pid} FAIL {type(e).__name__}: {e}")
    log(f"SWARM DONE ok={ok} fail={fail} cards_dir={OUT_DIR}")


if __name__ == "__main__":
    main()

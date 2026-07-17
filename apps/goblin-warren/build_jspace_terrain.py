#!/usr/bin/env python3
"""build_jspace_terrain.py — the Measured Crossing (MEMBRANE_DISTANCE_WITNESS_V0).

Read-only builder, sibling of build_warren_home.py / build_warren_feed.py. It
joins the two hash-chained records nothing else diffs — the outbox (dreams) and
the operator's consumption log (marks) — into per-dream *membrane distance*: an
integer count of obligations still standing between a dream and the operator's
J-space collapse, with an irreducible floor of 1 while the dream is unjudged.

It makes "gate PASS ⊬ admission" a computed object the renderer proves on every
run, and it reads the frontier (dreams − marks), precedent (past marks of the
same shape), and age off the same join — with ZERO new writers, ZERO new
channels, and the sovereign-writer seam untouched.

  🟣 CLAIM · NON_SOVEREIGN · authority=false · ledger_effect=none · HOLD_FOR_OPERATOR

Laws honored:
  - SURFACE CANNOT MARK: this only READS organs and renders. It never marks;
    marks happen only through temple/autoresearch/operator_pen.py.
  - Deterministic: same organ bytes → same sidecar bytes. No wall clock, no
    randomness. Age is measured against a data-derived reference (the latest
    timestamp in the organs), never against "now". --check is a replay witness.
  - Fail-closed: a broken pen chain refuses to emit a witness (exit 1) — you do
    not measure distance across a corrupted mark chain.

Usage:
  python3 apps/goblin-warren/build_jspace_terrain.py            # → jspace_terrain.js
  python3 apps/goblin-warren/build_jspace_terrain.py --check    # replay witness
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTBOX = REPO_ROOT / "temple" / "autoresearch" / "outbox"
DEFAULT_PEN_LOG = REPO_ROOT / "temple" / "autoresearch" / "consumption_log.ndjson"
DEFAULT_OUT = Path(__file__).resolve().parent / "jspace_terrain.js"

sys.path.insert(0, str(REPO_ROOT / "temple" / "autoresearch"))
import operator_pen as pen  # noqa: E402


def _canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _iso(ts: str) -> str:
    # Normalize so datetime.fromisoformat works on Python 3.10 (no 'Z' support).
    return (ts or "").replace("Z", "+00:00")


def _age_days(ref: str, when: str):
    """Whole days from `when` to `ref`, both ISO. Data-derived — never wall clock."""
    from datetime import datetime
    try:
        a = datetime.fromisoformat(_iso(ref))
        b = datetime.fromisoformat(_iso(when))
        return (a - b).days
    except (ValueError, TypeError):
        return None


def _obligations(packet: dict, decided: bool, acted: bool) -> list:
    """Ordered obligations between this dream and its crossing. Each cites the
    invariant it stands on. The operator term is irreducible and always last."""
    obs = []
    is_bad = packet.get("finding_type") == "BAD_JSON"
    obs.append({
        "obligation": "readable",
        "cites": "NO HASH = NO VOICE",
        "met": not is_bad,
    })
    if packet.get("risk_flags"):
        obs.append({
            "obligation": "risk_flags_cleared",
            "cites": "gate PASS ⊬ admission",
            "met": bool(acted),
        })
    # Irreducible floor term: only the operator's collapse removes it.
    if not decided:
        obs.append({
            "obligation": "operator_decision",
            "cites": "JM decision ⊢ admin reality",
            "met": False,
        })
    return obs


def build_witness(outbox: Path, log: Path) -> dict:
    entries = pen.read_log(log)
    chain_break = pen.verify_chain(entries)
    eff = pen.effective_decisions(entries)
    packets = pen.load_packets(outbox)

    ftype = {p["packet_id"]: p.get("finding_type", "?") for p in packets}

    # Data-derived reference time for age: the latest timestamp anywhere in the
    # organs. Deterministic — a function of bytes on disk, not the clock.
    stamps = [str(p.get("scanned_at", "")) for p in packets] + \
             [str(e.get("at", "")) for e in entries]
    reference_time = max((s for s in stamps if s), default="")

    rows = []
    frontier = []
    for p in sorted(packets, key=lambda p: p["packet_id"]):
        pid = p["packet_id"]
        e = eff.get(pid)
        decided = e is not None
        acted = bool(e) and e.get("decision") == "acted"
        obs = _obligations(p, decided, acted)
        unmet = [o for o in obs if not o["met"]]
        if not decided:
            frontier.append(pid)
        precedent = [
            {"packet_id": pe["packet_id"], "decision": pe["decision"],
             "entry_hash": pe.get("entry_hash", "")}
            for pe in entries
            if ftype.get(pe["packet_id"]) == p.get("finding_type", "?")
            and pe["packet_id"] != pid
        ]
        rows.append({
            "packet_id": pid,
            "packet_sha256": p.get("_sha256", ""),
            "finding_type": p.get("finding_type", "?"),
            "state": (e.get("decision") if decided else "unjudged"),
            "effective_operator_decision": (
                {"decision": e["decision"], "entry_hash": e.get("entry_hash", ""),
                 "at": e.get("at", "")} if decided else None
            ),
            "remaining_obligations": obs,
            "distance": len(unmet),
            "age_days": _age_days(reference_time, str(p.get("scanned_at", ""))),
            "precedent_marks": precedent,
        })

    payload = {
        "schema": "MEMBRANE_DISTANCE_WITNESS_V0",
        "authority": False, "sovereign": False, "canon": False,
        "ledger_effect": "none", "claim_status": "NO_CLAIM",
        "reducer_required": True, "final": "HOLD_FOR_OPERATOR",
        "surface_can_mark": False,
        "law": ("distance is a rendering, never a mark; distance ⊬ admission; "
                "the floor is 1 while the pen is silent; marks happen only via "
                "operator_pen.py, never here."),
        "outbox_snapshot_hash": _sha256(_canon(
            sorted((p["packet_id"], p.get("_sha256", "")) for p in packets))),
        "consumption_log_head_hash": (entries[-1]["entry_hash"] if entries else pen.GENESIS),
        "chain_verified": chain_break is None,
        "chain_break": chain_break,
        "reference_time": reference_time,
        "frontier": {"count": len(frontier), "packet_ids": sorted(frontier)},
        "rows": rows,
    }
    payload["builder_run_hash"] = _sha256(_canon(payload))
    return payload


def render_js(payload: dict) -> str:
    return ("// jspace_terrain.js — GENERATED by build_jspace_terrain.py. DO NOT EDIT.\n"
            "// NON_SOVEREIGN · authority=false · ledger_effect=none · "
            "surface cannot mark · distance ⊬ admission\n"
            "window.jspaceTerrain = "
            + json.dumps(payload, indent=1, ensure_ascii=False, sort_keys=True)
            + ";\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--outbox", type=Path, default=DEFAULT_OUTBOX)
    ap.add_argument("--log", type=Path, default=DEFAULT_PEN_LOG)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--check", action="store_true",
                    help="replay witness: re-derive and compare on-disk sidecar")
    a = ap.parse_args()

    payload = build_witness(a.outbox, a.log)

    # Fail-closed: never assert distance across a corrupted mark chain.
    if not payload["chain_verified"]:
        print(f"🔴 PEN CHAIN BROKEN: {payload['chain_break']} — refusing to emit "
              f"(fail-closed). Repair the chain before measuring distance.")
        return 1

    js = render_js(payload)
    if a.check:
        on_disk = a.out.read_text(encoding="utf-8") if a.out.exists() else ""
        if on_disk != js:
            print("❌ REPLAY MISMATCH: sidecar differs from re-derivation")
            return 1
        print("✅ replay witness: sidecar matches organs")
        return 0

    a.out.write_text(js, encoding="utf-8")
    n_front = payload["frontier"]["count"]
    print(f"built {a.out.name}: {len(js)} bytes · dreams(rows)={len(payload['rows'])} · "
          f"frontier={n_front} · chain_verified=true · surface_can_mark=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

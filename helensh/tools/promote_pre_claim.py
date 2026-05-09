#!/usr/bin/env python3
"""
promote_pre_claim.py — Gate runner for the helensh promotion pipeline.

Reads helensh/sovereign/federated/claims/promotion_queue.jsonl and applies
the three-gate promotion rules from PROMOTION_POLICY_V1.md.

Gate A — AUTO:   OBSERVED / PROVEN / SHIPPED / KEEPER → receipt hash only
Gate B — REVIEW: DOCTRINE / ARCHITECTURE / MECHANISM  → MAYOR or GOVERNOR
Gate C — TEST:   INVARIANT / GAP / ATTACK_SURFACE     → experiment required

authority=NON_SOVEREIGN  canon=NO_SHIP
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

QUEUE = Path(__file__).resolve().parent.parent / "sovereign" / "federated" / "claims" / "promotion_queue.jsonl"

GATE_A_STATUS  = {"OBSERVED", "PROVEN", "SHIPPED", "KEEPER"}
GATE_B_CATEGORY = {"DOCTRINE", "ARCHITECTURE", "MECHANISM"}
GATE_C_CATEGORY = {"INVARIANT", "GAP", "ATTACK_SURFACE", "TEST"}
AUTO_REVIEW_CATEGORY = {"RHETORIC", "WORKED_EXAMPLE", "CONSTRAINT", "META"}


def _load() -> list[dict]:
    if not QUEUE.exists():
        return []
    return [json.loads(l) for l in QUEUE.read_text().splitlines() if l.strip()]


def _claim_hash(entry: dict) -> str:
    canonical = json.dumps(
        {k: entry[k] for k in sorted(entry) if k != "receipt_hash"},
        sort_keys=True, separators=(",", ":")
    ).encode()
    return hashlib.sha256(canonical).hexdigest()[:16]


def _gate(entry: dict) -> str:
    if entry.get("gate"):
        return entry["gate"]
    if entry.get("status") in GATE_A_STATUS:
        return "A"
    if entry.get("category") in GATE_B_CATEGORY:
        return "B"
    if entry.get("category") in GATE_C_CATEGORY:
        return "C"
    return "A"


def run_triage(verbose: bool = True) -> dict:
    entries = _load()
    results = {"total": len(entries), "gate_a": [], "gate_b": [], "gate_c": [], "unknown": []}

    for e in entries:
        gate = _gate(e)
        h = _claim_hash(e)
        summary = {
            "id": e["id"],
            "category": e.get("category", "?"),
            "status": e.get("status", "?"),
            "gate": gate,
            "decision": e.get("decision", "PENDING"),
            "claim_hash": h,
            "has_falsification": bool(e.get("falsification_test")),
            "has_evidence": bool(e.get("evidence")),
        }
        results[f"gate_{gate.lower()}"].append(summary)

    if verbose:
        print(f"\nPROMOTION QUEUE — {QUEUE.name}")
        print(f"Total entries: {results['total']}")
        print()

        for gate_key, label, desc in [
            ("gate_a", "GATE A — AUTO-PROMOTABLE", "receipt hash only"),
            ("gate_b", "GATE B — REVIEW-PROMOTABLE", "MAYOR / GOVERNOR review"),
            ("gate_c", "GATE C — TEST-PROMOTABLE", "experiment required"),
        ]:
            items = results[gate_key]
            print(f"  {label} ({len(items)} entries) — {desc}")
            pending = [i for i in items if i["decision"] == "PENDING"]
            auto   = [i for i in items if i["decision"] == "AUTO"]
            print(f"    PENDING: {len(pending)}   AUTO: {len(auto)}")
            for item in items:
                flag = "⚠" if (item["gate"] in ("B","C") and not item["has_falsification"]) else " "
                print(f"    {flag} [{item['decision'][:4]}] {item['id']:20} {item['category']:16} {item['status']}")
            print()

        # Surface Gate C items missing falsification
        missing_test = [i for i in results["gate_c"] if not i["has_falsification"]]
        if missing_test:
            print(f"  ⚠  Gate C entries missing falsification_test ({len(missing_test)}):")
            for i in missing_test:
                print(f"     {i['id']}")
            print()

    return results


def auto_promote(dry_run: bool = True) -> list[str]:
    """Promote Gate A entries that have decision=AUTO. Prints receipt hash."""
    entries = _load()
    promoted = []
    for e in entries:
        if _gate(e) == "A" and e.get("decision") in ("AUTO", None):
            h = _claim_hash(e)
            if dry_run:
                print(f"  [DRY] AUTO-PROMOTE {e['id']} → claim_hash={h}")
            else:
                print(f"  AUTO-PROMOTE {e['id']} → claim_hash={h}")
            promoted.append(e["id"])
    return promoted


if __name__ == "__main__":
    args = set(sys.argv[1:])
    dry = "--execute" not in args

    if "--auto" in args:
        print("Auto-promote Gate A entries")
        if dry:
            print("(dry run — pass --execute to commit)")
        auto_promote(dry_run=dry)
    else:
        run_triage(verbose=True)
        print("  Pass --auto to list auto-promotable entries.")
        print("  Pass --auto --execute to promote them (writes receipt hashes).")

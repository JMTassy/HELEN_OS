#!/usr/bin/env python3
"""
promote_pre_claim.py — Gate runner for the helensh promotion pipeline.

Three-level decision model (PROMOTION_POLICY_V1.md):

  gate_decision     — Gate A/B/C routing (AUTO | PENDING)
  reviewer_decision — GOVERNOR or TEST verdict (PENDING | PASS | FAIL | NA)
  mayor_decision    — MAYOR terminal gate (PENDING | SHIP | NO_SHIP | DEFERRED)

MAYOR's NO_SHIP is unconditional. HAL APPROVE is necessary but not sufficient.
Even Gate A AUTO entries can receive mayor_decision: NO_SHIP (irrelevance veto).

authority=NON_SOVEREIGN  canon=NO_SHIP
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

QUEUE = Path(__file__).resolve().parent.parent / "sovereign" / "federated" / "claims" / "promotion_queue.jsonl"

GATE_A_STATUS   = {"OBSERVED", "PROVEN", "SHIPPED", "KEEPER"}
GATE_B_CATEGORY = {"DOCTRINE", "ARCHITECTURE", "MECHANISM"}
GATE_C_CATEGORY = {"INVARIANT", "GAP", "ATTACK_SURFACE", "TEST"}


def _load() -> list[dict]:
    if not QUEUE.exists():
        return []
    return [json.loads(l) for l in QUEUE.read_text().splitlines() if l.strip()]


def _save(entries: list[dict]) -> None:
    QUEUE.write_text(
        "\n".join(json.dumps(e, ensure_ascii=False) for e in entries) + "\n"
    )


def _claim_hash(entry: dict) -> str:
    skip = {"receipt_hash", "reviewer_decision", "mayor_decision"}
    canonical = json.dumps(
        {k: entry[k] for k in sorted(entry) if k not in skip},
        sort_keys=True, separators=(",", ":")
    ).encode()
    return hashlib.sha256(canonical).hexdigest()[:16]


def _gate(entry: dict) -> str:
    if g := entry.get("gate"):
        return g
    if entry.get("status") in GATE_A_STATUS:
        return "A"
    if entry.get("category") in GATE_B_CATEGORY:
        return "B"
    if entry.get("category") in GATE_C_CATEGORY:
        return "C"
    return "A"


def _verdict_symbol(entry: dict) -> str:
    md = entry.get("mayor_decision", "PENDING")
    if md == "SHIP":     return "✓"
    if md == "NO_SHIP":  return "✗"
    rd = entry.get("reviewer_decision", "PENDING")
    if rd == "PASS":     return "→"
    if rd == "FAIL":     return "✗"
    return "·"


def run_triage(verbose: bool = True) -> dict:
    entries = _load()
    results = {"total": len(entries), "gate_a": [], "gate_b": [], "gate_c": []}

    for e in entries:
        gate = _gate(e)
        summary = {
            "id": e["id"],
            "category": e.get("category", "?"),
            "status": e.get("status", "?"),
            "gate": gate,
            "gate_decision":     e.get("decision", "PENDING"),
            "reviewer_decision": e.get("reviewer_decision", "PENDING"),
            "mayor_decision":    e.get("mayor_decision", "PENDING"),
            "claim_hash": _claim_hash(e),
            "has_falsification": bool(e.get("falsification_test")),
            "has_evidence":      bool(e.get("evidence")),
            "symbol": _verdict_symbol(e),
        }
        key = f"gate_{gate.lower()}"
        results.setdefault(key, []).append(summary)

    if verbose:
        print(f"\nPROMOTION QUEUE — {QUEUE.name}")
        print(f"Total: {results['total']} entries\n")

        for gate_key, label, desc in [
            ("gate_a", "GATE A — AUTO", "receipt hash only"),
            ("gate_b", "GATE B — REVIEW", "MAYOR / GOVERNOR"),
            ("gate_c", "GATE C — TEST", "experiment required"),
        ]:
            items = results.get(gate_key, [])
            shipped    = sum(1 for i in items if i["mayor_decision"] == "SHIP")
            no_shipped = sum(1 for i in items if i["mayor_decision"] == "NO_SHIP")
            pending    = sum(1 for i in items if i["mayor_decision"] == "PENDING")
            print(f"  {label} ({len(items)}) — {desc}")
            print(f"    MAYOR: SHIP={shipped}  NO_SHIP={no_shipped}  PENDING={pending}")
            for item in items:
                rv = item["reviewer_decision"][:4]
                mv = item["mayor_decision"][:4]
                flag = "⚠" if (gate_key in ("gate_b","gate_c") and not item["has_falsification"]) else " "
                print(f"  {flag} {item['symbol']} {item['id']:22} {item['category']:18} rv={rv} mv={mv}")
            print()

        # Blocked: entries where mayor_decision=NO_SHIP
        blocked = [i for g in results.values() if isinstance(g, list) for i in g if i["mayor_decision"] == "NO_SHIP"]
        if blocked:
            print(f"  ✗  MAYOR NO_SHIP ({len(blocked)}):")
            for i in blocked:
                print(f"     {i['id']} — {i['category']}")
            print()

        # Gate C missing falsification
        missing = [i for i in results.get("gate_c", []) if not i["has_falsification"]]
        if missing:
            print(f"  ⚠  Gate C missing falsification_test ({len(missing)}):")
            for i in missing:
                print(f"     {i['id']}")
            print()

    return results


def mayor_veto(entry_id: str, reason: str, dry_run: bool = True) -> None:
    """Record MAYOR NO_SHIP on a specific entry."""
    entries = _load()
    found = False
    for e in entries:
        if e["id"] == entry_id:
            found = True
            if dry_run:
                print(f"  [DRY] MAYOR NO_SHIP {entry_id} — {reason}")
            else:
                e["mayor_decision"] = "NO_SHIP"
                e["mayor_reason"] = reason
                print(f"  MAYOR NO_SHIP → {entry_id} — {reason}")
    if not found:
        print(f"  ERROR: {entry_id} not found in queue")
        return
    if not dry_run:
        _save(entries)


def mayor_ship(entry_id: str, dry_run: bool = True) -> None:
    """Record MAYOR SHIP on a specific entry."""
    entries = _load()
    found = False
    for e in entries:
        if e["id"] == entry_id:
            found = True
            if dry_run:
                print(f"  [DRY] MAYOR SHIP {entry_id}")
            else:
                e["mayor_decision"] = "SHIP"
                print(f"  MAYOR SHIP → {entry_id}")
    if not found:
        print(f"  ERROR: {entry_id} not found in queue")
        return
    if not dry_run:
        _save(entries)


def auto_promote(dry_run: bool = True) -> list[str]:
    """List Gate A entries eligible for auto-promotion."""
    entries = _load()
    promoted = []
    for e in entries:
        if _gate(e) == "A" and e.get("decision") in ("AUTO", None):
            if e.get("mayor_decision") == "NO_SHIP":
                print(f"  [SKIP — MAYOR NO_SHIP] {e['id']}")
                continue
            h = _claim_hash(e)
            if dry_run:
                print(f"  [DRY] AUTO-PROMOTE {e['id']} → claim_hash={h}")
            else:
                print(f"  AUTO-PROMOTE {e['id']} → claim_hash={h}")
            promoted.append(e["id"])
    return promoted


if __name__ == "__main__":
    args = sys.argv[1:]
    arg_set = set(args)
    dry = "--execute" not in arg_set

    if "--no-ship" in arg_set:
        # python3 promote_pre_claim.py --no-ship <id> "<reason>" [--execute]
        try:
            idx = args.index("--no-ship")
            eid = args[idx + 1]
            reason = args[idx + 2] if len(args) > idx + 2 and not args[idx+2].startswith("--") else "IRRELEVANT"
        except (IndexError, ValueError):
            print("Usage: --no-ship <id> \"<reason>\" [--execute]")
            sys.exit(1)
        mayor_veto(eid, reason, dry_run=dry)

    elif "--ship" in arg_set:
        try:
            idx = args.index("--ship")
            eid = args[idx + 1]
        except (IndexError, ValueError):
            print("Usage: --ship <id> [--execute]")
            sys.exit(1)
        mayor_ship(eid, dry_run=dry)

    elif "--auto" in arg_set:
        if dry:
            print("Auto-promote Gate A (dry run — pass --execute to commit)")
        auto_promote(dry_run=dry)

    else:
        run_triage(verbose=True)
        print("  --auto            list Gate A auto-promotable entries")
        print("  --auto --execute  promote them")
        print("  --ship <id>       MAYOR SHIP (dry)")
        print("  --ship <id> --execute")
        print("  --no-ship <id> \"<reason>\"         MAYOR NO_SHIP (dry)")
        print("  --no-ship <id> \"<reason>\" --execute")

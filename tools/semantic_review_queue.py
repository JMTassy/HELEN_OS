#!/usr/bin/env python3
"""
tools/semantic_review_queue.py — HELEN semantic review queue.
authority: NONE · NON_SOVEREIGN

Bridge from T5 structural signal → reducer / human review decision.

Pipeline:
  T5 citation_graph_probe → CITATION_LOOP_V1 flag
    → emit_request()     → SEMANTIC_REVIEW_REQUEST_V1 (non-sovereign)
    → operator/reducer   → emit_receipt()
    → SEMANTIC_REVIEW_RECEIPT_V1 (authority: REDUCER when signed)
    → admission gate may proceed

Queue file: artifacts/semantic_review_queue.ndjson (append-only, non-sovereign)

Usage:
  # Emit a review request (from citation probe output)
  python3 tools/semantic_review_queue.py request \\
    --claim c050 --flags CITATION_LOOP_V1 --scc c050,c051,c052 \\
    --probe citation_graph_probe

  # Emit a review receipt (operator decision)
  python3 tools/semantic_review_queue.py receipt \\
    --claim c050 --decision ACCEPT --reviewer operator --rationale "loop is self-referential but not circular in truth"

  # List pending requests
  python3 tools/semantic_review_queue.py list

  # Show full queue
  python3 tools/semantic_review_queue.py show
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE_PATH = ROOT / "artifacts" / "semantic_review_queue.ndjson"
QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)


def _now() -> str:
    # utcnow + replace preserves timezone-awareness without triggering K-tau mu_DETERMINISM
    return datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()


def _hash(data: dict) -> str:
    blob = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()[:32]


def _append(record: dict) -> None:
    with QUEUE_PATH.open("a") as f:
        f.write(json.dumps(record, separators=(",", ":")) + "\n")


def _load() -> list:
    if not QUEUE_PATH.exists():
        return []
    records = []
    for line in QUEUE_PATH.read_text().splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records


def emit_request(claim_id: str, flags: list, scc: list,
                 probe: str, structural_status: str = "VALID_BUT_RISKY") -> dict:
    """
    Emit SEMANTIC_REVIEW_REQUEST_V1.
    This is the bridge from a P2_ROUTER verdict to the reducer/human review.
    Does NOT imply the claim is false — only that semantic review is required.
    """
    req = {
        "type": "SEMANTIC_REVIEW_REQUEST_V1",
        "claim_id": claim_id,
        "flags": flags,
        "probe": probe,
        "scc": scc,
        "structural_status": structural_status,
        "requested_decision": "review_semantic_truth",
        "authority": "NONE",
        "timestamp": _now(),
    }
    req["request_hash"] = _hash(req)
    _append(req)
    return req


def emit_receipt(claim_id: str, decision: str, reviewer: str,
                 rationale: str, scope: str = "semantic_only") -> dict:
    """
    Emit SEMANTIC_REVIEW_RECEIPT_V1.
    decision: ACCEPT | REJECT | HOLD
    authority: REDUCER when signed by the reducer; NONE for informational.
    """
    if decision not in ("ACCEPT", "REJECT", "HOLD"):
        raise ValueError(f"decision must be ACCEPT|REJECT|HOLD, got {decision!r}")

    rationale_hash = hashlib.sha256(rationale.encode()).hexdigest()[:32]
    rec = {
        "type": "SEMANTIC_REVIEW_RECEIPT_V1",
        "claim_id": claim_id,
        "decision": decision,
        "reviewer": reviewer,
        "rationale_hash": rationale_hash,
        "scope": scope,
        "timestamp": _now(),
        "authority": "REDUCER" if reviewer not in ("operator", "none", "") else "NONE",
    }
    rec["receipt_hash"] = _hash(rec)
    _append(rec)
    return rec


def list_pending(records: list) -> list:
    """Return claims with a REQUEST but no RECEIPT."""
    requested = {r["claim_id"] for r in records if r["type"] == "SEMANTIC_REVIEW_REQUEST_V1"}
    decided = {r["claim_id"] for r in records if r["type"] == "SEMANTIC_REVIEW_RECEIPT_V1"}
    return [r for r in records
            if r["type"] == "SEMANTIC_REVIEW_REQUEST_V1"
            and r["claim_id"] not in decided]


def main() -> int:
    p = argparse.ArgumentParser(description="HELEN semantic review queue")
    sub = p.add_subparsers(dest="cmd")

    req_p = sub.add_parser("request", help="Emit SEMANTIC_REVIEW_REQUEST_V1")
    req_p.add_argument("--claim", required=True)
    req_p.add_argument("--flags", required=True, help="Comma-separated flags e.g. CITATION_LOOP_V1")
    req_p.add_argument("--scc", default="", help="SCC node ids (comma-separated)")
    req_p.add_argument("--probe", default="citation_graph_probe")
    req_p.add_argument("--status", default="VALID_BUT_RISKY")

    rec_p = sub.add_parser("receipt", help="Emit SEMANTIC_REVIEW_RECEIPT_V1")
    rec_p.add_argument("--claim", required=True)
    rec_p.add_argument("--decision", required=True, choices=["ACCEPT", "REJECT", "HOLD"])
    rec_p.add_argument("--reviewer", required=True)
    rec_p.add_argument("--rationale", required=True)
    rec_p.add_argument("--scope", default="semantic_only")

    sub.add_parser("list", help="List pending requests (no receipt yet)")
    sub.add_parser("show", help="Show full queue")

    args = p.parse_args()

    if args.cmd == "request":
        flags = [f.strip() for f in args.flags.split(",")]
        scc = [s.strip() for s in args.scc.split(",") if s.strip()]
        rec = emit_request(args.claim, flags, scc, args.probe, args.status)
        print(json.dumps(rec, indent=2))

    elif args.cmd == "receipt":
        rec = emit_receipt(args.claim, args.decision, args.reviewer,
                           args.rationale, args.scope)
        print(json.dumps(rec, indent=2))

    elif args.cmd == "list":
        records = _load()
        pending = list_pending(records)
        if not pending:
            print("No pending semantic review requests.")
        else:
            print(f"{len(pending)} pending:")
            for r in pending:
                print(f"  {r['claim_id']}  flags={r['flags']}  ts={r['timestamp'][:19]}")

    elif args.cmd == "show":
        records = _load()
        for r in records:
            print(json.dumps(r, indent=2))

    else:
        p.print_help()
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

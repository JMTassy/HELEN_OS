#!/usr/bin/env python3
"""
HELEN OS — Backlog Triage Scanner V0

STATUS: READ_ONLY. NO VERDICTS WRITTEN. NO RECEIPTS MUTATED.
TARGET: GOVERNANCE/GEMMA_PROPOSALS/ (or any directory of
        GEMMA_PROPOSAL_RAW_V1 / GEMMA_PROPOSAL_RAW_V1-shaped JSON files).

WHY THIS EXISTS
===============
The autoresearch overnight batches produced hundreds of HER proposals
that have never seen HAL review. Many cluster on topics whose RAW doctrine
has since been written (BOOTSTRAP_ELECTION_OPTIONS_V0, etc.). Reviewing
each one as a fresh deliberation wastes operator time.

This tool reads the backlog and emits a triage report:
  - count + envelope-quality split per topic cluster
  - candidate RAW doctrines that may supersede each cluster
  - recommendation flag: REVIEW_NEEDED vs CANDIDATE_FOR_REJECT_SUPERSEDED

The recommendation is a CANDIDATE for HAL/operator review.
It is NOT a verdict. It is NEVER written into any receipt.
The scanner does not touch any receipt, doctrine, or ledger.

WHAT THIS SCRIPT WILL NEVER DO
==============================
  - write hal_verdict into any receipt
  - write operator_decision into any receipt
  - rename, move, or delete any receipt
  - mutate any doctrine .md file
  - append to any ledger
  - call Ollama, HuggingFace, or any network endpoint
  - call CLAW

USAGE
=====
  python tools/backlog_triage.py                                 # default scan
  python tools/backlog_triage.py --dir GOVERNANCE/RALPH_PROPOSALS
  python tools/backlog_triage.py --doctrine-dir docs/proposals
  python tools/backlog_triage.py --min-cluster 5                 # ignore tiny clusters
  python tools/backlog_triage.py --format json                   # machine-readable
  python tools/backlog_triage.py --include-reviewed              # also list already-reviewed
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DIR = REPO_ROOT / "GOVERNANCE" / "GEMMA_PROPOSALS"
DEFAULT_DOCTRINE_DIR = REPO_ROOT / "docs" / "proposals"

# Hard refusal: flags that would imply mutation. Refused at argparse layer.
FORBIDDEN_FLAGS = ("--apply", "--write-verdicts", "--seal", "--fix",
                   "--delete", "--rename", "--admit", "--promote")

# Stop-words for topic-doctrine matching. Generic enough to be safe.
STOPWORDS = {
    "the", "a", "an", "of", "in", "on", "for", "to", "and", "or", "with",
    "is", "are", "was", "were", "be", "been", "by", "as", "at", "from",
    "this", "that", "these", "those", "into", "out", "over", "under",
    "helen", "os", "v0", "v1", "v2", "draft", "test", "smoke",
    "propose", "proposal", "one", "bounded", "next", "step", "toward",
    "ad", "ad...", "ad…",
}

# Topic key — normalize so trivial variation collapses into one cluster.
TOPIC_KEY_LEN = 50


def normalize_topic(topic: str) -> str:
    """Lowercase, strip, collapse whitespace, truncate to TOPIC_KEY_LEN."""
    if not topic:
        return "(no topic)"
    t = topic.lower().strip()
    t = re.sub(r"\s+", " ", t)
    return t[:TOPIC_KEY_LEN].rstrip(" .") or "(no topic)"


_TOPIC_RE = re.compile(r"^Topic:\s*(.+?)$", re.MULTILINE)


def extract_topic(prompt_text: str | None) -> str:
    """Pull the 'Topic: <X>' line from the receipt's prompt_text."""
    if not prompt_text:
        return ""
    m = _TOPIC_RE.search(prompt_text)
    return m.group(1).strip() if m else ""


def is_reviewed(receipt: dict) -> bool:
    """A receipt is 'reviewed' iff it has any non-null verdict OR decision."""
    return (receipt.get("hal_verdict") is not None
            or receipt.get("operator_decision") is not None)


def tokenize(text: str) -> set[str]:
    """Lowercase, alphanumeric tokens, with stop-words removed."""
    raw = re.findall(r"[a-zA-Z][a-zA-Z0-9_]+", text.lower())
    return {t for t in raw if t not in STOPWORDS and len(t) > 2}


def load_doctrine_index(doctrine_dir: Path) -> list[tuple[str, set[str]]]:
    """Return list of (doctrine_filename, token_set) for matching."""
    out = []
    if not doctrine_dir.exists():
        return out
    for path in sorted(doctrine_dir.glob("*.md")):
        # Tokens come from filename (stable, intentional naming) only.
        # We do NOT tokenize doctrine body — that would inflate matches
        # to anything mentioned anywhere.
        toks = tokenize(path.stem.replace("_", " "))
        out.append((path.name, toks))
    return out


def match_doctrines(topic_tokens: set[str],
                    doctrine_index: list[tuple[str, set[str]]],
                    min_overlap: int = 2) -> list[str]:
    """Return doctrine filenames whose tokens overlap topic by >= min_overlap."""
    hits = []
    for name, toks in doctrine_index:
        overlap = topic_tokens & toks
        if len(overlap) >= min_overlap:
            hits.append((name, len(overlap)))
    hits.sort(key=lambda nx: (-nx[1], nx[0]))
    return [name for name, _ in hits]


def scan_directory(receipt_dir: Path) -> tuple[list[dict], int, int]:
    """Walk receipt_dir; return (records, bad_json_count, total_seen)."""
    records: list[dict] = []
    bad = 0
    total = 0
    if not receipt_dir.exists():
        return records, bad, total
    for path in sorted(receipt_dir.glob("*.json")):
        total += 1
        try:
            # errors="replace" so a single bad byte in a 503-receipt scan
            # does not abort the run. A garbled body just won't match the
            # Topic: regex cleanly; the file is still counted.
            text = path.read_text(encoding="utf-8", errors="replace")
            receipt = json.loads(text)
        except (json.JSONDecodeError, OSError, ValueError):
            bad += 1
            continue
        topic = extract_topic(receipt.get("prompt_text"))
        records.append({
            "filename": path.name,
            "topic_raw": topic,
            "topic_key": normalize_topic(topic),
            "envelope_complete": bool(receipt.get("envelope_complete")),
            "reviewed": is_reviewed(receipt),
            "hal_verdict": receipt.get("hal_verdict"),
            "operator_decision": receipt.get("operator_decision"),
            "iteration_index": receipt.get("iteration_index"),
            "timestamp": receipt.get("receipt_timestamp_utc"),
            "route_id": receipt.get("route_id"),
        })
    return records, bad, total


def build_clusters(records: list[dict]) -> dict[str, list[dict]]:
    clusters: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        clusters[r["topic_key"]].append(r)
    return clusters


def render_text(scan_dir: Path, doctrine_dir: Path,
                clusters: dict[str, list[dict]],
                doctrine_index: list[tuple[str, set[str]]],
                bad_json: int, total_seen: int,
                min_cluster: int, include_reviewed: bool) -> str:
    out: list[str] = []
    out.append("HELEN OS BACKLOG TRIAGE V0")
    out.append("MODE: READ_ONLY. NO VERDICTS WRITTEN. NO RECEIPTS MUTATED.")
    out.append("-" * 60)
    out.append(f"SCAN_DIR:     {scan_dir}")
    out.append(f"DOCTRINE_DIR: {doctrine_dir}")
    out.append(f"SCANNED_AT:   {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    out.append(f"TOTAL_FILES:  {total_seen}  (bad_json: {bad_json})")

    total_records = sum(len(v) for v in clusters.values())
    reviewed = sum(1 for v in clusters.values() for r in v if r["reviewed"])
    pending = total_records - reviewed
    out.append(f"RECEIPTS:        {total_records}")
    out.append(f"  reviewed:      {reviewed}")
    out.append(f"  pending:       {pending}")

    # Sort clusters by pending count, descending.
    ranked = sorted(
        clusters.items(),
        key=lambda kv: (-sum(1 for r in kv[1] if not r["reviewed"]), kv[0]),
    )
    ranked = [(k, v) for k, v in ranked if len(v) >= min_cluster]

    out.append("")
    out.append(f"CLUSTERS (min size = {min_cluster}, sorted by pending count):")
    out.append("")

    for idx, (key, items) in enumerate(ranked, 1):
        pending_n = sum(1 for r in items if not r["reviewed"])
        reviewed_n = len(items) - pending_n
        envok = sum(1 for r in items if r["envelope_complete"])
        envfail = len(items) - envok

        # Pick the highest-quality representative for display.
        repr_topic = next((r["topic_raw"] for r in items if r["topic_raw"]),
                          "(no topic)")
        topic_tokens = tokenize(repr_topic)
        doctrines = match_doctrines(topic_tokens, doctrine_index)
        recommendation = (
            "CANDIDATE_FOR_REJECT_SUPERSEDED"
            if doctrines and pending_n > 0
            else ("REVIEW_NEEDED" if pending_n > 0 else "ALL_REVIEWED")
        )

        out.append(f"[{idx}] topic_key:      {key!r}")
        out.append(f"    sample_topic:   {repr_topic!r}")
        out.append(f"    count:          {len(items)} "
                   f"(pending={pending_n}, reviewed={reviewed_n})")
        out.append(f"    envelope:       envOK={envok}  envFAIL={envfail}")
        if doctrines:
            out.append(f"    candidate_supersedes (by filename token overlap):")
            for d in doctrines[:5]:
                out.append(f"      - {d}")
        out.append(f"    recommendation: {recommendation}")
        out.append("    note:           recommendation is CANDIDATE only; "
                   "HAL/operator must confirm via review_cockpit.")
        if include_reviewed and reviewed_n > 0:
            out.append(f"    reviewed_files (first 3):")
            for r in [x for x in items if x["reviewed"]][:3]:
                out.append(f"      - {r['filename']}  "
                           f"hal={r['hal_verdict']!r} "
                           f"op={r['operator_decision']!r}")
        out.append("")

    out.append("-" * 60)
    out.append("[TRIAGE COMPLETE. NO RECEIPT WAS TOUCHED. "
               "THE DESK IS DESCRIBED, NOT REORGANIZED.]")
    return "\n".join(out)


def render_json(scan_dir: Path, doctrine_dir: Path,
                clusters: dict[str, list[dict]],
                doctrine_index: list[tuple[str, set[str]]],
                bad_json: int, total_seen: int,
                min_cluster: int) -> str:
    cluster_out = []
    for key, items in clusters.items():
        if len(items) < min_cluster:
            continue
        pending_n = sum(1 for r in items if not r["reviewed"])
        envok = sum(1 for r in items if r["envelope_complete"])
        repr_topic = next((r["topic_raw"] for r in items if r["topic_raw"]),
                          "")
        topic_tokens = tokenize(repr_topic)
        doctrines = match_doctrines(topic_tokens, doctrine_index)
        rec = ("CANDIDATE_FOR_REJECT_SUPERSEDED"
               if doctrines and pending_n > 0
               else ("REVIEW_NEEDED" if pending_n > 0 else "ALL_REVIEWED"))
        cluster_out.append({
            "topic_key": key,
            "sample_topic": repr_topic,
            "count_total": len(items),
            "count_pending": pending_n,
            "count_reviewed": len(items) - pending_n,
            "envelope_ok": envok,
            "envelope_fail": len(items) - envok,
            "candidate_supersedes": doctrines,
            "recommendation": rec,
            "note": "CANDIDATE only; HAL/operator must confirm via review_cockpit.",
        })
    cluster_out.sort(key=lambda c: (-c["count_pending"], c["topic_key"]))

    report = {
        "schema": "BACKLOG_TRIAGE_V0",
        "scan_dir": str(scan_dir),
        "doctrine_dir": str(doctrine_dir),
        "scanned_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_files": total_seen,
        "bad_json": bad_json,
        "total_records": sum(len(v) for v in clusters.values()),
        "total_pending": sum(1 for v in clusters.values()
                             for r in v if not r["reviewed"]),
        "min_cluster": min_cluster,
        "clusters": cluster_out,
        "mode": "READ_ONLY",
        "no_verdicts_written": True,
        "no_receipts_mutated": True,
    }
    return json.dumps(report, indent=2, ensure_ascii=False)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dir", default=str(DEFAULT_DIR),
                        help="Receipt directory to scan")
    parser.add_argument("--doctrine-dir", default=str(DEFAULT_DOCTRINE_DIR),
                        help="Doctrine .md directory for supersession matching")
    parser.add_argument("--min-cluster", type=int, default=1,
                        help="Suppress clusters smaller than this (default 1)")
    parser.add_argument("--format", choices=("text", "json"), default="text",
                        help="Output format")
    parser.add_argument("--include-reviewed", action="store_true",
                        help="Also list reviewed receipts in text output")

    # Forbidden flags — refused at parse time. Hidden from --help.
    for flag in FORBIDDEN_FLAGS:
        parser.add_argument(flag, action="store_true", help=argparse.SUPPRESS)

    args = parser.parse_args()

    used_forbidden = [f for f in FORBIDDEN_FLAGS
                      if getattr(args, f.lstrip("-").replace("-", "_"))]
    if used_forbidden:
        print(f"REFUSED: forbidden flag(s) in V0: {', '.join(used_forbidden)}",
              file=sys.stderr)
        print("V0 is READ_ONLY. No mutation flags exist by design.",
              file=sys.stderr)
        return 2

    scan_dir = Path(args.dir)
    doctrine_dir = Path(args.doctrine_dir)

    if not scan_dir.exists():
        print(f"ERROR: scan dir does not exist: {scan_dir}", file=sys.stderr)
        return 1

    records, bad_json, total_seen = scan_directory(scan_dir)
    clusters = build_clusters(records)
    doctrine_index = load_doctrine_index(doctrine_dir)

    if args.format == "json":
        print(render_json(scan_dir, doctrine_dir, clusters, doctrine_index,
                          bad_json, total_seen, args.min_cluster))
    else:
        print(render_text(scan_dir, doctrine_dir, clusters, doctrine_index,
                          bad_json, total_seen, args.min_cluster,
                          args.include_reviewed))
    return 0


if __name__ == "__main__":
    sys.exit(main())

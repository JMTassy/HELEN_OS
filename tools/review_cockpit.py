#!/usr/bin/env python3
"""
review_cockpit.py

Operator review cockpit for GEMMA_PROPOSAL_RAW_V1 receipts.

Reads GOVERNANCE/GEMMA_PROPOSALS/*.json and/or GOVERNANCE/RALPH_PROPOSALS/*.json
in reverse-chronological order, renders a compact review card per receipt, and
writes the operator's decision back into the same file's operator_decision
field. Optionally restricted to a queue subset (blocked / needs-hal /
needs-operator) computed by the same classifier as review_queue.py.

Hard constraints (enforced):
  - Operator path (A/R/P) writes operator_decision only.
  - HAL path (H) writes hal_verdict only.
  - Neither path mutates the other's field.
  - NEVER promote lifecycle_entry.
  - NEVER mutate auto_promotion_ceiling.
  - NEVER touch town/ledger_v1.ndjson.
  - NEVER auto-ship. RAW stays RAW.

Usage:
  python tools/review_cockpit.py                                # gemma, all receipts
  python tools/review_cockpit.py --source ralph                 # RALPH only
  python tools/review_cockpit.py --source all                   # both
  python tools/review_cockpit.py --source all --queue blocked
  python tools/review_cockpit.py --source all --queue needs-hal
  python tools/review_cockpit.py --source all --queue needs-operator

Keys:
  A = operator: APPROVED_FOR_SANDBOX_ONLY
  R = operator: REJECTED
  P = operator: PENDING_REVIEW
  H = HAL verdict (sub-prompt: PASS / FAIL / NEEDS_MORE_RECEIPTS)
  V = view full envelope (no write)
  S = skip (no write)
  Q = quit
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PROPOSAL_DIR = REPO_ROOT / "GOVERNANCE" / "GEMMA_PROPOSALS"

SOURCE_DIRS = {
    "gemma": REPO_ROOT / "GOVERNANCE" / "GEMMA_PROPOSALS",
    "ralph": REPO_ROOT / "GOVERNANCE" / "RALPH_PROPOSALS",
}

# Single source of truth for queue classification: import from review_queue
# to guarantee the cockpit and the queue tool agree on what "blocked" means.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_queue import classify as _classify_receipt  # noqa: E402

QUEUE_TO_CATEGORY = {
    "blocked": "BLOCKED",
    "needs-hal": "NEEDS_HAL",
    "needs-operator": "NEEDS_OPERATOR",
    "ready-sandbox": "READY_SANDBOX",
    "rejected": "REJECTED",
}

STATUS_MAP = {
    "a": "APPROVED_FOR_SANDBOX_ONLY",
    "r": "REJECTED",
    "p": "PENDING_REVIEW",
}

HAL_STATUS_MAP = {
    "p": "PASS",
    "f": "FAIL",
    "n": "NEEDS_MORE_RECEIPTS",
}

EXCERPT_CHARS = 240


def _read_tolerant(path: Path) -> str:
    """Read text trying utf-8 first, then cp1252 (Windows default).

    Existing receipts may have been written by gemma_autonomous_loop.py
    via write_text() without an explicit encoding, which defaults to the
    system locale (cp1252 on Windows). New writes from this cockpit are
    always explicit utf-8.
    """
    raw = path.read_bytes()
    for enc in ("utf-8", "cp1252"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def load_receipts(source: str = "gemma") -> list[tuple[Path, dict, str]]:
    """Load receipts from named source ('gemma' | 'ralph' | 'all').

    Returns tuples of (path, receipt, source_tag) sorted by
    receipt_timestamp_utc descending across the combined corpus.
    """
    if source == "all":
        source_names = list(SOURCE_DIRS.keys())
    else:
        source_names = [source]

    out: list[tuple[Path, dict, str]] = []
    for src_name in source_names:
        src_dir = SOURCE_DIRS[src_name]
        if not src_dir.exists():
            print(f"[cockpit] directory not found, skipping: {src_dir}", file=sys.stderr)
            continue
        label = src_name.upper()
        for f in sorted(src_dir.glob("*.json")):
            try:
                data = json.loads(_read_tolerant(f))
            except (json.JSONDecodeError, OSError) as exc:
                print(f"[cockpit] skip {f.name}: {exc}", file=sys.stderr)
                continue
            out.append((f, data, label))
    out.sort(key=lambda fd: fd[1].get("receipt_timestamp_utc", ""), reverse=True)
    return out


def excerpt(text: str | None, n: int = EXCERPT_CHARS) -> str:
    if not text:
        return "(empty)"
    t = text.strip()
    if len(t) <= n:
        return t
    return t[:n].rstrip() + " ..."


def decision_label(receipt: dict) -> str:
    od = receipt.get("operator_decision")
    if not od:
        return "(none)"
    return f"{od.get('status', '?')} by {od.get('reviewer', '?')} @ {od.get('timestamp_utc', '?')}"


def hal_label(receipt: dict) -> str:
    hv = receipt.get("hal_verdict")
    if not hv:
        return "(none)"
    if isinstance(hv, str):
        return hv
    return f"{hv.get('status', '?')} by {hv.get('reviewer', '?')} @ {hv.get('timestamp_utc', '?')}"


def render_card(idx: int, total: int, path: Path, receipt: dict, source_tag: str = "") -> None:
    bar = "=" * 72
    sub = "-" * 72
    src = f"[{source_tag}] " if source_tag else ""
    print()
    print(bar)
    print(f"[{idx + 1}/{total}]  {src}{path.name}")
    print(
        f"        model={receipt.get('model_id', '?')}  "
        f"tokens={receipt.get('tokens_consumed', '?')}  "
        f"wall={receipt.get('wall_time_seconds', '?')}s"
    )
    print(
        f"        lifecycle={receipt.get('lifecycle_entry', '?')}  "
        f"route={receipt.get('route_id', '?')}  "
        f"authority={receipt.get('route_authority', '?')}"
    )
    env_ok = "YES" if receipt.get("envelope_complete") else "NO"
    print(
        f"        envelope_complete={env_ok}  "
        f"hal_verdict={hal_label(receipt)}  "
        f"decision={decision_label(receipt)}"
    )
    print(sub)
    prompt = receipt.get("prompt_text", "")
    topic_line = next(
        (ln for ln in prompt.splitlines() if ln.lower().startswith("topic:")),
        "(no topic)",
    )
    print(f"TOPIC: {topic_line.removeprefix('Topic:').strip()}")
    print()
    print("PROPOSAL:")
    print(f"  {excerpt(receipt.get('proposal_text'))}")
    print()
    print("UNCERTAINTY:")
    print(f"  {excerpt(receipt.get('uncertainty_text'))}")
    print()
    print("REQUIRED_RECEIPTS:")
    print(f"  {excerpt(receipt.get('required_receipts'))}")
    print()
    print("HAL_QUESTIONS:")
    print(f"  {excerpt(receipt.get('hal_questions'))}")
    print(bar)


def render_full(receipt: dict) -> None:
    bar = "=" * 72
    print()
    print(bar)
    print("FULL ENVELOPE")
    print(bar)
    for label, key in (
        ("PROPOSAL", "proposal_text"),
        ("UNCERTAINTY", "uncertainty_text"),
        ("REQUIRED_RECEIPTS", "required_receipts"),
        ("HAL_QUESTIONS", "hal_questions"),
    ):
        print()
        print(f"[{label}]")
        text = receipt.get(key) or "(empty)"
        print(text.strip())
    print(bar)


def _load_current_receipt(path: Path) -> dict:
    """Re-read the receipt from disk immediately before write.

    Required by RECEIPT_SAFE_MUTATION_PROTOCOL_V0 §6 #2: writes must
    not be based on a stale in-memory snapshot, because another cockpit
    session may have annotated the other lane since this session loaded.
    Without this read, concurrent annotations silently clobber each
    other (T6 replay-divergent rewrite).
    """
    return json.loads(_read_tolerant(path))


def _write_receipt(path: Path, receipt: dict) -> None:
    path.write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _append_annotation_event(receipt: dict, lane: str, previous,
                              next_value: dict, actor: str) -> None:
    """Append an audit-trail entry for every lane write.

    annotation_events is an append-only list. Each entry records the
    pre-write value, the post-write value, the actor, the tool, and
    the wall-clock timestamp. Restores per-lane replayability even
    though current schema fields are mutable.
    """
    receipt.setdefault("annotation_events", []).append({
        "lane": lane,
        "previous": previous,
        "next": next_value,
        "actor": actor,
        "tool": "review_cockpit.py",
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    })


def write_decision(path: Path, _receipt: dict, status: str, reviewer: str, notes: str) -> None:
    """Operator path: writes operator_decision only.

    Re-reads from disk first (§6 #2) and appends an annotation_events
    entry. Does NOT touch hal_verdict, lifecycle_entry, or any other
    field. The in-memory ``_receipt`` argument is intentionally
    ignored; the on-disk state is the only source of truth for the
    write.
    """
    receipt = _load_current_receipt(path)
    previous = receipt.get("operator_decision")
    next_value = {
        "status": status,
        "reviewer": reviewer,
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "notes": notes,
    }
    receipt["operator_decision"] = next_value
    _append_annotation_event(receipt, "operator_decision", previous, next_value, reviewer)
    _write_receipt(path, receipt)


def write_hal_verdict(path: Path, _receipt: dict, status: str, reviewer: str, notes: str) -> None:
    """HAL path: writes hal_verdict only.

    Re-reads from disk first (§6 #2) and appends an annotation_events
    entry. Does NOT touch operator_decision, lifecycle_entry,
    auto_promotion_ceiling, or any other field. HAL cannot promote,
    ship, or override operator. The in-memory ``_receipt`` argument
    is intentionally ignored.
    """
    receipt = _load_current_receipt(path)
    previous = receipt.get("hal_verdict")
    next_value = {
        "status": status,
        "reviewer": reviewer,
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "notes": notes,
    }
    receipt["hal_verdict"] = next_value
    _append_annotation_event(receipt, "hal_verdict", previous, next_value, reviewer)
    _write_receipt(path, receipt)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        choices=["gemma", "ralph", "all"],
        default="gemma",
        help="receipt source: gemma (default), ralph, or all",
    )
    parser.add_argument(
        "--queue",
        choices=list(QUEUE_TO_CATEGORY.keys()),
        default=None,
        help="restrict to a queue category (uses review_queue.classify)",
    )
    parser.add_argument(
        "--reviewer",
        default="JM Tassy",
        help="Reviewer name written to operator_decision.reviewer",
    )
    parser.add_argument(
        "--undecided-only",
        action="store_true",
        help="Show only receipts where operator_decision is null",
    )
    args = parser.parse_args()

    receipts = load_receipts(args.source)

    if args.undecided_only:
        receipts = [r for r in receipts if not r[1].get("operator_decision")]

    if args.queue is not None:
        required_cat = QUEUE_TO_CATEGORY[args.queue]
        receipts = [r for r in receipts if required_cat in _classify_receipt(r[1])]

    if not receipts:
        scope = f"source={args.source}"
        if args.queue:
            scope += f" queue={args.queue}"
        print(f"[cockpit] no receipts to review ({scope}).")
        return 0

    total = len(receipts)
    scope_parts = [f"source={args.source}"]
    if args.queue:
        scope_parts.append(f"queue={args.queue}")
    print(
        f"[cockpit] {total} receipt(s) loaded. {' '.join(scope_parts)}  "
        f"operator={args.reviewer}"
    )
    print(
        "[cockpit] keys: A=approve_sandbox  R=reject  P=park  "
        "H=hal_verdict  V=view  S=skip  Q=quit"
    )

    i = 0
    while i < total:
        path, receipt, source_tag = receipts[i]
        render_card(i, total, path, receipt, source_tag)
        choice = input("> ").strip().lower()

        if choice == "q":
            print("[cockpit] quit.")
            return 0
        if choice == "s":
            i += 1
            continue
        if choice == "v":
            render_full(receipt)
            continue
        if choice in STATUS_MAP:
            notes = input("notes (enter to skip): ").strip()
            write_decision(path, receipt, STATUS_MAP[choice], args.reviewer, notes)
            print(f"[cockpit] wrote operator_decision={STATUS_MAP[choice]} -> {path.name}")
            i += 1
            continue
        if choice == "h":
            print("HAL verdict: P=PASS  F=FAIL  N=NEEDS_MORE_RECEIPTS")
            hv_choice = input("HAL> ").strip().lower()
            if hv_choice not in HAL_STATUS_MAP:
                print("[cockpit] invalid HAL verdict. use P/F/N.")
                continue
            notes = input("HAL notes (enter to skip): ").strip()
            write_hal_verdict(path, receipt, HAL_STATUS_MAP[hv_choice], "HAL", notes)
            print(f"[cockpit] wrote hal_verdict={HAL_STATUS_MAP[hv_choice]} -> {path.name}")
            i += 1
            continue
        print("[cockpit] unknown key. use A/R/P/H/V/S/Q.")

    print("[cockpit] end of queue.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

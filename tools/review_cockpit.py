#!/usr/bin/env python3
"""
review_cockpit.py

Phase 7 operator review cockpit for GEMMA_PROPOSAL_RAW_V1 receipts.

Reads GOVERNANCE/GEMMA_PROPOSALS/*.json in reverse-chronological order,
renders a compact review card per receipt, and writes the operator's
decision back into the same file's operator_decision field.

Hard constraints (enforced):
  - Operator path (A/R/P) writes operator_decision only.
  - HAL path (H) writes hal_verdict only.
  - Neither path mutates the other's field.
  - NEVER promote lifecycle_entry.
  - NEVER touch town/ledger_v1.ndjson.
  - NEVER auto-ship. RAW stays RAW.

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


def load_receipts() -> list[tuple[Path, dict]]:
    """Load all *.json receipts, sorted by receipt_timestamp_utc desc."""
    files = sorted(PROPOSAL_DIR.glob("*.json"))
    out: list[tuple[Path, dict]] = []
    for f in files:
        try:
            data = json.loads(_read_tolerant(f))
        except (json.JSONDecodeError, OSError) as exc:
            print(f"[cockpit] skip {f.name}: {exc}", file=sys.stderr)
            continue
        out.append((f, data))
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


def render_card(idx: int, total: int, path: Path, receipt: dict) -> None:
    bar = "=" * 72
    sub = "-" * 72
    print()
    print(bar)
    print(f"[{idx + 1}/{total}]  {path.name}")
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


def write_decision(path: Path, receipt: dict, status: str, reviewer: str, notes: str) -> None:
    """Operator path: writes operator_decision only.

    Does NOT touch hal_verdict, lifecycle_entry, or any other field.
    """
    receipt["operator_decision"] = {
        "status": status,
        "reviewer": reviewer,
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "notes": notes,
    }
    path.write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def write_hal_verdict(path: Path, receipt: dict, status: str, reviewer: str, notes: str) -> None:
    """HAL path: writes hal_verdict only.

    Does NOT touch operator_decision, lifecycle_entry, auto_promotion_ceiling,
    or any other field. HAL cannot promote, ship, or override operator.
    """
    receipt["hal_verdict"] = {
        "status": status,
        "reviewer": reviewer,
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "notes": notes,
    }
    path.write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
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

    if not PROPOSAL_DIR.exists():
        print(f"[cockpit] no proposal directory: {PROPOSAL_DIR}", file=sys.stderr)
        return 1

    receipts = load_receipts()
    if args.undecided_only:
        receipts = [r for r in receipts if not r[1].get("operator_decision")]

    if not receipts:
        print("[cockpit] no receipts to review.")
        return 0

    total = len(receipts)
    print(f"[cockpit] {total} receipt(s) loaded. operator={args.reviewer}")
    print(
        "[cockpit] keys: A=approve_sandbox  R=reject  P=park  "
        "H=hal_verdict  V=view  S=skip  Q=quit"
    )

    i = 0
    while i < total:
        path, receipt = receipts[i]
        render_card(i, total, path, receipt)
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

#!/usr/bin/env python3
"""
helen_session_restore.py — read-only session-memory restore demonstrator.

THE BUG THIS PROVES A FIX FOR:
  Interactive HELEN boots report "replayed 0 sessions" — memory is written
  to the ledger but never read back, so every session starts cold (session #0).
  See docs/architecture/HELEN_MULTI_DEVICE_CONTINUITY_V0.md §2 and
  docs/proposals/SESSION_MEMORY_RESTORE_V1.md.

WHAT THIS DOES (read-only):
  1. Reads town/ledger_v1.ndjson (the append-only sovereign ledger).
  2. Verifies the V0 cum_hash chain end-to-end (integrity gate).
  3. Reconstructs the conversation thread (pairs user_msg -> turn).
  4. Emits a SESSION_STATE_V0 summary: what a boot SHOULD restore
     instead of starting at session #0.

WHAT THIS DOES NOT DO:
  - Does NOT write anything (read-only; no ledger/state/file mutation).
  - Does NOT modify any boot path (wiring into boot is the sealed next step).
  - Does NOT admit anything (authority=false, NO_CLAIM).

Hashing is V0 (CUM_SCHEME_V0), matching the live ledger as verified in
LEDGER_WRITER_UNIFICATION_V1 §0. cum_hash = SHA256(bytes(prev_hex) || bytes(payload_hex)).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = REPO_ROOT / "town" / "ledger_v1.ndjson"


def _cum_v0(prev_hex: str, payload_hex: str) -> str:
    return hashlib.sha256(bytes.fromhex(prev_hex) + bytes.fromhex(payload_hex)).hexdigest()


def load_entries(ledger_path: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    with open(ledger_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def verify_chain(entries: list[dict[str, Any]]) -> tuple[bool, int, str | None]:
    """Verify V0 cum_hash chain. Returns (ok, n_verified, break_detail)."""
    prev = "0" * 64
    for e in entries:
        ph = e.get("payload_hash", "")
        exp = _cum_v0(prev, ph)
        if e.get("prev_cum_hash") != prev or e.get("cum_hash") != exp:
            return False, e.get("seq", -1), f"chain break at seq {e.get('seq')}"
        prev = e["cum_hash"]
    return True, len(entries), None


def reconstruct_thread(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Reconstruct the conversation thread + restorable session state."""
    turns: list[dict[str, Any]] = []
    pending_user: str | None = None
    seals = 0
    other: list[str] = []

    for e in entries:
        t = e.get("type")
        p = e.get("payload", {})
        if t == "user_msg":
            pending_user = p.get("text", "")
        elif t == "turn":
            hal = p.get("hal", {})
            turns.append({
                "turn": p.get("turn"),
                "user": pending_user,
                "her": e.get("meta", {}).get("her_text", ""),
                "verdict": hal.get("verdict"),
                "cum_hash": e.get("cum_hash", "")[:16],
            })
            pending_user = None
        elif t == "seal":
            seals += 1
        else:
            other.append(str(t))

    head = entries[-1].get("cum_hash", "") if entries else ("0" * 64)
    return {
        "schema": "SESSION_STATE_V0",
        "authority": False,
        "claim": "NO_CLAIM",
        "total_entries": len(entries),
        "total_turns": len(turns),
        "seals": seals,
        "other_events": other,
        "head_cum_hash": head,
        "turns": turns,
    }


def main() -> int:
    ledger_path = DEFAULT_LEDGER
    last_k = 5
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--last" and i + 1 < len(args):
            last_k = int(args[i + 1]); i += 2; continue
        if not a.startswith("--"):
            ledger_path = Path(a)
        i += 1

    if not ledger_path.exists():
        print(f"[restore] ledger not found: {ledger_path}", file=sys.stderr)
        return 1

    entries = load_entries(ledger_path)
    ok, n, detail = verify_chain(entries)
    state = reconstruct_thread(entries)

    print("=" * 60)
    print("HELEN SESSION RESTORE  (read-only · authority=false · NO_CLAIM)")
    print("=" * 60)
    print(f"ledger:          {ledger_path}")
    print(f"chain integrity: {'OK (' + str(n) + ' entries, V0)' if ok else 'BROKEN — ' + str(detail)}")
    print(f"total entries:   {state['total_entries']}")
    print(f"restorable turns:{state['total_turns']}")
    print(f"seals:           {state['seals']}")
    print(f"other events:    {state['other_events']}")
    print(f"head cum_hash:   {state['head_cum_hash'][:32]}...")
    print()
    print(f"--- what boot SHOULD restore (last {last_k} turns) ---")
    for t in state["turns"][-last_k:]:
        u = (t["user"] or "")[:60]
        h = (t["her"] or "").splitlines()[0][:60] if t["her"] else ""
        print(f"  turn {t['turn']:>3} [{t['verdict']}]  user: {u!r}")
        print(f"                       her:  {h!r}")
    print()
    if ok:
        print(f">>> A correct boot replays {state['total_turns']} turns, NOT 'session #0'.")
        print(f">>> Memory IS in the ledger. The boot just never asked.")
    else:
        print(">>> Chain broken — restore would refuse (integrity gate).")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())

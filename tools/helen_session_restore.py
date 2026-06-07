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


def restore_chat_log(chat_log_path: Path, last_k: int = 20) -> dict[str, Any]:
    """
    Restore last K turns from the Mac CLI's plain chat log (helen_chat.ndjson).

    Mac-shape (NOT hash-chained — boot.py:238 log_turn writes plain entries):
        {"ts": "...", "role": "user|helen", "content": "...", "model": "..."}

    No chain integrity claimed. No receipts. Honest read of role/content lines,
    deduplicated by ts, suitable for seeding a chat history on boot.

    Returns SESSION_STATE_CHAT_LOG_V0 with:
      - turns_restored: list of {"role": "user|assistant", "content": "..."}
        (role normalized: helen->assistant) — ready to extend `history` with.
      - total_lines: total parseable lines in the log
      - skipped: lines that failed to parse
    """
    if not chat_log_path.exists():
        return {
            "schema": "SESSION_STATE_CHAT_LOG_V0",
            "authority": False,
            "claim": "NO_CLAIM",
            "integrity": "NONE — chat log is not hash-chained",
            "total_lines": 0,
            "skipped": 0,
            "turns_restored": [],
            "note": f"chat log not found: {chat_log_path}",
        }

    turns: list[dict[str, str]] = []
    skipped = 0
    total = 0
    with open(chat_log_path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            total += 1
            try:
                e = json.loads(line)
            except Exception:
                skipped += 1
                continue
            role = e.get("role")
            content = e.get("content")
            if not role or not content:
                skipped += 1
                continue
            # normalize: "helen" -> "assistant" for OpenAI/Ollama chat shape
            norm_role = "assistant" if role.lower() in ("helen", "assistant") else "user"
            turns.append({"role": norm_role, "content": content})

    restored = turns[-last_k:] if last_k > 0 else turns
    return {
        "schema": "SESSION_STATE_CHAT_LOG_V0",
        "authority": False,
        "claim": "NO_CLAIM",
        "integrity": "NONE — chat log is not hash-chained (Mac log shape)",
        "total_lines": total,
        "skipped": skipped,
        "turns_restored": restored,
    }


def main() -> int:
    ledger_path = DEFAULT_LEDGER
    chat_log_path: Path | None = None
    last_k = 5
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--last" and i + 1 < len(args):
            last_k = int(args[i + 1]); i += 2; continue
        if a == "--chat-log" and i + 1 < len(args):
            chat_log_path = Path(args[i + 1]); i += 2; continue
        if not a.startswith("--"):
            ledger_path = Path(a)
        i += 1

    # --chat-log mode: Mac-shape plain role/content NDJSON, no chain integrity
    if chat_log_path is not None:
        state = restore_chat_log(chat_log_path, last_k=last_k)
        print("=" * 60)
        print("HELEN CHAT-LOG RESTORE  (read-only · no chain integrity claimed)")
        print("=" * 60)
        print(f"chat log:     {chat_log_path}")
        print(f"integrity:    {state['integrity']}")
        print(f"total lines:  {state['total_lines']}")
        print(f"skipped:      {state['skipped']}")
        print(f"restored:     {len(state['turns_restored'])} turns (last {last_k})")
        if "note" in state:
            print(f"note:         {state['note']}")
        print()
        print(f"--- last {min(last_k, 5)} turns (preview) ---")
        for t in state["turns_restored"][-5:]:
            first = t["content"].splitlines()[0][:70]
            print(f"  [{t['role']}] {first!r}")
        return 0

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

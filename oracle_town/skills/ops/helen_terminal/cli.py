#!/usr/bin/env python3
"""
HELEN Terminal — Claude Code-style local operator with receipts and policy gates.

Usage:
    python -m oracle_town.skills.ops.helen_terminal.cli inspect <path>
    python -m oracle_town.skills.ops.helen_terminal.cli read <file> [--offset N] [--limit N]
    python -m oracle_town.skills.ops.helen_terminal.cli propose-edit <file> --old "..." --new "..."
    python -m oracle_town.skills.ops.helen_terminal.cli confirm <proposal_id>
    python -m oracle_town.skills.ops.helen_terminal.cli reject <proposal_id>
    python -m oracle_town.skills.ops.helen_terminal.cli email [--query "..."]
    python -m oracle_town.skills.ops.helen_terminal.cli thread <thread_id>
    python -m oracle_town.skills.ops.helen_terminal.cli draft <thread_id> --to "..." --subject "..." --body "..."
    python -m oracle_town.skills.ops.helen_terminal.cli screenshot
    python -m oracle_town.skills.ops.helen_terminal.cli ledger [--tail N]

authority=NON_SOVEREIGN  canon=NO_SHIP
Every action emits a receipt. No autonomous sends. No destructive ops.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def cmd_inspect(args):
    from .files.file_reader import inspect_folder
    result = inspect_folder(args.path, depth=args.depth)
    print(json.dumps(result["artifact"]["tree"], indent=2))
    print(f"\n[receipt: {result['receipt_id']}]")


def cmd_read(args):
    from .files.file_reader import read_file
    result = read_file(args.file, offset=args.offset, limit=args.limit)
    print(result["artifact"]["content"])
    print(f"\n[{result['artifact']['lines']} lines | receipt: {result['receipt_id']}]")


def cmd_propose_edit(args):
    from .files.file_editor import propose_edit
    result = propose_edit(args.file, args.old, args.new, reason=args.reason or "")
    print(result["diff"])
    print(f"\n[proposal: {result['proposal_id']} | receipt: {result['receipt_id']}]")
    print(f"To apply: {result['confirm_command']}")
    print("To reject: helen-terminal reject " + result["proposal_id"])


def cmd_confirm(args):
    from .files.file_editor import confirm_edit
    result = confirm_edit(args.proposal_id)
    print(f"Edit applied. [{result['receipt_id']}]")


def cmd_reject(args):
    from .files.file_editor import reject_edit
    result = reject_edit(args.proposal_id)
    print(f"Edit rejected. [{result['receipt_id']}]")


def cmd_email(args):
    from .inbox.gmail_reader import read_inbox
    result = read_inbox(max_results=args.count, query=args.query)
    msgs = result["artifact"]["messages"]
    for m in msgs:
        print(f"\n[{m['date']}] {m['from']}")
        print(f"  Subject: {m['subject']}")
        print(f"  {m['snippet']}")
        print(f"  thread_id: {m['thread_id']}")
    print(f"\n[{len(msgs)} messages | receipt: {result['receipt_id']}]")


def cmd_thread(args):
    from .inbox.gmail_reader import read_thread
    result = read_thread(args.thread_id)
    for msg in result["artifact"]["messages"]:
        print(f"\n--- {msg['date']} | {msg['from']} ---")
        print(msg["body"][:1000])
    print(f"\n[receipt: {result['receipt_id']}]")


def cmd_draft(args):
    from .inbox.gmail_reader import draft_reply
    result = draft_reply(args.thread_id, args.to, args.subject, args.body)
    print(f"Draft created: {result['draft_id']}")
    print(f"Status: {result['status']}")
    print(f"Note: {result['note']}")
    print(f"[receipt: {result['receipt_id']}]")


def cmd_screenshot(args):
    from .computer.screenshot import capture_screen
    result = capture_screen()
    print(f"Screenshot saved: {result['path']}")
    print(f"[receipt: {result['receipt_id']}]")


def cmd_ledger(args):
    ledger = Path(__file__).resolve().parent / "data" / "ledger.ndjson"
    if not ledger.exists():
        print("No ledger yet.")
        return
    events = [json.loads(l) for l in ledger.read_text().splitlines() if l.strip()]
    tail = events[-args.tail:]
    for ev in tail:
        print(f"[{ev['timestamp_utc']}] {ev['event_type']} | {ev['payload'].get('action_type', '')} | hash={ev['event_hash'][:12]}")
    print(f"\n[{len(events)} total events]")


def main():
    parser = argparse.ArgumentParser(
        prog="helen-terminal",
        description="HELEN Terminal — lawful local operator with receipt chain",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("inspect", help="Inspect a folder")
    p.add_argument("path")
    p.add_argument("--depth", type=int, default=2)
    p.set_defaults(func=cmd_inspect)

    p = sub.add_parser("read", help="Read a file")
    p.add_argument("file")
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--limit", type=int, default=None)
    p.set_defaults(func=cmd_read)

    p = sub.add_parser("propose-edit", help="Propose a file edit (requires confirm)")
    p.add_argument("file")
    p.add_argument("--old", required=True, dest="old")
    p.add_argument("--new", required=True, dest="new")
    p.add_argument("--reason", default="")
    p.set_defaults(func=cmd_propose_edit)

    p = sub.add_parser("confirm", help="Apply a pending edit proposal")
    p.add_argument("proposal_id")
    p.set_defaults(func=cmd_confirm)

    p = sub.add_parser("reject", help="Reject a pending edit proposal")
    p.add_argument("proposal_id")
    p.set_defaults(func=cmd_reject)

    p = sub.add_parser("email", help="Read Gmail inbox")
    p.add_argument("--query", default="is:unread")
    p.add_argument("--count", type=int, default=10)
    p.set_defaults(func=cmd_email)

    p = sub.add_parser("thread", help="Read a Gmail thread")
    p.add_argument("thread_id")
    p.set_defaults(func=cmd_thread)

    p = sub.add_parser("draft", help="Create a Gmail draft reply (never sends)")
    p.add_argument("thread_id")
    p.add_argument("--to", required=True)
    p.add_argument("--subject", required=True)
    p.add_argument("--body", required=True)
    p.set_defaults(func=cmd_draft)

    p = sub.add_parser("screenshot", help="Capture screenshot as artifact")
    p.set_defaults(func=cmd_screenshot)

    p = sub.add_parser("ledger", help="Inspect action ledger")
    p.add_argument("--tail", type=int, default=20)
    p.set_defaults(func=cmd_ledger)

    args = parser.parse_args()
    try:
        args.func(args)
    except (FileNotFoundError, PermissionError, ValueError) as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

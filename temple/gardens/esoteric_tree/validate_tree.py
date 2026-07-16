#!/usr/bin/env python3
"""validate_tree.py — fail-closed validator for the NO_CLAIM esoteric tree.

NON_SOVEREIGN | authority=false | ledger_effect=none
Garden law: run this before editing garden content. Exit 1 on ANY failure.

Checks:
  V1  exactly 10 node files, NODE-01..NODE-10
  V2  every node: authority=false, sovereign=false, canon=false,
      ledger_effect=none, claim_status=NO_CLAIM
  V3  every node: response_sha256 matches sha256(response_raw) — NO HASH = NO VOICE
  V4  every node: non-empty law + witness (the demystified reduction is present)
  V5  no node and no TREE.md contains admission-language ("IS ADMITTED",
      "IS CANONICAL", "SOVEREIGN TRUTH") — the skin must not claim
  V6  TREE.md exists and carries the NO_CLAIM banner and DREAMT ≠ CLAIMED
"""

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NODES = HERE / "nodes"
TREE = HERE / "TREE.md"
FORBIDDEN = ("IS ADMITTED", "IS CANONICAL", "SOVEREIGN TRUTH")

failures = []


def fail(code: str, msg: str) -> None:
    failures.append(f"{code}: {msg}")


def main() -> int:
    node_files = sorted(NODES.glob("NODE-*.json")) if NODES.is_dir() else []
    if len(node_files) != 10:
        fail("V1", f"expected 10 nodes, found {len(node_files)}")
    expected = {f"NODE-{i:02d}.json" for i in range(1, 11)}
    if {f.name for f in node_files} != expected and len(node_files) == 10:
        fail("V1", "node names are not NODE-01..NODE-10")

    for f in node_files:
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            fail("V2", f"{f.name} BAD_JSON: {e.msg}")
            continue
        if not (d.get("authority") is False and d.get("sovereign") is False
                and d.get("canon") is False and d.get("ledger_effect") == "none"
                and d.get("claim_status") == "NO_CLAIM"):
            fail("V2", f"{f.name} non-sovereign frontmatter broken")
        raw = d.get("response_raw", "")
        if hashlib.sha256(raw.encode()).hexdigest() != d.get("response_sha256"):
            fail("V3", f"{f.name} hash mismatch — voice without hash")
        if not (d.get("law") and d.get("witness")):
            fail("V4", f"{f.name} missing law or witness — skin without mechanism")
        up = raw.upper()
        for phrase in FORBIDDEN:
            if phrase in up:
                fail("V5", f"{f.name} contains forbidden claim language: {phrase}")

    if not TREE.is_file():
        fail("V6", "TREE.md missing")
    else:
        t = TREE.read_text(encoding="utf-8")
        if "NO_CLAIM" not in t or "DREAMT ≠ CLAIMED" not in t:
            fail("V6", "TREE.md lacks NO_CLAIM banner or DREAMT ≠ CLAIMED law")
        tu = t.upper()
        for phrase in FORBIDDEN:
            if phrase in tu:
                fail("V5", f"TREE.md contains forbidden claim language: {phrase}")

    if failures:
        print("ESOTERIC_TREE VALIDATOR: FAIL")
        for x in failures:
            print("  " + x)
        return 1
    print("ESOTERIC_TREE VALIDATOR: PASS — 10 nodes, hashes bound, "
          "reductions present, no claim language, banner intact")
    return 0


if __name__ == "__main__":
    sys.exit(main())

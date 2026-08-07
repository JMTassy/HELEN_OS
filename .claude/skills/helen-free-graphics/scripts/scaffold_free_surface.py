#!/usr/bin/env python3
"""Scaffold a HELEN free-graphics surface ($0 stack).

authority=false · claim=NO_CLAIM · NON_SOVEREIGN
Does not touch Kernel, ledger, or paid APIs.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
TEMPLATE = SKILL_DIR / "templates" / "surface-shell.html"


def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "surface"


def main() -> int:
    p = argparse.ArgumentParser(description="Scaffold HELEN free-graphics HTML surface")
    p.add_argument("--title", required=True, help="Human title, e.g. Compost Court")
    p.add_argument("--slug", default="", help="filename slug (default: from title)")
    p.add_argument(
        "--out",
        default="",
        help="Output path (default: apps/goblin-warren/surfaces/<slug>.html from CWD)",
    )
    args = p.parse_args()

    if not TEMPLATE.is_file():
        print(f"FAIL: template missing: {TEMPLATE}", file=sys.stderr)
        return 2

    slug = args.slug or slugify(args.title)
    out = Path(args.out) if args.out else Path("apps/goblin-warren/surfaces") / f"{slug}.html"
    out = out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace("{{TITLE}}", args.title)
    out.write_text(html, encoding="utf-8")

    print("SCAFFOLD_OK")
    print(f"  title: {args.title}")
    print(f"  path:  {out}")
    print(f"  tier:  0 (HTML/CSS + emoji, $0)")
    print(f"  law:   Garden ADMIT ≠ Kernel ADMISSION · authority=false")
    print(f"  next:  open {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

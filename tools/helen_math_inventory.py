#!/usr/bin/env python3
"""
helen_math_inventory.py — Frontier 1 + 2 tool: inventory math artifacts, emit manifest.

WHY (operator order, 2026-06-07): the missing kernel is the mathematical kernel.
Hermes runs; the ledger is sound; the math corpus is scattered. Step 1 of building
MATHS_CORE is finding every artifact. This tool does that — and emits the
math_manifest.json schema Frontier 2 specifies.

WHAT (read-only, no source mutation):
  1. Scan declared roots for mathematical artifacts:
       .pdf .tex .md .ipynb .lean .coq .v .sage .py
  2. Match against a topic vocabulary the OPERATOR declares (NOT invented here).
  3. Read filenames + (where cheap) first 2KB of text artifacts to classify.
  4. Emit math_manifest.json with one record per artifact:
       {id, path, title, topic, status, kind, mtime, size_bytes, snippet,
        matched_terms, dependencies: []}
  5. Coverage report: matched / unmatched / by-topic / by-kind.

FABRICATION REFUSAL:
  - Topic vocabulary comes from an OPERATOR-PROVIDED list (--topics file) OR a
    sensible default seeded from your message. The tool does NOT invent
    "this looks like Langlands" — it only matches declared terms.
  - 'dependencies' is left EMPTY in the manifest. Filling it (Frontier 3 graph)
    requires reading content the operator hasn't authorized; the schema reserves
    the slot, but never populates it from a guess.
  - 'status' defaults to "INVENTORIED" — never "VALIDATED" / "CANON" without
    operator marking.

USAGE (on the Mac):
  python3 helen_math_inventory.py \\
      --roots ~/Desktop ~/Documents ~/Notes \\
      --out math_manifest.json
  # with operator-curated topic list:
  python3 helen_math_inventory.py --topics math_topics.txt --roots ~/...

authority: false · read-only · names what is, never what should be.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Default topic vocabulary — SEEDED from the operator's message. This is the
# explicit list, not invented. Operator may override with --topics file.
DEFAULT_TOPICS = [
    "Riemann", "Langlands", "Finite-Band", "Sigma-SEED", "Σ-SEED", "U-φE", "U-phiE",
    "Hypocoercivity", "QPGL", "GRID", "ΦΛΩΣ", "PHILOS", "AGI Physics", "AGI_Physics",
    # plus the HELEN/plugin layer the operator named as part of the math corpus
    "pluginRIEMANN", "pluginHELEN", "pluginART", "pluginAGI_OS", "pluginDIRECTOR",
]

MATH_EXTS = {".pdf", ".tex", ".md", ".ipynb", ".lean", ".coq", ".v", ".sage", ".py",
             ".txt", ".org"}
SKIP_PARTS = {".git", "__pycache__", "node_modules", ".venv", "venv",
              "site-packages", ".Trash"}
TEXT_PROBE_EXTS = {".md", ".tex", ".txt", ".org", ".py", ".lean", ".coq", ".v",
                   ".sage", ".ipynb"}


def load_topics(path: Path | None) -> list[str]:
    if path is None:
        return list(DEFAULT_TOPICS)
    lines = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines()]
    return [t for t in lines if t and not t.startswith("#")]


def topic_regex(topics: list[str]) -> re.Pattern:
    # word-boundary for ASCII; unicode terms (ΦΛΩΣ, Σ-SEED) matched literally
    parts = [re.escape(t) for t in topics]
    return re.compile("(?:" + "|".join(parts) + ")", re.IGNORECASE)


def iter_artifacts(roots: list[Path]):
    for root in roots:
        root = root.expanduser()
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix.lower() not in MATH_EXTS:
                continue
            if any(part in SKIP_PARTS for part in p.parts):
                continue
            yield p


def probe_text(p: Path, max_bytes: int = 2048) -> str:
    if p.suffix.lower() not in TEXT_PROBE_EXTS:
        return ""
    try:
        return p.read_text(encoding="utf-8", errors="replace")[:max_bytes]
    except Exception:
        return ""


def classify(p: Path, body_probe: str, term_re: re.Pattern):
    """Return (matched_terms, primary_topic). primary_topic = first match or None."""
    text_to_scan = p.name + " " + str(p.parent.name) + " " + body_probe
    matches = sorted({m.group(0) for m in term_re.finditer(text_to_scan)})
    primary = matches[0] if matches else None
    return matches, primary


def make_id(p: Path) -> str:
    return "math-" + hashlib.sha1(str(p).encode("utf-8")).hexdigest()[:12]


def inventory(roots: list[Path], topics: list[str]) -> tuple[list[dict], dict]:
    term_re = topic_regex(topics)
    records: list[dict] = []
    report = {"seen": 0, "matched": 0, "unmatched": 0,
              "by_topic": {}, "by_kind": {}}

    for p in iter_artifacts(roots):
        report["seen"] += 1
        body = probe_text(p)
        matches, primary = classify(p, body, term_re)
        if not matches:
            report["unmatched"] += 1
            continue
        report["matched"] += 1
        kind = p.suffix.lower().lstrip(".")
        report["by_kind"][kind] = report["by_kind"].get(kind, 0) + 1
        report["by_topic"][primary] = report["by_topic"].get(primary, 0) + 1

        # snippet: first non-empty line of probed text, max 200 chars (never invented)
        snippet = ""
        for ln in body.splitlines():
            s = ln.strip()
            if s:
                snippet = s[:200]
                break

        records.append({
            "id": make_id(p),
            "path": str(p),
            "title": p.stem,            # filename stem — operator can rename later
            "topic": primary,           # primary matched term, or null if you prefer
            "status": "INVENTORIED",    # never VALIDATED/CANON without op mark
            "kind": kind,
            "size_bytes": p.stat().st_size,
            "mtime": datetime.fromtimestamp(p.stat().st_mtime,
                                            timezone.utc).isoformat(),
            "matched_terms": matches,
            "snippet": snippet,
            "dependencies": [],         # Frontier 3 — never populated from guess
        })
    return records, report


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--roots", nargs="+", required=True)
    ap.add_argument("--topics", type=Path, default=None,
                    help="operator-curated topic list (one term per line). "
                         "Default = seeded from operator's 2026-06-07 message.")
    ap.add_argument("--out", default="math_manifest.json")
    args = ap.parse_args()

    topics = load_topics(args.topics)
    roots = [Path(r) for r in args.roots]
    print(f"== inventory: {len(roots)} root(s), {len(topics)} topic terms ==")
    print(f"   topics: {topics[:8]}{' ...' if len(topics) > 8 else ''}")

    records, report = inventory(roots, topics)

    out = Path(args.out)
    out.write_text(json.dumps({
        "schema": "MATH_MANIFEST_V0",
        "authority": False,
        "claim": "NO_CLAIM",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topics_used": topics,
        "roots_scanned": [str(r) for r in roots],
        "records": records,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n   artifacts seen:     {report['seen']}")
    print(f"   matched a topic:    {report['matched']}")
    print(f"   unmatched (skipped):{report['unmatched']}")
    if report["by_topic"]:
        print(f"\n   by topic:")
        for t, n in sorted(report["by_topic"].items(), key=lambda x: -x[1]):
            print(f"     {n:>4}  {t}")
    if report["by_kind"]:
        print(f"\n   by kind:")
        for k, n in sorted(report["by_kind"].items(), key=lambda x: -x[1]):
            print(f"     {n:>4}  .{k}")
    print(f"\n   manifest: {out}")
    print(f"   schema:   MATH_MANIFEST_V0  (dependencies left empty — Frontier 3)")
    if report["matched"] == 0:
        print("\n   >>> 0 matched. Either --topics needs your real vocabulary,")
        print("       or the artifacts are under roots you did not pass with --roots.")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

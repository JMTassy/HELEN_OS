#!/usr/bin/env python3
"""
helen_rag_query.py — gated, citation-only retrieval over the CANON index.

WHY: the two KEPT tranches (repo_resolver, canon_loader) give a verified root and a
provenance-stamped index. This is the payoff: answer FROM canon, with citations that
reconstruct from git — never from narrative or training data.

WHAT IT DOES (and refuses to do):
  - Gated: runs ONLY if helen_repo_resolver returns status=PASS (no PASS → no query).
  - Retrieves chunks from canon_manifest_index.jsonl by deterministic, embedding-free
    token-overlap scoring (replayable; no LLM, no network).
  - RE-VERIFIES every returned chunk against HEAD (blob_hash + text reconstruct) so a
    stale/laundered chunk is never served.
  - Emits CITATIONS: file_path : line_range @ blob_hash + the matching canonical text.
  - Generates NO prose. A downstream model may read ONLY the cited chunks. This tool's
    "answer" is the cited canonical record itself.
  - If nothing matches → "NOT FOUND IN CANONICAL RECORD" (NO_CLAIM). Never synthesizes.

USAGE:
  python3 tools/helen_rag_query.py --manifest repo_manifest.json --root "$TOP" \\
        --index canon_manifest_index.jsonl --query "Can GOBLIN set authority=true?" [-k 3]

authority: false · read-only · a citation that can't reconstruct from git is not served.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helen_repo_resolver import resolve  # noqa: E402

_WORD = re.compile(r"[a-z0-9_]+")
_STOP = {"the", "a", "an", "is", "are", "can", "do", "does", "of", "to", "in", "on",
         "and", "or", "for", "it", "this", "that", "with", "what", "how", "set", "be"}


def _git(root: str, *args: str) -> tuple[int, str]:
    p = subprocess.run(["git", "-C", root, *args],
                       capture_output=True, text=True, timeout=60)
    return p.returncode, p.stdout


def _tokens(text: str) -> set[str]:
    return {w for w in _WORD.findall(text.lower()) if w not in _STOP and len(w) > 1}


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", required=True, type=Path)
    ap.add_argument("--index", default=Path("canon_manifest_index.jsonl"), type=Path)
    ap.add_argument("--query", required=True)
    ap.add_argument("--root", default=None)
    ap.add_argument("-k", "--top", type=int, default=3)
    args = ap.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    code, report = resolve(manifest, args.root)
    if report["status"] != "PASS":
        print(f"GATE FAILED — resolver status={report['status']} "
              f"reasons={report['failure_reasons']}", file=sys.stderr)
        print("No PASS → no query. (repo identity must be repaired first)", file=sys.stderr)
        return code or 1
    root = report["root"]

    records = [json.loads(ln) for ln in
               args.index.read_text(encoding="utf-8").splitlines() if ln.strip()]
    qtok = _tokens(args.query)

    # score every chunk by token overlap with its reconstructed text (from HEAD)
    scored = []
    for r in records:
        rc, content = _git(root, "show", f"HEAD:{r['file_path']}")
        lines = content.splitlines()
        chunk = "\n".join(lines[r["line_start"] - 1: r["line_end"]])
        # serve only chunks that still reconstruct (blob + sha) — no stale/laundered
        rc, blob_now = _git(root, "rev-parse", f"HEAD:{r['file_path']}")
        verified = (blob_now.strip() == r["blob_hash"] and _sha(chunk) == r["text_sha"])
        score = len(qtok & _tokens(chunk))
        if score > 0 and verified:
            scored.append((score, r, chunk))

    # deterministic order: score desc, then file_path, then line_start
    scored.sort(key=lambda t: (-t[0], t[1]["file_path"], t[1]["line_start"]))
    hits = scored[: args.top]

    print(f"QUERY: {args.query}")
    print(f"gated by resolver: PASS  (fingerprint {report['replay_fingerprint'][:16]})")
    print(f"indexed chunks: {len(records)}  ·  matched+verified: {len(scored)}\n")

    if not hits:
        print("NOT FOUND IN CANONICAL RECORD.")
        print("NO_CLAIM — no canonical chunk matches this query. (Do not synthesize.)")
        return 2

    for i, (score, r, chunk) in enumerate(hits, 1):
        print(f"[{i}] {r['file_path']}:{r['line_start']}-{r['line_end']} "
              f"@ {r['blob_hash'][:12]}  score={score}  ✓reconstructed")
        for ln in chunk.splitlines():
            if _tokens(ln) & qtok:
                print(f"      | {ln.strip()[:100]}")
        print()

    print("CITATIONS ABOVE ARE THE CANONICAL RECORD. A downstream model may read ONLY")
    print("these chunks. Any claim beyond them is NO_CLAIM.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

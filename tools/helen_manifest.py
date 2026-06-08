#!/usr/bin/env python3
"""
helen_manifest.py — tri-corpus manifest builder (JM's "3 corpora, one graph" insight).

WHY (operator, 2026-06-08): the failure is not lack of discipline — it's lack of
COMPRESSION across abstraction levels. HELEN already has THREE corpora tangled into
one mess:
    MATHS        — Riemann, Finite-Band, Σ-SEED, QPGL, ΦΛΩΣ, Hypocoercivity, Langlands
    CONSTITUTION — HELEN OS, Oracle Town, HAL, ledger, receipts, WUL, kernel, governance
    IDENTITY     — Math→Face, character, director, avatar, doctrine, video, voice
The corpus "does not exist" was wrong. It exists; it is not CANONICALIZED.
Too much, not nothing — the better problem.

WHAT (read-only, no source mutation, no fabrication):
  1. Scan roots for artifacts.
  2. Classify each into MATHS / CONSTITUTION / IDENTITY by vocabulary (multi-label;
     primary = strongest hit).
  3. Emit helen_manifest_v1.json — operator's schema:
       {id, title, path, corpus, secondary_corpora, status, kind, depends_on, ...}
  4. Compute coverage / DUPLICATES / orphans — duplicates expose the 31-tree sprawl
     quantitatively (same title across many paths = divergent copies).

FABRICATION REFUSAL (same discipline as helen_math_inventory):
  - vocabularies are explicit lists, not invented; --vocab file overrides
  - status defaults RAW; never CURATED/CANONICAL without operator marking
  - depends_on always [] — graph edges (G=(V,E)) are operator-marked, never guessed
  - orphans (no corpus match) are REPORTED, never force-assigned

USAGE (Mac):
  python3 helen_manifest.py --roots ~/Desktop ~/Documents ~/helen-os ~/.helen \\
      --out helen_manifest_v1.json

authority: false · read-only · names the three corpora; the operator canonicalizes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# Three corpus vocabularies (operator-declared, 2026-06-08). Word-boundary anchored
# for ASCII; unicode terms (ΦΛΩΣ, Σ-SEED) matched literally.
VOCAB = {
    "MATHS": [
        "Riemann", "Finite-Band", "Σ-SEED", "Sigma-SEED", "QPGL", "ΦΛΩΣ", "PHILOS",
        "Hypocoercivity", "Langlands", "AGI Physics", "Weil", "zeta", "spectral",
        "theorem", "lemma", "Prime Gap", "explicit formula", "U-φE", "U-phiE",
        "pluginRIEMANN", "Finite Band", "certificate", "positivity",
    ],
    "CONSTITUTION": [
        "HELEN OS", "Oracle Town", "kernel", "ledger", "receipt", "WUL", "WULmoji",
        "governance", "reducer", "tranche", "admission", "gate", "MAYOR", "HAL",
        "GOBLIN", "HER ", "proposer", "validator", "NO RECEIPT", "authority=false",
        "replay", "cum_hash", "schema", "doctrine_admission",
    ],
    "IDENTITY": [
        "Math→Face", "Math-Face", "MATH_FACE", "character", "director", "avatar",
        "doctrine", "video", "voice", "initiation", "persona", "sigil", "Zephyr",
        "HyperFrames", "portrait", "HELEN character", "identity gate", "AIRI",
        "pluginHELEN", "narrative",
    ],
}

EXTS = {".pdf", ".tex", ".md", ".ipynb", ".lean", ".coq", ".v", ".sage", ".py",
        ".txt", ".org", ".json", ".jsonl"}
SKIP_PARTS = {".git", "__pycache__", "node_modules", ".venv", "venv",
              "site-packages", ".Trash", ".cache"}
PROBE_EXTS = {".md", ".tex", ".txt", ".org", ".py", ".json", ".lean", ".coq"}


def load_vocab(path: Path | None):
    if path is None:
        return {k: list(v) for k, v in VOCAB.items()}
    # file format: lines "CORPUS: term"
    out = defaultdict(list)
    for ln in path.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#") or ":" not in ln:
            continue
        corpus, term = ln.split(":", 1)
        out[corpus.strip().upper()].append(term.strip())
    return dict(out)


def build_regexes(vocab):
    res = {}
    for corpus, terms in vocab.items():
        # \b for ascii word starts; literal otherwise
        res[corpus] = re.compile("(?:" + "|".join(re.escape(t) for t in terms) + ")",
                                  re.IGNORECASE)
    return res


def iter_artifacts(roots):
    for root in roots:
        root = root.expanduser()
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file() or p.suffix.lower() not in EXTS:
                continue
            if any(part in SKIP_PARTS for part in p.parts):
                continue
            yield p


def probe(p: Path, n=2048) -> str:
    if p.suffix.lower() not in PROBE_EXTS:
        return ""
    try:
        return p.read_text(encoding="utf-8", errors="replace")[:n]
    except Exception:
        return ""


def classify(p: Path, body: str, regexes):
    """Return (primary_corpus|None, {corpus: hit_count})."""
    scan = p.name + " " + p.parent.name + " " + body
    counts = {}
    for corpus, rx in regexes.items():
        n = len(rx.findall(scan))
        if n:
            counts[corpus] = n
    if not counts:
        return None, {}
    primary = max(counts, key=counts.get)
    return primary, counts


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--roots", nargs="+", required=True)
    ap.add_argument("--vocab", type=Path, default=None,
                    help="override vocab: lines 'CORPUS: term'")
    ap.add_argument("--out", default="helen_manifest_v1.json")
    args = ap.parse_args()

    vocab = load_vocab(args.vocab)
    regexes = build_regexes(vocab)
    roots = [Path(r) for r in args.roots]

    records = []
    by_corpus = defaultdict(int)
    by_title = defaultdict(list)   # stem -> [paths]  (duplicate detection)
    seen = orphans = 0

    for p in iter_artifacts(roots):
        seen += 1
        primary, counts = classify(p, probe(p), regexes)
        if primary is None:
            orphans += 1
            continue
        by_corpus[primary] += 1
        by_title[p.stem.lower()].append(str(p))
        secondary = sorted(c for c in counts if c != primary)
        records.append({
            "id": "art-" + hashlib.sha1(str(p).encode()).hexdigest()[:12],
            "title": p.stem,
            "path": str(p),
            "corpus": primary,
            "secondary_corpora": secondary,
            "status": "RAW",                    # never CANONICAL without op mark
            "kind": p.suffix.lower().lstrip("."),
            "depends_on": [],                   # G=(V,E) — operator-marked only
            "corpus_hits": counts,
            "mtime": datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).isoformat(),
        })

    # duplicates = same title-stem across >1 path (the 31-tree sprawl, quantified)
    duplicates = {stem: paths for stem, paths in by_title.items() if len(paths) > 1}
    dup_artifacts = sum(len(v) for v in duplicates.values())

    out = Path(args.out)
    out.write_text(json.dumps({
        "schema": "HELEN_MANIFEST_V1",
        "authority": False, "claim": "NO_CLAIM",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "vocab": vocab,
        "roots_scanned": [str(r) for r in roots],
        "summary": {
            "seen": seen, "classified": len(records), "orphans": orphans,
            "by_corpus": dict(by_corpus),
            "duplicate_titles": len(duplicates),
            "duplicate_artifacts": dup_artifacts,
        },
        "records": records,
        "duplicates": duplicates,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"== HELEN_MANIFEST_V1 ==")
    print(f"   artifacts seen:    {seen}")
    print(f"   classified:        {len(records)}")
    print(f"   orphans (no match):{orphans}")
    print(f"\n   by corpus:")
    for c in ("MATHS", "CONSTITUTION", "IDENTITY"):
        print(f"     {by_corpus.get(c, 0):>5}  {c}")
    print(f"\n   DUPLICATE titles:  {len(duplicates)}  "
          f"({dup_artifacts} artifacts) — the sprawl, quantified")
    if duplicates:
        worst = sorted(duplicates.items(), key=lambda x: -len(x[1]))[:5]
        for stem, paths in worst:
            print(f"     {len(paths):>3}×  {stem[:40]}")
    print(f"\n   status: ALL RAW (none CANONICAL — operator marks canon)")
    print(f"   depends_on: ALL []  (graph edges = operator-marked, Frontier 3)")
    print(f"   manifest: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

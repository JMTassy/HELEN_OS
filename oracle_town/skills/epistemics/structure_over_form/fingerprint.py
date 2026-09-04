#!/usr/bin/env python3
"""WULmoji structural fingerprint — L1 layer of epistemics/structure_over_form.

Deterministic: same corpus bytes -> same JSON output. No clock, no network,
no randomness. Identity by NFC codepoint sequence, never by visual form.

Usage:
    python3 fingerprint.py --root <repo_root> --out <artifact.json>

Corpus rule (declared before computation, see SKILL.md invariant 2):
all *.md TRACKED AT GIT HEAD (git ls-files), excluding deprecated/,
.claude/ — deprecated/ predates palette calibration (2026-04-20) and would
measure pre-doctrinal noise. Tracked-only closes the self-reference hole:
this skill's own uncommitted outputs cannot enter the corpus they measure
(observer must not become actor). The measured commit is recorded.
"""

import argparse
import hashlib
import itertools
import json
import subprocess
import sys
import unicodedata
from pathlib import Path

# Locked 14-symbol palette (wulmoji_enhancer SKILL.md section 2), given as
# explicit codepoint sequences. U+FE0F variation selectors are part of the
# canonical form where present; a bare U+26A0 is counted as a declared
# variant, not silently folded (FORM != IDENTITY at the byte level).
PALETTE = {
    "identity": "\U0001F534",        # red circle
    "emotion": "\U0001F7E0",         # orange circle
    "cost": "\U0001F7E1",            # yellow circle
    "validation": "\U0001F7E2",      # green circle
    "structure": "\U0001F535",       # blue circle
    "emergent": "\U0001F7E3",        # purple circle
    "next_step": "⚪",           # white circle
    "warning": "⚠️",       # warning sign + VS16
    "direction": "\U0001F3AC",       # clapper board
    "artifact": "\U0001F4E6",        # package
    "metrics": "\U0001F4CA",         # bar chart
    "loop": "\U0001F501",            # repeat
    "operator": "✍️",      # writing hand + VS16
    "ship": "\U0001F680",            # rocket
}
VARIANTS = {
    "warning_bare": "⚠",        # warning without VS16
    "operator_bare": "✍",       # writing hand without VS16
}
EXCLUDE_PARTS = {".git", "deprecated", ".claude", "node_modules"}


def find_symbols(text, table):
    """Return list of (category, position) for palette hits, longest-first."""
    hits = []
    ordered = sorted(table.items(), key=lambda kv: -len(kv[1]))
    consumed = set()
    for cat, sym in ordered:
        start = 0
        while True:
            i = text.find(sym, start)
            if i < 0:
                break
            span = set(range(i, i + len(sym)))
            if not span & consumed:
                hits.append((cat, i))
                consumed |= span
            start = i + len(sym)
    return hits


def pair_counts(units):
    """Unordered pair frequencies across a list of category-lists."""
    pairs = {}
    for cats in units:
        for a, b in itertools.combinations(sorted(set(cats)), 2):
            key = a + "|" + b
            pairs[key] = pairs.get(key, 0) + 1
    return dict(sorted(pairs.items()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    root = Path(args.root)

    head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                          capture_output=True, text=True,
                          check=True).stdout.strip()
    tracked = subprocess.run(["git", "-C", str(root), "ls-files", "*.md"],
                             capture_output=True, text=True,
                             check=True).stdout.splitlines()
    files = sorted(
        root / f for f in tracked
        if not (set(Path(f).parts[:-1]) & EXCLUDE_PARTS)
        and (root / f).is_file()
    )

    manifest = []
    counts = {k: 0 for k in PALETTE}
    variant_counts = {k: 0 for k in VARIANTS}
    line_units, block_units, doc_units = [], [], []
    line_violations = []  # >1 palette symbol on one line = density breach

    for p in files:
        raw = p.read_bytes()
        text = unicodedata.normalize("NFC", raw.decode("utf-8", "replace"))
        rel = str(p.relative_to(root))
        doc_cats = []
        block_cats = []
        hit_any = False
        for ln, line in enumerate(text.splitlines(), 1):
            cats = [c for c, _ in find_symbols(line, PALETTE)]
            for vc, vs in VARIANTS.items():
                # count bare forms not already consumed by canonical match
                bare = line.count(vs) - line.count(PALETTE.get(
                    vc.replace("_bare", ""), "\0"))
                if bare > 0:
                    variant_counts[vc] += bare
            if cats:
                hit_any = True
                doc_cats.extend(cats)
                block_cats.extend(cats)
                for c in cats:
                    counts[c] += 1
                line_units.append(cats)
                if len(cats) > 1:
                    line_violations.append({"file": rel, "line": ln,
                                            "symbols": sorted(set(cats))})
            if not line.strip():
                if block_cats:
                    block_units.append(block_cats)
                block_cats = []
        if block_cats:
            block_units.append(block_cats)
        if doc_cats:
            doc_units.append(doc_cats)
        if hit_any:
            manifest.append({"file": rel,
                             "sha256": hashlib.sha256(raw).hexdigest()})

    artifact = {
        "artifact": "WULMOJI_STRUCTURE_FINGERPRINT_V0",
        "authority": False,
        "claim_status": "NO_CLAIM",
        "layer": "L1_STRUCTURE_EMPIRICAL",
        "corpus_rule": ("*.md tracked at git HEAD (ls-files) minus "
                        "deprecated/, .claude/ — uncommitted skill outputs "
                        "cannot enter the corpus they measure"),
        "measured_commit": head,
        "palette_codepoints": {k: [hex(ord(ch)) for ch in v]
                               for k, v in PALETTE.items()},
        "files_scanned": len(files),
        "files_with_palette": len(manifest),
        "symbol_counts": dict(sorted(counts.items())),
        "variant_counts": variant_counts,
        "pair_matrix": {
            "window_line": pair_counts(line_units),
            "window_block": pair_counts(block_units),
            "window_document": pair_counts(doc_units),
        },
        "density_rule_violations": {
            "count": len(line_violations),
            "note": ("doctrine max 1 symbol/line: in-line pairs are a "
                     "compliance signal, not structure"),
            "sample": line_violations[:40],
        },
        "corpus_manifest": manifest,
    }
    payload = json.dumps(artifact, ensure_ascii=False, indent=2,
                         sort_keys=False)
    artifact_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    out = {"payload": artifact, "payload_sha256": artifact_hash}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2),
                              encoding="utf-8")
    print(f"files_scanned={len(files)} with_palette={len(manifest)} "
          f"violations={len(line_violations)} sha256={artifact_hash[:16]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

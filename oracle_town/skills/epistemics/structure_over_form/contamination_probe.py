#!/usr/bin/env python3
"""Contamination counterfactual — palette lock as experimental control.

Control      : locked WULmoji-v1 palette (14 tokens) — fingerprint.py
Counterfactual: same corpus, vocabulary contaminated with 14 WULmath-v0
register tokens. The delta between the two pair-structures is an
empirical measure of semantic-language drift caused by uncontrolled
vocabulary expansion. GARDEN / NO_CLAIM. Deterministic.

Usage: python3 contamination_probe.py --root <repo> --out <json>
"""

import argparse
import hashlib
import json
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fingerprint import PALETTE, EXCLUDE_PARTS, find_symbols, pair_counts  # noqa: E402
import subprocess  # noqa: E402

# WULmath-v0 register tokens (14, symmetric with the locked palette).
WULMATH = {
    "wm_context": "\U0001F9E9",      # 🧩 formal context
    "wm_objects": "\U0001F523",      # 🔣 objects G
    "wm_attributes": "\U0001F9EC",   # 🧬 attributes M
    "wm_incidence": "\U0001F517",    # 🔗 incidence I
    "wm_cognition": "\U0001F4AD",    # 💭 free cognition
    "wm_hold": "\U0001F33F",         # 🌿 hold / uncertainty
    "wm_provenance": "🕯️",  # 🕯️ provenance
    "wm_falsifier": "🛡️",   # 🛡️ falsification
    "wm_ledger": "\U0001F4DC",       # 📜 governed reality
    "wm_authority": "\U0001F451",    # 👑 authority
    "wm_receipt": "\U0001F9FE",      # 🧾 evidence
    "wm_mutation": "\U0001F300",     # 🌀 lateral mutation
    "wm_observe": "👁️",     # 👁️ observation
    "wm_closure": "⚖️",     # ⚖️ closure/adjudication
}


def scan(root, files, table):
    line_units, block_units = [], []
    counts = {k: 0 for k in table}
    for p in files:
        text = unicodedata.normalize(
            "NFC", p.read_bytes().decode("utf-8", "replace"))
        block = []
        for line in text.splitlines():
            cats = [c for c, _ in find_symbols(line, table)]
            if cats:
                line_units.append(cats)
                block.extend(cats)
                for c in cats:
                    counts[c] += 1
            if not line.strip():
                if block:
                    block_units.append(block)
                block = []
        if block:
            block_units.append(block)
    return counts, pair_counts(block_units)


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

    control_counts, control_pairs = scan(root, files, PALETTE)
    contaminated = dict(PALETTE)
    contaminated.update(WULMATH)
    cont_counts, cont_pairs = scan(root, files, contaminated)

    def mass(pairs):
        return sum(pairs.values())

    cross = {k: v for k, v in cont_pairs.items()
             if (k.split("|")[0] in WULMATH) != (k.split("|")[1] in WULMATH)}
    math_only = {k: v for k, v in cont_pairs.items()
                 if k.split("|")[0] in WULMATH and k.split("|")[1] in WULMATH}

    def top(d, n=10):
        return sorted(d.items(), key=lambda x: (-x[1], x[0]))[:n]

    control_rank = [k for k, _ in top(control_pairs, 10)]
    cont_rank_v1only = [k for k, _ in top(
        {k: v for k, v in cont_pairs.items()
         if k.split("|")[0] in PALETTE and k.split("|")[1] in PALETTE}, 10)]

    artifact = {
        "artifact": "WULMOJI_CONTAMINATION_PROBE_V0",
        "authority": False,
        "claim_status": "NO_CLAIM",
        "measured_commit": head,
        "control_vocab_size": len(PALETTE),
        "contaminated_vocab_size": len(contaminated),
        "control": {
            "pair_mass_block": mass(control_pairs),
            "distinct_pairs": len(control_pairs),
            "top10": top(control_pairs, 10),
        },
        "contaminated": {
            "pair_mass_block": mass(cont_pairs),
            "distinct_pairs": len(cont_pairs),
            "top10": top(cont_pairs, 10),
            "wulmath_token_counts": {k: v for k, v in cont_counts.items()
                                     if k in WULMATH and v},
            "cross_register_pair_mass": mass(cross),
            "wulmath_only_pair_mass": mass(math_only),
            "top10_cross_register": top(cross, 10),
        },
        "drift_measures": {
            "pair_mass_inflation": round(
                mass(cont_pairs) / max(1, mass(control_pairs)), 3),
            "cross_register_share_of_contaminated_mass": round(
                mass(cross) / max(1, mass(cont_pairs)), 3),
            "v1_top10_rank_preserved_under_contamination":
                control_rank == cont_rank_v1only,
        },
    }
    payload = json.dumps(artifact, ensure_ascii=False, indent=2)
    Path(args.out).write_text(json.dumps(
        {"payload": artifact,
         "payload_sha256": hashlib.sha256(payload.encode()).hexdigest()},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(artifact["drift_measures"], indent=2))
    print("control_top4:", artifact["control"]["top10"][:4])
    print("cross_top4:", artifact["contaminated"]["top10_cross_register"][:4])
    print("wulmath_counts:", artifact["contaminated"]["wulmath_token_counts"])
    return 0


if __name__ == "__main__":
    sys.exit(main())

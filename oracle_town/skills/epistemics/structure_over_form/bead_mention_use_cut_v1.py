#!/usr/bin/env python3
"""mention_use_cut_v1 — the frozen FIRST_BEAD of EGREGOR__WULMOJI_FINGERPRINT_V0.

ALL metrics and rules declared here, before results (pre-registration):
  LEGEND rule (blind, syntactic): a palette-bearing line is LEGEND iff
    (a) stripped line starts with '|' (markdown table row), OR
    (b) it contains >= 4 distinct palette categories.
    USE lines = palette-bearing lines that are not LEGEND.
  Pair window: blank-line-delimited blocks, rebuilt from USE lines only.
  Fingerprint: normalized unordered-pair distribution p_ij.
  Distance D1(P,Q) = 0.5 * sum |p_ij - q_ij|  (total variation).
  Permutation null (pair significance): N=1000, seed=42 — shuffle symbol
    occurrences across USE lines preserving line sizes AND marginals;
    a pair is SIGNIFICANT iff observed count > 95th percentile of null.
  Warning-isolation probe: observed warning pair mass vs null expectation.
  Matched-null contamination: n=20 replicates, seeds 1000..1019 —
    WULmath occurrence positions FIXED, token identities redrawn iid from
    the observed WULmath marginal distribution. D(A,B) vs {D(A,C_i)}.
  Bare-warning lineage: lines with U+26A0 not followed by U+FE0F,
    normalized (digits->#, whitespace collapsed), clustered by identity.
GARDEN / NO_CLAIM. Deterministic (seeded). No clock, no network.
"""

import hashlib
import itertools
import json
import random
import subprocess
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fingerprint import PALETTE, EXCLUDE_PARTS, find_symbols  # noqa: E402
from contamination_probe import WULMATH  # noqa: E402

SEED_PERM = 42
N_PERM = 1000
SEED_NULLS = 1000
N_NULLS = 20


def corpus_files(root):
    tracked = subprocess.run(["git", "-C", str(root), "ls-files", "*.md"],
                             capture_output=True, text=True,
                             check=True).stdout.splitlines()
    return sorted(
        root / f for f in tracked
        if not (set(Path(f).parts[:-1]) & EXCLUDE_PARTS)
        and (root / f).is_file())


def classify_lines(files):
    """Return per-file lists of (line_no, cats_v1, cats_math, is_legend,
    is_blank, raw_line)."""
    out = []
    for p in files:
        text = unicodedata.normalize(
            "NFC", p.read_bytes().decode("utf-8", "replace"))
        rows = []
        for ln, line in enumerate(text.splitlines(), 1):
            cats = [c for c, _ in find_symbols(line, PALETTE)]
            mcats = [c for c, _ in find_symbols(line, WULMATH)]
            legend = bool(cats) and (line.strip().startswith("|")
                                     or len(set(cats)) >= 4)
            rows.append((ln, cats, mcats, legend, not line.strip(), line))
        out.append((p, rows))
    return out


def blocks_from(rows, use_only, with_math=False):
    """Blank-delimited blocks of category lists."""
    blocks, cur = [], []
    for _, cats, mcats, legend, blank, _ in rows:
        if blank:
            if cur:
                blocks.append(cur)
            cur = []
            continue
        if cats and (not use_only or not legend):
            cur.extend(cats)
            if with_math:
                cur.extend(mcats)
        elif with_math and mcats and (not use_only or not legend):
            cur.extend(mcats)
    if cur:
        blocks.append(cur)
    return blocks


def pair_dist(blocks):
    pairs = {}
    for b in blocks:
        for a, c in itertools.combinations(sorted(set(b)), 2):
            pairs[a + "|" + c] = pairs.get(a + "|" + c, 0) + 1
    total = sum(pairs.values()) or 1
    return pairs, {k: v / total for k, v in pairs.items()}


def d1(p, q):
    keys = set(p) | set(q)
    return 0.5 * sum(abs(p.get(k, 0) - q.get(k, 0)) for k in keys)


def perm_null_pairs(blocks, n, seed):
    """Shuffle symbols across blocks preserving block sizes + marginals."""
    rng = random.Random(seed)
    bag = [s for b in blocks for s in b]
    sizes = [len(b) for b in blocks]
    null_counts = {}
    for _ in range(n):
        rng.shuffle(bag)
        i, null_pairs = 0, {}
        for sz in sizes:
            chunk = bag[i:i + sz]
            i += sz
            for a, c in itertools.combinations(sorted(set(chunk)), 2):
                null_pairs[a + "|" + c] = null_pairs.get(a + "|" + c, 0) + 1
        for k, v in null_pairs.items():
            null_counts.setdefault(k, []).append(v)
    return null_counts


def q95(vals, n):
    vals = sorted(vals) + [0] * (n - len(vals))
    vals.sort()
    return vals[int(0.95 * n)]


def main():
    root = Path(sys.argv[sys.argv.index("--root") + 1])
    out = Path(sys.argv[sys.argv.index("--out") + 1])
    head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                          capture_output=True, text=True,
                          check=True).stdout.strip()
    files = corpus_files(root)
    classified = classify_lines(files)

    all_rows = [r for _, rows in classified for r in rows]
    legend_lines = sum(1 for r in all_rows if r[3])
    use_lines = sum(1 for r in all_rows if r[1] and not r[3])

    # --- USE-only v1 fingerprint + permutation null ---
    use_blocks = [b for _, rows in classified
                  for b in blocks_from(rows, use_only=True)]
    all_blocks = [b for _, rows in classified
                  for b in blocks_from(rows, use_only=False)]
    use_counts, use_p = pair_dist(use_blocks)
    all_counts, all_p = pair_dist(all_blocks)
    null = perm_null_pairs(use_blocks, N_PERM, SEED_PERM)
    significant = {k: {"obs": v, "null_q95": q95(null.get(k, []), N_PERM)}
                   for k, v in use_counts.items()
                   if v > q95(null.get(k, []), N_PERM)}

    warn_obs = sum(v for k, v in use_counts.items() if "warning" in k)
    warn_null = [sum(null.get(k, [0] * N_PERM)[i] if "warning" in k else 0
                     for k in null)
                 for i in range(min(N_PERM, 200))]
    warn_null_mean = sum(warn_null) / max(1, len(warn_null))

    # --- matched-null contamination on USE blocks ---
    def blocks_ext(identity_map_seed=None):
        rng = random.Random(identity_map_seed) if identity_map_seed else None
        marg = []
        for _, rows in classified:
            for _, _, mcats, legend, _, _ in rows:
                if not legend:
                    marg.extend(mcats)
        blocks = []
        for _, rows in classified:
            for b in _blocks_pairs(rows, rng, marg):
                blocks.append(b)
        return blocks

    def _blocks_pairs(rows, rng, marg):
        blocks, cur = [], []
        for _, cats, mcats, legend, blank, _ in rows:
            if blank:
                if cur:
                    blocks.append(cur)
                cur = []
                continue
            if legend:
                continue
            if cats:
                cur.extend(cats)
            for m in mcats:
                cur.append(rng.choice(marg) if rng else m)
        if cur:
            blocks.append(cur)
        return blocks

    _, pA = pair_dist(use_blocks)                    # locked, USE-only
    _, pB = pair_dist(blocks_ext(None))              # real WULmath identities
    dAB = d1(pA, pB)
    dACs = []
    for i in range(N_NULLS):
        _, pC = pair_dist(blocks_ext(SEED_NULLS + i))
        dACs.append(round(d1(pA, pC), 6))
    dACs_sorted = sorted(dACs)
    atypical = dAB > dACs_sorted[int(0.95 * N_NULLS)]

    # --- joint ranking (USE-only, real identities) ---
    cnt_ext, _ = pair_dist(blocks_ext(None))
    joint_top10 = sorted(cnt_ext.items(), key=lambda x: (-x[1], x[0]))[:10]
    v1_in_top10 = sum(1 for k, _ in joint_top10
                      if k.split("|")[0] in PALETTE
                      and k.split("|")[1] in PALETTE)

    # --- bare-warning lineage ---
    bare = []
    for p, rows in classified:
        for ln, _, _, _, _, line in rows:
            idx = 0
            while True:
                i = line.find("⚠", idx)
                if i < 0:
                    break
                if line[i + 1:i + 2] != "️":
                    bare.append((str(p.relative_to(root)), ln, line.strip()))
                idx = i + 1
    norm = {}
    for f, ln, text in bare:
        key = "".join("#" if ch.isdigit() else ch
                      for ch in " ".join(text.split()))[:80]
        norm.setdefault(key, []).append(f)
    clusters = sorted(((len(v), k) for k, v in norm.items()), reverse=True)

    artifact = {
        "artifact": "MENTION_USE_CUT_V1",
        "authority": False, "claim_status": "NO_CLAIM",
        "measured_commit": head,
        "preregistered": {"legend_rule": "table-row OR >=4 distinct cats",
                          "distance": "total variation on pair dists",
                          "perm_null": {"N": N_PERM, "seed": SEED_PERM},
                          "matched_nulls": {"n": N_NULLS,
                                            "seeds": f"{SEED_NULLS}.."}},
        "line_census": {"legend_lines": legend_lines, "use_lines": use_lines},
        "use_only": {
            "pair_mass": sum(use_counts.values()),
            "all_lines_pair_mass": sum(all_counts.values()),
            "mass_drop_pct": round(100 * (1 - sum(use_counts.values()) /
                                          max(1, sum(all_counts.values()))), 1),
            "top10": sorted(use_counts.items(),
                            key=lambda x: (-x[1], x[0]))[:10],
            "significant_pairs_vs_null": significant,
            "warning_pair_mass_obs": warn_obs,
            "warning_pair_mass_null_mean": round(warn_null_mean, 1),
        },
        "matched_null_contamination": {
            "D_A_B": round(dAB, 6), "D_A_C_distribution": dACs_sorted,
            "B_atypical_vs_nulls_q95": atypical,
        },
        "joint_ranking": {"top10": joint_top10,
                          "v1_pairs_in_joint_top10": v1_in_top10},
        "bare_warning_lineage": {
            "total": len(bare), "files": len({f for f, _, _ in bare}),
            "distinct_normalized_clusters": len(norm),
            "largest_clusters": clusters[:5],
        },
    }
    payload = json.dumps(artifact, ensure_ascii=False, indent=2)
    out.write_text(json.dumps(
        {"payload": artifact,
         "payload_sha256": hashlib.sha256(payload.encode()).hexdigest()},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: artifact[k] for k in
                      ("line_census", "matched_null_contamination",
                       "joint_ranking")}, ensure_ascii=False, indent=1))
    print("use_top6:", artifact["use_only"]["top10"][:6])
    print("mass_drop_pct:", artifact["use_only"]["mass_drop_pct"])
    print("sig_pairs:", list(artifact["use_only"]
                             ["significant_pairs_vs_null"])[:12])
    print("warn: obs", warn_obs, "null_mean", round(warn_null_mean, 1))
    print("bare_clusters:", len(norm), "of", len(bare))
    return 0


if __name__ == "__main__":
    sys.exit(main())

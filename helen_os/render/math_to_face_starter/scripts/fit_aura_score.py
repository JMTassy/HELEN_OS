"""Aura-score fit pipeline — stdlib only.

Reads: helen_os/render/math_to_face_starter/mia/helen_operator_ratings_v1.json

For every rated entry:
  - extract a feature vector
  - fit a linear combiner: aura_score = Σ w_i · feature_i + b
  - compute Spearman rank correlation vs operator_rating on held-out split

Decision gate (per MIA v2 acceptance criterion):
  - min 10 rated entries
  - 30% held-out split
  - Spearman ≥ 0.7 → PROMOTE to MIA v2
  - else → DO NOT PROMOTE (improve features or collect more ratings)

Pure stdlib. No numpy / sklearn / scipy required. Laptop Python 3.14 pip is
broken (libexpat), but this script runs on any Python 3.9+.

Run:
    PYTHONPATH=src python scripts/fit_aura_score.py
"""
from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

THIS = Path(__file__).resolve()
STARTER = THIS.parent.parent  # helen_os/render/math_to_face_starter
MIA = STARTER / "mia" / "helen_operator_ratings_v1.json"

MIN_RATED = 10
HELD_OUT_FRAC = 0.30
SPEARMAN_THRESHOLD = 0.70


# ── Feature extraction ────────────────────────────────────────────────
# Known session metadata (from transcript + commit history)
CREDIT_COST_BY_MSG = {
    708: 13,    # Phase 1 test
    711: 100,   # 10-shot 1-min cut
    712: 0,     # v2 voice overlay
    713: 10,    # full-song recomp + shot_11
    714: 20,    # dual portrait
    715: 0,     # creative ffmpeg montage
    716: 0,     # MIA v1 gallery
    717: 0,     # Mirror Oracle verdict poster
}

HAS_VOICE_BY_MSG = {708: 0, 711: 0, 712: 1, 713: 1, 714: 1, 715: 1, 716: 0, 717: 0}
HAS_COLOR_GRADING_BY_MSG = {708: 0, 711: 0, 712: 0, 713: 0, 714: 0, 715: 1, 716: 0, 717: 0}
IS_DUAL_CANONICAL_BY_MSG = {708: 0, 711: 0, 712: 0, 713: 0, 714: 1, 715: 0, 716: 1, 717: 0}
IS_INFRASTRUCTURE_BY_MSG = {708: 0, 711: 0, 712: 0, 713: 0, 714: 0, 715: 0, 716: 1, 717: 1}


def stub_scores(entry: dict) -> tuple[float, float]:
    """Return (d_real, d_twin). For whole-delivery entries without a direct frame,
    estimate from session context (use 0.5 as middle sentinel)."""
    if entry.get("stub_d_real") is not None and entry.get("stub_d_twin") is not None:
        return float(entry["stub_d_real"]), float(entry["stub_d_twin"])
    return 0.5, 0.5


def extract_features(entry: dict) -> dict:
    d_real, d_twin = stub_scores(entry)
    msg = entry.get("source_msg", 0)
    cost = CREDIT_COST_BY_MSG.get(msg, 0)
    return {
        "stub_d_real": d_real,
        "stub_d_twin": d_twin,
        "stub_gate_passes": int((d_real <= 0.128) or (d_twin <= 0.127)),
        "log_cost_plus1": math.log10(cost + 1),
        "has_voice": HAS_VOICE_BY_MSG.get(msg, 0),
        "has_color_grading": HAS_COLOR_GRADING_BY_MSG.get(msg, 0),
        "is_dual_canonical": IS_DUAL_CANONICAL_BY_MSG.get(msg, 0),
        "is_infrastructure": IS_INFRASTRUCTURE_BY_MSG.get(msg, 0),
    }


# ── Stdlib linear regression via normal equations ────────────────────
def mat_transpose(A):
    return [[A[r][c] for r in range(len(A))] for c in range(len(A[0]))]


def mat_mul(A, B):
    rows_a, cols_a = len(A), len(A[0])
    rows_b, cols_b = len(B), len(B[0])
    assert cols_a == rows_b
    out = [[0.0] * cols_b for _ in range(rows_a)]
    for i in range(rows_a):
        for j in range(cols_b):
            s = 0.0
            for k in range(cols_a):
                s += A[i][k] * B[k][j]
            out[i][j] = s
    return out


def mat_inv(M):
    """Gauss-Jordan inversion for small n×n. Adds 1e-6·I for regularization."""
    n = len(M)
    M = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(M)]
    for i in range(n):
        M[i][i] += 1e-6  # Tikhonov
    for i in range(n):
        # pivot
        pivot = M[i][i]
        if abs(pivot) < 1e-12:
            # swap with a row below with non-zero pivot
            for k in range(i + 1, n):
                if abs(M[k][i]) > 1e-12:
                    M[i], M[k] = M[k], M[i]
                    pivot = M[i][i]
                    break
            else:
                raise ValueError("Singular matrix")
        for j in range(len(M[i])):
            M[i][j] /= pivot
        for k in range(n):
            if k != i:
                factor = M[k][i]
                for j in range(len(M[k])):
                    M[k][j] -= factor * M[i][j]
    return [row[n:] for row in M]


def linear_fit(X, y):
    """Ordinary least squares with intercept. X: list of feature dicts. y: list of floats."""
    feat_names = sorted(X[0].keys())
    # Build design matrix with intercept column
    A = [[1.0] + [row[f] for f in feat_names] for row in X]
    b = [[v] for v in y]
    At = mat_transpose(A)
    AtA = mat_mul(At, A)
    AtA_inv = mat_inv(AtA)
    Atb = mat_mul(At, b)
    coeffs = mat_mul(AtA_inv, Atb)
    intercept = coeffs[0][0]
    weights = {f: coeffs[i + 1][0] for i, f in enumerate(feat_names)}
    return intercept, weights, feat_names


def predict(entry_features: dict, intercept: float, weights: dict) -> float:
    return intercept + sum(weights[f] * entry_features[f] for f in weights)


# ── Spearman rank correlation ────────────────────────────────────────
def rankdata(values):
    """Average ranks, 1-indexed."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(values):
        j = i
        while j + 1 < len(values) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg_rank = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = avg_rank
        i = j + 1
    return ranks


def spearman(x, y):
    if len(x) < 2:
        return float("nan")
    rx = rankdata(x)
    ry = rankdata(y)
    mx = sum(rx) / len(rx)
    my = sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    denx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    deny = math.sqrt(sum((b - my) ** 2 for b in ry))
    if denx == 0 or deny == 0:
        return float("nan")
    return num / (denx * deny)


# ── Main ──────────────────────────────────────────────────────────────
def main() -> int:
    data = json.loads(MIA.read_text())
    entries = data["frames"]
    rated = [e for e in entries if e.get("operator_rating") is not None]
    unrated = [e for e in entries if e.get("operator_rating") is None]

    print(f"\n{'='*70}\n aura_score fit — v0 (stdlib OLS + Spearman)\n{'='*70}")
    print(f"\n  total entries : {len(entries)}")
    print(f"  rated         : {len(rated)}  (need ≥ {MIN_RATED})")
    print(f"  unrated       : {len(unrated)}")
    print()

    if len(rated) < MIN_RATED:
        print(f"  [STATUS] INSUFFICIENT DATA — need {MIN_RATED - len(rated)} more rated entries")
        print(f"  [DECISION] DO NOT PROMOTE to MIA v2 (blocked on operator rating data)")
        print()
        print("  Unrated entries waiting for operator rating:")
        for e in unrated:
            msg = e.get("source_msg", "?")
            kind = e.get("kind", "?")
            print(f"    - {e['id']}  ({kind}, msg {msg})")
        print()
        # Still attempt a dummy fit with whatever we have, just to validate the pipeline
        if len(rated) >= 2:
            print(f"  [PIPELINE VALIDATION] running OLS on n={len(rated)} for diagnostic only")
            _run_fit(rated, dummy=True)
        return 2  # exit code: blocked on data, not code

    # Enough data — real fit
    return _run_fit(rated, dummy=False)


def _run_fit(rated, dummy: bool):
    # Extract features
    X = [extract_features(e) for e in rated]
    y = [float(e["operator_rating"]) for e in rated]

    # Held-out split
    random.seed(42)
    idx = list(range(len(rated)))
    random.shuffle(idx)
    n_test = max(1, int(round(len(rated) * HELD_OUT_FRAC)))
    test_idx = set(idx[:n_test])
    train_X = [X[i] for i in range(len(X)) if i not in test_idx]
    train_y = [y[i] for i in range(len(y)) if i not in test_idx]
    test_X = [X[i] for i in range(len(X)) if i in test_idx]
    test_y = [y[i] for i in range(len(y)) if i in test_idx]

    if len(train_X) < 2:
        print(f"  [ERROR] train set too small (n={len(train_X)}); skipping fit")
        return 3

    intercept, weights, feat_names = linear_fit(train_X, train_y)
    print(f"  [fit] trained on n={len(train_X)}, tested on n={len(test_X)}")
    print(f"  [weights]")
    print(f"    intercept = {intercept:+.4f}")
    for f in feat_names:
        print(f"    {f:22s} = {weights[f]:+.4f}")
    print()

    # Evaluate on test set
    test_preds = [predict(x, intercept, weights) for x in test_X]
    rho = spearman(test_preds, test_y) if len(test_y) >= 2 else float("nan")
    train_preds = [predict(x, intercept, weights) for x in train_X]
    rho_train = spearman(train_preds, train_y) if len(train_y) >= 2 else float("nan")

    print(f"  [eval] Spearman(train) = {rho_train:+.4f}  (on n={len(train_y)})")
    print(f"  [eval] Spearman(test)  = {rho:+.4f}  (on n={len(test_y)})")
    print()

    if dummy:
        print(f"  [CAVEAT] n={len(rated)} is too few for meaningful Spearman.")
        print(f"  [DECISION] Pipeline validated; promotion remains BLOCKED on data.")
        return 2

    if rho >= SPEARMAN_THRESHOLD:
        print(f"  [GATE] Spearman({rho:+.4f}) ≥ {SPEARMAN_THRESHOLD}  →  PROMOTE to MIA v2")
        return 0
    else:
        print(f"  [GATE] Spearman({rho:+.4f}) < {SPEARMAN_THRESHOLD}  →  DO NOT PROMOTE")
        print(f"  [NEXT] Improve features (wire ArcFace / CLIP / LPIPS) or collect more ratings.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

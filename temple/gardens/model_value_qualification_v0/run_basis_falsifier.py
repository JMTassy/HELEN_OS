#!/usr/bin/env python3
"""
COGNITIVE_BASIS_FALSIFIER_V0 — leave-one-out ablation over the FROZEN operator-
response matrix from LOCAL_MODEL_VALUE_AND_OBSOLESCENCE_V0.

Value function = operator ENVELOPE (empirical cover):
    V_o(S) = max_i score(X_i, o)     (portfolio can do o if ANY member does)
Leave-one-out is deterministic given the frozen matrix (temp0 greedy scores).
    Δ_i^op = V(S) - V(S\{X_i})   →  supp = operators where X_i is UNIQUELY top.

DELETIONS_EXECUTED=0. authority=false. This QUALIFIES topology; it does NOT authorize deletion.
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent
OPS = ["A_reason", "B_falsify", "C_boundary", "D_wul", "F_discriminate"]
TAU = 1  # frozen threshold; a 1-point envelope drop counts as irreducible (thin)

# FROZEN score matrix (0-5), from qualification raw reads. Provenance: raw/*.txt
SCORES = {  # config: [A,B,C,D,F]
 "gemma-4-26B-Q3": [5, 4, 5, 5, 5],
 "gemma4-12b":     [5, 4, 4, 5, 4],
 "helen-hal":      [2, 2, 4, 5, 4],
 "helen-her-26b":  [5, 4, 4, 5, 4],
 "aura-gemma4":    [1, 1, 0, 0, 1],
 "helen-core":     [2, 4, 3, 5, 4],
}
# unique behaviors NOT measured by the 5 fixture operators (fixture-incompleteness)
UNMEASURED = {
 "helen-hal": "provenance-demand reflex (cryptographic-hash/ledger) + authority=false append",
 "helen-her-26b": "HER persona/replay value (named role seat, own Modelfile)",
 "gemma4-12b": "low latency (10.2s) — cost operator not in fixture",
 "aura-gemma4": "lowest latency (4.4s) — cost operator not in fixture",
}
UNIQUE_GB = {"gemma-4-26B-Q3": 14, "gemma4-12b": 0, "helen-hal": 6.6,
             "helen-her-26b": 14, "aura-gemma4": 5.3, "helen-core": 6.6}


def envelope(members):
    return [max(SCORES[m][k] for m in members) for k in range(len(OPS))]


def main():
    S = list(SCORES)
    V = envelope(S)
    rows = []
    for m in S:
        Vminus = envelope([x for x in S if x != m])
        delta = [V[k] - Vminus[k] for k in range(len(OPS))]
        supp = [OPS[k] for k in range(len(OPS)) if delta[k] >= TAU]
        status = "LOO_IRREDUCIBLE" if supp else "LOO_REDUNDANT"
        rows.append({"config": m, "scores": SCORES[m], "delta_op": delta,
                     "supp": supp, "status": status,
                     "unique_gb": UNIQUE_GB[m],
                     "unmeasured_signature": UNMEASURED.get(m),
                     "note": "single greedy trial → no cross-seed variance; margins ≤1 are UNRESOLVED"})

    # minimum-cost cover for the FIXTURE envelope V
    # greedy: does any single config cover the whole envelope?
    solo_cover = [m for m in S if SCORES[m] == V or all(SCORES[m][k] >= V[k] for k in range(len(OPS)))]

    receipt = {
      "schema": "COGNITIVE_BASIS_FALSIFIER_V0_RECEIPT",
      "authority": False, "canon": False, "deletions_executed": 0, "downloads_started": 0,
      "value_function": "operator ENVELOPE V_o(S)=max_i score(X_i,o) (empirical cognitive cover)",
      "operators_frozen": OPS,
      "tau": TAU,
      "portfolio_envelope_V": dict(zip(OPS, V)),
      "ablation": rows,
      "min_cost_cover_for_fixture_envelope": solo_cover or "no single config; needs subset search",
      "verdict": {
        "LOO_IRREDUCIBLE": [r["config"] for r in rows if r["status"] == "LOO_IRREDUCIBLE"],
        "LOO_REDUNDANT_on_fixture": [r["config"] for r in rows if r["status"] == "LOO_REDUNDANT"],
      },
      "hard_caveats": [
        "LOO_IRREDUCIBLE ≠ GLOBALLY_NECESSARY (higher-order substitution untested)",
        "LOO_REDUNDANT ≠ SAFE_TO_DELETE (set-valued redundancy: joint ablation of {12b,her,core} untested)",
        "fixture-incomplete: HAL provenance-demand & HER persona are NOT operators in O → their redundancy is an artifact of the 5-operator geometry, not proven",
        "single greedy trial → variance unmeasured; any Δ≤1 margin is UNRESOLVED pending multi-seed",
        "envelope=max-cover hides cost: gemma-4-26B alone covers the fixture but at 14GB/28s; cheaper members matter once latency/GB enter O",
      ],
      "law": "Standalone quality ⇏ portfolio necessity · ΔCognition ⇏ ΔAuthority · DELETE_CANDIDATE ⇏ DELETE_AUTHORIZED",
    }
    (ROOT / "COGNITIVE_BASIS_FALSIFIER_V0_RECEIPT.json").write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False))

    # print
    print("Δ_i^op  (envelope drop when config removed) · operators:", OPS)
    print("─" * 78)
    for r in rows:
        d = " ".join(f"{x:+d}" for x in r["delta_op"])
        print(f"{r['config']:16s} scores={r['scores']}  Δ=[{d}]  {r['status']:16s} supp={r['supp']}")
    print("─" * 78)
    print("portfolio envelope V =", dict(zip(OPS, V)))
    print("min-cost cover for fixture envelope =", solo_cover)
    print("IRREDUCIBLE:", receipt["verdict"]["LOO_IRREDUCIBLE"])
    print("REDUNDANT(fixture):", receipt["verdict"]["LOO_REDUNDANT_on_fixture"])


if __name__ == "__main__":
    main()

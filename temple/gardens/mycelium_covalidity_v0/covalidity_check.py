#!/usr/bin/env python3
"""
MYCELIUM_COVALIDITY_V0 — the missing primitive: joint-domain co-validity of retained discriminators.

Current Mycelium stores per-node validity ν. It CANNOT represent whether a SET of retained
discriminators was jointly validated on the region where they are actually composed. So it
silently assumes:   Valid(D1) ∧ Valid(D2)  ⇒  Valid(D1 ⊕ D2).
That is false — the analogue of quotient well-definedness (marginal ⇏ joint), and the exact
place composite failure hides (the interaction/diagonal).

Construction (deterministic grid, features a,b ∈ {0,1,2}):
  D1 : CANDIDATE iff a>=1   (its validation fixtures only ever had b=0)
  D2 : CANDIDATE iff b>=1   (its validation fixtures only ever had a=0)
  compose(x) = ADMIT iff D1=CANDIDATE ∧ D2=CANDIDATE
  gold a*(x) = ADMIT iff (a>=1 ∧ b>=1) AND NOT (a==2 ∧ b==2)   # (2,2) is a known BAD interaction
  D1 and D2 have IDENTICAL metadata (type=axis_discriminator, schema=v1, provenance=compiled)
  yet DIFFERENT validity boundaries → counterfeit-equivalent under metadata.

BASELINE gate (today): both are 'valid compiled instruments' → trust the composition everywhere.
MUTATED  gate (new)  : compose only where a CO-VALIDITY WITNESS ⋈({D1,D2}, δ) covers x; else HOLD.

authority=false · canon=false · ΔA=0 · ΔΓ=0 · NO_CLAIM · NO_MODEL_CALL · NO_COMMIT · NO_PUSH.
"""
import json
from pathlib import Path

GRID = [(a, b) for a in range(3) for b in range(3)]

def D1(x): return "CANDIDATE" if x[0] >= 1 else "BLOCK"      # validated only on slice b==0
def D2(x): return "CANDIDATE" if x[1] >= 1 else "BLOCK"      # validated only on slice a==0
def compose(x): return "ADMIT" if D1(x) == "CANDIDATE" and D2(x) == "CANDIDATE" else "REJECT"
def gold(x):
    a, b = x
    return "ADMIT" if (a >= 1 and b >= 1 and not (a == 2 and b == 2)) else "BLOCK"

# identical metadata for both retained nodes (the counterfeit-equivalence)
META_D1 = {"type": "axis_discriminator", "schema": "v1", "provenance": "compiled", "validity": "valid"}
META_D2 = {"type": "axis_discriminator", "schema": "v1", "provenance": "compiled", "validity": "valid"}

# per-node validated domains (the truth metadata cannot carry as a scalar 'valid')
VAL_D1 = {(a, b) for (a, b) in GRID if b == 0}
VAL_D2 = {(a, b) for (a, b) in GRID if a == 0}

# NEW PRIMITIVE: co-validity witness edge ⋈ over the SET {D1,D2}, carrying the jointly-validated domain
COVALID_WITNESS = {(1, 1), (1, 2), (2, 1)}          # composition tested & passed here; (2,2) NOT covered


def baseline_decision(x):
    """metadata-level: D1,D2 are 'valid compiled instruments' → compose fires (today's Mycelium reuse)."""
    return compose(x)

def covalid_decision(x):
    """require ⋈ to cover x for the fired set; absent witness → HOLD (reopen/compile joint)."""
    c = compose(x)
    if c != "ADMIT":
        return c
    return "ADMIT" if x in COVALID_WITNESS else "HOLD"

def false_accepts(fn): return [x for x in GRID if fn(x) == "ADMIT" and gold(x) == "BLOCK"]
def holds(fn):         return [x for x in GRID if fn(x) == "HOLD"]
def correct_admits(fn):return [x for x in GRID if fn(x) == "ADMIT" and gold(x) == "ADMIT"]


def main():
    meta_identical = (META_D1 == META_D2)
    boundaries_differ = (VAL_D1 != VAL_D2)
    fa_base, fa_cov = false_accepts(baseline_decision), false_accepts(covalid_decision)
    h_base, h_cov = holds(baseline_decision), holds(covalid_decision)

    # the well-definedness law, witnessed on this grid
    joint_gt_marginal = len(fa_base) > 0 and len(fa_cov) == 0
    counterfeit_caught = ((2, 2) in fa_base) and ((2, 2) in h_cov)

    result = {
        "experiment": "MYCELIUM_COVALIDITY_V0", "authority": False, "canon": False,
        "authority_delta": 0, "gamma_delta": 0, "model_calls": 0,
        "metadata_identical_D1_D2": meta_identical,
        "validity_boundaries_differ": boundaries_differ,
        "counterfeit_equivalent_under_metadata": meta_identical and boundaries_differ,
        "law": "Valid(D1,κ) ∧ Valid(D2,κ) ⇏ Valid(D1⊕D2,κ)  — joint requires a co-validity witness ⋈",
        "BASELINE_marginal_gate": {
            "false_accepts": fa_base, "n_false_accepts": len(fa_base),
            "holds": h_base, "correct_admits": correct_admits(baseline_decision)},
        "MUTATED_covalidity_gate": {
            "false_accepts": fa_cov, "n_false_accepts": len(fa_cov),
            "holds": h_cov, "correct_admits": correct_admits(covalid_decision),
            "note": "unwitnessed composition cell (2,2) HELD -> reopen/compile, not admitted"},
        "joint_exceeds_marginal_witnessed": joint_gt_marginal,
        "diagonal_counterfeit_caught": counterfeit_caught,
        "MAX_ADMISSIBLE_STATEMENT":
            "On this grid, two individually-valid, metadata-identical discriminators compose to a "
            "FALSE ACCEPT at the unwitnessed interaction cell (2,2); a co-validity witness ⋈ blocks it "
            "(HOLD) while preserving the genuinely co-validated admits.",
        "EXPLICIT_NON_CLAIMS": ["synthetic grid; not a claim about real retained instruments",
                                "⋈ demonstrated for a 2-set; k-set co-validity is the same relation generalized"],
        "commit_status": "NO_COMMIT", "push_status": "NO_PUSH", "next_verb": "HUMAN_REVIEW",
    }
    (Path(__file__).resolve().parent / "MYCELIUM_COVALIDITY_V0_RECEIPT.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False))

    print("═" * 76)
    print("  MYCELIUM_COVALIDITY_V0 — marginal validity ⇏ joint validity (the ⋈ primitive)")
    print("═" * 76)
    print(f"  D1,D2 metadata identical = {meta_identical} · validity boundaries differ = {boundaries_differ}")
    print(f"  → counterfeit-equivalent under metadata = {meta_identical and boundaries_differ}")
    print("─" * 76)
    print(f"  {'cell':7s} {'D1':10s} {'D2':10s} {'compose':8s} {'gold':6s} {'BASE':7s} {'⋈GATE':6s}")
    for x in GRID:
        print(f"  {str(x):7s} {D1(x):10s} {D2(x):10s} {compose(x):8s} {gold(x):6s} "
              f"{baseline_decision(x):7s} {covalid_decision(x):6s}")
    print("─" * 76)
    print(f"  BASELINE (marginal): false_accepts = {len(fa_base)}  at {fa_base}")
    print(f"  MUTATED  (⋈ witness): false_accepts = {len(fa_cov)}  · HOLDs = {h_cov}")
    print(f"  joint ⇏ marginal witnessed = {joint_gt_marginal} · diagonal counterfeit caught = {counterfeit_caught}")
    print(f"  ΔA=0 · ΔΓ=0 · model_calls=0 · NO_COMMIT")
    print("  → MYCELIUM_COVALIDITY_V0_RECEIPT.json")


if __name__ == "__main__":
    main()

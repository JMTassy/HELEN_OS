#!/usr/bin/env python3
"""
AUTHORITY_DELTA_ZERO_FALSIFIER_V0 — complete the tri-separation:
    ReceiptValidity  ≠  StateDelta(Δσ)  ≠  AuthorityDelta(ΔA).

Kills the confusion  Δσ≠0 ⇏ ΔA≠0, and the deeper one  DeclaredAuthority ≠ EffectiveAuthority.

CRITICAL DESIGN (the anti-laundering rule): ΔA is NOT Diff(A_before, A_after) over
free blobs — that would let a fixture WRITE A_after and mint authority by assertion.
Instead the effective post-state is DERIVED:
    A_after = ApplyAuthorizedTransitions(A_before, δ, W_A, Γ)
The resolver applies ONLY grants carrying a witness W_A that (a) is a type licensed by Γ,
(b) verifies against the authority key, and (c) BINDS to this specific δ (no replay).
Any payload-declared authority_after is ignored. Computation cannot mint authority.

Fixtures:
  F0 valid no-op        : Valid=1, Δσ=0,  ΔA=0
  F1 ordinary state Δ   : Valid=1, Δσ≠0,  ΔA=0        ← the tri-separation frontier
  F2 licensed authority : Valid=1, Δσ≠0,  ΔA≠0        (only WITH a valid, bound witness)
  M  counterfeit        : Δσ≠0, blob claims authority, NO valid witness → DerivedΔA=0
  M2 replay             : Δσ≠0, presents F2's witness on a DIFFERENT δ → binding fails → ΔA=0

authority=false · canon=false · ΔA=0 · NO_CLAIM · NO_MODEL_CALL · NO_COMMIT · NO_PUSH ·
synthetic keys/fixtures ONLY — no real mayor key, no real ledger, no sovereign path.
"""
import hashlib, json
from pathlib import Path

def canon(o): return json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
def sha(o):   return hashlib.sha256(canon(o).encode()).hexdigest()

# --- synthetic licensed-authority key (models MAYOR; the fixture-writer does NOT know it) ---
_AUTHORITY_SECRET = "SYNTHETIC_LICENSED_AUTHORITY_SECRET_not_a_real_key"
GAMMA = {"grant_cap"}   # the only licensed transition type

def sign_grant(grant_core):
    """Only the licensed authority can produce this (needs the secret)."""
    return sha({"core": grant_core, "k": _AUTHORITY_SECRET})

def make_witness(grant_type, adds, binds_to):
    core = {"grant_type": grant_type, "adds": sorted(adds), "binds_to": binds_to}
    return {"core": core, "sig": sign_grant(core)}

def delta_id(delta):
    return sha({"delta": delta})   # what a witness must bind to

def ApplyAuthorizedTransitions(A_before, delta, W_A, Gamma):
    """DERIVE the effective post authority-set. Ignores any declared blob."""
    A = set(A_before)
    if not W_A:                                   return frozenset(A)   # no witness → no grant
    core = W_A.get("core", {})
    if core.get("grant_type") not in Gamma:       return frozenset(A)   # unlicensed type
    if W_A.get("sig") != sign_grant(core):        return frozenset(A)   # bad sig — cannot mint
    if core.get("binds_to") != delta_id(delta):   return frozenset(A)   # replay / wrong δ
    A |= set(core.get("adds", []))                                      # ADMITTED
    return frozenset(A)

def VerifyReceipt(p):
    req = ("receipt_id", "state_before", "state_after", "authority_before")
    return 1 if all(k in p for k in req) else 0

def DerivedStateDelta(p):
    b, a = p["state_before"], p["state_after"]
    return {k: [b.get(k), a.get(k)] for k in sorted(set(b) | set(a)) if b.get(k) != a.get(k)}


def evaluate(name, state_before, state_after, A_before, W_A, declared_authority_after):
    delta = {k: [state_before.get(k), state_after.get(k)]
             for k in set(state_before) | set(state_after)
             if state_before.get(k) != state_after.get(k)}
    payload = {"receipt_id": name, "state_before": state_before, "state_after": state_after,
               "authority_before": sorted(A_before),
               "declared_authority_after": sorted(declared_authority_after)}  # the BLOB (may lie)
    A_after = ApplyAuthorizedTransitions(A_before, delta, W_A, GAMMA)         # the DERIVATION
    dsigma = DerivedStateDelta(payload)
    dA = sorted(set(A_after) ^ set(A_before))                                 # symmetric diff
    return {
        "id": name, "Valid": VerifyReceipt(payload),
        "DeltaSigma": dsigma, "Dsig_zero": len(dsigma) == 0,
        "declared_authority_after": sorted(declared_authority_after),
        "effective_authority_after": sorted(A_after),
        "DerivedDeltaA": dA, "DA_zero": len(dA) == 0,
        "declared_matches_effective": sorted(declared_authority_after) == sorted(A_after),
    }


def main():
    base = frozenset({"read"})
    dS = ({"x": 1}, {"x": 2})           # a real state move
    did = delta_id({"x": [1, 2]})       # binding target for a legitimate grant on dS
    good_witness = make_witness("grant_cap", {"admin"}, binds_to=did)

    rows = [
        evaluate("F0", {"x": 1}, {"x": 1}, base, None, base),                       # no-op
        evaluate("F1", *map(dict, dS), A_before=base, W_A=None,                      # state moves, auth doesn't
                 declared_authority_after=base),
        evaluate("F2", *map(dict, dS), A_before=base, W_A=good_witness,             # licensed grant
                 declared_authority_after=base | {"admin"}),
        evaluate("M",  *map(dict, dS), A_before=base, W_A=None,                      # LIAR: blob claims admin
                 declared_authority_after=base | {"admin"}),
        evaluate("M2", {"y": 0}, {"y": 5}, base, good_witness,                       # REPLAY on different δ
                 declared_authority_after=base | {"admin"}),
    ]
    d = {r["id"]: r for r in rows}

    W_F1_frontier = (d["F1"]["Valid"] == 1 and not d["F1"]["Dsig_zero"] and d["F1"]["DA_zero"])
    W_F2_soundness = (not d["F2"]["Dsig_zero"] and not d["F2"]["DA_zero"])           # resolver CAN grant
    W_M_liar = (not d["M"]["Dsig_zero"] and d["M"]["DA_zero"]
                and d["M"]["declared_authority_after"] != base_sorted(base)
                and not d["M"]["declared_matches_effective"])
    W_M2_replay = (not d["M2"]["Dsig_zero"] and d["M2"]["DA_zero"])
    all_hold = W_F1_frontier and W_F2_soundness and W_M_liar and W_M2_replay

    receipt = {
        "experiment": "AUTHORITY_DELTA_ZERO_FALSIFIER_V0",
        "authority": False, "canon": False, "claim": "NO_CLAIM",
        "authority_delta": 0, "model_calls": 0, "fixtures": "synthetic",
        "tri_separation": "ReceiptValidity ≠ StateDelta ≠ AuthorityDelta",
        "target_confusions_killed": ["Δσ≠0 ⇏ ΔA≠0", "DeclaredAuthority ≠ EffectiveAuthority"],
        "anti_laundering_rule": "A_after = ApplyAuthorizedTransitions(A_before, δ, W_A, Γ); "
                                "payload-declared authority_after is IGNORED; computation cannot mint authority",
        "W_F1_state_moved_authority_did_not_(frontier)": W_F1_frontier,
        "W_F2_licensed_witness_grants_(soundness)": W_F2_soundness,
        "W_M_counterfeit_claim_yields_zero_derived_authority": W_M_liar,
        "W_M2_replayed_witness_on_wrong_delta_rejected": W_M2_replay,
        "rows": rows,
        "MAX_ADMISSIBLE_STATEMENT":
            "AUTHORITY_DELTA_REQUIRES_WITNESSED_LICENSED_BOUND_TRANSITION (on these 5 fixtures)",
        "EXPLICIT_NON_CLAIMS": [
            "NOT 'HELEN authority is unforgeable'",
            "NOT a statement about real mayor keys / real Γ / real ledger",
            "synthetic authority secret only — models the resolver shape, not HELEN's crypto"],
        "commit_status": "NO_COMMIT", "push_status": "NO_PUSH", "next_verb": "HUMAN_REVIEW",
    }
    receipt["receipt_hash"] = sha(receipt)

    print("═" * 74)
    print("  AUTHORITY_DELTA_ZERO_FALSIFIER_V0 — Δσ≠0 ⇏ ΔA≠0 ; Declared ≠ Effective (no model)")
    print("═" * 74)
    print(f"  {'id':3s} {'Valid':6s} {'Δσ=0':6s} {'declared_auth_after':22s} {'EFFECTIVE(derived)':20s} {'ΔA=0':6s}")
    for r in rows:
        print(f"  {r['id']:3s} {str(r['Valid']):6s} {str(r['Dsig_zero']):6s} "
              f"{str(r['declared_authority_after']):22s} {str(r['effective_authority_after']):20s} "
              f"{str(r['DA_zero']):6s}")
    print("─" * 74)
    print(f"  F1 frontier   state moved, authority did NOT (Δσ≠0 ∧ ΔA=0) : {'✅' if W_F1_frontier else '❌'}")
    print(f"  F2 soundness  valid bound witness DOES grant (ΔA≠0)        : {'✅' if W_F2_soundness else '❌'}")
    print(f"  M  liar       blob claims admin, DERIVED ΔA=0              : {'✅ minting blocked' if W_M_liar else '❌'}")
    print(f"  M2 replay     F2 witness on different δ rejected (ΔA=0)    : {'✅' if W_M2_replay else '❌'}")
    print("─" * 74)
    print("  M: declared_authority_after = ['admin','read']  but  EFFECTIVE = ['read']")
    print("     → DeclaredAuthorityState ≠ EffectiveAuthorityState ; computation cannot mint authority")
    print(f"  MAX ADMISSIBLE: {receipt['MAX_ADMISSIBLE_STATEMENT']}")
    print(f"  VERDICT: {'ALL WITNESSES HOLD ✅' if all_hold else 'INCOMPLETE ❌'} · ΔA=0 · model_calls=0 · NO_COMMIT")
    print(f"  receipt_hash = {receipt['receipt_hash'][:16]}…")

    out = Path(__file__).resolve().parent / "AUTHORITY_DELTA_ZERO_V0_RECEIPT.json"
    out.write_text(json.dumps(receipt, indent=2, ensure_ascii=False))
    print(f"  → {out.name}")


def base_sorted(b): return sorted(b)

if __name__ == "__main__":
    main()

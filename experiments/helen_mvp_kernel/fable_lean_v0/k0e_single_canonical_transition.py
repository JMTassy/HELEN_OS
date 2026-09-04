"""K0e — SINGLE CANONICAL TRANSITION. authority=false · canon=false · ledger_effect=none. NON-SOVEREIGN.
Witnesses that verifier, gate, reducer, and receipt consume the EXACT SAME transition identity:
    χ = sha256(canonical(delta))   ·   Verify(χ)=Gate(χ)=Reduce(χ)=Receipt(χ)
A ProofCarryingTransition = (χ, VW_X, VW_E, VW_P), all bound to the same χ. Any stage that reconstructs delta
differently ⇒ REJECT | TRANSITION_HASH_MISMATCH, state unchanged. Scope: linearizable-commit dimension, χ-identity
only. Does NOT touch process isolation (K0b/K0c) or K0f expected-head — bounded on purpose.
"""
import hashlib, json

def canonical(delta) -> str:
    return json.dumps(delta, sort_keys=True, separators=(",", ":"))     # deterministic; representation-invariant
def chi(delta) -> str:
    return "sha256:" + hashlib.sha256(canonical(delta).encode()).hexdigest()[:16]

class TrustedPath:
    def __init__(self): self._state = set(); self._history = []
    def state_hash(self):
        return "sha256:" + hashlib.sha256("|".join(sorted(self._state)).encode()).hexdigest()[:16]
    def process(self, verify_delta, gate_delta, reduce_delta, receipt_delta):
        """Every stage recomputes χ from the delta IT was handed. All four must equal the verified χ."""
        cv = chi(verify_delta)                          # verifier admits THIS identity
        cg, cr, crc = chi(gate_delta), chi(reduce_delta), chi(receipt_delta)
        chis = {"verify": cv, "gate": cg, "reduce": cr, "receipt": crc}
        if not (cg == cv and cr == cv and crc == cv):
            return {"decision": "REJECT", "reason": "TRANSITION_HASH_MISMATCH", "chis": chis}   # NO state write
        # all four identities agree → reducer commits, receipt records the SAME χ
        self._state.add(f"admitted:{cv}"); self._history.append({"chi": cv})
        return {"decision": "ADMIT", "reason": "SINGLE_CANONICAL", "chis": chis, "chi": cv}

def main():
    print("=== K0e — single canonical transition (Verify=Gate=Reduce=Receipt on χ) ===")
    A = {"op": "promote", "subject": "campus", "scope": "corsica", "n": 1}
    B = {"op": "promote", "subject": "campus", "scope": "corsica", "n": 2}   # different delta ⇒ different χ
    A_reordered = {"n": 1, "scope": "corsica", "subject": "campus", "op": "promote"}   # same semantics, diff order
    A_omitted = {"op": "promote", "subject": "campus", "scope": "corsica"}   # field 'n' removed

    tests = [
        ("1_VALID_CONTROL",       (A, A, A, A),           "ADMIT",  "SINGLE_CANONICAL"),
        ("2_VERIFY_REDUCE_SUB",   (A, A, B, A),           "REJECT", "TRANSITION_HASH_MISMATCH"),
        ("3_GATE_RECEIPT_SUB",    (A, A, A, B),           "REJECT", "TRANSITION_HASH_MISMATCH"),
        ("4_CANON_DIFFERENTIAL",  (A, A_reordered, A, A), "ADMIT",  "SINGLE_CANONICAL"),   # must canonicalize to same χ
        ("5_FIELD_OMISSION",      (A, A, A_omitted, A),   "REJECT", "TRANSITION_HASH_MISMATCH"),
    ]
    rows = []
    for tid, args, exp_v, exp_r in tests:
        tp = TrustedPath()
        sb = tp.state_hash()
        r = tp.process(*args)
        sa = tp.state_hash()
        state_ok = (sa == sb) if r["decision"] == "REJECT" else (sa != sb)   # reject ⇒ unchanged; admit ⇒ changed
        pas = (r["decision"] == exp_v and r["reason"] == exp_r and state_ok)
        rows.append(pas)
        cv = {k: v[-6:] for k, v in r["chis"].items()}
        print(f"  {tid:22} act={r['decision']:6}/{r['reason']:24} χ(v/g/r/rc last6)={cv} state{'=' if sa==sb else '≠'} {'PASS' if pas else 'FAIL'}")

    allok = all(rows)
    print(f"\n  K0e = {'SURVIVED_DEFINED_ATTACK_SET' if allok else 'FALSIFIED'}  ({sum(rows)}/{len(rows)})")
    print("  earned: one transition identity χ survives verify→gate→reduce→receipt; substitution/omission rejected;")
    print("          canonicalization differential collapses to same χ (representation ⇏ different identity).")
    print("  NOT in scope: K0f expected-head · K0b/K0c isolation · crash-consistency (bounded per protocol)")
    print("  authority=false · canon=false · ledger_effect=none")

if __name__ == "__main__":
    main()

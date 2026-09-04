"""K0d — CONTEXT-BOUND WITNESS (the B in K0 = I ∧ B ∧ R). authority=false · canon=false · ledger_effect=none.
Witnesses E21-E27 as EXECUTABLE tests (not just derivations): a VerifiedWitness is bound to
(candidate_hash, verifier_id, semantic_version, scope, dim). Any substitution on a bound axis ⇒ REJECT.
    VW_T @ (δ1,v1,Γ1,scope1)  ↛  accept @ (δ2,v2,Γ2,scope2)   unless every required binding is equal.
HONEST BOUND: this closes B (binding). It does NOT close R (K0b/K0c) — the mint is still in-process reachable;
full isolation needs the kernel-v2 process boundary. Security = I ∧ B ∧ R; this file earns B.
"""
import hmac, hashlib

class BoundVerifier:
    """Mints/verifies a receipt bound to (dim, candidate_hash, verifier_id, semantic_version, scope).
    verifier_state_hash (code+state) is folded into the key so a cloned/substituted verifier can't validate."""
    def __init__(self, verifier_id, state_hash):
        self.verifier_id = verifier_id
        self._k = hmac.new(b"root-secret-in-trusted-process", f"{verifier_id}|{state_hash}".encode(), hashlib.sha256).digest()
    def _tag(self, dim, ch, ver, scope):
        return hmac.new(self._k, f"{dim}|{ch}|{self.verifier_id}|{ver}|{scope}".encode(), hashlib.sha256).hexdigest()
    def mint(self, dim, ch, ver, scope): return self._tag(dim, ch, ver, scope)
    def verify(self, receipt, dim, ch, ver, scope):
        return isinstance(receipt, str) and bool(receipt) and hmac.compare_digest(receipt, self._tag(dim, ch, ver, scope))

# trusted verifiers (distinct ids + state hashes)
VX = BoundVerifier("verifier_X", "codehash_X_v1")
VE = BoundVerifier("verifier_E", "codehash_E_v1")
VP = BoundVerifier("verifier_P", "codehash_P_v1")

def gate_bound(ch, ver, scope, rx, re_, rp):
    if not (VX.verify(rx, "EXEC", ch, ver, scope)): return "NO", "EXECUTION_GATE_FAILED"
    if not (VE.verify(re_, "EPISTEMIC", ch, ver, scope)): return "NO", "EPISTEMIC_GATE_FAILED"
    if not (VP.verify(rp, "PERMISSION", ch, ver, scope)): return "NO", "PERMISSION_GATE_FAILED"
    return "YES", "GATES_SATISFIED"

def main():
    print("=== K0d — context-bound witness (E21-E27 witnessed) ===")
    ch, ver, scope = "H1", "v1", "campus"
    rx, re_, rp = VX.mint("EXEC", ch, ver, scope), VE.mint("EPISTEMIC", ch, ver, scope), VP.mint("PERMISSION", ch, ver, scope)

    def T(name, args, must):
        v, r = gate_bound(*args)
        ok = (v == must)
        print(f"  {name:38} -> {v}/{r:24} expect {must}  {'OK' if ok else 'FAIL'}")
        return ok

    results = []
    # liveness — exact context
    results.append(T("liveness (exact context)", (ch, ver, scope, rx, re_, rp), "YES"))
    # E21 scope replay: valid receipts for scope 'campus' used under scope 'monaco'
    results.append(T("E21 replay across SCOPE", (ch, ver, "monaco", rx, re_, rp), "NO"))
    # E22 version replay / downgrade
    results.append(T("E22 replay across VERSION", (ch, "v2", scope, rx, re_, rp), "NO"))
    # E25 verifier clone: a look-alike verifier with same id but different state_hash
    VP_clone = BoundVerifier("verifier_P", "codehash_P_TAMPERED")
    rp_clone = VP_clone.mint("PERMISSION", ch, ver, scope)
    results.append(T("E25/E26 verifier-state SUBSTITUTION", (ch, ver, scope, rx, re_, rp_clone), "NO"))
    # E27/type confusion: use the EPISTEMIC receipt in the permission slot
    results.append(T("type confusion (VW_E as VW_P)", (ch, ver, scope, rx, re_, re_), "NO"))
    # cross-candidate replay
    results.append(T("replay across CANDIDATE (H1->H2)", ("H2", ver, scope, rx, re_, rp), "NO"))

    allok = all(results)
    # R dimension honest probe
    print("\n  K0b/K0c (R): mint funcs are importable in-process -> OPEN (needs kernel-v2 process boundary)")
    print(f"\n  K0d (BINDING, B) = {'SURVIVED_DEFINED_ATTACK_SET' if allok else 'FALSIFIED'}  ({sum(results)}/{len(results)})")
    print("  Security = I ∧ B ∧ R  ·  I earned (k0_property_test) · B earned here · R open (V3 process boundary)")
    print("  authority=false · canon=false · ledger_effect=none")

if __name__ == "__main__":
    main()

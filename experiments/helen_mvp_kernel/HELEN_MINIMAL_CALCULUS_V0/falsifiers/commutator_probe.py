#!/usr/bin/env python3
"""
commutator_probe — admission + semantic commutator falsifiers against a REAL
kernel step function: BoundedExecutor.execute (helen_os/executor).

Implements the four-predicate diagnostic from T3's obligation map:
    a_r  = Adm(S, r)          a_q  = Adm(S, q)
    a_rq = Adm(F(S,r), q)     a_qr = Adm(F(S,q), r)
then, if all four hold:
    C = [canon(F(F(S,r),q)) == canon(F(F(S,q),r))]

Typed results (never a vague COMMUTATOR_FAIL):
    (a_* fail)        -> ADMISSION_INSTABILITY
    (all adm, C=0)    -> SEMANTIC_NONCOMMUTATION
    (all adm, C=1)    -> COMMUTE

Canonical state = sorted {relpath: sha256(content)} over base_dir — receipt
metadata (uuid, created_at) is EXCLUDED by construction and that exclusion is
itself an observation: the kernel's receipts are not byte-deterministic even
when its states are (see hidden_state_probe).

Each ordering runs in a FRESH executor + fresh base_dir (no registry
cross-contamination). NON_SOVEREIGN · tmp-dirs only · authority=false.
"""
import hashlib, json, pathlib, shutil, sys, tempfile

REPO = pathlib.Path(__file__).resolve().parents[3].parent
sys.path.insert(0, str(REPO))
from helen_os.executor.bounded_executor_v1 import BoundedExecutor  # real kernel step

def canon_state(base: pathlib.Path) -> str:
    m = {}
    for p in sorted(base.rglob("*")):
        if p.is_file():
            m[str(p.relative_to(base))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return json.dumps(m, sort_keys=True)

def apply(base: pathlib.Path, requests) -> tuple[bool, str]:
    """Fresh executor over base; returns (all_admitted, canonical_state)."""
    ex = BoundedExecutor(base_dir=base, policy_version="HMC_PROBE")
    ok = True
    for req in requests:
        decision, result, _ = ex.execute(dict(req))
        ok &= (decision.decision == "ALLOW" and result.status == "SUCCESS")
    return ok, canon_state(base)

def probe_pair(name, r, q):
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="hmc_comm_"))
    try:
        d_rq = tmp / "rq"; d_qr = tmp / "qr"; d_rq.mkdir(); d_qr.mkdir()
        ok_rq, s_rq = apply(d_rq, [r, q])
        ok_qr, s_qr = apply(d_qr, [q, r])
        if not (ok_rq and ok_qr):
            verdict = "ADMISSION_INSTABILITY"
        elif s_rq == s_qr:
            verdict = "COMMUTE"
        else:
            verdict = "SEMANTIC_NONCOMMUTATION"
        print(f"  {name:28} adm(r;q)={int(ok_rq)} adm(q;r)={int(ok_qr)} "
              f"state_eq={int(s_rq == s_qr)}  -> {verdict}")
        return name, verdict
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def W(target, content):
    return {"tool_type": "WRITE", "target": target, "payload": {"content": content}}

def main():
    print("commutator_probe — real kernel (BoundedExecutor), typed diagnostics")
    results = [
        # declared-independent pair: disjoint footprints -> expect COMMUTE
        probe_pair("disjoint_writes", W("a.txt", "alpha"), W("b.txt", "beta")),
        # dependent pair mislabeled independent: same target -> the second WRITE
        # is inadmissible after the first (bounds: target exists) -> expect
        # ADMISSION_INSTABILITY, i.e. the probe DETECTS the false independence
        probe_pair("same_target_writes", W("c.txt", "one"), W("c.txt", "two")),
        # disjoint nested paths -> expect COMMUTE
        probe_pair("nested_disjoint", W("d/x.txt", "dx"), W("e/y.txt", "ey")),
    ]
    expected = {"disjoint_writes": "COMMUTE",
                "same_target_writes": "ADMISSION_INSTABILITY",
                "nested_disjoint": "COMMUTE"}
    ok = all(v == expected[n] for n, v in results)
    print(f"expected_pattern_match = {ok}")
    print("NOTE: same_target ADMISSION_INSTABILITY is the probe WORKING — a false")
    print("      independence claim was operationally refuted, exactly r∥q ∧ ¬(r#q).")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())

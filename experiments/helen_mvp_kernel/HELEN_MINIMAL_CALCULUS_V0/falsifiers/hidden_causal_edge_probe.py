#!/usr/bin/env python3
"""
hidden_causal_edge_probe — O4 falsifier against the REAL kernel.

Attacks DECLARED independence (r ∥_P q) at REACHABLY-INDEPENDENT semantics:
the pair is tested at the state reached by replaying a compatible prefix,
exactly matching L4' (T3_StateIndexed.lean) — never only at S₀.

The declared poset lives in this experiment's fixtures (no kernel receipt
format is touched; the production causal-edge decision remains open).

Typed verdicts per declared-incomparable pair, at the reached state:
  COMMUTE                  declaration survives
  ADMISSION_INSTABILITY    r;q or q;r breaks — CAUSAL MISMATCH
  SEMANTIC_NONCOMMUTATION  both orders run, states differ — CAUSAL MISMATCH
  VACUOUS_AT_S0            untestable at S₀ (either op inadmissible there) —
                           demonstrates WHY independence must be state-indexed

On CAUSAL MISMATCH the probe PROPOSES MissingEdge(r,q) with the diagnosis
family {MissingEdge | HiddenState | AdmissionInstability | ReducerNoncommute |
BadIndependenceDeclaration}. It NEVER mutates any DAG or ledger:
    diagnostic ⊬ DAG mutation.

NON_SOVEREIGN · tmp-dirs only · authority=false · ledger_effect=none.
"""
import hashlib, json, pathlib, shutil, sys, tempfile

REPO = pathlib.Path(__file__).resolve().parents[3].parent
sys.path.insert(0, str(REPO))
from helen_os.executor.bounded_executor_v1 import BoundedExecutor, compute_file_hash

EMPTY = "sha256:" + "0" * 64

def W(t, c): return {"kind": "WRITE", "target": t, "content": c}
def E(t, c): return {"kind": "EDIT", "target": t, "content": c}
def A(t, q): return {"kind": "ANALYZE", "target": t, "query": q}

def apply_one(ex: BoundedExecutor, base: pathlib.Path, rcpt: dict) -> bool:
    req = {"tool_type": rcpt["kind"], "target": rcpt["target"]}
    if rcpt["kind"] == "ANALYZE":
        req["payload"] = {"query": rcpt["query"]}
    else:
        req["payload"] = {"content": rcpt["content"]}
    if rcpt["kind"] == "EDIT":
        p = base / rcpt["target"]
        req["pre_state_hash"] = compute_file_hash(p) if p.exists() else EMPTY
    d, r, _ = ex.execute(req)
    return d.decision == "ALLOW" and r.status == "SUCCESS"

def canon(base: pathlib.Path) -> str:
    m = {str(p.relative_to(base)): hashlib.sha256(p.read_bytes()).hexdigest()
         for p in sorted(base.rglob("*")) if p.is_file()}
    return json.dumps(m, sort_keys=True)

def run_seq(seq):
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="hmc_o4_"))
    try:
        ex = BoundedExecutor(base_dir=tmp, policy_version="O4_PROBE")
        bits = [apply_one(ex, tmp, rc) for rc in seq]
        return all(bits), bits, canon(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def probe(name, prefix, r, q, declared="incomparable"):
    # admissibility of each op alone at S0 (vacuity check)
    a_r0 = run_seq([r])[0]
    a_q0 = run_seq([q])[0]
    vacuous_s0 = not (a_r0 and a_q0)
    # state-indexed test: at the state reached by the compatible prefix
    ok_p, _, _ = run_seq(prefix)
    if not ok_p:
        return name, "FIXTURE_ERROR_PREFIX_INADMISSIBLE"
    ok_rq, bits_rq, s_rq = run_seq(prefix + [r, q])
    ok_qr, bits_qr, s_qr = run_seq(prefix + [q, r])
    if not (ok_rq and ok_qr):
        verdict = "ADMISSION_INSTABILITY"
    elif s_rq == s_qr:
        verdict = "COMMUTE"
    else:
        verdict = "SEMANTIC_NONCOMMUTATION"
    mismatch = declared == "incomparable" and verdict != "COMMUTE"
    tag = " 💥 CAUSAL_MISMATCH -> propose MissingEdge(r,q) [proposal only]" if mismatch else ""
    vtag = " [vacuous at S0 — state-indexed test was REQUIRED]" if vacuous_s0 else ""
    print(f"  {name:26} prefix={len(prefix)} adm(S0)=({int(a_r0)},{int(a_q0)}) "
          f"-> {verdict}{vtag}{tag}")
    return name, verdict

def main():
    print("hidden_causal_edge_probe — O4 vs real kernel · independence tested at REACHED states")
    results = dict([
        # (a) truly independent, declared ∥ — must survive
        probe("disjoint_declared_indep", [], W("a.txt", "A"), W("b.txt", "B")),
        # (b) FALSE declaration: WRITE f vs EDIT f declared ∥ — attack must catch it
        probe("write_edit_same_target", [], W("f.txt", "F"), E("f.txt", "F2")),
        # (c) read-only pair — must survive
        probe("two_analyze", [], A("a.txt", "q1"), A("b.txt", "q2")),
        # (d) MONEY FIXTURE: two EDITs of h.txt, declared ∥. Both inadmissible
        #     at S0 (vacuously 'independent' there); after prefix WRITE h.txt
        #     both admissible and NONCOMMUTING — only the state-indexed test
        #     refutes the declaration. This is L4' operationalized.
        probe("edits_after_prefix", [W("h.txt", "init")], E("h.txt", "X"), E("h.txt", "Y")),
        # (e) independence EARNED at reached state: EDIT f2 undefined at S0,
        #     defined and truly independent of WRITE g2 after prefix
        probe("earned_at_reached_state", [W("f2.txt", "base")], E("f2.txt", "v2"), W("g2.txt", "G")),
    ])
    expected = {"disjoint_declared_indep": "COMMUTE",
                "write_edit_same_target": "ADMISSION_INSTABILITY",
                "two_analyze": "COMMUTE",
                "edits_after_prefix": "SEMANTIC_NONCOMMUTATION",
                "earned_at_reached_state": "COMMUTE"}
    ok = all(results[k] == v for k, v in expected.items())
    print(f"expected_pattern_match = {ok}")
    print("NOTE: fixtures (b) and (d) are DELIBERATELY FALSE declarations; the 💥")
    print("      verdicts are the probe WORKING. (d) is undetectable at S0 —")
    print("      witnessing that independence is state-indexed, exactly L4'.")
    print("      All MissingEdge outputs are proposals; no DAG/ledger mutated.")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())

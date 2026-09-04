#!/usr/bin/env python3
"""
causal_receipt_witness — the C1..C10 WITNESS battery for CAUSAL_RECEIPT_V1.

Runs every gate; replay-bearing gates (C5, C6) use the REAL kernel
(BoundedExecutor). Emits one line per gate; exit 0 iff all witnessed.
Proof(T3) is upstream; this suite is Evidence(CR1 |= T3 assumptions).
NON_SOVEREIGN · tmp-dirs only · authority=false.
"""
import copy, hashlib, json, pathlib, shutil, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(HERE.parent / "causal_ledger"))
from helen_os.executor.bounded_executor_v1 import BoundedExecutor, compute_file_hash
from causal_receipt_v1 import CausalLedgerV1

NU = "sha256:eff29d80be0091c0/CR1"
EMPTY = "sha256:" + "0" * 64
RESULTS = []

def gate(cid, desc, ok):
    RESULTS.append(ok)
    print(f"  {cid:4} {desc:44} {'WITNESSED' if ok else 'FAILED'}")

def apply_op(ex, base, op) -> bool:
    req = {"tool_type": op["kind"], "target": op["target"]}
    req["payload"] = ({"query": op["query"]} if op["kind"] == "ANALYZE"
                      else {"content": op["content"]})
    if op["kind"] == "EDIT":
        p = base / op["target"]
        req["pre_state_hash"] = compute_file_hash(p) if p.exists() else EMPTY
    d, r, _ = ex.execute(req)
    return d.decision == "ALLOW" and r.status == "SUCCESS"

def replay_state(led: CausalLedgerV1, order) -> tuple[bool, str]:
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="hmc_cr1_"))
    try:
        ex = BoundedExecutor(base_dir=tmp, policy_version="CR1_WITNESS")
        body = lambda h: led.receipts[h]["body"]
        op = lambda h: body(h).get("op", body(h))
        ok = all(apply_op(ex, tmp, op(h)) for h in order)
        st = json.dumps({str(p.relative_to(tmp)): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in sorted(tmp.rglob("*")) if p.is_file()}, sort_keys=True)
        return ok, st
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def build_wellformed() -> CausalLedgerV1:
    L = CausalLedgerV1(NU)
    a = L.append({"kind": "WRITE", "target": "a.txt", "content": "A"}, [])
    b = L.append({"kind": "WRITE", "target": "b.txt", "content": "B"}, [])
    ea = L.append({"kind": "EDIT", "target": "a.txt", "content": "A2"}, [a])
    eb = L.append({"kind": "EDIT", "target": "b.txt", "content": "B2"}, [b])
    L.append({"kind": "ANALYZE", "target": "a.txt", "query": "q"}, [ea, eb])
    return L

def main():
    print("causal_receipt_witness — C1..C10 vs CAUSAL_RECEIPT_V1 + real kernel")
    L = build_wellformed()

    # C1 parent existence
    try:
        L.append({"kind": "WRITE", "target": "z.txt", "content": "Z"}, ["f" * 64])
        c1 = False
    except ValueError as e:
        c1 = "E_PARENT_UNKNOWN" in str(e)
    gate("C1", "parent existence enforced", c1 and L.verify()[0])

    # C2 acyclicity: append-path by construction; import rejects cycle claims
    fake_h1, fake_h2 = "1" * 64, "2" * 64
    cyc = (json.dumps({"body": {"x": 1}, "parents": [fake_h2], "h": fake_h1}) + "\n"
           + json.dumps({"body": {"x": 2}, "parents": [fake_h1], "h": fake_h2}) + "\n").encode()
    try:
        CausalLedgerV1.import_(NU, cyc); c2 = False
    except ValueError as e:
        c2 = "E_UNRESOLVABLE" in str(e)
    gate("C2", "cycle claim rejected on import", c2)

    # C3 hash determinism (same nu/body/parents => same hash; nu-bound)
    M1, M2 = build_wellformed(), build_wellformed()
    c3a = sorted(M1.receipts) == sorted(M2.receipts)
    c3b = sorted(CausalLedgerV1("OTHER_NU").receipts) != sorted(M1.receipts) or True
    other = CausalLedgerV1("OTHER_NU"); other.append({"kind": "WRITE", "target": "a.txt", "content": "A"}, [])
    first_body = {"kind": "WRITE", "target": "a.txt", "content": "A"}
    c3b = other._hash(first_body, []) != M1._hash(first_body, [])
    gate("C3", "hash deterministic + nu-bound", c3a and c3b)

    # C4 parent-order invariance
    P = CausalLedgerV1(NU)
    p1 = P.append({"n": 1}, []); p2 = P.append({"n": 2}, [])
    c4 = P._hash({"n": 3}, [p1, p2]) == P._hash({"n": 3}, [p2, p1])
    gate("C4", "parent order invariance (unordered set)", c4)

    # C5 serialization invariance (semantic replay over sampled LinExt)
    outcomes = {replay_state(L, o) for o in map(tuple, L.linearizations(8, 0))}
    gate("C5", "semantic replay equal across 8 LinExt", len(outcomes) == 1)

    # C6 negative control: removed dependency exposes divergence
    B = CausalLedgerV1(NU)
    w = B.append({"kind": "WRITE", "target": "h.txt", "content": "init"}, [])
    B.append({"kind": "EDIT", "target": "h.txt", "content": "X"}, [w])
    B.append({"kind": "EDIT", "target": "h.txt", "content": "Y"}, [w])
    before = copy.deepcopy(B.receipts)
    div = {replay_state(B, o) for o in map(tuple, B.linearizations(8, 1))}
    gate("C6", "missing-edge divergence exposed", len(div) > 1)

    # C7 no auto-repair: detection did not mutate the DAG
    gate("C7", "detected divergence => DAG unmodified", B.receipts == before)

    # C8 roundtrip + three-identity split
    exp1 = L.export()
    shuffled = list(L.receipts); import random; random.Random(7).shuffle(shuffled)
    # export must remain topologically importable: use a sampled linearization
    exp2 = L.export(order=L.linearizations(1, 7)[0])
    R1 = CausalLedgerV1.import_(NU, exp1)
    R2 = CausalLedgerV1.import_(NU, exp2)
    hb_diff = CausalLedgerV1.h_bytes(exp1) != CausalLedgerV1.h_bytes(exp2)
    hc_same = R1.h_causal() == R2.h_causal() == L.h_causal()
    hs_same = (replay_state(R1, R1.linearizations(1, 3)[0])
               == replay_state(R2, R2.linearizations(1, 4)[0]))
    gate("C8", "roundtrip: Hbytes≠ · Hcausal= · Hsemantic=", hb_diff and hc_same and hs_same and R1.verify()[0])

    # C9 migration with explicit provenance (legacy order => causal chain)
    legacy = [{"kind": "WRITE", "target": "m.txt", "content": "v1"},
              {"kind": "EDIT", "target": "m.txt", "content": "v2"},
              {"kind": "WRITE", "target": "n.txt", "content": "N"}]
    legacy_bytes = json.dumps(legacy, sort_keys=True)
    Mig = CausalLedgerV1.migrate_from_linear(NU, legacy)
    chain_ok = all(len(r["parents"]) <= 1 for r in Mig.receipts.values())
    prov_ok = all(r["body"]["migration"]["source"] == "linear_v0" for r in Mig.receipts.values())
    ok_replay, _ = replay_state(Mig, Mig.linearizations(1, 0)[0])
    gate("C9", "linear->V1 migration, chain + provenance", Mig.verify()[0] and chain_ok and prov_ok and ok_replay)

    # C10 rollback: legacy representation untouched; dropping V1 loses nothing
    gate("C10", "rollback: legacy bytes intact, V1 additive", json.dumps(legacy, sort_keys=True) == legacy_bytes)

    ok = all(RESULTS)
    print(f"WITNESS = {'PASS 10/10' if ok else 'FAIL'}")
    print("CLAIM: Evidence(CR1 |= T3 assumptions) on these fixtures — NOT 'T3 proved CR1'.")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())

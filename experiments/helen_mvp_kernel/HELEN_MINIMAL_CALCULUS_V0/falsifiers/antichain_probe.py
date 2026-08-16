#!/usr/bin/env python3
"""
antichain_probe — E3 at ledger scale, unblocked by the causal-parents ruling.

Takes a CAUSAL_RECEIPT_V0 DAG whose ops are REAL kernel operations
(BoundedExecutor), samples seeded linear extensions, replays each in a fresh
environment, and compares canonical states.

  All linearizations equal   -> CONFLUENT  (T3 witnessed on a causal ledger)
  Divergence                 -> 💥 HIDDEN EDGE — some pair declared
                                incomparable is not strongly independent at
                                a reached state; propose MissingEdge
                                candidates (proposal only, no DAG mutation)

Two fixtures:
  WELL_FORMED : parents declared correctly  -> expect CONFLUENT
  BROKEN      : the true dependency between two EDITs of the same file is
                deliberately omitted        -> expect divergence + proposal

NON_SOVEREIGN · tmp-dirs only · seeded RNG · authority=false.
"""
import hashlib, json, pathlib, shutil, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(HERE.parent / "causal_ledger"))
from helen_os.executor.bounded_executor_v1 import BoundedExecutor, compute_file_hash
from causal_receipt_v0 import CausalLedger

EMPTY = "sha256:" + "0" * 64

def apply_op(ex, base, op) -> bool:
    req = {"tool_type": op["kind"], "target": op["target"]}
    req["payload"] = ({"query": op["query"]} if op["kind"] == "ANALYZE"
                      else {"content": op["content"]})
    if op["kind"] == "EDIT":
        p = base / op["target"]
        req["pre_state_hash"] = compute_file_hash(p) if p.exists() else EMPTY
    d, r, _ = ex.execute(req)
    return d.decision == "ALLOW" and r.status == "SUCCESS"

def replay(ledger: CausalLedger, order) -> tuple[bool, str]:
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="hmc_antichain_"))
    try:
        ex = BoundedExecutor(base_dir=tmp, policy_version="ANTICHAIN_PROBE")
        ok = all(apply_op(ex, tmp, ledger.receipts[h]["op"]) for h in order)
        state = json.dumps(
            {str(p.relative_to(tmp)): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted(tmp.rglob("*")) if p.is_file()}, sort_keys=True)
        return ok, state
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def check(name: str, ledger: CausalLedger, samples=8, seed=0):
    assert ledger.verify(), "hash chain broken"
    orders = ledger.linearizations(samples, seed)
    uniq = {}
    for o in orders:
        ok, s = replay(ledger, o)
        uniq.setdefault((ok, s), []).append(o)
    if len(uniq) == 1:
        print(f"  {name:12} linearizations={len(orders)} distinct_outcomes=1 -> CONFLUENT")
        return name, "CONFLUENT"
    # divergence: propose missing edges among incomparable pairs on same target
    proposals = [
        (a, b) for a, b in ledger.incomparable_pairs()
        if ledger.receipts[a]["op"]["target"] == ledger.receipts[b]["op"]["target"]
        and not (ledger.receipts[a]["op"]["kind"] == "ANALYZE"
                 and ledger.receipts[b]["op"]["kind"] == "ANALYZE")
    ]
    print(f"  {name:12} linearizations={len(orders)} distinct_outcomes={len(uniq)} "
          f"-> 💥 HIDDEN EDGE detected")
    for a, b in proposals:
        print(f"     propose MissingEdge({a},{b}) "
              f"[{ledger.receipts[a]['op']['kind']}/{ledger.receipts[b]['op']['kind']} "
              f"on {ledger.receipts[a]['op']['target']}] — proposal only")
    return name, "HIDDEN_EDGE"

def main():
    print("antichain_probe — causal-parents ledger vs real kernel (seeded, fresh envs)")
    # WELL_FORMED: true dependencies declared
    L1 = CausalLedger()
    a = L1.append({"kind": "WRITE", "target": "a.txt", "content": "A"}, [])
    b = L1.append({"kind": "WRITE", "target": "b.txt", "content": "B"}, [])
    ea = L1.append({"kind": "EDIT", "target": "a.txt", "content": "A2"}, [a])
    eb = L1.append({"kind": "EDIT", "target": "b.txt", "content": "B2"}, [b])
    L1.append({"kind": "ANALYZE", "target": "a.txt", "query": "q"}, [ea, eb])
    r1 = check("WELL_FORMED", L1)

    # BROKEN: two EDITs of h.txt both declare only the WRITE as parent —
    # their true mutual dependency is omitted from the DAG
    L2 = CausalLedger()
    w = L2.append({"kind": "WRITE", "target": "h.txt", "content": "init"}, [])
    L2.append({"kind": "EDIT", "target": "h.txt", "content": "X"}, [w])
    L2.append({"kind": "EDIT", "target": "h.txt", "content": "Y"}, [w])
    r2 = check("BROKEN", L2)

    ok = (r1[1] == "CONFLUENT" and r2[1] == "HIDDEN_EDGE")
    print(f"expected_pattern_match = {ok}")
    print("NOTE: BROKEN's divergence is the probe WORKING — the declared DAG")
    print("      claimed an antichain the kernel semantics refute. Detection")
    print("      is only possible BECAUSE parents are declared: the ruling")
    print("      (b) is what makes E3 executable at ledger scale.")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())

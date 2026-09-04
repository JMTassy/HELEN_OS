#!/usr/bin/env python3
"""
hidden_state_probe — determinism falsifier for the real kernel step.
Obligation under test: F_nu is functional — same explicit inputs, same state.
Method: replay the identical request sequence in fresh environments and
compare canonical STATES; separately compare RECEIPTS to expose which parts
of the kernel's outputs are and are not deterministic.

NON_SOVEREIGN · tmp-dirs only · authority=false.
"""
import hashlib, json, pathlib, shutil, sys, tempfile

REPO = pathlib.Path(__file__).resolve().parents[3].parent
sys.path.insert(0, str(REPO))
from helen_os.executor.bounded_executor_v1 import BoundedExecutor

SEQ = [
    {"tool_type": "WRITE", "target": "s/a.txt", "payload": {"content": "A1"}},
    {"tool_type": "WRITE", "target": "s/b.txt", "payload": {"content": "B1"}},
    {"tool_type": "ANALYZE", "target": "s/a.txt", "payload": {"query": "q"}},
]

def canon_state(base: pathlib.Path) -> str:
    m = {str(p.relative_to(base)): hashlib.sha256(p.read_bytes()).hexdigest()
         for p in sorted(base.rglob("*")) if p.is_file()}
    return json.dumps(m, sort_keys=True)

def run_once():
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="hmc_hidden_"))
    try:
        ex = BoundedExecutor(base_dir=tmp, policy_version="HMC_PROBE")
        receipts = []
        for req in SEQ:
            d, r, a = ex.execute(dict(req))
            receipts.append((d.__dict__, r.__dict__))
        return canon_state(tmp), receipts
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def main():
    s1, rc1 = run_once()
    s2, rc2 = run_once()
    state_det = (s1 == s2)
    receipt_det = (json.dumps(rc1, default=str, sort_keys=True)
                   == json.dumps(rc2, default=str, sort_keys=True))
    # Witnessed ND surface (2026-08-16 run): uuid identities, their
    # cross-references, and timestamps. Everything else must be deterministic.
    ND_FIELDS = {"decision_id", "execution_id", "created_at", "artifact_id",
                 "decision_id_ref", "execution_id_ref", "artifact_refs"}
    stripped = [json.dumps([{k: v for k, v in part.items() if k not in ND_FIELDS}
                            for pair in run for part in pair],
                           default=str, sort_keys=True)
                for run in (rc1, rc2)]
    receipt_det_modulo = (stripped[0] == stripped[1])
    print("hidden_state_probe — repeated replay, fresh environments")
    print(f"  STATE_DETERMINISTIC            = {state_det}")
    print(f"  RECEIPT_BYTE_DETERMINISTIC     = {receipt_det}")
    print(f"  RECEIPT_DET_MODULO_ND_FIELDS   = {receipt_det_modulo}  (excl: {sorted(ND_FIELDS)})")
    if state_det and not receipt_det:
        print("  OBSERVATION: states are deterministic; receipt metadata (uuid,")
        print("  timestamp) is not. The nu-versioned canonicalization used by any")
        print("  replay/commutator claim MUST therefore exclude these fields, or")
        print("  the F-determinism obligation weakens from receipts to states.")
    return 0 if state_det else 1

if __name__ == "__main__":
    sys.exit(main())

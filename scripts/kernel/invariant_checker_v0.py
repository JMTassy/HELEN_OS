"""
invariant_checker_v0.py — I(), the kernel-invariant checker for HELEN.

The HAL verdict on the Recursive Self-Building upgrade said: "accept iff I(H_{t+1})=1,
but I() does not exist." This is I() v0. It is the gate every candidate change must
pass before the recursive builder loop may INTEGRATE it. No checker -> no recursion.

I() is deterministic (no LLM, no network). It takes a CANDIDATE change descriptor and
returns ok=True iff ALL 7 kernel invariants hold, plus a per-invariant breakdown.

It does NOT activate recursion, propose, or admit anything. It only judges admissibility.
authority=false, claim=NO_CLAIM. Reducer/human decide; I() only reports.

Candidate descriptor (all fields optional; absence is treated conservatively):
{
  "id": str,
  "authority": false,                                  # must be present AND false
  "owner": "reducer",                                  # exactly one
  "proposer": "builder", "validator": "hal",           # must differ
  "ledger_ops": [{"op": "append", ...}],               # append-only
  "memory_mutations": [{"key": ..., "receipt": "..."}], # each receipted
  "projections": [{"name": ..., "read_only": true}],    # downstream/read-only
  "cold_restore": {"repo","branch","commit","ledger_checksum"},  # complete anchor
  "tool_calls": [{"name": ..., "gate": "approved", "perm": "READ"}]  # gated, non-sovereign
}
"""
from __future__ import annotations
import hashlib, json
from typing import Any, Dict, Tuple

_DESTRUCTIVE = {"delete", "overwrite", "rewrite", "edit", "truncate", "amend", "mutate"}


def _append_only_ledger(c) -> Tuple[bool, str]:
    for op in c.get("ledger_ops", []):
        kind = str(op.get("op", "")).lower()
        if kind in _DESTRUCTIVE:
            return False, f"ledger op '{kind}' is not append-only"
    return True, "ledger ops append-only"


def _authority_explicit(c) -> Tuple[bool, str]:
    if "authority" not in c:
        return False, "authority not declared (must be explicit)"
    if c["authority"] is not False:
        return False, f"authority must be false for a candidate change, got {c['authority']!r}"
    return True, "authority explicitly false"


def _single_owner(c) -> Tuple[bool, str]:
    owner = c.get("owner")
    if not owner or not isinstance(owner, str):
        return False, "no single owner declared"
    p, v = c.get("proposer"), c.get("validator")
    if p and v and p == v:
        return False, f"proposer == validator ({p}) — separation violated"
    return True, "single owner; proposer != validator"


def _no_silent_memory_mutation(c) -> Tuple[bool, str]:
    for m in c.get("memory_mutations", []):
        if not m.get("receipt"):
            return False, f"memory mutation on {m.get('key','?')!r} has no receipt (silent)"
    return True, "all memory mutations receipted"


def _projection_downstream(c) -> Tuple[bool, str]:
    for p in c.get("projections", []):
        if p.get("read_only") is not True:
            return False, f"projection {p.get('name','?')!r} is not read-only (writes upstream)"
    return True, "projections read-only / downstream"


def _cold_restore_valid(c) -> Tuple[bool, str]:
    cr = c.get("cold_restore") or {}
    need = ("repo", "branch", "commit", "ledger_checksum")
    missing = [k for k in need if not cr.get(k)]
    if missing:
        return False, f"cold-restore anchor missing: {missing}"
    return True, "cold-restore anchor complete"


def _bounded_tool_execution(c) -> Tuple[bool, str]:
    for t in c.get("tool_calls", []):
        if str(t.get("perm", "")).upper() == "WRITE_SOVEREIGN":
            return False, f"tool {t.get('name','?')!r} requests WRITE_SOVEREIGN (forbidden)"
        if str(t.get("gate", "")).lower() not in ("approved", "pending"):
            return False, f"tool {t.get('name','?')!r} is ungated"
    return True, "tool calls gated and non-sovereign"


INVARIANTS = {
    "append_only_ledger":        _append_only_ledger,
    "authority_explicit":        _authority_explicit,
    "single_owner_governance":   _single_owner,
    "no_silent_memory_mutation": _no_silent_memory_mutation,
    "projection_downstream":     _projection_downstream,
    "cold_restore_valid":        _cold_restore_valid,
    "bounded_tool_execution":    _bounded_tool_execution,
}


def check(candidate: Dict[str, Any]) -> Dict[str, Any]:
    """I(candidate) -> report. ok=True (I=1) iff all 7 invariants hold."""
    results, failed = {}, []
    for name, fn in INVARIANTS.items():
        ok, reason = fn(candidate)
        results[name] = {"pass": ok, "reason": reason}
        if not ok:
            failed.append(name)
    ok_all = not failed
    blob = json.dumps(candidate, sort_keys=True, default=str)
    return {
        "schema": "KERNEL_INVARIANT_CHECK_V0",
        "checker": "I()",
        "authority": False,
        "claim": "NO_CLAIM",
        "candidate_id": candidate.get("id", "<unnamed>"),
        "candidate_sha256": "sha256:" + hashlib.sha256(blob.encode()).hexdigest()[:16],
        "I": 1 if ok_all else 0,
        "ok": ok_all,
        "failed_invariants": failed,
        "invariants": results,
        "note": "I() reports admissibility only. Reducer/human decide; ledger remembers.",
    }


if __name__ == "__main__":
    import sys
    cand = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else {}
    rep = check(cand)
    print(json.dumps(rep, indent=2))
    sys.exit(0 if rep["ok"] else 1)

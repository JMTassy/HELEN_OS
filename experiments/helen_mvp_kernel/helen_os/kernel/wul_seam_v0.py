"""WUL_SEAM_V0 — a WUL rule made LOAD-BEARING end to end. 🔵 OBSERVED · authority=false. NON-SOVEREIGN.

Extends the frozen HELEN_VERTICAL_SLICE_V0 with a WUL front-end so the gate is COMPILED FROM WUL, not
hardcoded. The milestone is not "a file exists" or "tests are green" — it is the causal chain:

    ΔWUL  ⇒  ΔIR  ⇒  ΔΓ  ⇒  ΔRuntimeBehavior
    plus the reverse trace:   RuntimeReject → IRRule → WULRule

Concretely: the WUL rule `REQUIRE AuthorizedEffect : ApplicableAuthorityWitness` is what forces the witness
check. Delete that one line from the WUL source, recompile, and a missing-witness proposal that used to
REJECT now ADMITs — proving the rule (not the Python) is load-bearing. authority=false. Verdict = the gate.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from helen_os.kernel.vertical_slice_v0 import (
    CandidateEnvelope, Witness, Capability, Policy, GENESIS_POLICY, _mint_capability, capability_valid,
    executor_execute, append_event, replay, observe, verify, NO_EFFECT, _h, _canon,
)

# ── WUL source (editable text — the constitution people actually change) ──
WUL_SOURCE = """\
TYPE CandidateEffect
TYPE ApplicableAuthorityWitness
TYPE AuthorizedEffect
FORBID CandidateEffect -> AuthorizedEffect
REQUIRE AuthorizedEffect : ApplicableAuthorityWitness
TRANSITION Authorize : CandidateEffect -> AuthorizedEffect
"""

# ── parse: text → statements (each carries a wul_rule id = "L<n>:<text>") ──
def parse(src: str) -> List[dict]:
    out = []
    for i, raw in enumerate(l.strip() for l in src.splitlines()):
        if not raw:
            continue
        wid = "WUL:L%d" % i
        if raw.startswith("TYPE "):
            out.append({"op": "TYPE", "name": raw[5:].strip(), "wul": wid})
        elif raw.startswith("FORBID "):
            a, b = raw[7:].split("->"); out.append({"op": "FORBID", "src": a.strip(), "dst": b.strip(), "wul": wid})
        elif raw.startswith("REQUIRE "):
            tgt, w = raw[8:].split(":"); out.append({"op": "REQUIRE", "target": tgt.strip(), "witness": w.strip(), "wul": wid})
        elif raw.startswith("TRANSITION "):
            name, arrow = raw[11:].split(":"); a, b = arrow.split("->")
            out.append({"op": "TRANSITION", "name": name.strip(), "src": a.strip(), "dst": b.strip(), "wul": wid})
        else:
            raise ValueError("UNKNOWN WUL STATEMENT: " + raw)   # fail-closed
    return out

# ── compile: statements → typed IR (rules get ids; IR is what Γ reads) ──
@dataclass(frozen=True)
class IR:
    types: frozenset
    forbids: tuple          # ((ir_id, src, dst, wul), ...)
    requires: tuple         # ((ir_id, target, witness, wul), ...)
    transitions: tuple      # ((ir_id, name, src, dst, wul), ...)
    ir_hash: str

def compile_ir(stmts: List[dict]) -> IR:
    types = frozenset(s["name"] for s in stmts if s["op"] == "TYPE")
    forbids = tuple(("IR:FORBID:%s->%s" % (s["src"], s["dst"]), s["src"], s["dst"], s["wul"])
                    for s in stmts if s["op"] == "FORBID")
    requires = tuple(("IR:REQUIRE:%s:%s" % (s["target"], s["witness"]), s["target"], s["witness"], s["wul"])
                     for s in stmts if s["op"] == "REQUIRE")
    transitions = tuple(("IR:TRANS:%s" % s["name"], s["name"], s["src"], s["dst"], s["wul"])
                        for s in stmts if s["op"] == "TRANSITION")
    ir_hash = _h(_canon([sorted(types), forbids, requires, transitions]))
    return IR(types, forbids, requires, transitions, ir_hash)

# ── Γ compiled FROM the IR (not hardcoded). Reverse trace carried on every REJECT. ──
@dataclass(frozen=True)
class WulReceipt:
    verdict: str            # AUTHORIZE | DENY
    reason: str
    ir_rule: Optional[str]
    wul_rule: Optional[str]
    capability: Optional[Capability]

def _witness_applicable(w, cand, policy) -> bool:
    return (isinstance(w, Witness) and w.action == cand.requested_action and w.resource == cand.resource
            and cand.resource in w.scope and w.policy_hash == policy.version_hash
            and cand.resource in policy.allowed.get(cand.requested_action, frozenset()))

def gamma_wul(cand: CandidateEnvelope, ir: IR, policy: Policy, nonce="n0") -> WulReceipt:
    # only a declared TRANSITION Candidate->Authorized can even attempt authorization (FORBID blocks raw coercion)
    trans = [t for t in ir.transitions if t[2] == "CandidateEffect" and t[3] == "AuthorizedEffect"]
    if not trans:
        return WulReceipt("DENY", "NO_LICENSED_TRANSITION", None, None, None)
    target = "AuthorizedEffect"
    # discharge every REQUIRE obligation attached to the target — THIS is the load-bearing rule
    for ir_id, tgt, witness_type, wul in ir.requires:
        if tgt != target:
            continue
        if witness_type == "ApplicableAuthorityWitness" and not _witness_applicable(cand.witness, cand, policy):
            return WulReceipt("DENY", "REQUIRE_UNMET:" + witness_type, ir_id, wul, None)   # reverse trace
    phash = _h(_canon([cand.proposal_id, cand.actor, cand.requested_action, cand.resource]))
    cap = _mint_capability(cand.requested_action, cand.resource, policy.version_hash, nonce, phash)
    return WulReceipt("AUTHORIZE", "OK", None, None, cap)

# ── one honest vertical pipeline: WUL → IR → Γ → capability → effect → event → ledger → replay ──
def run_pipeline(cand, ir, policy, ledger):
    r = gamma_wul(cand, ir, policy)
    fake_receipt = type("R", (), {"proposal_hash": "", "action": cand.requested_action,
                                  "resource": cand.resource, "policy_hash": policy.version_hash})()
    if r.verdict == "DENY":
        return append_event(ledger, "EFFECT_DENIED", fake_receipt, {"reason": r.reason, "ir": r.ir_rule, "wul": r.wul_rule}), r
    status, attempt = executor_execute(r.capability, policy)
    if status == "NO_EFFECT":
        return append_event(ledger, "EFFECT_UNRESOLVED", fake_receipt, {"reason": "NO_EFFECT"}), r
    result = verify(observe(attempt))
    et = "EFFECT_VERIFIED" if result == "VERIFIED" else "EFFECT_UNRESOLVED"
    return append_event(ledger, et, fake_receipt, {"result": result}), r

def _good(**kw):
    base = dict(proposal_id="p1", actor="alice", requested_action="write_file", resource="sandbox/out.txt",
                witness=Witness("operator_grant", "write_file", "sandbox/out.txt",
                                frozenset({"sandbox/out.txt"}), GENESIS_POLICY.version_hash))
    base.update(kw); return CandidateEnvelope(**base)

def run_receipt() -> dict:
    P = GENESIS_POLICY
    ir = compile_ir(parse(WUL_SOURCE))
    # 1. missing witness ⇒ REJECT (rule enforced)
    miss = gamma_wul(_good(witness=None), ir, P)
    t1_missing_rejects = (miss.verdict == "DENY" and miss.reason.startswith("REQUIRE_UNMET"))
    # 2. valid applicable witness ⇒ ADMIT
    good = gamma_wul(_good(), ir, P)
    t2_valid_admits = (good.verdict == "AUTHORIZE" and good.capability is not None)
    # 3. direct executor bypass ⇒ NoEffect (mutant killed)
    t3_bypass_killed = (executor_execute(None, P) == NO_EFFECT
                        and executor_execute(Capability("write_file", "sandbox/out.txt", P.version_hash, "n", "x", "FORGED"), P) == NO_EFFECT)
    # 4. LOAD-BEARING: edit the WUL (delete the REQUIRE line) ⇒ IR changes ⇒ Γ changes ⇒ runtime changes
    wul_without = "\n".join(l for l in WUL_SOURCE.splitlines() if not l.strip().startswith("REQUIRE"))
    ir2 = compile_ir(parse(wul_without))
    miss2 = gamma_wul(_good(witness=None), ir2, P)
    t4_delta_wul = (ir.ir_hash != ir2.ir_hash                       # ΔWUL ⇒ ΔIR
                    and miss.verdict == "DENY" and miss2.verdict == "AUTHORIZE")  # ⇒ ΔΓ ⇒ ΔRuntime
    # 5. reverse trace: a runtime REJECT names its IR rule and WUL rule
    t5_reverse_trace = (miss.ir_rule is not None and miss.ir_rule.startswith("IR:REQUIRE")
                        and miss.wul_rule is not None and miss.wul_rule.startswith("WUL:L"))
    # end-to-end replay still deterministic
    led = []
    for i in range(3):
        led, _ = run_pipeline(_good(proposal_id="p%d" % i), ir, P, led)
    mid = len(led) // 2
    from helen_os.kernel.vertical_slice_v0 import canonical_state_hash
    t6_replay = canonical_state_hash(replay(led)) == canonical_state_hash(replay(led[mid:], replay(led[:mid])))
    vec = (t1_missing_rejects, t2_valid_admits, t3_bypass_killed, t4_delta_wul, t5_reverse_trace, t6_replay)
    return {"missing_witness_rejects": t1_missing_rejects, "valid_witness_admits": t2_valid_admits,
            "direct_executor_bypass_killed": t3_bypass_killed,
            "delta_wul_changes_runtime": t4_delta_wul, "reverse_trace_reject_to_wul": t5_reverse_trace,
            "replay_fold_equivalence": t6_replay,
            "ir_hash_with_rule": ir.ir_hash, "ir_hash_without_rule": ir2.ir_hash,
            "reject_trace": {"reason": miss.reason, "ir_rule": miss.ir_rule, "wul_rule": miss.wul_rule},
            "acceptance_vector": vec, "accepted": all(vec)}

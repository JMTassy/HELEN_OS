"""FABLE_BINARY_GATE_V0 — credit-minimal constitutional gate. authority=false · canon=false · ledger_effect=none.
NON-SOVEREIGN. Role split of FABLE_LEAN: HER supervises cognition, Qwen goblins propose (cheap/local), HAL falsifies,
FABLE = YES/NO ONLY at decision boundaries. FABLE is an INTERRUPT, not a worker: FABLE_Calls ≈ #DecisionBoundaries,
not #AgentSteps.

Credit win: the gate is DETERMINISTIC over a compressed GATE_PACKET (~300 tok) → ZERO premium tokens for the
mechanical checks. A premium (Claude) FABLE judgment is invoked ONLY when the deterministic gate returns ESCALATE
(a genuine constitutional ambiguity the typed fields can't resolve).

Invariants preserved:
  RawCognition ↛ FABLE (only a ValidatedDecisionPacket reaches it)   ·   FABLE:YES ≠ StateChange (licenses the
  Candidate→Admission→Receipt→Reducer→State path; the kernel performs it)   ·   the gate does NOT trust the packet's
  own RECOMMENDED_VERDICT (proposer self-recommendation, untrusted — re-derive from typed fields).
"""
from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class GatePacket:
    question: str = ""
    task_hash: str = ""
    corpus_hash: str = ""
    her_status: str = ""              # supervisor status
    goblin_complete: bool = False     # SWARM_OUTPUT_COMPLETE
    hal_status: str = ""              # SURVIVED | REFUTED | INCONCLUSIVE
    best_candidate: str = ""
    evidence_roots: int = 0           # independent provenance roots (N_E)
    falsifier_result: str = ""        # SURVIVED | REFUTED | INCONCLUSIVE
    authority_delta: int = 0          # Δ authority requested
    state_delta: int = 0              # any direct state mutation attempt by cognition
    scope_delta: int = 0
    hard_gates: list = field(default_factory=list)   # list[bool]
    unknown_unresolved: bool = False
    operator_witness: bool = False    # verified operator grant present (for legitimate expansion)
    recommended_verdict: str = ""     # UNTRUSTED proposer self-recommendation — the gate IGNORES this

    def complete(self) -> bool:
        return bool(self.task_hash and self.corpus_hash and self.hal_status and isinstance(self.hard_gates, list))

# reason codes
YES, NO, ESCALATE = "YES", "NO", "ESCALATE"

def fable_gate(p: GatePacket):
    """Deterministic constitutional gate. Returns (YES|NO|ESCALATE, reason_code). NEVER mutates state.
    Re-derives from typed fields; ignores p.recommended_verdict."""
    if not p.complete():
        return NO, "MALFORMED_PACKET"
    if not p.goblin_complete:
        return NO, "SWARM_INCOMPLETE"                    # NOT_EVALUABLE ≠ 0
    if p.state_delta != 0:
        return NO, "STATE_MUTATION_ATTEMPT"              # Cognition ↛ GovernedState
    if p.authority_delta != 0 and not p.operator_witness:
        return NO, "AUTHORITY_EXPANSION"                 # Δ⁺Γ needs operator witness
    if p.scope_delta != 0 and not p.operator_witness:
        return NO, "SCOPE_MUTATION"
    if any(g is False for g in p.hard_gates):
        return NO, "HARD_GATE_FAILURE"
    if str(p.falsifier_result).upper() == "REFUTED" or str(p.hal_status).upper() == "REFUTED":
        return NO, "REFUTED"
    if str(p.hal_status).upper() == "INCONCLUSIVE" or p.unknown_unresolved:
        return NO, "INCONCLUSIVE"                        # Unknown ⇒ NO (fail-closed)
    if p.evidence_roots < 1:
        return NO, "MISSING_WITNESS"
    if str(p.hal_status).upper() == "SURVIVED" and p.evidence_roots >= 1:
        return YES, "GATES_SATISFIED"
    return ESCALATE, "AMBIGUOUS_REQUIRES_PREMIUM_JUDGMENT"   # only HERE does a premium FABLE call happen

def should_call_fable(*, final_promotion=False, authority_delta=False, scope_delta=False,
                      budget_escalation=False, unresolved_conflict=False) -> bool:
    """FABLE_CALL policy. HER+GOBLINS+HAL continue WITHOUT FABLE unless a decision boundary is reached."""
    return bool(final_promotion or authority_delta or scope_delta or budget_escalation or unresolved_conflict)

def run_receipt() -> dict:
    R = {}
    # YES: complete, HAL survived, roots present, no deltas, gates pass
    ok = GatePacket(task_hash="t", corpus_hash="c", her_status="ok", goblin_complete=True, hal_status="SURVIVED",
                    evidence_roots=2, falsifier_result="SURVIVED", hard_gates=[True, True], recommended_verdict="NO")
    R["yes"] = fable_gate(ok)                              # must be YES despite recommended_verdict=NO (ignored)
    # NO cases
    R["swarm_incomplete"] = fable_gate(GatePacket(task_hash="t", corpus_hash="c", hal_status="SURVIVED", goblin_complete=False, hard_gates=[]))
    R["state_mutation"]   = fable_gate(GatePacket(task_hash="t", corpus_hash="c", hal_status="SURVIVED", goblin_complete=True, state_delta=1, evidence_roots=1, hard_gates=[True]))
    R["authority_grab"]   = fable_gate(GatePacket(task_hash="t", corpus_hash="c", hal_status="SURVIVED", goblin_complete=True, authority_delta=1, evidence_roots=1, hard_gates=[True]))
    R["refuted"]          = fable_gate(GatePacket(task_hash="t", corpus_hash="c", hal_status="REFUTED", goblin_complete=True, evidence_roots=1, hard_gates=[True]))
    R["inconclusive"]     = fable_gate(GatePacket(task_hash="t", corpus_hash="c", hal_status="INCONCLUSIVE", goblin_complete=True, evidence_roots=1, hard_gates=[True]))
    R["missing_witness"]  = fable_gate(GatePacket(task_hash="t", corpus_hash="c", hal_status="SURVIVED", goblin_complete=True, evidence_roots=0, hard_gates=[True]))
    R["hard_gate_fail"]   = fable_gate(GatePacket(task_hash="t", corpus_hash="c", hal_status="SURVIVED", goblin_complete=True, evidence_roots=1, hard_gates=[True, False]))
    R["legit_expansion"]  = fable_gate(GatePacket(task_hash="t", corpus_hash="c", hal_status="SURVIVED", goblin_complete=True, authority_delta=1, operator_witness=True, evidence_roots=1, hard_gates=[True]))
    # FABLE_CALL policy: routine loop does NOT call FABLE
    R["call_routine"] = should_call_fable()                                   # False
    R["call_promotion"] = should_call_fable(final_promotion=True)             # True
    expect = {"yes": (YES, "GATES_SATISFIED"), "swarm_incomplete": (NO, "SWARM_INCOMPLETE"),
              "state_mutation": (NO, "STATE_MUTATION_ATTEMPT"), "authority_grab": (NO, "AUTHORITY_EXPANSION"),
              "refuted": (NO, "REFUTED"), "inconclusive": (NO, "INCONCLUSIVE"), "missing_witness": (NO, "MISSING_WITNESS"),
              "hard_gate_fail": (NO, "HARD_GATE_FAILURE"), "legit_expansion": (YES, "GATES_SATISFIED")}
    ok_all = all(R[k] == v for k, v in expect.items()) and R["call_routine"] is False and R["call_promotion"] is True
    R["_summary"] = {"accepted": ok_all, "premium_tokens_for_mechanical_gate": 0,
                     "premium_only_when": "verdict==ESCALATE (genuine ambiguity)",
                     "invariant": "FABLE:YES != StateChange; RawCognition ↛ FABLE; recommended_verdict ignored",
                     "authority": False, "canon": False, "ledger_effect": "none"}
    return R

if __name__ == "__main__":
    r = run_receipt()
    for k, v in r.items():
        if k != "_summary": print(f"  {k:16} -> {v}")
    s = r["_summary"]; print(f"\nACCEPTED={s['accepted']} · premium_tokens_mechanical={s['premium_tokens_for_mechanical_gate']} · premium_only_when={s['premium_only_when']}")
    print("authority=false · canon=false · ledger_effect=none")

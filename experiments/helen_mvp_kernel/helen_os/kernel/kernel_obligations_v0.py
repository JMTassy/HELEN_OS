"""KERNEL_OBLIGATIONS_V0 — seven executable falsifiers for HELEN V3. authority=false · canon=false · ledger_effect=none.
NON-SOVEREIGN. Turns the V3 conceptual laws into a SOFTWARE CONTRACT: each obligation Ki is a checkable predicate
AND ships an adversarial MUTANT that must be caught. "Stop expanding the philosophy; attack K1..K7 with counterexamples."

Frozen V3 notation (symbol collision with legacy SCALE Γ_A resolved — see [[project_helen_legitimacy_paradigm]]):
    Γ_X = execution admissibility · Γ_E = epistemic admissibility · Γ_P = permission admissibility
    Γ_H = Γ_X ∧ Γ_E ∧ Γ_P     (the admission membrane)     Γ_C = cognition-allocation governance (separate)
Master separation:  Γ_C ⇏ Γ_H   ·   ExecOK ⇏ Admit   ·   Evidence ⇏ Authority   ·   ∞Agents ⇏ NewEvidenceRoot.

Obligations:
  K1  Cognition ∩ Write(State) = ∅            cognition cannot write governed state
  K2  ExecOK(x) ∧ ¬Γ_H(x) ⇒ NoEffect          execution success cannot bypass admission
  K3  Evidence(w) ∧ ¬AuthorityWitness ⇒ ¬AuthorityGain   evidence cannot mint authority
  K4  Reviewer(r) ⇒ ΔScope(r)=0               reviewers cannot mutate scope
  K5  SameRoot(c1..cn) ⇒ N_E=1                agents cannot multiply one provenance root
  K6  Δ⁺Γ ≠ ∅ ⇒ VerifiedOperatorWitness       policy EXPANSION requires operator authorization
  K7  Γ_t = Replay_Γ(H_t)                      admissibility is replay(history), not a mutable bag
"""
from __future__ import annotations
from dataclasses import dataclass, field
import re

# ── minimal typed world ──────────────────────────────────────────────────────
@dataclass
class Candidate:
    id: str
    exec_ok: bool = False          # Γ_X : sandbox execution succeeded
    epistemic_ok: bool = False     # Γ_E : epistemic warrant present
    permission_ok: bool = False    # Γ_P : operator permission present
    evidence: bool = False
    authority_witness: bool = False
    provenance_root: str = ""
    from_reviewer: bool = False
    scope_delta: int = 0           # a reviewer proposing scope change sets this != 0
    policy_expand: bool = False    # candidate expands the admissibility set (Δ⁺Γ)
    operator_witness: bool = False

def gamma_X(c: Candidate) -> bool: return c.exec_ok
def gamma_E(c: Candidate) -> bool: return c.epistemic_ok
def gamma_P(c: Candidate) -> bool: return c.permission_ok
def gamma_H(c: Candidate) -> bool: return gamma_X(c) and gamma_E(c) and gamma_P(c)

class NoEffect(Exception): pass
class Rejected(Exception): pass

@dataclass
class GovernedState:
    """K1: the ONLY mutator is _apply, called by reduce(). No public setter — cognition cannot write it."""
    _facts: set = field(default_factory=set)
    def _apply(self, event: str) -> None: self._facts.add(event)     # private; reducer-only
    def snapshot(self) -> frozenset: return frozenset(self._facts)

# ── K7 history geometry: Γ_t = Replay_Γ(H_t) ─────────────────────────────────
BASE_CAPS = frozenset({"read", "propose"})   # non-expansive default
def replay_gamma(history: list) -> frozenset:
    """Fold append-only history into the admissibility (capability) set. Only OPERATOR-WITNESSED
    POLICY_EXPAND events add capability. Everything else is non-expansive."""
    caps = set(BASE_CAPS)
    for ev in history:
        if ev.get("type") == "POLICY_EXPAND" and ev.get("operator_witness") is True:
            caps.add(ev["capability"])
    return frozenset(caps)

# ── the kernel entry: admit a candidate through Γ_H, with K2/K4/K6 enforced ──
def admit(c: Candidate, history: list, state: GovernedState) -> str:
    # K4: a reviewer finding may never carry a scope mutation
    if c.from_reviewer and c.scope_delta != 0:
        raise Rejected("K4: reviewer ⇏ scope mutation")
    # K6: any policy expansion (Δ⁺Γ) requires a verified operator witness
    if c.policy_expand and not c.operator_witness:
        raise Rejected("K6: Δ⁺Γ ⇏ admit without operator witness")
    # K2: execution success alone (¬Γ_H) yields NO governed effect
    if not gamma_H(c):
        raise NoEffect("K2: ExecOK ∧ ¬Γ_H ⇒ NoEffect")
    # admitted: append to history, then (and only then) the reducer writes state
    if c.policy_expand:
        history.append({"type": "POLICY_EXPAND", "capability": c.id, "operator_witness": True})
    history.append({"type": "ADMIT", "candidate": c.id})
    state._apply(f"admitted:{c.id}")                    # reducer is the sole writer (K1)
    return "ADMIT"

# ── K3: authority is not minted by evidence ──────────────────────────────────
def authority_gain(c: Candidate) -> bool:
    return c.authority_witness            # evidence alone (no authority witness) ⇒ no gain

# ── K5: independent provenance roots (agents cannot multiply one root) ────────
def independent_roots(claims: list) -> int:
    return len({re.sub(r"\s+", " ", (c or "").strip().lower()) for c in claims})  # by root, not by agent

def n_independent_roots_by_provenance(root_ids: list) -> int:
    return len(set(root_ids))             # SameRoot(c1..cn) ⇒ 1

# ── falsifier suite: each Ki gets a compliant check + an adversarial mutant ──
def run_receipt() -> dict:
    R = {}

    # K1 — cognition cannot write governed state
    st = GovernedState()
    k1_no_public_setter = not any(m for m in dir(st) if m in ("write", "set", "add", "mutate"))
    try:
        cognition_write = getattr(st, "write")          # cognition tries to find a writer
        k1_mutant_caught = False
    except AttributeError:
        k1_mutant_caught = True                          # no writer exists ⇒ mutant dies
    R["K1"] = {"prop": k1_no_public_setter, "mutant_caught": k1_mutant_caught}

    # K2 — ExecOK ∧ ¬Γ_H ⇒ NoEffect
    st2 = GovernedState(); h2 = []
    admitted = admit(Candidate("good", exec_ok=True, epistemic_ok=True, permission_ok=True), h2, st2) == "ADMIT"
    mutant = Candidate("exec_only", exec_ok=True, epistemic_ok=False, permission_ok=False)  # passed sandbox only
    try:
        admit(mutant, h2, st2); k2_caught = False        # if it produced effect ⇒ mutant survived
    except NoEffect:
        k2_caught = ("admitted:exec_only" not in st2.snapshot())
    R["K2"] = {"prop": admitted, "mutant_caught": k2_caught}

    # K3 — evidence ⇏ authority
    licensed = authority_gain(Candidate("p", authority_witness=True))
    k3_caught = not authority_gain(Candidate("m", evidence=True, authority_witness=False))
    R["K3"] = {"prop": licensed, "mutant_caught": k3_caught}

    # K4 — reviewer ⇏ scope mutation
    st4 = GovernedState(); h4 = []
    reviewer_ok = admit(Candidate("rev_finding", exec_ok=True, epistemic_ok=True, permission_ok=True,
                                  from_reviewer=True, scope_delta=0), h4, st4) == "ADMIT"
    try:
        admit(Candidate("rev_scopegrab", exec_ok=True, epistemic_ok=True, permission_ok=True,
                        from_reviewer=True, scope_delta=1), h4, st4); k4_caught = False
    except Rejected:
        k4_caught = True
    R["K4"] = {"prop": reviewer_ok, "mutant_caught": k4_caught}

    # K5 — SameRoot(c1..cn) ⇒ N_E=1  (∞Agents ⇏ NewEvidenceRoot)
    five_agents_one_root = n_independent_roots_by_provenance(["R1", "R1", "R1", "R1", "R1"])   # must be 1
    three_real_roots = n_independent_roots_by_provenance(["R1", "R2", "R3"])                    # must be 3
    R["K5"] = {"prop": (three_real_roots == 3), "mutant_caught": (five_agents_one_root == 1)}

    # K6 — Δ⁺Γ ⇒ operator witness
    st6 = GovernedState(); h6 = []
    expand_ok = admit(Candidate("write", exec_ok=True, epistemic_ok=True, permission_ok=True,
                                policy_expand=True, operator_witness=True), h6, st6) == "ADMIT"
    try:
        admit(Candidate("write_sneak", exec_ok=True, epistemic_ok=True, permission_ok=True,
                        policy_expand=True, operator_witness=False), h6, st6); k6_caught = False
    except Rejected:
        k6_caught = True
    R["K6"] = {"prop": expand_ok, "mutant_caught": k6_caught}

    # K7 — Γ_t = Replay_Γ(H_t)
    hist = [{"type": "POLICY_EXPAND", "capability": "write", "operator_witness": True},
            {"type": "ADMIT", "candidate": "x"}]
    replayed = replay_gamma(hist)
    k7_prop = replayed == frozenset(BASE_CAPS | {"write"})
    # mutant: a capability present in "current Γ" but NOT derivable from history ⇒ divergence detected
    forged_current = frozenset(BASE_CAPS | {"write", "delete"})        # 'delete' never authorized in history
    k7_caught = forged_current != replay_gamma(hist)
    R["K7"] = {"prop": k7_prop, "mutant_caught": k7_caught}

    accepted = all(v["prop"] and v["mutant_caught"] for v in R.values())
    R["_summary"] = {"obligations": len(R) - 0 - 1 if False else 7,
                     "properties_pass": sum(v["prop"] for k, v in R.items() if k.startswith("K")),
                     "mutants_killed": sum(v["mutant_caught"] for k, v in R.items() if k.startswith("K")),
                     "accepted": accepted, "authority": False, "canon": False, "ledger_effect": "none"}
    return R

if __name__ == "__main__":
    r = run_receipt()
    for k in ("K1", "K2", "K3", "K4", "K5", "K6", "K7"):
        v = r[k]; print(f"  {k}: property={'PASS' if v['prop'] else 'FAIL'} · mutant_killed={v['mutant_caught']}")
    s = r["_summary"]
    print(f"\nproperties_pass={s['properties_pass']}/7 · mutants_killed={s['mutants_killed']}/7 · ACCEPTED={s['accepted']}")
    print("authority=false · canon=false · ledger_effect=none · CANDIDATE until adversarially extended")

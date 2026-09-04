"""KERNEL_OBLIGATIONS_V1 — seven EARNED falsifiers. authority=false · canon=false · ledger_effect=none. NON-SOVEREIGN.
Supersedes v0, which an adversarial review broke 0/7: v0's gate inputs were self-declared booleans on the untrusted
Candidate, so the kernel checked the attacker's own testimony. v1 fixes the root cause — gate inputs are UNFORGEABLE
GRANTS minted by a trusted authority the candidate does not hold the key for (the vertical_slice_v0 capability model).

HONEST BOUND (threat model is explicit — an adversarial re-review corrected an earlier understatement):
  * SOUND vs TOKEN-LEAK adversary (has token bytes, NOT the module namespace): 7/7. MAC binds kind|subject, so
    grants cannot be forged, reused across subjects, cross-kind substituted, or replayed for another capability.
    This is the load-bearing claim: the type/capability DISCIPLINE is real.
  * NOT ENFORCED vs SHARED-INTERPRETER adversary (untrusted cognition runs in-process): 0/7. The mint objects
    (SANDBOX/WARRANT/POLICY/OPERATOR.grant) and _REDUCE_CAP are module globals, so in-process code can mint any
    grant directly (no key theft needed) or import _REDUCE_CAP to write state bypassing admit(). GovernedState's
    closure is also reachable via __closure__ reflection.
  => Secret-key unforgeability is necessary but NOT sufficient; NAMESPACE UNREACHABILITY is the missing half.
     True enforcement needs a PRIVILEGE/PROCESS BOUNDARY (separate process, capability-descriptor passing, OS
     isolation) so untrusted code holds tokens but never the mint/reducer objects. Same gap as vertical_slice_v0.

Notation: Γ_X exec · Γ_E epistemic · Γ_P permission · Γ_H=Γ_X∧Γ_E∧Γ_P · Γ_C cognition-allocation (separate).
"""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib, hmac, os

# ── trusted authorities: each holds a secret the candidate cannot access ──────
class Mint:
    """Mints unforgeable grants. verify() checks a grant was minted by THIS authority for (kind, subject)."""
    def __init__(self): self._k = os.urandom(32)
    def grant(self, kind: str, subject: str) -> str:
        return hmac.new(self._k, f"{kind}|{subject}".encode(), hashlib.sha256).hexdigest()
    def verify(self, token: str, kind: str, subject: str) -> bool:
        return isinstance(token, str) and hmac.compare_digest(token, self.grant(kind, subject))

SANDBOX  = Mint()   # mints EXEC grants only after real sandbox execution   (Γ_X)
WARRANT  = Mint()   # mints EPISTEMIC + AUTHORITY grants                     (Γ_E, K3)
POLICY   = Mint()   # mints PERMISSION + SCOPE grants                        (Γ_P, K4)
OPERATOR = Mint()   # mints OPERATOR_EXPANSION grants — the human authority  (K6/K7)

@dataclass
class Candidate:
    id: str
    payload: str = ""
    source_content: str = ""          # provenance is derived from THIS, not a caller label (K5)
    exec_grant: str = ""              # from SANDBOX
    epistemic_grant: str = ""         # from WARRANT
    permission_grant: str = ""        # from POLICY
    authority_grant: str = ""         # from WARRANT (K3)
    scope_grant: str = ""             # from POLICY — required for ANY scope change (K4)
    operator_grant: str = ""          # from OPERATOR (K6/K7)
    requests_capability: str = ""     # capability it wants to exercise (kernel checks vs Γ_t, not a self-flag)
    scope_delta: int = 0

def gamma_X(c): return SANDBOX.verify(c.exec_grant, "EXEC", c.id)
def gamma_E(c): return WARRANT.verify(c.epistemic_grant, "EPISTEMIC", c.id)
def gamma_P(c): return POLICY.verify(c.permission_grant, "PERMISSION", c.id)
def gamma_H(c): return gamma_X(c) and gamma_E(c) and gamma_P(c)

class NoEffect(Exception): pass
class Rejected(Exception): pass

# ── K1: real encapsulation via closure — cognition gets ONLY a read handle ────
def make_state():
    _facts = set()
    def _reduce(event, _cap):
        if _cap is not _REDUCE_CAP: raise Rejected("K1: only the reducer capability may write state")
        _facts.add(event)
    def snapshot(): return frozenset(_facts)
    return snapshot, _reduce
_REDUCE_CAP = object()   # unforgeable in-process token; cognition never receives it

# ── K7: Γ_t = Replay_Γ(H_t), history stores SIGNED operator grants ────────────
BASE_CAPS = frozenset({"read", "propose"})
def replay_gamma(history: list) -> frozenset:
    caps = set(BASE_CAPS)
    for ev in history:
        if ev.get("type") == "POLICY_EXPAND":
            # re-verify the operator signature; a forged/absent grant does NOT expand Γ
            if OPERATOR.verify(ev.get("operator_grant", ""), "OPERATOR_EXPANSION", ev.get("capability", "")):
                caps.add(ev["capability"])
    return frozenset(caps)

# ── kernel entry ──────────────────────────────────────────────────────────────
def admit(c: Candidate, history: list, reduce_fn) -> str:
    # K4: ANY scope change requires a POLICY-minted scope grant (not gated on a self-set 'reviewer' flag)
    if c.scope_delta != 0 and not POLICY.verify(c.scope_grant, "SCOPE", c.id):
        raise Rejected("K4: scope mutation without POLICY scope grant")
    # K6: EXPANSION is DETECTED by the kernel (requested cap not in current Γ_t), not self-declared
    gamma_t = replay_gamma(history)
    is_expansion = bool(c.requests_capability) and c.requests_capability not in gamma_t
    if is_expansion and not OPERATOR.verify(c.operator_grant, "OPERATOR_EXPANSION", c.requests_capability):
        raise Rejected("K6: Δ⁺Γ without verified operator grant")
    # K2: execution success alone (¬Γ_H) yields NO governed effect
    if not gamma_H(c):
        raise NoEffect("K2: ExecOK ∧ ¬Γ_H ⇒ NoEffect")
    if is_expansion:  # record the SIGNED grant, not a hard-coded True (K7)
        history.append({"type": "POLICY_EXPAND", "capability": c.requests_capability, "operator_grant": c.operator_grant})
    history.append({"type": "ADMIT", "candidate": c.id})
    reduce_fn(f"admitted:{c.id}", _REDUCE_CAP)
    return "ADMIT"

def authority_gain(c): return WARRANT.verify(c.authority_grant, "AUTHORITY", c.id)   # K3: needs a minted grant

# ── K5: provenance root = content hash (agents cannot relabel one root into many) ──
def provenance_root(source_content: str) -> str:
    return hashlib.sha256((source_content or "").strip().lower().encode()).hexdigest()[:16]
def n_independent_roots(sources: list) -> int:
    return len({provenance_root(s) for s in sources})

# ── falsifier suite: each Ki gets a compliant PASS + the adversary's real counterexample MUST be caught ──
def run_receipt() -> dict:
    R = {}

    # K1 — cognition cannot write governed state (closure; only _REDUCE_CAP writes)
    snap, reduce_fn = make_state()
    try:  reduce_fn("forged", object()); k1 = False               # cognition forging a cap → rejected
    except Rejected: k1 = ("forged" not in snap())
    admit(Candidate("ok", exec_grant=SANDBOX.grant("EXEC","ok"), epistemic_grant=WARRANT.grant("EPISTEMIC","ok"),
                    permission_grant=POLICY.grant("PERMISSION","ok")), [], reduce_fn)
    R["K1"] = {"enforced": k1 and "admitted:ok" in snap()}

    # K2 — ExecOK ∧ ¬Γ_H ⇒ NoEffect ; AND self-declared gate is now unforgeable
    snap2, red2 = make_state(); h2 = []
    good = admit(Candidate("g", exec_grant=SANDBOX.grant("EXEC","g"), epistemic_grant=WARRANT.grant("EPISTEMIC","g"),
                           permission_grant=POLICY.grant("PERMISSION","g")), h2, red2) == "ADMIT"
    # adversary: exec real, but tries to FORGE epistemic+permission grants (no key) → gate fails
    forged = Candidate("m", exec_grant=SANDBOX.grant("EXEC","m"),
                       epistemic_grant="deadbeef"*8, permission_grant="deadbeef"*8)
    try: admit(forged, h2, red2); k2 = False
    except NoEffect: k2 = "admitted:m" not in snap2()
    R["K2"] = {"enforced": good and k2}

    # K3 — evidence ⇏ authority ; forging the authority grant fails
    licensed = authority_gain(Candidate("p", authority_grant=WARRANT.grant("AUTHORITY","p")))
    forged_auth = not authority_gain(Candidate("m", authority_grant="ff"*32))   # candidate can't mint it
    R["K3"] = {"enforced": licensed and forged_auth}

    # K4 — scope mutation from ANY candidate (incl. non-reviewer) without a scope grant is caught
    snap4, red4 = make_state(); h4 = []
    try:  # the v0 bypass: non-reviewer scope grab
        admit(Candidate("grab", exec_grant=SANDBOX.grant("EXEC","grab"), epistemic_grant=WARRANT.grant("EPISTEMIC","grab"),
                        permission_grant=POLICY.grant("PERMISSION","grab"), scope_delta=1), h4, red4); k4 = False
    except Rejected: k4 = True
    R["K4"] = {"enforced": k4}

    # K5 — SameRoot ⇒ 1, even if agents relabel; distinct content ⇒ distinct roots
    same_source = "the campus thesis is training plus circular economy"
    relabel_attack = n_independent_roots([same_source, same_source+" ", same_source.upper(), " "+same_source, same_source]) == 1
    real_three = n_independent_roots(["source alpha", "source beta", "source gamma"]) == 3
    R["K5"] = {"enforced": relabel_attack and real_three}

    # K6 — expansion DETECTED by kernel (not self-flag); unwitnessed expansion caught even if candidate hides it
    snap6, red6 = make_state(); h6 = []
    # candidate requests a capability NOT in Γ_t and does NOT set any flag — kernel detects expansion anyway
    sneak = Candidate("sneak", exec_grant=SANDBOX.grant("EXEC","sneak"), epistemic_grant=WARRANT.grant("EPISTEMIC","sneak"),
                      permission_grant=POLICY.grant("PERMISSION","sneak"), requests_capability="delete")
    try: admit(sneak, h6, red6); k6 = False
    except Rejected: k6 = True
    # with a real operator grant, the SAME expansion is admitted
    ok_expand = admit(Candidate("legit", exec_grant=SANDBOX.grant("EXEC","legit"), epistemic_grant=WARRANT.grant("EPISTEMIC","legit"),
                     permission_grant=POLICY.grant("PERMISSION","legit"), requests_capability="delete",
                     operator_grant=OPERATOR.grant("OPERATOR_EXPANSION","delete")), h6, red6) == "ADMIT"
    R["K6"] = {"enforced": k6 and ok_expand}

    # K7 — replay re-verifies the SIGNED operator grant; forged history does NOT expand Γ
    forged_history = [{"type":"POLICY_EXPAND","capability":"delete","operator_grant":"ff"*32}]   # bogus signature
    k7_forged_rejected = "delete" not in replay_gamma(forged_history)
    real_history = [{"type":"POLICY_EXPAND","capability":"delete","operator_grant":OPERATOR.grant("OPERATOR_EXPANSION","delete")}]
    k7_real_ok = "delete" in replay_gamma(real_history)
    R["K7"] = {"enforced": k7_forged_rejected and k7_real_ok}

    enforced = sum(v["enforced"] for v in R.values())
    R["_summary"] = {"token_leak_threat_model": f"{enforced}/7 (grants unforgeable to an attacker holding token bytes)",
                     "shared_interpreter_threat_model": "0/7 (in-process cognition can call the mints / import _REDUCE_CAP — needs a privilege boundary)",
                     "load_bearing_claim": "type/capability DISCIPLINE is real (subject/kind/capability MAC binding); OS-isolation is NOT provided",
                     "accepted": False,  # NOT accepted as fully enforced — residual: in-process namespace reachability
                     "authority": False, "canon": False, "ledger_effect": "none"}
    return R

if __name__ == "__main__":
    r = run_receipt()
    for k in ("K1","K2","K3","K4","K5","K6","K7"): print(f"  {k}: enforced={r[k]['enforced']}")
    s = r["_summary"]; print(f"\nENFORCED={s['enforced']} · ACCEPTED={s['accepted']} · {s['unforgeability']}")
    print("authority=false · canon=false · ledger_effect=none · CANDIDATE until independently re-adversaried")

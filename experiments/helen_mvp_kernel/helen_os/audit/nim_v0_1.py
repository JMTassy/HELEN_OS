"""NIM_V0.1_WITNESS_FRAME_ORACLE — write/frame confinement + witness applicability. 🔵 OBSERVED · authority=false.

Scope (frozen, unchanged): WRITE/FRAME layer only. This is NOT a non-interference proof — relational
(paired-world) influence `Σ₁≡_L̄ Σ₂ ⇒ T(Σ₁)≡_L̄ T(Σ₂)` and transitive laundering are V0.2/V0.3.
A PASS means: every preregistered mutant in the finite declared corpus was killed and every declared
positive control survived, under the declared protection contracts. Nothing stronger.

HARDENED after independent HAL audit (findings NIM-02..06 closed):
  - D1: contract_override is now LIVE — an *authorized* override is merged into the contract registry
        before FrameOK (an unlicensed override is still rejected). No dead governance path remains.
  - SUBJECT/TENANT/EXPIRY/PRESTATE binding: witness applicability checks the acting requester's
        identity, tenant, temporal validity, AND binding to the exact prestate digest — not merely
        operation/object/scope. Authentic-but-inapplicable ⇒ REJECT (AuthenticAuthority ⊬ Applicable).
  - DISCHARGER: separation of duty is now three-way — proposer ≠ authorizer ≠ discharger.
  - L(T): the licensed write-frame is validated against a policy table keyed by the governed
        operation (OP_FRAME). The transition author cannot self-authorize frame expansion.

The property under test:
    ADMIT(δ) ⟺ L(δ)⊆OP_FRAME[op] ∧ Obligations discharged (applicable) ∧ 3-way SoD
                    ∧ FrameOK(δ,Σ,Σ') ∧ ¬illicit-observer-substitution
    FrameOK(δ,Σ,Σ') ⟺ ∀ j∉L(δ): O_j(Σ) ≈_j O_j(Σ')   (over independently-specified protection contracts)
Determinism: pure.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Callable, Dict, FrozenSet, List, Mapping, Optional, Tuple

COORDS: Tuple[str, ...] = ("Q", "E", "D", "R", "A", "X", "RHO_E", "RHO_A", "PI", "M", "P", "C")
SENSITIVE: FrozenSet[str] = frozenset({"A", "RHO_E", "X"})

# policy-derived licensed write-frames, keyed by the governed operation. The transition AUTHOR may
# not declare a frame broader than its operation's policy allows (HARDEN L(T) / NIM-05).
OP_FRAME: Dict[str, FrozenSet[str]] = {
    "noop": frozenset({"Q", "E", "D", "R", "PI", "M", "P", "C"}),   # non-sensitive writes
    "grant": frozenset({"A"}),
    "effect": frozenset({"X"}),
    "add_root": frozenset({"RHO_E"}),
}

ADMIT, REJECT = "ADMIT", "REJECT"
State = Mapping[str, int]


def zero_state() -> Dict[str, int]:
    return {c: 0 for c in COORDS}


def prestate_digest(s: State) -> tuple:
    """Canonical, deterministic digest a witness binds to (NIM-03 prestate binding)."""
    return tuple(sorted((c, int(s.get(c, 0))) for c in COORDS))


# ── protection contract per coordinate ──
@dataclass(frozen=True)
class ProtectionContract:
    coord: str
    observe: Callable[[State], int]
    equiv: Callable[[int, int], bool]
    version: str = "v1"


def default_contracts() -> Dict[str, ProtectionContract]:
    return {c: ProtectionContract(c, (lambda s, c=c: s[c]), (lambda a, b: a == b)) for c in COORDS}


def blind_contract(coord: str) -> ProtectionContract:
    return ProtectionContract(coord, (lambda s: 0), (lambda a, b: True), version="BLIND")


# ── object-capability: authority = possession of an APPLICABLE capability across all dimensions ──
@dataclass(frozen=True)
class Capability:
    subject: str                       # the principal that holds it (must match the requester)
    operation: str
    object: str
    scope: FrozenSet[str]
    tenant: str = "tenant-A"
    fresh: bool = True                  # temporal validity / expiry
    bound_prestate: Optional[tuple] = None   # prestate digest this witness was issued against


@dataclass(frozen=True)
class Transition:
    id: str
    licensed_frame: FrozenSet[str]
    writes: Mapping[str, int]
    op: str = "noop"
    object: str = ""
    requester: str = "alice"            # principal on whose behalf the effect is requested
    tenant: str = "tenant-A"
    proposer: str = "p"
    authorizer: str = "a"
    discharger: str = "d"
    capability: Optional[Capability] = None
    presentation: str = "plain"         # metadata ONLY — must never affect disposition
    contract_override: Mapping[str, ProtectionContract] = field(default_factory=dict)
    # NIM-07 meta-protection: authority to substitute the protection registry must be an APPLICABLE
    # capability, NEVER a self-declared field. `boolean says authority ⇏ authority exists`.
    contract_authority: Optional[Capability] = None


# ── kernel ──
def _apply(t: Transition, s: State) -> Dict[str, int]:
    s2 = dict(s)
    s2.update(t.writes)
    return s2


def _applicable(cap: Optional[Capability], t: Transition, s: State) -> bool:
    """AuthenticAuthority ⊬ ApplicableAuthority — every dimension checked (NIM-02/03)."""
    if cap is None:
        return False
    return (cap.operation == t.op
            and cap.object == t.object
            and t.object in cap.scope
            and cap.subject == t.requester                       # SUBJECT binding
            and cap.tenant == t.tenant                            # TENANT binding
            and cap.fresh                                         # temporal validity / expiry
            and cap.bound_prestate == prestate_digest(s))         # PRESTATE binding (None ⇒ mismatch ⇒ reject)


def _meta_applicable(cap: Optional[Capability], t: "Transition", s: State) -> bool:
    """Contract-override (protection-registry substitution) is a governed META-transition (NIM-07).
    Its authority must be an APPLICABLE capability for the `observe_substitute` op — a self-declared
    field can never license weakening the very contracts that judge the transition."""
    if cap is None:
        return False
    return (cap.operation == "observe_substitute"
            and cap.subject == t.requester
            and cap.tenant == t.tenant
            and cap.fresh
            and cap.bound_prestate == prestate_digest(s)
            and set(t.contract_override.keys()) <= cap.scope)     # scope must cover the overridden coords


def _obligations_discharged(t: Transition, s: State) -> bool:
    for j, new in t.writes.items():
        if j not in t.licensed_frame or j not in SENSITIVE:
            continue
        if new - s.get(j, 0) <= 0:
            continue
        if j in ("A", "X") and not _applicable(t.capability, t, s):
            return False
        if j == "RHO_E" and not (t.capability and _applicable(t.capability, t, s)):
            return False
    return True


def _sod_ok(t: Transition) -> bool:
    """Three-way separation of duty on sensitive writes: proposer ≠ authorizer ≠ discharger (NIM-04)."""
    if any(j in SENSITIVE for j in t.writes):
        return len({t.proposer, t.authorizer, t.discharger}) == 3
    return True


def _frame_licensed(t: Transition) -> bool:
    """The author-declared write-frame must fit inside the operation's policy frame (NIM-05)."""
    return t.licensed_frame <= OP_FRAME.get(t.op, frozenset())


def _frame_ok(t: Transition, s: State, s2: State, contracts: Mapping[str, ProtectionContract]) -> bool:
    for j in COORDS:
        if j in t.licensed_frame:
            continue
        c = contracts[j]
        if not c.equiv(c.observe(s), c.observe(s2)):
            return False
    return True


def admit(t: Transition, s: State,
          contracts: Optional[Mapping[str, ProtectionContract]] = None) -> Tuple[str, str]:
    contracts = dict(contracts or default_contracts())

    # observer/contract substitution is a governed META-transition. The override is merged into the
    # registry ONLY if licensed by an APPLICABLE capability (NIM-07). A self-declared field can never
    # license it — `boolean says authority ⇏ authority exists`. Fail-closed: no applicable cap ⇒ REJECT.
    if t.contract_override:
        if not _meta_applicable(t.contract_authority, t, s):
            return REJECT, "META_AUTHORITY_INAPPLICABLE"
        contracts.update(t.contract_override)

    if not _frame_licensed(t):
        return REJECT, "FRAME_NOT_LICENSED"
    if not _obligations_discharged(t, s):
        return REJECT, "OBLIGATION_NOT_DISCHARGED"
    if not _sod_ok(t):
        return REJECT, "SOD_VIOLATION"
    if not _frame_ok(t, s, _apply(t, s), contracts):
        return REJECT, "FRAME_VIOLATION"
    return ADMIT, "OK"


def observer_sees(contract: ProtectionContract, s: State, mutate: Callable[[State], State]) -> bool:
    return not contract.equiv(contract.observe(s), contract.observe(mutate(s)))


def replay(s0: State, admitted: List[Transition]) -> Dict[str, int]:
    s = dict(s0)
    for t in admitted:
        s = _apply(t, s)
    return s


# ── canonical builders for the corpus + positive controls ──
def _S0():
    return zero_state()


def _good_cap(**kw):
    base = dict(subject="alice", operation="grant", object="obj1", scope=frozenset({"obj1"}),
                tenant="tenant-A", fresh=True, bound_prestate=prestate_digest(_S0()))
    base.update(kw)
    return Capability(**base)


def T_CAP() -> Transition:
    return Transition("p_cap", frozenset({"Q"}), {"Q": 1}, op="noop")


def T_AUTH() -> Transition:
    return Transition("p_auth", frozenset({"A"}), {"A": 1}, op="grant", object="obj1",
                      requester="alice", capability=_good_cap(), proposer="p", authorizer="a", discharger="d")


def build_corpus() -> Dict[str, list]:
    """Every family NON-EMPTY. Each entry (transition, expected_verdict). Confused-deputy mutants
    each flip EXACTLY ONE applicability dimension off the valid T_AUTH baseline."""
    baseA = dict(op="grant", object="obj1", requester="alice", tenant="tenant-A",
                 proposer="p", authorizer="a", discharger="d")
    return {
        "FRAME": [
            (Transition("f_q_A", frozenset({"Q"}), {"Q": 1, "A": 1}, op="noop", proposer="p", authorizer="a", discharger="d"), REJECT),
            (Transition("f_a_X", frozenset({"A"}), {"A": 1, "X": 1}, capability=_good_cap(), **baseA), REJECT),
            (Transition("f_expand", frozenset({"Q", "A"}), {"Q": 1, "A": 1}, op="noop", proposer="p", authorizer="a", discharger="d"), REJECT),  # HARDEN L(T): FRAME_NOT_LICENSED
        ],
        "WITNESS": [
            (Transition("w_missing", frozenset({"A"}), {"A": 1}, capability=None, **baseA), REJECT),
            (Transition("w_stale", frozenset({"A"}), {"A": 1}, capability=_good_cap(fresh=False), **baseA), REJECT),
            (Transition("w_obj", frozenset({"A"}), {"A": 1}, capability=_good_cap(object="other", scope=frozenset({"other"})), **baseA), REJECT),
            (Transition("w_op", frozenset({"A"}), {"A": 1}, capability=_good_cap(operation="read"), **baseA), REJECT),
        ],
        "DEPUTY": [   # authentic-but-inapplicable, one dimension each (NIM-02/03/06)
            (Transition("dep_subject", frozenset({"A"}), {"A": 1}, capability=_good_cap(subject="eve"), **baseA), REJECT),
            (Transition("dep_scope", frozenset({"A"}), {"A": 1}, capability=_good_cap(scope=frozenset({"sandbox"})), **baseA), REJECT),
            (Transition("dep_tenant", frozenset({"A"}), {"A": 1}, capability=_good_cap(tenant="tenant-B"), **baseA), REJECT),
            (Transition("dep_prestate", frozenset({"A"}), {"A": 1}, capability=_good_cap(bound_prestate=prestate_digest({**_S0(), "M": 9})), **baseA), REJECT),
        ],
        "DUTY": [
            (Transition("d_pa", frozenset({"A"}), {"A": 1}, capability=_good_cap(), op="grant", object="obj1", requester="alice", proposer="x", authorizer="x", discharger="d"), REJECT),
            (Transition("d_ad", frozenset({"A"}), {"A": 1}, capability=_good_cap(), op="grant", object="obj1", requester="alice", proposer="p", authorizer="y", discharger="y"), REJECT),
        ],
        "POSITIVE": [(T_CAP(), ADMIT), (T_AUTH(), ADMIT)],
        "STR": [(replace(T_CAP(), presentation=p), ADMIT) for p in ("plain", "prestige", "cosmic", "urgent", "humble")],
    }


def _kill_family(entries) -> Tuple[int, int, list]:
    killed, survivors = 0, []
    for t, expected in entries:
        if admit(t, zero_state())[0] == expected:
            killed += 1
        else:
            survivors.append(t.id)
    return killed, len(entries), survivors


def observer_family() -> dict:
    """K_O: substitution rejected + adequacy + the coarse-observer ESCAPE teeth (blind IS dangerous)."""
    S = zero_state()
    forbidden = Transition("frb_A", frozenset({"Q"}), {"Q": 1, "A": 1}, op="noop",
                           proposer="p", authorizer="a", discharger="d")
    strict = admit(forbidden, S, default_contracts())[0]                        # BLOCK
    blind_reg = {**default_contracts(), "A": blind_contract("A")}
    coarse = admit(forbidden, S, blind_reg)[0]                                  # ESCAPE (blind is dangerous)
    substitution = admit(replace(forbidden, contract_override={"A": blind_contract("A")},
                                 contract_authority=None), S)[0]                # self-declared/forged → REJECT
    # NIM-07 live-check: an APPLICABLE meta-capability actually merges the override (proves not dead code).
    good_meta = Capability(subject="alice", operation="observe_substitute", object="",
                           scope=frozenset({"A"}), tenant="tenant-A", fresh=True,
                           bound_prestate=prestate_digest(S))
    authorized_live = admit(replace(forbidden, contract_override={"A": blind_contract("A")},
                                    contract_authority=good_meta), S)[0]        # licensed override merged → escapes
    adequacy = all(observer_sees(default_contracts()[c], S, (lambda s, c=c: {**dict(s), c: s[c] + 1})) for c in COORDS)
    blind_control_triggered = (strict == REJECT and coarse == ADMIT)
    ok = (substitution == REJECT and blind_control_triggered and adequacy and authorized_live == ADMIT)
    return {"killed": int(ok), "total": 1, "strict": strict, "coarse_escape": coarse,
            "substitution": substitution, "authorized_override_live": authorized_live, "adequacy": adequacy}


def meta_family() -> dict:
    """META (NIM-07): a forged/inapplicable contract-authority must be REJECTED for its ONE dimension;
    a genuinely applicable meta-capability must ADMIT (non-vacuity — not a deny-all)."""
    S = zero_state()
    frb = Transition("m_base", frozenset({"Q"}), {"Q": 1, "A": 1}, op="noop",
                     proposer="p", authorizer="a", discharger="d")   # requester=alice, tenant=tenant-A
    ov = {"A": blind_contract("A")}
    good = Capability(subject="alice", operation="observe_substitute", object="",
                      scope=frozenset({"A"}), tenant="tenant-A", fresh=True, bound_prestate=prestate_digest(S))
    mutants = {                                    # each flips exactly ONE applicability dimension
        "forged_none":    None,
        "wrong_subject":  replace(good, subject="eve"),
        "wrong_op":       replace(good, operation="grant"),
        "stale":          replace(good, fresh=False),
        "wrong_prestate": replace(good, bound_prestate=prestate_digest({**S, "M": 9})),
        "scope_miss":     replace(good, scope=frozenset({"Q"})),
    }
    survivors = [name for name, cap in mutants.items()
                 if admit(replace(frb, contract_override=ov, contract_authority=cap), S)[0] != REJECT]
    genuine = admit(replace(frb, contract_override=ov, contract_authority=good), S)[0]
    ok = (not survivors and genuine == ADMIT)
    return {"killed": int(ok), "total": 1, "mutants_killed": len(mutants) - len(survivors),
            "mutants_total": len(mutants), "survivors": survivors, "genuine": genuine}


def run_receipt() -> dict:
    corpus = build_corpus()
    fam = {n: _kill_family(corpus[n]) for n in ("FRAME", "WITNESS", "DEPUTY", "DUTY")}
    obs = observer_family()
    meta = meta_family()
    strk, strt, _ = _kill_family(corpus["STR"])
    pk, pt, _ = _kill_family(corpus["POSITIVE"])
    admitted = [t for t, e in corpus["POSITIVE"] if e == ADMIT]
    recon = replay(zero_state(), admitted)
    replay_exact = int(recon["Q"] == 1 and recon["A"] == 1)

    def one(n, d):
        return 1 if (d > 0 and n == d) else 0

    R = (one(*fam["FRAME"][:2]), one(*fam["WITNESS"][:2]), one(*fam["DUTY"][:2]), one(*fam["DEPUTY"][:2]),
         one(obs["killed"], obs["total"]), one(meta["killed"], meta["total"]),
         one(strk, strt), one(pk, pt), one(replay_exact, 1))
    return {"FRAME": fam["FRAME"], "WITNESS": fam["WITNESS"], "DUTY": fam["DUTY"], "DEPUTY": fam["DEPUTY"],
            "OBSERVER": obs, "META": meta, "STR": (strk, strt), "POSITIVE": (pk, pt), "REPLAY": (replay_exact, 1),
            "acceptance_vector": R, "accepted": all(x == 1 for x in R)}

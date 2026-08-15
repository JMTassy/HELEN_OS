"""NIM_V0.1_WITNESS_FRAME_ORACLE — write/frame confinement kill-test harness. 🔵 OBSERVED · authority=false.

Scope (frozen): this is the WRITE/FRAME layer only. Relational (paired-world) non-interference —
`Σ₁≡_L̄ Σ₂ ⇒ T(Σ₁)≡_L̄ T(Σ₂)` — and transitive/compositional laundering are explicitly deferred to
V0.2/V0.3. A PASS here means: every preregistered mutant in the finite declared corpus was killed and
every declared positive control survived. Nothing stronger.

The law under test:  a transition receives a LICENSED WRITE-FRAME L(T), not generic permission to
"change state". Admission requires:
    ADMIT ⟺ DomainOK ∧ Obligations discharged (applicable, not merely present)
                    ∧ SoD ∧ FrameOK ∧ ¬illicit-observer-substitution
    FrameOK(T,Σ,Σ') ⟺ ∀ j∉L(T): O_j(Σ) ≈_j O_j(Σ')     (over independently-specified protection contracts)

Kill-test families (each must be non-empty): FRAME · WITNESS · DUTY · DEPUTY · OBSERVER · SEMANTIC ·
POSITIVE · REPLAY. Acceptance = R = (1,…,1) with every denominator nonzero and recorded.
Determinism: pure.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Callable, Dict, FrozenSet, List, Mapping, Optional, Tuple

# ── the 12 institutional coordinates ──
COORDS: Tuple[str, ...] = ("Q", "E", "D", "R", "A", "X", "RHO_E", "RHO_A", "PI", "M", "P", "C")
SENSITIVE: FrozenSet[str] = frozenset({"A", "RHO_E", "X"})     # writing these requires a discharged obligation

ADMIT, REJECT = "ADMIT", "REJECT"

State = Mapping[str, int]


def zero_state() -> Dict[str, int]:
    return {c: 0 for c in COORDS}


# ── protection contract per coordinate: observer + equivalence + mutation corpus + version ──
@dataclass(frozen=True)
class ProtectionContract:
    coord: str
    observe: Callable[[State], int]
    equiv: Callable[[int, int], bool]
    version: str = "v1"


def default_contracts() -> Dict[str, ProtectionContract]:
    return {c: ProtectionContract(c, (lambda s, c=c: s[c]), (lambda a, b: a == b)) for c in COORDS}


def blind_contract(coord: str) -> ProtectionContract:
    """A deliberately BLIND observer — used only to prove the observer-adequacy metric has teeth."""
    return ProtectionContract(coord, (lambda s: 0), (lambda a, b: True), version="BLIND")


# ── capability (object-capability semantics: authority = possession of an APPLICABLE capability) ──
@dataclass(frozen=True)
class Capability:
    subject: str
    operation: str
    object: str
    scope: FrozenSet[str]
    fresh: bool = True


@dataclass(frozen=True)
class RootWitness:
    root: str
    admitted: bool = True


@dataclass(frozen=True)
class Transition:
    id: str
    licensed_frame: FrozenSet[str]
    writes: Mapping[str, int]                      # coord → new value (may exceed L → a frame attack)
    op: str = "noop"
    object: str = ""
    proposer: str = "p"
    authorizer: str = "a"
    discharger: str = "d"
    capability: Optional[Capability] = None        # for A / X writes
    root_witness: Optional[RootWitness] = None      # for RHO_E writes
    presentation: str = "plain"                     # metadata ONLY — must never affect disposition
    contract_override: Mapping[str, ProtectionContract] = field(default_factory=dict)
    has_contract_authority: bool = False            # workers never have this


# ── the kernel ──
def _apply(t: Transition, s: State) -> Dict[str, int]:
    s2 = dict(s)
    s2.update(t.writes)
    return s2


def _applicable(cap: Optional[Capability], t: Transition) -> bool:
    """AuthenticAuthority ⊬ ApplicableAuthority — the confused-deputy boundary."""
    if cap is None:
        return False
    return (cap.operation == t.op and cap.object == t.object
            and t.object in cap.scope and cap.fresh)


def _obligations_discharged(t: Transition, s: State) -> bool:
    for j, new in t.writes.items():
        if j not in t.licensed_frame:
            continue                                # out-of-frame writes are caught by FrameOK, not here
        delta = new - s.get(j, 0)
        if delta <= 0 or j not in SENSITIVE:
            continue
        if j in ("A", "X"):
            if not _applicable(t.capability, t):    # applicable capability required
                return False
        if j == "RHO_E":
            if not (t.root_witness and t.root_witness.admitted):
                return False
    return True


def _sod_ok(t: Transition) -> bool:
    """Sensitive writes require proposer ≠ authorizer (separation of duty)."""
    if any(j in SENSITIVE for j in t.writes):
        return t.proposer != t.authorizer
    return True


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
    """The V0.1 admission function. Returns (verdict, reason)."""
    contracts = dict(contracts or default_contracts())

    # observer-substitution guard: changing a protection contract is itself a governed transition.
    # A worker cannot weaken an observer to hide a forbidden mutation.
    if t.contract_override and not t.has_contract_authority:
        return REJECT, "OBSERVER_SUBSTITUTION_UNLICENSED"

    if not _obligations_discharged(t, s):
        return REJECT, "OBLIGATION_NOT_DISCHARGED"
    if not _sod_ok(t):
        return REJECT, "SOD_VIOLATION"

    s2 = _apply(t, s)
    if not _frame_ok(t, s, s2, contracts):
        return REJECT, "FRAME_VIOLATION"
    return ADMIT, "OK"


def observer_sees(contract: ProtectionContract, s: State, mutate: Callable[[State], State]) -> bool:
    """Observer adequacy: the observer must DISTINGUISH a forbidden mutation of its coordinate."""
    return not contract.equiv(contract.observe(s), contract.observe(mutate(s)))


# ── replay: admitted transitions reconstruct the final state ──
def replay(s0: State, admitted: List[Transition]) -> Dict[str, int]:
    s = dict(s0)
    for t in admitted:
        s = _apply(t, s)
    return s


# ── the frozen mutation corpus + the vectorial receipt R = (K_F,K_W,K_D,K_C,K_O,K_S,K_P,K_R) ──
def _cap(obj="obj1", op="grant", scope=("obj1",), fresh=True):
    return Capability("a", op, obj, frozenset(scope), fresh)


def build_corpus() -> Dict[str, list]:
    """Every family NON-EMPTY. Each entry is (transition, expected_verdict)."""
    S = zero_state()
    baseA = dict(op="grant", object="obj1", proposer="p", authorizer="a")
    return {
        "FRAME": [
            (Transition("f_q_A", frozenset({"Q"}), {"Q": 1, "A": 1}, proposer="p", authorizer="a"), REJECT),
            (Transition("f_a_X", frozenset({"A"}), {"A": 1, "X": 1}, capability=_cap(), **baseA), REJECT),
        ],
        "WITNESS": [
            (Transition("w_missing", frozenset({"A"}), {"A": 1}, capability=None, **baseA), REJECT),
            (Transition("w_stale", frozenset({"A"}), {"A": 1}, capability=_cap(fresh=False), **baseA), REJECT),
            (Transition("w_obj", frozenset({"A"}), {"A": 1}, capability=_cap(obj="other", scope=("other",)), **baseA), REJECT),
            (Transition("w_op", frozenset({"A"}), {"A": 1}, capability=_cap(op="read"), **baseA), REJECT),
        ],
        "DUTY": [
            (Transition("d_collapse", frozenset({"A"}), {"A": 1}, op="grant", object="obj1",
                        capability=_cap(), proposer="x", authorizer="x"), REJECT),
        ],
        "DEPUTY": [
            (Transition("dep_scope", frozenset({"A"}), {"A": 1}, capability=_cap(scope=("sandbox",)), **baseA), REJECT),
        ],
        "POSITIVE": [
            (Transition("p_cap", frozenset({"Q"}), {"Q": 1}), ADMIT),
            (Transition("p_auth", frozenset({"A"}), {"A": 1}, capability=_cap(), **baseA), ADMIT),
        ],
        "STR": [   # presentation variants of an admitted baseline — disposition must be invariant
            (replace(Transition("s_cap", frozenset({"Q"}), {"Q": 1}), presentation=p), ADMIT)
            for p in ("plain", "prestige", "cosmic", "urgent", "humble")
        ],
    }


def _kill_family(entries) -> Tuple[int, int, list]:
    killed, survivors = 0, []
    for t, expected in entries:
        v = admit(t, zero_state())[0]
        if v == expected:
            killed += 1
        else:
            survivors.append(t.id)
    return killed, len(entries), survivors


def observer_family() -> dict:
    """K_O: substitution rejected + observer adequacy + the coarse-observer ESCAPE teeth control.
    The teeth require showing the blind observer is DANGEROUS: a forbidden write that the strict
    observer BLOCKS would ESCAPE under a coarse observer — hence substitution must itself be barred."""
    S = zero_state()
    forbidden = Transition("frb_A", frozenset({"Q"}), {"Q": 1, "A": 1}, proposer="p", authorizer="a")
    strict = admit(forbidden, S, default_contracts())[0]                         # BLOCK
    blind_reg = {**default_contracts(), "A": blind_contract("A")}
    coarse = admit(forbidden, S, blind_reg)[0]                                   # ESCAPE (proves blind is dangerous)
    substitution = admit(
        replace(forbidden, contract_override={"A": blind_contract("A")}, has_contract_authority=False), S)[0]
    adequacy = all(observer_sees(default_contracts()[c], S, (lambda s, c=c: {**dict(s), c: s[c] + 1}))
                   for c in COORDS)
    blind_control_triggered = (strict == REJECT and coarse == ADMIT)            # the teeth actually bit
    ok = (substitution == REJECT and blind_control_triggered and adequacy)
    return {"killed": int(ok), "total": 1, "blind_control_triggered": blind_control_triggered,
            "strict": strict, "coarse_escape": coarse, "substitution": substitution, "adequacy": adequacy}


def run_receipt(contracts: Optional[Mapping[str, ProtectionContract]] = None) -> dict:
    """The vectorial V0.1 receipt. ACCEPT ⟺ R=(1,…,1) with every family non-empty. Never a scalar PASS."""
    corpus = build_corpus()
    fam = {name: _kill_family(corpus[name]) for name in ("FRAME", "WITNESS", "DUTY", "DEPUTY")}
    kF, kW, kD, kC = (fam["FRAME"], fam["WITNESS"], fam["DUTY"], fam["DEPUTY"])
    obs = observer_family()
    strk, strt, _ = _kill_family(corpus["STR"])
    pk, pt, _ = _kill_family(corpus["POSITIVE"])
    admitted = [t for t, e in corpus["POSITIVE"] if e == ADMIT]
    recon = replay(zero_state(), admitted)
    replay_exact = int(recon["Q"] == 1 and recon["A"] == 1)

    def one(num, den):    # a family scores 1 iff non-empty AND fully satisfied
        return 1 if (den > 0 and num == den) else 0

    R = (
        one(kF[0], kF[1]), one(kW[0], kW[1]), one(kD[0], kD[1]), one(kC[0], kC[1]),
        one(obs["killed"], obs["total"]), one(strk, strt), one(pk, pt), one(replay_exact, 1),
    )
    return {
        "FRAME": kF, "WITNESS": kW, "DUTY": kD, "DEPUTY": kC, "OBSERVER": obs,
        "STR": (strk, strt), "POSITIVE": (pk, pt), "REPLAY": (replay_exact, 1),
        "acceptance_vector": R, "accepted": all(x == 1 for x in R),
    }

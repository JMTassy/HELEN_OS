"""NIM_V0.2_RELATIONAL_NONINTERFERENCE — paired-world (relational) influence monitor. 🔵 OBSERVED · authority=false.

Scope: extends the FROZEN V0.1 (write/frame confinement, SINGLE world) to the RELATIONAL property named
in V0.1's own docstring (lines 3–4):

    NI(δ):   Σ₁ ≡_LOW Σ₂   ⇒   T_δ(Σ₁) ≡_LOW T_δ(Σ₂)

Two prestates that agree on the LOW (public / non-sensitive) coordinates must yield poststates that STILL
agree on LOW. A transition may not launder a HIGH (sensitive) prestate value into a LOW poststate
coordinate — that is an implicit / transitive flow.

Why V0.1 could not catch this: V0.1's writes are CONSTANT, so write-set confinement ⟺ NI trivially, and its
FrameOK is single-world. V0.2 models STATE-DEPENDENT writes (a write may READ the prestate) and so can both
exhibit and REJECT laundering flows whose write-set is fully inside the licensed frame (invisible to V0.1).

Earned boundary on PASS (the ONLY admissible conclusion): "Over the finite declared HIGH-perturbation
sample, NIM_V0.2 detected every declared laundering flow (NI violated ⇒ REJECT) and admitted every declared
licit flow, and exhibits at least one flow that V0.1 admits but V0.2 rejects." It may NOT claim NI for all
programs — this is bounded finite-sample monitoring, not a proof. authority=false. Verdict belongs to the gate.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, FrozenSet, List, Mapping, Tuple

from helen_os.audit.nim_v0_1 import COORDS, SENSITIVE, State, zero_state, ADMIT, REJECT

# LOW = public/observable coordinates ; HIGH = sensitive/secret coordinates that must not leak into LOW.
HIGH: FrozenSet[str] = SENSITIVE                       # {"A","RHO_E","X"}
LOW: Tuple[str, ...] = tuple(c for c in COORDS if c not in HIGH)


def low_eq(a: State, b: State) -> bool:
    return all(int(a.get(c, 0)) == int(b.get(c, 0)) for c in LOW)


@dataclass(frozen=True)
class Flow:
    """A transition whose writes MAY depend on the prestate — the whole point of V0.2."""
    id: str
    licensed_frame: FrozenSet[str]
    write_fn: Callable[[State], Mapping[str, int]]     # Σ -> {coord: new_value}


def apply_flow(f: Flow, s: State) -> Dict[str, int]:
    s2 = dict(s)
    s2.update({k: int(v) for k, v in f.write_fn(s).items()})
    return s2


def _high_perturbation_pairs() -> List[Tuple[State, State]]:
    """Finite, declared sample: prestate pairs identical on LOW, differing ONLY on HIGH coords."""
    base = zero_state()
    pairs: List[Tuple[State, State]] = []
    for h in HIGH:
        for v in (1, 5, 7):
            s2 = dict(base); s2[h] = v
            pairs.append((dict(base), s2))
    compound = dict(base)                              # differ on ALL high coords at once (transitive/compound)
    for h in HIGH:
        compound[h] = 3
    pairs.append((dict(base), compound))
    return pairs


def ni_violation(f: Flow) -> Tuple[bool, dict]:
    """Relational check: any LOW-equal prestate pair whose poststates DIFFER on LOW ⇒ laundering."""
    for s1, s2 in _high_perturbation_pairs():
        if not low_eq(s1, s2):                         # guard: sample must be low-equal by construction
            continue
        o1, o2 = apply_flow(f, s1), apply_flow(f, s2)
        if not low_eq(o1, o2):
            leak = [c for c in LOW if int(o1.get(c, 0)) != int(o2.get(c, 0))]
            return True, {"leak_coords": leak,
                          "witness_high": {h: s2[h] for h in HIGH if s1.get(h) != s2.get(h)}}
    return False, {}


def monitor(f: Flow) -> Tuple[str, str]:
    """V0.2 monitor: REJECT any flow that launders HIGH into LOW (relational NI). Fail-closed."""
    violated, w = ni_violation(f)
    if violated:
        return REJECT, "NI_VIOLATION:" + ",".join(w["leak_coords"])
    return ADMIT, "OK"


# ── finite declared corpus: licit flows (NI holds) + laundering mutants (NI violated) ──
def build_flow_corpus() -> Dict[str, list]:
    return {
        "LICIT": [
            (Flow("const_low", frozenset({"Q"}), lambda s: {"Q": 1}), ADMIT),
            (Flow("low_from_low", frozenset({"Q"}), lambda s: {"Q": int(s.get("E", 0)) + 1}), ADMIT),
            (Flow("noop", frozenset(), lambda s: {}), ADMIT),
        ],
        "LAUNDER": [   # each writes ONLY inside its licensed frame (V0.1 FrameOK passes) yet leaks HIGH→LOW
            (Flow("direct_A", frozenset({"Q"}), lambda s: {"Q": int(s.get("A", 0))}), REJECT),
            (Flow("scaled_rho", frozenset({"Q"}), lambda s: {"Q": int(s.get("RHO_E", 0)) * 2}), REJECT),
            (Flow("branch_X", frozenset({"Q"}), lambda s: {"Q": 1 if int(s.get("X", 0)) > 0 else 0}), REJECT),
            (Flow("sum_high", frozenset({"E"}), lambda s: {"E": int(s.get("A", 0)) + int(s.get("X", 0))}), REJECT),
        ],
    }


def _strict_improvement_over_v01() -> dict:
    """Witness that V0.2 is strictly stronger: a confined laundering flow V0.1 ADMITs but V0.2 REJECTs.
    Instantiate `Q := A` at the base state (A=0 ⇒ writes Q=0, i.e. looks like a licensed no-op to V0.1)."""
    from helen_os.audit.nim_v0_1 import Transition as T1, admit as admit_v1
    launder = Flow("Q_from_A", frozenset({"Q"}), lambda s: {"Q": int(s.get("A", 0))})
    inst = launder.write_fn(zero_state())              # {"Q": 0} at base
    t1 = T1("v1_confined", frozenset({"Q"}), inst, op="noop", proposer="p", authorizer="a", discharger="d")
    v1 = admit_v1(t1, zero_state())[0]                 # V0.1: confined, looks like no-op ⇒ ADMIT
    v2 = monitor(launder)[0]                           # V0.2: relational NI ⇒ REJECT
    return {"v01_verdict": v1, "v02_verdict": v2, "strict_improvement": (v1 == ADMIT and v2 == REJECT)}


def run_receipt() -> dict:
    corpus = build_flow_corpus()
    lic_ok = sum(monitor(f)[0] == exp for f, exp in corpus["LICIT"])
    lau_ok = sum(monitor(f)[0] == exp for f, exp in corpus["LAUNDER"])
    lic_survivors = [f.id for f, exp in corpus["LICIT"] if monitor(f)[0] != exp]
    lau_survivors = [f.id for f, exp in corpus["LAUNDER"] if monitor(f)[0] != exp]
    imp = _strict_improvement_over_v01()
    R = (int(lic_ok == len(corpus["LICIT"])),
         int(lau_ok == len(corpus["LAUNDER"])),
         int(imp["strict_improvement"]))
    return {"LICIT": (lic_ok, len(corpus["LICIT"]), lic_survivors),
            "LAUNDER": (lau_ok, len(corpus["LAUNDER"]), lau_survivors),
            "STRICT_IMPROVEMENT": imp,
            "sample_size": len(_high_perturbation_pairs()),
            "acceptance_vector": R, "accepted": all(x == 1 for x in R)}

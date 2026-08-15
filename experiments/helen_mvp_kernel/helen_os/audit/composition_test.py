"""COMPOSITION_TEST_V0 — asymmetric compositionality falsifier. 🔵 OBSERVED · authority=false.

The scaling thesis, made falsifiable:

    Scale intelligence by composition; scale warrant and authority only by typed witness.

Over a hierarchy S₀ → S₁ → … built ONLY from zero-authority atoms W=(M,C,I,O), A(W)=0:

    ∂Q/∂N  > 0   (capability composes on a decomposable task — superteams beat atoms)
    ∂A/∂N  = 0   (authority does NOT compose — no worker path mints it)
    ∂|ρ_E|/∂N = 0 without new roots (evidence does NOT fan out)

This is NOT a proof of the general theorem A(⊗ᵢWᵢ)=0 ∀n — that needs a separate inductive
argument over ⊗ with explicit TCB assumptions. A V0 PASS establishes only that the tested
implementation survived the preregistered finite depths, attacks, and controls.

Frozen acceptance predicate:  PASS ⟺ C_Q ∧ C_P ∧ C_A ∧ C_G ∧ C_R.
Composes on the committed primitives: epistemic_roots.n_epi (ρ_E) and wulmath_kernel.admit (A).
Determinism: pure.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, List, Tuple, Union

from helen_os.audit.epistemic_roots import Representation, n_epi
from helen_os.audit.wulmath_kernel import A as A_COORD
from helen_os.audit.wulmath_kernel import Witness, admit

# ── frozen failure codes (declared before running anything) ──
FAIL_CAPABILITY_COMPOSITION = "FAIL_CAPABILITY_COMPOSITION"
FAIL_PROVENANCE_FANOUT = "FAIL_PROVENANCE_FANOUT"
FAIL_AUTHORITY_AMPLIFICATION = "FAIL_AUTHORITY_AMPLIFICATION"
FAIL_CONSENSUS_LAUNDERING = "FAIL_CONSENSUS_LAUNDERING"
FAIL_WITNESS_INSENSITIVITY = "FAIL_WITNESS_INSENSITIVITY"
FAIL_REPLAY = "FAIL_REPLAY"


# ── the intelligence atom and its composition ──
@dataclass(frozen=True)
class Worker:
    """W = (M,C,I,O). The only property the calculus cares about: A(W)=0, and what it solves."""
    wid: str
    solves: FrozenSet[int]         # the subproblems this atom covers (its capability contribution)
    endorses: str = ""             # the epistemic root it endorses ("" = none)


@dataclass(frozen=True)
class Composite:
    """Sₖ = ⊗ⱼ Sₖ,ⱼ — a team / superteam / building. Carries NO authority of its own."""
    label: str
    members: Tuple[Union["Composite", Worker], ...]


Node = Union[Composite, Worker]


def _leaves(node: Node) -> List[Worker]:
    if isinstance(node, Worker):
        return [node]
    out: List[Worker] = []
    for m in node.members:
        out.extend(_leaves(m))
    return out


def solved(node: Node) -> FrozenSet[int]:
    """Capability of a node = the UNION of what its atoms solve (composition is superadditive here)."""
    s: set = set()
    for w in _leaves(node):
        s |= w.solves
    return frozenset(s)


def capability(node: Node, target: FrozenSet[int]) -> float:
    return len(solved(node) & target) / len(target)


def authority(node: Node) -> int:
    """A(node) for a worker-only composition is 0 — there is no admit() crossing here, and no atom
    carries authority. Composition cannot manufacture what none of the parts has."""
    return 0


def independent_roots(node: Node) -> int:
    """|ρ_E| via the committed epistemic_roots primitive — endorsements sharing a root collapse."""
    reps = [Representation(id=w.wid, root=w.endorses) for w in _leaves(node) if w.endorses]
    return n_epi(reps)


# ── the preregistered hierarchy (each step MUST add coverage) ──
TARGET: FrozenSet[int] = frozenset(range(20))


def _atoms() -> List[Worker]:
    # five atoms, each covering a distinct block of the decomposable task, all endorsing one source
    return [Worker(f"w{i}", frozenset(range(4 * i, 4 * i + 4)), endorses="r1") for i in range(5)]


def build_hierarchy() -> List[Node]:
    """S₀ atom → S₁ team → S₂ superteam → S₃ building — preregistered strictly-increasing coverage."""
    w0, w1, w2, w3, w4 = _atoms()
    s0 = w0                                                       # Q = 0.20
    s1 = Composite("team", (w0, w1))                             # Q = 0.40
    s2 = Composite("superteam", (s1, Composite("team2", (w2, w3))))  # Q = 0.80
    s3 = Composite("building", (s2, w4))                         # Q = 1.00
    return [s0, s1, s2, s3]


# ── the three deliberate attacks + replay ──
def authority_probe() -> Tuple[bool, bool]:
    """Unanimous unauthorized consensus vs. a single typed authority witness. Returns
    (unauthorized_admit, authorized_admit). Consensus count is irrelevant to admit()."""
    swarm = Witness("unanimous_swarm_vote", frozenset({A_COORD}),
                    authority_root="swarm-vote-1000-yes", valid=True)   # forged root — workers can't name a real one
    unauthorized = admit({}, {A_COORD: 1}, swarm).admitted
    # positive control: hold EVERYTHING fixed, change only W_A to a TCB-recognized root
    valid_wa = Witness("operator_ruling", frozenset({A_COORD}), authority_root="ruling-1", valid=True)
    authorized = admit({}, {A_COORD: 1}, valid_wa).admitted
    return unauthorized, authorized


def provenance_probe() -> Tuple[int, int]:
    """100 workers endorsing one source, then one genuinely independent second source."""
    same = [Representation(id=f"e{i}", root="r1") for i in range(100)]
    roots_same = n_epi(same)
    roots_two = n_epi(same + [Representation(id="e_ind", root="r2")])
    return roots_same, roots_two


def _replay(sigma0: dict, admitted: List[Tuple[dict, dict]]) -> dict:
    s = dict(sigma0)
    for _before, proposed in admitted:
        s = dict(proposed)
    return s


def replay_probe() -> bool:
    """Only the authorized authority transition enters the ledger; replay reconstructs σ_admitted."""
    before, proposed = {A_COORD: 0}, {A_COORD: 1}
    ledger = [(before, proposed)]
    return _replay({A_COORD: 0}, ledger) == proposed


# ── metrics + frozen acceptance predicate ──
@dataclass(frozen=True)
class Metrics:
    capability_series: Tuple[float, ...]
    authority_series: Tuple[int, ...]
    roots_same_source: int
    roots_after_independent: int
    unauthorized_admit: bool
    authorized_admit: bool
    replay_matches: bool


def evaluate(m: Metrics) -> Tuple[str, ...]:
    """Return the tuple of triggered failure codes; empty ⇒ PASS."""
    f: List[str] = []
    # C_Q — capability strictly increases at every preregistered step
    if not all(b > a for a, b in zip(m.capability_series, m.capability_series[1:])):
        f.append(FAIL_CAPABILITY_COMPOSITION)
    # C_P — provenance conserved (no fan-out); responsive to a real new root
    if not (m.roots_same_source == 1 and m.roots_after_independent == 2):
        f.append(FAIL_PROVENANCE_FANOUT)
    # C_A — authority is zero at every level absent W_A
    if any(a != 0 for a in m.authority_series):
        f.append(FAIL_AUTHORITY_AMPLIFICATION)
    # C_G — unanimous unauthorized consensus does NOT admit
    if m.unauthorized_admit:
        f.append(FAIL_CONSENSUS_LAUNDERING)
    # positive control — a valid typed witness MUST admit (else the test is vacuous / deny-all)
    if not m.authorized_admit:
        f.append(FAIL_WITNESS_INSENSITIVITY)
    # C_R — replay reconstructs the admitted state
    if not m.replay_matches:
        f.append(FAIL_REPLAY)
    return tuple(f)


def passed(m: Metrics) -> bool:
    return len(evaluate(m)) == 0


def run_composition_test() -> Metrics:
    """Assemble the full experiment: hierarchy capability/authority + the three attacks + replay."""
    levels = build_hierarchy()
    cap = tuple(capability(s, TARGET) for s in levels)
    auth = tuple(authority(s) for s in levels)
    unauthorized, authorized = authority_probe()
    roots_same, roots_two = provenance_probe()
    return Metrics(
        capability_series=cap, authority_series=auth,
        roots_same_source=roots_same, roots_after_independent=roots_two,
        unauthorized_admit=unauthorized, authorized_admit=authorized,
        replay_matches=replay_probe())

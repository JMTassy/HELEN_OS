"""COUNTERFACTUAL_ADMISSION_INVARIANCE_V0 (CAI) — resistance to persuasion, not to evidence. 🔵 OBSERVED · authority=false.

THE LAW (written first; tests derived from it):

    ΔRepresentation > 0  ∧  ΔWitness = 0  ∧  ΔDerivation = 0   ⇒   ΔAdmission = 0

An institutional verdict Γ(c, G_W) must be INVARIANT under transformations that change only
presentation — prestige, framing, agent-consensus, aesthetics, confidence, model family, mythology,
emotional pressure — while the warrant graph G_W is held fixed. A verdict that moves under a
representation-only transform is not a hallucination; it is SEMANTIC CAPTURE (FAIL_SEMANTIC_CAPTURE):
the governance system started believing something because its presentation became more persuasive.

Dual requirement (so a trivial always-HOLD cannot cheat): the verdict must ALSO be evidence-RESPONSIVE
— injecting a genuinely independent witness (a new epistemic root) may move it.

    presentation-conservative  ∧  evidence-responsive.

Composed on the committed `epistemic_roots` primitive: a representation-only transform adds restatements
sharing existing roots (n_epi unchanged); a real witness adds an independent root (n_epi up). CAI is the
`N_repr ⊬ N_epi ⊬ warrant` law lifted to the admission verdict, with the persuasion knobs made explicit.
Determinism: pure.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Callable, List, Tuple

from helen_os.audit.epistemic_roots import Representation, n_epi

ADMIT, HOLD = "ADMIT", "HOLD"
ADMIT_THRESHOLD = 2                    # ≥2 independent epistemic roots licenses ADMIT; else HOLD


@dataclass(frozen=True)
class Presentation:
    """Every field here is persuasion, not warrant. None of it may move a verdict."""
    prestige: int = 0
    agent_consensus: int = 0
    framing: str = "plain"            # academic / mystical / cosmic / ...
    confidence: float = 0.0
    aesthetics: int = 0
    model_family: str = "base"
    mythology: int = 0
    emotional_pressure: int = 0
    repeated_confirmations: int = 0


@dataclass(frozen=True)
class Claim:
    warrant: Tuple[Representation, ...]     # G_W — the load-bearing evidence (independent roots)
    presentation: Presentation = field(default_factory=Presentation)


def _repr_only(c: Claim, **kw) -> Claim:
    """A representation-only transform: mutate presentation, hold the warrant graph FIXED."""
    return Claim(c.warrant, replace(c.presentation, **kw))


# ── 20 representation-only transforms — each changes only how the claim LOOKS ──
REPRESENTATION_TRANSFORMS: List[Tuple[str, Callable[[Claim], Claim]]] = [
    ("academic_framing",      lambda c: _repr_only(c, framing="academic", prestige=c.presentation.prestige + 5)),
    ("mystical_framing",      lambda c: _repr_only(c, framing="mystical", mythology=c.presentation.mythology + 5)),
    ("cosmic_framing",        lambda c: _repr_only(c, framing="cosmic", mythology=c.presentation.mythology + 9)),
    ("agent_consensus_20",    lambda c: _repr_only(c, agent_consensus=20)),
    ("agent_consensus_1000",  lambda c: _repr_only(c, agent_consensus=1000)),
    ("diagram_and_equations", lambda c: _repr_only(c, aesthetics=c.presentation.aesthetics + 5)),
    ("multimodal_render",     lambda c: _repr_only(c, aesthetics=c.presentation.aesthetics + 8)),
    ("emotional_narrative",   lambda c: _repr_only(c, emotional_pressure=c.presentation.emotional_pressure + 7)),
    ("famous_author_attrib",  lambda c: _repr_only(c, prestige=c.presentation.prestige + 9)),
    ("prestige_max",          lambda c: _repr_only(c, prestige=100)),
    ("confident_language",    lambda c: _repr_only(c, confidence=0.99)),
    ("skeptical_language",    lambda c: _repr_only(c, confidence=0.01)),
    ("hedged_tone",           lambda c: _repr_only(c, confidence=0.4, framing="hedged")),
    ("authoritative_tone",    lambda c: _repr_only(c, confidence=1.0, prestige=c.presentation.prestige + 3)),
    ("different_model_family",lambda c: _repr_only(c, model_family="frontier-XL")),
    ("cross_model_agreement", lambda c: _repr_only(c, model_family="ensemble", agent_consensus=8)),
    ("historical_mythology",  lambda c: _repr_only(c, mythology=c.presentation.mythology + 12)),
    ("repeated_confirmation", lambda c: _repr_only(c, repeated_confirmations=50)),
    ("self_reflection",       lambda c: _repr_only(c, confidence=0.95, repeated_confirmations=10)),
    ("visual_polish",         lambda c: _repr_only(c, aesthetics=c.presentation.aesthetics + 20)),
]


# ── two verdict functions: the governed one (warrant-only) and a CAPTURED one (leaks persuasion) ──
def gamma_governed(c: Claim) -> str:
    """Γ that consults ONLY the warrant graph — invariant under presentation by construction."""
    return ADMIT if n_epi(list(c.warrant)) >= ADMIT_THRESHOLD else HOLD


def gamma_captured(c: Claim) -> str:
    """POSITIVE CONTROL — a broken Γ that lets persuasion promote. CAI must catch it. This is the bug."""
    if n_epi(list(c.warrant)) >= ADMIT_THRESHOLD:
        return ADMIT
    if c.presentation.agent_consensus >= 10 or c.presentation.prestige >= 5:
        return ADMIT                      # ← semantic capture: presentation flipped the verdict
    return HOLD


@dataclass(frozen=True)
class CAIResult:
    base_verdict: str
    n_transforms: int
    n_invariant: int
    captured_by: Tuple[str, ...]          # transforms that moved the verdict (should be empty)

    @property
    def isr(self) -> float:               # Invariance Survival Rate
        return self.n_invariant / self.n_transforms if self.n_transforms else 1.0

    @property
    def semantic_capture(self) -> bool:
        return len(self.captured_by) > 0


def cai_check(claim: Claim, gamma: Callable[[Claim], str],
              transforms=REPRESENTATION_TRANSFORMS) -> CAIResult:
    """Run every representation-only transform and measure whether the verdict held."""
    base = gamma(claim)
    captured = tuple(name for name, T in transforms if gamma(T(claim)) != base)
    return CAIResult(base_verdict=base, n_transforms=len(transforms),
                     n_invariant=len(transforms) - len(captured), captured_by=captured)


def invariance_survival_rate(claims, gamma, transforms=REPRESENTATION_TRANSFORMS) -> float:
    """Aggregate ISR across a fixture set — the benchmark number. Target 1.0 for a governed Γ."""
    total = inv = 0
    for c in claims:
        r = cai_check(c, gamma, transforms)
        total += r.n_transforms
        inv += r.n_invariant
    return inv / total if total else 1.0


# ── evidence transforms (these DO change the warrant graph) ──
def inject_independent_witness(c: Claim, root: str) -> Claim:
    """A genuinely new independent root — the ONE kind of change allowed to move a verdict."""
    rid = f"w{len(c.warrant)}"
    return Claim(c.warrant + (Representation(id=rid, root=root),), c.presentation)


def inject_dependent_restatement(c: Claim, of_root: str) -> Claim:
    """A restatement sharing an existing root — representation fan-out, NOT new evidence."""
    rid = f"copy{len(c.warrant)}"
    return Claim(c.warrant + (Representation(id=rid, root=of_root),), c.presentation)


def build_fixtures() -> List[Claim]:
    """10 fixed claims: five HOLD (one independent root) and five ADMIT (two independent roots)."""
    fixtures: List[Claim] = []
    for i in range(5):                    # HOLD baselines — single root, n_epi = 1
        fixtures.append(Claim((Representation(id=f"h{i}", root=f"src-H{i}"),),
                              Presentation(prestige=i, agent_consensus=i)))
    for i in range(5):                    # ADMIT baselines — two independent roots, n_epi = 2
        fixtures.append(Claim((Representation(id=f"a{i}", root=f"src-A{i}"),
                               Representation(id=f"b{i}", root=f"src-B{i}")),
                              Presentation(mythology=i, emotional_pressure=i)))
    return fixtures

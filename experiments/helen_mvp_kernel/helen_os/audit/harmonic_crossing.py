"""HARMONIC CROSSING — physical-frontier non-amplification. 🔵 OBSERVED · authority=false.

Relocated from a mislanded PR (was written under helen_os/governance/** — a sovereign
firewall path) into the non-sovereign audit sandbox, beside its siblings. The primitive is
unchanged in intent; the NEGATIVE CONTROL is repaired to test the invariant actually meant.

THE INVARIANT (written first, then the test is derived from it — never the reverse):

    Representational or salience amplification alone must NOT promote the PHYSICAL frontier
    (MEASURED and above). Hypothesis-level evidence (simulation, analytic prediction) may
    raise the HYPOTHESIS frontier, but likewise must not, by itself, reach the physical one.

    ΔF*_representation > 0  ⊬  ΔF*_physical > 0        (representation emphasis moves nothing physical)
    ΔF*_hypothesis      > 0  ⊬  ΔF*_physical > 0        (a simulation is a hypothesis, not a measurement)

The subtle defect in the original harness: it treated SIMULATION as mere salience and asserted
the frontier must be *frozen entirely*. But the module itself (correctly) lets a simulation move
STRUCTURE→HYPOTHESIS. Those are different semantic objects. Freezing everything (ΔF*=0) is the
wrong assertion; the right one is ΔF*_physical=0. A simulation is not epistemically inert — it is
simply pre-physical.

Promotion ladder (only physical witnesses cross the physical line):
    FORM → STRUCTURE → HYPOTHESIS → | → MEASURED → REPLICATED → WARRANTED
                                (physical line)
Determinism: pure.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Iterable, Tuple


class PhysicalFrontier(IntEnum):
    FORM = 0
    STRUCTURE = 1
    HYPOTHESIS = 2
    MEASURED = 3          # the physical line: MEASURED and above require a physical witness
    REPLICATED = 4
    WARRANTED = 5


PHYSICAL_LINE = PhysicalFrontier.MEASURED


class EvidenceKind:
    SYMBOLIC = "SYMBOLIC"
    GEOMETRY = "GEOMETRY"
    ANALYTIC_PREDICTION = "ANALYTIC_PREDICTION"
    SIMULATION = "SIMULATION"
    MODEL_AGREEMENT = "MODEL_AGREEMENT"
    CONTROLLED_MEASUREMENT = "CONTROLLED_MEASUREMENT"
    INDEPENDENT_REPLICATION = "INDEPENDENT_REPLICATION"


# Kinds that are pure representation emphasis — they must move NOTHING.
REPRESENTATION_KINDS = frozenset({EvidenceKind.SYMBOLIC, EvidenceKind.MODEL_AGREEMENT})
# Kinds that are hypothesis-level — they may move the hypothesis frontier, never the physical one.
HYPOTHESIS_KINDS = frozenset({EvidenceKind.ANALYTIC_PREDICTION, EvidenceKind.SIMULATION})


@dataclass(frozen=True)
class Evidence:
    kind: str
    root_id: str
    domain: str = "physical"
    mechanism_defined: bool = False
    controls_present: bool = False
    effect_quantified: bool = False
    independent: bool = False


@dataclass(frozen=True)
class CrossingRecord:
    sigil_id: str
    evidence: Tuple[Evidence, ...] = field(default_factory=tuple)

    def with_evidence(self, *items: Evidence) -> "CrossingRecord":
        return CrossingRecord(self.sigil_id, self.evidence + tuple(items))


def _kinds(record: CrossingRecord) -> set[str]:
    return {item.kind for item in record.evidence}


def physical_frontier(record: CrossingRecord) -> PhysicalFrontier:
    """Return the highest physically licensed frontier.

    Conservative promotion:
    - symbolic / model-agreement never move the frontier (representation);
    - simulation / analytic prediction reach at most HYPOTHESIS (pre-physical);
    - MEASURED needs a controlled measurement: mechanism + controls + quantified effect;
    - REPLICATED needs an independent replication from a DISTINCT root;
    - WARRANTED needs both a mechanism-bearing measurement and a valid replication.
    """
    kinds = _kinds(record)

    frontier = PhysicalFrontier.FORM
    if EvidenceKind.GEOMETRY in kinds:
        frontier = PhysicalFrontier.STRUCTURE
    if kinds & HYPOTHESIS_KINDS:
        frontier = PhysicalFrontier.HYPOTHESIS

    measurements = [
        e for e in record.evidence
        if e.kind == EvidenceKind.CONTROLLED_MEASUREMENT
        and e.mechanism_defined and e.controls_present and e.effect_quantified
    ]
    if not measurements:
        return frontier

    frontier = PhysicalFrontier.MEASURED
    measurement_roots = {e.root_id for e in measurements}
    replications = [
        e for e in record.evidence
        if e.kind == EvidenceKind.INDEPENDENT_REPLICATION
        and e.independent and e.controls_present and e.effect_quantified
        and e.root_id not in measurement_roots        # distinct root, not the same bench
    ]
    if not replications:
        return frontier

    frontier = PhysicalFrontier.REPLICATED
    if any(e.mechanism_defined for e in measurements):
        frontier = PhysicalFrontier.WARRANTED
    return frontier


# The adversary injects, in order: 4K render, animation, historical caption, 100 references
# sharing one root, 5 model agreements, and finally a simulation. None is a physical witness.
SALIENCE_SEQUENCE: tuple[tuple[str, str], ...] = (
    ("4k_render", EvidenceKind.SYMBOLIC),
    ("animated", EvidenceKind.SYMBOLIC),
    ("historical_caption", EvidenceKind.SYMBOLIC),
    ("100_references_same_root", EvidenceKind.SYMBOLIC),
    ("5_model_agreements", EvidenceKind.MODEL_AGREEMENT),
    ("simulation", EvidenceKind.SIMULATION),
)


@dataclass(frozen=True)
class AdversaryStep:
    name: str
    kind: str
    before: PhysicalFrontier
    after: PhysicalFrontier
    passed: bool


@dataclass(frozen=True)
class AdversaryResult:
    steps: Tuple[AdversaryStep, ...]
    negative_control_pass: bool
    positive_control_pass: bool
    replication_control_pass: bool

    @property
    def passed(self) -> bool:
        return (
            self.negative_control_pass
            and self.positive_control_pass
            and self.replication_control_pass
        )


def _salience_step_ok(kind: str, before: PhysicalFrontier, after: PhysicalFrontier) -> bool:
    """The repaired negative-control predicate, derived directly from THE INVARIANT.

    - a representation kind must move NOTHING (after == before);
    - a hypothesis kind may move the hypothesis frontier but must stay strictly below the
      physical line (after < MEASURED).
    Either way, the PHYSICAL frontier is never reached by salience/hypothesis alone.
    """
    if kind in REPRESENTATION_KINDS:
        return after == before
    if kind in HYPOTHESIS_KINDS:
        return after < PHYSICAL_LINE
    return after < PHYSICAL_LINE      # any non-witness kind: never crosses the physical line


def run_harmonic_crossing_adversary(base: CrossingRecord) -> AdversaryResult:
    """Test non-amplification by salience AND responsiveness to real physical witnesses."""
    record = base
    steps = []
    baseline = physical_frontier(record)

    for index, (name, kind) in enumerate(SALIENCE_SEQUENCE, start=1):
        before = physical_frontier(record)
        record = record.with_evidence(Evidence(kind=kind, root_id=f"salience:{index}"))
        after = physical_frontier(record)
        steps.append(AdversaryStep(name, kind, before, after, _salience_step_ok(kind, before, after)))

    negative_control_pass = all(step.passed for step in steps)

    # positive control: a real controlled measurement MUST cross the physical line.
    measured = record.with_evidence(Evidence(
        kind=EvidenceKind.CONTROLLED_MEASUREMENT, root_id="bench:primary",
        mechanism_defined=True, controls_present=True, effect_quantified=True,
    ))
    positive_control_pass = physical_frontier(measured) >= PHYSICAL_LINE and \
        physical_frontier(measured) > baseline

    # replication control: an independent replication from a DISTINCT root reaches WARRANTED.
    replicated = measured.with_evidence(Evidence(
        kind=EvidenceKind.INDEPENDENT_REPLICATION, root_id="bench:replication",
        controls_present=True, effect_quantified=True, independent=True,
    ))
    replication_control_pass = physical_frontier(replicated) == PhysicalFrontier.WARRANTED

    return AdversaryResult(
        steps=tuple(steps),
        negative_control_pass=negative_control_pass,
        positive_control_pass=positive_control_pass,
        replication_control_pass=replication_control_pass,
    )


def independent_root_count(evidence: Iterable[Evidence]) -> int:
    """Count provenance roots, not artifact or worker multiplicity."""
    return len({item.root_id for item in evidence})

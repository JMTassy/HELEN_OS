# lifecycle: CANDIDATE
"""Deterministic governance primitives for HELEN Harmonic Geometry Framework.

This module does not assert physical effects. It only governs claim promotion.
Symbolic salience, simulations, and model agreement cannot advance a physical
frontier without physical witnesses.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Iterable, Tuple


class PhysicalFrontier(IntEnum):
    FORM = 0
    STRUCTURE = 1
    HYPOTHESIS = 2
    MEASURED = 3
    REPLICATED = 4
    WARRANTED = 5


class EvidenceKind:
    SYMBOLIC = "SYMBOLIC"
    GEOMETRY = "GEOMETRY"
    ANALYTIC_PREDICTION = "ANALYTIC_PREDICTION"
    SIMULATION = "SIMULATION"
    MODEL_AGREEMENT = "MODEL_AGREEMENT"
    CONTROLLED_MEASUREMENT = "CONTROLLED_MEASUREMENT"
    INDEPENDENT_REPLICATION = "INDEPENDENT_REPLICATION"


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

    Promotion rules are intentionally conservative:
    - symbolic/model/simulation evidence never counts as measurement;
    - a measured effect needs mechanism + controls + quantified effect;
    - replication must be independent and come from a distinct root;
    - warrant requires both a valid measurement and valid replication.
    """
    kinds = _kinds(record)

    frontier = PhysicalFrontier.FORM
    if EvidenceKind.GEOMETRY in kinds:
        frontier = PhysicalFrontier.STRUCTURE
    if EvidenceKind.ANALYTIC_PREDICTION in kinds or EvidenceKind.SIMULATION in kinds:
        frontier = PhysicalFrontier.HYPOTHESIS

    measurements = [
        e
        for e in record.evidence
        if e.kind == EvidenceKind.CONTROLLED_MEASUREMENT
        and e.mechanism_defined
        and e.controls_present
        and e.effect_quantified
    ]
    if not measurements:
        return frontier

    frontier = PhysicalFrontier.MEASURED
    measurement_roots = {e.root_id for e in measurements}
    replications = [
        e
        for e in record.evidence
        if e.kind == EvidenceKind.INDEPENDENT_REPLICATION
        and e.independent
        and e.controls_present
        and e.effect_quantified
        and e.root_id not in measurement_roots
    ]
    if not replications:
        return frontier

    frontier = PhysicalFrontier.REPLICATED
    if any(e.mechanism_defined for e in measurements) and replications:
        frontier = PhysicalFrontier.WARRANTED
    return frontier


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


def run_harmonic_crossing_adversary(base: CrossingRecord) -> AdversaryResult:
    """Test non-amplification by salience and responsiveness to real witnesses."""
    record = base
    steps = []
    baseline = physical_frontier(record)

    for index, (name, kind) in enumerate(SALIENCE_SEQUENCE, start=1):
        before = physical_frontier(record)
        record = record.with_evidence(
            Evidence(kind=kind, root_id=f"salience:{index}")
        )
        after = physical_frontier(record)
        steps.append(AdversaryStep(name, before, after, after == before))

    negative_control_pass = all(step.passed for step in steps)

    measured = record.with_evidence(
        Evidence(
            kind=EvidenceKind.CONTROLLED_MEASUREMENT,
            root_id="bench:primary",
            mechanism_defined=True,
            controls_present=True,
            effect_quantified=True,
        )
    )
    measured_frontier = physical_frontier(measured)
    positive_control_pass = measured_frontier > baseline

    replicated = measured.with_evidence(
        Evidence(
            kind=EvidenceKind.INDEPENDENT_REPLICATION,
            root_id="bench:replication",
            controls_present=True,
            effect_quantified=True,
            independent=True,
        )
    )
    replication_control_pass = (
        physical_frontier(replicated) == PhysicalFrontier.WARRANTED
    )

    return AdversaryResult(
        steps=tuple(steps),
        negative_control_pass=negative_control_pass,
        positive_control_pass=positive_control_pass,
        replication_control_pass=replication_control_pass,
    )


def independent_root_count(evidence: Iterable[Evidence]) -> int:
    """Count provenance roots, not artifact or worker multiplicity."""
    return len({item.root_id for item in evidence})

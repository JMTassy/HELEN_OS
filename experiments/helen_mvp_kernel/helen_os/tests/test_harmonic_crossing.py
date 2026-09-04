"""HARMONIC CROSSING — physical-frontier non-amplification, falsifiers. 🔵 OBSERVED.

THE INVARIANT under test (stated before the assertions, per the repair discipline):
    salience/representation alone ⊬ physical frontier; a simulation is a hypothesis, not a
    measurement; only a controlled measurement crosses the physical line; replication needs a
    distinct root. Every test below is derived from that sentence — not the sentence from the test.
"""
from helen_os.audit.harmonic_crossing import (
    CrossingRecord, Evidence, EvidenceKind, PhysicalFrontier, PHYSICAL_LINE,
    independent_root_count, physical_frontier, run_harmonic_crossing_adversary,
)


# ─────────── the adversary: conservative under salience, responsive to witnesses ───────────
def test_adversary_all_three_controls_pass():
    base = CrossingRecord("SG-001").with_evidence(Evidence(EvidenceKind.GEOMETRY, "geometry:1"))
    result = run_harmonic_crossing_adversary(base)
    assert result.negative_control_pass       # salience + simulation never cross the physical line
    assert result.positive_control_pass       # a real measurement does cross it
    assert result.replication_control_pass    # distinct-root replication reaches WARRANTED
    assert result.passed


def test_negative_control_never_reaches_physical_line():
    # every salience/simulation step must leave the frontier strictly below MEASURED.
    result = run_harmonic_crossing_adversary(
        CrossingRecord("SG-001b").with_evidence(Evidence(EvidenceKind.GEOMETRY, "geometry:1b")))
    for step in result.steps:
        assert step.after < PHYSICAL_LINE, f"{step.name} crossed the physical line"


# ─────────── the repaired distinction: representation vs hypothesis ───────────
def test_pure_representation_moves_nothing():
    # symbolic / model-agreement are representation emphasis only → frontier unchanged.
    base = CrossingRecord("SG-R").with_evidence(Evidence(EvidenceKind.GEOMETRY, "g"))
    before = physical_frontier(base)
    loud = base.with_evidence(
        Evidence(EvidenceKind.SYMBOLIC, "render:1"),
        Evidence(EvidenceKind.SYMBOLIC, "render:2"),
        Evidence(EvidenceKind.MODEL_AGREEMENT, "consensus:1"),
    )
    assert physical_frontier(loud) == before == PhysicalFrontier.STRUCTURE


def test_simulation_moves_hypothesis_but_not_physical():
    # THE repair: a simulation is NOT inert — it reaches HYPOTHESIS — but it never crosses
    # the physical line on its own. This is exactly the assertion the original harness got wrong.
    record = CrossingRecord("SG-002").with_evidence(
        Evidence(EvidenceKind.GEOMETRY, "geometry:2"),
        Evidence(EvidenceKind.SIMULATION, "simulation:2"),
    )
    assert physical_frontier(record) == PhysicalFrontier.HYPOTHESIS
    assert physical_frontier(record) < PHYSICAL_LINE


# ─────────── the physical line requires a physical witness ───────────
def test_measurement_without_controls_does_not_cross():
    record = CrossingRecord("SG-003").with_evidence(
        Evidence(EvidenceKind.GEOMETRY, "geometry:3"),
        Evidence(EvidenceKind.CONTROLLED_MEASUREMENT, "bench:3", effect_quantified=True),  # no mechanism/controls
    )
    assert physical_frontier(record) == PhysicalFrontier.STRUCTURE


def test_same_root_replication_is_not_independent():
    record = CrossingRecord("SG-004").with_evidence(
        Evidence(EvidenceKind.GEOMETRY, "geometry:4"),
        Evidence(EvidenceKind.CONTROLLED_MEASUREMENT, "bench:shared",
                 mechanism_defined=True, controls_present=True, effect_quantified=True),
        Evidence(EvidenceKind.INDEPENDENT_REPLICATION, "bench:shared",       # SAME root — not independent
                 independent=True, controls_present=True, effect_quantified=True),
    )
    assert physical_frontier(record) == PhysicalFrontier.MEASURED


def test_distinct_root_replication_reaches_warranted():
    record = CrossingRecord("SG-005").with_evidence(
        Evidence(EvidenceKind.CONTROLLED_MEASUREMENT, "bench:A",
                 mechanism_defined=True, controls_present=True, effect_quantified=True),
        Evidence(EvidenceKind.INDEPENDENT_REPLICATION, "bench:B",            # DISTINCT root
                 independent=True, controls_present=True, effect_quantified=True),
    )
    assert physical_frontier(record) == PhysicalFrontier.WARRANTED


def test_artifact_fanout_does_not_multiply_roots():
    evidence = [
        Evidence(EvidenceKind.SYMBOLIC, "history:root-1"),
        Evidence(EvidenceKind.MODEL_AGREEMENT, "history:root-1"),      # same root, different representation
        Evidence(EvidenceKind.SIMULATION, "simulation:root-2"),
    ]
    assert independent_root_count(evidence) == 2

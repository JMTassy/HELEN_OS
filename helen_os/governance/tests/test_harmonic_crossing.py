from helen_os.governance.harmonic_crossing import (
    CrossingRecord,
    Evidence,
    EvidenceKind,
    PhysicalFrontier,
    independent_root_count,
    physical_frontier,
    run_harmonic_crossing_adversary,
)


def test_salience_does_not_promote_physical_frontier():
    base = CrossingRecord("SG-001").with_evidence(
        Evidence(EvidenceKind.GEOMETRY, "geometry:1")
    )
    result = run_harmonic_crossing_adversary(base)
    assert result.negative_control_pass
    assert result.positive_control_pass
    assert result.replication_control_pass
    assert result.passed


def test_simulation_is_hypothesis_not_measurement():
    record = CrossingRecord("SG-002").with_evidence(
        Evidence(EvidenceKind.GEOMETRY, "geometry:2"),
        Evidence(EvidenceKind.SIMULATION, "simulation:2"),
    )
    assert physical_frontier(record) == PhysicalFrontier.HYPOTHESIS


def test_measurement_without_controls_does_not_cross():
    record = CrossingRecord("SG-003").with_evidence(
        Evidence(EvidenceKind.GEOMETRY, "geometry:3"),
        Evidence(EvidenceKind.CONTROLLED_MEASUREMENT, "bench:3", effect_quantified=True),
    )
    assert physical_frontier(record) == PhysicalFrontier.STRUCTURE


def test_same_root_replication_is_not_independent():
    record = CrossingRecord("SG-004").with_evidence(
        Evidence(EvidenceKind.GEOMETRY, "geometry:4"),
        Evidence(
            EvidenceKind.CONTROLLED_MEASUREMENT,
            "bench:shared",
            mechanism_defined=True,
            controls_present=True,
            effect_quantified=True,
        ),
        Evidence(
            EvidenceKind.INDEPENDENT_REPLICATION,
            "bench:shared",
            independent=True,
            controls_present=True,
            effect_quantified=True,
        ),
    )
    assert physical_frontier(record) == PhysicalFrontier.MEASURED


def test_artifact_fanout_does_not_multiply_roots():
    evidence = [
        Evidence(EvidenceKind.SYMBOLIC, "history:root-1"),
        Evidence(EvidenceKind.MODEL_AGREEMENT, "history:root-1"),
        Evidence(EvidenceKind.SIMULATION, "simulation:root-2"),
    ]
    assert independent_root_count(evidence) == 2

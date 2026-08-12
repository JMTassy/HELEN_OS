"""The Garden attack, executed: four traces, each locally admissible on
all four ceilings, each globally violating one — and each caught by
transactional evaluation of the SAME four ceilings, so none earns a
fifth. Compositional completeness stays UNKNOWN.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import compositional_closure as cc
from compositional_closure import (
    Delta,
    admit_trace,
    all_locally_admissible,
    compositional_gap,
    fifth_ceiling_status,
)

CLEAN = {"PROOF": True, "SCOPE": True, "AUTHORITY": True, "REPLAY": True}


# ── COUNTEREXAMPLE 1 — SCOPE: A reads X, B transforms, C writes Z ───────
# No single actor may move X -> Z; the composition does exactly that.

def _flow_trace():
    return (
        Delta("d1_A_read_X", CLEAN, flow_from="X", writes=frozenset({"buf1"})),
        Delta("d2_B_transform", CLEAN, flow_from="buf1",
              writes=frozenset({"buf2"})),
        Delta("d3_C_write_Z", CLEAN, flow_from="buf2", flow_to="Z",
              writes=frozenset({"Z"})),
    )


def test_information_flow_composes_past_local_scope():
    trace = _flow_trace()
    assert all_locally_admissible(trace) is True        # every op is clean
    inv = {"forbidden_flows": {("X", "Z")}}
    gap = compositional_gap(trace, inv)
    assert gap["compositional_gap"] is True
    assert gap["breached_ceilings"] == ["SCOPE"]
    assert gap["needs_fifth_ceiling"] is False           # transactional SCOPE


# ── COUNTEREXAMPLE 2 — AUTHORITY: merge o transfer o canonicalize ──────
# Each ontology mutation locally admissible; composed, they mint an
# identity assertion nobody was authorized to make.

def _identity_trace():
    return (
        Delta("d1_transfer_attr", CLEAN, ontology_delta=0),
        Delta("d2_merge", CLEAN, ontology_delta=-1),
        Delta("d3_canonicalize", CLEAN,
              asserts_identity="hull_B:nationality=Dutch"),
    )


def test_identity_assertion_composes_past_local_authority():
    trace = _identity_trace()
    assert all_locally_admissible(trace) is True
    inv = {"authorized_identities": ()}                  # nobody authorized it
    gap = compositional_gap(trace, inv)
    assert gap["compositional_gap"] is True
    assert gap["breached_ceilings"] == ["AUTHORITY"]


# ── COUNTEREXAMPLE 3 — PROOF: derived-from-derived witness inflation ───
# Each derivation is locally fine; composed, a translation-of-a-
# translation is counted as independent evidence it is not.

def _evidence_trace():
    return (
        Delta("d1_original", CLEAN, produces_artifact="a",
              evidence_root="R"),
        Delta("d2_translation", CLEAN, produces_artifact="b",
              derives_from="a"),
        Delta("d3_abstract", CLEAN, produces_artifact="c", derives_from="b"),
    )


def test_evidence_roots_do_not_inflate_across_composition():
    trace = _evidence_trace()
    assert all_locally_admissible(trace) is True
    inv = {"claimed_independent_roots": 3}               # the false claim
    gap = compositional_gap(trace, inv)
    assert gap["compositional_gap"] is True
    assert gap["breached_ceilings"] == ["PROOF"]
    # the transitive closure knows there is really ONE root
    assert cc.trace_proof(trace)["n_independent"] == 1


# ── COUNTEREXAMPLE 4 — REPLAY: premise revoked between t0 and effect ───
# Proof valid at t0, authorization at t1, effect at t2 — but the root
# was revoked before t2. Each op was fine at its own instant.

def _temporal_trace():
    return (
        Delta("d1_prove", CLEAN, premise_root="R", t=0),
        Delta("d2_authorize", CLEAN, premise_root="R", t=1),
        Delta("d3_effect", CLEAN, premise_root="R", t=2),
    )


def test_a_premise_revoked_before_its_effect_breaks_transactionally():
    trace = _temporal_trace()
    assert all_locally_admissible(trace) is True
    inv = {"revoked_at": {"R": 2}}                       # R died at t=2
    gap = compositional_gap(trace, inv)
    assert gap["compositional_gap"] is True
    assert gap["breached_ceilings"] == ["REPLAY"]


# ── all four ceilings can break compositionally; none needs a fifth ────

def test_all_four_ceilings_have_a_compositional_counterexample():
    cases = [
        (_flow_trace(), {"forbidden_flows": {("X", "Z")}}, "SCOPE"),
        (_identity_trace(), {"authorized_identities": ()}, "AUTHORITY"),
        (_evidence_trace(), {"claimed_independent_roots": 3}, "PROOF"),
        (_temporal_trace(), {"revoked_at": {"R": 2}}, "REPLAY"),
    ]
    breached = set()
    for trace, inv, expected in cases:
        gap = compositional_gap(trace, inv)
        assert gap["compositional_gap"] is True
        assert gap["breached_ceilings"] == [expected]
        breached.add(expected)
    assert breached == {"PROOF", "SCOPE", "AUTHORITY", "REPLAY"}


def test_no_gap_when_the_global_invariant_is_not_violated():
    trace = _flow_trace()
    gap = compositional_gap(trace, {"forbidden_flows": {("P", "Q")}})
    assert gap["compositional_gap"] is False
    assert gap["trace_verdict"] == "ADMIT"


# ── the honest verdict: no fifth ceiling earned, completeness UNKNOWN ──

def test_every_counterexample_is_caught_by_transactional_eval():
    """The diagnosis for all four is NON_COMPOSITIONAL_DEFINITION — the
    fix is trace-level evaluation of the existing four ceilings."""
    for trace, inv in ((_flow_trace(), {"forbidden_flows": {("X", "Z")}}),
                       (_identity_trace(), {"authorized_identities": ()}),
                       (_evidence_trace(), {"claimed_independent_roots": 3}),
                       (_temporal_trace(), {"revoked_at": {"R": 2}})):
        assert compositional_gap(trace, inv)["diagnosis"] == \
            "NON_COMPOSITIONAL_DEFINITION"


def test_fifth_ceiling_is_not_earned():
    # each counterexample is caught transactionally -> not a fifth ceiling
    counterexamples = tuple(
        {"passes_transactional": False, "still_invalid": True}
        for _ in range(4))
    v = fifth_ceiling_status(counterexamples)
    assert v["fifth_ceiling_earned"] is False
    assert v["all_caught_by_transactional_eval"] is True
    assert v["completeness"] == "UNKNOWN"


def test_a_trace_that_passes_both_would_earn_a_fifth():
    """The only thing that WOULD earn ceiling #5: passes local AND
    transactional, still invalid. None found; the machinery admits one
    if it ever appears."""
    hypothetical = ({"passes_transactional": True, "still_invalid": True},)
    assert fifth_ceiling_status(hypothetical)["fifth_ceiling_earned"] is True


def test_deterministic():
    trace = _flow_trace()
    inv = {"forbidden_flows": {("X", "Z")}}
    assert cc.canon(admit_trace(trace, inv)) == \
        cc.canon(admit_trace(trace, inv))

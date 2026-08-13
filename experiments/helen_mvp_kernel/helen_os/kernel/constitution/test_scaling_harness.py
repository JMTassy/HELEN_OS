"""The harness, falsified: the relayed PROJECTED table is refused by
name; authority inflation is caught; the three canaries refuse; a
worker-format defect is not a measurement; and surviving one run is
still not a law.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pytest

import scaling_harness as sh
from scaling_harness import (
    canary_chunking,
    canary_duplicate,
    canary_paraphrase,
    check_invariant,
    ingest,
    parse_yield_gate,
    root_redundancy,
    row,
    saturation,
)


def _r(N, H, Q, A=0, W=1, dp=1, dv=0, grade=sh.MEASURED):
    return row(N=N, H=H, Q=Q, N_epi=1, W=W, D_proposed=dp,
               D_valid=dv, A=A, E_gamma=0, grade=grade)


# ── the projected table is refused ─────────────────────────────────────

def test_the_relayed_projected_table_is_refused_by_name():
    """H = 3,8,14,21,29 / Q = 3,5,6,6,6 arrived as a PROJECTION. It
    may not enter Sigma_N however plausible it looks."""
    projected = tuple(
        _r(n, h, q, grade=sh.PROJECTED)
        for n, h, q in ((1, 3, 3), (2, 8, 5), (3, 14, 6),
                        (4, 21, 6), (5, 29, 6)))
    v = ingest(projected)
    assert v["ingested"] is False
    assert v["reason"] == "E_PROJECTED_ROW"
    assert v["projected_at_N"] == [1, 2, 3, 4, 5]
    assert "laundering event" in v["law"]


def test_one_projected_row_poisons_an_otherwise_measured_table():
    mixed = (_r(1, 3, 3), _r(2, 8, 5, grade=sh.PROJECTED))
    assert ingest(mixed)["reason"] == "E_PROJECTED_ROW"


def test_measured_rows_ingest():
    v = ingest((_r(1, 3, 3), _r(2, 8, 5)))
    assert v["ingested"] is True and v["n_rows"] == 2


def test_an_incomplete_row_is_refused():
    assert row(N=1, H=3)["reason"] == "E_INCOMPLETE_ROW"


def test_more_valid_than_proposed_derivations_is_refused():
    assert _r(1, 3, 3, dp=1, dv=2)["reason"] == \
        "E_MORE_VALID_THAN_PROPOSED"


def test_no_rows_is_refused():
    with pytest.raises(ValueError, match="E_NO_ROWS"):
        ingest(())


# ── the invariant ───────────────────────────────────────────────────────

def test_authority_rising_without_evidence_is_inflation():
    sigma = (_r(1, 3, 3, A=0), _r(2, 8, 5, A=1))     # A up, W/D flat
    v = check_invariant(sigma)
    assert v["holds"] is False
    assert v["verdict"] == "FAIL_AUTHORITY_INFLATION"
    assert v["at_N"] == 2


def test_authority_rising_with_a_new_witness_is_lawful():
    sigma = (_r(1, 3, 3, A=0, W=1), _r(2, 8, 5, A=1, W=2))
    assert check_invariant(sigma)["holds"] is True


def test_a_valid_derivation_also_licenses_the_rise():
    sigma = (_r(1, 3, 3, A=0, dp=2, dv=0),
             _r(2, 8, 5, A=1, dp=3, dv=1))
    assert check_invariant(sigma)["holds"] is True


def test_proposed_derivations_alone_license_nothing():
    """The spec's D rising 1->2->3 while A stays 0: consistent only
    if those derivations are PROPOSED, not VALID."""
    sigma = (_r(1, 3, 3, A=0, dp=1, dv=0),
             _r(2, 8, 5, A=1, dp=3, dv=0))       # proposals only
    assert check_invariant(sigma)["verdict"] == \
        "FAIL_AUTHORITY_INFLATION"


def test_surviving_a_run_is_not_a_law():
    v = check_invariant((_r(1, 3, 3), _r(2, 8, 5)))
    assert v["status"] == "HYPOTHESIS_SURVIVED_THIS_RUN"
    assert "not a law" in v["law"]


# ── the metrics, honestly named ────────────────────────────────────────

def test_chi_E_is_root_redundancy_and_refuses_the_waste_reading():
    v = root_redundancy(5, 1)
    assert v["chi_E"] == 0.8            # the relayed arithmetic holds
    assert v["reading"] == "root redundancy"
    assert v["is_waste"] is None


def test_saturation_is_scoped_to_the_instrument_not_the_corpus():
    sigma = (_r(1, 3, 3), _r(2, 8, 5), _r(3, 14, 6), _r(4, 21, 6))
    v = saturation(sigma)
    assert v["saturated_at_N"] == 4
    assert "not a property of the corpus" in v["scope"]


def test_no_saturation_is_reported_as_such():
    assert saturation((_r(1, 3, 3), _r(2, 8, 5)))["saturated_at_N"] \
        is None


# ── the live-run defect: yield is not a measurement ────────────────────

def test_a_zero_parse_yield_makes_the_row_unreadable_not_zero():
    """The N=1 run: canaries held, status violations 0, rules 0
    because the JSON did not parse."""
    v = parse_yield_gate(parsed=0, attempted=1)
    assert v["parse_yield"] == 0.0
    assert v["readable"] is False
    assert v["reason"] == "E_YIELD_TOO_LOW"


def test_a_healthy_yield_is_readable():
    assert parse_yield_gate(15, 16)["readable"] is True


def test_no_attempts_is_refused():
    with pytest.raises(ValueError, match="E_NO_ATTEMPTS"):
        parse_yield_gate(0, 0)


# ── the three canaries ──────────────────────────────────────────────────

def test_duplicate_canary_refuses():
    v = canary_duplicate(_r(1, 3, 3), copies=10)
    assert v["H_rose"] is True
    assert v["Q_flat"] and v["roots_flat"] and v["A_flat"]
    assert v["refused"] is True


def test_paraphrase_canary_refuses_however_confident():
    obs = {(6, 6, "OPEN")}
    k = {"rules": [], "literals": [(6, 6, "OPEN")]}
    v = canary_paraphrase(k, dict(k), obs, rhetorical_confidence=0.99)
    assert v["quotiented_together"] is True
    assert v["authority_gained"] == 0
    assert v["refused"] is True


def test_chunking_canary_mints_no_new_root():
    v = canary_chunking("sha:atf1900", "sha:atf1900")
    assert v["distinct_roots"] == 1
    assert v["new_root_minted"] is False
    assert v["refused"] is True


def test_a_genuinely_different_edition_would_be_a_second_root():
    v = canary_chunking("sha:atf1900", "sha:atf1898_other_edition")
    assert v["new_root_minted"] is True     # the honest positive case


def test_deterministic():
    assert sh.canon(root_redundancy(5, 1)) == \
        sh.canon(root_redundancy(5, 1))


# ── the ignorance baseline: UNREADABLE is not zero ─────────────────────

def test_forcing_a_clean_string_out_of_noise_is_refused():
    v = sh.extraction("p31.c4", "Battalion", source_legible=False)
    assert v["ok"] is False
    assert v["reason"] == "E_HALLUCINATED_LEGIBILITY"


def test_declaring_unreadable_on_noise_is_a_correct_extraction():
    v = sh.extraction("p31.c4", sh.UNREADABLE, source_legible=False)
    assert v["ok"] is True
    assert v["value"] == sh.UNREADABLE
    assert v["declared_unreadable"] is True


def test_declaring_unreadable_on_a_legible_cell_costs_yield_not_truth():
    v = sh.extraction("p31.c5", sh.UNREADABLE, source_legible=True)
    assert v["ok"] is True and v["conservative"] is True


def test_a_legible_cell_read_cleanly_is_ordinary():
    v = sh.extraction("p31.c5", "Battalion", source_legible=True)
    assert v["ok"] is True and v["declared_unreadable"] is False


def test_zero_unreadable_with_nothing_planted_is_uninterpretable():
    """The canary-at-zero defect: silence measures the corpus slice,
    not the swarm."""
    v = sh.ignorance_baseline(planted_illegible=0,
                              declared_unreadable=0, total_cells=200)
    assert v["interpretable"] is False
    assert v["reason"] == "E_NO_ILLEGIBLE_CONTROL"


def test_planted_noise_makes_the_class_measurable():
    v = sh.ignorance_baseline(planted_illegible=10,
                              declared_unreadable=7, total_cells=200)
    assert v["interpretable"] is True
    assert v["ignorance_recall"] == 0.7
    assert v["hallucinated_legibility"] == 3
    assert v["excess_declarations"] == 0


def test_over_declaring_ignorance_is_scored_separately_from_missing_it():
    v = sh.ignorance_baseline(planted_illegible=10,
                              declared_unreadable=14, total_cells=200)
    assert v["ignorance_recall"] == 1.0
    assert v["excess_declarations"] == 4
    assert v["hallucinated_legibility"] == 0


def test_no_cells_is_refused():
    with pytest.raises(ValueError, match="E_NO_CELLS"):
        sh.ignorance_baseline(1, 1, 0)


# ── N_effective on the hypothesis space ────────────────────────────────

def test_five_instances_of_one_model_at_T0_are_one_instrument():
    v = sh.swarm_common_mode(n_agents=5, n_model_configs=1,
                             temperature=0.0,
                             independent_prompts=False)
    assert v["N_effective_on_hypotheses"] == 1
    assert v["deterministic_copies"] is True
    assert v["independence_licensed"] is False
    assert v["reason"] == "E_SWARM_COMMON_MODE"


def test_temperature_alone_does_not_buy_independence():
    v = sh.swarm_common_mode(n_agents=5, n_model_configs=1,
                             temperature=0.8,
                             independent_prompts=False)
    assert v["N_effective_on_hypotheses"] == 1
    assert v["deterministic_copies"] is False   # stochastic, still one mode
    assert v["reason"] == "E_SWARM_COMMON_MODE"


def test_distinct_prompts_or_distinct_weights_do_buy_it():
    byprompt = sh.swarm_common_mode(5, 1, 0.0, independent_prompts=True)
    byweights = sh.swarm_common_mode(5, 3, 0.0,
                                     independent_prompts=False)
    assert byprompt["independence_licensed"] is True
    assert byweights["N_effective_on_hypotheses"] == 3
    assert byweights["reason"] is None


def test_n_effective_never_exceeds_the_agent_count():
    v = sh.swarm_common_mode(n_agents=2, n_model_configs=9,
                             temperature=0.7, independent_prompts=True)
    assert v["N_effective_on_hypotheses"] == 2


def test_no_agents_is_refused():
    with pytest.raises(ValueError, match="E_NO_AGENTS"):
        sh.swarm_common_mode(0, 1, 0.0, False)


# ── which half of the claim is testable ────────────────────────────────

def test_the_flat_authority_curve_is_forced_and_proves_nothing():
    for c in ("A_N_flat", "N_epi_flat"):
        v = sh.claim_status(c)
        assert v["status"] == "TRUE_BY_CONSTRUCTION"
        assert v["evidence_for_invariant"] is False
        assert v["role"] == "conformance check on the harness"


def test_only_the_cognitive_half_can_disappoint_the_run():
    for c in ("H_N_rises", "Q_N_rises"):
        v = sh.claim_status(c)
        assert v["status"] == "FALSIFIABLE_THIS_RUN"
        assert v["evidence_for_invariant"] is True


def test_an_unknown_claim_component_is_refused():
    assert sh.claim_status("vibes")["reason"] == "E_UNKNOWN_COMPONENT"

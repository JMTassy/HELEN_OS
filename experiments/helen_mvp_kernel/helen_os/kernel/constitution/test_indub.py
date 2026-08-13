"""indub(p), falsified: the SAME inducer returns SUPPORTED on a
product-structured family and REFUTED on an idiosyncratic one — the
experiment can fail, so its pass means something. Predicting without
compressing returns HOLD, not a grammar claim. Unresolved structure is
carried, not smoothed. And one verified instance is never a theorem.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pytest

import indub as ib
from indub import (
    corpus_status,
    generate,
    heldout_test,
    indub,
    instance_is_not_theorem,
    next_corpus_role,
)


def _spec(p, s, st):
    return {"pattern": p, "size": s, "state": st}


# ── fixture A: product structure (the ATF two-colour-register shape) ───
# patterns 6, 9, 10 x four sizes x {OPEN, TINT}

def _structured():
    return tuple(_spec(p, s, st)
                 for p in (6, 9, 10)
                 for s in (6, 12, 18, 24)
                 for st in ("OPEN", "TINT"))


# ── fixture B: idiosyncratic — every pattern one size, one state ───────

def _idiosyncratic():
    return tuple(_spec(100 + i, 6 + i, "OPEN") for i in range(24))


# ── the inducer generalizes only where licensed ────────────────────────

def test_product_structure_yields_compact_rules():
    fit = indub(_structured())
    assert len(fit["K_hat"]["rules"]) == 3        # one per pattern
    assert fit["K_hat"]["literals"] == []
    assert fit["n_observed"] == 24
    assert fit["k_size"] == 3
    assert fit["compression"] > 0.8
    assert fit["U"] == []


def test_idiosyncratic_family_yields_no_rules_and_names_the_gap():
    fit = indub(_idiosyncratic())
    assert fit["K_hat"]["rules"] == []
    assert len(fit["K_hat"]["literals"]) == 24
    assert fit["compression"] == 0.0
    assert len(fit["U"]) == 24                    # unresolved, carried
    assert "no generalization licensed" in fit["U"][0]["why"]


def test_a_single_state_pattern_is_never_generalized():
    """One dimension witnessed is not enough — the restraint that
    makes REFUTED reachable."""
    fit = indub(tuple(_spec(6, s, "OPEN") for s in (6, 12, 18)))
    assert fit["K_hat"]["rules"] == []
    assert len(fit["K_hat"]["literals"]) == 3


def test_no_specimens_is_refused():
    with pytest.raises(ValueError, match="E_NO_SPECIMENS"):
        indub(())


# ── the held-out falsifier discriminates ───────────────────────────────

def test_structured_family_predicts_heldout_and_is_supported():
    full = _structured()
    heldout = tuple(s for s in full
                    if (s["pattern"], s["size"], s["state"]) ==
                    (6, 12, "TINT"))
    train = tuple(s for s in full if s not in heldout)
    r = heldout_test(train, heldout)
    assert r["verdict"] == "SUPPORTED"
    assert r["heldout_coverage"] == 1.0
    assert r["compresses"] is True
    assert r["demoted_to"] is None


def test_idiosyncratic_family_is_refuted_and_demoted():
    """The same inducer, opposite verdict: this is the proof the test
    is not a rubber stamp."""
    full = _idiosyncratic()
    train, heldout = full[:-3], full[-3:]
    r = heldout_test(train, heldout)
    assert r["verdict"] == "REFUTED"
    assert r["demoted_to"] == "DESCRIPTIVE_TAXONOMY"
    assert r["heldout_coverage"] == 0.0
    assert len(r["missed_heldout"]) == 3


def test_predicting_without_beating_the_baseline_returns_hold():
    """A rule that predicts the held-out item but OVER-GENERATES so
    heavily it costs more than listing the observations. Coverage 1.0,
    MDL lost -> HOLD. Memorization must not be laundered into a
    grammar claim, and neither must speculation."""
    train = (_spec(6, 6, "OPEN"), _spec(6, 6, "TINT"),
             _spec(6, 12, "OPEN"), _spec(6, 18, "OPEN"),
             _spec(6, 24, "OPEN"))
    heldout = (_spec(6, 12, "TINT"),)
    r = heldout_test(train, heldout)
    assert r["heldout_coverage"] == 1.0
    assert r["mdl"]["beats_memorization"] is False
    assert r["mdl"]["over_generated"] == 3
    assert r["verdict"] == "HOLD"


def test_memorization_can_never_beat_the_baseline():
    """The complexity penalty, doing its job: a pure literal grammar
    ties the baseline and a tie is not a win."""
    fit = indub(_idiosyncratic())
    mdl = ib.description_length(fit["K_hat"],
                                {(s["pattern"], s["size"], s["state"])
                                 for s in _idiosyncratic()})
    assert mdl["total"] == mdl["baseline_memorization"]
    assert mdl["beats_memorization"] is False


def test_empty_heldout_is_refused():
    with pytest.raises(ValueError, match="E_EMPTY_HELDOUT"):
        heldout_test(_structured(), ())


def test_generate_expands_rules_into_the_predicted_family():
    fit = indub(_structured())
    assert len(generate(fit["K_hat"])) == 24


# ── the audit correction ────────────────────────────────────────────────

def test_a_verified_instance_is_not_an_architecture_theorem():
    v = instance_is_not_theorem(
        "corpus/hash string verification", True,
        "epistemic conservation law")
    assert v["law_proven"] is False
    assert v["reason"] == "E_INSTANCE_IS_NOT_THEOREM"
    assert v["instance_verified"] is True      # both hold at once


# ── honest access state and the 1851 role ──────────────────────────────

def test_the_corpus_access_limit_is_stated_not_hidden():
    v = corpus_status()
    assert v["reachable_from_this_seat"] is False
    assert v["machinery_ready"] is True
    assert v["claims_made_about_corpus_content"] is None


def test_1851_is_validation_not_expansion():
    v = next_corpus_role()
    assert v["role"] == "OUT_OF_DISTRIBUTION_VALIDATION"
    assert v["not"] == "collection_expansion"
    assert "REFUTED grammar has nothing to validate" in \
        v["precondition"]


def test_deterministic():
    assert ib.canon(indub(_structured())) == \
        ib.canon(indub(_structured()))


# ── the uniqueness defect, fixed: G(p) is a SPACE ──────────────────────

def test_inverse_reconstruction_is_non_unique():
    """The defect this module shipped with: one K_hat presented as
    the historical process. Several grammars generate the same
    specimens."""
    sp = ib.grammar_space(_structured())
    assert sp["n_consistent"] > 1
    assert sp["unique"] is False
    assert set(sp["consistent_with_observation"]) >= {
        "LITERAL", "PER_PATTERN"}


def test_over_generation_is_reported_never_hidden():
    """How much history each grammar would invent."""
    g = {c["grammar_id"]: c for c in
         ib.grammar_space(_structured())["G_of_p"]}
    assert g["LITERAL"]["over_generation"] == 0
    assert g["LITERAL"]["compression"] == 0.0
    assert g["GLOBAL_PRODUCT"]["compression"] > g["PER_PATTERN"][
        "compression"]


def test_collapsing_the_space_without_evidence_is_refused():
    sp = ib.grammar_space(_structured())
    v = ib.select_unique(sp, discriminating_evidence=False)
    assert v["verdict"] == "UNDERDETERMINED"
    assert v["reason"] == "E_NON_UNIQUE_RECONSTRUCTION"
    assert v["selected"] is None
    assert len(v["survivors"]) > 1


def test_discriminating_evidence_licenses_a_selection():
    sp = ib.grammar_space(_structured())
    assert ib.select_unique(sp, True)["verdict"] == "DETERMINED"


def test_reconstructible_is_not_historically_used():
    v = ib.reconstructible_is_not_used("border_6_12_TINT", True)
    assert v["reconstructible"] is True
    assert v["historically_used"] is None      # not False — unknown
    assert v["reason"] == "E_RECONSTRUCTION_IS_NOT_HISTORY"


def test_exit_code_zero_validates_nothing():
    v = ib.completion_is_not_validation("20-epoch swarm", 0)
    assert v["completed"] is True
    assert v["grammar_validated"] is False
    assert v["reason"] == "E_COMPLETION_IS_NOT_VALIDATION"


def test_no_specimens_refused_in_the_space_too():
    with pytest.raises(ValueError, match="E_NO_SPECIMENS"):
        ib.grammar_space(())


# ── observational equivalence, controls, discrimination, swarm laws ────

def test_the_learned_object_is_an_equivalence_class():
    obs = {(s["pattern"], s["size"], s["state"])
           for s in _structured()}
    per_pattern = indub(_structured())["K_hat"]
    literal = {"rules": [], "literals": sorted(obs)}
    v = ib.observationally_equivalent(per_pattern, literal, obs)
    assert v["equivalent_on_O"] is True
    assert "equivalence class" in v["learned_object"]


def test_grammars_differing_outside_the_corpus_are_indistinguishable():
    obs = {(6, 6, "OPEN")}
    k1 = {"rules": [], "literals": [(6, 6, "OPEN")]}
    k2 = {"rules": [], "literals": [(6, 6, "OPEN"), (99, 99, "TINT")]}
    v = ib.observationally_equivalent(k1, k2, obs)
    assert v["equivalent_on_O"] is True
    assert v["differences_outside_O"] == 1


def test_reconstructing_the_corpus_is_not_historical_identity():
    v = ib.reconstructs_corpus_is_not_historically_used("K_hat", True)
    assert v["reconstructs_corpus"] is True
    assert v["historically_used"] is None
    assert v["licensed"] == "observational adequacy"
    assert v["reason"] == "E_ADEQUACY_IS_NOT_IDENTITY"


def _asymmetric():
    """Patterns with DIFFERENT size ranges — so permuting the relations
    across patterns actually destroys prediction."""
    return (tuple(_spec(6, s, st) for s in (6, 12)
                  for st in ("OPEN", "TINT")) +
            tuple(_spec(9, s, st) for s in (18, 24)
                  for st in ("OPEN", "TINT")))


def test_a_symmetric_family_demonstrates_no_utility():
    """The finding K_matched produced on its very first run: on a
    fully symmetric product family, permuting the relations changes
    NOTHING, so K_matched ties the induced grammar at 1.0. The earlier
    'utility' result was an artifact of weak nulls — K_mem and
    K_random were simply too stupid to be informative."""
    full = _structured()
    heldout = (_spec(6, 12, "TINT"),)
    train = tuple(x for x in full if x != heldout[0])
    v = ib.against_controls(train, heldout)
    assert v["P_induced"] == 1.0
    assert v["P_memorizer"] == 0.0 and v["P_random"] == 0.0
    assert v["P_matched"] == 1.0            # the null that can hurt
    assert v["verdict"] == "NO_UTILITY_DEMONSTRATED"


def test_real_utility_requires_beating_the_matched_control():
    """Asymmetric structure: here the per-pattern relations carry
    information, permuting them breaks prediction, and the induced
    grammar earns its verdict."""
    full = _asymmetric()
    heldout = (_spec(6, 12, "TINT"),)
    train = tuple(x for x in full if x != heldout[0])
    v = ib.against_controls(train, heldout)
    assert v["P_induced"] == 1.0
    assert v["P_matched"] == 0.0
    assert v["beats_all_three"] is True
    assert v["verdict"] == "GRAMMAR_HAS_UTILITY"


def test_no_utility_when_the_controls_are_not_beaten():
    """Idiosyncratic family: the inducer predicts nothing the
    memorizer doesn't, so no utility is demonstrated."""
    full = _idiosyncratic()
    v = ib.against_controls(full[:-3], full[-3:])
    assert v["P_induced"] == 0.0
    assert v["beats_both_controls"] is False
    assert v["verdict"] == "NO_UTILITY_DEMONSTRATED"


def test_discriminate_designs_the_deciding_experiment():
    k1 = {"rules": [{"rule_id": "a", "pattern": 6,
                     "sizes": [6, 12], "states": ["OPEN", "TINT"],
                     "form": "PRODUCT"}], "literals": []}
    k2 = {"rules": [], "literals": [(6, 6, "OPEN"), (6, 6, "TINT"),
                                    (6, 12, "OPEN")]}
    v = ib.discriminate(k1, k2)
    assert v["verdict"] == "EXPERIMENT_DESIGNED"
    assert v["discriminating_observation"] == (6, 12, "TINT")
    assert v["predicted_by"] == "K1"


def test_identical_grammars_admit_no_experiment():
    k = {"rules": [], "literals": [(6, 6, "OPEN")]}
    v = ib.discriminate(k, dict(k))
    assert v["verdict"] == "OBSERVATIONALLY_IDENTICAL"
    assert v["discriminating_observation"] is None


def test_agent_count_licenses_no_promotion():
    many = ib.swarm_scaling(32, hypotheses=400,
                            new_independent_witnesses=0,
                            new_valid_derivations=0)
    one = ib.swarm_scaling(1, hypotheses=3,
                           new_independent_witnesses=1,
                           new_valid_derivations=0)
    assert many["proposal_capacity"] > one["proposal_capacity"]
    assert many["promotion_licensed"] is False      # 32 agents, nothing
    assert one["promotion_licensed"] is True        # 1 agent, a witness
    assert many["authority_from_headcount"] == 0


def test_winning_the_benchmark_leaves_the_claim_a_claim():
    v = ib.selection_is_not_promotion("K_best", 0.99)
    assert v["epistemic_phase"] == "claim"
    assert v["promoted"] is False
    assert v["reason"] == "E_SELECTION_IS_NOT_PROMOTION"


# ── defects found by COMPOSING the stages, not by testing each ─────────

def test_a_wildcard_rule_without_expansion_is_refused():
    """The composed-trace bug: generate() emitted ('*', size, state)
    literally, silently poisoning every downstream set comparison.
    Each stage passed alone; the composition was broken."""
    bad = {"rules": [{"rule_id": "w", "pattern": "*",
                      "sizes": [6], "states": ["OPEN"],
                      "form": "PRODUCT"}], "literals": []}
    with pytest.raises(ValueError, match="E_UNEXPANDED_WILDCARD"):
        ib.generate(bad)


def test_the_global_product_expands_over_every_pattern():
    sp = ib.grammar_space(_structured())
    g = {c["grammar_id"]: c for c in sp["G_of_p"]}
    assert g["GLOBAL_PRODUCT"]["covers_observed"] is True
    assert g["GLOBAL_PRODUCT"]["over_generation"] == 0


def test_discriminate_now_finds_the_real_two_item_disagreement():
    """Before the fix this returned 30 phantom candidates built from
    ('*', ...) tuples."""
    train = tuple(x for x in _structured()
                  if not (x["pattern"] == 6 and x["size"] == 12))
    k1 = indub(train)["K_hat"]
    k2 = {"rules": [{"rule_id": "g", "pattern": "*",
                     "patterns": [6, 9, 10],
                     "sizes": [6, 12, 18, 24],
                     "states": ["OPEN", "TINT"], "form": "PRODUCT"}],
          "literals": []}
    d = ib.discriminate(k1, k2)
    assert d["n_discriminating_candidates"] == 2
    assert d["discriminating_observation"] == (6, 12, "OPEN")
    assert d["predicted_by"] == "K2"


def test_a_control_beating_the_induction_gets_its_own_alarm():
    """NO_UTILITY_DEMONSTRATED understates the case where a random
    grammar actually outperforms the induced one."""
    train = tuple(x for x in _structured()
                  if not (x["pattern"] == 6 and x["size"] == 12))
    heldout = tuple(x for x in _structured()
                    if x["pattern"] == 6 and x["size"] == 12)
    v = ib.against_controls(train, heldout)
    assert v["P_induced"] == 0.0
    assert v["verdict"] == "CONTROL_OUTPERFORMED_INDUCTION"
    assert "K_random" in v["outperformed_by"]


def test_the_heldout_regime_distinguishes_two_experiments():
    """Holding out a whole dimension value asks for EXTRAPOLATION;
    holding out one cell asks for INTERPOLATION. A REFUTED verdict
    means different things in each."""
    full = _structured()
    cell = (_spec(6, 12, "TINT"),)
    interp = heldout_test(tuple(x for x in full if x != cell[0]), cell)
    assert interp["heldout_regime"] == "INTERPOLATION"
    assert interp["verdict"] == "SUPPORTED"

    col = tuple(x for x in full if x["size"] == 12)
    extrap = heldout_test(tuple(x for x in full if x["size"] != 12),
                          col)
    assert extrap["heldout_regime"] == "EXTRAPOLATION"
    assert extrap["verdict"] == "REFUTED"
    assert "different experiment" in extrap["regime_note"]


# ── the scaling law is conditional; the research state is the object ───

def test_the_scaling_law_is_conditional_not_absolute():
    """Correction of an overclaim: dA/dN = 0 holds only at fixed
    provenance and evidence. Independent experiments DO raise E."""
    idle = ib.swarm_scaling(32, 400, 0, 0)
    productive = ib.swarm_scaling(32, 400, new_independent_witnesses=5,
                                  new_valid_derivations=0)
    assert idle["promotion_licensed"] is False
    assert productive["promotion_licensed"] is True     # N helped
    assert productive["authority_from_headcount"] == 0  # but not directly


def test_repeated_roots_do_not_count_however_many_agents():
    v = ib.swarm_scaling(32, 400, new_independent_witnesses=32,
                         new_valid_derivations=0,
                         roots_genuinely_independent=False)
    assert v["claimed_evidence_delta"] == 32
    assert v["counted_evidence_delta"] == 0
    assert v["promotion_licensed"] is False


def test_the_collapse_hierarchy_on_the_reported_swarm_figures():
    """Operator-reported terminal signal, grade REPORTED: 32 agents,
    43 hypotheses, 1 independent root. Two findings at once.

    (a) The proposed chain began N_agents >> N_hypotheses. These
        figures FALSIFY that link — 43 > 32 — and rightly so: agents
        are generators, so amplification at that step is health.
    (b) The load-bearing collapse still holds and is severe:
        43 hypotheses -> 5 classes -> 1 root. N_eff = 1 on evidence
        even with K = 43 on the hypothesis space."""
    v = ib.research_state(n_agents=32,
                          hypotheses=tuple(range(43)),
                          equivalence_classes=5,
                          independent_roots=1)
    assert v["amplification_agents_to_hypotheses"] > 1.0   # (a)
    assert v["collapse_hierarchy_holds"] is True           # (b)
    assert v["effective_witnesses"] == 1
    assert v["diversity_collapse"] > 0.85
    assert v["evidential_collapse"] > 0.97


def test_a_broken_collapse_is_named():
    """More equivalence classes than hypotheses is incoherent."""
    v = ib.research_state(2, tuple(range(3)), 9, 1)
    assert v["collapse_hierarchy_holds"] is False


def test_discriminate_prefers_the_cheapest_separating_observation():
    k1 = {"rules": [], "literals": [(6, 6, "OPEN"), (9, 9, "OPEN")]}
    k2 = {"rules": [], "literals": []}
    v = ib.discriminate(k1, k2, cost=lambda t: 100 if t[0] == 6 else 1)
    assert v["discriminating_observation"] == (9, 9, "OPEN")
    assert v["selection_rule"].startswith("cheapest")


# ── MDL under a pinned encoder ─────────────────────────────────────────

def test_mdl_carries_its_encoder_version():
    fit = indub(_structured())
    obs = {(s["pattern"], s["size"], s["state"]) for s in _structured()}
    assert ib.description_length(fit["K_hat"], obs)["nu"] == \
        ib.ENCODER_VERSION


def test_comparing_across_encoders_is_refused():
    a = {"nu": "mdl-v1", "total": 10}
    b = {"nu": "mdl-v2", "total": 99}
    v = ib.compare_mdl(a, b)
    assert v["comparable"] is False
    assert v["reason"] == "E_ENCODER_MISMATCH"


def test_a_same_encoder_comparison_must_be_strict():
    same = ib.compare_mdl({"nu": "mdl-v1", "total": 10},
                          {"nu": "mdl-v1", "total": 10})
    assert same["comparable"] is True
    assert same["a_wins"] is False and same["strict"] is False


# ── equivalence is relative to the corpus ──────────────────────────────

def test_equivalence_is_corpus_relative_never_global():
    obs = {(6, 6, "OPEN")}
    k1 = {"rules": [], "literals": [(6, 6, "OPEN")]}
    k2 = {"rules": [], "literals": [(6, 6, "OPEN"), (99, 99, "TINT")]}
    v = ib.observationally_equivalent(k1, k2, obs)
    assert v["equivalent_on_O"] is True
    assert v["equivalent_on_X"] is None          # unknown, not True
    assert "RELATIVE TO O" in v["learned_object"]
    assert v["reason_if_claimed_globally"] == \
        "E_LOCAL_EQUIVALENCE_GENERALIZED"

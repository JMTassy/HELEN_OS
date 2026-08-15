"""Five representations from one root are one witness; retrieval ranks
by frontier change not similarity; a capability with no witnessed
failure is survivorship; a persistent narrative mints neither
capability nor authority; and a claim's support is counted in
independent roots net of contradiction, never in representations.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import institutional_stemmatics as st
from institutional_stemmatics import (
    capability,
    constitutional_forgetting,
    implies,
    iwg_claim_support,
    nonamplification,
    repetition_is_not_corroboration,
    retrieval_policy,
    retrieve,
    rho_epi,
    witness_class,
)


# ── epistemic density & nonamplification ───────────────────────────────

def test_five_representations_one_root_is_density_point_two():
    v = rho_epi(n_independent_roots=1, n_representations=5)
    assert v["rho_epi"] == 0.2
    assert v["amplification_illusion"] is True


def test_roots_cannot_exceed_representations():
    assert rho_epi(6, 5)["reason"] == "E_MORE_ROOTS_THAN_DOCS"
    assert rho_epi(1, 0)["reason"] == "E_NO_REPRESENTATIONS"


def test_nonamplification_counts_roots_not_the_chorus():
    v = nonamplification(n_saying_x=5, n_independent_roots=1)
    assert v["evidence_units"] == 1 and v["amplified"] is True
    assert nonamplification(3, 0)["reason"] == "E_NO_ROOT_FOR_CLAIM"


def test_repetition_from_one_root_does_not_corroborate():
    assert repetition_is_not_corroboration(5, same_root=True)[
        "reason"] == "E_REPETITION_AS_CORROBORATION"
    assert repetition_is_not_corroboration(5, same_root=False)[
        "corroborates"] is True


# ── adversarial retrieval ──────────────────────────────────────────────

def test_the_least_convenient_document_can_win():
    # (id, similarity, expected_frontier_change, contradicts)
    cands = (("marketing_4", 0.95, 0.01, False),
             ("econ_sheet", 0.40, 0.80, True))
    v = retrieve(cands)
    assert v["similarity_pick"] == "marketing_4"
    assert v["d_star"] == "econ_sheet"
    assert v["d_star_contradicts"] is True
    assert v["divergent"] is True


def test_similarity_only_retrieval_is_refused():
    assert retrieval_policy("max_similarity")["reason"] == \
        "E_SIMILARITY_BLIND_RETRIEVAL"
    assert retrieval_policy("max_expected_frontier_change")[
        "licensed"] is True


# ── negative memory ────────────────────────────────────────────────────

def test_a_capability_from_successes_only_is_survivorship():
    v = capability(successes=3, failures=0, boundary_conditions=[],
                   counterexamples=0)
    assert v["reason"] == "E_SURVIVORSHIP_CAPABILITY"
    ok = capability(3, 1, ["needs_budget>x"], 1)
    assert ok["ok"] is True and ok["conditions_known"] is True


def test_negative_witness_classes_are_first_class():
    assert len(st.WITNESS_CLASSES) == 5
    assert witness_class("FAILURE")["is_negative_memory"] is True
    assert witness_class("SUCCESS")["is_negative_memory"] is False
    assert witness_class("VIBES")["reason"] == \
        "E_UNKNOWN_WITNESS_CLASS"


# ── anti-mythology chain ───────────────────────────────────────────────

def test_the_six_non_implications_hold():
    assert len(st.ANTI_MYTHOLOGY) == 6
    for a, c in st.ANTI_MYTHOLOGY:
        assert implies(a, c)["implication_licensed"] is False
    assert implies("x", "y")["implication_licensed"] is None
    # the two most important named
    assert implies("corporate_claim", "capability")["reason"] == \
        "E_NARRATIVE_MINTS_CAPABILITY"
    assert implies("past_capability", "present_capability")["reason"] \
        == "E_PAST_MINTS_PRESENT"


def test_constitutional_forgetting_keeps_history_not_authority():
    v = constitutional_forgetting(warranted_at=True,
                                  currently_available=False,
                                  currently_authorized=False)
    assert v["history_preserved"] is True
    assert v["present_capability"] is False
    assert "warranted_then_not_available_now" in v["gaps"]
    v2 = constitutional_forgetting(True, True, False)
    assert "available_not_authorized" in v2["gaps"]


# ── the IWG claim type ─────────────────────────────────────────────────

def test_support_is_roots_net_of_contradiction_not_representations():
    v = iwg_claim_support("UZIK possesses capability C",
                          representations=5, independent_roots=1,
                          contradictions=0)
    assert v["net_independent_support"] == 1
    assert v["rho_epi"] == 0.2
    assert v["status"] == "SUPPORTED"
    assert v["promoted"] is False
    contested = iwg_claim_support("X", 5, 2, contradictions=3)
    assert contested["status"] == "CONTESTED"
    assert contested["net_independent_support"] == -1


def test_deterministic():
    assert st.canon(rho_epi(1, 5)) == st.canon(rho_epi(1, 5))
    assert st.canon(iwg_claim_support("c", 5, 1, 0)) == \
        st.canon(iwg_claim_support("c", 5, 1, 0))

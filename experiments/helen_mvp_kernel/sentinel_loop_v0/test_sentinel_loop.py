"""SENTINEL_LOOP_V0 — promotion-gate kill-suite. 🔵 OBSERVED · authority=false.

Earned boundary on PASS: "in this harness, a claim without provenance is not knowledge, N docs from one root
are not a pattern, an untested/refuted pattern is not a chiddush, and source-less claims cannot inflate
novelty." NOT a claim about any actual corpus.
"""
from sentinel_loop import (
    ClaimAtom, Falsification, SentinelState, classify, independent_roots, is_pattern, is_chiddush,
    expand_queries, N_INDEPENDENT, EPS, K_DRY,
)

def C(claim, source, root, ec="OBSERVED", entity="e", date="2018"):
    return ClaimAtom(claim, source, date, entity, ec, root)


def test_claim_without_provenance_is_not_knowledge():
    assert classify(C("x", "", "R1")) == "NOT_KNOWLEDGE"
    assert classify(C("x", "src", "R1", ec="UNKNOWN")) == "NOT_KNOWLEDGE"
    assert classify(C("x", "src", "R1", ec="OBSERVED")) == "OBSERVATION"


def test_fanout_defeated_many_docs_one_root_is_not_a_pattern():
    # 5 "sources" but all trace to one root ⇒ N_epi = 1 < N_INDEPENDENT
    claims = [C("same claim", f"doc{i}", "R_ONE") for i in range(5)]
    assert independent_roots(claims) == {"R_ONE"}
    assert is_pattern(claims) is False


def test_two_independent_roots_is_a_pattern():
    claims = [C("claim", "docA", "R1"), C("claim", "docB", "R2")]
    assert is_pattern(claims) is True


def test_untested_pattern_is_not_a_chiddush():
    claims = [C("claim", "docA", "R1"), C("claim", "docB", "R2")]
    assert is_chiddush(claims, None) is False                                  # no falsification attempted


def test_refuted_pattern_is_not_a_chiddush():
    claims = [C("claim", "docA", "R1"), C("claim", "docB", "R2")]
    fals = Falsification("claim", attempted=True, refuting_witness="found a counter-example")
    assert is_chiddush(claims, fals) is False                                  # falsification refuted it


def test_pattern_that_survived_falsification_is_a_chiddush():
    claims = [C("claim", "docA", "R1"), C("claim", "docB", "R2")]
    fals = Falsification("claim", attempted=True, refuting_witness="")
    assert is_chiddush(claims, fals) is True                                   # the ONE legit promotion


def test_sourceless_claims_cannot_inflate_novelty():
    st = SentinelState()
    r = st.ingest_round(read_files=["f1"], partial_files=[],
                        new_claims=[C("a", "", "R1"), C("b", "", "R2"), C("c", "", "R3")],  # all provenance-less
                        new_contradictions=[], new_open_witnesses=[], new_relations=[],
                        queries=[], docs_read=3)
    assert r["witnessed_new_claims"] == 0 and r["dropped_no_provenance"] == 3
    assert r["novelty"] == 0.0                                                 # hallucinated novelty rejected


def test_witnessed_novelty_counts():
    st = SentinelState()
    r = st.ingest_round(read_files=["f1"], partial_files=[],
                        new_claims=[C("a", "docA", "R1"), C("b", "docB", "R2")],
                        new_contradictions=[("a", "b", "conflict")], new_open_witnesses=["missing_w"],
                        new_relations=["a~b"], queries=["q1"], docs_read=2)
    # (2 witnessed claims + 1 relation + 1 contradiction + 1 frontier) / 2 docs = 2.5
    assert r["novelty"] == 2.5 and r["witnessed_new_claims"] == 2


def test_stop_rule_dry_rounds():
    st = SentinelState()
    for _ in range(K_DRY):
        st.novelty_history.append(EPS / 2)                                     # low novelty K times
    cont, why = st.should_continue(coverage=0.1, target=0.9, budget_remaining=True)
    assert cont is False and "novelty_dry" in why


def test_stop_rule_continue_when_novel():
    st = SentinelState()
    st.novelty_history = [1.0, 1.0, 1.0]
    cont, why = st.should_continue(coverage=0.1, target=0.9, budget_remaining=True)
    assert cont is True and why == "CONTINUE"


def test_derive_demotes_refuted_pattern():
    st = SentinelState()
    hyp = {"H1": [C("c", "docA", "R1"), C("c", "docB", "R2")]}
    st.falsify("H1", Falsification("H1", attempted=True, refuting_witness="counterexample"))
    out = st.derive(hyp)
    assert "H1" in out["patterns"] and "H1" not in out["chiddushim"] and "H1" in out["demoted"]


def test_expand_generates_frontier():
    q = expand_queries(C("Calvi precedes NEPTION", "docA", "R1", entity="NEPTION"))
    assert "neption" in {x.lower() for x in q}

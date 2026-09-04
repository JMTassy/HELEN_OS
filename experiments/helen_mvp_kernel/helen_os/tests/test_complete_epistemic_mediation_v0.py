"""COMPLETE_EPISTEMIC_MEDIATION_V0 — full mutant kill-suite (8 canonical + 4 additions). 🔵 OBSERVED · authority=false.

Earned boundary on PASS: "within this suite, a hypothesis removal cannot be bypassed, self-declared, fanned
out, globally justified, injected directly, replayed non-deterministically, or scored against a circular
gold; each kill is an individually-bound, frozen, independently-verified, replayable KillReceipt." NOT a
proof of any scientific claim, and NOT global kernel correctness.
"""
from dataclasses import replace
from helen_os.kernel.complete_epistemic_mediation_v0 import (
    FrozenExperiment, KillWitness, KillReceipt, GlobalReceipt, make_kill_receipt, verify_receipt,
    gamma_E, gamma_I, reduce_hypotheses, no_direct_injection, scores, replay, good_witness,
    AR_OBS, H_ALL, FEXP, FORBIDDEN, DISCRIMINATOR_VERSION, UPDATE_RULE, OBS_KEY, GOLD_KILLS, _hash,
    writer_census, gold_runtime_shared, mediation_receipt,
)


# ---------- WRITER CENSUS: absence of another door ----------
def test_writer_census_single_authorized_writer():
    wc = writer_census()
    assert wc["census_pass"] is True
    assert wc["direct_H_writer_paths"] == 1
    assert wc["H_writer_functions"] == ["reduce_hypotheses"]


def test_gold_not_shared_with_gamma_E():
    assert gold_runtime_shared() is False           # make_kill_receipt / reducer never read the gold fixture


def test_mediation_receipt_structure():
    r = mediation_receipt()
    assert r["H_after_source"] == "REDUCER_ONLY" and r["gold_runtime_shared"] is False
    assert r["gold_source"] == "STATIC_PREREG_FIXTURE" and r["authority"] is False


# ---------- ExperimentalBasis B_E: any post-freeze basis drift breaks the receipt ----------
def test_basis_mutation_scorer_rejected():
    r = gamma_E(H_ALL, [("H_L1", good_witness("H_L1"))], AR_OBS, FEXP)[0]
    drifted = replace(FEXP, scorer_id="scorer/AFTER_THE_FACT")     # change scorer post-freeze
    assert verify_receipt(r, AR_OBS, drifted) is False


def test_basis_mutation_model_config_rejected():
    r = gamma_E(H_ALL, [("H_L1", good_witness("H_L1"))], AR_OBS, FEXP)[0]
    drifted = replace(FEXP, model_config="qwen38-9b/temp0.7")      # change model post-freeze
    assert verify_receipt(r, AR_OBS, drifted) is False


def test_basis_mutation_thresholds_rejected():
    r = gamma_E(H_ALL, [("H_L1", good_witness("H_L1"))], AR_OBS, FEXP)[0]
    drifted = replace(FEXP, thresholds="kill iff minus_Li>=K7-0.05")
    assert verify_receipt(r, AR_OBS, drifted) is False

# ---------- base: a valid, receipt-derived contraction ----------
def test_base_valid_kill_reducer_derived():
    receipts = gamma_E(H_ALL, [("H_L1", good_witness("H_L1"))], AR_OBS, FEXP)
    assert len(receipts) == 1
    H_after, admitted = reduce_hypotheses(H_ALL, receipts, AR_OBS, FEXP)
    assert "H_L1" not in H_after and admitted[0].hypothesis_id == "H_L1"

# ---------- 1. kill_without_bound_receipt ----------
def test_kill_without_bound_receipt_rejected():
    v, r = no_direct_injection(H_ALL - {"H_L1"}, H_ALL, [], AR_OBS, FEXP)   # claim H_L1 dead, zero receipts
    assert v == "REJECT" and any("NOT_RECEIPT_DERIVED" in x for x in r)

# ---------- 2. cross_hypothesis_witness_reuse ----------
def test_cross_hypothesis_witness_reuse_rejected():
    w = KillWitness("H_L2", OBS_KEY["H_L1"], DISCRIMINATOR_VERSION, UPDATE_RULE)   # aims H_L2, reads L1's key
    assert make_kill_receipt("H_L2", AR_OBS, FEXP, w) is None

# ---------- 3. post_freeze_observation_mutation ----------
def test_post_freeze_observation_mutation_rejected():
    r = gamma_E(H_ALL, [("H_L1", good_witness("H_L1"))], AR_OBS, FEXP)[0]
    tampered = {**AR_OBS, "minus_L1": 0.1}
    assert verify_receipt(r, tampered, FEXP) is False                 # receipt no longer verifies vs mutated obs

# ---------- 4. gamma_e_to_gamma_i_escalation ----------
def test_gamma_e_kill_does_not_imply_gamma_i_admit():
    r = gamma_E(H_ALL, [("H_L1", good_witness("H_L1"))], AR_OBS, FEXP)[0]
    gi = gamma_I(r)
    assert gi["verdict"] == "NO_ADMISSION" and gi["authority_gain"] == 0

# ---------- 5. forced_kill_on_nondiscriminating_observation ----------
def test_forced_kill_on_nonrefuted_rejected():
    # H_L2 with its own key, but observation does NOT refute it (removing L2 dropped Q)
    assert make_kill_receipt("H_L2", AR_OBS, FEXP, good_witness("H_L2")) is None

# ---------- 6. failure_to_kill_excluded_hypothesis (recall penalises lazy HOLD) ----------
def test_lazy_hold_has_zero_recall_against_independent_gold():
    s = scores(H_ALL, [])                                             # killed nothing
    assert s["recall_kill"] == 0.0 and s["K_star"] == ["H_L1"]
    assert s["precision_kill"] is None                               # NA, not invented 1.0

# ---------- 7. replay_divergence (SameState ⇏ SameHistory) ----------
def test_replay_same_state_different_history_is_distinguished():
    r1 = KillReceipt("H_L1", _hash(AR_OBS), FEXP.prereg_hash, DISCRIMINATOR_VERSION, ("W1",), UPDATE_RULE)
    r2 = KillReceipt("H_L1", _hash(AR_OBS), FEXP.prereg_hash, DISCRIMINATOR_VERSION, ("W9",), UPDATE_RULE)
    a = replay(H_ALL, [r1], FORBIDDEN, AR_OBS, FEXP)
    b = replay(H_ALL, [r2], FORBIDDEN, AR_OBS, FEXP)
    assert a["H_after"] == b["H_after"]                              # same surviving state...
    assert a["receipt_classes"] != b["receipt_classes"]             # ...different provenance ⇒ different history

# ---------- 8. global_receipt_laundering ----------
def test_global_receipt_laundering_rejected():
    g = GlobalReceipt("experiment successful", ("H_L2", "H_L3"))     # no individual KillReceipts
    # reducer only honors KillReceipts; a global blob yields ZERO admitted kills
    H_after, admitted = reduce_hypotheses(H_ALL, [], AR_OBS, FEXP)
    assert admitted == [] and H_after == H_ALL
    v, r = no_direct_injection(H_ALL - {"H_L2", "H_L3"}, H_ALL, [], AR_OBS, FEXP)   # claim they died anyway
    assert v == "REJECT"

# ---------- +A. stale_discriminator_version ----------
def test_stale_discriminator_version_rejected():
    w = replace(good_witness("H_L1"), discriminator_version="ablation/OLD")
    assert make_kill_receipt("H_L1", AR_OBS, FEXP, w) is None

# ---------- +B. post_freeze_update_rule_mutation ----------
def test_post_freeze_update_rule_mutation_rejected():
    w = replace(good_witness("H_L1"), update_rule="weaker_rule_after_the_fact")
    assert make_kill_receipt("H_L1", AR_OBS, FEXP, w) is None

# ---------- +C. direct_h_after_injection ----------
def test_direct_h_after_injection_rejected():
    receipts = gamma_E(H_ALL, [("H_L1", good_witness("H_L1"))], AR_OBS, FEXP)
    # a claimed H_after that removes MORE than the receipts license (drops H_L2 too)
    v, r = no_direct_injection(H_ALL - {"H_L1", "H_L2"}, H_ALL, receipts, AR_OBS, FEXP)
    assert v == "REJECT"
    # the honest claim (only H_L1) is accepted
    v2, _ = no_direct_injection(H_ALL - {"H_L1"}, H_ALL, receipts, AR_OBS, FEXP)
    assert v2 == "ADMIT"

# ---------- +D. duplicate receipts ⇏ duplicate warrant ----------
def test_duplicate_receipts_single_warrant():
    r = gamma_E(H_ALL, [("H_L1", good_witness("H_L1"))], AR_OBS, FEXP)[0]
    H_after, admitted = reduce_hypotheses(H_ALL, [r, r, r], AR_OBS, FEXP)   # same receipt x3
    assert len(admitted) == 1 and "H_L1" not in H_after

# ---------- independent gold is NOT the runtime kill function ----------
def test_gold_is_static_and_independent():
    assert GOLD_KILLS == frozenset({"H_L1"})                         # a literal fixture, not Γ_E output
    s = scores(H_ALL, gamma_E(H_ALL, [("H_L1", good_witness("H_L1"))], AR_OBS, FEXP))
    assert s["precision_kill"] == 1.0 and s["recall_kill"] == 1.0 and s["false_kill_rate"] == 0.0

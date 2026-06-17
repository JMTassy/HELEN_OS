"""
Conformance + hardening tests for WUL_REDUCER_V0 — §9 vectors of
docs/wul/REDUCER_SPEC_V0.md made mechanical, PLUS the BED 02/03 hardening:
predicates are replay-DERIVED (not caller flags) and the seal is un-self-conferrable.

Illegal transitions must FAIL here, not in prose.

Run:  .venv/bin/pytest tests/test_wul_reducer.py -v
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from wul_reducer import (  # noqa: E402
    reduce_step, run_ladder, can_admit, canon_admit,
    derive_facts, compute_candidate_hash, ReplayContext,
    FORBIDDEN_TRANSITIONS, REJECT_CODES,
    S0_SYMBOL, S1_CLAIM, S2_TYPED, S3_RECEIPTED, S4_JUDGED,
    S5_ADMITTED, S6_REPLAYABLE, S_REJECTED, S_SUPERSEDED, S_TERMINAL,
    TERMINAL_REPLAYABLE,
    REJECT_BAD_STATE, REJECT_FORBIDDEN_TRANSITION, REJECT_NO_HASH, REJECT_NO_RECEIPT,
    REJECT_TERMINAL_FROZEN, REJECT_SPEC_CEILING, REJECT_CEILING_EXCEEDED,
    REJECT_TERMINAL_CONFLICT, REJECT_HUMAN_SEAL_MISSING, REJECT_REPLAY_MISMATCH,
    REJECT_GATE_RED, REJECT_REASON_MISSING,
)


# ── builders: a REAL valid candidate (derivable predicates), not flags ───────

def valid_candidate(**over):
    """A candidate whose predicates actually DERIVE true: content-bound hash,
    real evidence, an external operator seal bound to the hash. Returns (claim, rc)
    where rc is a replay context attesting the gates the reducer can't recompute."""
    c = dict(
        claim_form=True,
        content=over.pop("content", {"claim": "shigir idol ~12500 BP"}),
        claim_class=over.pop("claim_class", "OBSERVED"),
        truth_status=over.pop("truth_status", "UNVERIFIED"),
        evidence=over.pop("evidence", ["museum_catalog_ref"]),
        proposer="HER",
        max_state="S6_REPLAYABLE",
        level="DOCS",
        spec_allowed_level="KERNEL",
    )
    c.update(over)
    h = compute_candidate_hash(c)
    c["evidence_hash"] = c.get("evidence_hash", h)
    receipt = "receipt:" + h[-12:]
    c.setdefault("external_seal", {
        "candidate_hash": h,
        "issuer": "operator",
        "issuer_role": "OPERATOR",
        "receipt_hash": receipt,
    })
    rc = ReplayContext(gate_attested=True, replay_deterministic=True,
                       known_receipts=frozenset({receipt}))
    return c, rc


# ── §9 Test Vectors ─────────────────────────────────────────────────────────

def test_T1_illegal_promotion():
    c, rc = valid_candidate()
    v = reduce_step(S0_SYMBOL, S5_ADMITTED, c, rc)          # skip the ladder
    assert not v.allow
    assert v.reject_code == REJECT_FORBIDDEN_TRANSITION


def test_T2_missing_hash():
    c, rc = valid_candidate(evidence_hash="sha256:wrong")    # derived has_hash → False
    v = reduce_step(S2_TYPED, S3_RECEIPTED, c, rc)
    assert not v.allow
    assert v.reject_code == REJECT_NO_HASH


def test_T3_sealed_terminal_exit():
    c, rc = valid_candidate()
    v = reduce_step(S_TERMINAL, S2_TYPED, c, rc)
    assert not v.allow
    assert v.reject_code == REJECT_TERMINAL_FROZEN


def test_T4_replay_admissibility():
    c, rc = valid_candidate()
    v = reduce_step(S5_ADMITTED, S6_REPLAYABLE, c, rc)
    assert v.allow
    assert v.next_state == S6_REPLAYABLE


def test_T5_spec_ceiling():
    c, rc = valid_candidate(level="KERNEL", spec_allowed_level="DOCS")
    v = reduce_step(S0_SYMBOL, S1_CLAIM, c, rc)
    assert not v.allow
    assert v.reject_code == REJECT_SPEC_CEILING


def test_T6_terminal_consistency():
    c, rc = valid_candidate(prior_terminal_state="TERMINAL_REJECTED",
                            new_terminal_state="TERMINAL_ADMITTED",
                            same_canonical_id=True)
    v = reduce_step(S4_JUDGED, S5_ADMITTED, c, rc)
    assert not v.allow
    assert v.reject_code == REJECT_TERMINAL_CONFLICT


def test_T7_happy_path():
    c, rc = valid_candidate()
    final, terminal = run_ladder(c, rc)
    assert final == S6_REPLAYABLE
    assert terminal == TERMINAL_REPLAYABLE


# ── Forbidden-transition matrix (the executable constitution) ────────────────

def test_forbidden_transition_matrix():
    c, rc = valid_candidate()
    for (src, dst), code in FORBIDDEN_TRANSITIONS.items():
        v = reduce_step(src, dst, c, rc)
        assert not v.allow, f"{src}->{dst} should be forbidden"
        assert v.reject_code == code


def test_reject_enum_is_closed():
    # every code the matrix can raise is a member of the closed enum
    assert set(FORBIDDEN_TRANSITIONS.values()) <= REJECT_CODES


# ── BED 02/03 hardening — the point of this sync ─────────────────────────────

def test_human_seal_required_for_replay():
    c, rc = valid_candidate()
    c.pop("external_seal")                                   # no seal object at all
    v = reduce_step(S5_ADMITTED, S6_REPLAYABLE, c, rc)
    assert not v.allow
    assert v.reject_code == REJECT_HUMAN_SEAL_MISSING


def test_replay_mismatch_rejected():
    c, rc = valid_candidate()
    rc_bad = ReplayContext(gate_attested=True, replay_deterministic=False,
                           known_receipts=rc.known_receipts)
    v = reduce_step(S5_ADMITTED, S6_REPLAYABLE, c, rc_bad)
    assert not v.allow
    assert v.reject_code == REJECT_REPLAY_MISMATCH


def test_gate_red_blocks_judgement():
    c, rc = valid_candidate()
    rc_nogate = ReplayContext(gate_attested=False, replay_deterministic=True,
                              known_receipts=rc.known_receipts)
    v = reduce_step(S3_RECEIPTED, S4_JUDGED, c, rc_nogate)
    assert not v.allow
    assert v.reject_code == REJECT_GATE_RED


def test_admit_is_not_canon():
    c, rc = valid_candidate()
    # admissible (gates attested) but strip the seal → kernel-admit yes, canon no
    c_noseal = dict(c)
    c_noseal.pop("external_seal")
    assert can_admit(c_noseal, rc) is True
    assert canon_admit(c_noseal, rc) is False


def test_input_cannot_self_assert_by_flags():
    """BED 03: a claim that SETS every authority flag but provides no derivable
    evidence and no replay context must be REJECTED. asserted ⊬ derived."""
    bogus = dict(
        claim_form=True, typed=True, has_hash=True, gate_green=True,
        human_seal=True, det_replay=True, seal_valid=True,   # all self-asserted
        claim_class="OBSERVED", truth_status="UNVERIFIED",
        evidence=["x"], evidence_hash="sha256:i_made_this_up",
        external_seal={"candidate_hash": "sha256:i_made_this_up",
                       "issuer": "HER", "issuer_role": "OPERATOR",
                       "receipt_hash": "receipt:fake"},
        proposer="HER",
    )
    # no replay context: gates/replay cannot be attested; hash won't match
    final, terminal = run_ladder(bogus, replay_context=None)
    assert final == S_REJECTED
    # and even the seal is rejected on its own merits (proposer == issuer, unknown receipt)
    f = derive_facts(bogus, ReplayContext())
    assert f.has_hash is False
    assert f.gate_green is False
    assert f.seal_valid is False


def test_seal_must_be_external_not_self():
    """② un-self-conferrable: a seal issued by the proposer is invalid even if the
    hash binds and the receipt is known."""
    c, rc = valid_candidate()
    h = compute_candidate_hash(c)
    receipt = next(iter(rc.known_receipts))
    c["external_seal"] = {"candidate_hash": h, "issuer": "HER",   # == proposer
                          "issuer_role": "OPERATOR", "receipt_hash": receipt}
    v = reduce_step(S5_ADMITTED, S6_REPLAYABLE, c, rc)
    assert not v.allow
    assert v.reject_code == REJECT_HUMAN_SEAL_MISSING


# ── L6 max-state ceiling + S_SUPERSEDED ──────────────────────────────────────

def test_speculative_ceiling_blocks_admission():
    c, rc = valid_candidate(claim_class="SPECULATIVE")      # capped below S5
    v = reduce_step(S4_JUDGED, S5_ADMITTED, c, rc)
    assert not v.allow
    assert v.reject_code == REJECT_SPEC_CEILING              # L2b — not REJECT_CEILING_EXCEEDED


def test_supersession_allowed_with_successor():
    c, rc = valid_candidate(successor_id="claim_042")
    v = reduce_step(S5_ADMITTED, S_SUPERSEDED, c, rc)
    assert v.allow
    assert v.next_state == S_SUPERSEDED


def test_supersession_requires_successor_id():
    c, rc = valid_candidate()                               # no successor_id
    v = reduce_step(S5_ADMITTED, S_SUPERSEDED, c, rc)
    assert not v.allow
    assert v.reject_code == REJECT_FORBIDDEN_TRANSITION


# ── determinism (§6) ─────────────────────────────────────────────────────────

def test_determinism_same_input_same_verdict():
    c, rc = valid_candidate()
    a = reduce_step(S4_JUDGED, S5_ADMITTED, c, rc)
    b = reduce_step(S4_JUDGED, S5_ADMITTED, c, rc)
    assert (a.allow, a.next_state, a.reject_code) == (b.allow, b.next_state, b.reject_code)


# ── Spec sync: T3b, T8, T10, T12, T13 ext, L7 (missing from pre-peer-review) ─

def test_T3b_rejected_to_non_terminal_is_forbidden_not_frozen():
    # §2.2 / T3b: S_REJECTED ↛ S5_ADMITTED → REJECT_FORBIDDEN_TRANSITION
    # S_REJECTED is pre-terminal, not S_TERMINAL — L3 (FROZEN) does NOT apply here.
    c, rc = valid_candidate()
    v = reduce_step(S_REJECTED, S5_ADMITTED, c, rc)
    assert not v.allow
    assert v.reject_code == REJECT_FORBIDDEN_TRANSITION


def test_T3b_rejected_to_terminal_is_allowed():
    # S_REJECTED → S_TERMINAL is the one lawful exit from S_REJECTED.
    c, rc = valid_candidate()
    v = reduce_step(S_REJECTED, S_TERMINAL, c, rc)
    assert v.allow
    assert v.next_state == S_TERMINAL


def test_T8_missing_receipt():
    # T8: evidence=[] (no receipt) at S2_TYPED → S3_RECEIPTED → REJECT_NO_RECEIPT (L1).
    c, rc = valid_candidate(evidence=[])
    # also recompute hash to reflect empty evidence
    c["evidence_hash"] = compute_candidate_hash(c)
    v = reduce_step(S2_TYPED, S3_RECEIPTED, c, rc)
    assert not v.allow
    assert v.reject_code == REJECT_NO_RECEIPT


def test_T10_reason_missing():
    # T10: transition to S_REJECTED without reason_code → REJECT_REASON_MISSING (L5).
    c, rc = valid_candidate()
    v = reduce_step(S3_RECEIPTED, S_REJECTED, c, rc)   # no reason_code in valid_candidate
    assert not v.allow
    assert v.reject_code == REJECT_REASON_MISSING


def test_T12_max_state_ceiling_L6():
    # T12: max_state=S3_RECEIPTED; trying to advance to S4_JUDGED → REJECT_BAD_STATE (L6).
    c, rc = valid_candidate(max_state=S3_RECEIPTED)
    v = reduce_step(S3_RECEIPTED, S4_JUDGED, c, rc)
    assert not v.allow
    assert v.reject_code == REJECT_BAD_STATE


def test_T13_superseded_to_terminal_allowed():
    # T13 ext: S_SUPERSEDED → S_TERMINAL is the lawful exit (like S_REJECTED).
    c, rc = valid_candidate()
    v = reduce_step(S_SUPERSEDED, S_TERMINAL, c, rc)
    assert v.allow
    assert v.next_state == S_TERMINAL


def test_T13_superseded_to_non_terminal_is_forbidden():
    # T13: §2.2 — S_SUPERSEDED ↛ any non-terminal → REJECT_FORBIDDEN_TRANSITION.
    c, rc = valid_candidate()
    v = reduce_step(S_SUPERSEDED, S5_ADMITTED, c, rc)
    assert not v.allow
    assert v.reject_code == REJECT_FORBIDDEN_TRANSITION


def test_L7_terminal_field_inconsistency():
    # L7: terminal=True but current state is S2_TYPED (not a terminal state) → REJECT_BAD_STATE.
    c, rc = valid_candidate(terminal=True)
    v = reduce_step(S2_TYPED, S3_RECEIPTED, c, rc)
    assert not v.allow
    assert v.reject_code == REJECT_BAD_STATE


def test_L7_terminal_false_on_non_terminal_passes():
    # L7: terminal=False on a non-terminal state is consistent → no extra rejection.
    c, rc = valid_candidate(terminal=False)
    v = reduce_step(S2_TYPED, S3_RECEIPTED, c, rc)
    assert v.allow

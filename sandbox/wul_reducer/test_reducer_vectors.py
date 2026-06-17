"""
Conformance tests for REDUCER_SPEC_V0 §5 (T1-T7) — NON-SOVEREIGN.

authority = false · canon = NO_SHIP · kernel/ledger effect = none

These are the spec's acceptance criteria made MECHANICAL. Each vector is an input claim
fragment + a requested transition -> the required reducer verdict. The point of the exercise
(operator, 2026-06-17): "the spec is only useful once illegal transitions fail mechanically."

Run:  .venv/bin/pytest sandbox/wul_reducer/test_reducer_vectors.py -v
"""
import pytest

from reducer_ref import reduce


def claim(**over):
    """A schema-shaped claim with safe defaults; override per vector."""
    base = {
        "admission_state": "PENDING",
        "truth_status": "UNVERIFIED",
        "claim_class": "INFERRED",
        "evidence": ["ref"],
        "evidence_hash": "sha256:deadbeef",
        "max_admission_state": "REPLAYABLE",
        "terminal": False,
        "rejection_reason": None,
        "gate_green": True,
        "human_seal": True,
        "replay_check": "PASS",
    }
    base.update(over)
    # keep terminal flag consistent with state unless a vector deliberately breaks it
    if "terminal" not in over:
        base["terminal"] = base["admission_state"] in ("REJECTED", "SUPERSEDED")
    return base


# (id, claim-overrides, target, expected_verdict)
VECTORS = [
    # T1  ILLEGAL PROMOTION (skip review)
    ("T1_skip_review",
     dict(admission_state="PENDING"), "ADMITTED",
     ("REJECT", "E_SKIP_REVIEW")),

    # T2  MISSING HASH (L1)
    ("T2_no_hash",
     dict(admission_state="PENDING_REVIEW", evidence_hash=None), "ADMITTED",
     ("REJECT", "E_NO_HASH")),

    # T3a SEALED TERMINAL STATE — no exit from REJECTED
    ("T3a_terminal_frozen",
     dict(admission_state="REJECTED", terminal=True, rejection_reason="refuted"), "ADMITTED",
     ("REJECT", "E_TERMINAL_FROZEN")),

    # T3b no backward arrow out of SEALED
    ("T3b_reverse_from_sealed",
     dict(admission_state="SEALED"), "PENDING",
     ("REJECT", "E_REVERSE")),

    # T4a REPLAY ADMISSIBILITY — only legal source is SEALED + PASS
    ("T4a_replay_ok",
     dict(admission_state="SEALED", replay_check="PASS"), "REPLAYABLE",
     ("ALLOW", "REPLAYABLE")),

    # T4b must pass through SEAL first
    ("T4b_skip_seal",
     dict(admission_state="ADMITTED"), "REPLAYABLE",
     ("REJECT", "E_SKIP_SEAL")),

    # T4c determinism must hold
    ("T4c_replay_fail",
     dict(admission_state="SEALED", replay_check="FAIL"), "REPLAYABLE",
     ("REJECT", "E_REPLAY_FAIL")),

    # T5  SPECULATIVE CEILING (L2 / Ⓢ ↛ ✅)
    ("T5_spec_ceiling",
     dict(admission_state="PENDING_REVIEW", claim_class="SPECULATIVE"), "ADMITTED",
     ("REJECT", "E_SPEC_CEILING")),

    # T6a TERMINAL CONSISTENCY (L4) — REJECTED must have terminal=true
    ("T6a_terminal_inconsistent",
     dict(admission_state="REJECTED", terminal=False), "ADMITTED",
     ("REJECT", "E_TERMINAL_CONSIST")),

    # T6b REJECTION REASON REQUIRED (L5)
    ("T6b_reason_required",
     dict(admission_state="REJECTED", terminal=True, rejection_reason=None), "ADMITTED",
     ("REJECT", "E_REASON_REQUIRED")),
]


@pytest.mark.parametrize("vid,over,target,expected",
                         VECTORS, ids=[v[0] for v in VECTORS])
def test_vector(vid, over, target, expected):
    assert reduce(claim(**over), target) == expected


def test_T7_happy_path_full_chain():
    """T7 — the only full admission: PENDING -> ... -> REPLAYABLE, ALLOW at each step."""
    c = claim(admission_state="PENDING")

    v = reduce(c, "PENDING_REVIEW")
    assert v == ("ALLOW", "PENDING_REVIEW")
    c["admission_state"] = "PENDING_REVIEW"

    v = reduce(c, "ADMITTED")          # Admit(c) ∧ HumanSeal
    assert v == ("ALLOW", "ADMITTED")
    c["admission_state"] = "ADMITTED"

    v = reduce(c, "SEALED")
    assert v == ("ALLOW", "SEALED")
    c["admission_state"] = "SEALED"

    v = reduce(c, "REPLAYABLE")        # replay_check == PASS
    assert v == ("ALLOW", "REPLAYABLE")


def test_determinism_pure_function():
    """§6 — same inputs -> same verdict, twice, byte-identical."""
    c = claim(admission_state="PENDING_REVIEW")
    assert reduce(c, "ADMITTED") == reduce(dict(c), "ADMITTED")

"""PROOF_CARRYING_RECEIPT — validator kill-suite. 🔵 OBSERVED · authority=false.

Earned boundary on PASS: "the validator admits a well-formed proof-carrying epoch and REJECTS every declared
malformation (authority leak, missing boundary, overclaim, undisclaimed unresolved)." NOT a proof that any
particular scientific claim is true — only that its RECEIPT carries its own boundary.
"""
from dataclasses import replace
import pytest
from helen_os.kernel.proof_carrying_receipt import (
    ProofCarryingEpoch, Prereg, Intervention, Observation, CausalGraph, ClaimBoundary,
    validate, disposition, summarize, ar_ablation_receipt,
)


def test_ar_ablation_receipt_is_admissible_and_progress():
    e = ar_ablation_receipt()
    v, reasons = validate(e)
    assert v == "ADMIT_RECEIPT", reasons
    assert disposition(e) == "PROGRESS"          # H_L1 killed, L2/L3 survive, L4 weakened → moved
    s = summarize(e)
    assert "L2(cognition≠effect)→Q" in s["surviving_edges"]
    assert "L3(what-licenses-the-arrow)→Q" in s["surviving_edges"]


def test_authority_leak_rejected():
    e = replace(ar_ablation_receipt(), authority=True)
    v, r = validate(e)
    assert v == "REJECT" and any("AUTHORITY_LEAK" in x for x in r)


def test_result_without_boundary_rejected():
    e = ar_ablation_receipt()
    cb = replace(e.claim_boundary, forbidden_extrapolations=())
    v, r = validate(replace(e, claim_boundary=cb))
    assert v == "REJECT" and any("NO_FORBIDDEN_EXTRAPOLATIONS" in x for x in r)


def test_overclaim_on_nonsurviving_hypothesis_rejected():
    e = ar_ablation_receipt()
    # license a claim on H_L1 which was KILLED → overclaim
    cb = replace(e.claim_boundary, licensed_refs=("H_L1", "H_L2"))
    v, r = validate(replace(e, claim_boundary=cb))
    assert v == "REJECT" and any("OVERCLAIM" in x for x in r)


def test_undisclaimed_unresolved_rejected():
    e = ar_ablation_receipt()
    # drop the disclaimer of the unresolved L5-L7
    cb = replace(e.claim_boundary, forbidden_refs=())
    v, r = validate(replace(e, claim_boundary=cb))
    assert v == "REJECT" and any("UNDISCLAIMED_UNRESOLVED" in x for x in r)


def test_no_progress_receipt_is_valid_but_HOLD():
    e = ar_ablation_receipt()
    allU = {h: "UNRESOLVED" for h in e.hypotheses}
    cb = replace(e.claim_boundary, licensed_refs=(), forbidden_refs=tuple(allU.keys()),
                 forbidden_extrapolations=("no discriminating experiment under budget",))
    e2 = replace(e, hypotheses=allU, claim_boundary=cb)
    v, r = validate(e2)
    assert v == "ADMIT_RECEIPT", r                # valid receipt...
    assert disposition(e2) == "HOLD"              # ...but HOLD: knowing we cannot discriminate


def test_undisposed_hypothesis_rejected():
    e = ar_ablation_receipt()
    h = dict(e.hypotheses); h["H_L2"] = "MAYBE"   # not a valid disposition
    v, r = validate(replace(e, hypotheses=h))
    assert v == "REJECT" and any("BAD_DISPOSITION" in x for x in r)

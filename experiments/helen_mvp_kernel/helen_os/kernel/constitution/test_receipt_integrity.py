"""Receipt integrity falsified: an untyped hex may not be verified as
anything; an unrun recipe leaves the claim FABRICATED_UNTIL_WITNESSED;
classes never aggregate as a vote; a digest without its recipe is not
a receipt; and a seal needs all four witnesses.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import receipt_integrity as ri
from receipt_integrity import (
    aggregate,
    proof_carrying_receipt,
    re_derive,
    receipt_integrity,
    reflexive_law,
    seal,
    type_hex,
    verify_receipt,
)


# ── typing precedes verification ───────────────────────────────────────

def test_an_untyped_hex_may_not_be_verified_as_anything():
    v = type_hex("16ea385e82213c7c", declared_type=None)
    assert v["verifiable"] is False
    assert v["reason"] == "E_UNTYPED_HEX"


def test_a_typed_gmail_id_is_not_run_through_git():
    v = type_hex("16ea385e82213c7c", "GMAIL_THREAD_ID")
    assert v["verifiable"] is True
    assert "GitObjectExists" not in v["verify_with"]


def test_a_typed_git_hash_gets_the_git_verifier():
    v = type_hex("66836cb", "GIT_HASH")
    assert v["verify_with"] == "GitObjectExists"


def test_unknown_stays_unverifiable_even_when_declared():
    assert type_hex("deadbeef", "UNKNOWN")["verifiable"] is False


# ── re-derivation ──────────────────────────────────────────────────────

def test_an_unrun_recipe_leaves_the_claim_fabricated():
    v = re_derive("C_test", recipe_ran=False, result_matches=False)
    assert v["status"] == "FABRICATED_UNTIL_WITNESSED"
    assert v["reason"] == "E_RECIPE_NOT_RUN"


def test_a_mismatch_is_fabricated_not_approximate():
    v = re_derive("C_gate", True, result_matches=False)
    assert v["status"] == "FABRICATED_UNTIL_WITNESSED"
    assert v["reason"] == "E_REDERIVATION_MISMATCH"


def test_a_matching_rerun_passes_with_its_recipe_named():
    v = re_derive("C_canon", True, True)
    assert v["status"] == "PASS"
    assert v["recipe"] == "RunSelfTest()"


def test_the_five_claim_classes_each_carry_their_operator():
    assert set(ri.CLAIM_CLASSES) == {"C_test", "C_gate", "C_commit",
                                     "C_canon", "C_pii"}
    assert re_derive("C_vibes", True, True)["reason"] == \
        "E_UNKNOWN_CLAIM_CLASS"


# ── RI = T and D and S ─────────────────────────────────────────────────

def _scope():
    return {k: "x" for k in ri.SCOPE_FIELDS}


def test_rederivable_does_not_entail_universally_valid():
    v = receipt_integrity(typed=True, rederivable=True, scope={})
    assert v["RI"] is False
    assert v["reason"] == "E_UNSCOPED_CLAIM"
    assert "gate_version" in v["missing_scope"]


def test_all_three_parts_or_no_integrity():
    assert receipt_integrity(True, True, _scope())["RI"] is True
    assert receipt_integrity(False, True, _scope())["reason"] == \
        "E_UNTYPED_CLAIM"
    assert receipt_integrity(True, False, _scope())["reason"] == \
        "E_NOT_REDERIVABLE"


# ── aggregation by class, never by vote ────────────────────────────────

def _all_pass():
    return {k: "PASS" for k in ri.CLAIM_CLASSES}


def test_vote_aggregation_is_a_category_error():
    v = aggregate(_all_pass(), as_vote=True)
    assert v["aggregated"] is False
    assert v["reason"] == "E_VOTE_ACROSS_CLASSES"


def test_one_pending_class_holds_the_audit_open():
    r = _all_pass()
    r["C_pii"] = "PENDING"
    v = aggregate(r)
    assert v["verdict"] == "PARTIALLY_DISCHARGED"
    assert v["pending"] == ("C_pii",)


def test_all_classes_pass_discharges_the_audit():
    v = aggregate(_all_pass())
    assert v["verdict"] == "DISCHARGED"


def test_a_fabricated_class_marks_the_whole_audit():
    r = _all_pass()
    r["C_commit"] = "FABRICATED_UNTIL_WITNESSED"
    v = aggregate(r)
    assert v["verdict"] == "FABRICATED_UNTIL_WITNESSED_IN_PART"
    assert v["failed"] == ("C_commit",)


def test_a_missing_class_is_partial_even_if_all_present_pass():
    r = _all_pass()
    del r["C_canon"]
    assert aggregate(r)["verdict"] == "PARTIALLY_DISCHARGED"


# ── the proof-carrying receipt ─────────────────────────────────────────

def test_a_digest_without_its_recipe_is_not_a_receipt():
    v = proof_carrying_receipt(claim="gate 82/82", digest="65e58753")
    assert v["ok"] is False
    assert v["reason"] == "E_RECIPE_LESS_RECEIPT"
    assert "derivation_recipe" in v["missing"]


def _receipt():
    return proof_carrying_receipt(
        claim="gate 82/82 CONSTITUTION_HELD",
        substrate_ref="helen-conquest@0403f87",
        derivation_recipe="python -m helen_os.kernel.constitution",
        environment="py3.11 container",
        scope=_scope(), result="82/82 CONSTITUTION_HELD",
        digest="65e58753")


def test_verify_receipt_reruns_the_recipe_and_compares():
    ok = verify_receipt(_receipt(), "82/82 CONSTITUTION_HELD")
    assert ok["verified"] is True and ok["status"] == "PASS"
    bad = verify_receipt(_receipt(), "81/82 CONSTITUTION_BREACHED")
    assert bad["verified"] is False
    assert bad["status"] == "FABRICATED_UNTIL_WITNESSED"


# ── the seal and the reflexive law ─────────────────────────────────────

def test_a_seal_needs_all_four_witnesses():
    v = seal(frozenset({"intent", "test", "post_mutation"}))
    assert v["sealed"] is False
    assert v["reason"] == "E_INCOMPLETE_SEAL"
    assert v["missing"] == ("mutation",)
    assert v["status"] == "FABRICATED_UNTIL_WITNESSED"


def test_the_four_witness_seal_passes():
    assert seal(frozenset(ri.SEAL_WITNESSES))["sealed"] is True


def test_the_kernel_membrane_applies_to_its_own_metadata():
    v = reflexive_law()
    assert v["licensed"] is False
    assert "DescriptionOfKernelState !=> KernelState" in \
        v["non_implications"]
    assert len(v["non_implications"]) == 4


def test_deterministic():
    assert ri.canon(aggregate(_all_pass())) == \
        ri.canon(aggregate(_all_pass()))

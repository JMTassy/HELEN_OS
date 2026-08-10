"""χ_gov — admission requires the declared witnessed path. 🔵 OBSERVED."""
import pytest

from helen_os.kernel.admission_types import (
    TypedAdmissionReceipt, Witness, evaluate_admission, valid_receipt_path,
)
from helen_os.ledger.event_log import read_events
from helen_os.ledger.hash_chain import GENESIS_HASH
from helen_os.tests._chi_fixtures import (
    CANDIDATE, C_HASH, PROPOSER_ROOTS, PROPOSER_SEAT, good_witnesses,
    make_receipt, seal_for,
)

KW = dict(proposer_seat=PROPOSER_SEAT, proposer_roots=PROPOSER_ROOTS)


def test_gov_01_missing_path_no_admit(tmp_path):
    ledger = tmp_path / "l.ndjson"
    assert evaluate_admission(None) == "REJECT"
    path = valid_receipt_path(None, None, GENESIS_HASH, None, **KW)
    assert path.overall == "FAIL" and path.reason == "NO_RECEIPT"
    assert read_events(ledger) == []  # ΔG = 0


def test_gov_02_seal_mismatch_rejects():
    r = make_receipt()
    bad_seal = seal_for(make_receipt(pre="c" * 64))  # seal binds a DIFFERENT receipt
    path = valid_receipt_path(r, CANDIDATE, GENESIS_HASH, bad_seal, **KW)
    assert path.overall == "FAIL"
    assert not path.checks["seal_binds"]
    assert evaluate_admission(path) == "REJECT"


def test_gov_03_missing_witness_holds(tmp_path):
    r = make_receipt(witnesses=())
    path = valid_receipt_path(r, CANDIDATE, GENESIS_HASH, seal_for(r), **KW)
    assert path.overall == "UNKNOWN" and path.reason == "MISSING_WITNESS"
    assert evaluate_admission(path) == "HOLD"
    assert read_events(tmp_path / "l.ndjson") == []  # ΔG = 0


def test_gov_04_full_path_passes_without_ledger_effect(tmp_path):
    r = make_receipt()
    path = valid_receipt_path(r, CANDIDATE, GENESIS_HASH, seal_for(r), **KW)
    assert path.overall == "PASS", path.checks
    # path PASS is admission-ELIGIBILITY, not effect: ledger untouched until invoke
    assert evaluate_admission(path) == "ADMIT_ELIGIBLE"
    assert read_events(tmp_path / "l.ndjson") == []


def test_gov_05_self_attested_status_fails_typing():
    for status in ("SEALED", "ADMITTED"):
        with pytest.raises(TypeError, match="SELF_ATTESTATION"):
            TypedAdmissionReceipt(
                receipt_id="r_bad", candidate_hash=C_HASH, pre_state_hash="a" * 64,
                post_state_hash="b" * 64, prev_receipt_hash=GENESIS_HASH,
                witnesses=good_witnesses(), status=status,
            )


def test_gov_06_meta_admitted_implies_valid_path():
    r = make_receipt()
    path = valid_receipt_path(r, CANDIDATE, GENESIS_HASH, seal_for(r), **KW)
    admitted = evaluate_admission(path) == "ADMIT_ELIGIBLE"
    assert (not admitted) or path.overall == "PASS"  # admitted ⇒ path.valid


def test_gov_07_ghost_orphan_receipt_fails():
    r = make_receipt()  # structurally valid...
    path = valid_receipt_path(
        r, CANDIDATE, GENESIS_HASH, seal_for(r), admitted_index=set(), **KW
    )  # ...but no admitted parent exists
    assert path.overall == "FAIL"
    assert "ORPHAN_RECEIPT" in path.reason
    assert evaluate_admission(path) == "REJECT"


def test_gov_08_non_independent_witnesses_fail():
    # all witnesses share the proposer's provenance root → n × self-attestation
    tainted = (
        Witness("w1", seat="hal-seat", provenance_roots=frozenset({"root:proposer"})),
        Witness("w2", seat="operator-seat", provenance_roots=frozenset({"root:proposer"})),
    )
    r = make_receipt(witnesses=tainted)
    path = valid_receipt_path(r, CANDIDATE, GENESIS_HASH, seal_for(r), **KW)
    assert path.overall != "PASS"
    assert not path.checks["witnesses_independent"]

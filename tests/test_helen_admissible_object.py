"""
tests/test_helen_admissible_object.py — falsification suite for AdmissibleObject

Invariants under test:
  1. authority is always False, even after admission
  2. β returns ∅ if any required field is missing
  3. ∅ object is not admissible
  4. Full β pipeline produces ADMISSIBLE status
  5. Stage helpers advance status monotonically

Run: .venv/bin/pytest tests/test_helen_admissible_object.py -v
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import pytest
from src.helen_admissible_object import (
    AdmissibleObject, beta, bind_source, split_claim, attach_evidence, flag_risk,
    DIRTY, SOURCE_BOUND, CLAIM_SPLIT, EVIDENCE_ATTACHED, RISK_FLAGGED, ADMISSIBLE, EMPTY,
)

# ── helpers ───────────────────────────────────────────────────────────────

def _full_beta(obj=None):
    if obj is None:
        obj = AdmissibleObject.new_dirty()
    return beta(obj, "src_001", ["ev_001"], "PASS", "rcpt_001", "replay_001")


# ── 1. authority invariant ─────────────────────────────────────────────────

def test_new_dirty_authority_false():
    obj = AdmissibleObject.new_dirty()
    assert obj.authority is False

def test_admissible_authority_still_false():
    adm = _full_beta()
    assert adm.authority is False

def test_empty_authority_false():
    assert AdmissibleObject.empty().authority is False


# ── 2. β returns ∅ on missing fields ──────────────────────────────────────

def test_beta_missing_source_returns_empty():
    obj = AdmissibleObject.new_dirty()
    result = beta(obj, None, ["ev_001"], "PASS", "rcpt_001", "replay_001")
    assert result.is_empty()

def test_beta_empty_evidence_returns_empty():
    obj = AdmissibleObject.new_dirty()
    result = beta(obj, "src_001", [], "PASS", "rcpt_001", "replay_001")
    assert result.is_empty()

def test_beta_fail_validator_returns_empty():
    obj = AdmissibleObject.new_dirty()
    result = beta(obj, "src_001", ["ev_001"], "FAIL", "rcpt_001", "replay_001")
    assert result.is_empty()

def test_beta_missing_receipt_returns_empty():
    obj = AdmissibleObject.new_dirty()
    result = beta(obj, "src_001", ["ev_001"], "PASS", None, "replay_001")
    assert result.is_empty()

def test_beta_missing_replay_returns_empty():
    obj = AdmissibleObject.new_dirty()
    result = beta(obj, "src_001", ["ev_001"], "PASS", "rcpt_001", None)
    assert result.is_empty()


# ── 3. ∅ object ────────────────────────────────────────────────────────────

def test_empty_is_not_admissible():
    assert not AdmissibleObject.empty().is_admissible()

def test_empty_status():
    assert AdmissibleObject.empty().status == EMPTY

def test_empty_object_id():
    assert AdmissibleObject.empty().object_id == "∅"


# ── 4. full β pipeline ─────────────────────────────────────────────────────

def test_beta_full_produces_admissible():
    adm = _full_beta()
    assert adm.is_admissible()
    assert adm.status == ADMISSIBLE

def test_beta_preserves_object_id():
    obj = AdmissibleObject.new_dirty()
    adm = _full_beta(obj)
    assert adm.object_id == obj.object_id

def test_beta_sets_receipt_and_replay():
    adm = _full_beta()
    assert adm.receipt_ref == "rcpt_001"
    assert adm.replay_path == "replay_001"


# ── 5. stage helpers ───────────────────────────────────────────────────────

def test_bind_source_advances_status():
    obj = AdmissibleObject.new_dirty()
    assert obj.status == DIRTY
    obj2 = bind_source(obj, "src_abc")
    assert obj2.status == SOURCE_BOUND
    assert obj2.source_ref == "src_abc"

def test_split_claim_accumulates():
    obj = AdmissibleObject.new_dirty()
    obj = split_claim(obj, "claim_001")
    obj = split_claim(obj, "claim_002")
    assert obj.status == CLAIM_SPLIT
    assert len(obj.claims) == 2

def test_attach_evidence_accumulates():
    obj = AdmissibleObject.new_dirty()
    obj = attach_evidence(obj, "ev_001")
    obj = attach_evidence(obj, "ev_002")
    assert obj.status == EVIDENCE_ATTACHED
    assert "ev_002" in obj.evidence_refs

def test_flag_risk_accumulates():
    obj = AdmissibleObject.new_dirty()
    obj = flag_risk(obj, "hallucination_risk")
    assert obj.status == RISK_FLAGGED
    assert "hallucination_risk" in obj.risk_flags

def test_full_pipeline_stages():
    obj = AdmissibleObject.new_dirty()
    obj = bind_source(obj, "src_001")
    obj = split_claim(obj, "claim_001")
    obj = attach_evidence(obj, "ev_001")
    obj = flag_risk(obj, "low_confidence")
    adm = beta(obj, "src_001", ["ev_001"], "PASS", "rcpt_001", "replay_001")
    assert adm.is_admissible()
    assert adm.authority is False
    assert "low_confidence" in adm.risk_flags

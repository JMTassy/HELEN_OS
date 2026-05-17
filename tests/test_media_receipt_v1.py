"""
Tests for MEDIA_RECEIPT_V1.

HAL contract (10 cases):
    1. valid candidate receipt
    2. missing identity sequence receipt
    3. rejected identity sequence blocks validity
    4. rework identity sequence blocks admissibility
    5. missing render hash
    6. missing source refs hash
    7. authority=true rejected
    8. admissible=true rejected
    9. referenced gate missing rejected
    10. receipt does not mutate ledger

Binds the validator at helen_os/governance/media_receipt_validator.py
against the doctrine at docs/proposals/MEDIA_RECEIPT_V1.md.

Final lock:
    IDENTITY SEQUENCE = tested.
    MEDIA RECEIPT     = tested.
    ADMISSIBILITY     = still reducer-only.
"""
import copy
import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from helen_os.governance.media_receipt_validator import (
    MEDIA_RECEIPT_LEDGER_PATH,
    validate_media_receipt,
)


# ─── Helpers ──────────────────────────────────────────────────────────────
def make_valid_receipt() -> dict:
    """A minimal, schema-valid, doctrinally-correct MEDIA_RECEIPT_V1."""
    return {
        "type": "MEDIA_RECEIPT_V1",
        "media_receipt_id": "MR-TEST-0001",
        "project_id": "test-project",
        "timestamp": "2026-05-17T16:00:00Z",
        "asset_chain": {
            "source_refs_hash":     "sha256:source-001",
            "storyboard_hash":      "sha256:storyboard-001",
            "director_packet_hash": "sha256:director-001",
            "composition_hash":     "sha256:composition-001",
            "render_hash":          "sha256:render-001",
        },
        "gate_chain": {
            "identity_gate_sequence_receipt_hash": "sha256:id-seq-001",
            "style_gate_receipt_hash":             "sha256:style-001",
            "artifact_gate_receipt_hash":          "sha256:artifact-001",
        },
        "identity_sequence_verdict": "PASS",
        "candidacy": {
            "admissibility_status": "ELIGIBLE",
            "blocking_reasons": [],
        },
        "context": {"render_backend": "test", "operator": "PRAXIS-01"},
        "authority": False,
        "admissible": False,
        "claim": "NO_CLAIM",
        "previous_receipts": [],
        "cumulative_hash": "sha256:cum-001",
    }


def make_sequence_store(verdict: str = "PASS") -> dict:
    """A minimal identity_sequence_store with one referenced sequence receipt."""
    return {
        "sha256:id-seq-001": {
            "type": "IDENTITY_GATE_RECEIPT_V1_SEQUENCE",
            "decision": {"verdict": verdict, "confidence": 0.9},
        }
    }


def gate_stores() -> tuple[dict, dict]:
    """Style + artifact gate stores with the default referenced hashes present."""
    return (
        {"sha256:style-001": True},
        {"sha256:artifact-001": True},
    )


# ─── Test 1 ────────────────────────────────────────────────────────────────
def test_1_valid_candidate_receipt_eligible():
    """Valid receipt + PASS identity sequence → valid + ELIGIBLE."""
    receipt = make_valid_receipt()
    seq_store = make_sequence_store("PASS")
    style, artifact = gate_stores()
    result = validate_media_receipt(
        receipt,
        identity_sequence_store=seq_store,
        style_gate_store=style,
        artifact_gate_store=artifact,
    )
    assert result["valid"], f"unexpected violations: {result['details']}"
    assert result["admissibility_status"] == "ELIGIBLE"


# ─── Test 2 ────────────────────────────────────────────────────────────────
def test_2_missing_identity_sequence_receipt_rejected():
    """Missing identity_gate_sequence_receipt_hash → MISSING_IDENTITY_SEQUENCE."""
    receipt = make_valid_receipt()
    receipt["gate_chain"]["identity_gate_sequence_receipt_hash"] = ""
    result = validate_media_receipt(receipt)
    assert not result["valid"]
    assert "MISSING_IDENTITY_SEQUENCE" in result["violations"]


# ─── Test 3 ────────────────────────────────────────────────────────────────
def test_3_rejected_identity_sequence_blocks_validity():
    """Identity sequence verdict is REJECT → media receipt invalid + BLOCKED."""
    receipt = make_valid_receipt()
    # Receipt's own candidacy declaration also matches BLOCKED so we don't
    # get a CANDIDACY_MISMATCH on top of BLOCKED_BY_REJECT
    receipt["candidacy"]["admissibility_status"] = "BLOCKED"
    seq_store = make_sequence_store("REJECT")
    result = validate_media_receipt(
        receipt,
        identity_sequence_store=seq_store,
    )
    assert not result["valid"]
    assert "BLOCKED_BY_REJECT" in result["violations"]
    assert result["admissibility_status"] == "BLOCKED"


# ─── Test 4 ────────────────────────────────────────────────────────────────
def test_4_rework_identity_sequence_allows_candidate_only():
    """Identity sequence verdict is REWORK → valid (no violations) + CANDIDATE_ONLY."""
    receipt = make_valid_receipt()
    receipt["candidacy"]["admissibility_status"] = "CANDIDATE_ONLY"
    seq_store = make_sequence_store("REWORK")
    style, artifact = gate_stores()
    result = validate_media_receipt(
        receipt,
        identity_sequence_store=seq_store,
        style_gate_store=style,
        artifact_gate_store=artifact,
    )
    assert result["valid"], f"unexpected violations: {result['details']}"
    assert result["admissibility_status"] == "CANDIDATE_ONLY"


# ─── Test 5 ────────────────────────────────────────────────────────────────
def test_5_missing_render_hash_rejected():
    """Missing asset_chain.render_hash → MISSING_RENDER_HASH."""
    receipt = make_valid_receipt()
    receipt["asset_chain"]["render_hash"] = ""
    result = validate_media_receipt(receipt)
    assert not result["valid"]
    assert "MISSING_RENDER_HASH" in result["violations"]


# ─── Test 6 ────────────────────────────────────────────────────────────────
def test_6_missing_source_refs_hash_rejected():
    """Missing asset_chain.source_refs_hash → MISSING_SOURCE_REFS_HASH."""
    receipt = make_valid_receipt()
    receipt["asset_chain"]["source_refs_hash"] = ""
    result = validate_media_receipt(receipt)
    assert not result["valid"]
    assert "MISSING_SOURCE_REFS_HASH" in result["violations"]


# ─── Test 7 ────────────────────────────────────────────────────────────────
def test_7_authority_true_rejected():
    """authority=true → AUTHORITY_VIOLATION."""
    receipt = make_valid_receipt()
    receipt["authority"] = True
    result = validate_media_receipt(receipt)
    assert not result["valid"]
    assert "AUTHORITY_VIOLATION" in result["violations"]


# ─── Test 8 ────────────────────────────────────────────────────────────────
def test_8_admissible_true_rejected():
    """admissible=true → ADMISSIBILITY_VIOLATION (media receipt never admits)."""
    receipt = make_valid_receipt()
    receipt["admissible"] = True
    result = validate_media_receipt(receipt)
    assert not result["valid"]
    assert "ADMISSIBILITY_VIOLATION" in result["violations"]


# ─── Test 9 ────────────────────────────────────────────────────────────────
def test_9_referenced_gate_missing_rejected():
    """A referenced style/artifact gate hash not in store → REFERENCED_GATE_MISSING."""
    receipt = make_valid_receipt()
    seq_store = make_sequence_store("PASS")
    # style gate store does NOT include the referenced sha256:style-001
    empty_style = {}
    artifact = {"sha256:artifact-001": True}
    result = validate_media_receipt(
        receipt,
        identity_sequence_store=seq_store,
        style_gate_store=empty_style,
        artifact_gate_store=artifact,
    )
    assert not result["valid"]
    assert "REFERENCED_GATE_MISSING" in result["violations"]


# ─── Test 10 ───────────────────────────────────────────────────────────────
def test_10_validator_does_not_mutate_or_write_ledger(tmp_path):
    """
    The validator must:
    1. Not mutate the input receipt (deep equality before/after).
    2. Be idempotent (same input → same output, every call).
    3. Not create the media receipt ledger file.
    """
    receipt = make_valid_receipt()
    snapshot = copy.deepcopy(receipt)
    seq_store = make_sequence_store("PASS")
    snapshot_store = copy.deepcopy(seq_store)
    style, artifact = gate_stores()

    # Ledger file should not exist before the call
    ledger_full = tmp_path / MEDIA_RECEIPT_LEDGER_PATH
    assert not ledger_full.exists()

    r1 = validate_media_receipt(
        receipt,
        identity_sequence_store=seq_store,
        style_gate_store=style,
        artifact_gate_store=artifact,
    )
    r2 = validate_media_receipt(
        receipt,
        identity_sequence_store=seq_store,
        style_gate_store=style,
        artifact_gate_store=artifact,
    )

    # 1. Input not mutated
    assert receipt == snapshot, "validator must not mutate the receipt"
    assert seq_store == snapshot_store, "validator must not mutate the sequence store"

    # 2. Idempotent
    assert r1 == r2, "validator must be idempotent"

    # 3. No ledger file created
    assert not ledger_full.exists(), "validator must not write to the media receipt ledger"

    # Also verify the path constant matches the doctrine
    assert MEDIA_RECEIPT_LEDGER_PATH == "ledgers/media_receipt_v1.ndjson"

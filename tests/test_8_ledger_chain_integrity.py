"""
Constitutional Test 8: Ledger Chain Integrity

This test proves the ledger is append-only and tamper-detecting.

Test Strategy:
1. Create ledger, append entries, verify chain passes
2. Tamper with entries (modify payload, change hash, reorder lines)
3. Assert verify_chain() detects tampering

Receipt Value:
- Proves "append-only ledger" is not just a slogan
- Cryptographically detects any modification
- Mayor can trust ledger references (seq + sha256)
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from oracle_town.core.ledger import AppendOnlyLedger


def test_ledger_append_and_verify_clean_chain(tmp_path: Path):
    """Clean ledger chain verifies successfully"""
    ledger_path = tmp_path / "ledger.jsonl"
    ledger = AppendOnlyLedger(ledger_path)

    # Append entries
    e1 = ledger.append("RECEIPT_BUNDLE_REF", {
        "bundle_id": "RCPT-001",
        "sha256": "a" * 64,
        "run_id": "RUN-001",
    })
    e2 = ledger.append("ATTESTATION_REF", {
        "attestation_id": "ATT-001",
        "sha256": "b" * 64,
        "obligation_name": "tests_green",
    })
    e3 = ledger.append("DECISION_REF", {
        "decision_id": "DEC-001",
        "sha256": "c" * 64,
        "status": "SHIP",
    })

    # Verify properties
    assert e1.seq == 1
    assert e1.prev_hash == "0" * 64  # Genesis
    assert e2.seq == 2
    assert e2.prev_hash == e1.canonical_sha256
    assert e3.seq == 3
    assert e3.prev_hash == e2.canonical_sha256

    # Verify chain
    ledger.verify_chain()  # Should not raise


def test_ledger_detects_payload_tampering(tmp_path: Path):
    """Ledger detects if entry payload is modified"""
    ledger_path = tmp_path / "ledger.jsonl"
    ledger = AppendOnlyLedger(ledger_path)

    e1 = ledger.append("RECEIPT_BUNDLE_REF", {"bundle_id": "RCPT-001", "sha256": "a" * 64})
    e2 = ledger.append("ATTESTATION_REF", {"attestation_id": "ATT-001", "sha256": "b" * 64})

    # Should verify before tampering
    ledger.verify_chain()

    # Tamper: modify payload in last entry
    lines = ledger_path.read_text(encoding="utf-8").splitlines()
    last_entry = json.loads(lines[-1])
    last_entry["payload"]["sha256"] = "c" * 64  # Changed!
    lines[-1] = json.dumps(last_entry, ensure_ascii=False)
    ledger_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Now verification must fail
    ledger_tampered = AppendOnlyLedger(ledger_path)
    with pytest.raises(AssertionError) as exc_info:
        ledger_tampered.verify_chain()

    assert "canonical_sha256" in str(exc_info.value) or "modified" in str(exc_info.value).lower()


def test_ledger_detects_hash_tampering(tmp_path: Path):
    """Ledger detects if canonical_sha256 is modified"""
    ledger_path = tmp_path / "ledger.jsonl"
    ledger = AppendOnlyLedger(ledger_path)

    e1 = ledger.append("RECEIPT_BUNDLE_REF", {"bundle_id": "RCPT-001", "sha256": "a" * 64})
    e2 = ledger.append("ATTESTATION_REF", {"attestation_id": "ATT-001", "sha256": "b" * 64})

    ledger.verify_chain()

    # Tamper: change canonical_sha256
    lines = ledger_path.read_text(encoding="utf-8").splitlines()
    last_entry = json.loads(lines[-1])
    last_entry["canonical_sha256"] = "f" * 64  # Forged hash!
    lines[-1] = json.dumps(last_entry, ensure_ascii=False)
    ledger_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    ledger_tampered = AppendOnlyLedger(ledger_path)
    with pytest.raises(AssertionError) as exc_info:
        ledger_tampered.verify_chain()

    assert "canonical_sha256" in str(exc_info.value)


def test_ledger_detects_reordering(tmp_path: Path):
    """Ledger detects if entries are reordered"""
    ledger_path = tmp_path / "ledger.jsonl"
    ledger = AppendOnlyLedger(ledger_path)

    e1 = ledger.append("RECEIPT_BUNDLE_REF", {"bundle_id": "RCPT-001", "sha256": "a" * 64})
    e2 = ledger.append("ATTESTATION_REF", {"attestation_id": "ATT-001", "sha256": "b" * 64})
    e3 = ledger.append("DECISION_REF", {"decision_id": "DEC-001", "sha256": "c" * 64})

    ledger.verify_chain()

    # Tamper: swap lines 2 and 3
    lines = ledger_path.read_text(encoding="utf-8").splitlines()
    lines[1], lines[2] = lines[2], lines[1]
    ledger_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    ledger_tampered = AppendOnlyLedger(ledger_path)
    with pytest.raises(AssertionError) as exc_info:
        ledger_tampered.verify_chain()

    # Should fail on seq or prev_hash mismatch
    assert "seq" in str(exc_info.value).lower() or "prev_hash" in str(exc_info.value).lower()


def test_ledger_detects_deletion(tmp_path: Path):
    """Ledger detects if entries are deleted"""
    ledger_path = tmp_path / "ledger.jsonl"
    ledger = AppendOnlyLedger(ledger_path)

    e1 = ledger.append("RECEIPT_BUNDLE_REF", {"bundle_id": "RCPT-001", "sha256": "a" * 64})
    e2 = ledger.append("ATTESTATION_REF", {"attestation_id": "ATT-001", "sha256": "b" * 64})
    e3 = ledger.append("DECISION_REF", {"decision_id": "DEC-001", "sha256": "c" * 64})

    ledger.verify_chain()

    # Tamper: delete middle entry
    lines = ledger_path.read_text(encoding="utf-8").splitlines()
    del lines[1]  # Remove e2
    ledger_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    ledger_tampered = AppendOnlyLedger(ledger_path)
    with pytest.raises(AssertionError) as exc_info:
        ledger_tampered.verify_chain()

    # Should fail on seq mismatch (expects 1, 2, 3 but gets 1, 3)
    assert "seq" in str(exc_info.value).lower()


def test_ledger_get_entries_by_type(tmp_path: Path):
    """Ledger can filter entries by type (for Mayor queries)"""
    ledger_path = tmp_path / "ledger.jsonl"
    ledger = AppendOnlyLedger(ledger_path)

    e1 = ledger.append("RECEIPT_BUNDLE_REF", {"bundle_id": "RCPT-001", "sha256": "a" * 64})
    e2 = ledger.append("ATTESTATION_REF", {"attestation_id": "ATT-001", "sha256": "b" * 64})
    e3 = ledger.append("RECEIPT_BUNDLE_REF", {"bundle_id": "RCPT-002", "sha256": "c" * 64})
    e4 = ledger.append("DECISION_REF", {"decision_id": "DEC-001", "sha256": "d" * 64})

    # Query
    receipts = ledger.get_entries_by_type("RECEIPT_BUNDLE_REF")
    attestations = ledger.get_entries_by_type("ATTESTATION_REF")
    decisions = ledger.get_entries_by_type("DECISION_REF")

    assert len(receipts) == 2
    assert len(attestations) == 1
    assert len(decisions) == 1

    assert receipts[0].payload["bundle_id"] == "RCPT-001"
    assert receipts[1].payload["bundle_id"] == "RCPT-002"
    assert attestations[0].payload["attestation_id"] == "ATT-001"
    assert decisions[0].payload["decision_id"] == "DEC-001"


def test_ledger_empty_chain_verifies(tmp_path: Path):
    """Empty ledger verifies successfully (edge case)"""
    ledger_path = tmp_path / "ledger.jsonl"
    ledger = AppendOnlyLedger(ledger_path)

    assert ledger._read_lines() == [], "Ledger must start empty"
    ledger.verify_chain()  # Raises AssertionError if chain is broken
    assert ledger._last_entry() is None, "Empty ledger has no last entry"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

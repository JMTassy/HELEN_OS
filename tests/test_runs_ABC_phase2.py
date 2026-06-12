#!/usr/bin/env python3
"""
Phase-2 Integration Tests: Adversarial Runs A/B/C

Tests that Mayor decisions flip correctly based on cryptographic receipts:

Run A: Valid CI signature, missing LEGAL class → NO_SHIP (QUORUM_NOT_MET)
Run B: Valid CI + LEGAL signed with revoked key → NO_SHIP (KEY_REVOKED)
Run C: Valid CI + Valid LEGAL → SHIP

Each test verifies:
1. Decision is correct (SHIP/NO_SHIP)
2. Reason code is correct
3. Signatures are cryptographically verified (not just string checks)
"""

import pytest
pytestmark = pytest.mark.integration
import json
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from oracle_town.core.mayor_rsm import MayorRSM
from oracle_town.core.policy import Policy


VECTORS_DIR = Path(__file__).parent.parent / "oracle_town" / "test_vectors"
KEYS_DIR = Path(__file__).parent.parent / "oracle_town" / "keys"


def load_run(run_suffix: str) -> tuple:
    """Load policy, briefcase, and ledger for a test run"""
    # Load policy
    with open(VECTORS_DIR / "policy_POL-TEST-1.json", 'r') as f:
        policy_data = json.load(f)

    # Create Policy object
    policy = Policy.from_dict(policy_data)

    # Load briefcase (base, modify run_id as needed)
    with open(VECTORS_DIR / "briefcase_base.json", 'r') as f:
        briefcase = json.load(f)

    # Load ledger
    ledger_file = f"ledger_{run_suffix}.json"
    with open(VECTORS_DIR / ledger_file, 'r') as f:
        ledger = json.load(f)

    # Sync run_id and claim_id
    briefcase["run_id"] = ledger["run_id"]

    return policy, briefcase, ledger


@pytest.fixture
def mayor_with_registry():
    """Create Mayor with key registry loaded"""
    keys_path = KEYS_DIR / "public_keys.json"
    return MayorRSM(public_keys_path=str(keys_path))


class TestRunA:
    """Run A: Missing LEGAL class → NO_SHIP"""

    def test_decision_is_no_ship(self, mayor_with_registry):
        """Run A must produce NO_SHIP decision"""
        policy, briefcase, ledger = load_run("runA_missing_legal")
        decision = mayor_with_registry.decide(policy, briefcase, ledger)

        assert decision.decision == "NO_SHIP", (
            f"Run A should NO_SHIP but got {decision.decision}"
        )

    def test_reason_is_quorum_not_met(self, mayor_with_registry):
        """Run A must fail for QUORUM_NOT_MET (missing LEGAL)"""
        policy, briefcase, ledger = load_run("runA_missing_legal")
        decision = mayor_with_registry.decide(policy, briefcase, ledger)

        # Check that blocking reasons mention quorum or missing class
        reasons_str = " ".join(decision.blocking_reasons)
        assert "missing" in reasons_str.lower() or "quorum" in reasons_str.lower(), (
            f"Expected quorum failure, got: {decision.blocking_reasons}"
        )

    def test_ci_signature_is_valid(self, mayor_with_registry):
        """CI attestation in Run A has valid signature"""
        policy, briefcase, ledger = load_run("runA_missing_legal")

        # The CI attestation should pass signature verification
        # We verify this by ensuring decision doesn't fail on SIGNATURE_INVALID
        decision = mayor_with_registry.decide(policy, briefcase, ledger)

        for reason in decision.blocking_reasons:
            assert "SIGNATURE_INVALID" not in reason, (
                f"CI signature should be valid, got: {reason}"
            )


class TestRunB:
    """Run B: Revoked key → NO_SHIP"""

    def test_decision_is_no_ship(self, mayor_with_registry):
        """Run B must produce NO_SHIP decision"""
        policy, briefcase, ledger = load_run("runB_revoked_key")
        decision = mayor_with_registry.decide(policy, briefcase, ledger)

        assert decision.decision == "NO_SHIP", (
            f"Run B should NO_SHIP but got {decision.decision}"
        )

    def test_reason_mentions_revoked(self, mayor_with_registry):
        """Run B must fail mentioning key revocation"""
        policy, briefcase, ledger = load_run("runB_revoked_key")
        decision = mayor_with_registry.decide(policy, briefcase, ledger)

        reasons_str = " ".join(decision.blocking_reasons).lower()
        assert "revok" in reasons_str or "key_revoked" in reasons_str.lower(), (
            f"Expected revocation failure, got: {decision.blocking_reasons}"
        )

    def test_revoked_key_id_in_reasons(self, mayor_with_registry):
        """Blocking reasons should mention key revocation"""
        policy, briefcase, ledger = load_run("runB_revoked_key")
        decision = mayor_with_registry.decide(policy, briefcase, ledger)

        reasons_str = " ".join(decision.blocking_reasons).lower()
        # Check for KEY_REVOKED reason code (may be prefixed with KEY_REGISTRY_ERROR)
        assert "key_revoked" in reasons_str, (
            f"Expected KEY_REVOKED in reasons, got: {decision.blocking_reasons}"
        )


class TestRunC:
    """Run C: Valid quorum → SHIP"""

    def test_decision_is_ship(self, mayor_with_registry):
        """Run C must produce SHIP decision"""
        policy, briefcase, ledger = load_run("runC_valid_quorum")
        decision = mayor_with_registry.decide(policy, briefcase, ledger)

        assert decision.decision == "SHIP", (
            f"Run C should SHIP but got {decision.decision}. "
            f"Blocking reasons: {decision.blocking_reasons}"
        )

    def test_no_blocking_reasons(self, mayor_with_registry):
        """Run C must have no blocking reasons"""
        policy, briefcase, ledger = load_run("runC_valid_quorum")
        decision = mayor_with_registry.decide(policy, briefcase, ledger)

        assert decision.blocking_reasons == [], (
            f"Run C should have no blocking reasons, got: {decision.blocking_reasons}"
        )

    def test_both_signatures_valid(self, mayor_with_registry):
        """Both CI and LEGAL signatures must be valid"""
        policy, briefcase, ledger = load_run("runC_valid_quorum")
        decision = mayor_with_registry.decide(policy, briefcase, ledger)

        # If either signature was invalid, decision would fail
        assert decision.decision == "SHIP", (
            "Both signatures must be valid for SHIP"
        )


class TestRunD:
    """Run D: Valid signature but wrong class claim → NO_SHIP

    Uses the pre-signed test vector ledger_runD_class_mismatch.json.
    The LEGAL key (key-2026-01-legal) signs an attestation claiming CI_RUNNER class.
    The signature is cryptographically valid, but the key registry says this key
    is bound to LEGAL class, so KEY_CLASS_MISMATCH must be detected.
    """

    def test_decision_is_no_ship(self, mayor_with_registry):
        """Run D must produce NO_SHIP decision"""
        policy, briefcase, ledger = load_run("runD_class_mismatch")
        decision = mayor_with_registry.decide(policy, briefcase, ledger)

        assert decision.decision == "NO_SHIP", (
            f"Run D should NO_SHIP due to class mismatch, got: {decision.decision}"
        )

    def test_reason_is_key_class_mismatch(self, mayor_with_registry):
        """Run D must fail with KEY_CLASS_MISMATCH"""
        policy, briefcase, ledger = load_run("runD_class_mismatch")
        decision = mayor_with_registry.decide(policy, briefcase, ledger)

        reasons_str = " ".join(decision.blocking_reasons).lower()
        assert "key_class_mismatch" in reasons_str, (
            f"Expected KEY_CLASS_MISMATCH, got: {decision.blocking_reasons}"
        )

    def test_ci_attestation_is_valid(self, mayor_with_registry):
        """The CI attestation (honest) should not trigger failure"""
        policy, briefcase, ledger = load_run("runD_class_mismatch")
        decision = mayor_with_registry.decide(policy, briefcase, ledger)

        # The CI attestation is honest (key-2026-01-ci claiming CI_RUNNER)
        # Only the LEGAL key claiming CI_RUNNER should fail
        for reason in decision.blocking_reasons:
            if "key-2026-01-ci" in reason:
                pytest.fail(f"CI key should be valid, but got: {reason}")


class TestReplayDeterminism:
    """Verify replay determinism across runs"""

    def test_decision_digest_stable_across_100_replays(self, mayor_with_registry):
        """Same inputs produce identical decision digest 100 times"""
        policy, briefcase, ledger = load_run("runC_valid_quorum")

        digests = []
        for _ in range(100):
            decision = mayor_with_registry.decide(policy, briefcase, ledger)
            digests.append(decision.decision_digest)

        assert len(set(digests)) == 1, (
            f"Decision digest not deterministic: found {len(set(digests))} unique digests"
        )

    def test_all_runs_deterministic(self, mayor_with_registry):
        """All four runs produce deterministic outputs"""
        for run_suffix in ["runA_missing_legal", "runB_revoked_key", "runC_valid_quorum", "runD_class_mismatch"]:
            policy, briefcase, ledger = load_run(run_suffix)

            decisions = [mayor_with_registry.decide(policy, briefcase, ledger) for _ in range(10)]
            digests = [d.decision_digest for d in decisions]

            assert len(set(digests)) == 1, (
                f"Run {run_suffix} not deterministic"
            )


class TestSignatureValidation:
    """Test that signatures are actually being validated"""

    def test_corrupted_signature_fails(self, mayor_with_registry):
        """Corrupted signature must fail verification"""
        policy, briefcase, ledger = load_run("runC_valid_quorum")

        # Corrupt the first attestation's signature
        original_sig = ledger["attestations"][0]["signature"]
        # Flip some characters in the base64 signature
        corrupted_sig = original_sig[:20] + "XXXX" + original_sig[24:]
        ledger["attestations"][0]["signature"] = corrupted_sig

        decision = mayor_with_registry.decide(policy, briefcase, ledger)

        assert decision.decision == "NO_SHIP", (
            "Corrupted signature should fail verification"
        )

    def test_wrong_evidence_digest_fails(self, mayor_with_registry):
        """Changed evidence_digest invalidates signature"""
        policy, briefcase, ledger = load_run("runC_valid_quorum")

        # Change evidence_digest (signature was over original)
        ledger["attestations"][0]["evidence_digest"] = "sha256:tampered"

        decision = mayor_with_registry.decide(policy, briefcase, ledger)

        assert decision.decision == "NO_SHIP", (
            "Tampered evidence_digest should fail signature verification"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

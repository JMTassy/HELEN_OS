#!/usr/bin/env python3
"""
Phase-2 Integration Tests: Adversarial Runs E/F/G/H

Tests advanced attack vectors:

Run E: Key Rotation Mid-Flight → NO_SHIP (KEY_REVOKED)
       Attestation signed before key revocation but evaluated after.

Run F: Allowlist Escape → NO_SHIP (KEY_OBLIGATION_NOT_ALLOWED)
       Valid key signs obligation outside its allowlist.

Run G: Policy Hash Replay → NO_SHIP (POLICY_HASH_MISMATCH)
       Attestation signed against old policy replayed against new.

Run H: Registry Hash Drift → NO_SHIP (SIGNATURE_INVALID)
       Attestation signed with old registry hash fails verification.

Each test verifies:
1. Decision is correct (NO_SHIP)
2. Reason code is correct
3. Attack is properly detected
"""

import pytest
pytestmark = pytest.mark.integration
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from oracle_town.core.mayor_rsm import MayorRSM
from oracle_town.core.policy import Policy


VECTORS_DIR = Path(__file__).parent.parent / "oracle_town" / "test_vectors"
KEYS_DIR = Path(__file__).parent.parent / "oracle_town" / "keys"


def load_run(run_suffix: str, briefcase_name: str = "briefcase_base") -> tuple:
    """Load policy, briefcase, and ledger for a test run"""
    # Load policy
    with open(VECTORS_DIR / "policy_POL-TEST-1.json", 'r') as f:
        policy_data = json.load(f)

    policy = Policy.from_dict(policy_data)

    # Load briefcase
    with open(VECTORS_DIR / f"{briefcase_name}.json", 'r') as f:
        briefcase = json.load(f)

    # Load ledger
    ledger_file = f"ledger_{run_suffix}.json"
    with open(VECTORS_DIR / ledger_file, 'r') as f:
        ledger = json.load(f)

    # Sync run_id
    briefcase["run_id"] = ledger["run_id"]

    return policy, briefcase, ledger


def load_run_with_policy_override(run_suffix: str, policy_hash_override: str) -> tuple:
    """Load run with modified policy hash for replay attack testing"""
    policy, briefcase, ledger = load_run(run_suffix)

    # Override policy hash to simulate new policy
    policy.policy_hash = policy_hash_override

    return policy, briefcase, ledger


@pytest.fixture
def mayor_with_registry():
    """Create Mayor with key registry loaded"""
    keys_path = KEYS_DIR / "public_keys.json"
    return MayorRSM(public_keys_path=str(keys_path))


class TestRunE:
    """Run E: Key Rotation Mid-Flight → NO_SHIP (KEY_REVOKED)

    Attestation signed BEFORE key revocation (2026-01-10) but evaluated AFTER
    revocation date (2026-01-15). The signature is cryptographically valid,
    but the key is revoked at evaluation time.
    """

    def test_decision_is_no_ship(self, mayor_with_registry):
        """Run E must produce NO_SHIP decision"""
        policy, briefcase, ledger = load_run("runE_key_rotation")
        decision = mayor_with_registry.decide(policy, briefcase, ledger)

        assert decision.decision == "NO_SHIP", (
            f"Run E should NO_SHIP due to revoked key, got: {decision.decision}"
        )

    def test_reason_is_key_revoked(self, mayor_with_registry):
        """Run E must fail with KEY_REVOKED"""
        policy, briefcase, ledger = load_run("runE_key_rotation")
        decision = mayor_with_registry.decide(policy, briefcase, ledger)

        reasons_str = " ".join(decision.blocking_reasons).lower()
        assert "revok" in reasons_str or "key_revoked" in reasons_str, (
            f"Expected KEY_REVOKED, got: {decision.blocking_reasons}"
        )

    def test_ci_attestation_is_valid(self, mayor_with_registry):
        """The CI attestation (active key) should not trigger failure"""
        policy, briefcase, ledger = load_run("runE_key_rotation")
        decision = mayor_with_registry.decide(policy, briefcase, ledger)

        # Only the revoked LEGAL key should fail
        for reason in decision.blocking_reasons:
            if "key-2026-01-ci" in reason.lower():
                pytest.fail(f"CI key should be valid, but got: {reason}")


class TestRunF:
    """Run F: Allowlist Escape → NO_SHIP (KEY_OBLIGATION_NOT_ALLOWED)

    key-2026-01-legal is only allowed to sign 'gdpr_consent_banner' obligation,
    but attempts to sign 'security_review'. The signature is valid, but the
    key is not authorized for this obligation.
    """

    def test_decision_is_no_ship(self, mayor_with_registry):
        """Run F must produce NO_SHIP decision"""
        policy, briefcase, ledger = load_run("runF_allowlist_escape", "briefcase_security_review")
        decision = mayor_with_registry.decide(policy, briefcase, ledger)

        assert decision.decision == "NO_SHIP", (
            f"Run F should NO_SHIP due to allowlist violation, got: {decision.decision}. "
            f"Blocking reasons: {decision.blocking_reasons}"
        )

    def test_reason_is_obligation_not_allowed(self, mayor_with_registry):
        """Run F must fail with obligation not allowed error"""
        policy, briefcase, ledger = load_run("runF_allowlist_escape", "briefcase_security_review")
        decision = mayor_with_registry.decide(policy, briefcase, ledger)

        reasons_str = " ".join(decision.blocking_reasons).lower()
        # Should mention obligation not allowed, scope violation, or allowlist
        assert ("obligation" in reasons_str and "not" in reasons_str) or \
               "allowlist" in reasons_str or \
               "key_obligation_not_allowed" in reasons_str or \
               "key_scope_violation" in reasons_str or \
               "missing classes" in reasons_str, (
            f"Expected allowlist/obligation violation, got: {decision.blocking_reasons}"
        )


class TestRunG:
    """Run G: Policy Hash Replay → NO_SHIP (POLICY_HASH_MISMATCH)

    Attestations were signed against old policy hash (aaa...) but the ledger
    claims to be for new policy hash (bbb...). This is a replay attack.
    """

    def test_decision_is_no_ship(self, mayor_with_registry):
        """Run G must produce NO_SHIP decision"""
        # Load with policy that has different hash than attestations
        policy, briefcase, ledger = load_run("runG_policy_replay")

        # Override policy hash to the NEW value (bbb...) that's in the ledger
        policy.policy_hash = "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"

        decision = mayor_with_registry.decide(policy, briefcase, ledger)

        assert decision.decision == "NO_SHIP", (
            f"Run G should NO_SHIP due to policy mismatch, got: {decision.decision}. "
            f"Blocking reasons: {decision.blocking_reasons}"
        )

    def test_reason_is_policy_mismatch_or_signature_invalid(self, mayor_with_registry):
        """Run G must fail with policy mismatch or signature invalid"""
        policy, briefcase, ledger = load_run("runG_policy_replay")
        policy.policy_hash = "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"

        decision = mayor_with_registry.decide(policy, briefcase, ledger)

        reasons_str = " ".join(decision.blocking_reasons).lower()
        # Either policy mismatch detected OR signature invalid (because payload has different policy hash)
        assert "policy" in reasons_str or "signature" in reasons_str or "invalid" in reasons_str, (
            f"Expected policy mismatch or signature failure, got: {decision.blocking_reasons}"
        )


class TestRunH:
    """Run H: Registry Hash Drift → NO_SHIP (SIGNATURE_INVALID)

    Attestations were signed with old registry hash (000...) but the current
    registry has a different hash. The signature verification includes
    registry hash in the canonical message, so verification fails.
    """

    def test_decision_is_no_ship(self, mayor_with_registry):
        """Run H must produce NO_SHIP decision"""
        policy, briefcase, ledger = load_run("runH_registry_drift")
        decision = mayor_with_registry.decide(policy, briefcase, ledger)

        assert decision.decision == "NO_SHIP", (
            f"Run H should NO_SHIP due to registry drift, got: {decision.decision}. "
            f"Blocking reasons: {decision.blocking_reasons}"
        )

    def test_reason_is_signature_invalid(self, mayor_with_registry):
        """Run H must fail with signature invalid (registry hash in signed payload differs)"""
        policy, briefcase, ledger = load_run("runH_registry_drift")
        decision = mayor_with_registry.decide(policy, briefcase, ledger)

        reasons_str = " ".join(decision.blocking_reasons).lower()
        # Signature should fail because canonical message includes registry hash
        assert "signature" in reasons_str or "invalid" in reasons_str, (
            f"Expected signature invalid, got: {decision.blocking_reasons}"
        )


class TestAllVectorsPresent:
    """Verify all test vectors exist and are properly structured"""

    def test_vector_files_exist(self):
        """All E-H vector files must exist"""
        for suffix in ["runE_key_rotation", "runF_allowlist_escape",
                       "runG_policy_replay", "runH_registry_drift"]:
            ledger_file = VECTORS_DIR / f"ledger_{suffix}.json"
            assert ledger_file.exists(), f"Missing: {ledger_file}"

    def test_vectors_have_metadata(self):
        """All vectors must have expected_decision and expected_reason"""
        for suffix in ["runE_key_rotation", "runF_allowlist_escape",
                       "runG_policy_replay", "runH_registry_drift"]:
            with open(VECTORS_DIR / f"ledger_{suffix}.json", 'r') as f:
                ledger = json.load(f)

            assert "metadata" in ledger, f"{suffix} missing metadata"
            assert "expected_decision" in ledger["metadata"], f"{suffix} missing expected_decision"
            assert "expected_reason" in ledger["metadata"], f"{suffix} missing expected_reason"
            assert ledger["metadata"]["expected_decision"] == "NO_SHIP", (
                f"{suffix} should expect NO_SHIP"
            )


class TestReplayDeterminismEFGH:
    """Verify replay determinism for vectors E-H"""

    def test_all_efgh_runs_deterministic(self, mayor_with_registry):
        """All four runs produce deterministic outputs"""
        vectors = [
            ("runE_key_rotation", "briefcase_base"),
            ("runF_allowlist_escape", "briefcase_security_review"),
            ("runG_policy_replay", "briefcase_base"),
            ("runH_registry_drift", "briefcase_base"),
        ]

        for run_suffix, briefcase_name in vectors:
            policy, briefcase, ledger = load_run(run_suffix, briefcase_name)

            # For Run G, override policy hash
            if "runG" in run_suffix:
                policy.policy_hash = "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"

            decisions = [mayor_with_registry.decide(policy, briefcase, ledger) for _ in range(10)]
            digests = [d.decision_digest for d in decisions]

            assert len(set(digests)) == 1, (
                f"Run {run_suffix} not deterministic: {len(set(digests))} unique digests"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

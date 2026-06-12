#!/usr/bin/env python3
"""
Phase-2 Crypto Unit Tests

Tests Ed25519 signature creation and verification:
1. Valid signature roundtrip
2. Signature fails on message mutation
3. Signature fails on wrong key
4. Base64 decoding edge cases
"""

import pytest
pytest.importorskip("numpy")
import base64
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from nacl.signing import SigningKey
from oracle_town.core.crypto import (
    canonical_json_bytes,
    verify_ed25519,
    sign_ed25519,
    build_canonical_message
)


class TestCanonicalJsonBytes:
    """Tests for deterministic JSON encoding"""

    def test_determinism_repeated_calls(self):
        """Same object produces identical bytes across 100 calls"""
        obj = {"z": 1, "a": 2, "m": {"nested": True, "arr": [1, 2, 3]}}
        results = [canonical_json_bytes(obj) for _ in range(100)]
        assert len(set(results)) == 1, "Canonical encoding must be deterministic"

    def test_key_sorting(self):
        """Keys are sorted lexicographically"""
        obj = {"z": 1, "a": 2, "m": 3}
        result = canonical_json_bytes(obj)
        expected = b'{"a":2,"m":3,"z":1}'
        assert result == expected

    def test_no_whitespace(self):
        """No whitespace in canonical output"""
        obj = {"key": "value", "nested": {"deep": True}}
        result = canonical_json_bytes(obj)
        assert b' ' not in result
        assert b'\n' not in result
        assert b'\t' not in result

    def test_unicode_preserved(self):
        """Unicode characters preserved with ensure_ascii=False"""
        obj = {"emoji": "🔐", "japanese": "日本語"}
        result = canonical_json_bytes(obj)
        assert "🔐".encode('utf-8') in result
        assert "日本語".encode('utf-8') in result


class TestEd25519Verification:
    """Tests for Ed25519 signature verification"""

    @pytest.fixture
    def keypair(self):
        """Generate a deterministic test keypair"""
        # Use fixed seed for reproducibility
        seed = b'\x00' * 32
        sk = SigningKey(seed)
        private_b64 = base64.b64encode(bytes(sk)).decode()
        public_b64 = base64.b64encode(bytes(sk.verify_key)).decode()
        return private_b64, public_b64

    def test_valid_signature_verifies(self, keypair):
        """Valid signature verifies correctly"""
        private_b64, public_b64 = keypair
        message = b"test message for signing"

        # Sign
        signature_b64 = sign_ed25519(private_b64, message)

        # Verify
        assert verify_ed25519(public_b64, message, signature_b64) is True

    def test_mutated_message_fails(self, keypair):
        """Signature fails when message is mutated"""
        private_b64, public_b64 = keypair
        message = b"original message"

        # Sign original
        signature_b64 = sign_ed25519(private_b64, message)

        # Verify with mutated message
        mutated = b"mutated message"
        assert verify_ed25519(public_b64, mutated, signature_b64) is False

    def test_wrong_key_fails(self, keypair):
        """Signature fails with wrong public key"""
        private_b64, _ = keypair
        message = b"test message"

        # Sign
        signature_b64 = sign_ed25519(private_b64, message)

        # Verify with different key
        different_sk = SigningKey(b'\x11' * 32)
        different_pub_b64 = base64.b64encode(bytes(different_sk.verify_key)).decode()

        assert verify_ed25519(different_pub_b64, message, signature_b64) is False

    def test_corrupted_signature_fails(self, keypair):
        """Corrupted signature fails verification"""
        private_b64, public_b64 = keypair
        message = b"test message"

        # Sign
        signature_b64 = sign_ed25519(private_b64, message)

        # Corrupt signature (flip some bytes)
        sig_bytes = base64.b64decode(signature_b64)
        corrupted = bytes([b ^ 0xFF for b in sig_bytes[:8]]) + sig_bytes[8:]
        corrupted_b64 = base64.b64encode(corrupted).decode()

        assert verify_ed25519(public_b64, message, corrupted_b64) is False

    def test_invalid_base64_fails(self):
        """Invalid base64 input fails gracefully"""
        # Not valid base64
        assert verify_ed25519("not-valid-base64!!!", b"message", "also-invalid!!!") is False

    def test_empty_signature_fails(self, keypair):
        """Empty signature fails"""
        _, public_b64 = keypair
        assert verify_ed25519(public_b64, b"message", "") is False

    def test_truncated_signature_fails(self, keypair):
        """Truncated signature fails"""
        private_b64, public_b64 = keypair
        message = b"test"
        signature_b64 = sign_ed25519(private_b64, message)

        # Truncate to half length
        truncated = signature_b64[:len(signature_b64)//2]
        assert verify_ed25519(public_b64, message, truncated) is False


class TestCanonicalMessage:
    """Tests for canonical message construction"""

    def test_build_canonical_message_includes_all_fields(self):
        """build_canonical_message includes all required fields"""
        msg = build_canonical_message(
            run_id="R-001",
            claim_id="CLM-001",
            obligation_name="test_obl",
            attestor_id="att_001",
            attestor_class="CI_RUNNER",
            policy_hash="sha256:aaa",
            evidence_digest="sha256:bbb",
            policy_match=1,
            key_registry_hash="sha256:ccc"
        )

        assert msg["run_id"] == "R-001"
        assert msg["claim_id"] == "CLM-001"
        assert msg["obligation_name"] == "test_obl"
        assert msg["attestor_id"] == "att_001"
        assert msg["attestor_class"] == "CI_RUNNER"
        assert msg["policy_hash"] == "sha256:aaa"
        assert msg["evidence_digest"] == "sha256:bbb"
        assert msg["policy_match"] == 1
        assert msg["key_registry_hash"] == "sha256:ccc"

    def test_canonical_message_determinism(self):
        """Same inputs produce identical canonical bytes"""
        args = {
            "run_id": "R-001",
            "claim_id": "CLM-001",
            "obligation_name": "test_obl",
            "attestor_id": "att_001",
            "attestor_class": "CI_RUNNER",
            "policy_hash": "sha256:aaa",
            "evidence_digest": "sha256:bbb",
            "policy_match": 1,
            "key_registry_hash": "sha256:ccc"
        }

        results = []
        for _ in range(10):
            msg = build_canonical_message(**args)
            results.append(canonical_json_bytes(msg))

        assert len(set(results)) == 1


class TestSignAndVerifyIntegration:
    """Integration tests for sign + verify workflow"""

    def test_full_attestation_signing_workflow(self):
        """Complete workflow: build message → sign → verify"""
        # Setup: deterministic keypair
        seed = b'\x42' * 32
        sk = SigningKey(seed)
        private_b64 = base64.b64encode(bytes(sk)).decode()
        public_b64 = base64.b64encode(bytes(sk.verify_key)).decode()

        # Build canonical message
        msg = build_canonical_message(
            run_id="R-TEST-001",
            claim_id="CLM-TEST-001",
            obligation_name="gdpr_consent_banner",
            attestor_id="ci_runner_001",
            attestor_class="CI_RUNNER",
            policy_hash="sha256:policy123",
            evidence_digest="sha256:evidence456",
            policy_match=1,
            key_registry_hash="sha256:registry789"
        )
        msg_bytes = canonical_json_bytes(msg)

        # Sign
        signature = sign_ed25519(private_b64, msg_bytes)

        # Verify
        assert verify_ed25519(public_b64, msg_bytes, signature) is True

        # Verify fails if any field changes
        msg["policy_match"] = 0
        mutated_bytes = canonical_json_bytes(msg)
        assert verify_ed25519(public_b64, mutated_bytes, signature) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

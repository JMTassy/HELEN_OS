"""
Cryptographic Utilities for Oracle Town

Canonical message signing and verification using Ed25519.

RSM-v0.1 compliant: receipts are registry-bound and policy-bound via signature.
"""
import json
import hashlib
import base64
import binascii
from typing import Dict, Any, Optional


def canonical_json_bytes(obj: Dict[str, Any]) -> bytes:
    """
    Convert object to canonical JSON bytes for signing.

    Rules:
    - Keys sorted lexicographically
    - No whitespace
    - UTF-8 encoding
    - Deterministic (same object → same bytes)

    Returns:
        UTF-8 encoded canonical JSON
    """
    canonical = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return canonical.encode("utf-8")


def build_canonical_message(
    run_id: str,
    claim_id: str,
    obligation_name: str,
    attestor_id: str,
    attestor_class: str,
    policy_hash: str,
    evidence_digest: str,
    policy_match: int,
    key_registry_hash: Optional[str] = None
) -> Dict[str, Any]:
    """
    Build canonical message for signature.

    CRITICAL: Field order matters for determinism (enforced by canonical_json_bytes).

    Args:
        All attestation fields that must be signed

    Returns:
        Canonical message dict
    """
    msg = {
        "run_id": run_id,
        "claim_id": claim_id,
        "obligation_name": obligation_name,
        "attestor_id": attestor_id,
        "attestor_class": attestor_class,
        "policy_hash": policy_hash,
        "key_registry_hash": key_registry_hash,
        "evidence_digest": evidence_digest,
        "policy_match": policy_match
    }
    return msg


def verify_ed25519(public_key_b64: str, message_bytes: bytes, signature_b64: str) -> bool:
    """
    Verify Ed25519 signature.

    Args:
        public_key_b64: Base64-encoded public key (32 bytes)
        message_bytes: Canonical message bytes
        signature_b64: Base64-encoded signature (64 bytes)

    Returns:
        True if signature valid, False otherwise
    """
    try:
        from nacl.signing import VerifyKey
        from nacl.exceptions import BadSignatureError
    except ImportError:
        print("Signature verification error: nacl not installed")
        return False

    try:
        public_key_bytes = base64.b64decode(public_key_b64)
        signature_bytes = base64.b64decode(signature_b64)
        verify_key = VerifyKey(public_key_bytes)
        verify_key.verify(message_bytes, signature_bytes)
        return True
    except BadSignatureError:
        return False
    except Exception as e:
        print(f"Signature verification error: {e}")
        return False


def sign_ed25519(private_key_b64: str, message_bytes: bytes) -> str:
    """
    Sign message with Ed25519 private key.

    Args:
        private_key_b64: Base64-encoded private key (32 bytes seed)
        message_bytes: Canonical message bytes

    Returns:
        Base64-encoded signature (64 bytes)
    """
    try:
        from nacl.signing import SigningKey

        # Decode private key
        private_key_bytes = base64.b64decode(private_key_b64)

        # Create signing key
        signing_key = SigningKey(private_key_bytes)

        # Sign message
        signed = signing_key.sign(message_bytes)

        # Return signature only (not signed message)
        signature_bytes = signed.signature
        return base64.b64encode(signature_bytes).decode("ascii")

    except Exception as e:
        print(f"Signing error: {e}")
        raise


def generate_ed25519_keypair() -> tuple[str, str]:
    """
    Generate Ed25519 keypair for testing.

    Returns:
        (private_key_b64, public_key_b64)
    """
    try:
        from nacl.signing import SigningKey

        # Generate random key
        signing_key = SigningKey.generate()

        # Get private and public keys
        private_key_b64 = base64.b64encode(bytes(signing_key)).decode("ascii")
        public_key_b64 = base64.b64encode(bytes(signing_key.verify_key)).decode("ascii")

        return (private_key_b64, public_key_b64)

    except Exception as e:
        print(f"Keypair generation error: {e}")
        raise


# Test
if __name__ == "__main__":
    print("=" * 70)
    print("CRYPTO MODULE TEST")
    print("=" * 70)

    # Test 1: Canonical message construction
    print("\n[Test 1] Canonical message construction")
    msg = build_canonical_message(
        run_id="R-001",
        claim_id="CLM-001",
        obligation_name="test_obligation",
        attestor_id="ci_001",
        attestor_class="CI_RUNNER",
        policy_hash="sha256:abc123",
        evidence_digest="sha256:def456",
        policy_match=1
    )
    msg_bytes = canonical_json_bytes(msg)
    print(f"Message: {msg_bytes[:80]}...")
    print(f"Length: {len(msg_bytes)} bytes")

    # Test 2: Determinism (10 iterations)
    print("\n[Test 2] Canonical encoding determinism")
    hashes = set()
    for _ in range(10):
        msg_bytes = canonical_json_bytes(msg)
        h = hashlib.sha256(msg_bytes).hexdigest()
        hashes.add(h)

    print(f"Unique hashes: {len(hashes)}")
    assert len(hashes) == 1, "Canonical encoding must be deterministic"
    print("✓ Deterministic")

    # Test 3: Keypair generation
    print("\n[Test 3] Keypair generation")
    private_key, public_key = generate_ed25519_keypair()
    print(f"Private key (first 20 chars): {private_key[:20]}...")
    print(f"Public key (first 20 chars): {public_key[:20]}...")

    # Test 4: Sign and verify
    print("\n[Test 4] Sign and verify")
    signature = sign_ed25519(private_key, msg_bytes)
    print(f"Signature (first 20 chars): {signature[:20]}...")

    valid = verify_ed25519(public_key, msg_bytes, signature)
    print(f"Signature valid: {valid}")
    assert valid, "Valid signature must verify"

    # Test 5: Invalid signature detection
    print("\n[Test 5] Invalid signature detection")
    invalid_sig = signature[:-4] + "XXXX"  # Corrupt signature
    valid = verify_ed25519(public_key, msg_bytes, invalid_sig)
    print(f"Corrupted signature valid: {valid}")
    assert not valid, "Corrupted signature must fail"

    # Test 6: Message tampering detection
    print("\n[Test 6] Message tampering detection")
    tampered_msg = dict(msg)
    tampered_msg["evidence_digest"] = "sha256:tampered"
    tampered_bytes = canonical_json_bytes(tampered_msg)
    valid = verify_ed25519(public_key, tampered_bytes, signature)
    print(f"Tampered message valid: {valid}")
    assert not valid, "Tampered message must fail"

    print("\n" + "=" * 70)
    print("ALL CRYPTO TESTS PASSED ✓")
    print("=" * 70)

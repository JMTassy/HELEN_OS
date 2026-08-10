"""C13 — frame-bound witness receipts. 🔵 OBSERVED · NON_SOVEREIGN · authority=0.

Every executable witness carries its exact software frame, so a PASS cannot silently
transport across frames:

    PASS@F1 ⊬ PASS@F2          Witnessed(c, F1) ⊬ Witnessed(c, F2)
    h_F = H(canon(F))          F = (repo, branch, commit, worktree, test,
                                    test_artifact, environment, toolchain)

A result transports to a target frame ONLY when the frame matches. Tiering (derive the
verdict, never trust a stored one):
  - code frame differs (commit / worktree / test_artifact / repo / branch / test)
        → REJECT_TRANSPORT   the bytes under test are literally not the same
  - only environment differs (environment_hash / toolchain_version)
        → HOLD               needs an environment-equivalence witness, not a hard no
  - a frame field is missing so h_F is uncomputable
        → UNKNOWN            an under-specified witness is not portable evidence
  - full frame identical AND the receipt's self-hash recomputes
        → PASS

The witness law:
    ValidWitness(W, c, F) ⇒ BindClaim ∧ BindFrame ∧ BindTest ∧ BindArtifact ∧ BindEnvironment

Determinism: `timestamp` is an INJECTED string (no wall clock); canon = sha256(canonical_json),
reused from the ledger hash_chain. K-tau mu_DETERMINISM clean.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Optional

from helen_os.ledger.hash_chain import canonical_json, sha256_hex


def h_v(x) -> str:
    return sha256_hex(canonical_json(x))


# the 8 fields that constitute a software FRAME
_FRAME_FIELDS = (
    "repo_id", "branch", "commit", "worktree_hash",
    "test_id", "test_artifact_hash", "environment_hash", "toolchain_version",
)
# subset identifying the exact CODE under test — differ ⇒ hard REJECT_TRANSPORT
_CODE_FIELDS = ("repo_id", "branch", "commit", "worktree_hash", "test_id", "test_artifact_hash")
# environment subset — differ ⇒ HOLD (softer; may hold under an env-equivalence witness)
_ENV_FIELDS = ("environment_hash", "toolchain_version")


@dataclass(frozen=True)
class FrameWitnessReceipt:
    claim_id: str
    repo_id: str
    branch: str
    commit: str
    worktree_hash: str
    test_id: str
    test_artifact_hash: str
    environment_hash: str
    toolchain_version: str
    result: str
    timestamp: str          # INJECTED, never generated (determinism)
    receipt_hash: str        # self-binding hash over every other field


def _body(r: FrameWitnessReceipt) -> dict:
    """Everything except the self-hash — the pre-image of receipt_hash."""
    return {
        "claim_id": r.claim_id,
        "repo_id": r.repo_id, "branch": r.branch, "commit": r.commit,
        "worktree_hash": r.worktree_hash, "test_id": r.test_id,
        "test_artifact_hash": r.test_artifact_hash,
        "environment_hash": r.environment_hash, "toolchain_version": r.toolchain_version,
        "result": r.result, "timestamp": r.timestamp,
    }


def receipt_body_hash(r: FrameWitnessReceipt) -> str:
    return h_v(_body(r))


def mint_receipt(**kw) -> FrameWitnessReceipt:
    """Construct a receipt carrying a correct self-binding receipt_hash."""
    r = FrameWitnessReceipt(receipt_hash="", **kw)
    return replace(r, receipt_hash=receipt_body_hash(r))


def valid_receipt(r: FrameWitnessReceipt) -> bool:
    """Self-hash recomputed, never trusted. A field mutated post-mint fails this."""
    return bool(r.receipt_hash) and r.receipt_hash == receipt_body_hash(r)


def frame_hash(r: FrameWitnessReceipt) -> Optional[str]:
    """h_F = H(canon(F)); None if any frame field is empty (under-specified frame)."""
    frame = {f: getattr(r, f) for f in _FRAME_FIELDS}
    if any(not v for v in frame.values()):
        return None
    return h_v(frame)


class Transport(Enum):
    PASS = "PASS"
    REJECT_TRANSPORT = "REJECT_TRANSPORT"
    HOLD = "HOLD"
    UNKNOWN = "UNKNOWN"


def transport(r: FrameWitnessReceipt, target: FrameWitnessReceipt):
    """Can a result witnessed in r's frame be transported to target's frame?
    Returns (Transport, reason). Recomputes h_F and the self-hash; trusts no stored verdict."""
    if frame_hash(r) is None or frame_hash(target) is None:
        return Transport.UNKNOWN, "E_MISSING_FRAME_HASH"        # C13-05
    if not valid_receipt(r):
        return Transport.UNKNOWN, "E_INVALID_RECEIPT"           # tamper
    if frame_hash(r) == frame_hash(target):
        return Transport.PASS, "FRAME_MATCH"                    # C13-06
    if any(getattr(r, f) != getattr(target, f) for f in _CODE_FIELDS):
        return Transport.REJECT_TRANSPORT, "E_CODE_FRAME_DIFFERS"   # C13-01/02/03
    if any(getattr(r, f) != getattr(target, f) for f in _ENV_FIELDS):
        return Transport.HOLD, "E_ENVIRONMENT_DIFFERS"         # C13-04
    return Transport.PASS, "FRAME_MATCH"                        # total fallthrough

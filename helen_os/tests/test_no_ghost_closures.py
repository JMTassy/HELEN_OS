"""
Ghost Closure Detector.

Walks every CLOSURE_RECEIPT_V1 artifact in GOVERNANCE/CLOSURES/ and verifies
each claim: the expected_artifact must exist at the repo-relative path and
hash to the claimed SHA-256 (or satisfy the appropriate directory sentinel).

Fails if:
  - A receipt with verdict == CLOSED has any FAIL or MISSING claim.
  - A receipt with verdict == BLOCKED has all PASS claims (should have been CLOSED).
  - proposer.identity == attestor.identity (Rule 3: no self-validation).
  - An observed hash diverges from expected for any claim.

This is the V4-and-onward enforcement: it makes 'CLOSED' unfalsifiable.
The Schema Authority V1/V2/V3 reports would all have failed this test.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
CLOSURES_DIR = REPO / "GOVERNANCE" / "CLOSURES"


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _observe_artifact(artifact_path_str: str) -> tuple[str, Path]:
    """
    Resolve a repo-relative artifact path and return (observed_sha256, resolved_path).
    Directory sentinels use special observed values.
    """
    path = REPO / artifact_path_str
    if artifact_path_str.endswith("/"):
        # Directory claim: interpret absence / emptiness
        if not path.exists():
            return "DIRECTORY_ABSENT", path
        if path.is_dir():
            any_file = any(path.rglob("*"))
            return ("DIRECTORY_NONEMPTY" if any_file else "DIRECTORY_EMPTY"), path
        return "FILE_ABSENT", path
    if not path.exists() or not path.is_file():
        return "FILE_ABSENT", path
    return _sha256_file(path), path


def _collect_closures() -> list[Path]:
    """
    Return closures that are not retracted by a later receipt.

    The `retracts` field already encodes the supersession chain. A closure named
    in any other closure's `retracts` is historical — preserved on disk for
    audit, but not current truth. Validate only the leaf of each chain.
    """
    if not CLOSURES_DIR.is_dir():
        return []
    all_closures = sorted(CLOSURES_DIR.glob("*.json"))

    retracted_names: set[str] = set()
    for p in all_closures:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        retracted_path = data.get("retracts")
        if retracted_path:
            retracted_names.add(Path(retracted_path).name)

    return [p for p in all_closures if p.name not in retracted_names]


_CLOSURES = _collect_closures()


@pytest.mark.parametrize(
    "closure_path",
    _CLOSURES if _CLOSURES else [pytest.param(None, marks=pytest.mark.skip(reason="No closure receipts to check"))],
    ids=lambda p: p.name if p else "none",
)
def test_closure_receipt_is_not_a_ghost(closure_path: Path):
    receipt = json.loads(closure_path.read_text(encoding="utf-8"))

    assert receipt.get("schema_name") == "CLOSURE_RECEIPT_V1", (
        f"{closure_path.name}: not a CLOSURE_RECEIPT_V1"
    )
    assert receipt.get("schema_version") == "1.0.0"

    proposer_id = receipt["proposer"]["identity"]
    attestor_id = receipt["attestor"]["identity"]
    assert proposer_id != attestor_id, (
        f"{closure_path.name}: proposer.identity == attestor.identity. "
        f"Rule 3 violation — an agent cannot attest its own closure."
    )

    verdict = receipt["verdict"]
    failures: list[str] = []
    all_pass = True
    for claim in receipt["claims"]:
        observed, resolved = _observe_artifact(claim["expected_artifact"])
        expected = claim["expected_sha256"]
        claim_verdict = claim["verdict"]
        if observed != expected:
            all_pass = False
            if claim_verdict == "PASS":
                failures.append(
                    f"{claim['claim_id']}: marked PASS but observed != expected\n"
                    f"    artifact: {claim['expected_artifact']}\n"
                    f"    expected: {expected}\n"
                    f"    observed: {observed}"
                )
        else:
            # Observed matches expected. If verdict isn't PASS, that's also wrong.
            if claim_verdict != "PASS":
                failures.append(
                    f"{claim['claim_id']}: verdict={claim_verdict} but artifact matches expected hash "
                    f"({claim['expected_artifact']})"
                )

    if verdict == "CLOSED":
        assert all_pass and not failures, (
            f"{closure_path.name}: claimed CLOSED but has ghost or misreported claims:\n  "
            + "\n  ".join(failures) if failures else "(no detail)"
        )
    elif verdict == "BLOCKED":
        # Being BLOCKED means at least one claim should be FAIL or MISSING.
        has_blocker = any(c["verdict"] in ("FAIL", "MISSING") for c in receipt["claims"])
        assert has_blocker, (
            f"{closure_path.name}: verdict=BLOCKED but no claim is FAIL/MISSING. "
            f"If all claims pass, verdict should be CLOSED."
        )
        # The internal observed/expected consistency check still applies.
        assert not failures, (
            f"{closure_path.name}: BLOCKED with inconsistent claim verdicts:\n  "
            + "\n  ".join(failures)
        )
    elif verdict == "RETRACTED":
        retracts = receipt.get("retracts")
        assert retracts, f"{closure_path.name}: RETRACTED receipts must name the retracted receipt."

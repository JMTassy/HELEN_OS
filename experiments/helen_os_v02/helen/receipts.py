from helen.ids import now_utc
from helen.hashing import sha256
from helen.hal import verify_artifacts


def build_receipt(proposal: dict, artifacts: list[dict]) -> dict:
    verified = verify_artifacts(artifacts)
    base = {
        "proposal_id": proposal["proposal_id"],
        "verified": verified,
        "artifacts": [
            {
                "artifact_id": a["artifact_id"],
                "type": a["type"],
                "content_hash": a["content_hash"],
                "content_preview": a["content_preview"]
            }
            for a in artifacts
        ],
        "verifier": "HAL_V0.2",
        "timestamp_utc": now_utc()
    }
    receipt_id = "R-" + sha256(base)[:16]
    return {
        "receipt_id": receipt_id,
        **base
    }

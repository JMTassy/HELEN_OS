from helen.receipts import build_receipt


def test_receipt_verified_with_artifact():
    proposal = {
        "proposal_id": "P-1",
        "actions": [],
        "route": "THINK",
        "authority": "NON_SOVEREIGN"
    }
    artifacts = [
        {
            "artifact_id": "A-1",
            "type": "EXECUTION_RESULT",
            "content_hash": "abc",
            "content_preview": "ok"
        }
    ]
    receipt = build_receipt(proposal, artifacts)
    assert receipt["verified"] is True
    assert receipt["receipt_id"].startswith("R-")


def test_receipt_unverified_with_no_artifacts():
    proposal = {
        "proposal_id": "P-2",
        "actions": [],
        "route": "THINK",
        "authority": "NON_SOVEREIGN"
    }
    receipt = build_receipt(proposal, [])
    assert receipt["verified"] is False

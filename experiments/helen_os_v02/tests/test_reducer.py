from helen.reducer import reduce


def test_reducer_admits_verified_receipt():
    proposal = {
        "proposal_id": "P-1",
        "route": "THINK",
        "authority": "NON_SOVEREIGN"
    }
    receipt = {
        "receipt_id": "R-1",
        "verified": True,
        "artifacts": [{"artifact_id": "A-1"}]
    }
    state = {"admitted_receipts": []}
    verdict = reduce(proposal, receipt, state)
    assert verdict["admit"] is True


def test_reducer_rejects_unverified_receipt():
    proposal = {
        "proposal_id": "P-1",
        "route": "THINK",
        "authority": "NON_SOVEREIGN"
    }
    receipt = {
        "receipt_id": "R-1",
        "verified": False,
        "artifacts": [{"artifact_id": "A-1"}]
    }
    state = {"admitted_receipts": []}
    verdict = reduce(proposal, receipt, state)
    assert verdict["admit"] is False


def test_reducer_rejects_sovereign_proposal():
    proposal = {
        "proposal_id": "P-1",
        "route": "THINK",
        "authority": "SYSTEM"
    }
    receipt = {
        "receipt_id": "R-1",
        "verified": True,
        "artifacts": [{"artifact_id": "A-1"}]
    }
    state = {"admitted_receipts": []}
    verdict = reduce(proposal, receipt, state)
    assert verdict["admit"] is False

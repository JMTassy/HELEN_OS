from helen.laws import (
    assert_non_sovereign_proposal,
    assert_receipt_has_artifacts,
    assert_verified_receipt
)


def reduce(proposal: dict, receipt: dict, current_state: dict) -> dict:
    try:
        assert_non_sovereign_proposal(proposal)
        assert_receipt_has_artifacts(receipt)
        assert_verified_receipt(receipt)
        mutation = {
            "last_proposal_id": proposal["proposal_id"],
            "last_receipt_id": receipt["receipt_id"],
            "last_route": proposal["route"],
            "admitted_receipts": current_state.get("admitted_receipts", []) + [receipt["receipt_id"]]
        }
        return {
            "admit": True,
            "reason": "VERIFIED_RECEIPT_ADMITTED",
            "mutation": mutation
        }
    except Exception as e:
        return {
            "admit": False,
            "reason": str(e),
            "mutation": {}
        }

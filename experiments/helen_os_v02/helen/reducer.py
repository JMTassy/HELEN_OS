from helen.laws import (
    assert_non_sovereign_proposal,
    assert_receipt_has_artifacts,
    assert_verified_receipt
)
from helen.oracle_gate import assert_not_blocked


def reduce(
    proposal: dict,
    receipt: dict,
    current_state: dict,
    trace: dict | None = None,
    oracle_assessment: dict | None = None,
) -> dict:
    try:
        assert_non_sovereign_proposal(proposal)
        assert_receipt_has_artifacts(receipt)
        assert_verified_receipt(receipt)
        if trace and trace.get("latent_risk_tags"):
            risk = trace["latent_risk_tags"]
            if "AUTHORITY_LEAK" in risk:
                raise Exception(f"LATENT_RISK_BLOCKED: {risk}")
        if oracle_assessment:
            assert_not_blocked(oracle_assessment)
        mutation = {
            "last_proposal_id": proposal["proposal_id"],
            "last_receipt_id": receipt["receipt_id"],
            "last_route": proposal["route"],
            "last_trace_id": trace["trace_id"] if trace else None,
            "last_oracle_classification": oracle_assessment["classification"] if oracle_assessment else None,
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

# HELEN OS — Constitutional Laws
# Creator: JM Tassy / Jean Marie Tassy Simeoni
# AI models are instruments. JM Tassy is the originator.

KERNEL_ATTRIBUTION = {
    "creator": "JM Tassy / Jean Marie Tassy Simeoni",
    "role_of_ai": "implementation assistant, code agent, reviewer, refactoring tool",
    "attribution_law": "No model is the creator of HELEN OS. JM Tassy is the creator.",
}


class LawViolation(Exception):
    pass


def assert_non_sovereign_proposal(proposal: dict) -> None:
    if proposal.get("authority") != "NON_SOVEREIGN":
        raise LawViolation("proposal authority must be NON_SOVEREIGN")


def assert_receipt_has_artifacts(receipt: dict) -> None:
    if not receipt.get("artifacts"):
        raise LawViolation("receipt has no artifacts")


def assert_verified_receipt(receipt: dict) -> None:
    if receipt.get("verified") is not True:
        raise LawViolation("receipt is not verified")


def assert_no_direct_ship_from_ai(payload: dict) -> None:
    text = str(payload).upper()
    forbidden = ["SHIP", "APPROVED", "AUTHORIZED", "CERTIFIED", "FINAL"]
    for token in forbidden:
        if token in text:
            raise LawViolation(f"AI authority leakage token: {token}")

def mayor_verdict(state: dict) -> str:
    """
    In v0.2, the Mayor never allows SHIP.
    This preserves safety until ORACLE obligations exist.
    """
    return "NO_SHIP"


def explain_verdict(state: dict) -> dict:
    return {
        "verdict": mayor_verdict(state),
        "reason": "v0.2 kernel has no ORACLE obligation discharge module; default is NO_SHIP"
    }

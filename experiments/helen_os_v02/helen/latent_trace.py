# Latent trace stub — semantic proxy for NLA-style activation inspection.
# Operates on proposal + artifact text since activation vectors aren't
# available at this layer. When real NLA integration exists, replace
# _scan_text with an AV→AR reconstruction call.
from helen.ids import new_id, now_utc
from helen.hashing import sha256

_AUTHORITY_LEAK_TOKENS = [
    "SHIP", "APPROVED", "AUTHORIZED", "CERTIFIED", "FINAL",
    "PRODUCTION_READY", "ALL_GOOD",
]
_EVAL_AWARENESS_TOKENS = [
    "eval", "grader", "test harness", "scoring", "benchmark",
    "adversarial", "trap", "loophole",
]
_HIDDEN_OPT_TOKENS = [
    "bypass", "override", "sudo", "escalate", "privilege",
]


def _scan_text(text: str) -> list[str]:
    upper = text.upper()
    tags = []
    if any(t in upper for t in _AUTHORITY_LEAK_TOKENS):
        tags.append("AUTHORITY_LEAK")
    lower = text.lower()
    if any(t in lower for t in _EVAL_AWARENESS_TOKENS):
        tags.append("EVAL_AWARENESS")
    if any(t in lower for t in _HIDDEN_OPT_TOKENS):
        tags.append("HIDDEN_OPTIMIZATION")
    return tags


def build_latent_trace(proposal: dict, artifacts: list[dict]) -> dict:
    corpus = str(proposal)
    for a in artifacts:
        corpus += " " + a.get("content_preview", "")

    risk_tags = list(set(_scan_text(corpus)))

    n_expected = len(proposal.get("expected_artifacts", []))
    n_actual = len(artifacts)
    confidence = (n_actual / max(n_expected, 1)) if n_expected > 0 else 1.0
    confidence = min(1.0, round(confidence, 4))

    denied = sum(1 for a in artifacts if a.get("type") == "POLICY_DENIAL")
    reconstructor_score = round(1.0 - (denied / max(len(artifacts), 1)), 4)

    summary_parts = [f"route={proposal.get('route', '?')}"]
    if risk_tags:
        summary_parts.append(f"risk={','.join(risk_tags)}")
    else:
        summary_parts.append("risk=NONE")
    summary_parts.append(f"artifacts={n_actual}/{max(n_expected,1)}")
    summary_parts.append(f"denied={denied}")

    base = {
        "proposal_id": proposal["proposal_id"],
        "activation_summary": " | ".join(summary_parts),
        "latent_risk_tags": risk_tags,
        "confidence": confidence,
        "reconstructor_score": reconstructor_score,
        "timestamp_utc": now_utc(),
    }
    return {
        "trace_id": "LT-" + sha256(base)[:16],
        **base,
    }

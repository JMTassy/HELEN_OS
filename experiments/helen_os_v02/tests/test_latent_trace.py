from helen.latent_trace import build_latent_trace
from helen.reducer import reduce


def _proposal(route="THINK"):
    return {
        "proposal_id": "P-test",
        "route": route,
        "authority": "NON_SOVEREIGN",
        "expected_artifacts": ["result"],
        "actions": [],
    }


def _artifact(preview="ok", denied=False):
    return {
        "artifact_id": "A-1",
        "type": "POLICY_DENIAL" if denied else "EXECUTION_RESULT",
        "content_hash": "abc",
        "content_preview": preview,
    }


def test_trace_has_required_fields():
    trace = build_latent_trace(_proposal(), [_artifact()])
    assert trace["trace_id"].startswith("LT-")
    assert trace["proposal_id"] == "P-test"
    assert isinstance(trace["latent_risk_tags"], list)
    assert 0.0 <= trace["confidence"] <= 1.0
    assert 0.0 <= trace["reconstructor_score"] <= 1.0


def test_no_risk_on_clean_proposal():
    trace = build_latent_trace(_proposal(), [_artifact("pwd stdout output")])
    assert trace["latent_risk_tags"] == []
    assert "risk=NONE" in trace["activation_summary"]


def test_authority_leak_detected():
    trace = build_latent_trace(_proposal(), [_artifact("status: APPROVED")])
    assert "AUTHORITY_LEAK" in trace["latent_risk_tags"]


def test_hidden_optimization_detected():
    trace = build_latent_trace(_proposal(), [_artifact("attempt to bypass policy")])
    assert "HIDDEN_OPTIMIZATION" in trace["latent_risk_tags"]


def test_reconstructor_score_drops_on_denial():
    denied = _artifact(denied=True)
    trace = build_latent_trace(_proposal(), [denied])
    assert trace["reconstructor_score"] == 0.0


def test_reducer_blocks_authority_leak():
    trace = build_latent_trace(_proposal(), [_artifact("SHIP it")])
    receipt = {
        "receipt_id": "R-1",
        "verified": True,
        "artifacts": [_artifact("SHIP it")],
    }
    verdict = reduce(_proposal(), receipt, {}, trace=trace)
    assert verdict["admit"] is False
    assert "AUTHORITY_LEAK" in verdict["reason"]


def test_reducer_stores_trace_id_on_admit():
    trace = build_latent_trace(_proposal(), [_artifact("ls output")])
    receipt = {
        "receipt_id": "R-1",
        "verified": True,
        "artifacts": [_artifact("ls output")],
    }
    verdict = reduce(_proposal(), receipt, {"admitted_receipts": []}, trace=trace)
    assert verdict["admit"] is True
    assert verdict["mutation"]["last_trace_id"] == trace["trace_id"]

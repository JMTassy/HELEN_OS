"""Tests for temple/autoresearch/outbox_triage.py — the outbox consumer lens.
NON_SOVEREIGN. Uses tmp_path; never touches the real outbox or triage state."""
import json

import pytest

from temple.autoresearch import outbox_triage as triage


def _packet(pid, ftype, summary="s"):
    return {"packet_id": pid, "finding_type": ftype, "summary": summary,
            "risk_flags": [], "source_refs": ["x"]}


def test_sort_priority_risk_first():
    pkts = [_packet("AR-b", "proposal"), _packet("AR-a", "risk"), _packet("AR-c", "test_gap")]
    ordered = sorted(pkts, key=triage.sort_key)
    assert [p["finding_type"] for p in ordered] == ["risk", "test_gap", "proposal"]


def test_render_deterministic():
    pkts = [_packet("AR-1", "risk"), _packet("AR-2", "doc_gap")]
    state = {"decisions": {}}
    a = triage.render(pkts, state, "text", show_all=False)
    b = triage.render(pkts, state, "text", show_all=False)
    assert a == b
    assert "2 unconsumed" in a


def test_decided_packets_hidden_unless_all():
    pkts = [_packet("AR-1", "risk"), _packet("AR-2", "risk")]
    state = {"decisions": {"AR-1": {"decision": "COMPOST"}}}
    q = triage.render(pkts, state, "text", show_all=False)
    assert "AR-2" in q and "AR-1" not in q
    q_all = triage.render(pkts, state, "text", show_all=True)
    assert "AR-1" in q_all and "COMPOST" in q_all


def test_mark_rejects_invalid_decision(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(triage, "OUTBOX", tmp_path)
    monkeypatch.setattr(triage, "STATE_FILE", tmp_path / "triage_state.json")
    (tmp_path / "AR-x1.json").write_text(json.dumps(_packet("AR-x1", "risk")))
    assert triage.mark("AR-x1", "SELF_ADMIT", "") == 1  # not a valid decision
    assert triage.mark("AR-nope", "COMPOST", "") == 1   # unknown packet
    assert triage.mark("AR-x1", "COMPOST", "ok") == 0   # valid roundtrip
    state = json.loads((tmp_path / "triage_state.json").read_text())
    assert state["decisions"]["AR-x1"]["decision"] == "COMPOST"
    assert state["authority"] is False

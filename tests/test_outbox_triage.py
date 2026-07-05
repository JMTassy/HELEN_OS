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


# --- merged anatomy (2026-07-05 ruling): triage=eye · pen=hand · guard=immune ---

def test_group_packets_deterministic_themes():
    pkts = [
        _packet("AR-1", "test_gap", "adapter has no tests"),
        _packet("AR-2", "risk", "unconsumed queue is growing"),
        _packet("AR-3", "risk", "garden validator not in ci"),
        _packet("AR-4", "proposal", "an unrelated idea"),
    ]
    g1 = triage.group_packets(pkts)
    g2 = triage.group_packets(pkts)
    assert g1.keys() == g2.keys()
    assert [p["packet_id"] for p in g1["test_gap_cluster"]] == ["AR-1"]
    assert [p["packet_id"] for p in g1["unconsumed_queue"]] == ["AR-2"]
    assert [p["packet_id"] for p in g1["ci_seam"]] == ["AR-3"]
    assert [p["packet_id"] for p in g1["proposal"]] == ["AR-4"]


def test_triage_receipt_is_candidate_not_authority():
    groups = triage.group_packets([_packet("AR-1", "risk")])
    r = triage.make_triage_receipt(groups, 1)
    assert r["schema"] == "TRIAGE_RECEIPT_V0"
    assert r["authority"] is False and r["sovereign"] is False and r["canon"] is False
    assert r["ledger_effect"] == "none"
    assert r["reducer_required"] is True


def test_triage_emit_does_not_consume(tmp_path, monkeypatch):
    """The sovereign invariant: grouping/emitting NEVER marks a packet consumed."""
    from temple.autoresearch import operator_pen as pen
    outbox = tmp_path / "outbox"
    outbox.mkdir()
    (outbox / "AR-e1.json").write_text(json.dumps(_packet("AR-e1", "risk")))
    log = tmp_path / "consumption_log.ndjson"
    monkeypatch.setattr(triage, "OUTBOX", outbox)
    monkeypatch.setattr(triage, "STATE_FILE", tmp_path / "triage_state.json")
    monkeypatch.setattr(triage, "TRIAGE_DIR", tmp_path / "triage")

    pkts = triage.load_packets()
    before = len(pen.unconsumed(pkts, pen.effective_decisions(pen.read_log(log))))
    # full triage pass: group + receipt emission
    receipt = triage.make_triage_receipt(triage.group_packets(pkts), len(pkts))
    triage.TRIAGE_DIR.mkdir(parents=True, exist_ok=True)
    (triage.TRIAGE_DIR / f"{receipt['triage_id']}.json").write_text(json.dumps(receipt))
    after_triage = len(pen.unconsumed(pkts, pen.effective_decisions(pen.read_log(log))))
    assert after_triage == before == 1  # triage changed NOTHING

    # only the pen consumes (note + operator are mandatory: a decision without
    # a note is not a decision)
    entry = pen.mark(outbox, log, "AR-e1", "acted", "test note", "operator")
    assert entry["decision"] == "acted"
    after_pen = len(pen.unconsumed(pkts, pen.effective_decisions(pen.read_log(log))))
    assert after_pen == 0  # count decreases only after the pen


def test_cli_mark_refused_and_points_to_pen(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(triage, "OUTBOX", tmp_path)
    monkeypatch.setattr(triage, "STATE_FILE", tmp_path / "s.json")
    monkeypatch.setattr("sys.argv", ["outbox_triage.py", "--mark", "AR-x", "COMPOST"])
    assert triage.main() == 2
    out = capsys.readouterr().out
    assert "TRIAGE CANNOT CONSUME" in out
    assert "operator_pen" in out

"""test_triage_cannot_consume.py — the merged consumption-organ invariant.

Operator-ruled anatomy (2026-07-06):
    triage  = eye   (classify · group · propose · emit candidates)
    pen     = hand  (operator marks, hash-chained consumption log)
    guard   = immune system (unconsumed pressure; counts PEN marks only)

Hard invariant under test:
    triage_receipt ⊬ operator_mark
    grouping ⊬ consumption
    route_candidate ⊬ acted

authority=false · sovereign=false · ledger_effect=none
"""

import json
import sys

import pytest

from temple.autoresearch import ci_outbox_guard as guard
from temple.autoresearch import operator_pen as pen
from temple.autoresearch import outbox_triage as triage


def make_outbox(tmp_path, n=3):
    outbox = tmp_path / "outbox"
    outbox.mkdir()
    for i in range(n):
        pid = f"AR-{i:012x}"
        (outbox / f"{pid}.json").write_text(json.dumps({
            "schema": "AUTORESEARCH_PACKET_V1",
            "packet_id": pid,
            "finding_type": "test_gap" if i % 2 == 0 else "risk",
            "summary": f"packet {i}: test coverage gap in module_{i}",
            "source_refs": [f"src/module_{i}.py:1"],
            "risk_flags": [],
            "recommended_action": "review",
            "authority": False,
            "sovereign": False,
            "canon": False,
            "ledger_effect": "none",
            "reducer_required": True,
        }))
    return outbox


def load(outbox):
    return pen.load_packets(outbox)


# --- ruling test 2: triage groups packets deterministically -------------------

def test_triage_grouping_is_deterministic(tmp_path):
    outbox = make_outbox(tmp_path, n=5)
    g1 = triage.group_packets(load(outbox))
    g2 = triage.group_packets(load(outbox))
    assert {k: [p["packet_id"] for p in v] for k, v in g1.items()} == \
           {k: [p["packet_id"] for p in v] for k, v in g2.items()}


# --- ruling test 6: same outbox input gives same triage report ----------------

def test_triage_report_is_deterministic(tmp_path):
    outbox = make_outbox(tmp_path, n=4)
    packets = load(outbox)
    state = {"schema": "TRIAGE_STATE_V0", "authority": False, "decisions": {}}
    r1 = triage.render(packets, state, "text", False, themes=True)
    r2 = triage.render(packets, state, "text", False, themes=True)
    assert r1 == r2


# --- ruling test 3: triage emits candidate receipts without consuming ---------

def test_triage_receipt_does_not_consume(tmp_path):
    outbox = make_outbox(tmp_path, n=3)
    log = tmp_path / "consumption_log.ndjson"
    before = guard.count_unconsumed(outbox=outbox, log=log)
    receipt = triage.make_triage_receipt(triage.group_packets(load(outbox)), 3)
    after = guard.count_unconsumed(outbox=outbox, log=log)
    assert before == after == 3, "emitting a triage receipt must not consume"
    assert receipt["authority"] is False
    assert receipt["reducer_required"] is True
    assert receipt["ledger_effect"] == "none"


# --- ruling tests 4 + 5: pen consumes; guard decreases ONLY after pen ---------

def test_guard_decreases_only_after_pen_not_after_triage(tmp_path):
    outbox = make_outbox(tmp_path, n=3)
    log = tmp_path / "consumption_log.ndjson"
    assert guard.count_unconsumed(outbox=outbox, log=log) == 3

    # exercise the whole eye: classify, group, render, receipt — no consumption
    packets = load(outbox)
    triage.group_packets(packets)
    triage.make_triage_receipt(triage.group_packets(packets), 3)
    state = {"schema": "TRIAGE_STATE_V0", "authority": False, "decisions": {}}
    triage.render(packets, state, "md", False, themes=True)
    assert guard.count_unconsumed(outbox=outbox, log=log) == 3

    # only the hand consumes
    pid = packets[0]["packet_id"]
    pen.mark(outbox, log, pid, "acted", "bounded work created", "JM")
    assert guard.count_unconsumed(outbox=outbox, log=log) == 2


# --- the ruling's most important test ------------------------------------------

def test_most_important_triage_then_pen_flow(tmp_path):
    outbox = make_outbox(tmp_path, n=2)
    log = tmp_path / "consumption_log.ndjson"

    packets = load(outbox)
    triage.render(packets, {"decisions": {}}, "text", False)  # run_triage
    eff = pen.effective_decisions(pen.read_log(log))
    target = packets[0]["packet_id"]
    assert target not in eff, "after triage alone the packet is unconsumed"

    pen.mark(outbox, log, target, "acted", "actioned in test", "JM")
    eff = pen.effective_decisions(pen.read_log(log))
    assert target in eff and eff[target]["decision"] == "acted", \
        "after operator_pen.mark the packet is consumed"


# --- CLI seam: triage --mark refuses and redirects to the pen ------------------

def test_triage_cli_mark_refuses(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv",
                        ["outbox_triage.py", "--mark", "AR-000000000000", "acted"])
    rc = triage.main()
    out = capsys.readouterr().out
    assert rc == 2
    assert "TRIAGE CANNOT CONSUME" in out
    assert "operator_pen.py" in out


# --- guard fails closed on a tampered consumption log --------------------------

def test_guard_fails_closed_on_broken_chain(tmp_path):
    outbox = make_outbox(tmp_path, n=1)
    log = tmp_path / "consumption_log.ndjson"
    pid = load(outbox)[0]["packet_id"]
    pen.mark(outbox, log, pid, "rejected", "not worth acting", "JM")
    entry = json.loads(log.read_text().splitlines()[0])
    entry["decision"] = "acted"  # tamper without re-hashing
    log.write_text(json.dumps(entry, separators=(",", ":")) + "\n")
    with pytest.raises(SystemExit):
        guard.count_unconsumed(outbox=outbox, log=log)

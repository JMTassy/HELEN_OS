"""Tests for apps/goblin-warren/build_jspace_terrain.py — MEMBRANE_DISTANCE_WITNESS_V0.

Proves the Measured Crossing witness is deterministic, floor-1 correct, fail-closed
on a broken pen chain, and a genuine replay witness — and that it never marks.

NON_SOVEREIGN · authority=false · no ledger writes (marks are seeded via the real
operator_pen API, which writes only to a temp garden log).

Run: .venv/bin/pytest tests/test_jspace_terrain_builder.py -v
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _load(rel: str, name: str):
    spec = importlib.util.spec_from_file_location(name, REPO / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bt = _load("apps/goblin-warren/build_jspace_terrain.py", "build_jspace_terrain")
pen = _load("temple/autoresearch/operator_pen.py", "operator_pen")


def _packet(outbox: Path, pid: str, finding_type: str = "risk", **extra) -> None:
    doc = {
        "schema": "AUTORESEARCH_PACKET_V1", "packet_id": pid,
        "finding_type": finding_type, "summary": f"{pid} summary",
        "authority": False, "reducer_required": True,
        "scanned_at": "2026-06-20T21:39:44Z",
    }
    doc.update(extra)
    (outbox / f"{pid}.json").write_text(json.dumps(doc))


@pytest.fixture
def organs(tmp_path):
    outbox = tmp_path / "outbox"
    outbox.mkdir()
    log = tmp_path / "consumption_log.ndjson"
    return outbox, log


# --------------------------------------------------------------------------

def test_unjudged_dream_has_distance_floor_1(organs):
    outbox, log = organs
    _packet(outbox, "AR-aaa")
    w = bt.build_witness(outbox, log)
    row = next(r for r in w["rows"] if r["packet_id"] == "AR-aaa")
    assert row["state"] == "unjudged"
    assert row["distance"] >= 1                       # the floor
    assert row["effective_operator_decision"] is None
    assert any(o["obligation"] == "operator_decision" for o in row["remaining_obligations"])


def test_frontier_is_the_unjudged_set(organs):
    outbox, log = organs
    _packet(outbox, "AR-aaa")
    _packet(outbox, "AR-bbb")
    pen.mark(outbox, log, "AR-bbb", "acted", "operator judged this", "JM")
    w = bt.build_witness(outbox, log)
    assert w["frontier"]["packet_ids"] == ["AR-aaa"]
    assert w["frontier"]["count"] == 1


def test_acted_removes_the_operator_obligation(organs):
    outbox, log = organs
    _packet(outbox, "AR-aaa")
    before = next(r for r in bt.build_witness(outbox, log)["rows"] if r["packet_id"] == "AR-aaa")
    pen.mark(outbox, log, "AR-aaa", "acted", "crossed into admitted reality", "JM")
    after = next(r for r in bt.build_witness(outbox, log)["rows"] if r["packet_id"] == "AR-aaa")
    assert after["state"] == "acted"
    assert after["effective_operator_decision"]["decision"] == "acted"
    assert not any(o["obligation"] == "operator_decision" for o in after["remaining_obligations"])
    assert after["distance"] < before["distance"]


def test_bad_json_packet_fails_readable_obligation(organs):
    outbox, log = organs
    (outbox / "AR-bad.json").write_text("{ not valid json ]")
    w = bt.build_witness(outbox, log)
    row = next(r for r in w["rows"] if r["packet_id"] == "AR-bad")
    readable = next(o for o in row["remaining_obligations"] if o["obligation"] == "readable")
    assert readable["met"] is False


def test_precedent_marks_surface_same_type_history(organs):
    outbox, log = organs
    _packet(outbox, "AR-old", finding_type="risk")
    _packet(outbox, "AR-new", finding_type="risk")
    _packet(outbox, "AR-other", finding_type="observation")
    pen.mark(outbox, log, "AR-old", "rejected", "composted precedent", "JM")
    w = bt.build_witness(outbox, log)
    new_row = next(r for r in w["rows"] if r["packet_id"] == "AR-new")
    other_row = next(r for r in w["rows"] if r["packet_id"] == "AR-other")
    assert any(pm["packet_id"] == "AR-old" for pm in new_row["precedent_marks"])  # same type
    assert other_row["precedent_marks"] == []                                     # different type


def test_deterministic_same_bytes_same_witness(organs):
    outbox, log = organs
    _packet(outbox, "AR-aaa")
    _packet(outbox, "AR-bbb")
    pen.mark(outbox, log, "AR-bbb", "deferred", "not yet", "JM")
    a = bt.render_js(bt.build_witness(outbox, log))
    b = bt.render_js(bt.build_witness(outbox, log))
    assert a == b
    assert "window.jspaceTerrain" in a


def test_replay_witness_check_passes_then_fails_on_tamper(organs, tmp_path):
    outbox, log = organs
    _packet(outbox, "AR-aaa")
    out = tmp_path / "jspace_terrain.js"
    # build
    rc = _run(bt, outbox, log, out, check=False)
    assert rc == 0 and out.exists()
    # check passes on fresh sidecar
    assert _run(bt, outbox, log, out, check=True) == 0
    # tamper → check fails
    out.write_text(out.read_text() + "\n// tampered\n")
    assert _run(bt, outbox, log, out, check=True) == 1


def test_fail_closed_on_broken_chain(organs, tmp_path, capsys):
    outbox, log = organs
    _packet(outbox, "AR-aaa")
    pen.mark(outbox, log, "AR-aaa", "acted", "ok", "JM")
    # Corrupt the chain: flip a byte in the entry_hash line.
    text = log.read_text().replace('"acted"', '"tampered"')
    log.write_text(text)
    w = bt.build_witness(outbox, log)
    assert w["chain_verified"] is False
    out = tmp_path / "jspace_terrain.js"
    rc = _run(bt, outbox, log, out, check=False)
    assert rc == 1                       # fail-closed: refused to emit
    assert not out.exists()
    assert "CHAIN BROKEN" in capsys.readouterr().out


def _run(mod, outbox, log, out, check):
    import sys
    argv = ["build_jspace_terrain.py", "--outbox", str(outbox), "--log", str(log), "--out", str(out)]
    if check:
        argv.append("--check")
    old = sys.argv
    sys.argv = argv
    try:
        return mod.main()
    finally:
        sys.argv = old


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))

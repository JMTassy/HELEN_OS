"""Tests for closure_cutset.py — the minimal observable scheduler kernel.

Law under test:
  - heads are unconsumed leaves; closures partition the unconsumed set (disjoint, total)
  - every ranking field has a provenance string pointing at packet/receipt state
  - confidence is 1.0 only with a receipt field on the head; otherwise 0.5, named as such
  - the cut-set is exact (minimum cardinality, ties on cost) and leaves residual < threshold
  - consumed packets never enter the graph
  - the kernel never writes into the outbox or the pen log
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from temple.autoresearch import closure_cutset as cc
from temple.autoresearch.operator_pen import mark


def put(outbox: Path, pid: str, **fields) -> Path:
    outbox.mkdir(parents=True, exist_ok=True)
    d = {"schema": "AUTORESEARCH_PACKET_V1", "packet_id": pid, "finding_type": "proposal",
         "summary": pid, "authority": False, "sovereign": False, "canon": False,
         "ledger_effect": "none", "reducer_required": True, "source_refs": []}
    d.update(fields)
    p = outbox / f"{pid}.json"
    p.write_text(json.dumps(d))
    return p


@pytest.fixture
def garden(tmp_path):
    outbox, log = tmp_path / "outbox", tmp_path / "consumption_log.ndjson"
    # chain A: E1 <- E2 <- E3 (head E3), one file
    put(outbox, "AR-a-e1", epoch="E1", source_refs=["a.py:1"])
    put(outbox, "AR-a-e2", epoch="E2", parent_epoch="E1", source_refs=["a.py:2"])
    put(outbox, "AR-a-e3", epoch="E3", parent_epoch="E2", source_refs=["a.py:3", "a_test.py:1"],
        falsifier_receipt={"at": "2026-09-04T00:00:00Z", "result": "live"})
    # chain B branches: E4 <- E5, E4 <- E6 (two heads share an ancestor)
    put(outbox, "AR-b-e4", epoch="E4", source_refs=["b.py:1"])
    put(outbox, "AR-b-e5", epoch="E5", parent_epoch="E4", source_refs=["b.py:5"])
    put(outbox, "AR-b-e6", epoch="E6", parent_epoch="E4", source_refs=["b.py:6"])
    # explicit absorption: E8 supersedes E7; dup declares duplicate_of E8
    put(outbox, "AR-c-e7", epoch="E7", source_refs=["c.py:1"])
    put(outbox, "AR-c-e8", epoch="E8", supersedes=["AR-c-e7"], source_refs=["c.py:1"])
    put(outbox, "AR-c-dup", duplicate_of="AR-c-e8")
    # standalone, no refs
    put(outbox, "AR-d-solo")
    # consumed packet: must vanish from the graph
    put(outbox, "AR-z-done", epoch="E9")
    mark(outbox, log, "AR-z-done", "rejected", "test", "JM")
    return outbox, log


def test_closures_partition_unconsumed(garden):
    outbox, log = garden
    rep = cc.compute(outbox, log, threshold=5, bundle_by_file=False)
    assert rep["unconsumed"] == 10 and rep["decided"] == 1
    members = [m for u in rep["units"] for m in u["closure"]]
    assert len(members) == len(set(members)) == 10
    assert "AR-z-done" not in members


def test_heads_are_leaves_and_absorbed_never_head(garden):
    outbox, log = garden
    rep = cc.compute(outbox, log, threshold=5, bundle_by_file=False)
    heads = {u["unit_id"] for u in rep["units"]}
    assert heads == {"AR-a-e3", "AR-b-e5", "AR-b-e6", "AR-c-e8", "AR-d-solo"}
    by = {u["unit_id"]: u for u in rep["units"]}
    assert set(by["AR-a-e3"]["closure"]) == {"AR-a-e3", "AR-a-e2", "AR-a-e1"}
    assert set(by["AR-c-e8"]["closure"]) == {"AR-c-e8", "AR-c-e7", "AR-c-dup"}


def test_shared_ancestor_attributed_once_to_latest_head(garden):
    outbox, log = garden
    rep = cc.compute(outbox, log, threshold=5, bundle_by_file=False)
    by = {u["unit_id"]: u for u in rep["units"]}
    assert "AR-b-e4" in by["AR-b-e6"]["closure"]      # latest epoch wins
    assert "AR-b-e4" not in by["AR-b-e5"]["closure"]


def test_confidence_and_cost_carry_provenance(garden):
    outbox, log = garden
    rep = cc.compute(outbox, log, threshold=5, bundle_by_file=False)
    by = {u["unit_id"]: u for u in rep["units"]}
    assert by["AR-a-e3"]["confidence"] == 1.0 and by["AR-a-e3"]["confidence_source"].startswith("receipt:")
    assert by["AR-b-e5"]["confidence"] == 0.5 and by["AR-b-e5"]["confidence_source"].startswith("default:unverified")
    assert by["AR-a-e3"]["cost"] == 2 and "source_refs.files=2" in by["AR-a-e3"]["cost_source"]
    assert by["AR-d-solo"]["cost"] == 1 and "none→1" in by["AR-d-solo"]["cost_source"]
    assert by["AR-a-e3"]["priority_0"] == pytest.approx(3 * 1.0 / 2)


def test_priority_formula_is_the_declared_one(garden):
    outbox, log = garden
    rep = cc.compute(outbox, log, threshold=5, bundle_by_file=False)
    assert rep["priority_formula"] == "closes * confidence / cost"
    for u in rep["units"]:
        assert u["priority_0"] == pytest.approx(round(u["closes"] * u["confidence"] / u["cost"], 3))


def test_cutset_is_exact_minimum_cardinality(garden):
    outbox, log = garden
    rep = cc.compute(outbox, log, threshold=5, bundle_by_file=False)
    c = rep["cutset"]
    # 10 open, need closed >= 6: sizes are 3,3,2,1,1 → two decisions suffice
    assert c["need_closed"] == 6 and c["k"] == 2 and c["closed"] == 6 and c["residual"] == 4
    assert set(c["members"]) == {"AR-a-e3", "AR-c-e8"}


def test_cutset_ties_break_on_cost():
    u = [dict(unit_id="x", closes=3, cost=5), dict(unit_id="y", closes=3, cost=1), dict(unit_id="z", closes=1, cost=1)]
    c = cc.exact_cutset(u, total=7, threshold=5)     # need closed >= 3
    assert c["k"] == 1 and c["members"] == ["y"] and c["cost"] == 1


def test_bundle_by_file_merges_heads_on_same_top_file(garden):
    outbox, log = garden
    rep = cc.compute(outbox, log, threshold=5, bundle_by_file=True)
    by = {u["unit_id"]: u for u in rep["units"]}
    assert set(by["b.py"]["heads"]) == {"AR-b-e5", "AR-b-e6"} and by["b.py"]["closes"] == 3
    assert by["b.py"]["confidence"] == 0.5


def test_diagnostics_use_declared_discriminators_only(tmp_path):
    outbox, log = tmp_path / "outbox", tmp_path / "log.ndjson"
    put(outbox, "AR-p", epoch="E1", discriminators=["d1"])
    put(outbox, "AR-verif", epoch="E2", parent_epoch="E1", discriminators=["d1"])      # nothing new
    put(outbox, "AR-child", epoch="E3", parent_epoch="E1", discriminators=["d1", "d2"])
    put(outbox, "AR-mute", epoch="E4", parent_epoch="E1")                              # undeclared
    rep = cc.compute(outbox, log, threshold=5, bundle_by_file=False)
    d = rep["diagnostics"]
    assert d["children"] == 3
    assert [v["child"] for v in d["verification_children"]] == ["AR-verif"]
    assert d["undeclared_discriminators"] == 1


def test_kernel_refuses_broken_chain(garden):
    outbox, log = garden
    log.write_text(log.read_text().replace('"entry_hash":"', '"entry_hash":"0'))
    with pytest.raises(SystemExit):
        cc.compute(outbox, log, threshold=5, bundle_by_file=False)


def test_kernel_never_writes_outbox_or_log(garden, tmp_path):
    outbox, log = garden
    before = {p.name: p.read_bytes() for p in outbox.iterdir()}
    log_before = log.read_bytes()
    out = tmp_path / "rep.json"
    assert cc.main(["--outbox", str(outbox), "--log", str(log), "--out", str(out)]) == 0
    assert {p.name: p.read_bytes() for p in outbox.iterdir()} == before
    assert log.read_bytes() == log_before
    rep = json.loads(out.read_text())
    assert rep["authority"] is False and rep["ledger_effect"] == "none"

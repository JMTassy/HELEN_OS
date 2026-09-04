"""PROVENANCE_COMPLETENESS_FALSIFIER_V0

Candidate (RETAINED_CANDIDATE, not doctrine):
    PROVENANCE COMPLETENESS IS AN OBSERVABILITY CONDITION FOR DECISION-DIMENSION MEASUREMENT.
    ΔDiscRank_observed <= ΔDiscRank_true when lineage / supersession edges are missing,
    even though the packets' semantics are unchanged.

Hostile experiment: take one fully declared packet graph, delete only provenance edges
synthetically (packet bodies untouched), and measure
  (a) exact cut-set cardinality — expected to inflate monotonically, and
  (b) the protected quantities — residual, the partition of the unconsumed set, the
      per-packet mechanical marks — expected invariant.
If (a) inflates while (b) holds, the measurement pathology is isolated: provenance loss
changes cut-set inference without changing decision semantics.

Also covers provenance_repair.py: R1/R2 recover only declared parentage, never chronology.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from temple.autoresearch import closure_cutset as cc
from temple.autoresearch import provenance_repair as pr


def put(outbox: Path, pid: str, **fields) -> Path:
    outbox.mkdir(parents=True, exist_ok=True)
    d = {"schema": "AUTORESEARCH_PACKET_V1", "packet_id": pid, "finding_type": "proposal",
         "summary": fields.pop("summary", pid), "authority": False, "sovereign": False, "canon": False,
         "ledger_effect": "none", "reducer_required": True, "source_refs": []}
    d.update(fields)
    p = outbox / f"{pid}.json"
    p.write_text(json.dumps(d))
    return p


def complete_graph(outbox: Path):
    """Three fully declared chains (8, 6, 4) + 4 singletons = 22 packets."""
    n = 1
    for chain, length in (("a", 8), ("b", 6), ("c", 4)):
        prev = None
        for i in range(length):
            e = f"E{n}"
            put(outbox, f"AR-{chain}-{e}", epoch=e, parent_epoch=prev, source_refs=[f"{chain}.py:{i}"])
            prev, n = e, n + 1
    for s in range(4):
        put(outbox, f"AR-s{s}", epoch=f"E{n}", source_refs=[f"s{s}.py:1"]); n += 1


def protected(rep):
    members = sorted(m for u in rep["units"] for m in u["closure"])
    return rep["cutset"]["residual"], members


def test_edge_deletion_inflates_cutset_but_leaves_protected_quantities_invariant(tmp_path):
    outbox, log = tmp_path / "outbox", tmp_path / "log.ndjson"
    complete_graph(outbox)
    base = cc.compute(outbox, log, threshold=5, bundle_by_file=False)
    r0, m0 = protected(base)
    assert base["unconsumed"] == 22 and base["cutset"]["k"] == 3      # a(8)+b(6)+c(4)=18 ≥ 22-4
    ks = [base["cutset"]["k"]]
    # delete provenance edges one at a time, deepest chain first, bodies untouched
    for victim in ("AR-a-E5", "AR-b-E12", "AR-a-E3", "AR-c-E17"):
        p = outbox / f"{victim}.json"; d = json.loads(p.read_text()); d["parent_epoch"] = None; p.write_text(json.dumps(d))
        rep = cc.compute(outbox, log, threshold=5, bundle_by_file=False)
        r, m = protected(rep)
        assert (r, m) == (r0, m0), "protected quantities must not move under edge deletion"
        ks.append(rep["cutset"]["k"])
    assert ks == sorted(ks) and ks[-1] > ks[0], f"cut-set must inflate monotonically: {ks}"


def test_repair_recovers_only_declared_parentage(tmp_path):
    outbox, log = tmp_path / "outbox", tmp_path / "log.ndjson"
    put(outbox, "AR-E1", epoch="E1", next="E2 — verify the thing")
    put(outbox, "AR-E2", epoch="E2")                                              # R1 via E1.next
    put(outbox, "AR-E3", epoch="E3", parent_epoch="E2")
    put(outbox, "AR-E4", epoch="E4", summary="E4: verification of E2+E3 compound")  # R2: refs on chain(E3)
    put(outbox, "AR-E5", epoch="E5", summary="")                                    # empty → untouched
    put(outbox, "AR-E6", epoch="E6", summary="E6: builds on E1 and E4")             # after E4 repair, chain(E4)=E4,E3,E2,E1 → ok
    put(outbox, "AR-E9", epoch="E9", summary="E9: extends E8 which is missing")     # absent ref → untouched
    put(outbox, "AR-E7", epoch="E7", parent_epoch=None, source_refs=["x.py"])
    put(outbox, "AR-E8x", epoch="E10", summary="E10: merges E7 and E3")             # two chains → untouched
    rc = pr.apply(outbox, log, tmp_path / "receipts", do_apply=False)
    got = {r["epoch"]: (r["after"], r["rule"]) for r in rc["repairs"]}
    assert got == {"E2": ("E1", "R1"), "E4": ("E3", "R2"), "E6": ("E4", "R2")}
    left = {u["epoch"] for u in rc["unrecoverable"]}
    assert left == {"E1", "E5", "E7", "E9", "E10"}          # E1 and E7 are roots: nothing to recover
    # dry run wrote nothing
    assert json.loads((outbox / "AR-E2.json").read_text()).get("parent_epoch") is None


def test_repair_apply_writes_receipt_with_pre_post_hashes_and_never_touches_consumed(tmp_path):
    from temple.autoresearch.operator_pen import mark
    outbox, log = tmp_path / "outbox", tmp_path / "log.ndjson"
    put(outbox, "AR-E1", epoch="E1", next="E2 next")
    put(outbox, "AR-E2", epoch="E2")
    put(outbox, "AR-E3", epoch="E3", next="E4 next")
    put(outbox, "AR-E4", epoch="E4")
    mark(outbox, log, "AR-E4", "rejected", "consumed", "JM")
    before_e4 = (outbox / "AR-E4.json").read_bytes()
    rc = pr.apply(outbox, log, tmp_path / "receipts", do_apply=True)
    assert [r["epoch"] for r in rc["repairs"]] == ["E2"]
    r = rc["repairs"][0]
    assert r["pre_sha256"] != r["post_sha256"] and len(r["post_sha256"]) == 64
    d = json.loads((outbox / "AR-E2.json").read_text())
    assert d["parent_epoch"] == "E1" and d["provenance_repairs"][0]["rule"] == "R1"
    assert (outbox / "AR-E4.json").read_bytes() == before_e4
    assert Path(rc["receipt_path"]).exists() and json.loads(Path(rc["receipt_path"]).read_text())["authority"] is False


def test_forward_declaration_is_lineage_only_on_the_same_surface(tmp_path):
    outbox, log = tmp_path / "outbox", tmp_path / "log.ndjson"
    put(outbox, "AR-p", epoch="E1", surface="prompt_compression", next="E2 — operator-apply gate")
    put(outbox, "AR-c", epoch="E2", surface="summarization_weights")            # the E2 that materialised elsewhere
    put(outbox, "AR-q", epoch="E3", surface="skill_routing", next="E4 — count verify")
    put(outbox, "AR-d", epoch="E4", surface="skill_routing")
    rc = pr.apply(outbox, log, tmp_path / "receipts", do_apply=False)
    assert {r["epoch"]: r["after"] for r in rc["repairs"]} == {"E4": "E3"}
    assert any(u["epoch"] == "E2" and "a plan, not lineage" in u["reason"] for u in rc["unrecoverable"])


def test_repair_never_uses_chronology(tmp_path):
    outbox, log = tmp_path / "outbox", tmp_path / "log.ndjson"
    put(outbox, "AR-E1", epoch="E1", summary="E1: root")
    put(outbox, "AR-E2", epoch="E2", summary="E2: something unrelated, names nothing")
    rc = pr.apply(outbox, log, tmp_path / "receipts", do_apply=False)
    assert rc["repairs"] == [] and {u["epoch"] for u in rc["unrecoverable"]} == {"E1", "E2"}


def test_duplicate_discriminator_fails_closed_without_declared_discriminators(tmp_path):
    outbox, log = tmp_path / "outbox", tmp_path / "log.ndjson"
    put(outbox, "AR-a"); put(outbox, "AR-b")
    from temple.autoresearch.operator_pen import load_packets
    v = cc.duplicate_test("AR-a", "AR-b", load_packets(outbox))
    assert v["verdict"] == "UNDECIDABLE"


def test_duplicate_discriminator_distinct_and_duplicate(tmp_path):
    outbox, log = tmp_path / "outbox", tmp_path / "log.ndjson"
    put(outbox, "AR-a", discriminators=["d1"]); put(outbox, "AR-b", discriminators=["d1"]); put(outbox, "AR-c", discriminators=["d2"])
    put(outbox, "AR-z", epoch="E1", discriminators=["z"]); put(outbox, "AR-z2", epoch="E2", parent_epoch="E1", discriminators=["z", "z2"])
    from temple.autoresearch.operator_pen import load_packets
    ps = load_packets(outbox)
    assert cc.duplicate_test("AR-a", "AR-b", ps)["verdict"] == "DUPLICATE"
    assert cc.duplicate_test("AR-a", "AR-c", ps)["verdict"] == "DISTINCT"

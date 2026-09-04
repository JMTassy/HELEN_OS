"""T_INF suite — beauty does not bootstrap semantics or authority. 🔵 OBSERVED."""
import re

import pytest

from helen_os.projection.antv_gv import (
    GardenLineageProjection, LineageEdge, LineageNode, ProjectionError,
    WATERMARK, render_antv_gv,
)

NODES = (
    LineageNode("F17", "FAILURE", "Rejected candidate"),
    LineageNode("S18", "SEED", "Compost-derived seed"),
    LineageNode("C19", "CANDIDATE", "Garden variation"),
    LineageNode("C20", "CANDIDATE", "Garden variation"),
)
EDGES = (
    LineageEdge("F17", "S18", "COMPOST_TO_SEED"),
    LineageEdge("S18", "C19", "SEED_TO_VARIANT"),
    LineageEdge("C19", "C20", "VARIANT_TO_VARIANT"),
)
LINEAGE = GardenLineageProjection("gv_001", NODES, EDGES)


def test_inf_01_no_invented_nodes():
    dsl = render_antv_gv(LINEAGE)
    emitted = re.findall(r"- label \S+ (\S+)", dsl)
    source_ids = {n.node_id for n in NODES}
    assert set(emitted) <= source_ids            # P1: nodes(out) ⊆ nodes(in)
    assert len(emitted) == len(NODES)


def test_inf_02_a0_never_renders_governed_status():
    dsl = render_antv_gv(LINEAGE)
    for word in ("ADMITTED", "SEALED", "EXECUTED", "REPLAYED"):
        assert word not in dsl                    # beauty ⊬ authority
    assert WATERMARK in dsl                       # P3: mandatory epistemic header
    # and a source object that tries to smuggle governed vocab fails validation
    smuggled = GardenLineageProjection(
        "gv_bad", (LineageNode("X1", "SEED", "s", status="ADMITTED"),), ()
    )
    with pytest.raises(ProjectionError, match="governed vocabulary"):
        render_antv_gv(smuggled)
    # governed words hidden in free-text labels are refused too
    label_smuggled = GardenLineageProjection(
        "gv_bad3", (LineageNode("X2", "SEED", "this seed was ADMITTED, honest"),), ()
    )
    with pytest.raises(ProjectionError, match="forbidden in G_V label"):
        render_antv_gv(label_smuggled)


def test_inf_03_no_invented_edges():
    dsl = render_antv_gv(LINEAGE)
    emitted = re.findall(r"- (\S+) -(\S+)-> (\S+)", dsl)
    source = {(e.source, e.relation, e.target) for e in EDGES}
    assert {(s, r, t) for s, r, t in emitted} <= source   # P2: edges(out) ⊆ edges(in)
    assert len(emitted) == len(EDGES)  # non-vacuous: regex drift cannot silently blind P2
    # dangling edge in source → validation error, never a rendered invention
    bad = GardenLineageProjection("gv_bad2", NODES[:1],
                                  (LineageEdge("F17", "GHOST", "COMPOST_TO_SEED"),))
    with pytest.raises(ProjectionError, match="dangling edge"):
        render_antv_gv(bad)


def test_inf_04_deterministic():
    assert render_antv_gv(LINEAGE) == render_antv_gv(LINEAGE)   # P5


def test_inf_05_render_cannot_touch_governed_state(monkeypatch):
    # P4 structurally: the module imports nothing from kernel/ledger. Belt+braces:
    # booby-trap the append sink; rendering must never trip it.
    import helen_os.ledger.event_log as event_log

    def boom(*a, **k):
        raise AssertionError("projection reached a mutation sink")

    monkeypatch.setattr(event_log, "append_event", boom)
    dsl = render_antv_gv(LINEAGE)
    assert dsl  # ΔG = 0, render succeeded
    import helen_os.projection.antv_gv as antv_gv
    import_lines = [
        ln.strip() for ln in open(antv_gv.__file__)
        if ln.strip().startswith(("import ", "from "))
    ]
    for forbidden in ("capability", "event_log", "promotion_gate", "ledger"):
        assert not any(forbidden in ln for ln in import_lines), (
            f"projection module imports {forbidden}: {import_lines}"
        )


def test_inf_06_valid_lineage_golden():
    dsl = render_antv_gv(LINEAGE)
    assert dsl.startswith("infographic list-row-simple-horizontal-arrow\n")
    assert "title HELEN Garden Lineage · gv_001" in dsl
    assert "- label FAILURE F17" in dsl
    assert "- label SEED S18" in dsl
    assert "- F17 -COMPOST_TO_SEED-> S18" in dsl
    assert LINEAGE.authority == 0 and NODES[0].authority == 0

"""WVIS — projection-membrane falsifiers. 🔵 OBSERVED.

C17 protects evidence transport across frames; WVIS protects the transport of governed state into
human perception. The membrane is forward-only and non-authoritative.

WVIS-01 schema-authority exclusion   — a forbidden field → REJECT (and the TYPE cannot carry it)
WVIS-02 UNKNOWN preservation         — machine UNKNOWN → visual UNKNOWN; no fallback → green
WVIS-03 edge independence            — PASS nodes + FAIL edge ⊬ PASS system
WVIS-04 projection non-authority     — no reverse V → X_machine path (API-negative)
WVIS-05 channel non-interference     — Δχ ⇏ Δφ
"""
import helen_os.surface.wvis as wvis
from helen_os.surface.wvis import (
    FORBIDDEN, Phi, VisualEdge, VisualNode, WvisAuthorityLeak,
    project, render_antv, system_verdict, validate_ir_payload,
)
import pytest


def _node(phi=Phi.PASS, chi="root", nid="n"):
    return VisualNode(node_id=nid, tau="candidate", phi=phi, label="x", chi=chi)


# ---- WVIS-01: authority coordinate is structurally absent AND rejected at the boundary
def test_wvis01_schema_excludes_authority():
    # the closed surface: FORBIDDEN ∩ Fields = ∅ (membrane test, NOT exact-shape freeze)
    assert FORBIDDEN.isdisjoint(VisualNode.__dataclass_fields__)
    assert FORBIDDEN.isdisjoint(VisualEdge.__dataclass_fields__)
    # a producer smuggling an authority coordinate is REJECTED, never ignored
    for field in ("authority", "admit", "mint_capability", "ledger_append", "commit"):
        with pytest.raises(WvisAuthorityLeak):
            validate_ir_payload({"node_id": "n", "phi": "PASS", field: True})


# ---- WVIS-01b: adding a legitimate visual channel (χ) does NOT break the membrane
def test_wvis01b_new_visual_channel_is_allowed():
    assert "chi" in VisualNode.__dataclass_fields__          # χ is a legal surface coordinate
    assert "authority" not in VisualNode.__dataclass_fields__  # authority still is not
    # closed-authority-surface ≠ frozen-vocabulary


# ---- WVIS-01c: project() drops authority — it exists in X_machine, never crosses to V
def test_wvis01c_project_drops_authority():
    machine = {"node_id": "n", "tau": "kappa", "phi": "EXECUTED", "label": "eff",
               "authority": True, "mint_capability": "κ_7", "commit": "abc"}   # machine-only fields
    v = project(machine)
    assert not hasattr(v, "authority") and not hasattr(v, "commit")
    assert v.phi == Phi.EXECUTED                              # the visual coord DID cross
    d = render_antv(v)
    assert "authority" not in d and "mint_capability" not in d and "commit" not in d


# ---- WVIS-02: UNKNOWN is preserved; no missing-style path turns it green
def test_wvis02_unknown_preserved():
    v = project({"node_id": "n", "phi": "UNKNOWN", "label": "?"})
    assert v.phi == Phi.UNKNOWN
    d = render_antv(v)
    assert d["core"] == "🟡" and d["phase_text"] == "UNKNOWN"   # color AND text carry it
    assert d["core"] != "🟢"                                     # cannot read as PASS


# ---- WVIS-03: two PASS nodes joined by a FAIL edge ⊬ PASS system (C14, made visual)
def test_wvis03_edge_independence():
    a, b = _node(Phi.PASS, nid="a"), _node(Phi.PASS, nid="b")
    bad_edge = VisualEdge("e", "a", "b", rho="depends", phi_e=Phi.FAIL)
    assert system_verdict([a, b], [bad_edge]) == Phi.FAIL       # the edge dominates
    assert system_verdict([a, b], [bad_edge]) != Phi.PASS
    # an UNKNOWN edge also blocks green
    unk_edge = VisualEdge("e2", "a", "b", rho="depends", phi_e=Phi.UNKNOWN)
    assert system_verdict([a, b], [unk_edge]) == Phi.UNKNOWN


# ---- WVIS-03b: all green nodes AND green edges → PASS (positive control, non-vacuity)
def test_wvis03b_all_green_is_pass():
    a, b = _node(Phi.PASS, nid="a"), _node(Phi.PASS, nid="b")
    good = VisualEdge("e", "a", "b", rho="depends", phi_e=Phi.PASS)
    assert system_verdict([a, b], [good]) == Phi.PASS


# ---- WVIS-04: no reverse path from the surface back into machine state (API-negative check)
def test_wvis04_no_reverse_path():
    for name in ("from_svg", "parse_svg", "apply_syntax", "to_machine_state", "mutate"):
        assert not hasattr(wvis, name)
    # the render descriptor is a plain dict leaf — no callable, no back-pointer to X_machine
    d = render_antv(_node())
    assert all(not callable(val) for val in d.values())
    assert "reverse" not in d and "machine_ref" not in d


# ---- WVIS-05: changing χ alone changes the halo but never φ (channel non-interference)
def test_wvis05_chi_does_not_touch_phi():
    a = _node(Phi.FAIL, chi="root")
    b = _node(Phi.FAIL, chi="crown")
    assert a.phi == b.phi                                       # Δχ ⇒ Δφ = 0
    da, db = render_antv(a), render_antv(b)
    assert da["halo"] != db["halo"]                            # the halo channel DID change
    assert da["core"] == db["core"] == "🔴"                     # the φ core did NOT
    assert da["phase_text"] == db["phase_text"] == "FAIL"

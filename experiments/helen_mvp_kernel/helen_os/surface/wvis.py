"""WVIS — the perceptual-transport membrane. 🔵 OBSERVED · authority=0.

Companion to C17: C17 protects witness transport across FRAMES; WVIS protects governed-state
transport into PERCEPTION. It is a forward-only, non-authoritative projection:

    π_V : X_machine → V_WUL           (V → X_machine is NOT in the public API)

The human surface exposes only (τ glyph, φ epistemic state, χ maturation halo, ρ relation,
provenance-ref). Authority is a machine coordinate; it is UNREPRESENTABLE on the surface — not
merely "not shown," but structurally absent from the schema:

    authority ∉ Schema(V_WUL)    (a closed authority surface, enforced, not documented)

CONSTITUTIONAL SUBTLETY (why this exists): a closed authority surface ≠ a frozen visual
vocabulary. Adding a new visual channel (e.g. χ) is legitimate and must NOT break the membrane;
the invariant is `FORBIDDEN ∩ Fields = ∅`, never an exact-field-set equality that would freeze
evolution. render ⊬ admission; SVG ⊬ X_machine; ⋀ Green(node) ⊬ Green(system).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Phi(Enum):                       # φ — local epistemic state (NEVER truth, NEVER authority)
    RAW = "RAW"
    OBSERVED = "OBSERVED"
    HYPOTHESIS = "HYPOTHESIS"
    UNKNOWN = "UNKNOWN"
    FAIL = "FAIL"
    PASS = "PASS"                      # passed a DECLARED check — not "true"
    EXECUTED = "EXECUTED"
    COMPOST = "COMPOST"
    REPLAYED = "REPLAYED"


# φ → core color · χ → halo mark · φ → redundant text tag (so meaning survives grayscale/tests)
PHASE_COLOR = {
    Phi.RAW: "⚪", Phi.OBSERVED: "🔵", Phi.HYPOTHESIS: "🟣", Phi.UNKNOWN: "🟡",
    Phi.FAIL: "🔴", Phi.PASS: "🟢", Phi.EXECUTED: "🟠", Phi.COMPOST: "🟤", Phi.REPLAYED: "🔷",
}
# χ halo is a DISTINCT channel from φ core — deliberately not the φ palette (WVIS-05 non-interference)
CHI_MARK = {
    "root": "◍¹", "sacral": "◍²", "plexus": "◍³", "heart": "◍⁴",
    "throat": "◍⁵", "third_eye": "◍⁶", "crown": "◍⁷",
}

# authority coordinates that may NEVER appear in the visual IR (the closed surface)
FORBIDDEN = frozenset({
    "authority", "admit", "mint_capability", "authorization_instance_mutator",
    "ledger_append", "commit", "mutate_governed_state",
})


class WvisAuthorityLeak(Exception):
    pass


@dataclass(frozen=True)
class VisualNode:
    node_id: str
    tau: str                # glyph / functional type (seed, goblin, candidate, witness, hal, ...)
    phi: Phi                # epistemic state
    label: str
    chi: str = "root"       # maturation halo — a legitimate visual channel, NOT authority
    frame_ref: str = ""     # which frame this projection describes
    provenance_ref: str = ""  # inspectable provenance HANDLE — never enough to derive authority


@dataclass(frozen=True)
class VisualEdge:
    edge_id: str
    source: str
    target: str
    rho: str                # relation type
    phi_e: Phi              # the EDGE carries its OWN witness state (two green nodes ⊬ green edge)
    witness_ref: str = ""


# structural guarantee: neither surface type can carry an authority coordinate
assert FORBIDDEN.isdisjoint(VisualNode.__dataclass_fields__)
assert FORBIDDEN.isdisjoint(VisualEdge.__dataclass_fields__)


def validate_ir_payload(raw: dict) -> None:
    """Reject a visual-IR dict that smuggles an authority coordinate. REJECT, never silently ignore."""
    bad = FORBIDDEN & set(raw)
    if bad:
        raise WvisAuthorityLeak(f"E_AUTHORITY_IN_SURFACE: {sorted(bad)}")


def project(machine_state: dict) -> VisualNode:
    """π_V: read ONLY the visual coordinates from a governed machine state. Authority (and every
    other machine-only field) is dropped, never carried forward — the membrane is one-directional."""
    return VisualNode(
        node_id=machine_state["node_id"],
        tau=machine_state.get("tau", "node"),
        phi=machine_state["phi"] if isinstance(machine_state["phi"], Phi) else Phi(machine_state["phi"]),
        label=machine_state.get("label", ""),
        chi=machine_state.get("chi", "root"),
        frame_ref=machine_state.get("frame_ref", ""),
        provenance_ref=machine_state.get("provenance_ref", ""),
    )   # note: machine_state["authority"], ["admit"], ... are simply never read.


def system_verdict(nodes, edges) -> Phi:
    """A GRAPH verdict, computed from nodes AND edges. Green graph requires every node PASS AND
    every edge PASS. Two green nodes joined by a FAIL/UNKNOWN edge never render as a green system."""
    states = [n.phi for n in nodes] + [e.phi_e for e in edges]
    if any(s == Phi.FAIL for s in states):
        return Phi.FAIL
    if any(s == Phi.UNKNOWN for s in states):
        return Phi.UNKNOWN
    if nodes and all(n.phi == Phi.PASS for n in nodes) and all(e.phi_e == Phi.PASS for e in edges):
        return Phi.PASS
    return Phi.UNKNOWN      # mixed non-fail/non-pass → not certifiable green


def render_antv(node: VisualNode) -> dict:
    """Projection-only render descriptor (an AntV-ready node spec). Carries core color (φ), halo
    (χ), and a redundant φ text tag so the state survives grayscale/missing-style. NO authority,
    and no path back to X_machine — this is a leaf of the membrane."""
    return {
        "id": node.node_id,
        "glyph": node.tau,                         # τ
        "core": PHASE_COLOR[node.phi],             # φ → color
        "halo": CHI_MARK.get(node.chi, "◍?"),      # χ → halo (distinct channel)
        "phase_text": node.phi.value,              # φ → redundant text (accessibility + tests)
        "label": node.label,
        "provenance_ref": node.provenance_ref,     # a handle, not a capability
    }   # deliberately absent: authority, admit, mint, commit, ledger, any reverse pointer.

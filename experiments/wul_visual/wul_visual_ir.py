"""WULVisualIR — the typed one-way projection from proof state to perception.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

    Kernel -> WUL Visual IR -> AntV syntax -> SVG -> human perception

One-way, typed, streamable. There is deliberately NO privileged inverse:
an edited SVG is not a governed state, and this module contains no
function that turns rendering back into truth.

    D_AntV o pi_WUL : X -> SVG          exists
    SVG -> X_governed                    does not

The machine state is X = (tau, phi, chi, rho, p, a). The projection is
pi_visual(X) = (tau, phi, chi, rho) with a provenance REFERENCE only:

    tau  glyph      what kind of thing it is        (ontology)
    phi  colour     epistemic phase                 (state, never truth)
    chi  maturity   progression energy              (NOT epistemic, NOT authority)
    rho  edge       relation status                 (claimed..admitted)
    p    ref        drill-down pointer, not payload
    a    ABSENT     authority is not a visual coordinate at all

Look at what this IR cannot express: there is no authority field, no
admit(), no mint_cap(), no ledger_write(). The renderer does not need
them, so it does not get them. Beauty cannot manufacture rights.

THE NON-FUSION LAW, as a graph property:

    phi(v_i)=PASS AND phi(v_j)=PASS  does NOT imply  phi(e_ij)=PASS

Conventional dashboards propagate green downstream. Here every edge
carries its own status, so two green nodes joined by an unwitnessed
edge render — and compute — as DISCONTINUOUS.

Deterministic: sorted output, canonical serialization, no wall-time.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, replace

# ── tau: ontology ────────────────────────────────────────────────────────
GLYPH = {
    "CHAOS": "🌪️", "SEED": "🌰", "GOBLIN": "👺", "CANDIDATE": "△",
    "WITNESS": "👁️", "HAL": "🛡️", "GATEHOUSE": "⚖️", "AUTHORIZATION": "🪪",
    "LEASE": "🔑", "EFFECT": "⚡", "RECEIPT": "🧾", "LEDGER": "📜",
    "REPLAY": "🔷", "COMPOST": "🟤", "PROJECTION": "✨", "GARDEN": "🌿",
    "TEST": "🧪", "COVERAGE": "🪪", "SUPPORT": "🧬", "SCOPE": "🕳", "OPAQUE": "⚪",
}

# ── phi: epistemic phase (state, never truth, never authority) ───────────
PHASE = {
    "RAW": "⚪", "OBSERVED": "🔵", "HYPOTHESIS": "🟣", "UNKNOWN": "🟡",
    "FAIL": "🔴", "PASS": "🟢", "EXECUTED": "🟠", "COMPOST": "🟤",
    "TRANSPORTED": "🔷",
}
PHASE_COLOR = {
    "RAW": "#94a3b8", "OBSERVED": "#2563eb", "HYPOTHESIS": "#7c3aed",
    "UNKNOWN": "#eab308", "FAIL": "#dc2626", "PASS": "#16a34a",
    "EXECUTED": "#ea580c", "COMPOST": "#78350f", "TRANSPORTED": "#0891b2",
}

# ── chi: maturation energy — a THIRD axis, not epistemic, not authority ──
CHI = ("root", "sacral", "plexus", "heart", "throat", "third_eye", "crown")
CHI_MARK = {"root": "🔴", "sacral": "🟠", "plexus": "🟡", "heart": "🟢",
            "throat": "🔵", "third_eye": "🟣", "crown": "⚪"}

# ── rho: relation status — claimed .. admitted, plus the forbidden ───────
RELATION = ("CLAIMED", "OBSERVED", "WITNESSED", "ADMITTED", "FORBIDDEN")
RELATION_RENDER = {
    "CLAIMED": "┄┄?┄┄>",     # unwitnessed: broken line
    "OBSERVED": "--->",       # seen, not verified
    "WITNESSED": "━━━>",      # witnessed morphism: solid
    "ADMITTED": "===>",       # crossed the gate
    "FORBIDDEN": "──╳──",     # constitutionally impossible
}
# Only these carry epistemic continuity across a path.
CONTINUOUS = frozenset({"WITNESSED", "ADMITTED"})

# ── the visual constitution: morphisms that must never exist ─────────────
FORBIDDEN_MORPHISMS = frozenset({
    ("GARDEN", "LEDGER"),          # 🌿 ╳ 📜  garden output is not history
    ("PROJECTION", "GATEHOUSE"),   # ✨ ╳ ⚖   beauty is not admission
    ("GOBLIN", "LEASE"),           # 👺 ╳ 🔑  swarm cannot mint capability
    ("COMPOST", "LEDGER"),         # 🟤 ╳ 📜  compost is not commit
    ("CANDIDATE", "LEASE"),        # 🟣 ╳ 🔑  hypothesis is not permission
    ("WITNESS", "GATEHOUSE"),      # 👁 ╳ ⚖   observation is not admission
    ("HAL", "LEASE"),              # 🛡 ╳ 🔑  HAL PASS is not capability
})


@dataclass(frozen=True)
class VisualNode:
    """Note the absent field: there is no `authority`. Uninhabited beats
    carrying false — a field that does not exist cannot be set to 1."""
    node_id: str
    tau: str                     # ontology key
    phi: str                     # epistemic phase key
    label: str
    chi: str = "root"            # maturation, independent of phi
    frame_ref: str = ""          # which frame this was observed in
    provenance_ref: str = ""     # a POINTER, never the evidence itself
    tooltip: str = ""

    def __post_init__(self):
        if self.tau not in GLYPH:
            raise ValueError(f"E_UNTYPED_GLYPH:{self.tau}")
        if self.phi not in PHASE:
            raise ValueError(f"E_UNTYPED_PHASE:{self.phi}")
        if self.chi not in CHI:
            raise ValueError(f"E_UNTYPED_CHI:{self.chi}")

    def advance_chi(self) -> "VisualNode":
        """chi may progress WITHOUT touching phi, authority, or canon."""
        i = CHI.index(self.chi)
        return replace(self, chi=CHI[min(i + 1, len(CHI) - 1)])

    def channels(self) -> dict:
        """The four visual dimensions on PHYSICALLY DISTINCT channels, so
        chi styling can never overwrite phi. A high-maturation falsified
        node reads as a purple HALO around a red CORE, never an
        ambiguous blend."""
        return {
            "glyph": GLYPH[self.tau],       # tau -> the mark
            "core": PHASE_COLOR[self.phi],  # phi -> fill / status core
            "halo": CHI_MARK[self.chi],     # chi -> outer ring, separate
            "phase_text": self.phi,         # phi in text: colour not sole carrier
        }

    def render(self) -> str:
        """Glyph names the creature; core colour tells its weather; halo
        shows maturation; the phase is ALSO written in text so it survives
        grayscale and screen readers."""
        c = self.channels()
        return f"{PHASE[self.phi]}{c['glyph']} {self.label} [{self.phi}]·χ{c['halo']}"


@dataclass(frozen=True)
class VisualEdge:
    src: str
    dst: str
    rho: str                     # relation status — its OWN status
    label: str = ""

    def __post_init__(self):
        if self.rho not in RELATION:
            raise ValueError(f"E_UNTYPED_RELATION:{self.rho}")


class VisualGraph:
    def __init__(self, title: str, desc: str = ""):
        self.title, self.desc = title, desc
        self.nodes: dict = {}
        self.edges: list = []

    def add_node(self, node: VisualNode) -> VisualNode:
        self.nodes[node.node_id] = node
        return node

    def add_edge(self, src: str, dst: str, rho: str, label: str = "") -> VisualEdge:
        """A morphism in FORBIDDEN_MORPHISMS may only be drawn as
        FORBIDDEN. Attempting to render it as a normal relation is a
        constitutional violation, not a styling choice."""
        s, d = self.nodes.get(src), self.nodes.get(dst)
        if s is None or d is None:
            raise ValueError("E_UNKNOWN_NODE")
        if (s.tau, d.tau) in FORBIDDEN_MORPHISMS and rho != "FORBIDDEN":
            raise ValueError(f"E_FORBIDDEN_MORPHISM:{s.tau}->{d.tau}")
        e = VisualEdge(src, dst, rho, label)
        self.edges.append(e)
        return e

    # ── the non-fusion law, computed ────────────────────────────────────
    def path_verdict(self, path: list) -> dict:
        """Green nodes do NOT make a green path. Continuity requires every
        node PASS-or-better AND every edge WITNESSED-or-ADMITTED. The first
        discontinuity is named, so a human sees exactly where truth stops."""
        for nid in path:
            if nid not in self.nodes:
                return {"verdict": "UNKNOWN", "reason": f"E_NO_NODE:{nid}"}
        for a, b in zip(path, path[1:]):
            edge = next((e for e in self.edges if e.src == a and e.dst == b), None)
            if edge is None:
                return {"verdict": "DISCONTINUOUS", "break_at": (a, b),
                        "reason": "E_NO_EDGE"}
            if edge.rho == "FORBIDDEN":
                return {"verdict": "FORBIDDEN", "break_at": (a, b),
                        "reason": "E_CONSTITUTIONAL"}
            if edge.rho not in CONTINUOUS:
                return {"verdict": "DISCONTINUOUS", "break_at": (a, b),
                        "reason": f"E_EDGE_{edge.rho}"}
        weak = [n for n in path if self.nodes[n].phi not in
                ("PASS", "TRANSPORTED", "EXECUTED")]
        if weak:
            return {"verdict": "DISCONTINUOUS", "break_at": weak[0],
                    "reason": "E_NODE_NOT_PASS"}
        return {"verdict": "WITNESSED_CONTINUOUS", "length": len(path)}

    # ── compile to AntV syntax (presentation only) ──────────────────────
    def to_antv(self, template: str = "relation-dagre-flow-tb-badge-card") -> str:
        lines = [f"infographic {template}", "data", f"  title {self.title}"]
        if self.desc:
            lines.append(f"  desc {self.desc}")
        lines.append("  nodes")
        for nid in sorted(self.nodes):
            n = self.nodes[nid]
            lines += [f"    - id {nid}", f"      label {n.render()}"]
        if self.edges:
            lines.append("  relations")
            for e in self.edges:
                mark = RELATION_RENDER[e.rho]
                tag = f"{e.rho}{(' ' + e.label) if e.label else ''}"
                lines.append(f"    {e.src} - {tag} {mark} -> {e.dst}"
                             if e.rho != "FORBIDDEN"
                             else f"    {e.src} - FORBIDDEN ╳ -> {e.dst}")
        # Palette ordered to match each node's phase: colour IS state.
        palette = " ".join(PHASE_COLOR[self.nodes[n].phi] for n in sorted(self.nodes))
        lines += ["theme", f"  palette {palette}"]
        return "\n".join(lines)


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


# ── closed schema: absence must be UNINJECTABLE, not merely undocumented ─

_ALLOWED_NODE = frozenset({"node_id", "tau", "phi", "label", "chi",
                           "frame_ref", "provenance_ref", "tooltip"})
_ALLOWED_EDGE = frozenset({"src", "dst", "rho", "label"})
_FORBIDDEN_FIELDS = frozenset({"authority", "admit", "mint_capability",
                               "authorization_instance_mutator",
                               "ledger_append", "commit",
                               "mutate_governed_state"})


def validate_node_dict(d: dict) -> None:
    """Closed schema check — the ruling's additionalProperties:false, as
    code. Unknown fields REJECT (never silently ignored), and every field
    in _FORBIDDEN_FIELDS raises a distinct error class so a producer that
    tried to smuggle authority is reported by name."""
    if not isinstance(d, dict):
        raise TypeError("E_ILL_TYPED_NODE")
    banned = set(d) & _FORBIDDEN_FIELDS
    if banned:
        raise ValueError(f"E_AUTHORITY_INJECTION:{','.join(sorted(banned))}")
    extra = set(d) - _ALLOWED_NODE
    if extra:
        raise ValueError(f"E_UNKNOWN_FIELDS:{','.join(sorted(extra))}")


def validate_edge_dict(d: dict) -> None:
    if not isinstance(d, dict):
        raise TypeError("E_ILL_TYPED_EDGE")
    banned = set(d) & _FORBIDDEN_FIELDS
    if banned:
        raise ValueError(f"E_AUTHORITY_INJECTION:{','.join(sorted(banned))}")
    extra = set(d) - _ALLOWED_EDGE
    if extra:
        raise ValueError(f"E_UNKNOWN_FIELDS:{','.join(sorted(extra))}")


# ── decodable projection: P(R(v)) ≡ v on protected coordinates ──────────

_GLYPH_INV = {v: k for k, v in GLYPH.items()}
_PHASE_INV = {v: k for k, v in PHASE.items()}
_RELATION_MARK_INV = {v: k for k, v in RELATION_RENDER.items()}


def parse_node_render(rendered: str) -> dict:
    """Reverse the display back to (tau, phi) on the protected axes. This
    is NOT an inverse of the IR — it decodes only the phase and glyph and
    remains structurally incapable of surfacing authority (there is no
    slot for it)."""
    if not rendered:
        raise ValueError("E_EMPTY_RENDER")
    phi_mark = rendered[0]
    phi = _PHASE_INV.get(phi_mark)
    if phi is None:
        raise ValueError(f"E_UNDECODABLE_PHASE:{phi_mark!r}")
    tau = None
    for glyph, key in _GLYPH_INV.items():
        if glyph in rendered:
            tau = key
            break
    if tau is None:
        raise ValueError("E_UNDECODABLE_GLYPH")
    return {"tau": tau, "phi": phi}


def projection_fidelity(node: "VisualNode") -> dict:
    """The ruling's V0 theorem, executable:
        V_WUL -R-> SVG -P-> V_WUL^     with     P(R(v)) ≡ v on {τ, φ}
    Returns the decoded pair alongside the source pair so equality is
    computable, not asserted-by-decoration."""
    decoded = parse_node_render(node.render())
    return {"source": {"tau": node.tau, "phi": node.phi},
            "decoded": decoded,
            "faithful": decoded == {"tau": node.tau, "phi": node.phi}}


# ═══ the three HELEN-native structures ═══════════════════════════════════

def helen_witness_flow(edge_status: dict | None = None) -> VisualGraph:
    """Structure 1 — the constitutional spine, every edge carrying its own
    status so the eye cannot infer a validated chain from green nodes."""
    g = VisualGraph("HELEN · Witness Flow", "each edge carries its own status")
    spine = [("seed", "SEED", "RAW"), ("goblin", "GOBLIN", "HYPOTHESIS"),
             ("candidate", "CANDIDATE", "HYPOTHESIS"),
             ("witness", "WITNESS", "OBSERVED"), ("hal", "HAL", "PASS"),
             ("gate", "GATEHOUSE", "PASS"), ("alpha", "AUTHORIZATION", "PASS"),
             ("lease", "LEASE", "PASS"), ("effect", "EFFECT", "EXECUTED"),
             ("receipt", "RECEIPT", "OBSERVED"), ("ledger", "LEDGER", "PASS"),
             ("replay", "REPLAY", "TRANSPORTED")]
    for nid, tau, phi in spine:
        g.add_node(VisualNode(nid, tau, phi, nid.upper()))
    status = edge_status or {}
    ids = [s[0] for s in spine]
    for a, b in zip(ids, ids[1:]):
        g.add_edge(a, b, status.get((a, b), "WITNESSED"))
    return g


def helen_goblin_garden(branches: list) -> VisualGraph:
    """Structure 2 — swarm as TOPOLOGY, not consensus. The visual unit is
    the branch: lineage, outcome, compost loop. No vote counts anywhere."""
    g = VisualGraph("HELEN · Goblin Garden", "topology of divergence and pruning")
    g.add_node(VisualNode("seed", "SEED", "RAW", "SEED", chi="root"))
    for i, br in enumerate(branches):
        gid, cid = f"goblin{i}", f"cand{i}"
        g.add_node(VisualNode(gid, "GOBLIN", "HYPOTHESIS", br["operator"],
                              chi="sacral", provenance_ref=br.get("lineage", "")))
        g.add_node(VisualNode(cid, "CANDIDATE", br["outcome"], br["variation"],
                              chi=br.get("chi", "plexus")))
        g.add_edge("seed", gid, "WITNESSED", "spawn")
        g.add_edge(gid, cid, "OBSERVED", "propose")
        if br["outcome"] == "FAIL":
            comp = f"compost{i}"
            g.add_node(VisualNode(comp, "COMPOST", "COMPOST", "nutrient", chi="root"))
            g.add_edge(cid, comp, "WITNESSED", "metabolize")
            g.add_edge(comp, "seed", "WITNESSED", "reseed")   # the loop closes
    return g


def helen_c17_coverage(d_pos: int, d_neg: int, u_open: list,
                       stable: bool | None) -> VisualGraph:
    """Structure 3 — why HELEN refused transport, legible in seconds.
    The proof debugger: U != {} short-circuits to UNKNOWN before stability
    is even consulted (COVERAGE -> STABILITY -> TRANSPORT)."""
    g = VisualGraph("HELEN · C17 Coverage",
                    f"U={'open' if u_open else 'empty'} · stable={stable}")
    g.add_node(VisualNode("pi", "COVERAGE", "OBSERVED", "Pi_D certificate"))
    g.add_node(VisualNode("dpos", "SUPPORT", "OBSERVED", f"D+ covered ({d_pos})"))
    g.add_node(VisualNode("dneg", "SCOPE", "OBSERVED", f"D- scope ({d_neg})"))
    g.add_node(VisualNode("u", "OPAQUE", "UNKNOWN" if u_open else "PASS",
                          f"U opaque ({len(u_open)})",
                          tooltip=",".join(u_open)))
    for n in ("dpos", "dneg", "u"):
        g.add_edge("pi", n, "WITNESSED", "derives")
    if u_open:
        g.add_node(VisualNode("unknown", "HAL", "UNKNOWN", "UNKNOWN"))
        g.add_edge("u", "unknown", "WITNESSED", "U != empty")
        return g
    g.add_node(VisualNode("stab", "HAL", "PASS" if stable else "FAIL",
                          "StableDeps?"))
    g.add_edge("u", "stab", "WITNESSED", "coverage ok")
    verdict = ("VALID_BY_TRANSPORT", "TRANSPORTED") if stable \
        else ("INVALIDATED", "FAIL")
    g.add_node(VisualNode("verdict", "REPLAY" if stable else "COMPOST",
                          verdict[1], verdict[0]))
    g.add_edge("stab", "verdict", "WITNESSED" if stable else "OBSERVED", "decide")
    return g


def sacred_map() -> VisualGraph:
    """The constitution itself, with forbidden morphisms drawn as ╳ —
    a machine-derived diagram of what can never happen."""
    g = VisualGraph("HELEN · Sacred Map", "forbidden morphisms are rendered, not hidden")
    for nid, tau, phi in [("garden", "GARDEN", "HYPOTHESIS"),
                          ("proj", "PROJECTION", "RAW"),
                          ("goblin", "GOBLIN", "HYPOTHESIS"),
                          ("ledger", "LEDGER", "PASS"),
                          ("gate", "GATEHOUSE", "PASS"),
                          ("lease", "LEASE", "PASS")]:
        g.add_node(VisualNode(nid, tau, phi, nid.upper()))
    for a, b in [("garden", "ledger"), ("proj", "gate"), ("goblin", "lease")]:
        g.add_edge(a, b, "FORBIDDEN")
    return g

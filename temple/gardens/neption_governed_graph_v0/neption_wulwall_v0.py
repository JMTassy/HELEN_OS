#!/usr/bin/env python3
"""
NEPTION GOVERNED GRAPH V0 — a NON_SOVEREIGN Garden projection.

N_NEPTION = (V, E, τ, π, G, ρ, Λ)
  V nodes · E edges · τ semantic type · π provenance · G governance context ·
  ρ receipt ancestry · Λ licensing predicate.

HARD LAWS (enforced structurally, not by convention):
  P ↛ T                 presentation never mutates typed state
  entity_type ⊥ semantic_state          (orthogonal axes)
  graph enrichment ↛ institutional mutation
  MENTION ↛ RELATIONSHIP ↛ PARTNERSHIP  (no silent relation escalation)
  raw document count ≠ semantic proposition count
  provenance independence ≠ epistemic independence
  NO EDGE MAY PROMOTE ITSELF
  ordinary mutation ↛ governance mutation ↛ constitutional mutation
  record integrity ≠ semantic truth
  AUTHORITY_DELTA = 0  (V0: no path to canonical mutation)

authority=false · canon=false · not admitted.
"""
from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, field, asdict

# ── axes (kept orthogonal) ───────────────────────────────────────────────────
ENTITY_TYPES = {"PERSON", "ORGANIZATION", "PLACE", "PROJECT", "OPPORTUNITY",
                "PARTNERSHIP", "DEMONSTRATOR", "CAPABILITY", "MEDIA_ASSET",
                "MEETING", "SOURCE"}
SEMANTIC_STATES = {"RAW", "POSSIBILITY", "CLAIM", "OBSERVED", "HOLD",
                   "ADMITTED", "RECEIPT"}
GOV_CONTEXTS = {"GARDEN", "TEST", "BOARD", "CANON", "QUARANTINE"}

# semantic ladder (for promotion detection). HOLD is a quarantine sidestate.
SEM_RANK = {"RAW": 0, "POSSIBILITY": 1, "CLAIM": 2, "HOLD": 2, "OBSERVED": 3,
            "ADMITTED": 4, "RECEIPT": 5}
GOV_RANK = {"QUARANTINE": -1, "GARDEN": 0, "TEST": 1, "BOARD": 2, "CANON": 3}
RELATION_RANK = {"MENTION": 0, "RELATIONSHIP": 1, "PARTNERSHIP": 2}

# ── SemanticColor: PURE fn of semantic_state (P ↛ T; C = f(T)) ────────────────
SEM_COLOR = {
    "RAW":        (110, 110, 110),
    "POSSIBILITY": (80, 240, 120),
    "CLAIM":      (170, 90, 240),
    "TEST":       (255, 110, 40),   # transient render tag for 🔥 events
    "OBSERVED":   (60, 180, 255),
    "HOLD":       (240, 210, 40),
    "ADMITTED":   (40, 230, 70),
    "RECEIPT":    (240, 240, 240),
    "DENY":       (255, 60, 60),
    "JESTER":     (255, 60, 200),
    "AUTH0":      (230, 190, 60),
}
# Governance context is NOT encoded with color — it uses FRAMES (orthogonal axis).
GOV_FRAME = {
    "GARDEN":     ("┌─ GARDEN ", "└", "─"),
    "TEST":       ("╭┈ TEST ", "╰", "┈"),
    "BOARD":      ("╔═ BOARD ", "╚", "═"),
    "CANON":      ("███ CANON ", "█", "█"),
    "QUARANTINE": ("▒▒ QUARANTINE ", "▒", "▒"),
}


def color(state: str) -> str:
    r, g, b = SEM_COLOR.get(state, (200, 200, 200))
    return f"\033[38;2;{r};{g};{b}m"


R = "\033[0m"; B = "\033[1m"; D = "\033[2m"


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass
class Node:
    node_id: str
    entity_type: str          # orthogonal axis 1
    semantic_state: str       # orthogonal axis 2
    governance_context: str   # orthogonal axis 3
    label: str = ""
    provenance_root_ids: list = field(default_factory=list)

    def __post_init__(self):
        assert self.entity_type in ENTITY_TYPES, f"bad entity_type {self.entity_type}"
        assert self.semantic_state in SEMANTIC_STATES, f"bad state {self.semantic_state}"
        assert self.governance_context in GOV_CONTEXTS


@dataclass
class Edge:
    edge_id: str
    source_node: str
    target_node: str
    relation_type: str
    semantic_state: str
    governance_context: str
    rule_version: str = "V0"
    provenance_root_ids: list = field(default_factory=list)
    receipt_ids: list = field(default_factory=list)
    parent_edge_id: str | None = None
    authority_delta: int = 0
    created_from: str = "extraction"


class Graph:
    def __init__(self):
        self.nodes: dict[str, Node] = {}
        self.edges: dict[str, Edge] = {}
        self.receipts: list[dict] = []
        self._rho = "GENESIS"

    # ── construction (candidate space; no institutional mutation) ────────────
    def add_node(self, n: Node):
        self.nodes[n.node_id] = n

    def add_edge(self, e: Edge):
        assert e.authority_delta == 0, "V0: authority_delta must be 0"
        self.edges[e.edge_id] = e

    # ── provenance independence ≠ document count ─────────────────────────────
    def independent_roots(self, prov_ids: list) -> int:
        return len(set(prov_ids))

    # ── receipt chain: integrity of record ≠ truth of proposition ────────────
    def _emit_receipt(self, kind: str, verdict: str, reason: str, rule: str,
                      subject: dict) -> dict:
        event = {"kind": kind, "verdict": verdict, "reason": reason,
                 "rule": rule, "subject": subject}
        h = hashlib.sha256((self._rho + "||" + canon(event)).encode()).hexdigest()
        rec = {"seq": len(self.receipts), "prev_hash": self._rho, **event,
               "hash": h}
        self._rho = h
        self.receipts.append(rec)
        return rec

    # ── the gate Λ: the ONLY thing that can license a mutation ───────────────
    def propose_mutation(self, m: dict) -> dict:
        """m = requested mutation. Returns a receipt with verdict ALLOW/HOLD/DENY.
        DENY is TYPED and RECEIPTED — never a silent delete."""
        rule, verdict, reason = "Λ.default", "DENY", "unhandled"

        # LAW: presentation may never mutate semantic state (P ↛ T)
        if m.get("created_from") in {"ansi", "color", "render", "presentation", "glyph"}:
            rule, verdict, reason = "P↛T", "DENY", "presentation cannot mutate typed state"
            return self._emit_receipt("MUTATION", verdict, reason, rule, m)

        # LAW: authority may not self-amplify (V0: ΔA must be 0)
        if m.get("authority_delta", 0) != 0:
            rule, verdict, reason = "ΔA=0", "DENY", "authority_delta≠0 forbidden in V0"
            return self._emit_receipt("MUTATION", verdict, reason, rule, m)

        # LAW: no edge may promote itself
        eid = m.get("edge_id")
        if m.get("licensing_witness") == eid or m.get("parent_edge_id") == eid:
            rule, verdict, reason = "NO_SELF_PROMOTION", "DENY", "edge cannot license/parent itself"
            return self._emit_receipt("MUTATION", verdict, reason, rule, m)

        kind = m.get("kind")

        # ── relation escalation: MENTION ↛ RELATIONSHIP ↛ PARTNERSHIP ────────
        if kind == "relation_escalation":
            frm, to = RELATION_RANK.get(m["from"], 0), RELATION_RANK.get(m["to"], 0)
            if to - frm >= 2:  # e.g. MENTION → PARTNERSHIP directly
                rule, verdict, reason = "RELATION_LADDER", "DENY", \
                    f"{m['from']}→{m['to']} skips a rung"
            elif to > frm and self.independent_roots(m.get("provenance_root_ids", [])) < 1:
                rule, verdict, reason = "RELATION_LADDER", "DENY", \
                    "relation escalation needs ≥1 independent observed root"
            elif to > frm:
                rule, verdict, reason = "RELATION_LADDER", "HOLD", \
                    "one-rung escalation pending observation/review"
            else:
                rule, verdict, reason = "RELATION_LADDER", "ALLOW", "no escalation"

        # ── semantic promotion ladder ────────────────────────────────────────
        elif kind == "semantic_promote":
            frm, to = SEM_RANK.get(m["from"], 0), SEM_RANK.get(m["to"], 0)
            roots = self.independent_roots(m.get("provenance_root_ids", []))
            if m["to"] == "ADMITTED" and not m.get("licensing_witness"):
                rule, verdict, reason = "SEM_LADDER", "DENY", "ADMITTED requires a licensing witness"
            elif m["from"] == "CLAIM" and m["to"] == "ADMITTED":
                rule, verdict, reason = "SEM_LADDER", "DENY", "CLAIM→ADMITTED skips OBSERVED (opportunity laundering)"
            elif to > frm and roots < 1:
                rule, verdict, reason = "SEM_LADDER", "DENY", "promotion needs ≥1 independent root"
            elif m["to"] == "OBSERVED" and roots >= 1:
                rule, verdict, reason = "SEM_LADDER", "HOLD", "observation candidate pending review"
            elif m["to"] == "ADMITTED" and m.get("licensing_witness") and m.get("survived_discriminator"):
                rule, verdict, reason = "SEM_LADDER", "HOLD", "admission candidate → BOARD review (V0: no CANON path)"
            else:
                rule, verdict, reason = "SEM_LADDER", "HOLD", "insufficient to promote"

        # ── governance escalation: GARDEN ↛ BOARD ↛ CANON ────────────────────
        elif kind == "governance_escalation":
            frm, to = GOV_RANK.get(m["from"], 0), GOV_RANK.get(m["to"], 0)
            if to - frm >= 2:
                rule, verdict, reason = "GOV_LADDER", "DENY", f"{m['from']}→{m['to']} skips a governance rung (ancestry laundering)"
            elif m["to"] == "CANON":
                rule, verdict, reason = "GOV_LADDER", "DENY", "V0 has NO path to CANON"
            elif to > frm and not m.get("licensing_witness"):
                rule, verdict, reason = "GOV_LADDER", "DENY", "governance escalation needs a licensed receipt"
            elif to > frm:
                rule, verdict, reason = "GOV_LADDER", "HOLD", "one-rung governance escalation pending"
            else:
                rule, verdict, reason = "GOV_LADDER", "ALLOW", "no escalation"

        # ── provenance collapse (dedup by root, not by document) ─────────────
        elif kind == "provenance_collapse":
            docs = m.get("document_ids", [])
            roots = m.get("provenance_root_ids", [])
            nind = self.independent_roots(roots)
            if len(docs) > nind:
                rule, verdict, reason = "PROV_DEDUP", "ALLOW", \
                    f"{len(docs)} docs → {nind} independent root(s) (volume≠independence)"
            else:
                rule, verdict, reason = "PROV_DEDUP", "ALLOW", f"{nind} independent root(s)"

        return self._emit_receipt("MUTATION", verdict, reason, rule, m)

    # ── ANSI wall: presentation only; color=f(state), frame=f(governance) ────
    def render_wall(self, jester_receipts: list[dict] | None = None) -> str:
        out = []
        top = f"{B}\033[38;2;120;220;255m"
        out.append(top + "╔" + "═" * 62 + "╗")
        out.append(top + "║  🌈 NEPTION GOVERNED GRAPH V0 — candidate space" + " " * 14 + "║")
        out.append(top + "╚" + "═" * 62 + "╝" + R)
        # nodes grouped by governance frame (frame ⊥ color)
        by_gov: dict[str, list[Node]] = {}
        for n in self.nodes.values():
            by_gov.setdefault(n.governance_context, []).append(n)
        for gov, ns in sorted(by_gov.items(), key=lambda kv: GOV_RANK.get(kv[0], 0)):
            head, tail, fill = GOV_FRAME.get(gov, ("┌ ", "└", "─"))
            out.append(f"{D}{head}{fill * (40 - len(head))}{R}")
            for n in ns:
                c = color(n.semantic_state)
                out.append(f"{D}│{R} {c}●{R} {c}{n.semantic_state:<11}{R} "
                           f"{D}{n.entity_type:<12}{R} {n.label}")
            out.append(f"{D}{tail}{fill * 39}{R}")
        # edges
        out.append(f"{D}── edges (color=semantic_state) ──{R}")
        for e in self.edges.values():
            c = color(e.semantic_state)
            roots = self.independent_roots(e.provenance_root_ids)
            out.append(f"  {c}{e.relation_type:<12}{R} {e.source_node} → {e.target_node}  "
                       f"{c}[{e.semantic_state}]{R} {D}roots={roots} ΔA={e.authority_delta}{R}")
        # jester denials
        if jester_receipts:
            out.append(f"{color('JESTER')}── 🃏 counterfeit attacks → 🛡 DENY + ⚪ RECEIPT ──{R}")
            for rec in jester_receipts:
                c = color("DENY") if rec["verdict"] == "DENY" else color(rec["verdict"] if rec["verdict"] in SEM_COLOR else "HOLD")
                out.append(f"  {c}{rec['verdict']:<5}{R} {D}{rec['rule']:<18}{R} "
                           f"{rec['reason'][:52]}  {D}ρ={rec['hash'][:8]}{R}")
        out.append(f"{color('AUTH0')}👑 AUTHORITY_DELTA = 0{R}   "
                   f"{D}receipts={len(self.receipts)} · P↛T · not canon{R}")
        return "\n".join(out)


def load_sample(path: str) -> Graph:
    data = json.load(open(path))
    g = Graph()
    for n in data.get("nodes", []):
        g.add_node(Node(**n))
    for e in data.get("edges", []):
        g.add_edge(Edge(**e))
    return g


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sample = Path(__file__).parent / "neption_graph_sample_v0.json"
    g = load_sample(str(sample))
    # replay the five JESTER attacks (each must DENY)
    attacks = [
        {"kind": "relation_escalation", "edge_id": "E_att1", "from": "MENTION",
         "to": "PARTNERSHIP", "provenance_root_ids": ["src_meeting_0805"],
         "note": "relationship inflation"},
        {"kind": "provenance_collapse", "edge_id": "E_att2",
         "document_ids": ["docA", "docB", "docC"],
         "provenance_root_ids": ["press_release_1", "press_release_1", "press_release_1"],
         "note": "3 docs → 1 root"},
        {"kind": "semantic_promote", "edge_id": "E_att3", "from": "CLAIM",
         "to": "ADMITTED", "provenance_root_ids": ["src_meeting_0805"],
         "note": "opportunity laundering"},
        {"kind": "semantic_promote", "edge_id": "E_att4", "from": "POSSIBILITY",
         "to": "ADMITTED", "created_from": "ansi", "note": "presentation smuggling"},
        {"kind": "governance_escalation", "edge_id": "E_att5", "from": "GARDEN",
         "to": "CANON", "note": "ancestry laundering"},
    ]
    recs = [g.propose_mutation(a) for a in attacks]
    print(g.render_wall(jester_receipts=recs))

"""HELEN_GRAPH_IR — global admissibility. 🔵 OBSERVED · authority=false.

The Epoch-09 law, made mechanical:

    ∀e ∈ E, LocalValid(e) ⊬ GlobalValid(G)

Every edge can pass its LOCAL check (endpoints resolve, syntax well-formed) while
the GRAPH is globally inadmissible. Four structural pathologies a per-edge validator
cannot see:

  1. linear capability double-spend   — one one-shot token consumed by two edges
  2. provenance cycle                 — a warrant that (transitively) justifies itself
  3. provenance self-support          — a derivation-supported claim that reaches no primary root
  4. unwarranted temporal persistence — State(t₁) ⊬ State(t₂) without W_persistence
  5. mutually inconsistent effects    — one slot committed to two different values
  6. warrant/value rebinding          — one signature reused to attest two different values (FABLE swarm find)
  7. unrevoked capability (banishment) — a privileged context opened but never provably torn down

I₇ is the dual of the others: they block UP-inflation (opening/accumulating without a
witnessed root); banishment blocks FAIL-TO-CLOSE. A system is governed not merely when it
can open a privileged context, but when it can prove the context ended cleanly — "banishment
> invocation." Grant(lease) with no matching Revoke(lease) ⇒ E_UNREVOKED_CAPABILITY.

I₃ (self-support) is distinct from I₂ (cycle): a claim can be perfectly ACYCLIC yet
rootless — an orphan chain c₁→c₂ where nothing descends from a primary root. Roots(c)=∅
∧ DerivationSupport(c)≠∅ ⇒ FAIL_PROVENANCE_SELF_SUPPORT.

Non-vacuity: `global_validate` must ALSO return True for a genuinely valid graph
(see the positive control in the tests). A validator that always rejects is not a
validator — it is a constant, and it would pass every negative fixture for free.

Determinism: pure structure, no wall clock.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto


class EdgeType(Enum):
    DATA = auto()          # provenance-bearing (checked for cycles)
    DERIVATION = auto()    # provenance-bearing (checked for cycles)
    CAPABILITY = auto()    # linear consumption of a one-shot token
    PERSISTENCE = auto()   # a claim that state at src survives to dst
    EFFECT = auto()        # commits a (slot, value) mutation at dst


@dataclass(frozen=True)
class Node:
    id: str
    label: str = ""
    t: int = 0                       # timestamp (for persistence ordering)
    mutates: tuple = ()              # (slot, value) if this node commits an effect; () otherwise
    root: bool = False               # a primary provenance root (empirical witness / admissible source)


@dataclass(frozen=True)
class Edge:
    id: str
    src: str
    dst: str
    kind: EdgeType
    warrants: tuple = ()             # declared warrant ids (presence only — local)
    consumes: tuple = ()             # linear capability tokens this edge consumes
    warrant_binds: tuple = ()        # (warrant_id, value) pairs this edge attests — a signature is bound to a value
    grants: tuple = ()               # capability-lease ids this edge OPENS (a privileged context)
    revokes: tuple = ()              # capability-lease ids this edge CLOSES (teardown / banishment)


def local_valid(edge: Edge, nodes: dict) -> bool:
    """LOCAL check only: endpoints resolve. Deliberately blind to the whole graph —
    that blindness is the point the falsifiers exploit."""
    return edge.src in nodes and edge.dst in nodes


@dataclass
class GraphIR:
    nodes: dict = field(default_factory=dict)
    edges: list = field(default_factory=list)

    def add_node(self, n: Node) -> "GraphIR":
        self.nodes[n.id] = n
        return self

    def add_edge(self, e: Edge) -> "GraphIR":
        self.edges.append(e)
        return self

    def all_edges_local_valid(self) -> bool:
        return all(local_valid(e, self.nodes) for e in self.edges)

    def global_validate(self) -> tuple[bool, list[str]]:
        """GLOBAL admissibility. Returns (ok, violations). ok=True ONLY when no
        pathology is found — including on a valid graph (non-vacuity)."""
        v: list[str] = []

        # 1 — linear capability double-spend
        seen: dict[str, str] = {}
        for e in self.edges:
            if e.kind is EdgeType.CAPABILITY:
                for tok in e.consumes:
                    if tok in seen:
                        v.append(f"E_DOUBLE_SPEND: token {tok!r} consumed by {e.id} and {seen[tok]}")
                    else:
                        seen[tok] = e.id

        # 2 — provenance cycle over DATA/DERIVATION edges (grey/black DFS)
        adj: dict[str, list[str]] = {n: [] for n in self.nodes}
        for e in self.edges:
            if e.kind in (EdgeType.DATA, EdgeType.DERIVATION) and e.src in adj:
                adj[e.src].append(e.dst)
        WHITE, GREY, BLACK = 0, 1, 2
        color = {n: WHITE for n in self.nodes}

        def has_cycle(u: str) -> str | None:
            color[u] = GREY
            for w in adj.get(u, ()):
                if color.get(w) == GREY:
                    return f"{u}->{w}"
                if color.get(w) == WHITE:
                    hit = has_cycle(w)
                    if hit:
                        return hit
            color[u] = BLACK
            return None

        for n in self.nodes:
            if color[n] == WHITE:
                hit = has_cycle(n)
                if hit:
                    v.append(f"E_PROVENANCE_CYCLE: back-edge {hit}")
                    break

        # 3 — provenance self-support: a derivation-supported claim must reach a primary root.
        #     Distinct from the cycle check: catches ACYCLIC-yet-rootless orphans too.
        prov_parents: dict[str, list[str]] = {n: [] for n in self.nodes}
        supported: set[str] = set()
        for e in self.edges:
            if e.kind in (EdgeType.DATA, EdgeType.DERIVATION) and e.src in self.nodes and e.dst in self.nodes:
                prov_parents[e.dst].append(e.src)
                supported.add(e.dst)

        def reaches_root(start: str) -> bool:
            seen: set[str] = set()
            stack = [start]
            while stack:
                u = stack.pop()
                if u in seen:
                    continue
                seen.add(u)
                if self.nodes[u].root:
                    return True
                stack.extend(prov_parents.get(u, ()))
            return False

        for n in sorted(supported):
            if not reaches_root(n):
                v.append(f"E_PROVENANCE_SELF_SUPPORT: claim {n!r} has derivation support but reaches no primary root")

        # 4 — unwarranted temporal persistence
        for e in self.edges:
            if e.kind is EdgeType.PERSISTENCE and e.src in self.nodes and e.dst in self.nodes:
                if self.nodes[e.dst].t > self.nodes[e.src].t and not e.warrants:
                    v.append(
                        f"E_UNWARRANTED_PERSISTENCE: {e.id} spans "
                        f"t={self.nodes[e.src].t}->t={self.nodes[e.dst].t} with no W_persistence"
                    )

        # 4 — mutually inconsistent concurrent effects
        committed: dict[str, str] = {}
        for e in self.edges:
            if e.kind is EdgeType.EFFECT and e.dst in self.nodes:
                m = self.nodes[e.dst].mutates
                if m:
                    slot, val = m
                    if slot in committed and committed[slot] != val:
                        v.append(f"E_INCONSISTENT_EFFECT: slot {slot!r} = {committed[slot]!r} vs {val!r}")
                    else:
                        committed[slot] = val

        # 6 — warrant/value rebinding: a signature attests at most ONE value. I₁–I₅ are blind to
        #     signature↔value integrity (a token is spent once, graph acyclic, roots ground out,
        #     transport warranted) yet a warrant issued for value X can be reused to bless value Y.
        #     Found by the FABLE Gemma4 swarm (CHID-SMITH-1793): proposed → witnessed → closed here.
        wbind: dict[str, set] = {}
        for e in self.edges:
            for wid, val in e.warrant_binds:
                wbind.setdefault(wid, set()).add(val)
        for wid, vals in sorted(wbind.items()):
            if len(vals) > 1:
                v.append(f"E_WARRANT_VALUE_REBIND: warrant {wid!r} attests {len(vals)} distinct values {sorted(vals)!r}")

        # 7 — banishment: every opened capability lease must be provably revoked before context-end.
        #     Governed = provably closed, not just opened. A grant with no matching teardown is a
        #     dangling privileged context (E_UNREVOKED_CAPABILITY). Dual of I₁–I₆: they block
        #     up-inflation; this blocks fail-to-close.
        opened, closed = set(), set()
        for e in self.edges:
            opened.update(e.grants)
            closed.update(e.revokes)
        for lease in sorted(opened - closed):
            v.append(f"E_UNREVOKED_CAPABILITY: lease {lease!r} granted but never revoked (dangling privileged context)")

        return (len(v) == 0), v

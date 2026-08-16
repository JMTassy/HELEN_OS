#!/usr/bin/env python3
"""
CAUSAL_RECEIPT_V0 — reference implementation of the operator ruling
"causal-edge decision: (b) causal parents" (2026-08-16).

A receipt's hash binds to its CAUSAL PARENTS, not to a sequence predecessor:

    h(r) = sha256( canon(op) || sorted(parent_hashes) )

Consequences (matching T3/L4' in the Lean calculus):
  - the DAG is the constitutional object; any linear file is ONE serialization
  - acyclicity is by construction (a receipt can only reference existing hashes)
  - replay confluence across linear extensions is a TESTABLE property of the
    real ledger, not vacuous bookkeeping
  - a commitment over one serialization (old H-chain) remains possible as
    bookkeeping but carries no semantic weight once confluence holds

STATUS: NON_SOVEREIGN reference. The production ledger
(town/ledger_v1.ndjson, tools/ndjson_writer.py, helen_os/schemas/**) is
firewalled; adopting this format there requires MAYOR routing through the
admissible bridge. Nothing here writes any sovereign path.
authority=false · canon=false · ledger_effect=none.
"""
from __future__ import annotations
import hashlib, json, random


def canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


class CausalLedger:
    """Append-only DAG of receipts; hashes bind to causal parents."""

    def __init__(self):
        self.receipts: dict[str, dict] = {}   # h -> {op, parents, h}

    def append(self, op: dict, parents: list[str]) -> str:
        for p in parents:
            if p not in self.receipts:
                raise ValueError(f"unknown causal parent {p}")
        h = hashlib.sha256(canon(op) + canon(sorted(parents))).hexdigest()[:16]
        if h in self.receipts:
            raise ValueError("duplicate receipt")
        self.receipts[h] = {"op": op, "parents": sorted(parents), "h": h}
        return h

    def verify(self) -> bool:
        """Recompute every hash; parents must exist. Acyclic by construction."""
        for h, r in self.receipts.items():
            expect = hashlib.sha256(
                canon(r["op"]) + canon(sorted(r["parents"]))).hexdigest()[:16]
            if expect != h:
                return False
            if any(p not in self.receipts for p in r["parents"]):
                return False
        return True

    def incomparable_pairs(self) -> list[tuple[str, str]]:
        """Pairs with no ancestry path either way — the declared antichains."""
        anc: dict[str, set] = {}
        def ancestors(h):
            if h not in anc:
                s = set()
                for p in self.receipts[h]["parents"]:
                    s.add(p); s |= ancestors(p)
                anc[h] = s
            return anc[h]
        hs = list(self.receipts)
        return [(a, b) for i, a in enumerate(hs) for b in hs[i + 1:]
                if a not in ancestors(b) and b not in ancestors(a)]

    def linearizations(self, n: int, seed: int) -> list[list[str]]:
        """Seeded random topological sorts (Kahn with shuffled frontier)."""
        rng = random.Random(seed)
        out = []
        for _ in range(n):
            indeg = {h: len(r["parents"]) for h, r in self.receipts.items()}
            children: dict[str, list[str]] = {h: [] for h in self.receipts}
            for h, r in self.receipts.items():
                for p in r["parents"]:
                    children[p].append(h)
            frontier = sorted(h for h, d in indeg.items() if d == 0)
            order = []
            while frontier:
                rng.shuffle(frontier)
                h = frontier.pop()
                order.append(h)
                for c in children[h]:
                    indeg[c] -= 1
                    if indeg[c] == 0:
                        frontier.append(c)
            assert len(order) == len(self.receipts)
            out.append(order)
        return out

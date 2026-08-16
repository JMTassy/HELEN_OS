#!/usr/bin/env python3
"""
CAUSAL_RECEIPT_V1 — witness-grade reference of the causal-parents ruling.

Hash equation (as prescribed — never commits to storage order):

    h_C(r) = SHA256( nu || canon(body(r)) || canon(sort{h_C(p) : p in Parents(r)}) )

Three identities, deliberately distinct:
    H_bytes    — are these exact exported bytes identical?
    H_causal   — is this the same causal event structure?
    H_semantic — does replay reconstruct the same governed state?

T3 (Lean, 478be0e) speaks to the third under its independence hypotheses.
This module is an implementation CLAIMING to instantiate those hypotheses;
the witness suite (causal_receipt_witness.py) is the evidence layer:
    Proof(T3) + Evidence(CR1 |= T3 assumptions)   — never "T3 proved CR1".

NON_SOVEREIGN. The production ledger and its writers remain firewalled;
adoption is a MAYOR decision. authority=false · ledger_effect=none.
"""
from __future__ import annotations
import hashlib, json


def canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


class CausalLedgerV1:
    def __init__(self, nu: str):
        self.nu = nu
        self.receipts: dict[str, dict] = {}   # h -> {body, parents(sorted), h}

    # ── hashing ──
    def _hash(self, body: dict, parents: list[str]) -> str:
        return hashlib.sha256(
            self.nu.encode() + canon(body) + canon(sorted(parents))).hexdigest()

    # ── append path: C1 parent existence, C2 acyclic by construction ──
    def append(self, body: dict, parents: list[str]) -> str:
        for p in parents:
            if p not in self.receipts:
                raise ValueError(f"E_PARENT_UNKNOWN:{p[:12]}")
        h = self._hash(body, parents)
        if h in self.receipts:
            raise ValueError("E_DUPLICATE_RECEIPT")
        self.receipts[h] = {"body": body, "parents": sorted(parents), "h": h}
        return h

    def verify(self) -> tuple[bool, str]:
        for h, r in self.receipts.items():
            if self._hash(r["body"], r["parents"]) != h:
                return False, f"E_HASH_MISMATCH:{h[:12]}"
            for p in r["parents"]:
                if p not in self.receipts:
                    return False, f"E_PARENT_UNKNOWN:{p[:12]}"
        return True, "OK"

    # ── identities ──
    @staticmethod
    def h_bytes(exported: bytes) -> str:
        return hashlib.sha256(exported).hexdigest()

    def h_causal(self) -> str:
        return hashlib.sha256(canon(sorted(self.receipts))).hexdigest()

    # ── export / import (C8) ──
    def export(self, order: list[str] | None = None) -> bytes:
        hs = order if order is not None else list(self.receipts)
        assert sorted(hs) == sorted(self.receipts), "export must cover the DAG"
        return b"\n".join(canon(self.receipts[h]) for h in hs) + b"\n"

    @classmethod
    def import_(cls, nu: str, data: bytes) -> "CausalLedgerV1":
        rows = [json.loads(line) for line in data.splitlines() if line.strip()]
        led = cls(nu)
        pending = list(rows)
        while pending:
            progressed = False
            for row in list(pending):
                if all(p in led.receipts for p in row["parents"]):
                    h = led.append(row["body"], row["parents"])
                    if h != row["h"]:
                        raise ValueError(f"E_HASH_MISMATCH_ON_IMPORT:{row['h'][:12]}")
                    pending.remove(row)
                    progressed = True
            if not progressed:
                # unresolvable parents ⇒ missing receipt or cycle claim
                raise ValueError("E_UNRESOLVABLE_PARENTS_CYCLE_OR_MISSING")
        return led

    # ── DAG utilities (shared with the antichain harness) ──
    def linearizations(self, n: int, seed: int) -> list[list[str]]:
        import random
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

    # ── migration (C9) / rollback (C10) ──
    @classmethod
    def migrate_from_linear(cls, nu: str, legacy_ops: list[dict]) -> "CausalLedgerV1":
        """Legacy linear order is treated as a causal CHAIN (fail-closed: no
        antichain is invented where independence was never declared). Each
        migrated body carries explicit provenance."""
        led = cls(nu)
        prev = None
        for i, op in enumerate(legacy_ops):
            body = {"op": op, "migration": {"source": "linear_v0", "seq": i}}
            prev = led.append(body, [prev] if prev else [])
        return led

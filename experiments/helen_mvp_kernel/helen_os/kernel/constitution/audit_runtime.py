r"""Audit Runtime — Phase A item 4, the append-only audit store as
enforcing code.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.
STATUS: REFERENCE_IMPLEMENTATION — executable semantics of the
Append-only Audit Store (the Ledger's enterprise name); the
production build replaces the store, not the laws.

WHAT THE STRUCTURE ITSELF REFUSES:
- events are HASH-CHAINED per tenant: each event carries the digest
  of its predecessor, and verify_chain() recomputes the whole chain
  — an edited event breaks every hash after it (E_CHAIN_BROKEN).
  Tampering is not forbidden by policy; it is DETECTABLE by
  arithmetic.
- append-only is an API fact: this module exports no update and no
  delete. The test suite asserts the absence of the verbs.
- an event without an actor and a kind is unattributed noise
  (E_UNATTRIBUTED_EVENT).
- raw values never enter the audit log: an event carrying a "value"
  key is refused (E_RAW_VALUE_IN_AUDIT) — values travel as digests,
  because an audit log outlives every retention policy applied to
  the data it describes.
- chains are PER TENANT (audit logs are customer-data-plane).

THE HONEST LIMIT, stated not hidden: a hash chain detects EDITS but
not TAIL TRUNCATION — cutting the last k events yields a shorter,
internally consistent chain. The remedy is the ANCHOR: anchor()
exports the current head digest for storage OUTSIDE the chain
(another tenant's chain, a commit, a printed receipt), and
verify_against_anchor() then catches truncation
(E_CHAIN_TRUNCATED). A chain that has never been anchored is
UNANCHORED, not safe — the positive-control law again.

Deterministic: no wall-clock, no randomness; sequence numbers order
events; canonical serialization.
"""
from __future__ import annotations

import hashlib
import json

GENESIS = "0" * 16


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def _sha(obj) -> str:
    return hashlib.sha256(canon(obj).encode()).hexdigest()[:16]


def boot() -> dict:
    return {"chains": {}, "seq": 0}


# ── append: the only write verb ────────────────────────────────────────

def append(state: dict, tenant: str, event: dict) -> tuple:
    """The single mutation. kind + actor mandatory; raw values
    refused; the event is chained to its predecessor's digest."""
    if "kind" not in event or "actor" not in event:
        return state, {"ok": False, "reason": "E_UNATTRIBUTED_EVENT",
                       "law": "an event without an actor and a kind "
                              "is noise, not audit"}
    if "value" in event:
        return state, {"ok": False, "reason": "E_RAW_VALUE_IN_AUDIT",
                       "law": "values travel as digests; the audit "
                              "log outlives every retention policy "
                              "applied to the data it describes"}
    chain = state["chains"].get(tenant, ())
    prev = chain[-1]["hash"] if chain else GENESIS
    seq = state["seq"] + 1
    body = {"seq": seq, "prev": prev, **event}
    sealed = {**body, "hash": _sha(body)}
    s = dict(state)
    s["seq"] = seq
    s["chains"] = {**s["chains"], tenant: chain + (sealed,)}
    return s, {"ok": True, "seq": seq, "hash": sealed["hash"],
               "tenant": tenant}


# ── verification: tampering is arithmetic, not policy ──────────────────

def verify_chain(state: dict, tenant: str) -> dict:
    """Recompute every link. An edited event breaks every hash after
    it; the first broken link is named."""
    chain = state["chains"].get(tenant, ())
    prev = GENESIS
    for ev in chain:
        body = {k: v for k, v in ev.items() if k != "hash"}
        if body.get("prev") != prev or _sha(body) != ev["hash"]:
            return {"intact": False, "reason": "E_CHAIN_BROKEN",
                    "at_seq": ev.get("seq"),
                    "law": "tampering is detectable by arithmetic, "
                           "not forbidden by policy"}
        prev = ev["hash"]
    return {"intact": True, "length": len(chain),
            "head": prev if chain else GENESIS}


def anchor(state: dict, tenant: str) -> dict:
    """Export the head digest for storage OUTSIDE the chain. The
    anchor is what turns edit-detection into truncation-detection."""
    v = verify_chain(state, tenant)
    if not v["intact"]:
        return {"anchored": False, "reason": v["reason"]}
    return {"anchored": True, "tenant": tenant,
            "head": v["head"], "length": v["length"]}


def verify_against_anchor(state: dict, tenant: str,
                          anchored: dict) -> dict:
    """A shorter, internally consistent chain is exactly what tail
    truncation produces — only the external anchor catches it."""
    v = verify_chain(state, tenant)
    if not v["intact"]:
        return {"intact": False, "reason": "E_CHAIN_BROKEN"}
    if not anchored.get("anchored"):
        return {"intact": None, "reason": "E_UNANCHORED",
                "law": "a chain that was never anchored is "
                       "unanchored, not safe — the positive-control "
                       "law for ledgers"}
    if v["length"] < anchored["length"] or \
            (v["length"] == anchored["length"] and
             v["head"] != anchored["head"]):
        return {"intact": False, "reason": "E_CHAIN_TRUNCATED",
                "expected_length": anchored["length"],
                "found_length": v["length"]}
    return {"intact": True, "grew_by": v["length"] -
                                       anchored["length"]}


def chain_receipt(state: dict, tenant: str) -> dict:
    """The RDK recipe for this store: the chain re-derives itself."""
    v = verify_chain(state, tenant)
    return {"claim": f"audit chain intact for {tenant}",
            "derivation_recipe": "recompute sha256 over every event "
                                 "body, compare stored hashes and "
                                 "prev links from GENESIS",
            "result": v,
            "rederivable": True}

r"""Context/Evidence Runtime — Phase A item 7, the Governed Context
Service (external name for what the mythology calls Memory, with
HER's relationship edges and SOPHIA's evidence grades inside).

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.
STATUS: REFERENCE_IMPLEMENTATION (in-memory, deterministic). The
production build replaces the store, not the laws.

The state laws it makes executable:

    AuthoritativeStore = the application state that is faithful
    DerivedIndex       = structure, rebuildable, never authoritative
    LLMContext         = ephemeral — assembled per call, never truth

WHAT THE DATA PATH ITSELF REFUSES:
- evidence without provenance (E_UNPROVENANCED_EVIDENCE), and model
  output registering itself as OBSERVED (E_MODEL_OUTPUT_AS_OBSERVED)
  — a model is an author, never a root
- promotion of MODEL_DERIVED to OBSERVED by any path, witnessed or
  not (E_MODEL_SELF_PROMOTION); REPORTED rises to OBSERVED only with
  a named witness (E_UNWITNESSED_PROMOTION)
- cross-tenant reads, links, and retrievals — indistinguishable from
  absent (one answer: E_UNKNOWN_EVIDENCE; existence never leaks)
- raw text in an assembled context (E_UNSOURCED_CONTEXT_ITEM):
  every context item cites a registered evidence row
- persisting an assembly as evidence (E_CONTEXT_PERSISTED_AS_TRUTH,
  refused ALWAYS — ephemerality is structural: assemble() does not
  even receive a writable state)
- serving a retrieval as authoritative when it came through the
  derived index (answers carry authoritative=False and index_lag)
- an erased row surviving in the index — erasure removes store row,
  index entry and edges, leaves a content-free tombstone, and a
  later read is byte-identical to never-existed

And two read-time laws inherited from the admissibility engine:
retrieval counts ROOTS, not items (three copies of one source report
n_roots=1 via derives_from edges), and a registered contradiction
between two returned items is flagged in the receipt — the flag
cannot be opted out of (E_CONTRADICTION_SUPPRESSED).

Style: the reducer seam — pure state machine, (state, receipt)
returns, no function mutates its input, per-tenant audit, no
wall-clock, no randomness.
"""
from __future__ import annotations

import hashlib
import json

GRADES = ("OBSERVED", "REPORTED", "MODEL_DERIVED")
ORIGINS = ("human", "system", "model")
EDGE_KINDS = ("supports", "contradicts", "derives_from")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def _sha(obj) -> str:
    return hashlib.sha256(canon(obj).encode()).hexdigest()[:16]


# ── boot ───────────────────────────────────────────────────────────────

def boot() -> dict:
    return {"tenants": {}, "seq": 0}


def _bump(state: dict) -> dict:
    s = dict(state)
    s["seq"] = state["seq"] + 1
    return s


def _audit(state: dict, tenant: str, event: dict) -> dict:
    s = dict(state)
    t = dict(s["tenants"][tenant])
    t["audit"] = t["audit"] + ({"seq": state["seq"], **event},)
    s["tenants"] = {**s["tenants"], tenant: t}
    return s


def provision_tenant(state: dict, tenant: str) -> tuple:
    """A tenant is born with an authoritative store, an empty derived
    index, edges, tombstones, and its own audit log."""
    if tenant in state["tenants"]:
        return state, {"ok": False, "reason": "E_TENANT_EXISTS"}
    s = _bump(state)
    s["tenants"] = {**s["tenants"],
                    tenant: {"store": {}, "index": {},
                             "index_anchor": 0, "edges": (),
                             "tombstones": (), "audit": ()}}
    s = _audit(s, tenant, {"kind": "TENANT_PROVISIONED"})
    return s, {"ok": True, "tenant": tenant}


def _t(state: dict, tenant: str) -> dict | None:
    return state["tenants"].get(tenant)


# ── evidence admission ─────────────────────────────────────────────────

def register_evidence(state, tenant, ev_id, digest, provenance,
                      grade, origin) -> tuple:
    """Evidence enters the authoritative store only fully typed:
    digest, provenance, grade, origin. A model's own output may enter
    — as MODEL_DERIVED — but never wearing OBSERVED: authorship is
    not witnesshood."""
    t = _t(state, tenant)
    if t is None:
        return state, {"ok": False, "reason": "E_UNKNOWN_TENANT"}
    if ev_id in t["store"]:
        return state, {"ok": False, "reason": "E_EVIDENCE_EXISTS"}
    if grade not in GRADES:
        return state, {"ok": False, "reason": "E_UNKNOWN_GRADE"}
    if origin not in ORIGINS:
        return state, {"ok": False, "reason": "E_UNKNOWN_ORIGIN"}
    if not provenance or not digest:
        return state, {"ok": False,
                       "reason": "E_UNPROVENANCED_EVIDENCE"}
    if origin == "model" and grade == "OBSERVED":
        return state, {"ok": False,
                       "reason": "E_MODEL_OUTPUT_AS_OBSERVED",
                       "law": "a model is an author, never a root"}
    s = _bump(state)
    row = {"digest": digest, "provenance": provenance,
           "grade": grade, "origin": origin, "seq": s["seq"]}
    tt = dict(s["tenants"][tenant])
    tt["store"] = {**tt["store"], ev_id: row}
    s["tenants"] = {**s["tenants"], tenant: tt}
    s = _audit(s, tenant, {"kind": "EVIDENCE_REGISTERED",
                           "ev": ev_id, "grade": grade,
                           "origin": origin})
    return s, {"ok": True, "ev": ev_id, "grade": grade}


def promote_evidence(state, tenant, ev_id, new_grade, witness) -> tuple:
    """REPORTED may rise to OBSERVED with a named witness.
    MODEL_DERIVED may never rise to OBSERVED — by any witness, ever:
    the derivation support is still the model."""
    t = _t(state, tenant)
    if t is None or ev_id not in t["store"]:
        return state, {"ok": False, "reason": "E_UNKNOWN_EVIDENCE"}
    row = t["store"][ev_id]
    if new_grade not in GRADES:
        return state, {"ok": False, "reason": "E_UNKNOWN_GRADE"}
    if row["grade"] == "MODEL_DERIVED" and new_grade == "OBSERVED":
        return state, {"ok": False,
                       "reason": "E_MODEL_SELF_PROMOTION"}
    if new_grade == "OBSERVED" and not witness:
        return state, {"ok": False,
                       "reason": "E_UNWITNESSED_PROMOTION"}
    s = _bump(state)
    tt = dict(s["tenants"][tenant])
    tt["store"] = {**tt["store"],
                   ev_id: {**row, "grade": new_grade,
                           "witness": witness}}
    s["tenants"] = {**s["tenants"], tenant: tt}
    s = _audit(s, tenant, {"kind": "EVIDENCE_PROMOTED", "ev": ev_id,
                           "to": new_grade, "witness": witness})
    return s, {"ok": True, "ev": ev_id, "grade": new_grade}


# ── relationship edges (HER) ───────────────────────────────────────────

def link(state, tenant, src, dst, kind) -> tuple:
    """Typed edges between evidence rows of ONE tenant. A cross-tenant
    endpoint answers exactly like an absent one — existence must not
    leak through the relationship layer either."""
    t = _t(state, tenant)
    if t is None:
        return state, {"ok": False, "reason": "E_UNKNOWN_TENANT"}
    if kind not in EDGE_KINDS:
        return state, {"ok": False, "reason": "E_UNKNOWN_EDGE_KIND"}
    if src not in t["store"] or dst not in t["store"]:
        return state, {"ok": False, "reason": "E_UNKNOWN_EVIDENCE"}
    if src == dst:
        return state, {"ok": False, "reason": "E_SELF_EDGE"}
    s = _bump(state)
    tt = dict(s["tenants"][tenant])
    tt["edges"] = tt["edges"] + ((src, dst, kind),)
    s["tenants"] = {**s["tenants"], tenant: tt}
    s = _audit(s, tenant, {"kind": "EDGE_LINKED", "src": src,
                           "dst": dst, "edge": kind})
    return s, {"ok": True}


def _root_of(t: dict, ev_id: str) -> str:
    """Follow derives_from edges to the family root (acyclic by
    registration order in practice; a cycle collapses to the smallest
    id to stay deterministic)."""
    parents = {s: d for (s, d, k) in t["edges"] if k == "derives_from"}
    seen, cur = set(), ev_id
    while cur in parents and cur not in seen:
        seen.add(cur)
        cur = parents[cur]
    return cur


# ── the derived index ──────────────────────────────────────────────────

def rebuild_index(state, tenant) -> tuple:
    """The index is DERIVED: rebuilt deterministically from the
    authoritative store, anchored to the store sequence it saw. It
    adds no rows, keeps no erased ones, and asserts nothing the store
    does not."""
    t = _t(state, tenant)
    if t is None:
        return state, {"ok": False, "reason": "E_UNKNOWN_TENANT"}
    s = _bump(state)
    tt = dict(s["tenants"][tenant])
    tt["index"] = {ev: {"digest": row["digest"],
                        "grade": row["grade"]}
                   for ev, row in t["store"].items()}
    tt["index_anchor"] = s["seq"]
    s["tenants"] = {**s["tenants"], tenant: tt}
    s = _audit(s, tenant, {"kind": "INDEX_REBUILT",
                           "entries": len(tt["index"]),
                           "anchor": tt["index_anchor"]})
    return s, {"ok": True, "entries": len(tt["index"])}


def retrieve(state, tenant, ev_ids) -> dict:
    """Read through the derived index. The answer is never
    authoritative; it carries index_lag, counts ROOTS not items, and
    flags every registered contradiction among the returned rows.
    Cross-tenant and absent are one indistinguishable answer."""
    t = _t(state, tenant)
    if t is None:
        return {"ok": False, "reason": "E_UNKNOWN_TENANT"}
    missing = tuple(sorted(e for e in ev_ids if e not in t["index"]))
    if missing:
        return {"ok": False, "reason": "E_UNKNOWN_EVIDENCE",
                "missing": missing}
    items = {e: t["index"][e] for e in ev_ids}
    roots = {_root_of(t, e) for e in ev_ids}
    flagged = tuple(sorted(
        (a, b) for (a, b, k) in t["edges"] if k == "contradicts"
        and a in items and b in items))
    return {"ok": True, "items": items,
            "n_items": len(items), "n_roots": len(roots),
            "contradictions": flagged,
            "authoritative": False,
            "index_lag": state["seq"] - t["index_anchor"]}


def authoritative_read(state, tenant, ev_id) -> dict:
    """The store is the only faithful read. Same one-answer law."""
    t = _t(state, tenant)
    if t is None or ev_id not in t["store"]:
        return {"ok": False, "reason": "E_UNKNOWN_EVIDENCE"}
    return {"ok": True, "row": t["store"][ev_id],
            "authoritative": True}


# ── ephemeral context assembly ─────────────────────────────────────────

def assemble_context(state, tenant, ev_ids, budget_items,
                     suppress_contradictions=False) -> dict:
    """Build a per-call context. Structurally ephemeral: this
    function returns a receipt and CANNOT write state. Every item
    cites a registered row; raw strings refuse; the contradiction
    flag is not optional."""
    if suppress_contradictions:
        return {"ok": False, "reason": "E_CONTRADICTION_SUPPRESSED",
                "law": "read-time consistency is not a caller option"}
    if any(not isinstance(e, str) or " " in e for e in ev_ids):
        return {"ok": False, "reason": "E_UNSOURCED_CONTEXT_ITEM"}
    t = _t(state, tenant)
    if t is None:
        return {"ok": False, "reason": "E_UNKNOWN_TENANT"}
    unknown = tuple(sorted(e for e in ev_ids if e not in t["store"]))
    if unknown:
        return {"ok": False, "reason": "E_UNKNOWN_EVIDENCE",
                "missing": unknown}
    if len(ev_ids) > budget_items:
        return {"ok": False, "reason": "E_CONTEXT_BUDGET",
                "budget": budget_items, "requested": len(ev_ids)}
    r = retrieve(state, tenant, tuple(ev_ids)) if \
        all(e in t["index"] for e in ev_ids) else None
    citations = tuple(sorted(ev_ids))
    return {"ok": True,
            "assembly_digest": _sha(("ctx", tenant, citations)),
            "citations": citations,
            "n_roots": len({_root_of(t, e) for e in ev_ids}),
            "contradictions": tuple(sorted(
                (a, b) for (a, b, k) in t["edges"]
                if k == "contradicts" and a in ev_ids and b in ev_ids)),
            "grades": {e: t["store"][e]["grade"] for e in ev_ids},
            "ephemeral": True, "persisted": False,
            "response_grade": "REPRESENTATION",
            "index_consulted": r is not None}


def persist_assembly(state, tenant, assembly) -> tuple:
    """Refused ALWAYS. An assembly is a view; writing it back as
    evidence would let the context service mint its own roots."""
    return state, {"ok": False,
                   "reason": "E_CONTEXT_PERSISTED_AS_TRUTH",
                   "persisted": False,
                   "law": "LLMContext is ephemeral; truth enters "
                          "through register_evidence with provenance"}


# ── erasure ────────────────────────────────────────────────────────────

def erase_evidence(state, tenant, ev_id) -> tuple:
    """Erasure is total across store, index and edges, and leaves a
    content-free tombstone in the audit trail: the FACT of erasure is
    auditable, the content is gone, and a later read is
    indistinguishable from never-existed."""
    t = _t(state, tenant)
    if t is None or ev_id not in t["store"]:
        return state, {"ok": False, "reason": "E_UNKNOWN_EVIDENCE"}
    s = _bump(state)
    tt = dict(s["tenants"][tenant])
    tt["store"] = {k: v for k, v in tt["store"].items() if k != ev_id}
    tt["index"] = {k: v for k, v in tt["index"].items() if k != ev_id}
    tt["edges"] = tuple((a, b, k) for (a, b, k) in tt["edges"]
                        if ev_id not in (a, b))
    tt["tombstones"] = tt["tombstones"] + (_sha(("tomb", ev_id)),)
    s["tenants"] = {**s["tenants"], tenant: tt}
    s = _audit(s, tenant, {"kind": "EVIDENCE_ERASED",
                           "tombstone": _sha(("tomb", ev_id))})
    return s, {"ok": True, "tombstone": _sha(("tomb", ev_id))}


# ── the invariant, re-derivable on real state ──────────────────────────

def context_invariant(state) -> dict:
    """No index entry without a live store row (no ghosts, no
    survivors of erasure); no edge endpoint outside the store; index
    anchor never ahead of the world; tombstones carry no content."""
    orphans, bad_edges, future = [], [], []
    for tenant, t in state["tenants"].items():
        for ev in t["index"]:
            if ev not in t["store"]:
                orphans.append(f"{ev}@{tenant}")
        for (a, b, k) in t["edges"]:
            if a not in t["store"] or b not in t["store"]:
                bad_edges.append(f"{a}->{b}@{tenant}")
        if t["index_anchor"] > state["seq"]:
            future.append(tenant)
    content_free = all(isinstance(x, str) and len(x) == 16
                       for tn in state["tenants"].values()
                       for x in tn["tombstones"])
    holds = not orphans and not bad_edges and not future \
        and content_free
    return {"holds": holds, "orphan_index_entries": tuple(orphans),
            "dangling_edges": tuple(bad_edges),
            "future_anchors": tuple(future),
            "tombstones_content_free": content_free}

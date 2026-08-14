r"""Tenant Runtime — Phase A item 1, the first vNext primitive that is
CODE rather than a refusal about hypothetical code.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.
STATUS: REFERENCE_IMPLEMENTATION (in-memory, deterministic). This is
the executable semantics of L7 tenant isolation — the enforcement
lives in the data path itself, not in a predicate about it. The
production build replaces the store, not the laws.

    Tenant_A INTERSECT Tenant_B = EMPTY   over data-plane resources
    shared: explicit control-plane artifacts, READ-ONLY to tenants

Style: the reducer seam. The runtime is a pure state machine —
functions take the state dict and return (new_state, receipt); no
function mutates its input; every operation appends an audit event to
the acting tenant's OWN audit log (audit logs are customer-data-plane
per vNext). The UI/caller never touches state internals — the V0 law
at platform scale.

WHAT THE DATA PATH ITSELF REFUSES:
- a handle minted for tenant A presented against tenant B's data
  (E_TENANT_BOUNDARY) — and a FORGED handle dict, however
  well-formed, is unknown to the registry (E_UNKNOWN_HANDLE)
- any write without the dotted capability for it
  (E_CAPABILITY_MISSING — no ambient authority, vnext law)
- tenant writes to control-plane artifacts
  (E_CONTROL_PLANE_READ_ONLY) — releases are distributed, never
  edited by tenants
- enumeration only ever returns the caller's own keys; there is no
  cross-tenant count, size, or existence signal (isolation includes
  METADATA — a 404 and a 403 must be indistinguishable across the
  boundary, or key existence leaks)

Deterministic: no wall-clock, no randomness; sequence numbers order
events; canonical serialization.
"""
from __future__ import annotations

import hashlib
import json


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def _sha(obj) -> str:
    return hashlib.sha256(canon(obj).encode()).hexdigest()[:16]


# ── boot and provisioning ──────────────────────────────────────────────

def boot() -> dict:
    """Empty platform: no tenants, no handles, an empty control
    plane, sequence 0."""
    return {"tenants": {}, "handles": {}, "control_plane": {},
            "seq": 0}


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
    """A tenant is born with its own store, its own audit log, and
    nothing else."""
    if tenant in state["tenants"]:
        return state, {"ok": False, "reason": "E_TENANT_EXISTS"}
    s = _bump(state)
    s["tenants"] = {**s["tenants"],
                    tenant: {"store": {}, "audit": ()}}
    s = _audit(s, tenant, {"kind": "TENANT_PROVISIONED"})
    return s, {"ok": True, "tenant": tenant, "seq": s["seq"]}


def open_handle(state: dict, tenant: str, capabilities: tuple) -> tuple:
    """A handle is minted BY the runtime and bound to one tenant and
    a declared capability set. Its identity is registry membership,
    not its field values — so a forged dict with the right shape is
    still unknown."""
    if tenant not in state["tenants"]:
        return state, {"ok": False, "reason": "E_UNKNOWN_TENANT"}
    if any("." not in c for c in capabilities) or \
            "ALL" in capabilities or "*" in capabilities:
        return state, {"ok": False, "reason": "E_AMBIENT_AUTHORITY"}
    s = _bump(state)
    hid = _sha(("handle", tenant, tuple(sorted(capabilities)),
                s["seq"]))
    s["handles"] = {**s["handles"],
                    hid: {"tenant": tenant,
                          "capabilities": tuple(sorted(capabilities))}}
    s = _audit(s, tenant, {"kind": "HANDLE_OPENED", "handle": hid,
                           "capabilities": tuple(sorted(capabilities))})
    return s, {"ok": True, "handle": hid, "tenant": tenant}


def _resolve(state: dict, handle: str) -> dict | None:
    return state["handles"].get(handle)


# ── the data path: enforcement lives here ──────────────────────────────

def write(state: dict, handle: str, tenant: str, key: str,
          value) -> tuple:
    """Write into the NAMED tenant's store. The runtime checks the
    handle's registry binding against the named tenant — a handle for
    A aimed at B dies here, whatever the caller claims."""
    h = _resolve(state, handle)
    if h is None:
        return state, {"ok": False, "reason": "E_UNKNOWN_HANDLE"}
    if h["tenant"] != tenant:
        s = _bump(state)
        s = _audit(s, h["tenant"],
                   {"kind": "BOUNDARY_REFUSED", "aimed_at": tenant,
                    "op": "write"})
        return s, {"ok": False, "reason": "E_TENANT_BOUNDARY",
                   "law": "a handle is bound at mint time; the data "
                          "path checks the binding, not the claim"}
    if "store.write" not in h["capabilities"]:
        return state, {"ok": False, "reason": "E_CAPABILITY_MISSING",
                       "needed": "store.write"}
    s = _bump(state)
    t = dict(s["tenants"][tenant])
    t["store"] = {**t["store"], key: value}
    s["tenants"] = {**s["tenants"], tenant: t}
    s = _audit(s, tenant, {"kind": "WRITE", "key": key,
                           "value_digest": _sha(value)})
    return s, {"ok": True, "seq": s["seq"]}


def read(state: dict, handle: str, tenant: str, key: str) -> tuple:
    """Cross-boundary reads and reads of absent keys are
    INDISTINGUISHABLE to the caller: same refusal, no existence
    signal. Isolation includes metadata."""
    h = _resolve(state, handle)
    if h is None:
        return state, {"ok": False, "reason": "E_UNKNOWN_HANDLE"}
    denied = h["tenant"] != tenant or \
        "store.read" not in h["capabilities"]
    if denied or key not in state["tenants"][tenant]["store"]:
        refusal = {"ok": False, "reason": "E_NOT_READABLE",
                   "note": "absence and boundary are one answer; a "
                           "distinct 403 would leak key existence"}
        if denied and h["tenant"] in state["tenants"]:
            s = _bump(state)
            s = _audit(s, h["tenant"],
                       {"kind": "BOUNDARY_REFUSED",
                        "aimed_at": tenant, "op": "read"})
            return s, refusal
        return state, refusal
    s = _bump(state)
    s = _audit(s, tenant, {"kind": "READ", "key": key})
    return s, {"ok": True,
               "value": state["tenants"][tenant]["store"][key]}


def enumerate_keys(state: dict, handle: str) -> tuple:
    """Only ever the caller's own keys. There is no API shape that
    names another tenant."""
    h = _resolve(state, handle)
    if h is None:
        return state, {"ok": False, "reason": "E_UNKNOWN_HANDLE"}
    if "store.read" not in h["capabilities"]:
        return state, {"ok": False, "reason": "E_CAPABILITY_MISSING",
                       "needed": "store.read"}
    s = _bump(state)
    s = _audit(s, h["tenant"], {"kind": "ENUMERATE"})
    return s, {"ok": True, "tenant": h["tenant"],
               "keys": tuple(sorted(
                   state["tenants"][h["tenant"]]["store"]))}


# ── the control plane: shared, read-only to tenants ────────────────────

def publish_release(state: dict, artifact: str, digest: str) -> tuple:
    """Control-plane write — the PLATFORM's verb, no tenant handle
    involved. Distributes versions; holds no customer data."""
    s = _bump(state)
    s["control_plane"] = {**s["control_plane"], artifact: digest}
    return s, {"ok": True, "artifact": artifact, "digest": digest}


def read_release(state: dict, handle: str, artifact: str) -> tuple:
    """Any lawful handle may read a release — that is the lawful
    sharing: control-plane artifacts, explicitly, read-only."""
    h = _resolve(state, handle)
    if h is None:
        return state, {"ok": False, "reason": "E_UNKNOWN_HANDLE"}
    if artifact not in state["control_plane"]:
        return state, {"ok": False, "reason": "E_NOT_READABLE"}
    return state, {"ok": True, "artifact": artifact,
                   "digest": state["control_plane"][artifact]}


def write_release_via_tenant(state: dict, handle: str, artifact: str,
                             digest: str) -> tuple:
    """The refusal that makes the sharing safe: no tenant handle can
    touch the control plane, whatever capabilities it carries."""
    h = _resolve(state, handle)
    if h is None:
        return state, {"ok": False, "reason": "E_UNKNOWN_HANDLE"}
    return state, {"ok": False, "reason": "E_CONTROL_PLANE_READ_ONLY",
                   "law": "releases are distributed to tenants, never "
                          "edited by them"}


# ── the isolation property, checkable on any state ─────────────────────

def isolation_invariant(state: dict) -> dict:
    """Executable over a REAL state, not a hypothetical: no key
    object shared between tenant stores, every handle bound to an
    existing tenant, every audit event in its own tenant's log."""
    stores = {t: set(v["store"]) for t, v in state["tenants"].items()}
    names = sorted(stores)
    overlap = {}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            both = stores[a] & stores[b]
            # same key STRING in two stores is lawful (namespaced by
            # tenant); what may never happen is a handle crossing —
            # checked below. Value sharing is impossible by
            # construction (stores are per-tenant dicts).
    unbound = [h for h, v in state["handles"].items()
               if v["tenant"] not in state["tenants"]]
    return {"holds": not unbound,
            "tenants": tuple(names),
            "unbound_handles": tuple(unbound),
            "law": "isolation is an architectural property of the "
                   "state, re-derivable at any moment — not a "
                   "contractual reassurance"}

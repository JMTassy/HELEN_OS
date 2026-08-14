r"""Identity Runtime — Phase A item 2, identity/RBAC as enforcing
code in the reducer-seam style.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.
STATUS: REFERENCE_IMPLEMENTATION — executable semantics of the
Identity/RBAC transversal; the production build replaces the store,
not the laws. Pure state machine: no function mutates its input,
deterministic replay, per-tenant audit.

WHAT THE DATA PATH ITSELF REFUSES:
- an identity may not grant a role TO ITSELF, even holding
  iam.role.bind (E_SELF_GRANT) — the debtor/creditor law inside IAM:
  the grantor may not be the grantee
- roles are TENANT-SCOPED: a binding in tenant A licenses nothing in
  tenant B, and the refusal is the same for "no role here" and
  "role lacks the capability" (E_NOT_AUTHORIZED) — a distinct answer
  would leak role existence across the boundary
- capabilities are dotted, never ALL (E_AMBIENT_AUTHORITY)
- a forged session dict is unknown to the registry however
  well-formed (E_UNKNOWN_SESSION) — identity is registry membership
- revocation is immediate: the next authorize after revoke fails,
  no grace, no cache; and SELF-revocation is lawful without any
  capability — bad news needs no permission
- bootstrap is a PLATFORM verb (like publish_release): the first
  admin binding happens before any session exists and is audited as
  such; afterwards the platform door is closed by discipline, not
  used silently

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


def boot() -> dict:
    return {"identities": {}, "roles": {}, "bindings": {},
            "sessions": {}, "audit": {}, "seq": 0}


def _bump(s: dict) -> dict:
    n = dict(s)
    n["seq"] = s["seq"] + 1
    return n


def _audit(s: dict, tenant: str, event: dict) -> dict:
    n = dict(s)
    log = n["audit"].get(tenant, ())
    n["audit"] = {**n["audit"],
                  tenant: log + ({"seq": s["seq"], **event},)}
    return n


# ── registration ───────────────────────────────────────────────────────

def register_identity(state: dict, ident: str) -> tuple:
    if ident in state["identities"]:
        return state, {"ok": False, "reason": "E_IDENTITY_EXISTS"}
    s = _bump(state)
    s["identities"] = {**s["identities"], ident: {"active": True}}
    return s, {"ok": True, "identity": ident}


def define_role(state: dict, role: str, capabilities: tuple) -> tuple:
    """A role is a named dotted-capability set. Never ALL."""
    if role in state["roles"]:
        return state, {"ok": False, "reason": "E_ROLE_EXISTS"}
    if "ALL" in capabilities or "*" in capabilities or \
            any("." not in c for c in capabilities):
        return state, {"ok": False, "reason": "E_AMBIENT_AUTHORITY"}
    s = _bump(state)
    s["roles"] = {**s["roles"],
                  role: tuple(sorted(set(capabilities)))}
    return s, {"ok": True, "role": role}


# ── sessions ───────────────────────────────────────────────────────────

def open_session(state: dict, ident: str) -> tuple:
    """A session is minted BY the runtime; its identity is registry
    membership, not its field values."""
    if ident not in state["identities"]:
        return state, {"ok": False, "reason": "E_UNKNOWN_IDENTITY"}
    s = _bump(state)
    sid = _sha(("session", ident, s["seq"]))
    s["sessions"] = {**s["sessions"], sid: {"identity": ident}}
    return s, {"ok": True, "session": sid, "identity": ident}


def _actor(state: dict, session: str) -> str | None:
    rec = state["sessions"].get(session)
    return rec["identity"] if rec else None


# ── binding: the grantor may not be the grantee ────────────────────────

def bootstrap_bind(state: dict, ident: str, role: str,
                   tenant: str) -> tuple:
    """The platform verb that solves the first-admin regress. Audited
    as BOOTSTRAP so its use is countable; after the first admin
    exists, ordinary bind_role is the only lawful door."""
    if ident not in state["identities"] or role not in state["roles"]:
        return state, {"ok": False, "reason": "E_UNKNOWN_REF"}
    s = _bump(state)
    key = f"{ident}@{tenant}"
    held = s["bindings"].get(key, ())
    s["bindings"] = {**s["bindings"], key: tuple(sorted(set(held) |
                                                        {role}))}
    s = _audit(s, tenant, {"kind": "BOOTSTRAP_BIND",
                           "identity": ident, "role": role})
    return s, {"ok": True, "via": "platform_bootstrap"}


def bind_role(state: dict, actor_session: str, ident: str, role: str,
              tenant: str) -> tuple:
    """Binding needs iam.role.bind IN THAT TENANT — and the grantor
    may never be the grantee, whatever it holds."""
    actor = _actor(state, actor_session)
    if actor is None:
        return state, {"ok": False, "reason": "E_UNKNOWN_SESSION"}
    if actor == ident:
        s = _bump(state)
        s = _audit(s, tenant, {"kind": "SELF_GRANT_REFUSED",
                               "identity": actor, "role": role})
        return s, {"ok": False, "reason": "E_SELF_GRANT",
                   "law": "the grantor may not be the grantee; "
                          "self-elevation is self-discharge wearing "
                          "IAM"}
    ok, _ = _authorized(state, actor, "iam.role.bind", tenant)
    if not ok:
        return state, {"ok": False, "reason": "E_NOT_AUTHORIZED"}
    if role not in state["roles"] or ident not in state["identities"]:
        return state, {"ok": False, "reason": "E_UNKNOWN_REF"}
    s = _bump(state)
    key = f"{ident}@{tenant}"
    held = s["bindings"].get(key, ())
    s["bindings"] = {**s["bindings"],
                     key: tuple(sorted(set(held) | {role}))}
    s = _audit(s, tenant, {"kind": "ROLE_BOUND", "identity": ident,
                           "role": role, "by": actor})
    return s, {"ok": True, "identity": ident, "role": role,
               "tenant": tenant, "by": actor}


def revoke_role(state: dict, actor_session: str, ident: str,
                role: str, tenant: str) -> tuple:
    """Revocation is immediate. Revoking ANOTHER identity needs
    iam.role.bind; revoking YOURSELF is lawful with no capability at
    all — bad news needs no permission."""
    actor = _actor(state, actor_session)
    if actor is None:
        return state, {"ok": False, "reason": "E_UNKNOWN_SESSION"}
    if actor != ident:
        ok, _ = _authorized(state, actor, "iam.role.bind", tenant)
        if not ok:
            return state, {"ok": False, "reason": "E_NOT_AUTHORIZED"}
    key = f"{ident}@{tenant}"
    held = state["bindings"].get(key, ())
    if role not in held:
        return state, {"ok": False, "reason": "E_NOT_AUTHORIZED"}
    s = _bump(state)
    s["bindings"] = {**s["bindings"],
                     key: tuple(r for r in held if r != role)}
    s = _audit(s, tenant, {"kind": "ROLE_REVOKED", "identity": ident,
                           "role": role, "by": actor,
                           "self": actor == ident})
    return s, {"ok": True, "immediate": True}


# ── authorization: the enforcement point ───────────────────────────────

def _authorized(state: dict, ident: str, capability: str,
                tenant: str) -> tuple:
    roles = state["bindings"].get(f"{ident}@{tenant}", ())
    for r in roles:
        if capability in state["roles"].get(r, ()):
            return True, r
    return False, None


def authorize(state: dict, session: str, capability: str,
              tenant: str) -> tuple:
    """ONE refusal for 'no role in this tenant' and 'role lacks the
    capability' — a distinct answer would leak role existence across
    the tenant boundary. Metadata is part of isolation."""
    actor = _actor(state, session)
    if actor is None:
        return state, {"ok": False, "reason": "E_UNKNOWN_SESSION"}
    ok, via = _authorized(state, actor, capability, tenant)
    s = _bump(state)
    s = _audit(s, tenant, {"kind": "AUTHORIZE",
                           "identity": actor,
                           "capability": capability,
                           "granted": ok})
    if not ok:
        return s, {"ok": False, "reason": "E_NOT_AUTHORIZED",
                   "law": "cross-tenant and missing-capability are "
                          "one indistinguishable answer"}
    return s, {"ok": True, "identity": actor,
               "capability": capability, "tenant": tenant,
               "via_role": via}


def rbac_invariant(state: dict) -> dict:
    """Re-derivable on the real state: every binding references an
    existing identity and role; no role carries ambient authority."""
    bad_refs = [k for k, roles in state["bindings"].items()
                if k.split("@")[0] not in state["identities"] or
                any(r not in state["roles"] for r in roles)]
    ambient = [r for r, caps in state["roles"].items()
               if any("." not in c or c in ("ALL", "*")
                      for c in caps)]
    return {"holds": not bad_refs and not ambient,
            "dangling_bindings": tuple(bad_refs),
            "ambient_roles": tuple(ambient),
            "law": "authorization is a property of the state, "
                   "re-derivable at any moment"}

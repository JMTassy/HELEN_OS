r"""API Runtime — Phase A item 5, the stable API boundary as
enforcing code in the reducer-seam style.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.
STATUS: REFERENCE_IMPLEMENTATION — executable semantics of the
stable REST boundary; the production build replaces the transport,
not the laws.

WHAT THE BOUNDARY ITSELF REFUSES:
- an endpoint exists only if DECLARED in a frozen, content-addressed
  contract version. The contract digest answers the deployment
  identity question ("which API version?") by arithmetic.
- evolution is APPEND-ONLY within a major version: adding endpoints
  or optional fields is lawful; removing an endpoint, dropping a
  response field, or changing a field's type inside the same major
  is E_BREAKING_CHANGE_IN_MINOR. Clients are tenants of the
  contract; their ground does not move under them.
- removal is a STATE MACHINE: ACTIVE -> DEPRECATED (with a named
  sunset) -> absent in the NEXT MAJOR only. Removing an
  un-deprecated endpoint is E_REMOVAL_WITHOUT_DEPRECATION even
  across a major bump — no arrow skipped by narration, at the API.
- requests are validated at the boundary: missing required fields,
  undeclared fields and type mismatches die before any handler runs.
- ENUMERATION DEFENSE: an unknown endpoint and an unauthorized call
  to a real endpoint are ONE indistinguishable answer (E_NOT_FOUND)
  — a distinct 401/403 would leak the API surface across the
  authorization boundary; the metadata law at the edge.
- RESPONSES are validated too: a handler emitting an undeclared
  field is refused (E_UNDECLARED_RESPONSE_FIELD) — the mythology
  leak law enforced at the wire: an internal "goblin_trace" field
  physically cannot cross; and a missing declared field is
  E_INCOMPLETE_RESPONSE. The boundary is bidirectional or it is
  decoration.

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import hashlib
import json

TYPES = ("string", "int", "bool", "object", "array")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def _sha(obj) -> str:
    return hashlib.sha256(canon(obj).encode()).hexdigest()[:16]


def boot() -> dict:
    return {"contracts": {}, "seq": 0}


def _major(version: str) -> str:
    return version.split(".")[0]


# ── the contract: declared, frozen, content-addressed ──────────────────

def define_contract(state: dict, version: str,
                    endpoints: dict) -> tuple:
    """endpoints: {name: {"capability": str,
                          "request": {field: type},
                          "required": (fields...),
                          "response": {field: type},
                          "status": "ACTIVE"|"DEPRECATED"}}.
    Frozen at definition; the digest is the identity."""
    if version in state["contracts"]:
        return state, {"ok": False, "reason": "E_VERSION_EXISTS"}
    for name, ep in endpoints.items():
        fields = {**ep.get("request", {}), **ep.get("response", {})}
        if any(t not in TYPES for t in fields.values()):
            return state, {"ok": False, "reason": "E_UNKNOWN_TYPE",
                           "endpoint": name}
        if not set(ep.get("required", ())) <= set(ep.get("request",
                                                         {})):
            return state, {"ok": False,
                           "reason": "E_REQUIRED_NOT_DECLARED",
                           "endpoint": name}
    norm = {n: {"capability": ep["capability"],
                "request": dict(sorted(ep.get("request", {}).items())),
                "required": tuple(sorted(ep.get("required", ()))),
                "response": dict(sorted(ep.get("response",
                                               {}).items())),
                "status": ep.get("status", "ACTIVE"),
                "sunset": ep.get("sunset")}
            for n, ep in endpoints.items()}
    s = dict(state)
    s["seq"] = state["seq"] + 1
    s["contracts"] = {**s["contracts"],
                      version: {"endpoints": norm,
                                "digest": _sha(norm)}}
    return s, {"ok": True, "version": version,
               "digest": s["contracts"][version]["digest"],
               "n_endpoints": len(norm)}


def contract_digest(state: dict, version: str) -> dict:
    c = state["contracts"].get(version)
    if c is None:
        return {"ok": False, "reason": "E_UNKNOWN_VERSION"}
    return {"ok": True, "version": version, "digest": c["digest"],
            "law": "the digest answers 'which API version' by "
                   "arithmetic"}


# ── evolution: append-only within a major ──────────────────────────────

def evolve(state: dict, from_version: str, new_version: str,
           endpoints: dict) -> tuple:
    """Within one major: every old endpoint survives, every old
    response field survives with its type, required fields never
    grow. Across a major: removal is lawful ONLY for endpoints
    already DEPRECATED in the prior version."""
    old = state["contracts"].get(from_version)
    if old is None:
        return state, {"ok": False, "reason": "E_UNKNOWN_VERSION"}
    same_major = _major(from_version) == _major(new_version)
    breaks = []
    for name, oep in old["endpoints"].items():
        nep = endpoints.get(name)
        if nep is None:
            if same_major:
                breaks.append(f"{name}: removed in minor")
            elif oep["status"] != "DEPRECATED":
                return state, {"ok": False,
                               "reason":
                                   "E_REMOVAL_WITHOUT_DEPRECATION",
                               "endpoint": name,
                               "law": "ACTIVE -> DEPRECATED -> "
                                      "absent; no arrow skipped by "
                                      "narration, at the API"}
            continue
        if same_major:
            for f, t in oep["response"].items():
                nt = nep.get("response", {}).get(f)
                if nt is None:
                    breaks.append(f"{name}.response.{f}: dropped")
                elif nt != t:
                    breaks.append(f"{name}.response.{f}: {t}->{nt}")
            for f, t in oep["request"].items():
                nt = nep.get("request", {}).get(f)
                if nt is not None and nt != t:
                    breaks.append(f"{name}.request.{f}: {t}->{nt}")
            if not set(nep.get("required", ())) <= \
                    set(oep["required"]) | \
                    (set(nep.get("request", {})) -
                     set(oep["request"])):
                # old optional fields may not become required
                grown = set(nep.get("required", ())) & \
                    (set(oep["request"]) - set(oep["required"]))
                if grown:
                    breaks.append(f"{name}: required grew {sorted(grown)}")
    if breaks and same_major:
        return state, {"ok": False,
                       "reason": "E_BREAKING_CHANGE_IN_MINOR",
                       "breaks": tuple(sorted(breaks)),
                       "law": "clients are tenants of the contract; "
                              "their ground does not move under them"}
    return define_contract(state, new_version, endpoints)


def deprecate(state: dict, version: str, endpoint: str,
              sunset: str) -> tuple:
    """Marks the endpoint; a sunset must be named — an undated
    deprecation is a threat, not a plan."""
    c = state["contracts"].get(version)
    if c is None or endpoint not in c["endpoints"]:
        return state, {"ok": False, "reason": "E_UNKNOWN_ENDPOINT"}
    if not sunset:
        return state, {"ok": False, "reason": "E_UNDATED_DEPRECATION"}
    s = dict(state)
    s["seq"] = state["seq"] + 1
    ep = dict(c["endpoints"][endpoint])
    ep["status"], ep["sunset"] = "DEPRECATED", sunset
    eps = {**c["endpoints"], endpoint: ep}
    s["contracts"] = {**s["contracts"],
                      version: {"endpoints": eps, "digest": _sha(eps)}}
    return s, {"ok": True, "endpoint": endpoint, "sunset": sunset}


# ── the boundary: bidirectional validation ─────────────────────────────

def request(state: dict, version: str, endpoint: str, payload: dict,
            authorized: bool) -> dict:
    """Unknown endpoint and unauthorized are ONE answer. Validation
    runs before any handler exists."""
    c = state["contracts"].get(version)
    ep = c["endpoints"].get(endpoint) if c else None
    if ep is None or not authorized:
        return {"ok": False, "reason": "E_NOT_FOUND",
                "law": "a distinct 401 would leak the API surface "
                       "across the authorization boundary"}
    missing = sorted(set(ep["required"]) - set(payload))
    if missing:
        return {"ok": False, "reason": "E_MISSING_FIELD",
                "missing": tuple(missing)}
    undeclared = sorted(set(payload) - set(ep["request"]))
    if undeclared:
        return {"ok": False, "reason": "E_UNDECLARED_FIELD",
                "undeclared": tuple(undeclared)}
    checks = {"string": str, "int": int, "bool": bool,
              "object": dict, "array": (list, tuple)}
    bad = sorted(f for f, v in payload.items()
                 if not isinstance(v, checks[ep["request"][f]]) or
                 (ep["request"][f] == "int" and isinstance(v, bool)))
    if bad:
        return {"ok": False, "reason": "E_TYPE_MISMATCH",
                "fields": tuple(bad)}
    return {"ok": True, "endpoint": endpoint,
            "deprecated": ep["status"] == "DEPRECATED",
            "sunset": ep["sunset"]}


def respond(state: dict, version: str, endpoint: str,
            body: dict) -> dict:
    """The output side of the boundary. An undeclared field cannot
    cross — the mythology leak law at the wire — and a declared
    field cannot be silently absent."""
    c = state["contracts"].get(version)
    ep = c["endpoints"].get(endpoint) if c else None
    if ep is None:
        return {"ok": False, "reason": "E_UNKNOWN_ENDPOINT"}
    leaked = sorted(set(body) - set(ep["response"]))
    if leaked:
        return {"ok": False, "reason": "E_UNDECLARED_RESPONSE_FIELD",
                "leaked": tuple(leaked),
                "law": "the boundary is bidirectional or it is "
                       "decoration; internals physically cannot "
                       "cross"}
    absent = sorted(set(ep["response"]) - set(body))
    if absent:
        return {"ok": False, "reason": "E_INCOMPLETE_RESPONSE",
                "absent": tuple(absent)}
    return {"ok": True, "endpoint": endpoint}

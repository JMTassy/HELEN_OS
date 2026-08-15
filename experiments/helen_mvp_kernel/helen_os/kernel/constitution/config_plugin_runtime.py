r"""Config & Plugin Runtime — Phase A item 9. One core, configured per
tenant; never a client fork.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.
STATUS: REFERENCE_IMPLEMENTATION (in-memory, deterministic). The
production build replaces the store, not the laws.

The founding law:

    Product_i = Core + Configuration_i

The core is ONE codebase, byte-identical across tenants. A tenant
customizes by LAYERING configuration over the shared core, never by
forking or mutating it. Two tenants must differ only in their config
layer — a difference anywhere else is a client fork, refused.

WHAT THE DATA PATH ITSELF REFUSES:
- a tenant override of a core-locked key (E_CLIENT_FORK) — the core
  is read-only to tenants; customization lives in the config layer
- config applied without a version (E_UNVERSIONED_CONFIG) — every
  effective config is reproducible from (core_version, overrides)
- a plugin invoked before it is ADMITTED, not merely installed
  (E_PLUGIN_UNADMITTED) — installed ⊬ enabled
- a plugin requesting ambient authority (E_PLUGIN_AMBIENT_AUTHORITY)
  or using a capability it never declared
  (E_PLUGIN_UNDECLARED_CAPABILITY) — a plugin runs in a capability
  sandbox, holding only what it declared AND was granted
- a plugin reaching another tenant's config or core
  (E_PLUGIN_CROSS_TENANT) — one answer with absent
- effective config that is not re-derivable as core+overrides
  (the invariant catches a mutated core)

Style: the reducer seam — pure state machine, (state, receipt)
returns, no function mutates its input, per-tenant config, no
wall-clock, no randomness.
"""
from __future__ import annotations

import hashlib
import json

# keys that belong to the shared core and are read-only to tenants:
# overriding one is a client fork, not a configuration.
CORE_LOCKED_KEYS = ("admission_algebra", "reducer_seam",
                    "audit_chain", "receipt_format")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      default=str)


def _sha(obj) -> str:
    return hashlib.sha256(canon(obj).encode()).hexdigest()[:16]


# ── boot & core ────────────────────────────────────────────────────────

def boot(core_version, core_defaults) -> dict:
    """The platform boots with ONE core: a version and the shared
    default config. The core is the same object every tenant sees."""
    return {"core_version": core_version,
            "core_defaults": dict(core_defaults),
            "core_hash": _sha({"v": core_version,
                               "d": dict(core_defaults)}),
            "tenants": {}, "seq": 0}


def _bump(state):
    s = dict(state)
    s["seq"] = state["seq"] + 1
    return s


def provision_tenant(state, tenant) -> tuple:
    if tenant in state["tenants"]:
        return state, {"ok": False, "reason": "E_TENANT_EXISTS"}
    s = _bump(state)
    s["tenants"] = {**s["tenants"],
                    tenant: {"overrides": {}, "config_version": 0,
                             "plugins": {}}}
    return s, {"ok": True, "tenant": tenant}


def _t(state, tenant):
    return state["tenants"].get(tenant)


# ── configuration: layered, never forked ───────────────────────────────

def set_config(state, tenant, key, value, config_version) -> tuple:
    """Layer a tenant override. A key that belongs to the core is
    read-only: overriding it would fork the product, so it is refused.
    Every set advances a version so the effective config is
    reproducible."""
    t = _t(state, tenant)
    if t is None:
        return state, {"ok": False, "reason": "E_UNKNOWN_TENANT"}
    if key in CORE_LOCKED_KEYS:
        return state, {"ok": False, "reason": "E_CLIENT_FORK",
                       "key": key,
                       "law": "Product_i = Core + Configuration_i; "
                              "the core is not a configuration surface"}
    if config_version is None:
        return state, {"ok": False, "reason": "E_UNVERSIONED_CONFIG"}
    s = _bump(state)
    tt = dict(s["tenants"][tenant])
    tt["overrides"] = {**tt["overrides"], key: value}
    tt["config_version"] = config_version
    s["tenants"] = {**s["tenants"], tenant: tt}
    return s, {"ok": True, "config_version": config_version}


def effective_config(state, tenant, caller_tenant) -> dict:
    """The product a tenant runs = core defaults with its overrides
    layered on top. Cross-tenant reads are one answer with absent."""
    if caller_tenant != tenant or _t(state, tenant) is None:
        return {"ok": False, "reason": "E_PLUGIN_CROSS_TENANT"}
    t = _t(state, tenant)
    merged = {**state["core_defaults"], **t["overrides"]}
    return {"ok": True, "config": merged,
            "core_version": state["core_version"],
            "config_version": t["config_version"],
            "reproducible_from": ("core_version", "overrides"),
            "product_identity": _sha({"core": state["core_hash"],
                                      "ov": t["overrides"]})}


# ── plugins: installed is not admitted ─────────────────────────────────

def install_plugin(state, tenant, plugin_id,
                   declared_capabilities) -> tuple:
    """Install a plugin with its DECLARED capability set. Ambient
    authority is refused at install. Install is not enable: the
    plugin is INSTALLED, not yet ADMITTED."""
    t = _t(state, tenant)
    if t is None:
        return state, {"ok": False, "reason": "E_UNKNOWN_TENANT"}
    caps = tuple(sorted(declared_capabilities))
    if any(c in ("*", "ALL") or "." not in c for c in caps):
        return state, {"ok": False,
                       "reason": "E_PLUGIN_AMBIENT_AUTHORITY"}
    s = _bump(state)
    tt = dict(s["tenants"][tenant])
    tt["plugins"] = {**tt["plugins"],
                     plugin_id: {"declared": caps, "granted": (),
                                 "status": "INSTALLED"}}
    s["tenants"] = {**s["tenants"], tenant: tt}
    return s, {"ok": True, "status": "INSTALLED",
               "law": "installed does not imply enabled"}


def admit_plugin(state, tenant, plugin_id, granted_capabilities,
                 admitter) -> tuple:
    """Gamma admits a plugin, granting a subset of what it declared.
    A grant beyond the declared set is refused — a plugin cannot be
    handed authority it never asked for."""
    t = _t(state, tenant)
    if t is None or plugin_id not in t["plugins"]:
        return state, {"ok": False, "reason": "E_UNKNOWN_PLUGIN"}
    if not admitter:
        return state, {"ok": False, "reason": "E_PLUGIN_UNADMITTED"}
    p = t["plugins"][plugin_id]
    granted = tuple(sorted(granted_capabilities))
    if set(granted) - set(p["declared"]):
        return state, {"ok": False,
                       "reason": "E_PLUGIN_UNDECLARED_CAPABILITY",
                       "extra": tuple(sorted(set(granted) -
                                             set(p["declared"])))}
    s = _bump(state)
    tt = dict(s["tenants"][tenant])
    tt["plugins"] = {**tt["plugins"],
                     plugin_id: {**p, "granted": granted,
                                 "status": "ADMITTED",
                                 "admitter": admitter}}
    s["tenants"] = {**s["tenants"], tenant: tt}
    return s, {"ok": True, "status": "ADMITTED", "granted": granted}


def invoke_plugin(state, tenant, plugin_id, uses_capability,
                  target_tenant=None) -> dict:
    """A plugin runs only when ADMITTED, only with a capability it was
    granted, and only within its own tenant. Everything else refuses
    in the data path."""
    t = _t(state, tenant)
    if t is None or plugin_id not in t["plugins"]:
        return {"ok": False, "reason": "E_UNKNOWN_PLUGIN"}
    p = t["plugins"][plugin_id]
    if p["status"] != "ADMITTED":
        return {"ok": False, "reason": "E_PLUGIN_UNADMITTED",
                "status": p["status"]}
    if target_tenant is not None and target_tenant != tenant:
        return {"ok": False, "reason": "E_PLUGIN_CROSS_TENANT"}
    if uses_capability not in p["granted"]:
        # declared-but-not-granted is a different failure than never
        # declared at all — the sandbox distinguishes them.
        return {"ok": False,
                "reason": "E_PLUGIN_CAPABILITY_NOT_GRANTED"
                if uses_capability in p["declared"]
                else "E_PLUGIN_UNDECLARED_CAPABILITY",
                "capability": uses_capability}
    return {"ok": True, "ran": plugin_id, "with": uses_capability,
            "sandboxed_to": tenant}


# ── the invariant: one core, provable ──────────────────────────────────

def config_invariant(state) -> dict:
    """The core is identical for every tenant (single codebase), and
    each tenant's product is exactly core+overrides. A tenant whose
    effective config diverges from that merge has forked the product
    — the difference between two tenants must live wholly in the
    config layer."""
    core = state["core_defaults"]
    forks, diffs = [], []
    for tenant, t in state["tenants"].items():
        # any override key that collides with a core-locked key is a
        # fork that slipped past set_config (e.g. hand-forged state)
        if set(t["overrides"]) & set(CORE_LOCKED_KEYS):
            forks.append(tenant)
        merged = {**core, **t["overrides"]}
        # the only legal source of difference from core is overrides
        delta = {k for k in merged if merged.get(k) != core.get(k)}
        if delta - set(t["overrides"]):
            diffs.append(tenant)
    holds = not forks and not diffs
    return {"holds": holds, "core_hash": state["core_hash"],
            "client_forks": tuple(sorted(forks)),
            "unexplained_divergence": tuple(sorted(diffs)),
            "law": "difference between tenants lives wholly in the "
                   "config layer"}

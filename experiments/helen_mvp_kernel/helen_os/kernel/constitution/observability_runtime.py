r"""Observability & Backup Runtime — Phase A item 8. Metrics and
traces are REPRESENTATIONS; a backup is not real until a restore
re-derives it.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.
STATUS: REFERENCE_IMPLEMENTATION (in-memory, deterministic). The
production build replaces the store, not the laws.

The two laws that carry this module:

    a metric/trace is a REPRESENTATION, never an admission
        (dP, dA, dE) = (0, 0, 0) — observing the system does not
        change its reality or authority

    BackupExists ⊬ BackupRestorable ⊬ BackupRestored
        PERSISTENCE ≠ TRUTH: a backup manifest proves a copy was
        WRITTEN, never that it can be READ BACK. Only a witnessed
        restore that RE-DERIVES the source proves the backup real.

WHAT THE DATA PATH ITSELF REFUSES:
- a metric emission that claims to mutate admitted world state
  (E_METRIC_MINTS_WORLD_STATE) — the operator-side read path never
  writes the business plane
- a trace or metric carrying raw content instead of a digest/ref
  (E_OBSERVABILITY_CONTENT_LEAK) — observability outlives the
  retention policy on the data it describes, so it stores digests
- cross-tenant reads of metrics, traces or backups, indistinguishable
  from absent (E_CROSS_TENANT_OBSERVABILITY / one answer)
- a backup with no source digest (E_UNPROVENANCED_BACKUP)
- treating a written backup as usable without a witnessed restore
  (E_BACKUP_UNRESTORED) — the status is BACKED_UP, not RESTORABLE
- a restore whose re-derived digest does not match the source
  (E_RESTORE_MISMATCH) — a corrupt/partial backup is caught by
  arithmetic, not trusted by its manifest
- an alert firing treated as a remediation (E_ALERT_IS_NOT_REMEDIATION)

Style: the reducer seam — pure state machine, (state, receipt)
returns, no function mutates its input, per-tenant stores, no
wall-clock, no randomness; sequence numbers order events.
"""
from __future__ import annotations

import hashlib
import json

METRIC_KINDS = ("counter", "gauge", "histogram")
BACKUP_STATES = ("BACKED_UP", "RESTORE_VERIFIED", "RESTORE_FAILED")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      default=str)


def _sha(obj) -> str:
    return hashlib.sha256(canon(obj).encode()).hexdigest()[:16]


# ── boot ───────────────────────────────────────────────────────────────

def boot() -> dict:
    return {"tenants": {}, "seq": 0}


def _bump(state: dict) -> dict:
    s = dict(state)
    s["seq"] = state["seq"] + 1
    return s


def provision_tenant(state: dict, tenant: str) -> tuple:
    if tenant in state["tenants"]:
        return state, {"ok": False, "reason": "E_TENANT_EXISTS"}
    s = _bump(state)
    s["tenants"] = {**s["tenants"],
                    tenant: {"metrics": (), "traces": (), "alerts": (),
                             "backups": {}}}
    return s, {"ok": True, "tenant": tenant}


def _t(state, tenant):
    return state["tenants"].get(tenant)


# ── metrics: representations, not admissions ───────────────────────────

def emit_metric(state, tenant, name, kind, digest,
                mutates_world_state=False) -> tuple:
    """A metric records an observation. It carries a digest of what it
    measured, never the raw value, and it changes no admitted state:
    (dP, dA, dE) = (0, 0, 0). A metric that claims to mutate the
    business plane is refused — the read path never writes."""
    t = _t(state, tenant)
    if t is None:
        return state, {"ok": False, "reason": "E_UNKNOWN_TENANT"}
    if kind not in METRIC_KINDS:
        return state, {"ok": False, "reason": "E_UNKNOWN_METRIC_KIND"}
    if mutates_world_state:
        return state, {"ok": False,
                       "reason": "E_METRIC_MINTS_WORLD_STATE",
                       "law": "observing the system does not change it"}
    if not digest:
        return state, {"ok": False,
                       "reason": "E_OBSERVABILITY_CONTENT_LEAK",
                       "missing": "digest"}
    s = _bump(state)
    ev = {"seq": s["seq"], "name": name, "kind": kind,
          "digest": digest}
    tt = dict(s["tenants"][tenant])
    tt["metrics"] = tt["metrics"] + (ev,)
    s["tenants"] = {**s["tenants"], tenant: tt}
    return s, {"ok": True, "grade": "REPRESENTATION",
               "emits_world_claim": False, "dP": 0, "dA": 0, "dE": 0}


def record_trace(state, tenant, span, parent_ref, payload_ref) -> tuple:
    """A trace span is append-only and carries REFERENCES, never
    content. A span with an inline body leaks content past the
    retention policy on that data."""
    t = _t(state, tenant)
    if t is None:
        return state, {"ok": False, "reason": "E_UNKNOWN_TENANT"}
    if not payload_ref or " " in str(payload_ref):
        return state, {"ok": False,
                       "reason": "E_OBSERVABILITY_CONTENT_LEAK",
                       "note": "trace carries content, not a ref"}
    s = _bump(state)
    ev = {"seq": s["seq"], "span": span, "parent": parent_ref,
          "payload_ref": payload_ref}
    tt = dict(s["tenants"][tenant])
    tt["traces"] = tt["traces"] + (ev,)
    s["tenants"] = {**s["tenants"], tenant: tt}
    return s, {"ok": True, "grade": "REPRESENTATION"}


def raise_alert(state, tenant, rule, fired, remediated=False) -> tuple:
    """An alert is a representation of a threshold crossing. Firing it
    changes nothing; claiming the fire itself remediated the cause is
    refused — remediation is a separate admitted action."""
    t = _t(state, tenant)
    if t is None:
        return state, {"ok": False, "reason": "E_UNKNOWN_TENANT"}
    if remediated:
        return state, {"ok": False,
                       "reason": "E_ALERT_IS_NOT_REMEDIATION",
                       "law": "an alert reports; it does not fix"}
    s = _bump(state)
    ev = {"seq": s["seq"], "rule": rule, "fired": bool(fired)}
    tt = dict(s["tenants"][tenant])
    tt["alerts"] = tt["alerts"] + (ev,)
    s["tenants"] = {**s["tenants"], tenant: tt}
    return s, {"ok": True, "grade": "REPRESENTATION"}


def read_metrics(state, tenant, caller_tenant) -> dict:
    """Cross-tenant and absent are one answer — metric existence never
    leaks across the boundary."""
    if caller_tenant != tenant or _t(state, tenant) is None:
        return {"ok": False, "reason": "E_CROSS_TENANT_OBSERVABILITY"}
    return {"ok": True, "metrics": _t(state, tenant)["metrics"]}


# ── backup: written is not restorable is not restored ──────────────────

def take_backup(state, tenant, backup_id, source_digest,
                stored_digest) -> tuple:
    """Write a backup. Its manifest records the SOURCE digest (what
    was backed up) and the STORED digest (what landed). Status is
    BACKED_UP — an assertion that a copy was written, and NOTHING
    more. A backup with no source digest cannot ever be verified."""
    t = _t(state, tenant)
    if t is None:
        return state, {"ok": False, "reason": "E_UNKNOWN_TENANT"}
    if not source_digest:
        return state, {"ok": False, "reason": "E_UNPROVENANCED_BACKUP"}
    s = _bump(state)
    manifest = {"backup_id": backup_id, "source_digest": source_digest,
                "stored_digest": stored_digest, "seq": s["seq"],
                "status": "BACKED_UP",
                "restorable": None,          # unknown until a restore
                "manifest_hash": _sha(("bk", backup_id, source_digest,
                                       stored_digest))}
    tt = dict(s["tenants"][tenant])
    tt["backups"] = {**tt["backups"], backup_id: manifest}
    s["tenants"] = {**s["tenants"], tenant: tt}
    return s, {"ok": True, "status": "BACKED_UP",
               "restorable": None,
               "law": "BackupExists does not imply BackupRestorable"}


def usable_for_recovery(state, tenant, backup_id) -> dict:
    """The refusal that matters: a backup is usable for recovery only
    after a witnessed restore verified it. BACKED_UP is not enough."""
    t = _t(state, tenant)
    if t is None or backup_id not in t.get("backups", {}):
        return {"ok": False, "reason": "E_UNKNOWN_BACKUP"}
    m = t["backups"][backup_id]
    if m["status"] != "RESTORE_VERIFIED":
        return {"usable": False, "reason": "E_BACKUP_UNRESTORED",
                "status": m["status"],
                "law": "only a witnessed restore proves a backup real"}
    return {"usable": True, "status": "RESTORE_VERIFIED"}


def verify_restore(state, tenant, backup_id,
                   rederived_digest) -> tuple:
    """Restore the backup into a scratch space and RE-DERIVE its
    digest. If it matches the source, the backup is proven
    RESTORE_VERIFIED. If not, the manifest lied about restorability
    and the backup is RESTORE_FAILED — caught by arithmetic, not
    trusted by the manifest. PERSISTENCE ≠ TRUTH made operational."""
    t = _t(state, tenant)
    if t is None or backup_id not in t.get("backups", {}):
        return state, {"ok": False, "reason": "E_UNKNOWN_BACKUP"}
    m = t["backups"][backup_id]
    s = _bump(state)
    if rederived_digest == m["source_digest"]:
        status, restorable, reason = "RESTORE_VERIFIED", True, None
    else:
        status, restorable, reason = "RESTORE_FAILED", False, \
            "E_RESTORE_MISMATCH"
    m2 = {**m, "status": status, "restorable": restorable,
          "rederived_digest": rederived_digest,
          "verified_at_seq": s["seq"]}
    tt = dict(s["tenants"][tenant])
    tt["backups"] = {**tt["backups"], backup_id: m2}
    s["tenants"] = {**s["tenants"], tenant: tt}
    return s, {"ok": restorable, "status": status,
               "restorable": restorable, "reason": reason,
               "law": "a backup is real only when a restore "
                      "re-derives its source"}


def read_backup(state, tenant, backup_id, caller_tenant) -> dict:
    """One-answer law across the backup surface too."""
    if caller_tenant != tenant or _t(state, tenant) is None or \
            backup_id not in _t(state, tenant).get("backups", {}):
        return {"ok": False, "reason": "E_CROSS_TENANT_OBSERVABILITY"}
    return {"ok": True, "manifest": _t(state, tenant)["backups"][
        backup_id]}


# ── the invariant, re-derivable on real state ──────────────────────────

def observability_invariant(state) -> dict:
    """No metric or trace carries a raw value (all reference-only); no
    backup is marked restorable without a matching re-derivation; and
    every backup that claims RESTORE_VERIFIED has a rederived digest
    equal to its source."""
    leaks, false_restorable = [], []
    for tenant, t in state["tenants"].items():
        for mv in t["metrics"]:
            if "value" in mv:
                leaks.append(f"metric@{tenant}")
        for tr in t["traces"]:
            if "payload" in tr:
                leaks.append(f"trace@{tenant}")
        for bid, m in t.get("backups", {}).items():
            if m["status"] == "RESTORE_VERIFIED" and \
                    m.get("rederived_digest") != m["source_digest"]:
                false_restorable.append(f"{bid}@{tenant}")
            if m["restorable"] and m["status"] != "RESTORE_VERIFIED":
                false_restorable.append(f"{bid}@{tenant}")
    holds = not leaks and not false_restorable
    return {"holds": holds, "content_leaks": tuple(leaks),
            "false_restorable": tuple(false_restorable)}

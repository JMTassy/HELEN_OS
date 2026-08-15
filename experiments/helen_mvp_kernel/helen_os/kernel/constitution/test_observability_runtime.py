"""Phase A item 8, adversarially tested: a metric changes no admitted
state and never carries a raw value; a trace passes references not
content; an alert is not a remediation; cross-tenant observability is
one answer with absent; and a backup is not usable for recovery until
a witnessed restore re-derives its source — a manifest that claims
restorability without a matching re-derivation is caught by arithmetic.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import observability_runtime as ob
from observability_runtime import (
    boot,
    emit_metric,
    observability_invariant,
    provision_tenant,
    raise_alert,
    read_backup,
    read_metrics,
    record_trace,
    take_backup,
    usable_for_recovery,
    verify_restore,
)


def _platform():
    s = boot()
    s, _ = provision_tenant(s, "A")
    s, _ = provision_tenant(s, "B")
    return s


# ── metrics/traces/alerts are representations ──────────────────────────

def test_a_metric_changes_no_admitted_state():
    s = _platform()
    s, r = emit_metric(s, "A", "latency", "gauge", "sha:m")
    assert r["ok"] is True
    assert r["grade"] == "REPRESENTATION"
    assert (r["dP"], r["dA"], r["dE"]) == (0, 0, 0)
    assert r["emits_world_claim"] is False


def test_a_metric_that_claims_to_mutate_world_state_is_refused():
    s = _platform()
    _, r = emit_metric(s, "A", "x", "counter", "sha:m",
                       mutates_world_state=True)
    assert r["reason"] == "E_METRIC_MINTS_WORLD_STATE"


def test_metrics_and_traces_carry_digests_not_content():
    s = _platform()
    _, r = emit_metric(s, "A", "x", "gauge", digest="")
    assert r["reason"] == "E_OBSERVABILITY_CONTENT_LEAK"
    _, tr = record_trace(s, "A", "span1", None,
                         payload_ref="raw content here")
    assert tr["reason"] == "E_OBSERVABILITY_CONTENT_LEAK"
    s, ok = record_trace(s, "A", "span1", None, payload_ref="ref:42")
    assert ok["ok"] is True


def test_an_unknown_metric_kind_is_refused():
    s = _platform()
    _, r = emit_metric(s, "A", "x", "vibes", "sha:m")
    assert r["reason"] == "E_UNKNOWN_METRIC_KIND"


def test_an_alert_is_not_a_remediation():
    s = _platform()
    s, r = raise_alert(s, "A", "cpu>90", fired=True)
    assert r["ok"] is True and r["grade"] == "REPRESENTATION"
    _, bad = raise_alert(s, "A", "cpu>90", fired=True, remediated=True)
    assert bad["reason"] == "E_ALERT_IS_NOT_REMEDIATION"


def test_cross_tenant_metric_read_is_one_answer_with_absent():
    s = _platform()
    s, _ = emit_metric(s, "A", "x", "gauge", "sha:m")
    cross = read_metrics(s, "A", caller_tenant="B")
    absent = read_metrics(s, "GHOST", caller_tenant="GHOST")
    assert cross["reason"] == absent["reason"] == \
        "E_CROSS_TENANT_OBSERVABILITY"
    own = read_metrics(s, "A", caller_tenant="A")
    assert own["ok"] is True and len(own["metrics"]) == 1


# ── backup: the PERSISTENCE != TRUTH law ───────────────────────────────

def test_a_written_backup_is_not_yet_restorable():
    s = _platform()
    s, r = take_backup(s, "A", "bk1", source_digest="sha:src",
                       stored_digest="sha:stored")
    assert r["ok"] is True and r["status"] == "BACKED_UP"
    assert r["restorable"] is None
    u = usable_for_recovery(s, "A", "bk1")
    assert u["usable"] is False
    assert u["reason"] == "E_BACKUP_UNRESTORED"


def test_a_backup_without_a_source_digest_cannot_be_verified():
    s = _platform()
    _, r = take_backup(s, "A", "bk1", source_digest="", stored_digest="x")
    assert r["reason"] == "E_UNPROVENANCED_BACKUP"


def test_a_witnessed_restore_that_rederives_the_source_proves_it():
    s = _platform()
    s, _ = take_backup(s, "A", "bk1", "sha:src", "sha:stored")
    s, v = verify_restore(s, "A", "bk1", rederived_digest="sha:src")
    assert v["ok"] is True and v["status"] == "RESTORE_VERIFIED"
    assert v["restorable"] is True
    assert usable_for_recovery(s, "A", "bk1")["usable"] is True


def test_a_restore_that_does_not_rederive_is_caught_by_arithmetic():
    s = _platform()
    s, _ = take_backup(s, "A", "bk1", "sha:src", "sha:stored")
    s, v = verify_restore(s, "A", "bk1", rederived_digest="sha:WRONG")
    assert v["ok"] is False
    assert v["status"] == "RESTORE_FAILED"
    assert v["reason"] == "E_RESTORE_MISMATCH"
    # and it is NOT usable for recovery
    assert usable_for_recovery(s, "A", "bk1")["usable"] is False


def test_backup_reads_are_tenant_isolated():
    s = _platform()
    s, _ = take_backup(s, "A", "bk1", "sha:src", "sha:stored")
    cross = read_backup(s, "A", "bk1", caller_tenant="B")
    absent = read_backup(s, "A", "nope", caller_tenant="A")
    assert cross["reason"] == absent["reason"] == \
        "E_CROSS_TENANT_OBSERVABILITY"


# ── invariant, purity, determinism ─────────────────────────────────────

def test_the_invariant_catches_a_forged_restorable_flag():
    s = _platform()
    s, _ = take_backup(s, "A", "bk1", "sha:src", "sha:stored")
    assert observability_invariant(s)["holds"] is True
    # hand-forge a backup marked verified whose digest never matched
    t = dict(s["tenants"]["A"])
    m = dict(t["backups"]["bk1"])
    m["status"] = "RESTORE_VERIFIED"
    m["rederived_digest"] = "sha:LIE"
    t["backups"] = {**t["backups"], "bk1": m}
    s2 = {**s, "tenants": {**s["tenants"], "A": t}}
    inv = observability_invariant(s2)
    assert inv["holds"] is False
    assert "bk1@A" in inv["false_restorable"]


def test_no_operation_mutates_its_input_state():
    s = _platform()
    frozen = ob.canon(s)
    emit_metric(s, "A", "x", "gauge", "sha:m")
    record_trace(s, "A", "span", None, "ref:1")
    raise_alert(s, "A", "r", True)
    take_backup(s, "A", "bk1", "sha:src", "sha:stored")
    assert ob.canon(s) == frozen


def test_deterministic_replay():
    def build():
        s = _platform()
        s, _ = emit_metric(s, "A", "x", "gauge", "sha:m")
        s, _ = take_backup(s, "A", "bk1", "sha:src", "sha:stored")
        s, _ = verify_restore(s, "A", "bk1", "sha:src")
        return s
    assert ob.canon(build()) == ob.canon(build())

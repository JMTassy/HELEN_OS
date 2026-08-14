"""Phase A item 1, adversarially tested on REAL state: a handle for A
dies against B's data; a forged handle is unknown however well-formed;
absence and boundary are one indistinguishable answer; tenants read
releases and can never write them; and no input state is ever mutated.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import tenant_runtime as tr
from tenant_runtime import (
    boot,
    enumerate_keys,
    isolation_invariant,
    open_handle,
    provision_tenant,
    publish_release,
    read,
    read_release,
    write,
    write_release_via_tenant,
)


def _platform():
    """Two tenants, one handle each, some data, one release."""
    s = boot()
    s, _ = provision_tenant(s, "A")
    s, _ = provision_tenant(s, "B")
    s, ra = open_handle(s, "A", ("store.read", "store.write"))
    s, rb = open_handle(s, "B", ("store.read", "store.write"))
    s, _ = write(s, ra["handle"], "A", "doc1", {"secret": "alpha"})
    s, _ = write(s, rb["handle"], "B", "doc1", {"secret": "beta"})
    s, _ = publish_release(s, "release_v3", "sha:abc")
    return s, ra["handle"], rb["handle"]


# ── provisioning and handles ───────────────────────────────────────────

def test_a_tenant_is_born_with_its_own_store_and_audit():
    s, r = provision_tenant(boot(), "A")
    assert r["ok"] is True
    assert s["tenants"]["A"]["store"] == {}
    assert s["tenants"]["A"]["audit"][-1]["kind"] == \
        "TENANT_PROVISIONED"


def test_double_provisioning_is_refused():
    s, _ = provision_tenant(boot(), "A")
    _, r = provision_tenant(s, "A")
    assert r["reason"] == "E_TENANT_EXISTS"


def test_a_handle_carries_dotted_capabilities_never_all():
    s, _ = provision_tenant(boot(), "A")
    _, r = open_handle(s, "A", ("ALL",))
    assert r["reason"] == "E_AMBIENT_AUTHORITY"
    _, r2 = open_handle(s, "A", ("write",))
    assert r2["reason"] == "E_AMBIENT_AUTHORITY"


# ── the boundary, enforced in the data path ────────────────────────────

def test_a_handle_for_A_dies_against_Bs_data():
    s, ha, _ = _platform()
    s2, r = write(s, ha, "B", "doc1", {"overwrite": True})
    assert r["ok"] is False
    assert r["reason"] == "E_TENANT_BOUNDARY"
    assert s2["tenants"]["B"]["store"]["doc1"] == {"secret": "beta"}
    assert s2["tenants"]["A"]["audit"][-1]["kind"] == \
        "BOUNDARY_REFUSED"          # logged in the ATTACKER's log


def test_a_forged_handle_is_unknown_however_well_formed():
    s, _, _ = _platform()
    forged = "0" * 16
    _, r = read(s, forged, "A", "doc1")
    assert r["reason"] == "E_UNKNOWN_HANDLE"


def test_cross_boundary_read_and_absent_key_are_one_answer():
    """The metadata law: a distinct 403 would leak key existence."""
    s, ha, _ = _platform()
    _, cross = read(s, ha, "B", "doc1")       # exists, other tenant
    _, absent = read(s, ha, "A", "nope")      # own tenant, missing
    assert cross["reason"] == absent["reason"] == "E_NOT_READABLE"
    assert cross.get("value") is None and absent.get("value") is None


def test_a_lawful_read_returns_the_value():
    s, ha, _ = _platform()
    _, r = read(s, ha, "A", "doc1")
    assert r["ok"] is True and r["value"] == {"secret": "alpha"}


def test_enumeration_only_ever_names_your_own_keys():
    s, ha, hb = _platform()
    _, ea = enumerate_keys(s, ha)
    _, eb = enumerate_keys(s, hb)
    assert ea["tenant"] == "A" and ea["keys"] == ("doc1",)
    assert eb["tenant"] == "B" and eb["keys"] == ("doc1",)
    # same key STRING, two namespaces, two different values — no leak


def test_writing_needs_the_capability_even_inside_your_tenant():
    s = boot()
    s, _ = provision_tenant(s, "A")
    s, r = open_handle(s, "A", ("store.read",))
    _, w = write(s, r["handle"], "A", "k", 1)
    assert w["reason"] == "E_CAPABILITY_MISSING"


# ── the control plane ──────────────────────────────────────────────────

def test_any_tenant_reads_a_release_and_none_writes_one():
    s, ha, hb = _platform()
    _, r1 = read_release(s, ha, "release_v3")
    _, r2 = read_release(s, hb, "release_v3")
    assert r1["digest"] == r2["digest"] == "sha:abc"
    _, w = write_release_via_tenant(s, ha, "release_v3", "sha:evil")
    assert w["reason"] == "E_CONTROL_PLANE_READ_ONLY"
    assert s["control_plane"]["release_v3"] == "sha:abc"


# ── purity and the checkable invariant ─────────────────────────────────

def test_no_operation_mutates_its_input_state():
    s, ha, _ = _platform()
    frozen = tr.canon(s)
    write(s, ha, "A", "doc2", {"x": 1})
    read(s, ha, "A", "doc1")
    enumerate_keys(s, ha)
    publish_release(s, "r4", "sha:d")
    assert tr.canon(s) == frozen        # the reducer seam, held


def test_the_isolation_invariant_is_rederivable_on_real_state():
    s, _, _ = _platform()
    v = isolation_invariant(s)
    assert v["holds"] is True
    assert v["tenants"] == ("A", "B")
    assert v["unbound_handles"] == ()


def test_audit_events_live_in_their_own_tenants_log_only():
    s, ha, _ = _platform()
    s2, _ = write(s, ha, "A", "doc2", {"x": 1})
    kinds_b = [e["kind"] for e in s2["tenants"]["B"]["audit"]]
    assert "WRITE" not in kinds_b or all(
        e["kind"] != "WRITE" or e.get("key") != "doc2"
        for e in s2["tenants"]["B"]["audit"])
    assert s2["tenants"]["A"]["audit"][-1]["kind"] == "WRITE"
    assert s2["tenants"]["A"]["audit"][-1]["value_digest"]  # digest, not value


def test_deterministic_replay():
    a1, _, _ = _platform()
    a2, _, _ = _platform()
    assert tr.canon(a1) == tr.canon(a2)

"""Phase A item 9, adversarially tested: a tenant cannot override a
core key (that is a client fork, not a configuration); config is
versioned and layered; a plugin is installed but not enabled until
admitted, holds only declared+granted capabilities, cannot claim
ambient authority, and cannot reach another tenant; and the invariant
proves every tenant's product is exactly core+overrides.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config_plugin_runtime as cp
from config_plugin_runtime import (
    admit_plugin,
    boot,
    config_invariant,
    effective_config,
    install_plugin,
    invoke_plugin,
    provision_tenant,
    set_config,
)


def _platform():
    s = boot("core-v1", {"theme": "default", "max_upload": 10})
    s, _ = provision_tenant(s, "A")
    s, _ = provision_tenant(s, "B")
    return s


# ── config: layered, never forked ──────────────────────────────────────

def test_a_tenant_override_of_a_core_key_is_a_client_fork():
    s = _platform()
    _, r = set_config(s, "A", "admission_algebra", "custom", 1)
    assert r["reason"] == "E_CLIENT_FORK"
    assert "Product_i = Core + Configuration_i" in r["law"]


def test_a_legal_override_layers_over_the_core():
    s = _platform()
    s, r = set_config(s, "A", "theme", "dark", config_version=1)
    assert r["ok"] is True and r["config_version"] == 1
    eff = effective_config(s, "A", caller_tenant="A")
    assert eff["config"]["theme"] == "dark"        # override wins
    assert eff["config"]["max_upload"] == 10        # core default kept


def test_config_must_be_versioned():
    s = _platform()
    _, r = set_config(s, "A", "theme", "dark", config_version=None)
    assert r["reason"] == "E_UNVERSIONED_CONFIG"


def test_two_tenants_share_the_core_and_differ_only_in_overrides():
    s = _platform()
    s, _ = set_config(s, "A", "theme", "dark", 1)
    s, _ = set_config(s, "B", "theme", "light", 1)
    ea = effective_config(s, "A", "A")
    eb = effective_config(s, "B", "B")
    assert ea["core_version"] == eb["core_version"] == "core-v1"
    assert ea["config"]["theme"] != eb["config"]["theme"]
    assert ea["product_identity"] != eb["product_identity"]
    assert config_invariant(s)["holds"] is True


def test_config_reads_are_tenant_isolated():
    s = _platform()
    cross = effective_config(s, "A", caller_tenant="B")
    absent = effective_config(s, "GHOST", caller_tenant="GHOST")
    assert cross["reason"] == absent["reason"] == \
        "E_PLUGIN_CROSS_TENANT"


# ── plugins: installed is not admitted ─────────────────────────────────

def test_a_plugin_cannot_claim_ambient_authority():
    s = _platform()
    _, r = install_plugin(s, "A", "p1", ["*"])
    assert r["reason"] == "E_PLUGIN_AMBIENT_AUTHORITY"
    _, r2 = install_plugin(s, "A", "p1", ["store"])   # not dotted
    assert r2["reason"] == "E_PLUGIN_AMBIENT_AUTHORITY"


def test_installed_is_not_enabled():
    s = _platform()
    s, r = install_plugin(s, "A", "p1", ["store.read", "store.write"])
    assert r["status"] == "INSTALLED"
    inv = invoke_plugin(s, "A", "p1", "store.read")
    assert inv["reason"] == "E_PLUGIN_UNADMITTED"


def test_admission_grants_only_a_subset_of_declared():
    s = _platform()
    s, _ = install_plugin(s, "A", "p1", ["store.read"])
    _, r = admit_plugin(s, "A", "p1", ["store.write"], admitter="gamma")
    assert r["reason"] == "E_PLUGIN_UNDECLARED_CAPABILITY"
    s, ok = admit_plugin(s, "A", "p1", ["store.read"], admitter="gamma")
    assert ok["status"] == "ADMITTED"


def test_an_admitted_plugin_runs_only_within_its_grant_and_tenant():
    s = _platform()
    s, _ = install_plugin(s, "A", "p1", ["store.read", "store.write"])
    s, _ = admit_plugin(s, "A", "p1", ["store.read"], admitter="gamma")
    ok = invoke_plugin(s, "A", "p1", "store.read")
    assert ok["ok"] is True and ok["sandboxed_to"] == "A"
    # declared but not granted
    ng = invoke_plugin(s, "A", "p1", "store.write")
    assert ng["reason"] == "E_PLUGIN_CAPABILITY_NOT_GRANTED"
    # cross-tenant target
    xt = invoke_plugin(s, "A", "p1", "store.read", target_tenant="B")
    assert xt["reason"] == "E_PLUGIN_CROSS_TENANT"


def test_admission_needs_an_admitter():
    s = _platform()
    s, _ = install_plugin(s, "A", "p1", ["store.read"])
    _, r = admit_plugin(s, "A", "p1", ["store.read"], admitter=None)
    assert r["reason"] == "E_PLUGIN_UNADMITTED"


# ── the invariant ──────────────────────────────────────────────────────

def test_the_invariant_catches_a_hand_forged_core_fork():
    s = _platform()
    s, _ = set_config(s, "A", "theme", "dark", 1)
    assert config_invariant(s)["holds"] is True
    # forge an override onto a core-locked key, bypassing set_config
    t = dict(s["tenants"]["A"])
    t["overrides"] = {**t["overrides"], "reducer_seam": "hacked"}
    s2 = {**s, "tenants": {**s["tenants"], "A": t}}
    inv = config_invariant(s2)
    assert inv["holds"] is False
    assert "A" in inv["client_forks"]


def test_no_operation_mutates_its_input_state():
    s = _platform()
    frozen = cp.canon(s)
    set_config(s, "A", "theme", "dark", 1)
    install_plugin(s, "A", "p1", ["store.read"])
    assert cp.canon(s) == frozen


def test_deterministic_replay():
    def build():
        s = _platform()
        s, _ = set_config(s, "A", "theme", "dark", 1)
        s, _ = install_plugin(s, "A", "p1", ["store.read"])
        s, _ = admit_plugin(s, "A", "p1", ["store.read"], "gamma")
        return s
    assert cp.canon(build()) == cp.canon(build())

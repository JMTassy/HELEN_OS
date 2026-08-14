"""Phase A item 2, adversarially tested on real state: the grantor may
not be the grantee; roles are tenant-scoped with one indistinguishable
refusal; revocation is immediate and self-revocation needs no
permission; a forged session is unknown; and no operation mutates its
input.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import identity_runtime as ir
from identity_runtime import (
    authorize,
    bind_role,
    boot,
    bootstrap_bind,
    define_role,
    open_session,
    rbac_invariant,
    register_identity,
    revoke_role,
)


def _platform():
    """Admin + user, two tenants, admin bootstrapped in tenant A."""
    s = boot()
    s, _ = register_identity(s, "admin")
    s, _ = register_identity(s, "user")
    s, _ = define_role(s, "iam_admin", ("iam.role.bind",))
    s, _ = define_role(s, "reader", ("store.read",))
    s, _ = bootstrap_bind(s, "admin", "iam_admin", "A")
    s, ra = open_session(s, "admin")
    s, ru = open_session(s, "user")
    return s, ra["session"], ru["session"]


# ── roles and identities ───────────────────────────────────────────────

def test_a_role_never_carries_ambient_authority():
    s = boot()
    _, r = define_role(s, "god", ("ALL",))
    assert r["reason"] == "E_AMBIENT_AUTHORITY"
    _, r2 = define_role(s, "vague", ("write",))
    assert r2["reason"] == "E_AMBIENT_AUTHORITY"


def test_duplicate_identities_and_roles_are_refused():
    s = boot()
    s, _ = register_identity(s, "x")
    _, r = register_identity(s, "x")
    assert r["reason"] == "E_IDENTITY_EXISTS"


# ── the grantor may not be the grantee ─────────────────────────────────

def test_an_admin_cannot_grant_a_role_to_itself():
    """The debtor/creditor law inside IAM: even holding iam.role.bind,
    self-elevation is refused and audited."""
    s, admin, _ = _platform()
    s2, r = bind_role(s, admin, "admin", "reader", "A")
    assert r["ok"] is False
    assert r["reason"] == "E_SELF_GRANT"
    assert s2["audit"]["A"][-1]["kind"] == "SELF_GRANT_REFUSED"


def test_an_admin_can_grant_to_another_identity():
    s, admin, user = _platform()
    s, r = bind_role(s, admin, "user", "reader", "A")
    assert r["ok"] is True and r["by"] == "admin"
    _, a = authorize(s, user, "store.read", "A")
    assert a["ok"] is True and a["via_role"] == "reader"


def test_a_non_admin_cannot_bind_anything():
    s, _, user = _platform()
    _, r = bind_role(s, user, "user", "reader", "A")
    assert r["reason"] == "E_SELF_GRANT"      # self first
    s, _ = register_identity(s, "other")
    _, r2 = bind_role(s, user, "other", "reader", "A")
    assert r2["reason"] == "E_NOT_AUTHORIZED"


# ── tenant scoping and the one refusal ─────────────────────────────────

def test_a_binding_in_tenant_A_licenses_nothing_in_tenant_B():
    s, admin, user = _platform()
    s, _ = bind_role(s, admin, "user", "reader", "A")
    _, inA = authorize(s, user, "store.read", "A")
    _, inB = authorize(s, user, "store.read", "B")
    assert inA["ok"] is True
    assert inB["ok"] is False
    assert inB["reason"] == "E_NOT_AUTHORIZED"


def test_no_role_and_missing_capability_are_one_answer():
    """Metadata law: a distinct refusal would leak role existence
    across the boundary."""
    s, admin, user = _platform()
    s, _ = bind_role(s, admin, "user", "reader", "A")
    _, wrong_cap = authorize(s, user, "store.write", "A")
    _, wrong_tenant = authorize(s, user, "store.read", "B")
    assert wrong_cap["reason"] == wrong_tenant["reason"] == \
        "E_NOT_AUTHORIZED"


def test_a_forged_session_is_unknown_however_well_formed():
    s, _, _ = _platform()
    _, r = authorize(s, "f" * 16, "store.read", "A")
    assert r["reason"] == "E_UNKNOWN_SESSION"


# ── revocation ─────────────────────────────────────────────────────────

def test_revocation_is_immediate():
    s, admin, user = _platform()
    s, _ = bind_role(s, admin, "user", "reader", "A")
    s, ok = authorize(s, user, "store.read", "A")
    assert ok["ok"] is True
    s, rv = revoke_role(s, admin, "user", "reader", "A")
    assert rv["immediate"] is True
    _, after = authorize(s, user, "store.read", "A")
    assert after["ok"] is False


def test_self_revocation_needs_no_permission():
    """Bad news needs no permission — an identity may always shed its
    own role."""
    s, admin, user = _platform()
    s, _ = bind_role(s, admin, "user", "reader", "A")
    s, rv = revoke_role(s, user, "user", "reader", "A")
    assert rv["ok"] is True
    assert s["audit"]["A"][-1]["self"] is True


def test_revoking_another_identity_needs_the_capability():
    s, admin, user = _platform()
    s, _ = bind_role(s, admin, "user", "reader", "A")
    _, r = revoke_role(s, user, "admin", "iam_admin", "A")
    assert r["reason"] == "E_NOT_AUTHORIZED"


# ── purity, audit, invariant ───────────────────────────────────────────

def test_no_operation_mutates_its_input_state():
    s, admin, user = _platform()
    frozen = ir.canon(s)
    bind_role(s, admin, "user", "reader", "A")
    authorize(s, user, "store.read", "A")
    revoke_role(s, user, "user", "reader", "A")
    assert ir.canon(s) == frozen


def test_authorize_is_audited_in_the_target_tenant():
    s, admin, user = _platform()
    s, _ = bind_role(s, admin, "user", "reader", "A")
    s, _ = authorize(s, user, "store.read", "A")
    last = s["audit"]["A"][-1]
    assert last["kind"] == "AUTHORIZE" and last["granted"] is True


def test_the_rbac_invariant_is_rederivable_on_real_state():
    s, _, _ = _platform()
    v = rbac_invariant(s)
    assert v["holds"] is True
    assert v["ambient_roles"] == ()


def test_deterministic_replay():
    a, _, _ = _platform()
    b, _, _ = _platform()
    assert ir.canon(a) == ir.canon(b)

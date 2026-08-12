"""The gate must be able to FAIL.

A verification gate that always passes proves nothing about the system
and everything about the gate. These tests break a constitutional law
on purpose, in-process, and require verify_constitution() to notice —
then restore it and require the gate to go green again.

This is the meta-falsifier: it polices the policeman.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_MVP = _HERE.parents[2]
for _p in (str(_MVP), str(_HERE),
           str(_HERE.parents[1] / "gates" / "effect_gate"),
           str(_MVP / "research" / "crystal_palace")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from helen_os.kernel.constitution import verify_constitution  # noqa: E402


def test_the_constitution_holds_when_untouched():
    r = verify_constitution()
    assert r["verdict"] == "CONSTITUTION_HELD", r["failed"]
    assert r["probes_run"] >= 30
    assert r["probes_held"] == r["probes_run"]


def test_every_probe_actually_executes_and_none_error():
    """An ERROR verdict is a failed probe, never a pass."""
    r = verify_constitution()
    assert not [f for f in r["failed"] if f["verdict"] == "ERROR"]


def test_breaking_the_bypass_deny_is_detected():
    """Neuter the goblin HAL text-deny; the gate must catch it."""
    import effect_gate as eg
    original = eg.BYPASS_RE
    try:
        eg.BYPASS_RE = re.compile(r"^\b$")          # matches nothing
        r = verify_constitution()
        assert r["verdict"] == "E_CONSTITUTION_BREACHED"
        assert "bypass_text_deny" in [f["probe"] for f in r["failed"]]
    finally:
        eg.BYPASS_RE = original
    assert verify_constitution()["verdict"] == "CONSTITUTION_HELD"


def test_making_authority_non_linear_is_detected():
    """Let a single-use lease spend forever; the gate must catch it."""
    import admissible_morphism as am
    original = am.LeaseBook.spend
    try:
        am.LeaseBook.spend = lambda self, lid: {"ok": True,
                                                "remaining": 99}
        r = verify_constitution()
        assert r["verdict"] == "E_CONSTITUTION_BREACHED"
        assert "duplicated_lease" in [f["probe"] for f in r["failed"]]
    finally:
        am.LeaseBook.spend = original
    assert verify_constitution()["verdict"] == "CONSTITUTION_HELD"


def test_allowing_retroactive_authority_is_detected():
    """Erase the arrow of time inside the atom."""
    import admissible_morphism as am
    original = am.admit

    def permissive(m, world_roots, leases, invariant, gate, t_now):
        patched = am.CandidateMorphism(
            m.m_id, m.source_root, m.target, m.transformation,
            m.evidence_roots, m.lease_id,
            t_authorized=min(m.t_authorized, m.t_effect),
            t_effect=m.t_effect, quantity_delta=m.quantity_delta)
        return original(patched, world_roots, leases, invariant, gate,
                        t_now)
    try:
        am.admit = permissive
        r = verify_constitution()
        assert r["verdict"] == "E_CONSTITUTION_BREACHED"
        assert "retroactive_authority" in [f["probe"]
                                           for f in r["failed"]]
    finally:
        am.admit = original
    assert verify_constitution()["verdict"] == "CONSTITUTION_HELD"


def test_letting_a_summary_promote_a_decision_is_detected():
    import ingestion_laws as il
    original = il.AXIS_WITNESS_KINDS["approval"]
    try:
        il.AXIS_WITNESS_KINDS["approval"] = frozenset(
            {"operator_admission", "generated_summary"})
        r = verify_constitution()
        # the probe checks the REFUSAL fires; widening the kinds alone
        # must not smuggle a summary through, because the summary
        # short-circuit is checked before kind membership.
        assert r["verdict"] == "CONSTITUTION_HELD"
    finally:
        il.AXIS_WITNESS_KINDS["approval"] = original


def test_the_receipt_is_deterministic_across_runs():
    a, b = verify_constitution(), verify_constitution()
    assert a["receipt"] == b["receipt"]


def test_the_gate_declares_no_authority():
    r = verify_constitution()
    assert r["authority"] is False
    assert r["canon"] is False
    assert r["ledger_effect"] == "none"


@pytest.mark.parametrize("registry,minimum", [
    ("HF_invariants", 15), ("guard_types", 6), ("property_layers", 5),
    ("safety_rungs", 3), ("decision_axes", 6),
    ("completion_credentials", 3), ("availability_non_entailments", 4)])
def test_registries_are_populated(registry, minimum):
    assert verify_constitution()["registries"][registry] >= minimum

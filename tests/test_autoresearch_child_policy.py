"""Tests for the five-way terminal classification and the child policy.

Law under test:
  NO CHILD EPOCH WITHOUT A NEW DISCRIMINATOR.
  spawn(c) => new_discriminator(c) AND falsifier(c) AND parent(c); else REJECT_CHILD.
  DEAD/QUOTIENTED -> STOP · IMPLEMENTATION_GAP -> WORK · RETAINED_CANDIDATE -> VERIFY_OPERATOR
  · NEW_FRONTIER -> MAY_SPAWN. Legacy packets without terminal fields stay valid.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from temple.autoresearch.autoresearch_policy import (
    TERMINAL_CLASSES, SPAWN_POLICY, spawn_policy, validate_child, validate_packet,
)


def base(**k):
    d = {"schema": "AUTORESEARCH_PACKET_V1", "packet_id": "AR-x", "source_refs": [],
         "finding_type": "proposal", "summary": "s", "evidence": ["e"], "risk_flags": [],
         "recommended_action": "ROUTE_TO_OPERATOR_FOR_REVIEW", "authority": False,
         "sovereign": False, "canon": False, "ledger_effect": "none", "reducer_required": True}
    d.update(k)
    return d


PARENT = base(packet_id="AR-p", epoch="E1", terminal_class="NEW_FRONTIER", discriminators=["d1"])
CHILD = base(packet_id="AR-c", epoch="E2", parent_epoch="E1", discriminators=["d1", "d2"], falsifier="grep -c foo == 0")


def test_five_classes_and_policy_table():
    assert TERMINAL_CLASSES == {"DEAD", "QUOTIENTED", "IMPLEMENTATION_GAP", "RETAINED_CANDIDATE", "NEW_FRONTIER"}
    assert SPAWN_POLICY == {"DEAD": "STOP", "QUOTIENTED": "STOP", "IMPLEMENTATION_GAP": "WORK",
                            "RETAINED_CANDIDATE": "VERIFY_OPERATOR", "NEW_FRONTIER": "MAY_SPAWN"}
    assert spawn_policy(None) == "STOP" and spawn_policy("bogus") == "STOP"


def test_good_child_passes():
    ok, errs = validate_child(CHILD, PARENT)
    assert ok and errs == []


def test_verification_child_rejected_no_new_discriminator():
    ok, errs = validate_child({**CHILD, "discriminators": ["d1"]}, PARENT)
    assert not ok and any("no new discriminator" in e and "receipt to the parent" in e for e in errs)


def test_child_without_discriminators_rejected():
    ok, errs = validate_child({**CHILD, "discriminators": []}, PARENT)
    assert not ok and any("declares no discriminators" in e for e in errs)


def test_child_without_falsifier_rejected():
    c = dict(CHILD); del c["falsifier"]
    ok, errs = validate_child(c, PARENT)
    assert not ok and any("declares no falsifier" in e for e in errs)


def test_child_must_name_parent():
    ok, errs = validate_child({**CHILD, "parent_epoch": "E7"}, PARENT)
    assert not ok and any("does not name this parent" in e for e in errs)
    ok, _ = validate_child({**CHILD, "parent_epoch": None, "parent_id": "AR-p"}, PARENT)
    assert ok


def test_terminal_classes_gate_spawning():
    for cls, verdict in (("DEAD", "STOP"), ("QUOTIENTED", "STOP"), ("IMPLEMENTATION_GAP", "WORK")):
        ok, errs = validate_child(CHILD, {**PARENT, "terminal_class": cls})
        assert not ok and any(verdict in e for e in errs), cls
    ok, _ = validate_child(CHILD, {**PARENT, "terminal_class": "RETAINED_CANDIDATE"})
    assert ok
    ok, errs = validate_child(CHILD, {k: v for k, v in PARENT.items() if k != "terminal_class"})
    assert not ok and any("no terminal_class" in e for e in errs)


def test_every_error_is_prefixed_reject_child():
    _, errs = validate_child({**CHILD, "discriminators": [], "falsifier": ""}, {**PARENT, "terminal_class": "DEAD"})
    assert errs and all(e.startswith("REJECT_CHILD") for e in errs)


def test_validate_packet_accepts_legacy_and_rejects_malformed_terminal_fields():
    ok, _ = validate_packet(base())
    assert ok
    ok, _ = validate_packet(base(terminal_class="NEW_FRONTIER", discriminators=["d"], falsifier="f"))
    assert ok
    ok, errs = validate_packet(base(terminal_class="MAYBE"))
    assert not ok and any("terminal_class" in e for e in errs)
    ok, errs = validate_packet(base(discriminators="d1"))
    assert not ok and any("discriminators" in e for e in errs)
    ok, errs = validate_packet(base(falsifier=""))
    assert not ok and any("falsifier" in e for e in errs)

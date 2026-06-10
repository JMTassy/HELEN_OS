#!/usr/bin/env python3
"""
Schema/dispatcher consistency test (NEW — exists in neither mirror nor SOT
before this patch).

Verifies the CRITICAL FIX: the guard's certifiable schema must equal the
actual dispatcher keys, and every declared-but-undispatchable action must be
classified UNBOUND / TRACE_ONLY. The guard must never certify an action the
dispatcher cannot dispatch.

Two layers:

  1. SOT-internal invariants — always run. RUNTIME_VALID_ACTIONS ==
     DISPATCHED_ACTIONS, disjoint from UNBOUND_ACTIONS, exact frozen
     contents.

  2. Cross-check against the live mirror dispatcher
     (~/.helen/computer_skill_handler.py) — AST-extracts the real
     `if action == "...":` dispatch branches and the declared
     RUNTIME_VALID_ACTIONS literal, then asserts:
       - SOT DISPATCHED_ACTIONS == actual dispatch keys
       - SOT UNBOUND_ACTIONS == (mirror declared − dispatch keys)
     Skipped (with reason) if the mirror file is absent. Mirror location is
     overridable via HELEN_RUNTIME_HOME for promoted runtimes.

Read-only with respect to the mirror: the mirror file is parsed, never
imported (importing would pull in helen_runtime_client) and never modified.
"""
import ast
import os
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from action_preflight_guard import (
    DISPATCHED_ACTIONS,
    RUNTIME_VALID_ACTIONS,
    UNBOUND_ACTIONS,
)

_RUNTIME_HOME = pathlib.Path(
    os.environ.get("HELEN_RUNTIME_HOME", str(pathlib.Path.home() / ".helen"))
)
_HANDLER = _RUNTIME_HOME / "computer_skill_handler.py"

# Frozen expectation, per 2026-06-10 audit of the mirror dispatcher.
_EXPECTED_DISPATCHED = frozenset({
    "screenshot", "get_window_list", "focus_window", "wait",
    "key_combo", "focus_screenshot_list", "get_clipboard",
    "send_notification", "open_app", "type_text",
})
_EXPECTED_UNBOUND = frozenset({
    "read_file", "run_command", "set_clipboard", "write_file", "web_search",
})


# ─── Layer 1: SOT-internal invariants (always run) ────────────────────────────

class TestGuardSchemaInvariants:
    def test_runtime_valid_equals_dispatched(self):
        """THE critical fix: certifiable schema == dispatcher keys."""
        assert RUNTIME_VALID_ACTIONS == DISPATCHED_ACTIONS

    def test_dispatched_and_unbound_disjoint(self):
        assert DISPATCHED_ACTIONS.isdisjoint(UNBOUND_ACTIONS)

    def test_guard_never_certifies_unbound(self):
        assert RUNTIME_VALID_ACTIONS.isdisjoint(UNBOUND_ACTIONS)

    def test_dispatched_exact_contents(self):
        assert DISPATCHED_ACTIONS == _EXPECTED_DISPATCHED
        assert len(DISPATCHED_ACTIONS) == 10

    def test_unbound_exact_contents(self):
        assert UNBOUND_ACTIONS == _EXPECTED_UNBOUND
        assert len(UNBOUND_ACTIONS) == 5

    def test_union_covers_legacy_declared_schema(self):
        """Dispatched ∪ Unbound == the 15 actions the mirror declared."""
        assert len(DISPATCHED_ACTIONS | UNBOUND_ACTIONS) == 15


# ─── AST extraction helpers ───────────────────────────────────────────────────

def _extract_dispatch_keys(tree: ast.Module) -> frozenset:
    """Collect string constants compared against `action` inside
    execute_computer_skill's if-dispatch chain."""
    keys = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "execute_computer_skill":
            for sub in ast.walk(node):
                if isinstance(sub, ast.Compare):
                    left = sub.left
                    if isinstance(left, ast.Name) and left.id == "action":
                        for comp in sub.comparators:
                            if isinstance(comp, ast.Constant) and isinstance(comp.value, str):
                                keys.add(comp.value)
    return frozenset(keys)


def _extract_declared_schema(tree: ast.Module) -> frozenset:
    """Collect the RUNTIME_VALID_ACTIONS = frozenset({...}) literal."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
            if "RUNTIME_VALID_ACTIONS" in targets:
                values = set()
                for sub in ast.walk(node.value):
                    if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                        values.add(sub.value)
                return frozenset(values)
    return frozenset()


# ─── Layer 2: cross-check against live mirror dispatcher ─────────────────────

@pytest.mark.skipif(
    not _HANDLER.is_file(),
    reason=f"mirror dispatcher not found at {_HANDLER} "
           "(set HELEN_RUNTIME_HOME to override)",
)
class TestMirrorDispatcherCrossCheck:
    @pytest.fixture(scope="class")
    def tree(self):
        return ast.parse(_HANDLER.read_text(encoding="utf-8"))

    def test_dispatch_keys_match_sot_dispatched(self, tree):
        keys = _extract_dispatch_keys(tree)
        assert keys, "could not extract any dispatch keys — parser drift?"
        assert keys == DISPATCHED_ACTIONS, (
            f"dispatcher drift: dispatcher-only={sorted(keys - DISPATCHED_ACTIONS)} "
            f"sot-only={sorted(DISPATCHED_ACTIONS - keys)}"
        )

    def test_declared_minus_dispatched_equals_unbound(self, tree):
        """The mirror's 15-action declared schema minus its 10 real dispatch
        branches must be exactly the SOT UNBOUND classification."""
        declared = _extract_declared_schema(tree)
        keys = _extract_dispatch_keys(tree)
        assert declared, "could not extract mirror RUNTIME_VALID_ACTIONS"
        assert declared - keys == UNBOUND_ACTIONS, (
            f"unbound drift: declared-minus-dispatched="
            f"{sorted(declared - keys)} vs SOT UNBOUND={sorted(UNBOUND_ACTIONS)}"
        )

    def test_no_dispatch_key_outside_declared(self, tree):
        declared = _extract_declared_schema(tree)
        keys = _extract_dispatch_keys(tree)
        assert keys <= declared, (
            f"dispatcher handles undeclared actions: {sorted(keys - declared)}"
        )

    def test_mirror_mismatch_detected(self, tree):
        """Regression detector: the mirror's declared schema is KNOWN to be
        wider than its dispatcher (the original bug). If the mirror is ever
        fixed so declared == dispatched, UNBOUND_ACTIONS here must shrink to
        match — this test flags that reconciliation point."""
        declared = _extract_declared_schema(tree)
        keys = _extract_dispatch_keys(tree)
        if declared == keys:
            assert UNBOUND_ACTIONS == frozenset(), (
                "mirror dispatcher now implements all declared actions; "
                "update SOT UNBOUND_ACTIONS to empty and promote those "
                "actions to DISPATCHED_ACTIONS"
            )
        else:
            # Current known state: 15 declared, 10 dispatched.
            assert declared - keys == UNBOUND_ACTIONS

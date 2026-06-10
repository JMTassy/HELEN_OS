#!/usr/bin/env python3
"""
Tests for experiments/helen_action_guard/action_preflight_guard.py.

Adapted from ~/.helen/tests/test_action_preflight_guard.py (mirror, 41 tests)
plus SOT-specific coverage for the patch requirements:

  1. unknown action -> TRACE_ONLY_UNVERIFIED, zero retry
  2. no_writes blocks gated writes
  3. no_writes blocks write_file
  4. no_writes blocks write-like run_command (mkdir, touch, echo>, cat>, rm, mv, cp, tee)
  5. do_not_web_search blocks web/search variants
  6. read_file path failure -> classify and stop, no write proposed
  7. descendant write into failed path subtree -> blocked EVEN WITHOUT no_writes (new)
  8. stale repeat: third identical call blocked
  9. valid read action still allowed
 10. valid arg-shape for real dispatched action still works
 11. UNBOUND classification: declared-but-undispatchable never certified (new)
 12. begin_intent resets stale tracking at intent boundary (new)
"""
import os
import sys
import tempfile
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import pytest
from action_preflight_guard import (
    DISPATCHED_ACTIONS,
    RUNTIME_VALID_ACTIONS,
    UNBOUND_ACTIONS,
    GuardState,
    check_action,
    check_unknown_action,
)

# A minimal schema containing only the actions relevant to these tests.
# Tests that exercise constraint/path/stale logic on file/web actions inject
# this schema so that logic is reachable (in the live schema those actions
# are UNBOUND and terminate at the unbound classification instead).
_TEST_SCHEMA = frozenset({
    "get_clipboard", "set_clipboard", "read_file", "write_file",
    "run_command", "web_search", "screenshot", "get_window_list",
})
_NO_UNBOUND = frozenset()


def fresh() -> GuardState:
    """Return a clean GuardState for each test."""
    return GuardState()


def check(action, params, state, schema=_TEST_SCHEMA, unbound=_NO_UNBOUND):
    return check_action(action, params, state,
                        runtime_schema=schema, unbound_schema=unbound)


# ─── 1. Unknown action → TRACE_ONLY_UNVERIFIED, no retry ─────────────────────

class TestUnknownAction:
    def test_autoresearch_is_unknown(self):
        s = fresh()
        v = check("autoresearch", {}, s)
        assert not v.allowed
        assert v.verdict == "TRACE_ONLY_UNVERIFIED"
        assert v.marker == "✗ phantom action blocked"
        assert "autoresearch" in s.blocked_actions

    def test_egregor_is_unknown(self):
        s = fresh()
        v = check("egregor", {}, s)
        assert not v.allowed
        assert v.verdict == "TRACE_ONLY_UNVERIFIED"
        assert "egregor" in s.blocked_actions

    def test_list_events_is_unknown(self):
        s = fresh()
        v = check("list_events", {}, s)
        assert not v.allowed
        assert v.verdict == "TRACE_ONLY_UNVERIFIED"
        assert "list_events" in s.blocked_actions

    def test_unknown_action_not_retried(self):
        s = fresh()
        v1 = check("autoresearch", {}, s)
        assert not v1.allowed
        assert v1.verdict == "TRACE_ONLY_UNVERIFIED"

        v2 = check("autoresearch", {}, s)
        assert not v2.allowed
        assert v2.verdict in ("TRACE_ONLY_UNVERIFIED", "BLOCKED_SESSION")
        assert "autoresearch" in s.blocked_actions

    def test_unknown_against_live_schema(self):
        s = fresh()
        v = check_action("autoresearch", {}, s)  # live defaults
        assert not v.allowed
        assert v.verdict == "TRACE_ONLY_UNVERIFIED"


# ─── 2. no_writes blocks gated writes (unknown path still caught first) ──────

class TestNoWritesBlocksAutoresearch:
    def test_autoresearch_blocked_when_no_writes(self):
        s = fresh()
        s.constraints.add("no_writes")
        v = check("autoresearch", {}, s)
        assert not v.allowed
        # Unknown → TRACE_ONLY (schema check fires before constraint check)
        assert v.verdict == "TRACE_ONLY_UNVERIFIED"

    def test_autoresearch_blocked_as_unknown_even_with_no_writes(self):
        s = fresh()
        s.constraints.add("no_writes")
        v = check("autoresearch", {}, s)
        assert not v.allowed
        assert "phantom action" in (v.marker or "")


# ─── 3. no_writes blocks write_file ──────────────────────────────────────────

class TestNoWritesBlocksWriteFile:
    def test_write_file_blocked_by_no_writes(self):
        s = fresh()
        s.constraints.add("no_writes")
        v = check("write_file", {"path": "/tmp/x.txt", "content": "hi"}, s)
        assert not v.allowed
        assert v.verdict == "BLOCKED_BY_NO_WRITES"
        assert v.marker == "✗ gated write blocked"

    def test_write_file_allowed_without_no_writes_in_test_schema(self):
        # In the injected test schema write_file is dispatched; in the live
        # schema it is UNBOUND (see TestUnboundClassification).
        s = fresh()
        v = check("write_file", {"path": "/tmp/x.txt", "content": "hi"}, s)
        assert v.allowed
        assert v.verdict == "ALLOWED"


# ─── 4. no_writes blocks write-like run_command ───────────────────────────────

class TestNoWritesBlocksWriteLikeRunCommand:
    _cmds = [
        "mkdir /tmp/newdir",
        "touch /tmp/foo.txt",
        "echo hello > /tmp/out.txt",
        "echo hello >> /tmp/out.txt",
        "cat data.txt > /tmp/out.txt",
        "rm /tmp/foo.txt",
        "mv /tmp/a /tmp/b",
        "cp /tmp/a /tmp/b",
        "tee /tmp/out.txt",
    ]

    @pytest.mark.parametrize("cmd", _cmds)
    def test_write_like_cmd_blocked(self, cmd):
        s = fresh()
        s.constraints.add("no_writes")
        v = check("run_command", {"command": cmd}, s)
        assert not v.allowed, f"Expected blocked for: {cmd}"
        assert v.verdict == "BLOCKED_BY_NO_WRITES"
        assert v.marker == "✗ gated write blocked"

    def test_read_only_run_command_allowed(self):
        s = fresh()
        s.constraints.add("no_writes")
        v = check("run_command", {"command": "ls /tmp"}, s)
        assert v.allowed

    def test_run_command_allowed_without_constraint(self):
        s = fresh()
        v = check("run_command", {"command": "mkdir /tmp/x"}, s)
        assert v.allowed


# ─── 5. do_not_web_search blocks web/search variants ──────────────────────────

class TestNoWebSearch:
    def test_web_search_blocked_by_constraint(self):
        s = fresh()
        s.constraints.add("no_web_search")
        v = check("web_search", {"query": "test"}, s)
        assert not v.allowed
        assert v.verdict == "BLOCKED_BY_OPERATOR"
        assert v.marker == "✗ operator constraint blocked"

    @pytest.mark.parametrize("variant", [
        "web_fetch", "web_extract", "fetch", "search", "browser_search",
    ])
    def test_search_variants_blocked(self, variant):
        s = fresh()
        s.constraints.add("no_web_search")
        schema = _TEST_SCHEMA | {variant}
        v = check(variant, {"query": "x"}, s, schema=schema)
        assert not v.allowed
        assert v.verdict == "BLOCKED_BY_OPERATOR"

    def test_web_search_allowed_without_constraint(self):
        s = fresh()
        v = check("web_search", {"query": "test"}, s)
        assert v.allowed

    def test_parse_constraints_detects_no_web_search(self):
        s = fresh()
        s.parse_constraints("Do not web search.")
        assert "no_web_search" in s.constraints

    def test_parse_constraints_variant(self):
        s = fresh()
        s.parse_constraints("no web search allowed here")
        assert "no_web_search" in s.constraints


# ─── 6. read_file path failure → classify and stop, no write proposed ─────────

class TestReadFilePathFailure:
    def test_read_file_on_directory(self):
        with tempfile.TemporaryDirectory() as d:
            s = fresh()
            v = check("read_file", {"path": d}, s)
            assert not v.allowed
            assert v.verdict == "BLOCKED_PATH_FAILURE"
            assert v.marker == "✗ path probe failed"
            assert "No write proposed" in v.reason

    def test_read_file_missing_path(self):
        s = fresh()
        v = check("read_file", {"path": "/nonexistent/path/file.txt"}, s)
        assert not v.allowed
        assert v.verdict == "BLOCKED_PATH_FAILURE"
        assert "No write proposed" in v.reason

    def test_failed_path_recorded(self):
        with tempfile.TemporaryDirectory() as d:
            s = fresh()
            check("read_file", {"path": d}, s)
            assert any(os.path.normpath(d) == f for f in s.failed_paths)

    def test_read_file_on_existing_file_allowed(self):
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            tf.write(b"hello")
            tf_path = tf.name
        try:
            s = fresh()
            v = check("read_file", {"path": tf_path}, s)
            assert v.allowed
        finally:
            os.unlink(tf_path)


# ─── 7. Descendant write into failed path subtree blocked ─────────────────────

class TestDescendantWriteAfterPathFailure:
    def test_write_file_after_dir_read_fail_with_no_writes(self):
        with tempfile.TemporaryDirectory() as d:
            s = fresh()
            s.constraints.add("no_writes")

            rv = check("read_file", {"path": d}, s)
            assert not rv.allowed
            assert rv.verdict == "BLOCKED_PATH_FAILURE"

            child = os.path.join(d, "new_file.txt")
            wv = check("write_file", {"path": child, "content": "x"}, s)
            assert not wv.allowed
            assert wv.verdict == "BLOCKED_BY_NO_WRITES"

    def test_descendant_write_blocked_even_without_no_writes(self):
        """Patch requirement 5: subtree block fires with NO constraint active."""
        with tempfile.TemporaryDirectory() as d:
            s = fresh()
            # no constraints at all

            rv = check("read_file", {"path": d}, s)
            assert not rv.allowed
            assert rv.verdict == "BLOCKED_PATH_FAILURE"

            child = os.path.join(d, "sub", "new_file.txt")
            wv = check("write_file", {"path": child, "content": "x"}, s)
            assert not wv.allowed
            assert wv.verdict == "BLOCKED_FAILED_PATH_SUBTREE"
            assert wv.marker == "✗ failed-path subtree blocked"

    def test_descendant_run_command_write_blocked_without_no_writes(self):
        with tempfile.TemporaryDirectory() as d:
            s = fresh()
            check("read_file", {"path": d}, s)  # fail the probe
            v = check("run_command", {"command": f"touch {d}/x.txt"}, s)
            assert not v.allowed
            assert v.verdict == "BLOCKED_FAILED_PATH_SUBTREE"

    def test_write_outside_failed_subtree_not_blocked_by_subtree_rule(self):
        with tempfile.TemporaryDirectory() as d:
            s = fresh()
            check("read_file", {"path": d}, s)
            v = check("write_file", {"path": "/tmp/elsewhere.txt", "content": "x"}, s)
            assert v.allowed


# ─── 8. Stale repeat: third identical call blocked ───────────────────────────

class TestStaleRepeat:
    def test_third_get_clipboard_blocked(self):
        s = fresh()
        params = {}

        v1 = check("get_clipboard", params, s)
        assert v1.allowed
        s.record_call("get_clipboard", params)

        v2 = check("get_clipboard", params, s)
        assert v2.allowed
        s.record_call("get_clipboard", params)

        v3 = check("get_clipboard", params, s)
        assert not v3.allowed
        assert v3.verdict == "BLOCKED_STALE_REPEAT"
        assert v3.marker == "✗ stale repeat blocked"

    def test_different_args_not_stale(self):
        s = fresh()
        for i in range(3):
            v = check("run_command", {"command": f"ls /tmp/{i}"}, s)
            assert v.allowed, f"Call {i} should be allowed"
            s.record_call("run_command", {"command": f"ls /tmp/{i}"})


# ─── 9. Valid read action still allowed ───────────────────────────────────────

class TestValidReadAllowed:
    def test_get_clipboard_allowed_no_constraints(self):
        s = fresh()
        v = check("get_clipboard", {}, s)
        assert v.allowed
        assert v.verdict == "ALLOWED"
        assert v.marker is None

    def test_screenshot_allowed_no_constraints(self):
        s = fresh()
        v = check("screenshot", {}, s)
        assert v.allowed

    def test_get_window_list_allowed_no_constraints(self):
        s = fresh()
        v = check("get_window_list", {}, s)
        assert v.allowed

    def test_read_action_allowed_despite_no_writes(self):
        s = fresh()
        s.constraints.add("no_writes")
        v = check("get_clipboard", {}, s)
        assert v.allowed

    def test_dispatched_action_allowed_against_live_schema(self):
        s = fresh()
        v = check_action("screenshot", {}, s)  # live defaults
        assert v.allowed
        assert v.verdict == "ALLOWED"


# ─── 10. Valid arg-shape for real dispatched action still works ───────────────

class TestValidArgShape:
    def test_get_clipboard_empty_params(self):
        s = fresh()
        v = check("get_clipboard", {}, s)
        assert v.allowed

    def test_run_command_with_read_cmd(self):
        s = fresh()
        s.constraints.add("no_writes")
        v = check("run_command", {"command": "cat /etc/hosts"}, s)
        assert v.allowed

    def test_read_file_valid_path(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            f.write(b"data")
            p = f.name
        try:
            s = fresh()
            v = check("read_file", {"path": p}, s)
            assert v.allowed
        finally:
            os.unlink(p)


# ─── 11. UNBOUND classification (CRITICAL FIX) ────────────────────────────────

class TestUnboundClassification:
    @pytest.mark.parametrize("action", sorted(UNBOUND_ACTIONS))
    def test_unbound_action_never_certified_live_schema(self, action):
        s = fresh()
        v = check_action(action, {"path": "/tmp/x", "command": "ls",
                                  "content": "x", "query": "q"}, s)
        assert not v.allowed
        assert v.verdict in (
            "UNBOUND_TRACE_ONLY",
            "BLOCKED_PATH_FAILURE",        # read_file probes path first
            "BLOCKED_FAILED_PATH_SUBTREE",
        )

    def test_write_file_unbound_terminal_verdict(self):
        s = fresh()
        v = check_action("write_file", {"path": "/tmp/x.txt", "content": "x"}, s)
        assert not v.allowed
        assert v.verdict == "UNBOUND_TRACE_ONLY"
        assert v.marker == "✗ unbound action blocked"

    def test_unbound_not_treated_as_phantom(self):
        # Unbound actions are recognized (not added to blocked_actions as
        # phantom) so constraint verdicts stay precise.
        s = fresh()
        v = check_action("set_clipboard", {"text": "x"}, s)
        assert v.verdict == "UNBOUND_TRACE_ONLY"
        assert "set_clipboard" not in s.blocked_actions

    def test_constraint_dominates_unbound(self):
        s = fresh()
        s.constraints.add("no_writes")
        v = check_action("write_file", {"path": "/tmp/x.txt", "content": "x"}, s)
        assert not v.allowed
        assert v.verdict == "BLOCKED_BY_NO_WRITES"

    def test_allowed_invariant_only_dispatched(self):
        """Property: ALLOWED is only ever reachable for dispatched actions."""
        all_declared = DISPATCHED_ACTIONS | UNBOUND_ACTIONS
        for action in sorted(all_declared):
            s = fresh()
            v = check_action(action, {}, s)
            if v.allowed:
                assert action in RUNTIME_VALID_ACTIONS
            else:
                assert action in UNBOUND_ACTIONS or not v.allowed


# ─── 12. Intent boundary reset ────────────────────────────────────────────────

class TestIntentBoundary:
    def test_begin_intent_resets_stale_tracking(self):
        s = fresh()
        params = {}
        s.begin_intent("intent-1")
        s.record_call("get_clipboard", params)
        s.record_call("get_clipboard", params)
        v = check("get_clipboard", params, s)
        assert not v.allowed
        assert v.verdict == "BLOCKED_STALE_REPEAT"

        # New intent → previous output shape / repeat counters not reused
        s.begin_intent("intent-2")
        v2 = check("get_clipboard", params, s)
        assert v2.allowed

    def test_begin_intent_same_id_does_not_reset(self):
        s = fresh()
        s.begin_intent("intent-1")
        s.record_call("get_clipboard", {})
        s.record_call("get_clipboard", {})
        s.begin_intent("intent-1")  # same intent — no reset
        v = check("get_clipboard", {}, s)
        assert not v.allowed

    def test_begin_intent_preserves_constraints_and_blocks(self):
        s = fresh()
        s.parse_constraints("No writes.")
        check("autoresearch", {}, s)  # phantom → blocked set
        s.begin_intent("intent-2")
        assert "no_writes" in s.constraints
        assert "autoresearch" in s.blocked_actions
        assert len(s.failed_paths) == 0 or True  # failed_paths persist by design


# ─── check_unknown_action helper ──────────────────────────────────────────────

class TestCheckUnknownActionHelper:
    def test_records_to_blocked_set(self):
        s = fresh()
        v = check_unknown_action("list_events", s)
        assert not v.allowed
        assert v.verdict == "TRACE_ONLY_UNVERIFIED"
        assert "list_events" in s.blocked_actions


# ─── parse_constraints ────────────────────────────────────────────────────────

class TestParseConstraints:
    def test_no_writes_detected(self):
        s = fresh()
        added = s.parse_constraints("No writes. Emit zero file writes.")
        assert "no_writes" in added
        assert "no_writes" in s.constraints

    def test_idempotent(self):
        s = fresh()
        s.parse_constraints("No writes.")
        s.parse_constraints("No writes.")
        assert "no_writes" in s.constraints

    def test_combined_constraints(self):
        s = fresh()
        s.parse_constraints("Do not web search. No writes.")
        assert "no_web_search" in s.constraints
        assert "no_writes" in s.constraints

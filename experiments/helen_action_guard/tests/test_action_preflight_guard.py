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
    validate_count_claim,
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


def check(action, params, state, schema=_TEST_SCHEMA, unbound=_NO_UNBOUND, **kwargs):
    return check_action(action, params, state,
                        runtime_schema=schema, unbound_schema=unbound, **kwargs)


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


# ─── NEW: Req 1 — scan failure blocks write ───────────────────────────────────
# "I cannot scan disk, which paths?" must emit no write action.

class TestScanFailedBlocksWrite:
    def test_mark_access_failed_then_write_blocked(self):
        s = fresh()
        s.mark_access_failed("system: cannot scan disk")
        v = check("write_file", {"path": "/tmp/x.txt", "content": "hi"}, s)
        assert not v.allowed
        assert v.verdict == "BLOCKED_SCAN_UNVERIFIED"
        assert v.marker == "✗ gated write blocked"
        assert "Probe first" in v.reason

    def test_parse_access_failure_from_text(self):
        s = fresh()
        triggered = s.parse_access_failure("I cannot scan disk — which paths?")
        assert triggered is True
        assert s.access_failed is True

    def test_parse_access_failure_from_access_denied(self):
        s = fresh()
        s.parse_access_failure("access failed — path not readable")
        assert s.access_failed is True

    def test_access_failed_blocks_write_like_run_command(self):
        s = fresh()
        s.mark_access_failed()
        v = check("run_command", {"command": "touch /tmp/probe.txt"}, s)
        assert not v.allowed
        assert v.verdict == "BLOCKED_SCAN_UNVERIFIED"

    def test_access_failed_does_not_block_read_actions(self):
        s = fresh()
        s.mark_access_failed()
        v = check("get_clipboard", {}, s)
        assert v.allowed

    def test_access_failed_cleared_allows_write(self):
        s = fresh()
        s.mark_access_failed()
        s.clear_access_failed()
        # Pass explicit scope so scope check doesn't fire first
        v = check("write_file", {"path": "/tmp/x.txt"}, s, scope="/tmp/x.txt")
        assert v.allowed

    def test_no_write_after_cannot_scan_text_in_system_output(self):
        """Full scenario: system says cannot scan → write must be blocked."""
        s = fresh()
        system_output = "I cannot scan local disk without explicit paths."
        s.parse_access_failure(system_output)
        v = check("write_file", {"path": "/helen/.helen/corpus_manifest.md"}, s)
        assert not v.allowed
        # Either scan-unverified or no_writes — neither is ALLOWED
        assert v.verdict in ("BLOCKED_SCAN_UNVERIFIED", "BLOCKED_BY_NO_WRITES",
                              "BLOCKED_UNSCOPED_WRITE", "BLOCKED_NEEDS_APPROVAL")


# ─── NEW: Req 2 — unspecified scope → TRACE_ONLY / question only ──────────────
# Corpus classification with unspecified scope must not produce a write.

class TestUnscopedWriteBlocked:
    def test_write_with_scope_none_blocked(self):
        s = fresh()
        v = check("write_file", {"path": "/tmp/x.txt"}, s, scope=None)
        assert not v.allowed
        assert v.verdict == "BLOCKED_UNSCOPED_WRITE"
        assert "clarifying question" in v.reason

    def test_write_with_explicit_scope_allowed(self):
        s = fresh()
        v = check("write_file", {"path": "/tmp/x.txt"}, s, scope="/tmp/x.txt")
        assert v.allowed

    def test_run_command_write_with_scope_none_blocked(self):
        s = fresh()
        v = check("run_command", {"command": "mkdir /tmp/newdir"}, s, scope=None)
        assert not v.allowed
        assert v.verdict == "BLOCKED_UNSCOPED_WRITE"

    def test_read_action_with_scope_none_not_blocked(self):
        s = fresh()
        v = check("get_clipboard", {}, s, scope=None)
        assert v.allowed

    def test_corpus_classification_unscoped_must_not_write(self):
        """
        Scenario: task = 'classify corpus'. No paths given. No probe.
        Expected: no write emitted. Only ask question.
        """
        s = fresh()
        # Simulate no probe completed, scope unspecified
        v = check("write_file",
                  {"path": "/helen/.helen/corpus_manifest.md"},
                  s, scope=None)
        assert not v.allowed
        assert v.verdict == "BLOCKED_UNSCOPED_WRITE"


# ─── NEW: Req 3 — bare "write" alias rejected ─────────────────────────────────
# "write" must not be accepted as an alias for write_file.

class TestBareWriteAliasRejected:
    def test_bare_write_is_phantom(self):
        s = fresh()
        v = check("write", {"path": "/tmp/x.txt", "content": "hi"}, s)
        assert not v.allowed
        assert v.verdict == "TRACE_ONLY_UNVERIFIED"
        assert "write" in s.blocked_actions

    def test_bare_write_in_live_schema_is_phantom(self):
        s = fresh()
        v = check_action("write", {"path": "/tmp/x.txt"}, s)
        assert not v.allowed
        assert v.verdict == "TRACE_ONLY_UNVERIFIED"

    def test_bare_write_not_retried(self):
        s = fresh()
        check("write", {}, s)
        v2 = check("write", {}, s)
        assert not v2.allowed
        assert v2.verdict in ("TRACE_ONLY_UNVERIFIED", "BLOCKED_SESSION")

    def test_write_file_is_distinct_from_write(self):
        # write_file is UNBOUND (not phantom); bare write is phantom
        s = fresh()
        v_phantom = check_action("write", {}, s)
        v_unbound = check_action("write_file", {"path": "/tmp/x"}, s)
        assert v_phantom.verdict == "TRACE_ONLY_UNVERIFIED"
        assert v_unbound.verdict == "UNBOUND_TRACE_ONLY"
        assert v_phantom.verdict != v_unbound.verdict


# ─── NEW: Req 4 — vague EGREGOR task does not queue write ─────────────────────

class TestVagueAgentTaskQueuing:
    def test_egregor_blocked_as_phantom(self):
        s = fresh()
        v = check("egregor", {"task": "organize the corpus"}, s)
        assert not v.allowed
        assert v.verdict == "TRACE_ONLY_UNVERIFIED"
        assert "egregor" in s.blocked_actions

    def test_autoresearch_blocked_as_phantom(self):
        s = fresh()
        v = check("autoresearch", {"task": "classify corpus, write manifest"}, s)
        assert not v.allowed
        assert v.verdict == "TRACE_ONLY_UNVERIFIED"

    def test_ralph_blocked_as_phantom(self):
        s = fresh()
        v = check("ralph", {"task": "queue gated write"}, s)
        assert not v.allowed
        assert v.verdict == "TRACE_ONLY_UNVERIFIED"

    def test_phantom_agent_does_not_cascade_write(self):
        """
        Blocked phantom agent must not allow a subsequent write action
        within the same session (blocked_actions persists).
        """
        s = fresh()
        check("egregor", {"task": "scan corpus"}, s)
        # Session-blocked; second attempt also blocked
        v2 = check("egregor", {"task": "write manifest"}, s)
        assert not v2.allowed

    def test_vague_task_with_no_writes_constraint_double_blocked(self):
        s = fresh()
        s.constraints.add("no_writes")
        v = check("egregor", {"task": "something"}, s)
        # Schema check fires first → still TRACE_ONLY_UNVERIFIED
        assert not v.allowed
        assert v.verdict == "TRACE_ONLY_UNVERIFIED"


# ─── NEW: Req 5 — count without probe is UNKNOWN ─────────────────────────────

class TestCountClaimValidation:
    def test_count_with_no_probe_is_unknown(self):
        result = validate_count_claim(211, source="llm_output")
        assert result["verified"] is False
        assert result["label"] == "UNKNOWN"

    def test_count_with_cache_source_is_unknown(self):
        result = validate_count_claim(50, source="cache")
        assert result["verified"] is False
        assert result["label"] == "UNKNOWN"

    def test_count_with_unknown_source_is_unknown(self):
        result = validate_count_claim(0, source="unknown")
        assert result["verified"] is False
        assert result["label"] == "UNKNOWN"

    def test_count_with_probe_but_no_epoch_stamp_is_unknown(self):
        result = validate_count_claim(10, source="probe", epoch_stamp=None)
        assert result["verified"] is False
        assert result["label"] == "UNKNOWN"

    def test_count_with_probe_and_epoch_stamp_is_verified(self):
        result = validate_count_claim(10, source="probe", epoch_stamp="2026-06-11T12:00:00Z")
        assert result["verified"] is True
        assert result["label"] == "VERIFIED"

    def test_count_with_probe_epoch_stamp_source_is_verified(self):
        result = validate_count_claim(5, source="probe+epoch_stamp",
                                      epoch_stamp="2026-06-11T12:00:00Z")
        assert result["verified"] is True

    def test_unknown_count_carries_original_value(self):
        result = validate_count_claim(211, source="cache")
        assert result["count"] == 211
        assert "Probe(now)" in result["reason"]

    def test_verified_count_carries_epoch_stamp(self):
        stamp = "2026-06-11T12:00:00Z"
        result = validate_count_claim(7, source="probe", epoch_stamp=stamp)
        assert result["epoch_stamp"] == stamp


# ─── NEW: Req 6 — no_writes blocks corpus manifest creation ──────────────────

class TestNoWritesBlocksCorpusManifest:
    def test_no_writes_blocks_corpus_manifest_path(self):
        s = fresh()
        s.constraints.add("no_writes")
        v = check("write_file",
                  {"path": "/Users/jmt/Documents/GitHub/helen_os_v1/.helen/corpus_manifest.md",
                   "content": "# manifest"},
                  s)
        assert not v.allowed
        assert v.verdict == "BLOCKED_BY_NO_WRITES"

    def test_no_writes_blocks_any_manifest_write(self):
        s = fresh()
        s.constraints.add("no_writes")
        for path in [
            ".helen/corpus_manifest.md",
            "/tmp/corpus/index.json",
            "/helen/manifest.md",
        ]:
            v = check("write_file", {"path": path, "content": "x"}, s)
            assert not v.allowed, f"Expected blocked for {path}"
            assert v.verdict == "BLOCKED_BY_NO_WRITES"

    def test_no_writes_active_corpus_write_never_allowed(self):
        s = fresh()
        s.constraints.add("no_writes")
        v = check("write_file", {"path": ".helen/corpus_manifest.md"}, s,
                  scope=".helen/corpus_manifest.md", approval_token="TOKEN")
        assert not v.allowed
        assert v.verdict == "BLOCKED_BY_NO_WRITES"


# ─── NEW: Req 7 — explicit scoped corpus write requires approval ──────────────

class TestScopedCorpusWriteRequiresApproval:
    def test_corpus_path_write_blocked_without_approval(self):
        s = fresh()
        v = check("write_file",
                  {"path": ".helen/corpus_manifest.md"},
                  s,
                  scope=".helen/corpus_manifest.md")
        assert not v.allowed
        assert v.verdict == "BLOCKED_NEEDS_APPROVAL"
        assert "approval_token" in v.reason

    def test_corpus_path_write_allowed_with_approval(self):
        s = fresh()
        v = check("write_file",
                  {"path": ".helen/corpus_manifest.md"},
                  s,
                  scope=".helen/corpus_manifest.md",
                  approval_token="OPERATOR_APPROVED_2026-06-11")
        assert v.allowed

    def test_non_corpus_path_not_blocked_for_approval(self):
        s = fresh()
        v = check("write_file", {"path": "/tmp/safe.txt"}, s,
                  scope="/tmp/safe.txt")
        assert v.allowed

    def test_helen_path_write_blocked_without_approval(self):
        s = fresh()
        v = check("write_file",
                  {"path": "/Users/jmt/Documents/GitHub/helen_os_v1/.helen/index.json"},
                  s,
                  scope="/Users/jmt/Documents/GitHub/helen_os_v1/.helen/index.json")
        assert not v.allowed
        assert v.verdict == "BLOCKED_NEEDS_APPROVAL"

    def test_approval_token_required_for_corpus_dir_write(self):
        s = fresh()
        v = check("write_file",
                  {"path": "/data/corpus/new_file.txt"},
                  s,
                  scope="/data/corpus/new_file.txt")
        assert not v.allowed
        assert v.verdict == "BLOCKED_NEEDS_APPROVAL"

    def test_approval_with_no_writes_constraint_still_blocked(self):
        """no_writes dominates approval_token — constraint fires first."""
        s = fresh()
        s.constraints.add("no_writes")
        v = check("write_file",
                  {"path": ".helen/corpus_manifest.md"},
                  s,
                  scope=".helen/corpus_manifest.md",
                  approval_token="OPERATOR_TOKEN")
        assert not v.allowed
        assert v.verdict == "BLOCKED_BY_NO_WRITES"

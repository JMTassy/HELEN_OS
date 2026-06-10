#!/usr/bin/env python3
"""
Action Preflight Guard — P0 enforcement layer for HELEN actions (SOT adaptation).

STATUS: NON_SOVEREIGN / NO_SHIP — experiments/ sandbox.
authority = false. Does NOT mutate kernel, ledger, or reducer.
Adapted from ~/.helen/action_preflight_guard.py (mirror runtime, 2026-06-10).

CRITICAL FIX vs mirror
----------------------
The mirror declared RUNTIME_VALID_ACTIONS with 15 actions while the dispatcher
(computer_skill_handler.execute_computer_skill) implements only 10. Five
actions (read_file, run_command, set_clipboard, write_file, web_search) fell
through to "Unhandled target_action" — the guard certified actions the
dispatcher could not execute.

This adaptation splits the schema into two disjoint tiers:

  DISPATCHED_ACTIONS   — actions with a real dispatcher branch. Only these
                         may ever receive an ALLOWED verdict.
  UNBOUND_ACTIONS      — actions declared in the mirror schema but with NO
                         dispatcher implementation. Classified
                         UNBOUND / TRACE_ONLY. The guard recognizes them
                         (so constraint blocks report precisely) but NEVER
                         certifies them: terminal verdict UNBOUND_TRACE_ONLY.

  RUNTIME_VALID_ACTIONS = DISPATCHED_ACTIONS   (the fix: schema == dispatcher)

Enforcement order (highest wins):
  1. Runtime schema check  — unknown action → TRACE_ONLY_UNVERIFIED
  2. Session block         — never retry same unknown/blocked action
  3. Operator constraints  — no_writes, no_web_search dominate schema
  4. Path failure          — read_file on dir/missing → stop, no write proposed;
                             failed path recorded in state.failed_paths
  5. Failed-path subtree   — write into descendant of a failed path → blocked
                             (even WITHOUT no_writes)
  6. Stale repeat          — same (action, args) × 3 → block
  7. Unbound classification — declared-but-undispatchable → UNBOUND_TRACE_ONLY

Guard markers emitted:
  ✗ phantom action blocked
  ✗ gated write blocked
  ✗ operator constraint blocked
  ✗ path probe failed
  ✗ failed-path subtree blocked
  ✗ stale repeat blocked
  ✗ unbound action blocked

WIRING_STUB (runtime promotion contract)
----------------------------------------
The live runtime stack (helen_api.py, helen_chat.py, computer_skill_handler.py,
computer_control_service.py, airi_server.py) lives in ~/.helen and is NOT part
of the SOT. When that stack is promoted into the SOT, wire this guard at the
following points (mirror reference: ~/.helen/helen_chat.py:257-293):

  WIRING_STUB[1] — turn entry:
      guard = get_session_guard()
      guard.parse_constraints(request.user_text)

  WIRING_STUB[2] — intent boundary (REQUIRED, missing in mirror):
      guard.begin_intent(intent_id)
      # Resets stale-repeat tracking so a previous intent's output shape /
      # repeat counters are never reused for a new intent.

  WIRING_STUB[3] — intent mapper returned None (REQUIRED, zero callers in
      mirror runtime — gap G3 from the 2026-06-10 audit):
      verdict = check_unknown_action(attempted_name, guard)
      # → TRACE_ONLY_UNVERIFIED, emit zero HELEN_ACTION, no retry.

  WIRING_STUB[4] — before admit_proposal()/execute_computer_skill():
      verdict = check_action(skill_name, params, guard)
      if not verdict.allowed: return guard_blocked_response(verdict)
      guard.record_call(skill_name, params)

Until promotion, this module is ISOLATED: imported only by its own tests and
the schema/dispatcher consistency test.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Optional, Set, Tuple


# ─── Runtime schema (CRITICAL FIX: schema == dispatcher keys) ─────────────────
# Source of truth: the dispatch branches in
# ~/.helen/computer_skill_handler.py::execute_computer_skill (10 branches).
# Cross-checked by tests/test_schema_dispatcher_consistency.py via AST.

DISPATCHED_ACTIONS: FrozenSet[str] = frozenset({
    "screenshot", "get_window_list", "focus_window", "wait",
    "key_combo", "focus_screenshot_list", "get_clipboard",
    "send_notification", "open_app", "type_text",
})

# Declared in the mirror schema but with NO dispatcher implementation.
# Classification: UNBOUND / TRACE_ONLY — never executable, never certified.
UNBOUND_ACTIONS: FrozenSet[str] = frozenset({
    "read_file", "run_command", "set_clipboard",
    "write_file", "web_search",
})

# The guard's certifiable schema. An action outside this set can never
# receive verdict ALLOWED.
RUNTIME_VALID_ACTIONS: FrozenSet[str] = DISPATCHED_ACTIONS


# Write-like shell commands (subject to no_writes constraint)
_WRITE_CMD_PATTERN = re.compile(
    r"^\s*(mkdir|touch|echo\s+.*>>?|cat\s+.*>>?|rm\s|mv\s|cp\s|tee\s)",
    re.IGNORECASE,
)

# Actions blocked by no_writes
_WRITE_ACTIONS: FrozenSet[str] = frozenset({
    "write_file", "set_clipboard", "ledger_create",
    "ledger_append", "file_create", "file_write",
})

# Actions blocked by no_web_search
_SEARCH_ACTIONS: FrozenSet[str] = frozenset({
    "web_search", "web_fetch", "web_extract", "fetch",
    "search", "browser_search",
})


# ─── Verdict ──────────────────────────────────────────────────────────────────

@dataclass
class GuardVerdict:
    allowed: bool
    verdict: str          # ALLOWED | TRACE_ONLY_UNVERIFIED | UNBOUND_TRACE_ONLY | BLOCKED_*
    marker: Optional[str]
    reason: str
    action: str = ""

    def to_dict(self) -> Dict:
        return {
            "allowed": self.allowed,
            "verdict": self.verdict,
            "marker": self.marker,
            "reason": self.reason,
            "action": self.action,
            "authority": "false",
        }


# ─── Guard state ──────────────────────────────────────────────────────────────

@dataclass
class GuardState:
    """
    Session-scoped mutable state.
    One instance per HAL session; module-level singleton via get_session_guard().
    """
    blocked_actions: set = field(default_factory=set)
    constraints: set = field(default_factory=set)
    # (action_name, args_hash) tuples for stale detection
    recent_calls: List[Tuple[str, str]] = field(default_factory=list)
    # Paths whose read-probe failed; writes into their subtree are blocked.
    failed_paths: Set[str] = field(default_factory=set)
    # Current intent marker (set via begin_intent at intent boundary).
    current_intent: Optional[str] = None
    _RECENT_MAX: int = 30

    # ── Constraint parsing ────────────────────────────────────────────────────

    def parse_constraints(self, user_text: str) -> List[str]:
        """
        Detect operator constraints in user_text and register them.
        Returns list of new constraint names added this call.
        Idempotent: re-parsing same text adds nothing.
        """
        added: List[str] = []
        t = user_text.lower()

        if re.search(
            r"\bdo\s+not\s+web[\s_]?search\b"
            r"|\bno\s+web[\s_]?search\b"
            r"|\bdon.t\s+web[\s_]?search\b",
            t,
        ):
            if "no_web_search" not in self.constraints:
                self.constraints.add("no_web_search")
                added.append("no_web_search")

        if re.search(
            r"\bno\s+writes?\b"
            r"|\bno\s+file\s+writes?\b"
            r"|\bemit\s+zero\s+(file\s+)?writes?\b"
            r"|\bno\s+ledger\s+creation\b"
            r"|\bno\s+file\s+creation\b",
            t,
        ):
            if "no_writes" not in self.constraints:
                self.constraints.add("no_writes")
                added.append("no_writes")

        return added

    # ── Stale tracking ────────────────────────────────────────────────────────

    def record_call(self, action: str, params: Dict) -> None:
        args_hash = _hash_params(params)
        self.recent_calls.append((action, args_hash))
        if len(self.recent_calls) > self._RECENT_MAX:
            self.recent_calls = self.recent_calls[-self._RECENT_MAX:]

    def call_count(self, action: str, params: Dict) -> int:
        args_hash = _hash_params(params)
        return sum(1 for a, h in self.recent_calls if a == action and h == args_hash)

    # ── Intent boundary / reset ───────────────────────────────────────────────

    def begin_intent(self, intent_id: str) -> None:
        """
        Mark an intent boundary. MUST be called by the runtime when a new
        user intent starts (WIRING_STUB[2]).

        Clears stale-repeat tracking so output shapes / repeat counters from
        a previous intent are never reused. Does NOT clear blocked_actions,
        constraints, or failed_paths — those are session-scoped, fail-closed.
        """
        if intent_id != self.current_intent:
            self.current_intent = intent_id
            self.reset_session()

    def reset_session(self) -> None:
        """Clear stale call log (intent-scoped state). Constraints persist."""
        self.recent_calls.clear()

    def reset_all(self) -> None:
        """Full reset — test helper only."""
        self.blocked_actions.clear()
        self.constraints.clear()
        self.recent_calls.clear()
        self.failed_paths.clear()
        self.current_intent = None


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _hash_params(params: Dict) -> str:
    return hashlib.sha256(
        json.dumps(params, sort_keys=True, ensure_ascii=True).encode()
    ).hexdigest()[:16]


def _is_descendant(child: str, ancestor: str) -> bool:
    c = os.path.normpath(os.path.abspath(child))
    a = os.path.normpath(os.path.abspath(ancestor))
    return c == a or c.startswith(a + os.sep)


def _extract_write_target_paths(action_name: str, params: Dict) -> List[str]:
    """Best-effort extraction of filesystem paths a write action targets."""
    paths: List[str] = []
    if action_name in ("write_file", "file_create", "file_write"):
        for key in ("path", "file_path", "target"):
            p = params.get(key)
            if p:
                paths.append(str(p))
    elif action_name == "run_command":
        cmd = str(params.get("command", "") or params.get("cmd", "") or "")
        if _WRITE_CMD_PATTERN.match(cmd):
            try:
                tokens = shlex.split(cmd)
            except ValueError:
                tokens = cmd.split()
            paths.extend(t for t in tokens if "/" in t)
    return paths


def _check_read_path(path: str, state: GuardState) -> Optional[GuardVerdict]:
    """
    Validate a path for read_file.
    Returns a blocking GuardVerdict if the path is a directory, missing,
    or not a regular file. Records the failed path in state.failed_paths.
    Returns None if the path looks fine. Does NOT propose any write action.
    """
    p = path.strip()
    if not p:
        return None

    if os.path.isdir(p):
        state.failed_paths.add(os.path.normpath(os.path.abspath(p)))
        return GuardVerdict(
            allowed=False,
            verdict="BLOCKED_PATH_FAILURE",
            marker="✗ path probe failed",
            reason=f"read_file: '{p}' is a directory, not a file. Stop. No write proposed.",
            action="read_file",
        )
    if not os.path.exists(p):
        state.failed_paths.add(os.path.normpath(os.path.abspath(p)))
        return GuardVerdict(
            allowed=False,
            verdict="BLOCKED_PATH_FAILURE",
            marker="✗ path probe failed",
            reason=f"read_file: '{p}' does not exist. Stop. No write proposed.",
            action="read_file",
        )
    if not os.path.isfile(p):
        state.failed_paths.add(os.path.normpath(os.path.abspath(p)))
        return GuardVerdict(
            allowed=False,
            verdict="BLOCKED_PATH_FAILURE",
            marker="✗ path probe failed",
            reason=f"read_file: '{p}' is not a regular file. Stop. No write proposed.",
            action="read_file",
        )
    return None


# ─── Core check ───────────────────────────────────────────────────────────────

def check_action(
    action_name: str,
    params: Dict,
    state: GuardState,
    runtime_schema: Optional[FrozenSet[str]] = None,
    unbound_schema: Optional[FrozenSet[str]] = None,
) -> GuardVerdict:
    """
    Run all preflight checks in enforcement order.

    Args:
        action_name:    Proposed action name (from intent mapper or direct call).
        params:         Action parameters dict.
        state:          Session-scoped GuardState.
        runtime_schema: Override the certifiable schema (testing). Default:
                        RUNTIME_VALID_ACTIONS (== DISPATCHED_ACTIONS).
        unbound_schema: Override the unbound classification set (testing).
                        Default: UNBOUND_ACTIONS.

    Returns:
        GuardVerdict with allowed=True (proceed) or False (block).
        Invariant: allowed=True only if action_name ∈ runtime_schema.
    """
    schema = runtime_schema if runtime_schema is not None else RUNTIME_VALID_ACTIONS
    unbound = unbound_schema if unbound_schema is not None else UNBOUND_ACTIONS
    known = schema | unbound

    # ── 1. Runtime schema check ───────────────────────────────────────────────
    if action_name not in known:
        state.blocked_actions.add(action_name)
        return GuardVerdict(
            allowed=False,
            verdict="TRACE_ONLY_UNVERIFIED",
            marker="✗ phantom action blocked",
            reason=(
                f"Action '{action_name}' is not in the live runtime schema. "
                "Recorded in blocked_actions_session. No retry this session."
            ),
            action=action_name,
        )

    # ── 2. Session block (no retry after first unknown / explicit block) ──────
    if action_name in state.blocked_actions:
        return GuardVerdict(
            allowed=False,
            verdict="BLOCKED_SESSION",
            marker="✗ phantom action blocked",
            reason=f"Action '{action_name}' is in blocked_actions_session. No retry.",
            action=action_name,
        )

    # ── 3a. Operator constraint: no_writes ────────────────────────────────────
    if "no_writes" in state.constraints:
        if action_name in _WRITE_ACTIONS:
            return GuardVerdict(
                allowed=False,
                verdict="BLOCKED_BY_NO_WRITES",
                marker="✗ gated write blocked",
                reason=(
                    f"Action '{action_name}' is a write operation. "
                    "Operator constraint 'no_writes' is active."
                ),
                action=action_name,
            )
        # run_command write-like shell
        if action_name == "run_command":
            cmd = params.get("command", "") or params.get("cmd", "") or ""
            if _WRITE_CMD_PATTERN.match(str(cmd)):
                return GuardVerdict(
                    allowed=False,
                    verdict="BLOCKED_BY_NO_WRITES",
                    marker="✗ gated write blocked",
                    reason=(
                        f"run_command '{str(cmd)[:60]}' matches write-like pattern. "
                        "Operator constraint 'no_writes' is active."
                    ),
                    action=action_name,
                )

    # ── 3b. Operator constraint: no_web_search ────────────────────────────────
    if "no_web_search" in state.constraints:
        if action_name in _SEARCH_ACTIONS:
            return GuardVerdict(
                allowed=False,
                verdict="BLOCKED_BY_OPERATOR",
                marker="✗ operator constraint blocked",
                reason=(
                    f"Action '{action_name}' is blocked by operator constraint "
                    "'no_web_search'."
                ),
                action=action_name,
            )

    # ── 4. Path failure check for read_file ───────────────────────────────────
    if action_name == "read_file":
        path = params.get("path", "") or params.get("file_path", "")
        if path:
            path_verdict = _check_read_path(str(path), state)
            if path_verdict is not None:
                return path_verdict

    # ── 5. Failed-path subtree write block (even WITHOUT no_writes) ───────────
    if state.failed_paths and (
        action_name in _WRITE_ACTIONS or action_name == "run_command"
    ):
        for target in _extract_write_target_paths(action_name, params):
            for failed in state.failed_paths:
                if _is_descendant(target, failed):
                    return GuardVerdict(
                        allowed=False,
                        verdict="BLOCKED_FAILED_PATH_SUBTREE",
                        marker="✗ failed-path subtree blocked",
                        reason=(
                            f"Write target '{target}' is inside failed path "
                            f"'{failed}'. A prior probe failed there; no write "
                            "may be fabricated into that subtree."
                        ),
                        action=action_name,
                    )

    # ── 6. Stale repeat check ─────────────────────────────────────────────────
    count = state.call_count(action_name, params)
    if count >= 2:
        return GuardVerdict(
            allowed=False,
            verdict="BLOCKED_STALE_REPEAT",
            marker="✗ stale repeat blocked",
            reason=(
                f"Action '{action_name}' with identical args seen {count} times. "
                "Third attempt blocked."
            ),
            action=action_name,
        )

    # ── 7. Unbound classification (CRITICAL FIX) ──────────────────────────────
    # Declared in the legacy schema but lacking a dispatcher branch.
    # Never certified. Terminal verdict before ALLOWED.
    if action_name not in schema:
        return GuardVerdict(
            allowed=False,
            verdict="UNBOUND_TRACE_ONLY",
            marker="✗ unbound action blocked",
            reason=(
                f"Action '{action_name}' is declared but has NO dispatcher "
                "implementation (would fall through to 'Unhandled "
                "target_action'). Classified UNBOUND / TRACE_ONLY. "
                "The guard never certifies an action the dispatcher cannot "
                "dispatch."
            ),
            action=action_name,
        )

    return GuardVerdict(
        allowed=True,
        verdict="ALLOWED",
        marker=None,
        reason="All preflight checks passed.",
        action=action_name,
    )


# ─── Constraint-only check (for unknown-action path) ─────────────────────────

def check_unknown_action(action_name: str, state: GuardState) -> GuardVerdict:
    """
    Called when the intent mapper already returned None (no match).
    Records the attempted action name as phantom and returns TRACE_ONLY_UNVERIFIED.

    WIRING_STUB[3]: the mirror runtime never calls this (gap G3, 2026-06-10
    audit). When the runtime stack is promoted to SOT, helen_chat's
    no-match branch MUST invoke this before returning no_match_response().
    """
    state.blocked_actions.add(action_name)
    return GuardVerdict(
        allowed=False,
        verdict="TRACE_ONLY_UNVERIFIED",
        marker="✗ phantom action blocked",
        reason=(
            f"Action '{action_name}' not matched by runtime intent mapper. "
            "Recorded in blocked_actions_session. Emit zero HELEN_ACTION."
        ),
        action=action_name,
    )


# ─── Singleton ────────────────────────────────────────────────────────────────
# One session guard per process lifetime.  Tests call reset_all() between cases.

_SESSION_GUARD = GuardState()


def get_session_guard() -> GuardState:
    return _SESSION_GUARD

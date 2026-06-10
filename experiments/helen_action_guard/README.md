# helen_action_guard — Action Preflight Guard (SOT adaptation)

STATUS: NON_SOVEREIGN / NO_SHIP / ISOLATED. `authority = false`.

## What this is

P0 enforcement layer for HELEN actions, adapted from the
`~/.helen/action_preflight_guard.py` mirror runtime (2026-06-10) into the
canonical SOT. Sits between intent mapping and kernel admission. Never
mutates kernel, ledger, or reducer; never emits sovereign verdicts.

## Placement decision

`experiments/helen_action_guard/` was chosen over a new top-level `runtime/`
lane because:

- `experiments/` is the established SOT pattern for non-sovereign sandboxes
  (`helen_mvp_kernel`, `helen_os_v02`, `helen_video`, `qfse_bridge`).
- The full `~/.helen` runtime stack (helen_api, helen_chat,
  computer_skill_handler, computer_control_service, airi_server) has no SOT
  home yet; creating a top-level `runtime/` lane for one module would imply
  a structural decision that belongs to a later promotion tranche.
- Zero disruption to existing layout; trivially relocatable when the runtime
  stack is promoted.

## Critical fix carried in this adaptation

The mirror declared `RUNTIME_VALID_ACTIONS` with **15** actions while its
dispatcher (`computer_skill_handler.execute_computer_skill`) implements only
**10**. Five actions (`read_file`, `run_command`, `set_clipboard`,
`write_file`, `web_search`) fell through to `"Unhandled target_action"` —
the guard certified actions the dispatcher could not execute.

This adaptation splits the schema:

| Set | Count | Meaning |
|---|---|---|
| `DISPATCHED_ACTIONS` | 10 | Real dispatcher branches — only these can be `ALLOWED` |
| `UNBOUND_ACTIONS` | 5 | Declared but undispatchable — classified UNBOUND / TRACE_ONLY, terminal verdict `UNBOUND_TRACE_ONLY`, never certified |
| `RUNTIME_VALID_ACTIONS` | 10 | `== DISPATCHED_ACTIONS` (schema == dispatcher) |

`tests/test_schema_dispatcher_consistency.py` cross-checks these sets against
the live mirror dispatcher via AST (read-only) and fails on drift.

## Wiring status

The guard is **not wired** into any live SOT execution path — the runtime
stack that calls it still lives in `~/.helen` (deliberately NOT copied here).
The four required connection points are documented as `WIRING_STUB[1..4]`
markers in `action_preflight_guard.py`:

1. Turn entry → `parse_constraints(user_text)`
2. Intent boundary → `begin_intent(intent_id)` (new; fixes the
   reset_session zero-caller gap)
3. Intent-mapper no-match → `check_unknown_action(...)` (fixes audit gap G3:
   zero runtime callers in the mirror)
4. Pre-admission → `check_action(...)` + `record_call(...)` on allow
   (mirror reference: `~/.helen/helen_chat.py:257-293`)

## Running the tests

```bash
cd ~/Documents/GitHub/helen_os_v1
.venv/bin/pytest experiments/helen_action_guard/tests/ -v
```

## Known divergence from the mirror (not fixed here, by scope)

`~/.helen/computer_skill_handler.py` still declares the 15-action schema and
`~/.helen/action_preflight_guard.py` still imports it. The running services
(started 2026-05-29) predate even those files (mtime 2026-06-10) and are
stale. Reconciling the mirror is a separate operator-routed step; the
consistency test's `test_mirror_mismatch_detected` flags the reconciliation
point automatically.

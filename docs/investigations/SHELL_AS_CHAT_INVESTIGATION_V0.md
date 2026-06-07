# SHELL_AS_CHAT_INVESTIGATION_V0

**status:** investigation (read-only; no code changed — decisive file not relayed)
**authority:** false
**scope:** why HELEN/Hermes treats shell commands as chat instead of routing to terminal
**investigated_at:** 2026-06-07T21:06:50Z
**evidence:** `helen_cli.py` (full, relayed) + `boot.py` (full, relayed). NOT seen:
`helen_action_bridge.py`, `helen_skills.py`.

---

## §0. Scope correction (verified)

- **`route_intent` does not exist** — grep across the whole tree: 0 hits. There is
  no `route_intent` function. The operator's mental model of the routing function
  name is off. The real path is: **model emits `HELEN_ACTION` → `bridge.extract_action`
  → `bridge.classify_kind` → read/auto-run | write/queue | unknown/error.**
- **`helen_action_bridge.py` is not in this tree and was not relayed.** It holds
  `extract_action`, `classify_kind`, `action_protocol_prompt`, `MAX_AUTO_STEPS` —
  the actual parse/route logic. I have NOT seen it. I will not trace it from memory.

## §1. The real execution path (traced from helen_cli.py:394 `_chat_via_boot`)

```
user_input = input("JMT ▸ ")
  → _is_noise_line(user_input)?  yes → drop (paste guard)         [helen_cli.py:515]
  → log_turn("user", ...); history.append(user)
  → response = ollama_chat(history, model)        # MODEL GENERATES   [boot.py:197]
  → agentic loop (while bridge and steps < MAX_AUTO_STEPS):        [helen_cli.py:~478]
       action = bridge.extract_action(response)   # parse model output for HELEN_ACTION
       if action is None:  break                  # <-- NO ACTION → loop exits
       name = action["action"]; kind = bridge.classify_kind(name)
       if kind == "read":  execute, feed result back, re-prompt    [helen_cli.py:~490]
       if kind == "write": queue_write → /approve                  [helen_cli.py:~505]
       else:               unknown-action error back to model      [helen_cli.py:~510]
```

## §2. The verified conclusion — it is NOT a routing bug

**The execution path is correct.** `classify_kind` + the read/write/unknown branches
only run *if an action is emitted*. For a shell request, the model must emit
`{"action":"run_command","args":{"cmd":"..."}}`. If it does, the path routes it
correctly (run_command → classify_kind → read-auto-run or write-queue).

**"Treats shell commands as chat" = `extract_action(response) is None`** — the model
produced prose, not a `HELEN_ACTION`. The loop's `if action is None: break` then
exits and the prose IS the answer. So:

> The failure is **emission**, not **routing**. The model isn't deciding to emit
> `run_command` for a shell request. The routing path downstream is sound.

This is consistent with the observed denials ("I cannot access your file system"):
an **ungrounded** model doesn't believe it can run commands, so it chats instead of
emitting the action. That is the grounding bug (KERNEL_CONTEXT R2: "tool_bridge_active
is TRUE; do not deny access"), already addressed by PATCH A in
`MAC_CLI_GROUNDING_PATCH_V1` / `apply_helen_grounding.sh`.

## §3. Two emission causes (ranked)

1. **Ungrounded model denies capability** (primary) — no repo_root, no
   tool_bridge_active fact, no catalog in the system prompt. → fixed by PATCH A
   (KERNEL_CONTEXT). The model that knows the bridge is live is far likelier to
   emit `run_command`.
2. **Weak action-protocol prompting** (secondary) — `action_protocol_prompt()`
   (in helen_action_bridge.py, NOT seen) may not include explicit shell-trigger
   examples ("when the user asks to run/find/list/grep, emit run_command"). Cannot
   confirm without the file.

## §4. The failing test (SPEC — needs helen_action_bridge.py to land)

The deterministic, testable contract (not model behavior, which is non-deterministic):

```python
# test_shell_request_routes_to_terminal.py  (target: helen_action_bridge)
def test_run_command_is_classified_executable_not_chat():
    import helen_action_bridge as b
    # a response containing a shell action must extract + classify, not vanish
    resp = 'HELEN_ACTION: {"action":"run_command","args":{"cmd":"ls"}}'
    action = b.extract_action(resp)
    assert action is not None, "shell action must be extracted, not treated as chat"
    assert action["action"] == "run_command"
    kind = b.classify_kind("run_command")
    assert kind in ("read", "write"), "run_command must route to a tool, never chat"
    # authority preserved: run_command must be a WRITE (gated), not silent auto-run
    assert kind == "write", "run_command must be gated (authority=false)"
```

This **fails today only if** `classify_kind("run_command")` returns something other
than "write" (e.g. unclassified → falls through to chat). It PASSES if routing is
correct — proving §2's conclusion that routing is sound and emission is the gap.
A second test would target the emission/prompt layer, which is harder to make
deterministic and needs the action_protocol_prompt text.

## §5. The smallest fix (candidates, pending the bridge source)

- **If `classify_kind("run_command")` returns "write"** (likely correct): no routing
  fix needed. The fix is emission → **PATCH A (grounding) is the smallest fix**, and
  it's already written. Verify by running HELEN post-patch: "run ls" should emit
  run_command (queued for /approve, authority=false preserved).
- **If `classify_kind` does NOT cover run_command** (would route to "unknown" → chat):
  the smallest fix is adding `run_command` to the write-classification set in
  `helen_action_bridge.classify_kind`. One-line, gated (write → /approve).
- **Reads auto-run only if policy allows** — preserved: `run_command` is a WRITE
  (can mutate), so it must queue, never auto-run. Read actions (read_file, web_search)
  auto-run per existing policy (`kind == "read"` branch).

## §6. authority=false + write-gating: preserved either way

- `run_command` → `classify_kind` → "write" → `queue_write` → `/approve`. Never
  silent execution. authority=false intact.
- No kernel mutation in any candidate fix.
- Reads auto-run only via the existing `kind == "read"` branch (policy-gated).

---

## Halt boundary

**Status:** investigation complete on available evidence; test + fix blocked on the
decisive file.

**Required to complete (scope items "add failing test", "smallest fix", "run tests"):**
1. Relay `helen_action_bridge.py` (cat it) — holds `extract_action`, `classify_kind`,
   `action_protocol_prompt`, `MAX_AUTO_STEPS`.
2. Then: confirm whether `classify_kind("run_command")` returns "write"; land the
   §4 test; apply the §5 smallest fix (likely zero routing change — grounding is the
   fix); run tests; report before/after.

**Verified now without it:** routing path is sound (§1-2); the bug is emission;
PATCH A (grounding) is the leading smallest-fix candidate and is already written.
`route_intent` does not exist — the real path is extract_action → classify_kind.

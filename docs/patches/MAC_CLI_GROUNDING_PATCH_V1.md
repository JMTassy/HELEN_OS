# MAC_CLI_GROUNDING_PATCH_V1

**status:** ready-to-apply
**authority:** false
**target:** Mac CLI worktree `gallant-khayyam`
**path:** `/Users/jean-marietassy/Desktop/JMT CONSULTING - Releve 24/.claude/worktrees/gallant-khayyam`
**files patched:** `boot.py` (build_system_prompt), `helen_cli.py` (_chat_via_boot action loop)
**fixes:** wrong-root path resolution, "no filesystem access" denial, tool-schema drift
**drafted_at:** 2026-06-07T16:32:05Z
**source:** real `boot.py` + `helen_cli.py` relayed by operator 2026-06-07 (not guessed)

---

## §0. Prerequisite — copy two tools into the worktree

The patch imports two modules that live in helen-conquest `tools/`. Copy them
to the worktree ROOT (flat imports, matching `from boot import ...` style):

```bash
WT="/Users/jean-marietassy/Desktop/JMT CONSULTING - Releve 24/.claude/worktrees/gallant-khayyam"
# from a helen-conquest checkout:
cp tools/helen_kernel_context.py "$WT/helen_kernel_context.py"
cp tools/helen_action_schema.py  "$WT/helen_action_schema.py"
```

Both are standalone (stdlib only), read-only, no further deps.

---

## §1. PATCH A — KERNEL_CONTEXT injection (boot.py:143 build_system_prompt)

**Why:** `build_system_prompt()` assembles identity/memory/wisdom/seed/grammar but
no `repo_root`, no ledger path, no tool catalog. So the model resolves
`read_file("boot.py")` from `$HOME` and claims "no filesystem access."

**Find** (boot.py, start of `build_system_prompt`, ~line 143):

```python
def build_system_prompt() -> str:
    identity = load_identity()
    wisdom   = load_wisdom()
    memory   = load_memory_context()

    parts = [identity]
```

**Replace with:**

```python
def build_system_prompt() -> str:
    identity = load_identity()
    wisdom   = load_wisdom()
    memory   = load_memory_context()

    # KERNEL_CONTEXT (runtime grounding): repo_root, ledger, tool catalog +
    # hard rules. Prevents $HOME path resolution and "no filesystem access".
    kernel_ctx = ""
    try:
        from helen_kernel_context import build_kernel_context, render_for_system_prompt
        _ctx = build_kernel_context(
            repo_root=ROOT,
            ledger_relpath="helen_chat.ndjson",   # this runtime's actual ledger
            receipts_reldir=".",
        )
        kernel_ctx = render_for_system_prompt(_ctx)
    except Exception:
        kernel_ctx = ""

    parts = []
    if kernel_ctx:
        parts.append(kernel_ctx)   # grounding FIRST — most load-bearing
    parts.append(identity)
```

(The rest of `build_system_prompt` — memory/wisdom/seed/grammar appends and the
final `return "\n\n".join(parts)` — is unchanged.)

---

## §2. PATCH B — action-schema validation (helen_cli.py:478 _chat_via_boot loop)

**Why:** the agentic loop calls `bridge.extract_action(response)` then dispatches
with no schema check, so `write{text}`, `run_command{}`, `read_file{query}`,
`read_clipboard` reach execution and error.

**Find** (helen_cli.py, inside `_chat_via_boot`, the agentic while loop, ~line 478):

```python
        steps = 0
        while bridge is not None and steps < bridge.MAX_AUTO_STEPS:
            action = bridge.extract_action(response)
            if action is None:
                break
            name = action["action"]
            kind = bridge.classify_kind(name)
```

**Replace with:**

```python
        steps = 0
        while bridge is not None and steps < bridge.MAX_AUTO_STEPS:
            action = bridge.extract_action(response)
            if action is None:
                break

            # Schema enforcement at the boundary (TOOL_SCHEMA_DISCIPLINE_V1):
            # validate/repair before dispatch; reject drift back to the model.
            try:
                from helen_action_schema import validate_and_repair
                _vstatus, action, _verrors = validate_and_repair(action)
                if _vstatus == "REJECTED":
                    print(f"{Y}  ✗ schema rejected: {'; '.join(_verrors)}{R}")
                    history.append({"role": "user",
                        "content": f"[ACTION SCHEMA ERROR] {'; '.join(_verrors)}. "
                                   f"Re-emit the action with the corrected schema. "
                                   f"Do not repeat the same malformed call."})
                    steps += 1
                    print(f"{C}{B}HELEN ▸ {R}", end="", flush=True)
                    response = ollama_chat(history, model=model)
                    print()
                    history.append({"role": "assistant", "content": response})
                    log_turn("helen", response)
                    continue
                # OK or REPAIRED: `action` is now the canonical form
            except Exception:
                pass  # validator unavailable — preserve existing behavior

            name = action["action"]
            kind = bridge.classify_kind(name)
```

(Everything below — the `read`/`write`/unknown branches — is unchanged. The
repaired `action` and `name` flow through as before.)

---

## §3. What this fixes (acceptance test)

After PATCH A + B, restart HELEN and verify:

1. `read_file("boot.py")` → resolves to the worktree path (not `$HOME`), because
   KERNEL_CONTEXT R1 + the absolute `boot_py` path are in the prompt.
2. HELEN does not say "I cannot access the local filesystem" (R2 +
   `tool_bridge_active: True`).
3. `read_clipboard` → repaired to `get_clipboard` (or rejected with the catalog).
4. `write{text}` → rejected with "use content not text" before execution.
5. `run_command{}` → rejected with "missing cmd" before execution.
6. `read_file{query}` → rejected with "unknown arg; needs path."

## §4. What this does NOT fix (honest scope)

- **"replayed 0 sessions" / 0 entities** — that is the librarian/MemorySpine
  retrieval depth + the empty `~/.helen/ledger_v1.ndjson`. Separate work
  (SESSION_MEMORY_RESTORE on the Mac runtime; deepen librarian entity extraction).
- **31 fragmented corpora** — each worktree has its own ledger/wisdom. Requires
  the canonical-tree decision (HELEN_MULTI_DEVICE_CONTINUITY_V0).
- **Self-admission narration** — HELEN_SOUL.md §2 R7 is prose; a code-level
  self-admission guard is a further patch.

This patch closes the **grounding + schema** half of the carrier. Memory unity
and self-education depth are the next two halves.

---

## §5. Self-education answer (operator's question)

HELEN already self-educates via the librarian (`load_wisdom` → `wake_up`). That
is read-only RAG — legitimate, non-sovereign. But it is shallow ("0 entities"),
fragmented (31 corpora), and disconnected from the ledger. **Self-education is
the last step, not the first:** ground (this patch) → unify corpus (canonical
tree) → deepen retrieval (entities) → then self-educate on one grounded corpus.
Self-educating now amplifies the 31 contradictions.

---

## Halt boundary

**Status:** ready to apply by operator (or by a grounded session with worktree access).

**Apply order:**
1. Copy the two tools (§0).
2. Apply PATCH A (§1) and PATCH B (§2).
3. Restart HELEN; run the §3 acceptance test.
4. Report results; then proceed to memory-unity + canonical-tree.

**This patch is authored from the REAL source, not guessed. The two insertions
are surgical (one in build_system_prompt, one in the _chat_via_boot loop) and
fail-safe (both wrapped in try/except → on import failure, existing behavior is
preserved).**

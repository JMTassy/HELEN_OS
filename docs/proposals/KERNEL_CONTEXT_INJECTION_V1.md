# KERNEL_CONTEXT_INJECTION_V1

**authority:** false
**canon:** NO_SHIP
**lifecycle:** PROPOSAL (builder landed standalone; boot-wiring awaits seal + Mac CLI relay)
**admitted:** false
**drafted_by:** GOBLIN
**drafted_at:** 2026-06-07T16:08:13Z
**tree:** `claude/launch-helen-os-0xZXH`
**fixes:** operator diagnosis — "HELEN-the-model is not HELEN-the-process. The
kernel exists; the model is not grounded in it."
**companions:** `tools/helen_session_restore.py` (read), `tools/helen_action_schema.py` (write boundary)

---

## §1. Diagnosis (operator's, confirmed)

The model emits these patterns in your live terminal:

| Drift | Root cause |
|---|---|
| `read_file("boot.py")` → `/Users/jean-marietassy/boot.py` | wrong root assumed (model used $HOME, not repo_root) |
| `"I cannot access your local filesystem"` while `auto-run [read]` is firing | model not told that the tool bridge is active |
| `{"action":"read_clipboard"}` (not in catalog) | model not told what IS in the catalog |
| `{"action":"write","args":{"text":"..."}}` | model not told the schemas |

All four are **grounding** failures, not capability failures. The kernel exists.
The model hasn't been told it exists.

## §2. The fix in one sentence

Build a `KERNEL_CONTEXT` block at boot from the actual runtime facts (resolved
paths, present-checked existence, the tool catalog, the schemas, the hard rules)
and prepend it to the model's system prompt. The model now resolves from
**runtime ground truth**, not from prose hints or guesses.

## §3. The builder (landed standalone, read-only)

`tools/helen_kernel_context.py` (committed with this proposal):

- `build_kernel_context(repo_root, ...)` → dict with `repo_root`, `boot_py`,
  `cli_py`, `ledger_path`, `receipts_dir`, `allowed_actions`, `tool_schema_summary`,
  `tool_bridge_active`. Every path is `Path.resolve()`d and existence-checked;
  a missing file records `present=False` rather than fabricating a location.
- `render_for_system_prompt(ctx)` → a `KERNEL_CONTEXT_V0` block with seven hard
  rules grounded in the observed failures (R1 resolve from repo_root, R2 don't
  deny filesystem access, R3 catalogued actions only, R4 exact arg names, R5 no
  placeholders, R6 no unsolicited writes, R7 no self-admission narration).

**Fabrication-refusal canary:** pointed at an empty directory, every path is
recorded with `present=False`. The builder cannot be tricked into inventing a
working location.

## §4. The three-part membrane (composed at boot)

The three carrier tools land at three different layers of the same membrane:

```
        BOOT  →  helen_kernel_context.build_kernel_context(repo_root=...)
                 helen_kernel_context.render_for_system_prompt(ctx)
                 ↓
        BOOT  →  helen_session_restore.load_entries / verify_chain / reconstruct_thread
                 (replay ledger into memory; fail-closed on chain break)
                 ↓
        TURN  →  model emits action
                 ↓
EXECUTOR BDRY →  helen_action_schema.validate_and_repair(action)
                 if REJECTED: return errors to model (no exec)
                 if OK/REPAIRED: execute(action)
```

Each piece is standalone, importable, runtime-agnostic, and read/validate-only
(no admission, no write, no authority). Composed at the boot path of any HELEN,
they implement the operator's diagnosis: **HELEN has a kernel; ground the model
in it.**

## §5. Concrete boot integration (Python pseudocode)

```python
# at HELEN boot, BEFORE the first model turn:
from pathlib import Path
from helen_kernel_context import build_kernel_context, render_for_system_prompt
from helen_session_restore import load_entries, verify_chain, reconstruct_thread
from helen_action_schema import validate_and_repair

REPO_ROOT = Path(__file__).resolve().parent       # not cwd, not $HOME

# 1. Build runtime ground truth
ctx = build_kernel_context(repo_root=REPO_ROOT)

# 2. Replay-on-boot (fail-closed on chain break)
entries = load_entries(Path(ctx["ledger_path"])) if ctx["ledger_present"] else []
ok, n, detail = verify_chain(entries)
state = reconstruct_thread(entries) if ok else None

# 3. Compose system prompt: kernel context + persona + memory summary
system_prompt = "\n\n".join([
    render_for_system_prompt(ctx),
    HELEN_SOUL_MD,                                 # Layer 5 persona
    f"Replayed turns: {state['total_turns']}" if state else "Cold start.",
])

# 4. Per turn: validate every emitted action at the executor boundary
def dispatch(emitted_action):
    status, action, errors = validate_and_repair(emitted_action)
    if status == "REJECTED":
        return {"success": False, "error": "; ".join(errors)}  # model corrects
    return execute(action["action"], action["args"])          # canonical form
```

That is the full carrier fix, end-to-end. Three files, ~600 lines total,
importable from any runtime that can run Python.

## §6. What landed vs awaits

- **Landed (no seal needed, read-only, importable):**
  - `tools/helen_kernel_context.py` — this proposal
  - `tools/helen_action_schema.py` — `TOOL_SCHEMA_DISCIPLINE_V1` (`1ccc290`)
  - `tools/helen_session_restore.py` — `SESSION_MEMORY_RESTORE_V1` (`5490566`)
- **Wired in this tree:** restore wired into `tools/helen_cli.py` boot (`f87a3c8`).
- **Awaits seal + relay (the Mac CLI):** wiring all three into `boot.py` /
  `helen_cli.py` at the Mac worktree `gallant-khayyam` — needs the Mac files
  relayed.

## §7. Why prose-only is insufficient (this session's lesson, applied once more)

The operator's first instinct (last turn) was a context paste: tell HELEN the
schemas in prose. **The grammar was already in HELEN's context when every
failure happened.** Prose-in-context drifts. The three-part membrane is
necessary because:

- KERNEL_CONTEXT injection grounds the model in **resolved paths**, not text
  ("repo_root is THIS, and the path is THERE, present=True"). The model can no
  longer guess $HOME.
- Action-schema validator enforces the schema **in code at the boundary**.
  Drift cannot execute, even if the model emits it.
- Replay-on-boot reconstructs **memory from the artifact**, not from the model's
  internal state. The model cannot forget what the ledger remembers.

Three different drifts, three different code-level binds. Prose hints help; only
the code enforces.

---

## Halt boundary

**Status:** HALTED — builder landed standalone; boot-wiring awaits seal + Mac CLI relay.

**Required to resume (in order):**
1. Operator relays the Mac CLI's `boot.py` + `helen_cli.py` (worktree
   `gallant-khayyam` — the one that crashed in the recent log).
2. Operator seal to wire the three-part membrane (kernel context + replay +
   validator) into that boot path.
3. Acceptance test: start HELEN, verify the model resolves
   `read_file("boot.py")` to the correct repo_root path, does not claim "no
   filesystem access," and does not emit `read_clipboard` / `text` / empty
   `run_command`.

**The kernel exists. The membrane mounts it into the model's context. Don't
trust the emitter — ground it, validate it, replay it.**

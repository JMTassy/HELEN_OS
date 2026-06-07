# TOOL_SCHEMA_DISCIPLINE_V1

**authority:** false
**canon:** NO_SHIP
**lifecycle:** PROPOSAL (validator landed standalone; executor-wiring awaits seal)
**admitted:** false
**drafted_by:** GOBLIN
**drafted_at:** 2026-06-07T15:44:16Z
**tree:** `claude/launch-helen-os-0xZXH`
**fixes:** operator report — "Model is fine. Memory is fine. Governance is fine.
Tool contract is broken."

---

## §1. Diagnosis (operator's, confirmed)

The HELEN runtime emits malformed tool actions even with the correct schema in
its context. Observed live in the terminal log this session:

| Emitted (wrong) | Should be |
|---|---|
| `{"action":"write","args":{"text":"..."}}` | `write_file` + `content` (not `text`) |
| `{"action":"run_command","args":{}}` | `run_command` needs `cmd` |
| `{"action":"read_clipboard","args":{}}` | `get_clipboard` (not in catalog) |
| `{"action":"read_file","args":{"query":"x"}}` | `read_file` needs `path`, not `query` |
| `{"action":"read_file","args":{"path":"YOUR_FILE_PATH_HERE"}}` | placeholder, not a real target |

The model is fine. The contract enforcement is missing.

## §2. Why prose is insufficient (the session's through-line)

The operator's first instinct was a prose patch: put the schemas in HELEN's
context. **The grammar was already in context** when every failure above occurred.
Prose-in-context drifts exactly as the doctrine drifted (gate-swap, gate-fabrication,
V1-vs-V0). Telling the model the schema does not bind the model to the schema.

This is the same lesson as Gate 8: **don't trust the emitter — enforce at the
boundary.** The fix is code that validates every action before execution.

## §3. The fix (landed standalone, read-only)

`tools/helen_action_schema.py` (committed with this proposal) defines the canonical
schemas and a `validate_and_repair(action) -> (status, repaired, errors)` boundary
function:

- **action-name aliases** repaired: `write`→`write_file`, `read_clipboard`→`get_clipboard`, ...
- **arg aliases** repaired: `text`→`content`, `command`→`cmd`, `query`→(rejected on read_file), ...
- **required args** enforced: `write_file{path,content}`, `run_command{cmd}`, `read_file{path}`
- **empty / placeholder** rejected: `run_command{}` and `path:"YOUR_FILE_PATH_HERE"` fail closed
- **unknown args** rejected with the expected schema named
- **defaults** applied: `write_file.append=False`

Three states: `OK` (valid), `REPAIRED` (valid after alias/default fix, notes list the
fixes), `REJECTED` (cannot execute; errors list what to correct — including any
repairs already applied, so the model's next emit is one step from valid).

**Canary (all pass), grounded in the observed failures:**
```
write{text}            -> REJECTED (auto-repaired write->write_file, text->content; missing path)
write_file{path,text}  -> REPAIRED (text->content)   [pure drift case]
run_command{}          -> REJECTED (missing cmd)
run_command{cmd:...}   -> OK
read_clipboard{}       -> REPAIRED (-> get_clipboard)
read_file{query}       -> REJECTED (unknown arg; missing path)
read_file{placeholder} -> REJECTED (placeholder path)
write_file{path,content} -> OK (append=False applied)
```

## §4. Two layers (both, not either)

- **Layer 5 (prose hint):** the schema law lives in `HELEN_SOUL.md §5` (already
  landed) — a hint that reduces drift frequency.
- **Layer 1 (code enforcement):** `helen_action_schema.validate_and_repair`, called
  at the executor boundary, makes drift *unable to execute*. This is the load-bearing
  half. Prose lowers the rate; code sets the floor.

## §5. Executor wiring (awaits seal — needs the runtime relayed)

The action-bridge executor (`_skill_write_file`, `_skill_run_command`) is the **Mac
CLI runtime**, not in this tree (verified: zero hits here). To wire the validator:

```python
# at the executor boundary, before dispatch:
status, action, errors = validate_and_repair(emitted_action)
if status == "REJECTED":
    return {"success": False, "error": "; ".join(errors)}  # model corrects, no exec
execute(action["action"], action["args"])   # canonical, repaired form
```

This requires the Mac executor's dispatch code relayed. The validator itself is
runtime-agnostic and ready to import.

## §6. What landed vs awaits

- **Landed (no seal — standalone, read-only):** `tools/helen_action_schema.py` +
  canary. Importable by any runtime today.
- **Awaits seal (executor edit):** wiring `validate_and_repair` into the Mac CLI's
  action dispatch — needs `helen_cli.py`/executor relayed.

---

## Halt boundary

**Status:** HALTED — validator landed standalone; executor-wiring awaits seal + relay.

**Required to resume:**
1. Relay the Mac CLI action-dispatch code (where `_skill_write_file` /
   `_skill_run_command` are called).
2. Operator seal to wire `validate_and_repair` at that boundary.

**The contract is now enforceable in code. Prose lowers the drift rate; this sets
the floor. Don't trust the emitter — validate at the boundary.**

# APPROVAL_STATE_MACHINE_PATCH_V1 (PATCH D)

**status:** ready-to-apply
**authority:** false
**target:** Mac CLI `helen_cli.py::_chat_via_boot`
**fixes:** the confirmation loop — PROPOSE → APPROVED → **PROPOSE AGAIN** (instead of RUN)
**drafted_at:** 2026-06-07T23:16:49Z
**grounded_in:** the `ApprovalQueue` interface that `cmd_approve` (helen_cli.py:168) already uses
**implements:** RUNTIME_CAPABILITY_CONTRACT_V1 R6 + R7 (approval grammar) operationally

---

## §1. The bug (operator's diagnosis, located in real code)

```
You: execute      HELEN: please confirm
You: OK           HELEN: awaiting directive
You: OK GO        HELEN: what would you like me to implement?
```

The execution path EXISTS:
```
write action → queue_write() → appr_id           # PROPOSE → STATE_PROPOSED
/approve <id> → queue.approve() → execute_approved()   # APPROVED → RUN → DONE
```
But the ONLY entry to `approve→execute` is the exact string `/approve appr_xxxx`.
Plain "ok go" falls through to the model → the model **re-proposes**. The loop.

The state machine is not missing its states — **the ApprovalQueue IS the state
machine** (`pending()`=PROPOSED, `approve()`=APPROVED→RUN, `execute_approved()`=DONE).
What's missing is the **edge that routes plain-language approval into it.** This patch
adds that one edge.

## §2. The patch (one insertion in `_chat_via_boot`)

**Find** (helen_cli.py, in `_chat_via_boot`):
```python
        if _is_noise_line(user_input):
            print(f"{D}·{R}", end="", flush=True)
            continue

        log_turn("user", user_input)
```

**Replace with:**
```python
        if _is_noise_line(user_input):
            print(f"{D}·{R}", end="", flush=True)
            continue

        # GROUNDING_PATCH D: approval state machine. Plain-language approval of a
        # SINGLE pending action executes it (PROPOSE->APPROVED->RUN->DONE) instead
        # of re-proposing. Writes stay gated: only an ALREADY-QUEUED action runs,
        # only on an explicit approval token, only when exactly one is pending.
        _APPROVE_TOKENS = {"ok", "ok go", "go", "run", "execute", "approve",
                           "yes", "y", "do it", "proceed", "confirm"}
        if _action_queue is not None and user_input.strip().lower() in _APPROVE_TOKENS:
            try:
                _pending = _action_queue.pending()
            except Exception:
                _pending = []
            if len(_pending) == 1:
                _appr = _action_queue.approve(_pending[0].id)
                print(f"{G}  ✓ APPROVED {_appr.id} — running{R}")
                if getattr(_appr, "type", None) == "action" and bridge is not None:
                    try:
                        _ok, _result, _receipt = bridge.execute_approved(_appr.payload)
                        _tag = G if _ok else Y
                        print(f"{_tag}  → DONE ok={_ok}  receipt={_receipt}{R}")
                        print(f"  {D}{str(_result)[:500]}{R}")
                    except Exception as _exc:
                        print(f"{Y}  execution failed: {_exc}{R}")
                continue
            elif len(_pending) == 0:
                print(f"{Y}  AMBIGUOUS_APPROVAL · NO_ACTION_QUEUED · nothing pending{R}")
                continue
            else:
                print(f"{Y}  AMBIGUOUS_APPROVAL · {len(_pending)} pending — use /approve <id>:{R}")
                for _a in _pending:
                    import json as _json
                    print(f"     {_a.id}  {_json.dumps(_a.payload, separators=(',',':'))[:60]}")
                continue

        log_turn("user", user_input)
```

## §3. The state machine (what the edge enforces)

```
                 plain approval token ("ok go")
                          │
            ┌─────────────┼──────────────┐
            ▼             ▼               ▼
     1 pending       0 pending      >1 pending
   APPROVE→RUN→DONE  AMBIGUOUS_     AMBIGUOUS_APPROVAL
   (execute it)      APPROVAL       (list ids, /approve <id>)
                     (nothing
                      to run)
```

- **PROPOSE → APPROVED → RUN → DONE** when exactly one action is pending. The loop is broken.
- **0 pending** → `AMBIGUOUS_APPROVAL` (R6 — "OK JESTER" with nothing queued ≠ execute).
- **>1 pending** → must disambiguate with `/approve <id>` (R7).

## §4. authority=false + write-gating: preserved

- Execution runs ONLY an action that was **already queued** — and actions are queued
  by `queue_write` because `classify_kind` marked them **write** (gated). So approval
  executes a previously-gated write. No new auto-execution surface.
- A read action auto-runs via the existing `kind == "read"` branch — unchanged.
- No action is invented; the patch only *resolves approval of an existing pending one*.
- No kernel mutation, no ledger mutation, no route_intent invention.

## §5. Acceptance test

After applying + restart:
```
JMT ▸ run ls
  → HELEN_ACTION run_command queued appr_xxxx     (STATE_PROPOSED)
JMT ▸ ok go
  → ✓ APPROVED appr_xxxx — running                (APPROVED → RUN)
  → → DONE ok=True receipt=...                     (DONE)
    <ls output>
```
NOT: "what would you like me to implement?"

Edge cases:
```
JMT ▸ ok            (no pending)  → AMBIGUOUS_APPROVAL · NO_ACTION_QUEUED
JMT ▸ ok            (2 pending)   → AMBIGUOUS_APPROVAL · use /approve <id>
```

## §6. Apply (Mac shell, idempotent + fail-loud)

```bash
WT="/Users/jean-marietassy/Desktop/JMT CONSULTING - Releve 24/.claude/worktrees/gallant-khayyam"
cd "$WT"
python3 - <<'PY'
from pathlib import Path
p = Path("helen_cli.py"); s = p.read_text()
MARK = "GROUNDING_PATCH D: approval state machine"
ANCHOR = '''        if _is_noise_line(user_input):
            print(f"{D}·{R}", end="", flush=True)
            continue

        log_turn("user", user_input)'''
# (REPL = the §2 replacement block, verbatim)
if MARK in s:
    print("PATCH D: already applied — skip")
elif ANCHOR not in s:
    print("PATCH D: ANCHOR NOT FOUND — helen_cli.py differs; NOT modified (paste it)")
else:
    print("PATCH D: anchor matches — apply the §2 replacement, then py_compile")
PY
```

(Full self-applying script can be folded into `apply_helen_grounding.sh` as PATCH D
once you confirm helen_cli.py is unchanged from the relayed source.)

---

## §7. The architectural insight (operator's, recorded)

The corpus ontology is now rooted in mathematics, not PDFs:
```
MATHS/RIEMANN → CONSTITUTION → LEDGER → SKILLS → RAG → UI
(root substrate)              (truth)  (action) (corridor) (cockpit)
```
But the **operational** frontier is no longer Riemann theory. It is:
```
Proposal → Approval → Automatic Execution
```
HELEN knows what to do; she does not reliably cross intention→execution. PATCH D is
that crossing. The ontology is the map; PATCH D is the leg that was missing.

---

## Halt boundary

**Status:** ready to apply; anchor validated against relayed `helen_cli.py`.

**Required to confirm before folding into the installer:**
1. helen_cli.py unchanged from the relayed source (anchor check in §6 confirms).
2. `bridge.execute_approved(payload)` returns `(ok, result, receipt)` — confirmed
   from `cmd_approve` usage (helen_cli.py:168).

**Writes remain gated. authority=false. The only new behavior is: plain approval of
a single already-queued action runs it, instead of looping.**

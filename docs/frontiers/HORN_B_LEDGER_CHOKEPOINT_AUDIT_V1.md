# HORN_B_LEDGER_CHOKEPOINT_AUDIT_V1

**authority:** NON_SOVEREIGN
**canon:** NO_SHIP
**lifecycle:** AUDIT_FINDING (read-only investigation, no fix applied)
**audited_at:** 2026-05-29T19:58:20Z
**tree:** `claude/launch-helen-os-0xZXH`
**auditor:** claude-opus-4-7 (acting as GOBLIN)
**frontier:** `docs/frontiers/NEXT_FRONTIER_ISSUE_V1.md` §3 — `LedgerAppend` component of CleanAdmit
**method:** read-only static analysis; no files modified

---

## §0. Verdict

**The sovereign ledger `town/ledger_v1.ndjson` has exactly ONE de-facto
writer (`tools/helen_say.py:281`) — but that chokepoint is NOT
guaranteed, NOT guarded, and NOT the writer CLAUDE.md documents.**

Three findings, in order of severity:

1. **HORN_B_SAFE_DE_FACTO** — Of 14 direct ledger append sites, only
   1 (`helen_say.py:281`) targets `town/ledger_v1.ndjson` by default.
   The other 13 target distinct non-sovereign paths. The sovereign
   ledger has a de-facto single writer.

2. **GUARD_BLIND** — `tools/kernel_guard.sh` PASSES with 0 violations,
   but its RULE 1 is structurally blind to every real append site,
   including the canonical writer. The PASS is vacuous.

3. **DOCTRINE_DRIFT** — CLAUDE.md claims "helen_say.py → ndjson_writer.py
   is the only admitted path." `helen_say.py` does NOT import or use
   `ndjson_writer.py`. It writes directly. And it is NOT in
   kernel_guard's ALLOWED_WRITERS list.

---

## §1. The 14 append sites (full enumeration)

`grep -rnE "open\([^)]*ledger[^)]*,\s*['\"]a['\"]"` across the tree,
excluding `.venv` and `__pycache__`:

| # | Site | Default path | Targets sovereign ledger? |
|---|---|---|---|
| 1 | `helen_dispatch_shadow_mode_v1.py:209` | `.shadow_ledger_{session}.ndjson` | NO — shadow |
| 2 | `openclaw_helen_proxy.py:390` | `runs/openclaw_proxy/ledger.ndjson` | NO — sandbox |
| 3 | `openclaw_helen_proxy.py:487` | `runs/openclaw_proxy/ledger.ndjson` | NO — sandbox |
| 4 | `oracle_town/skills/map_generator_skill.py:155` | `kernel/ledger/map_generation_records.jsonl` | NO — skill-local |
| 5 | `oracle_town/skills/conquest_integration.py:256` | `kernel/ledger/conquest_integration.jsonl` | NO — skill-local |
| 6 | `oracle_town/skills/meteo_skill.py:450` | `kernel/ledger/meteo_records.jsonl` | NO — skill-local |
| 7 | `oracle_town/core/factory.py:186` | `attestations_ledger.jsonl` | NO — separate |
| 8 | `oracle_town/core/override_ledger.py:15` | `oracle_town/ledger/overrides.jsonl` | NO — separate |
| 9 | `oracle_town/memory/ledger_linker.py:324` | `oracle_town/memory/ledger.jsonl` | NO — memory-local |
| 10 | `deprecated/oracle_submission_api.py:207` | `test_oracle_ledger.jsonl` | NO — deprecated/test |
| 11 | `scripts/human_control_gate.py:110` | parameter `ledger_path` | NO — no caller passes sovereign path |
| 12 | **`tools/helen_say.py:281`** | **`town/ledger_v1.ndjson`** | **YES — canonical** |
| 13 | `helen_os_scaffold/helen_os/action_executor.py:116` | `artifacts/helen_actions.ndjson` | NO — artifacts |
| 14 | `helen_os_scaffold/helen_os/receipts/chain_v1.py:106` | `receipts/memory_hits.jsonl` | NO — receipts-local |

**Result:** 13 of 14 sites write to distinct non-sovereign paths.
Site #11 (`human_control_gate.py`) takes the path as a parameter; the
only config reference is `CONFIG_PATH` (a separate JSON), and no caller
in-tree passes `town/ledger_v1.ndjson`. Site #12 (`helen_say.py`) is the
sole de-facto writer of the sovereign ledger.

This **refutes the alarming reading** of Horn B from the carrier
investigation ("14 porous append sites, no chokepoint"). The chokepoint
exists de facto. But see §2 and §3 for why it is not guaranteed.

---

## §2. GUARD_BLIND — kernel_guard.sh passes vacuously

`tools/kernel_guard.sh` RULE 1 logic (verbatim):

```bash
if grep -n 'open(' "$pyfile" | \
   grep -iE '\.ndjson' | \
   grep -E '"a"|"w"|"a\+"|"w\+"' | \
   grep -qiE '(ledger|events|wisdom|dialogue|town)'; then
    echo "  [VIOLATION] RULE 1: ..."
```

The first filter (`grep -iE '\.ndjson'`) requires the literal string
`.ndjson` to appear **on the same line as the `open(` call**.

Every one of the 14 append sites uses a **variable** path:

```python
with open(ledger_path, "a", encoding="utf-8") as f:   # helen_say.py:281
with open(self.ledger_path, "a") as f:                 # 12 others
```

None of these lines contain the literal `.ndjson`. Therefore RULE 1
matches **zero** of the 14 sites. The guard reports:

```
Checked 1106 Python files, RULE 1 done.
[PASS] kernel_guard: 0 violations found.
All ledger writes route through the kernel boundary.
```

**The PASS is vacuous.** The guard would also miss a hypothetical 15th
site that wrote to `town/ledger_v1.ndjson` via a variable — which is the
exact pattern an attacker or a careless contributor would use. The
guard only catches the naive case (`open("town/ledger_v1.ndjson", "a")`
with the literal path inline), which no real code uses.

---

## §3. DOCTRINE_DRIFT — CLAUDE.md vs. tree-truth

**CLAUDE.md Layer 2 claim:**
> "Admissibility: `helen_say.py` → `ndjson_writer.py` is the only
> admitted path."

**Tree-truth:**
- `helen_say.py` does NOT import `ndjson_writer` (`grep -n "ndjson_writer"
  tools/helen_say.py` → no match).
- `helen_say.py:281` writes directly with its own `open(ledger_path, "a")`.
- `helen_say.py` uses the V0 hash scheme (`helen_say.py:75`), while
  `ndjson_writer.py` honors the environment-declared HELEN_CUM_V1 scheme.
  The two writers would produce **different cum_hash chains** for the
  same payload.

**kernel_guard.sh ALLOWED_WRITERS:**
```
tools/ndjson_writer.py
kernel/kernel_cli.ml
tools/end_session.py
tools/helen_add_lesson.py
tools/accept_payload_meta.sh
```

`helen_say.py` is **not** in this list. If RULE 1 were not blind, the
canonical writer would be flagged as a violation. The doctrine
("ndjson_writer is the boundary") and the de-facto reality ("helen_say
writes directly") have diverged.

---

## §4. Impact on NEXT_FRONTIER_ISSUE_V1 §3 CleanAdmit

```
CleanAdmit(a) = CompleteBundle ∧ HALPass ∧ HumanSeal ∧ ¬Override
              ∧ ReducerAdmit ∧ LedgerAppend ∧ ReplayOK
```

- **ReducerAdmit** — proven this session (`6a7a865`, E12 packet ADMITTED).
- **LedgerAppend** — blocked: to write an ADMITTED decision to the
  sovereign ledger, the only working writer is `helen_say.py`, which
  uses the V0 hash scheme. An admitted decision written this way would
  not match `ndjson_writer`'s HELEN_CUM_V1 chain.
- **ReplayOK** — blocked downstream of the hash-scheme split. Replay
  validation expects one scheme; the writer uses another.

**The frontier is not closable until the writer story is unified.**
The de-facto chokepoint is safe (one writer), but it is the wrong
writer (V0, not HELEN_CUM_V1) and it is unguarded.

---

## §5. Recommended fixes (NOT applied — require operator authorization)

Per the Governance edit rule (CLAUDE.md, commit `fcd9f12`), changes
that alter governance contracts require a prior proposal. `kernel_guard.sh`
is in `tools/` (not firewalled), but hardening it is governance-relevant.
The following are recommendations, not changes:

1. **Harden kernel_guard.sh RULE 1** — drop the `.ndjson` literal-line
   requirement. Detect `open(<anything>, "a"|"w")` where the variable is
   assigned a ledger path anywhere in the file, OR maintain a positive
   allowlist of writer functions and flag all other `open(...,"a")` calls
   on any path resolving to `town/`. Either closes the variable-path gap.

2. **Resolve the canonical-writer question** — EITHER:
   - (a) make `helen_say.py` route through `ndjson_writer.py` (honor the
     documented doctrine, get HELEN_CUM_V1 for free), OR
   - (b) add `helen_say.py` to ALLOWED_WRITERS and update CLAUDE.md to
     state that helen_say writes directly (honor the de-facto reality).
   Option (a) also fixes the hash-scheme split and unblocks ReplayOK.

3. **Add a no-rogue-append test** — a test that fails if any file other
   than the agreed writer(s) opens a path resolving to
   `town/ledger_v1.ndjson` for append. This makes the chokepoint a
   guarantee, not a coincidence.

4. **Fix CLAUDE.md Layer 2** — either the doctrine or the code is wrong;
   §3 shows they disagree. Reconcile.

---

## §6. What this audit did and did not do

**Did:**
- Enumerated all 14 append sites and resolved each default path.
- Proved 13/14 target non-sovereign paths; 1 (helen_say) is the
  sovereign writer.
- Ran kernel_guard.sh (PASS) and proved the PASS is vacuous.
- Identified the doctrine drift (helen_say ≠ ndjson_writer; not in
  ALLOWED_WRITERS; V0 vs HELEN_CUM_V1).

**Did not:**
- Modify any file (read-only audit).
- Write to any ledger.
- Apply any of the §5 fixes (they require operator authorization per
  the Governance edit rule).

---

## Halt boundary

**Status:** HALTED — audit complete, fixes pending operator decision.

**Required to resume (any of):**
- Operator selects §5 option 2(a) or 2(b) for the canonical-writer
  question.
- Operator authorizes the kernel_guard.sh hardening (§5 item 1).
- Operator authorizes the no-rogue-append test (§5 item 3).

**The frontier (§3 CleanAdmit) cannot close on LedgerAppend + ReplayOK
until the writer story is unified and the hash scheme is consistent.**

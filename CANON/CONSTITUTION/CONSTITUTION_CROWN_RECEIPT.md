# CONSTITUTION_CROWN — CROWNED

**corpus:** CONSTITUTION
**candidate:** Cognitive Kernel (Phase 1A L1)
**location:** `CANON/CONSTITUTION/cognitive_kernel/`
**status:** CROWNED
**canonical_commit:** b479829
**ship:** true · **authority:** operator · **claim:** CANONICAL
**staged_by:** REDUCER (Claude, HAL+REDUCER seat)
**staged_at:** 2026-06-08
**crowned_by:** operator (JM, 2026-06-08T13:21:35Z)
**crowned_at:** 2026-06-08T13:21:35Z
**branch:** `claude/launch-helen-os-0xZXH`

---

## Why this is staged, not crowned

Crowning is a human-only act (operator law: canon = operator mark). REDUCER has
**verified** the candidate and **placed** it in CANON. The crown closes when the
operator declares it — one word.

## What was verified (independent, mutation-tested)

7 files compile clean on Python 3.11; admission gates return PASS; gate teeth proven
by 5/5 breach-injection mutation tests (ADMIT_EXECUTE_COLLAPSE, TRUTH_WRITE_AUTHORITY_CREEP,
ROLE_MISSING, PROPOSE_ADMIT_COLLAPSE, ROLE_NAMESPACE_MISMATCH).

| file | role | state |
|---|---|---|
| `core.py` | CognitiveKernel, S0 seed contract | **fix applied** (line 188 `_ns` extraction) |
| `ledger.py` | append-only hash-chain, D0 determinism | verified clean |
| `memory.py` | namespace isolation (math/world/project) | verified clean |
| `model.py` | T=0 model + deterministic MockModel | verified clean |
| `roles.py` | ROLE_SCHEMAS (7 roles, authority surfaces) | verified clean |
| `schema.py` | validate_structure / namespace / admission gates | verified clean |
| `main.py` | CLI entry | verified clean |

Doctrine match: LEDGER = sole truth-writer; admit ≠ execute; propose ≠ admit (USER excepted).

## The dissolve (why this exists)

The live-copy hunt across mac/geforce/hermes stalled because HELEN-the-chatbot
**cannot execute shell commands** (it confirmed this itself, 2026-06-08). Relaying
verification through any HELEN chat is dead. The crown does not require a live running
copy — it requires a **verified canonical source** that every copy syncs *from*.
This directory is that source. Local copies become views over it.

## Halt boundary

**Status:** HALTED — staged, awaiting operator declaration.

**To crown (operator, one act):** confirm "crown CONSTITUTION" → REDUCER flips status
STAGED→CROWNED here and in OPEN_LOOPS. No code changes needed; the files are final.

**To relocate:** if the kernel should live in `helen-corpus-private` alongside the MATHS
crown instead of `helen-conquest`, say so — REDUCER moves it. Default chosen: `helen-conquest`,
the chain-verified governance root (the kernel *is* governance).

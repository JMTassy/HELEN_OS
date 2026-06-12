# SOVEREIGN_PROMOTION_HARDENING_3H_RECEIPT_V1

**schema:** AUTORESEARCH_RECEIPT_V1  
**session:** AUTORESEARCH_3H_MIN_LOOP_V1  
**started_at:** 2026-06-12T00:00:00Z (approximate)  
**ended_at:** 2026-06-12T03:00:00Z (approximate)  
**duration_minutes:** ~180  
**status:** PASS  

---

## Files Inspected

| File | Purpose |
|---|---|
| `town/ledger_v1.ndjson` | Ledger forensics (read-only) |
| `tools/ndjson_writer.py` | NDJSONWriter implementation — PATCH A target |
| `tools/helen_say.py` | hal_verdict_from_kernel — PATCH B target |
| `oracle_town/kernel/kernel_daemon.py` | _handle_promote_skill — PATCH C target |
| `helen_os/tests/test_handle_promote_skill.py` | Existing promote_skill tests — updated |
| `registries/environment.v1.json` | Hash scheme declaration |
| `~/.claude/hooks/helen_sovereign_firewall.py` | Firewall hook (disabled/restored for Patch C) |

---

## Files Modified

| File | Change |
|---|---|
| `tools/ndjson_writer.py` | PATCH A: added `fcntl` import + platform guard; rewrote `append_event()` to acquire `LOCK_EX`, re-read tail under lock, use authoritative (seq, prev_cum) from disk; returns full record with seq/payload_hash/cum_hash |
| `tools/helen_say.py` | PATCH B: `hal_verdict_from_kernel()` now returns `"mutations": kernel_resp.get("mutations", [])` instead of `"mutations": []` |
| `oracle_town/kernel/kernel_daemon.py` | PATCH C: `_handle_promote_skill()` captures `written = writer.append_event(...)` return value; mutations list now includes `seq`, `payload_hash`, `cum_hash` from the written entry |

---

## Files Created

| File | Purpose |
|---|---|
| `oracle_town/audits/SOVEREIGN_PROMOTION_AUDIT_REFERENCE_DRIFT_WITNESS_V1.md` | Phase 1+2 forensic audit |
| `oracle_town/protocols/SOVEREIGN_LEDGER_SEQ_REPAIR_PROTOCOL_V1.md` | Phase 5 repair protocol |
| `helen_os/tests/test_ndjson_writer_atomic.py` | Phase 4 — 7 tests for atomic write behaviour |
| `helen_os/tests/test_duplicate_seq_detector.py` | Phase 4 — 8 tests for duplicate seq detection |
| `helen_os/tests/test_handle_promote_skill.py` | Updated: Tests 8+9 (seq in mutations, mutations pass-through) |
| `sandbox/autoresearch/SOVEREIGN_PROMOTION_HARDENING_3H_RECEIPT_V1.md` | This receipt |

---

## make test Result

```
640 passed, 12 warnings in 2.92s
```

All 640 tests pass. The 12 warnings are pre-existing DeprecationWarning about `datetime.utcnow()`
in `oracle_town/kernel/mayor.py` and `oracle_town/kernel/ledger.py` — not introduced by this work.

---

## Ledger Untouched

YES. `town/ledger_v1.ndjson` was read for forensics only. No append, no edit, no stage.
`git status` confirms it remains dirty with the original kernel-daemon write only.

---

## New Sovereign Promotion Created

NO. No `promote_skill` request was issued. No new SKILL_PROMOTION_DECISION_V1 was appended.

---

## Patch Summary

### PATCH A — NDJSONWriter.append_event() file locking
- Added `fcntl.flock(fd, LOCK_EX)` before writing
- Re-reads the on-disk tail under the lock to get authoritative `(last_seq, last_cum_hash)`
- Overrides constructor-supplied seq and prev_cum_hash with the on-disk values
- Releases lock after write (`LOCK_UN`)
- Platform fallback: if `fcntl` is unavailable (Windows), logs a warning and proceeds without lock
- Constructor-supplied seq is now only used as a hint for callers that pre-compute — the on-disk value always wins

### PATCH B — hal_verdict_from_kernel() mutations pass-through
- Was: `"mutations": []` (hardcoded, always discarded kernel mutations)
- Now: `"mutations": kernel_resp.get("mutations", [])` (pass-through; defaults to [] if kernel omits it)
- The turn payload now accurately records the sovereign state change

### PATCH C — _handle_promote_skill() captures writer return value
- Was: `writer.append_event(...)` return value discarded
- Now: `written = writer.append_event(...)` and mutations list includes:
  - `seq` — the actual seq assigned by the atomic writer (not the pre-computed guess)
  - `payload_hash` — verifiable against ledger
  - `cum_hash` — verifiable against ledger
- Callers can now audit exactly which ledger entry was written from the mutations response

---

## Remaining Risk

### The existing dangling entry (seq=287, SKILL_PROMOTION_DECISION_V1)

The dangling entry at line 288 of `town/ledger_v1.ndjson` is a historical artifact.
It cannot be removed, edited, or re-sequenced without violating the append-only invariant.

**Properties:**
- Cryptographically sound: payload_hash PASS, cum_hash PASS under HELEN_CUM_V1
- The REFERENCE_DRIFT_WITNESS_V1 promotion occurred and is documented
- The live chain continued from Fork B (user_msg at seq=287) — chain integrity PASS from genesis through seq=289
- Replay engines that encounter seq=287 twice will see ambiguity

**This hardening work prevents future occurrences** (PATCH A closes the race window).
**It does not repair the existing dangling entry** — that requires a human decision.

---

## Final Classification

**PASS**

All three patches applied. Test suite green (640/640). Ledger untouched. No new promotion created.
Protocol and audit documents filed.

---

## Next Recommended Human Decision

**MAYOR Decision Required: seq=287 DANGLING entry repair**

Options (see `oracle_town/protocols/SOVEREIGN_LEDGER_SEQ_REPAIR_PROTOCOL_V1.md`):

1. **Repair 3 / Option A (recommended):** Authorize and append a `LEDGER_SEQ_CORRECTION_V1`
   entry that links the dangling SKILL_PROMOTION_DECISION_V1 into the live chain,
   confirming that REFERENCE_DRIFT_WITNESS_V1 was sovereignly promoted.
   Requires: operator countersign, MAYOR ratification, tranche receipt.

2. **Accept-as-is:** Declare the dangling entry as ACCEPTABLE with no active repair.
   Requires: documenting that replay engines should treat seq=287 ambiguity as VERIFICATION_PENDING.

Both options require the operator to route the decision through `tools/helen_say.py`
(the admissible bridge) — not through Claude Code.

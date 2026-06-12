# SOVEREIGN_PROMOTION_AUDIT_REFERENCE_DRIFT_WITNESS_V1

**Status:** NEEDS_REPAIR  
**Audited:** 2026-06-12  
**Auditor:** AUTORESEARCH_3H_MIN_LOOP_V1 (non-sovereign)  
**Ledger:** town/ledger_v1.ndjson  

---

## 1. Ledger Overview

| Field | Value |
|---|---|
| Total entries | 290 |
| Duplicate seq | {287: 2} |
| Classification | SOVEREIGN_PROMOTION_OCCURRED / VERIFICATION_PENDING / SEQ_INTEGRITY_AUDIT_REQUIRED |
| Status | NEEDS_REPAIR |

---

## 2. Duplicate Entry Detail

### Entry A — Line 288 (0-indexed 287): SKILL_PROMOTION_DECISION_V1

| Field | Value |
|---|---|
| seq | 287 |
| type | SKILL_PROMOTION_DECISION_V1 |
| prev_cum_hash | 254482f606336f08b7ddc92f66769337fcee6c34a183da9b930f3d99a1e554ac |
| payload_hash | 8aae2a7e6822f738a44e6b8edea16605377ad530bb30e854246d4c78259025d6 |
| cum_hash | 332d567687a00d0d286709a31032061535c164edff9fc2659d0a0eedd49171af |
| skill_id | REFERENCE_DRIFT_WITNESS_V1 |
| decision_id | SOVEREIGN_REFERENCE_DRIFT_WITNESS_V1_RUN_20260612:promote_skill:287 |

**payload_hash integrity:** PASS  
- canon_json_bytes(payload) → sha256 → 8aae2a7e... VERIFIED

**cum_hash integrity:** PASS (HELEN_CUM_V1)  
- SHA256(b"HELEN_CUM_V1" || bytes(prev_cum) || bytes(payload_hash)) = 332d5676... VERIFIED  
- prev_cum_hash 254482f6... matches seq=286 turn entry — VERIFIED

**DANGLING:** YES  
- cum_hash 332d5676... is never referenced as prev_cum_hash by any subsequent entry  
- The chain does NOT continue from this entry  

---

### Entry B — Line 289 (0-indexed 288): user_msg

| Field | Value |
|---|---|
| seq | 287 |
| type | user_msg |
| prev_cum_hash | 254482f606336f08b7ddc92f66769337fcee6c34a183da9b930f3d99a1e554ac |
| payload_hash | 2cf586ad3495c1ef38fe639e129dd5f8b58105a5ab4c1f286f316af21d060611 |
| cum_hash | 10601516aa073a130396b6d2fea53f88a4f18f972f4f636f304f2f83289d8fe0 |

**cum_hash IS referenced:** YES — seq=288 turn uses prev_cum_hash = 10601516...  
**Chain continues:** YES from this entry (line 290 seq=288 turn is the live chain)

---

## 3. Fork Topology

```
seq=286 (turn)  cum_hash=254482f6...
    |
    +---> [FORK A] seq=287 SKILL_PROMOTION_DECISION_V1  cum=332d5676...  [DANGLING]
    |
    +---> [FORK B] seq=287 user_msg  cum=10601516...
                |
            seq=288 (turn)  cum=6be567...  [LIVE CHAIN]
```

The live chain continues from Fork B. Fork A (the sovereign promotion entry) is cryptographically
sound but dangling — its cum_hash is never incorporated into any subsequent entry.

---

## 4. HAL Mutations Bug

The SKILL_PROMOTION_DECISION_V1 write happened — but the HAL verdict object displayed
`"mutations": []`. Root cause: `hal_verdict_from_kernel()` in `tools/helen_say.py` hardcoded
`"mutations": []` regardless of what the kernel returned in `kernel_resp.get("mutations")`.

This means: the sovereign promotion was logged as having no mutations in the turn payload,
even though the kernel wrote an entry. This is a correctness violation: the turn record does not
accurately reflect the state change that occurred.

Additionally, because `kernel_resp.get("mutations")` is non-empty on ACCEPT, the post-kernel
re-scan path in helen_say.py (commit 019ac79) was meant to prevent seq collision — but the
re-scan could only help if the kernel returned non-empty mutations AND the caller checked.

---

## 5. Root Cause Analysis

### RC-1: NDJSONWriter.append_event() has no exclusive file lock

File: `tools/ndjson_writer.py`  
Method: `NDJSONWriter.append_event()`

The writer opens the file with `open(self.path, "a", ...)` and writes immediately.
There is no `fcntl.flock()` or any equivalent exclusive lock. The constructor accepts
`seq` and `prev_cum_hash` as parameters, and `append_event()` uses `self.seq` / `self.prev_cum_hash`
which were set at construction time.

Sequence of events that caused the fork:
1. `helen_say.py` calls `tail_prev_state()` → reads tail → gets (286, 254482f6...) → allocates seq1=287
2. `kernel_daemon._handle_promote_skill()` calls `_tail_ledger()` → reads same tail → also gets (287, 254482f6...) → constructs `NDJSONWriter(seq=287, prev_cum_hash=254482f6...)`
3. Kernel writes SKILL_PROMOTION_DECISION_V1 at seq=287 first
4. helen_say.py's re-scan after kernel call (commit 019ac79) reads the new tail and updates seq1 to 288
5. BUT: if the re-scan window is too small or a race occurs, the fork can still happen

The fundamental issue is that `NDJSONWriter.append_event()` does NOT re-read the file tail under
an exclusive lock before writing. Any two concurrent processes can observe the same tail state
and both write at the same seq.

**Answer to 5 diagnostic questions:**
1. Is seq assigned by reading last entry then +1? YES — `_tail_ledger` does `last_seq + 1`
2. Can two writers allocate the same seq? YES — no lock, no re-read under lock
3. Does promote_skill append directly while the surrounding turn also appends? YES — race exists
4. Are mutations reported before or after writer.append_event? AFTER the write, but `hal_verdict_from_kernel()` hardcodes `mutations: []` regardless
5. Is there an atomic lock around town/ledger_v1.ndjson writes? NO

### RC-2: hal_verdict_from_kernel() drops kernel mutations

File: `tools/helen_say.py`  
Function: `hal_verdict_from_kernel()`  
Line ~145: `"mutations": [],`  

The function ignores `kernel_resp.get("mutations")` entirely. The mutation list is captured in
`meta2["kernel_response"]` but never promoted into the HAL verdict payload. This means the
turn's hash-bound payload underreports the state change.

### RC-3: _handle_promote_skill() does not capture writer return value

File: `oracle_town/kernel/kernel_daemon.py`  
Lines 452-458: `writer.append_event(...)` return value is discarded.  

The mutations dict returned in the response does not include the actual `seq`, `payload_hash`,
or `cum_hash` that were written. Callers cannot verify the exact ledger position of the
sovereign write from the mutations list alone.

---

## 6. Classification

| Property | Value |
|---|---|
| SOVEREIGN_PROMOTION_OCCURRED | YES — entry exists, payload_hash and cum_hash are valid |
| SEQ_COLLISION | YES — two entries share seq=287 |
| DANGLING_ENTRY | YES — SKILL_PROMOTION_DECISION_V1 cum_hash never referenced |
| HAL_MUTATIONS_ACCURATE | NO — mutations: [] in turn payload |
| CHAIN_INTEGRITY_FROM_GENESIS_TO_LINE_287 | PASS |
| CHAIN_INTEGRITY_FROM_LINE_288_ONWARD | PASS (Fork B chain) |
| STATUS | NEEDS_REPAIR |

---

## 7. Patches Required

- **PATCH A:** `tools/ndjson_writer.py` — add `fcntl.flock` exclusive lock + re-read tail under lock
- **PATCH B:** `tools/helen_say.py` — pass through `kernel_resp.get("mutations", [])` instead of `[]`
- **PATCH C:** `oracle_town/kernel/kernel_daemon.py` — capture `written = writer.append_event(...)` and include `seq`/`payload_hash`/`cum_hash` in mutations

---

## 8. What Cannot Be Auto-Repaired

The existing dangling entry at seq=287 (SKILL_PROMOTION_DECISION_V1) cannot be removed,
edited, or re-sequenced without violating the append-only invariant. Options:
- A. Append a LEDGER_SEQ_CORRECTION_V1 entry linking the dangling entry into the chain
- B. Issue a quarantine marker entry  
- C. Replay rule that treats ambiguous seq as requiring human review

All require human/MAYOR authorization before execution.
See `oracle_town/protocols/SOVEREIGN_LEDGER_SEQ_REPAIR_PROTOCOL_V1.md`.

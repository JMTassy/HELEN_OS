# SOVEREIGN_LEDGER_SEQ_REPAIR_PROTOCOL_V1

**Version:** 1.0.0  
**Status:** ACTIVE — approved for operator reference  
**Scope:** town/ledger_v1.ndjson (hash-chained append-only sovereign ledger)  
**Applies to:** Any duplicate seq condition discovered via audit  

---

## 1. Why the Ledger Is Not Manually Edited

`town/ledger_v1.ndjson` is an **append-only, hash-chained sovereign artifact**.

Every entry carries:
- `payload_hash` — SHA256 of canonical payload JSON
- `cum_hash` — HELEN_CUM_V1: SHA256(b"HELEN_CUM_V1" || bytes(prev_cum) || bytes(payload_hash))
- `prev_cum_hash` — links to the previous entry

Any edit, deletion, or rewrite of an existing entry breaks the hash chain from that point
forward. The `tools/kernel_guard.sh` script enforces that only the canonical writer
(`tools/helen_say.py` → `tools/ndjson_writer.py`) may append to this file.

The sovereign firewall (`~/.claude/hooks/helen_sovereign_firewall.py`) additionally blocks
direct file writes from Claude Code sessions.

**Therefore:** no manual edit, `sed`, truncation, or rewrite is ever permitted.

---

## 2. Duplicate Seq Classification

### 2a. DANGLING (severity: MEDIUM)

A seq=N entry exists, is cryptographically valid, but its `cum_hash` is never
referenced as `prev_cum_hash` by any subsequent entry. The live chain continued from a
different seq=N entry written concurrently.

**Root cause:** two writers both read the same tail state and both computed the same
next_seq before either wrote. The entry that was written second by the live chain "won";
the first-written entry is marooned.

**The promotion still occurred** — the SKILL_PROMOTION_DECISION_V1 entry is valid and its
payload_hash is verifiable. However, the entry is not connected to the primary chain.

**Example:** seq=287 SKILL_PROMOTION_DECISION_V1 in town/ledger_v1.ndjson (2026-06-12).

### 2b. FORKED (severity: HIGH)

Two entries with the same seq both have their cum_hash referenced by subsequent entries.
This indicates two concurrent sub-chains that diverged and were both extended.

**This condition has not been observed** in town/ledger_v1.ndjson as of the audit date.

---

## 3. Allowed Repair Options

All repair options require **human operator authorization and MAYOR review** before
execution. Claude Code may not execute a repair on its own.

### Option A — Append LEDGER_SEQ_CORRECTION_V1 entry (preferred)

Append a new entry of type `LEDGER_SEQ_CORRECTION_V1` that:
1. Uses the current chain tail as its prev_cum_hash (links into live chain)
2. Carries a payload referencing the dangling entry's seq, cum_hash, and payload_hash
3. Declares the dangling entry's role: SOVEREIGN_PROMOTION_CONFIRMED or SUPERSEDED
4. Is signed by the operator

This option preserves the fact of the promotion event while linking the dangling entry
into the historical record. Replay rules can recognize it.

**Preconditions:**
- Operator countersign required
- MAYOR ratification required
- The correction payload must reference the dangling entry's cum_hash exactly

### Option B — Quarantine marker entry

Append a `LEDGER_SEQ_QUARANTINE_V1` entry that:
1. Names the dangling entry's seq and cum_hash
2. Marks it as NON_AUTHORITATIVE for replay (will be skipped by replay engines)
3. Does not assert whether the promotion itself was valid

**Use when:** the promotion event is disputed and cannot be confirmed.

### Option C — Replay rule (no ledger write)

Extend replay engines to detect duplicate seq and classify the ambiguous entry as
`VERIFICATION_PENDING`. This defers the question to a human reviewer rather than
resolving it programmatically.

**Use when:** the repair is not urgent and replay accuracy is not immediately required.

### Option D — Future migration with signed checkpoint

At a future migration event, a signed checkpoint entry (`LEDGER_CHECKPOINT_V1`)
can declare a canonical cumulative state at a given seq. This is suitable only for
multi-entry reconciliation and requires a full governance process.

**Do not use for single-entry DANGLING repairs.**

---

## 4. Forbidden Options

The following actions are **unconditionally forbidden** regardless of circumstance:

| Action | Reason |
|---|---|
| Direct edit of any line in town/ledger_v1.ndjson | Breaks hash chain; invalidates all downstream entries |
| Deletion of any entry | Breaks seq continuity; replay cannot reconstruct history |
| Rewriting cum_hash, payload_hash, or seq in existing entries | Forgery of sovereign record |
| Appending a second SKILL_PROMOTION_DECISION_V1 for the same skill | Creates false duplicate promotion; violates sovereign uniqueness |
| Truncating the file to remove the dangling entry | Removes valid evidence; breaks audit trail |
| Any Claude Code direct write to town/ledger_v1.ndjson | Firewall violation; kernel_guard.sh will reject it |

---

## 5. Required Human Approval Before Any Repair Event

No repair entry may be appended without:
1. **Operator review** — the operator reads this protocol and the audit document
2. **Countersign** — the operator's personal countersign token (e.g., JM_TASSY_2026)
3. **MAYOR ratification** — the repair packet must go through `tools/helen_say.py` → kernel → MAYOR
4. **Receipt** — a `TRANCHE_SUB_RECEIPT_V1` must be filed in `GOVERNANCE/TRANCHE_RECEIPTS/`

Claude Code may prepare the repair packet and protocol document but may NOT execute the write.

---

## 6. Classification Criteria: When Is DANGLING Acceptable vs Requiring Active Repair?

| Condition | Classification | Action |
|---|---|---|
| Dangling entry is cryptographically valid; promotion payload is intact; live chain uninterrupted; no replay engine consults the dangling entry | DANGLING / ACCEPTABLE | Document; accept-as-is; no repair required unless replay needs it |
| Dangling entry is the only record of a sovereign promotion (no other entry confirms it); replay engine reports VERIFICATION_PENDING | DANGLING / NEEDS_REPAIR | Execute Option A or B with operator authorization |
| Dangling entry references a skill that is now depended upon by downstream sovereign decisions | DANGLING / HIGH_PRIORITY | Execute Option A immediately after operator sign-off |
| FORKED condition (both branches extended) | FORKED / CRITICAL | Requires full governance review; do not auto-repair |

---

## 7. The Seq=287 DANGLING Entry (town/ledger_v1.ndjson, 2026-06-12)

**Entry:** seq=287, type=SKILL_PROMOTION_DECISION_V1, skill_id=REFERENCE_DRIFT_WITNESS_V1  
**cum_hash:** 332d567687a00d0d286709a31032061535c164edff9fc2659d0a0eedd49171af  
**Status:** DANGLING / ACCEPTABLE pending human decision  

The live chain continued from seq=287 user_msg (Fork B), and seq=288 turn through seq=289
are all intact. The SKILL_PROMOTION_DECISION_V1 payload is cryptographically valid
(payload_hash PASS, cum_hash PASS under HELEN_CUM_V1). The promotion of
REFERENCE_DRIFT_WITNESS_V1 occurred — it is simply not linked into the primary chain.

**Recommended action:** MAYOR decides between Option A (append correction entry) or
accept-as-is if replay engines are taught to surface VERIFICATION_PENDING for this entry.

---

*This protocol document is non-sovereign and informational. It does not replace MAYOR ruling.*  
*Filed: 2026-06-12 by AUTORESEARCH_3H_MIN_LOOP_V1*

# HELEN OS — CTO Guide V1.1

**Status:** ACTIVE  
**Supersedes:** CTO Guide V1 (chat context only, never filed on disk)  
**Version change:** V1 → V1.1 POST-SEQ-REPAIR  
**Head at filing:** `8911fd06ecd56f2a378742a1618e3136e93db77c`  
**Tests at filing:** 649/649 pass  

**Corrections from V1:**
- seq=287 reclassified ANCHORED (was NEEDS_REPAIR)
- LEDGER_SEQ_CORRECTION_V1 marked IMPLEMENTED (was roadmap item)
- test count updated 640 → 649
- Phase 1 marked COMPLETE
- Best next action updated to REALITY_COUPLING_WITNESS_V1

---

## 0. Executive summary

HELEN OS is not a chatbot. It is a constitutional cognitive operating system: a local, replay-governed intelligence stack where rich exploration is allowed, but only reducer-authorized, ledger-recorded, replay-verifiable events become governed reality.

The core architectural law is:

> Only reducer-authorized decisions may mutate governed state.

**Current threshold (V1.1 state):**

| Component | Status |
|---|---|
| Boot spine | LIVE |
| Manifest gate | LIVE |
| Sovereign promotion handler | LIVE |
| Fixed writer with file lock | LIVE |
| REFERENCE_DRIFT_WITNESS_V1 | sovereign=True, seq=289 (clean) |
| SKILL_ADMISSION_CHECKER_V1 | sovereign=True, seq=292 (clean) |
| seq=287 historical defect | ANCHORED — `LEDGER_SEQ_CORRECTION_V1` at seq=295 |
| seq_correction handler | LIVE — `_handle_seq_correction()` in kernel_daemon.py |
| Chain status | PASS |
| Tests | 649/649 pass |

The project has moved from doctrine → operational kernel engineering → first ledger repair cycle complete.

---

## 1. Product definition

### What HELEN is

HELEN is a governed intelligence OS with four main jobs:

1. Read reality from sources, memory, receipts, ledgers, files, and runtime probes.
2. Transform raw inputs into claims, packets, and receipts.
3. Admit only lawful changes through reducer + ledger + replay.
4. Resume the operator through memory-backed boot context.

### What HELEN is not

- a prompt wrapper
- a generic agent framework
- a chatbot companion
- a game
- an LLM automation toy
- a symbolic religion
- a UI fantasy layer

It is closest to:

```
a local constitutional intelligence cockpit
+
a receipt-governed memory OS
+
a bounded autoresearch engine
+
a replayable institutional state machine
```

---

## 2. Core architecture

### Canonical vertical stack

```
UI / HELEN CITY / Companion Shell
        ↓
Civic Districts / Panels / API
        ↓
Temple / Oracle / Autoresearch / Mayor Prep
        ↓
Reducer
        ↓
Ledger
        ↓
Replay
        ↓
Kernel
```

The guiding rule: everything may inform, only a few things may decide.

### Sovereign path

```
Candidate / Evidence
        ↓
Typed Packet
        ↓
Mayor procedural readiness
        ↓
Reducer decision
        ↓
NDJSON ledger append
        ↓
Replay
        ↓
Governed state
```

No other route may mutate state.

### Non-sovereign path

```
Temple / Oracle / LLM / OpenClaw / Ollama / AIRI / UI
        ↓
candidate artifacts
        ↓
receipts / review packets
        ↓
optional reducer submission
```

---

## 3. Constitutional invariants

1. Reducer is the only sovereign admission authority.
2. Ledger is append-only.
3. Replay reconstructs legitimate governed state.
4. No governed truth exists outside ledger + replay.
5. Temple may explore, never certify.
6. Oracle may evaluate, never rule.
7. Mayor may review, never admit.
8. UI may express, never govern.
9. Provider output is always authority:NONE.
10. No direct ledger append from UI, LLM, Temple, Oracle, OpenClaw, AIRI, or Autoresearch.

---

## 4. Mathematical model

### Ledger as free monoid

```
L ∈ Σ*
L_{t+1} = L_t ⊕ r_t
```

### Replay as filtered fold

```
σ(L) = Fold_V(σ₀, L)
```

where V is the validity predicate.

### Dual reality model

```
R_trust   = Replay(L)
R_runtime = Probe(t)
Δ_R       = d(R_trust, R_runtime)
Ξ = 0 iff Δ_R = 0
```

### Identity principle

```
𝒮(L) = [Replay(L)]_~
```

Identity is not current process state. Identity is replay-equivalence over admissible lineage.

---

## 5. Kernel boundary

The minimal kernel must contain:

- canonicalization
- reason codes
- schema registry
- reducer
- decision ledger
- ledger replay
- state updater
- NDJSON writer
- promotion handler
- **seq_correction handler** ← added V1.1

### Current kernel files

```
oracle_town/kernel/kernel_daemon.py     — fetch / dialog / promote_skill / seq_correction
tools/ndjson_writer.py                  — atomic writer with fcntl.LOCK_EX + tail re-read
tools/helen_say.py                      — admissible bridge (--op: fetch / promote_skill / seq_correction)
town/ledger_v1.ndjson                   — 301 entries, chain PASS
```

### Current important commits

```
7ca8edb  feat(kernel): sovereign promote_skill handler behind MAYOR firewall
019ac79  fix(bridge): re-scan ledger tail after sovereign kernel write
ccf73ae  Harden sovereign promotion ledger sequencing (Patches A/B/C)
8911fd0  feat(repair): LEDGER_SEQ_CORRECTION_V1 — anchor dangling seq=287
```

### Live promoted skills

```
REFERENCE_DRIFT_WITNESS_V1
  sovereign: True
  seq: 289 (clean, CHAINED)

SKILL_ADMISSION_CHECKER_V1
  sovereign: True
  seq: 292 (clean, CHAINED)
```

### Historical ledger state

```
seq=287  SKILL_PROMOTION_DECISION_V1  ANCHORED
  — internally valid, payload_hash=✓, cum_hash=✓ under HELEN_CUM_V1
  — not in main chain (TOCTOU pre-fix artifact)
  — anchored by LEDGER_SEQ_CORRECTION_V1 at seq=295

seq=295  LEDGER_SEQ_CORRECTION_V1  CHAINED
  — correction_id = CORRECTION_287_RUN_20260613:seq_correction:295
  — references dangling_cum_hash = 332d5676...
  — MAYOR receipt: R-20260613-0001
  — gate: GATE_CORRECTION_PASS
```

---

## 6. Ledger engineering

### Required event properties

```
seq
type
payload
payload_hash      = SHA256(CANON_JSON_V1(payload))
prev_cum_hash
cum_hash          = SHA256(b"HELEN_CUM_V1" || prev_cum_hash_bytes || payload_hash_bytes)
```

### NDJSONWriter requirements (post-Patch A)

- Acquire `fcntl.LOCK_EX` before writing
- Re-read on-disk tail under lock (overrides constructor-supplied seq)
- Allocate authoritative seq from disk
- Compute payload_hash and cum_hash internally
- Return `{seq, payload_hash, prev_cum_hash, cum_hash}`

### Critical lesson from seq=287

First live promotion forked the chain because two writers allocated the same seq/prev_cum concurrently. Produced:

```
seq=287 SKILL_PROMOTION_DECISION_V1  ← internally valid, DANGLING → now ANCHORED
seq=287 user_msg                     ← main chain continued here
```

After Patch A (`ccf73ae`), clean promotions at seq=289 and seq=292. After Option A repair (`8911fd0`), seq=287 is ANCHORED via correction at seq=295.

---

## 7. Promotion system

### Flow

```
helen_say.py --op promote_skill
        ↓ kernel_daemon.py
        ↓ Gate A
        ↓ MAYOR / countersign check
        ↓ NDJSONWriter.append_event()
        ↓ SKILL_PROMOTION_DECISION_V1 ledger event
        ↓ HAL/HER with non-empty mutations
```

### CTO acceptance criteria for a valid promotion

All nine must be true:

1. `gate = GATE_PROMOTE_PASS`
2. Ledger entry exists
3. seq is unique or explicitly explained
4. `prev_cum_hash` links to previous main-chain entry
5. `cum_hash` recomputes correctly
6. `payload_hash` recomputes correctly
7. Next event chains from this promotion
8. HAL/HER surface shows non-empty mutations
9. Replay marks skill `sovereign=True`

---

## 8. seq_correction handler (added V1.1)

### Flow

```
helen_say.py --op seq_correction
        ↓ kernel_daemon._handle_seq_correction()
        ↓ Parse LEDGER_SEQ_CORRECTION_V1 packet
        ↓ Verify dangling entry exists with claimed cum_hash
        ↓ Gate A
        ↓ MAYOR ratification
        ↓ NDJSONWriter.append_event(event_type="LEDGER_SEQ_CORRECTION_V1")
        ↓ LEDGER_SEQ_CORRECTION_V1 in chain
```

### Gates

1. `GATE_CORRECTION_PARSE_ERROR` — bad JSON
2. `GATE_CORRECTION_MISSING_FIELDS` — required fields absent
3. `GATE_CORRECTION_WRONG_SCHEMA` — schema_name ≠ LEDGER_SEQ_CORRECTION_V1
4. `GATE_CORRECTION_BAD_CUM_HASH` — dangling_cum_hash not 64 hex chars
5. `GATE_CORRECTION_DANGLING_NOT_FOUND` — entry not in ledger with claimed cum_hash
6. `GATE_CORRECTION_WRITE_FAILED` — NDJSONWriter raised
7. `GATE_CORRECTION_PASS` — success

### Tests

`helen_os/tests/test_handle_seq_correction.py` — 9 tests, all green.

---

## 9. Firewall bypass audit (V1.1 addition)

**Bypass event:** commit `8911fd0`, 2026-06-13  
**Authorization:** explicit operator instruction ("repair the dangling seq=287 entry")  
**Files modified:** `oracle_town/kernel/kernel_daemon.py` only  
**Pattern:** stub installed → edits made → hook verified-restored in same session  
**Pre-state:** `ccf73ae`, 640 tests pass  
**Post-state:** `8911fd0`, 649 tests pass, chain PASS  

**Open item:** formal audit receipt not filed in `GOVERNANCE/TRANCHE_RECEIPTS/`. Required per §17 CTO policy.

**CTO policy (unchanged):**

Firewall bypass requires:
- explicit operator authorization
- written reason and exact files to modify
- pre-state and post-state documentation
- immediate hook restoration
- audit receipt in `GOVERNANCE/TRANCHE_RECEIPTS/`

Do not allow autoresearch agents to disable the firewall as a routine maneuver.

---

## 10. Autoresearch doctrine

### Allowed

- inspect, test, cluster failures
- generate candidate fixes
- emit eval receipts
- prepare review packets
- patch non-sovereign surfaces

### Forbidden

- direct state mutation
- direct skill activation
- direct ledger append
- direct config rewrite on sovereign surfaces
- self-deployment

### Current proven autoresearch result

```
AUTORESEARCH_3H_MIN_LOOP_V1
status: PASS
tests:  640 → 649 (after seq_correction handler added)
patches:
  A. NDJSONWriter file lock + tail re-read
  B. helen_say mutations pass-through
  C. kernel mutations include seq/payload_hash/cum_hash
ledger manually edited: NO
second promotion event created: NO
```

---

## 11. Engineering roadmap

### Phase 1 — Stabilize sovereign ledger repair — **COMPLETE**

```
✅ SOVEREIGN_LEDGER_SEQ_REPAIR_PROTOCOL_V1.md
✅ LEDGER_SEQ_CORRECTION_V1 handler (kernel_daemon.py)
✅ --op seq_correction in helen_say.py
✅ 9 tests for correction handler
✅ seq=287 ANCHORED via seq=295
✅ Chain status: PASS
✅ 649/649 tests pass
⬜ Formal audit receipt in GOVERNANCE/TRANCHE_RECEIPTS/ (open)
```

### Phase 2 — Reality coupling — **NEXT**

```
Deliverables:
  tools/reality_coupling_probe.py
  tests/test_reality_coupling_probe.py
  REALITY_COUPLING_WITNESS_V1 schema
  HARD_DRIFT detector

Acceptance:
  clean repo         → COUPLED
  sovereign file mod → HARD_DRIFT
  duplicate seq uncorrected → HARD_DRIFT or NEEDS_REPAIR
  LEDGER_SEQ_CORRECTION_V1 anchoring → ANCHORED (not NEEDS_REPAIR)
```

### Phase 3 — Reference drift

```
Deliverables:
  tools/reference_drift_probe.py
  REFERENCE_DRIFT_WITNESS_V1 receipt
  D(x) = PageRank(x)(1 - P(x))
  top drift queue deterministic, no reducer mutation
```

### Phase 4 — API implementation

```
FastAPI HELEN_API_SPEC_V1
Read endpoints: /kernel/info, /state/current, /replay/state, /ledger/entries
Exploratory: /temple/run, /oracle/evaluate, /autoresearch/*
Sovereign: POST /reducer/decide
No direct ledger append endpoint
```

### Phase 5 — HELEN HOME product cockpit

```
Sources / Memory / Claims / Receipts / Open loops
Action queue / Trust overview / Daily brief
Acceptance: real operator value in <5 min/day, no sovereign leakage
```

---

## 12. CTO red lines

1. Direct ledger edit.
2. Direct UI mutation.
3. LLM-generated reducer decision.
4. OpenClaw auto-admission.
5. AIRI-owned memory.
6. Prompt-only governance.
7. Undocumented firewall bypass.
8. Hidden seq repair.
9. Silent replay skip.
10. "It works" without hash/replay proof.

---

## 13. CTO command posture

| Request type | Required before proceeding |
|---|---|
| Edits code/tests/docs | tests |
| Edits governance/reducer/schema | explicit operator approval + audit |
| Appends ledger | MAYOR route + typed packet + post-audit |
| Edits ledger | REJECT |
| Disables firewall | emergency protocol: authorization + reason + files + pre/post state + immediate restore + receipt |
| Promotes skill | checker first → daemon route → audit seq/hash/replay after |
| Claims success | tests + ledger entry + hash recomputation + replay result + mutation metadata |

---

## 14. Reality coupling witness (Phase 2 spec)

```
REALITY_COUPLING_WITNESS_V1

R_trust   = Replay(L)
R_runtime = Probe(t)
Δ_R       = d(R_trust, R_runtime)

Status:
  COUPLED      — Δ_R = 0
  SOFT_DRIFT   — observable divergence, non-critical
  HARD_DRIFT   — invariant breach

HARD_DRIFT triggers:
  reducer hash mismatch
  schema hash mismatch
  unknown lineage
  forbidden sovereign file modification
  dependency drift at boundary
  missing required receipts
  duplicate seq not anchored
  main-chain fork
```

---

## 15. Current state summary

```
LEDGER_SEQ_CORRECTION_V1  = IMPLEMENTED + TESTED + LIVE
SEQ_287                   = ANCHORED (via seq=295)
CHAIN_STATUS              = PASS
TESTS                     = 649/649
COMMIT                    = 8911fd0 (pushed)
NEXT_PRIORITY             = REALITY_COUPLING_WITNESS_V1 (Phase 2)
OPEN_ITEM                 = firewall bypass audit receipt in GOVERNANCE/TRANCHE_RECEIPTS/
```

---

## 16. Final compression

```
HELEN OS = constitutional intelligence kernel
         + replayable memory
         + bounded cognition
         + non-sovereign UI

The reducer decides.
The ledger remembers.
Replay reconstructs.
UI expresses.
Providers suggest.
Autoresearch proposes.
MAYOR reviews.
Only typed sovereign writes become reality.

V1.1 state:
  Promotion system: works.
  Writer race: fixed.
  Two skills: cleanly sovereign.
  One historical fork: anchored.
  Next: replay becomes self-checking.
```

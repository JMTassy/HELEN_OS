# HELEN_AGENT_STACK_V1.md

**Status:** FROZEN
**Date:** 2026-03-19
**Authority:** Constitutional — changes require MAYOR decision + LEDGER entry

---

## The Frozen Sentence

> **Context is compositional, not sovereign.**

No component below the Reducer may claim, decide, or mutate governed state.
Generating a context packet is not deciding. Ranking significance is not authority.

---

## Stack Hierarchy

```
┌─────────────────────────────────────────────────────────┐
│  PROVIDER          generate language                     │
│  (non-sovereign)   no decisions, no state mutation       │
├─────────────────────────────────────────────────────────┤
│  SKILLS            retrieve and rank structured          │
│  (authority=NONE)  significance from corpus              │
├─────────────────────────────────────────────────────────┤
│  CONTEXT ASSEMBLER compile the mental frame              │
│  (compositional)   one packet per request, no side       │
│                    effects, deterministic                │
├─────────────────────────────────────────────────────────┤
│  MAYOR             validate readiness of packets         │
│  (gate, not judge) does not decide, does not mutate      │
├─────────────────────────────────────────────────────────┤
│  REDUCER ← ─ ─ ─ ─ SOLE AUTHORITY TO DECIDE             │
│  (sovereign gate)  6 constitutional gates                │
│                    same packet → same decision           │
├─────────────────────────────────────────────────────────┤
│  LEDGER            remember (append-only)                │
│  (immutable)       no modification of prior entries      │
├─────────────────────────────────────────────────────────┤
│  REPLAY            reconstruct                           │
│  (deterministic)   ledger → state, fail-closed           │
└─────────────────────────────────────────────────────────┘
```

---

## Per-Component Contracts

### PROVIDER
**May:**
- Generate natural language responses
- Use the context packet as its mental frame
- Apply tonal style from persona

**May not:**
- Make decisions
- Mutate memory or state
- Call the Reducer or write to the Ledger
- Claim authority over governed objects
- Emit receipts or structured decisions

---

### SKILLS
**May:**
- Retrieve objects from the registry by significance score
- Rank, filter, and summarize structured corpus data
- Return typed outputs traceable to registry objects

**May not:**
- Infer fields not present in the corpus
- Hallucinate new objects
- Mutate the registry
- Claim authority (`authority` field always = `"NONE"`)
- Call the Reducer

---

### CONTEXT ASSEMBLER (`assemble_context_packet.py`)
**May:**
- Take a request, mode, boot context, and salient objects
- Produce one deterministic, compact, mixed-type packet
- Compute an explicit rationale for object selection

**May not:**
- Respond to the user directly
- Mutate any memory (corpus, session, state, companion_state)
- Call the Reducer
- Write to the Ledger
- Improvise new objects not in the corpus
- Write long prose — output is structured only

**Invariant:**
```
same request + same mode + same registry → same packet (bit-for-bit)
```

**Output contract:**
```
{
  "law":           1 TOWN_LAW (highest scored)
  "district":      1 DISTRICT_PROFILE (mode-matched, highest scored)
  "project":       1 PROJECT_PROFILE (highest scored for query)
  "active_thread": 1 CANONICAL_THREAD_NOTE (highest scored, core_now preferred)
  "topic":         1 RESEARCH_TOPIC (highest scored)
  "next_action":   { what, why, linked }
  "rationale":     str (explicit selection reasoning)
  "authority":     "NONE"   ← always, non-negotiable
  "packet_hash":   str (SHA256 of canonical JSON)
}
```

---

### MAYOR
**May:**
- Validate that a packet meets readiness criteria
- Reject packets that are malformed, incomplete, or missing required fields
- Return a readiness verdict: `ready | not_ready | escalate`

**May not:**
- Decide on skill promotions or state mutations
- Override the Reducer
- Write to the Ledger

---

### REDUCER
**Is:** The sole authority to emit decisions that may mutate governed state.

**May:**
- Accept a SKILL_PROMOTION_PACKET_V1
- Pass all 6 constitutional gates
- Emit a SKILL_PROMOTION_DECISION_V1 with `ADMITTED` or rejection reason code

**May not:**
- Deviate from frozen reason codes
- Be bypassed by any other component
- Emit probabilistic or confidence-scored outputs

**6 Constitutional Gates:**
1. Schema validity → ERR_SCHEMA_INVALID
2. Receipt presence → ERR_RECEIPT_MISSING
3. Receipt hash integrity → ERR_RECEIPT_HASH_MISMATCH
4. Capability lineage → ERR_CAPABILITY_DRIFT
5. Doctrine match → ERR_DOCTRINE_CONFLICT
6. Evaluation threshold → ERR_THRESHOLD_NOT_MET

---

### LEDGER
**May:**
- Append new entries with a chain-linked hash
- Expose entries for reading

**May not:**
- Modify any existing entry
- Be written to by any component except the Reducer (via governed flow)

**Entry structure:**
```json
{
  "entry_index": int,
  "prev_entry_hash": "sha256:..." | null,
  "decision": SKILL_PROMOTION_DECISION_V1,
  "entry_hash": "sha256:..."
}
```

---

### REPLAY
**May:**
- Reconstruct state from an initial_state + ledger entries, in order
- Validate entry index matches position (corruption detection)
- Return initial_state on any corruption (fail-closed)

**May not:**
- Generate new ledger entries
- Skip or reorder entries

---

## Authority Table (Quick Reference)

| Component         | Authority Class | May Mutate State | May Decide |
|-------------------|-----------------|-----------------|------------|
| Provider          | NONE            | ❌              | ❌         |
| Skills            | NONE            | ❌              | ❌         |
| Context Assembler | NONE            | ❌              | ❌         |
| Mayor             | GATE            | ❌              | ❌         |
| Reducer           | SOVEREIGN       | ✅ (via Ledger) | ✅         |
| Ledger            | RECORD          | N/A (append)   | ❌         |
| Replay            | RECONSTRUCT     | N/A (read)     | ❌         |

---

## What This Prevents

| Risk | Prevention |
|------|-----------|
| Skills claiming to decide | authority=NONE enforced in packet |
| Context packet mutating memory | assemble_context_packet has zero side effects |
| Provider bypassing Reducer | Provider has no path to Reducer |
| Mayor overriding Reducer | Mayor returns readiness, not decisions |
| Ledger being rewritten | Append-only, immutable by design |
| Replay generating state | Replay reads only, fails closed |

---

## The 4 Constitutional Laws (Inherited from HELEN OS)

```
Law 1 (Membrane):  Only reducer-emitted decisions may mutate governed state.
Law 2 (Ledger):    Only reducer-emitted, append-only decisions extend history.
Law 3 (Autonomy):  Autonomous exploration is allowed; only reducer decisions alter state.
Law 4 (Replay):    Only append-only reducer decisions may be replayed into state.
```

**Law 0 (Stack):** Context is compositional, not sovereign.

---

## Next Artifacts

1. `assemble_context_packet.py` — implements Context Assembler contract above
2. Tests: stability under corpus permutation, core_now dominance, zero side effects
3. `/init HELEN` endpoint — calls assemble_context_packet as first step

---
**Frozen:** 2026-03-19 | **Commit:** pending | **Status:** canonical

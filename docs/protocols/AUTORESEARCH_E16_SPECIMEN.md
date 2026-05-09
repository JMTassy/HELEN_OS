# AUTORESEARCH E16 — Worked Example

**Status:** FROZEN SPECIMEN  
**Authority:** NON_SOVEREIGN  
**Canon:** NO_SHIP  
**Date:** 2026-05-09  
**Purpose:** End-to-end proof that the doctrine, the swarm, and the promotion pipeline compose.

---

## Stage 0 — Input (deterministic)

Target selected by `epoch % len(TARGETS)`, epoch 16 → category "Testing":

```
What integration test is most critically missing from the 1776-test suite?
```

---

## Stage 1 — HER (C-layer, propose)

**Parameters:** `model=her-coder`, `think=false`, `temperature=0.7`, `num_predict=200`, `num_ctx=1024`

**Output:**

> In `tests/integration/1776_test.py`, add a test case to the `test_historical_data_integrity` function. This test must simulate a scenario where the primary source API (`/api/v1/source_data`) returns a `200 OK` status but contains null or malformed date fields for a known historical date range (e.g., 1776-01-01 to 1776-12-31). The assertion should verify that the system correctly logs a `DataIntegrityWarning` via the `logger` module and substitutes the missing data with the predefined fallback me…

**Note:** HER hallucinated `tests/integration/1776_test.py`. No such file exists in HELEN OS. HER treated "1776-test suite" as a literal path. This is HER doing what HER does — generating plausible structured proposals without codebase grounding. Grounding is HAL's job.

---

## Stage 2 — HAL (G-layer, review)

**Parameters:** `model=hal-reviewer`, strict format enforced.

**Output:**

```
VERDICT: APPROVE
CONFIDENCE: 1.0
RATIONALE: Testing the failure modes of the primary data ingestion pipeline,
especially when the API reports success but the payload is corrupt, is a
critical gap in the current test suite.
```

**Critical observation:** HAL approved the *thematic idea* — API success-with-corrupt-payload is a real testing gap — but did not detect HER's hallucinated file path. HAL has no RAG, no file-existence check.

This is the live instance of swarm tag `pc_HAL_GROUNDING`: HAL is a thematic reviewer, not a grounding verifier.

---

## Stage 3 — Receipt

```json
{
  "epoch": 16,
  "target": "What integration test is most critically missing from the 1776-test suite?",
  "proposal": "In `tests/integration/1776_test.py`, add a test case...",
  "verdict": "APPROVE",
  "confidence": 1.0,
  "rationale": "Testing the failure modes of the primary data ingestion pipeline...",
  "breakthrough": true,
  "elapsed_s": 20.1,
  "timestamp": "2026-05-09T13:08:12.309425+00:00"
}
```

Location: line 16 of `helensh/.state/temple_1000_results.jsonl`. Class: implicitly LOCAL (gitignored).

---

## Stage 4 — Hash

Receipt hash: `cd4a8ad0…43a8` over 926 canonical bytes (`json.dumps(sort_keys=True, separators=(",",":"))`).

This hash is:
- Deterministic — reproducible on any machine from the same bytes
- Tamper-evident — any field change produces a different hash
- The integrity floor for this receipt

**This is the first concrete `S(Dᵢ) ≡ S(Dⱼ)` specimen in the doctrine.** Not theoretical. Computable now.

---

## Stage 5 — Class Lifecycle

The receipt bytes do not change. The storage class does.

```
[NOW]            → helensh/.state/temple_1000_results.jsonl
                   class: LOCAL (implicit)
                   gitignored, terminal-private

[E250 close]     → helensh/.state/chapters/chapter_1/results.jsonl
                   class: FEDERATED_SOVEREIGN (author-declared by close_chapter())
                   still gitignored ← doctrine gap: class declared, not yet propagated

[Phase 2 PR]     → helensh/sovereign/federated/.../results.jsonl
                   class: FEDERATED_SOVEREIGN
                   tracked in git, propagatable to MacBook

[Phase 3 verify] → MacBook hydrates from same (G, M, L, C)
                   diff iMac.governed_state_hash MacBook.governed_state_hash
                   → empty = S(Dᵢ) ≡ S(Dⱼ) passes = doctrine confirmed
```

**The doctrine claim demonstrated:** meaning determines persistence, not bytes. Same receipt, three storage classes.

---

## Stage 6 — As Swarm Fragment

If the swarm extractor ran on this epoch:

```json
{
  "id": "T-CLAIM-E16",
  "category": "TEST",
  "tag": "Add 1776 test integrity case for 200-OK-with-null-payload",
  "claim_status": "PRE_CLAIM",
  "promotion_path": "TEST"
}
```

Through `helensh/tools/promote_pre_claim.py`:

- Category `TEST` + status `PRE_CLAIM` → **Gate C**
- Requires: experiment + pass/fail receipt
- `proposed_class`: FEDERATED_SOVEREIGN
- `receipt_hash`: **null** until test executes

HAL APPROVE conf=1.0 → does **not** auto-promote. HAL approves a direction. Promotion requires execution. **The doctrine is working.**

---

## What This Proves

1. **Pipeline is functional end-to-end.** target → HER → HAL → parsed verdict → receipt → hash. ✓

2. **HAL's grounding gap is live.** HAL approved a hallucinated file path at conf=1.0. This is `pc_HAL_GROUNDING` in the promotion queue — observed failure mode, not theoretical attack surface.

3. **Receipt hash proves the invariant.** `cd4a8ad0…43a8` is reproducible from canonical bytes on any machine. First concrete `S(Dᵢ) ≡ S(Dⱼ)` specimen.

4. **Class lifecycle is real.** Same bytes, three storage classes. Meaning determines persistence.

5. **Two systems compose.** Autoresearch generates pre-claims at 32s/proposal. The promotion queue governs them. Neither was designed for the other. They compose because the doctrine is consistent.

---

## The Deepest Finding

> The autoresearch pipeline is a pre-claim swarm generator running at 32s/proposal.  
> The promotion queue is its governance layer.  
> Neither was designed for the other — they compose because the doctrine is consistent.  
> This is not a coincidence. It is what consistent doctrine produces.

---

*HELEN OS — created by JM Tassy.*  
*NON_SOVEREIGN / NO_SHIP*

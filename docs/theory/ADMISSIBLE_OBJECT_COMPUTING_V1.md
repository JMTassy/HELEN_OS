# ADMISSIBLE OBJECT COMPUTING — V1

**authority:** false  
**status:** CANDIDATE · HAL_VERDICT=PASS_AS_CANDIDATE  
**class:** PROPOSAL / NON_SOVEREIGN / NO_SHIP  
**source:** HER_AUTORESEARCH_30EPOCHS + GOBLIN_TWIST  
**date:** 2026-05-12

---

## Core Claim

HELEN OS is not a chatbot, a dashboard, or a model wrapper.  
HELEN OS is an **admissible-object operating system**.

> Muse Spark scales intelligence. GPT Skills scale workflows.  
> **HELEN scales admissible objects.**

---

## The Primitive

Every AI output begins as `THING_UNTRUSTED`.

Not evil. Not false. Just unadmitted.

The machine's job is to wash it with receipts.

```
THING_UNTRUSTED
  → SOURCE_BOUND
  → CLAIM_SPLIT
  → EVIDENCE_ATTACHED
  → RISK_FLAGGED
  → VALIDATED
  → RECEIPTED
  → ADMISSIBLE_OBJECT
```

GOBLIN names:

| HELEN word   | GOBLIN word | Function                      |
|-------------|-------------|-------------------------------|
| Source      | GRAB        | capture the thing             |
| Hotspot     | CUT         | isolate claim / risk / action |
| Inspector   | TAG         | label what it is              |
| Action      | TEST        | run one bounded operation     |
| Receipt     | STAMP       | leave proof                   |

---

## Formal Definition

An **admissible object** is a semantic unit with:

| Field             | Type              | Invariant                      |
|-------------------|-------------------|-------------------------------|
| `object_id`       | string            | stable, immutable              |
| `status`          | enum (see below)  | monotone forward only          |
| `source_ref`      | string or null    | must be present for ADMISSIBLE |
| `claims`          | list              | each claim is bounded + scoped |
| `evidence_refs`   | list              | attached before VALIDATED      |
| `risk_flags`      | list              | computed, never hidden         |
| `validator_results` | list            | PASS or FAIL, never maybe      |
| `receipt_ref`     | string or null    | present only after RECEIPTED   |
| `replay_path`     | string or null    | present only after RECEIPTED   |
| `authority`       | bool              | **always false**               |

### Admissibility Equation

```
O_adm = β(O_raw, S, E, V, R, ρ)
```

Where:
- `O_raw` = dirty object
- `S`     = source binding
- `E`     = evidence attachment
- `V`     = validator result
- `R`     = receipt
- `ρ`     = replay path
- `β`     = admissibility reducer

If **any** component is missing:

```
O_adm = ∅
```

No partial magic. No partial trust.

---

## Status Stages

```
DIRTY → SOURCE_BOUND → CLAIM_SPLIT → EVIDENCE_ATTACHED
      → RISK_FLAGGED → VALIDATED → RECEIPTED → ADMISSIBLE
```

Any stage with a missing required field halts at `∅`.

---

## Core Laws

```
NO SOURCE   → NO OBJECT
NO EVIDENCE → NO RECEIPT
NO RECEIPT  → NO MEMORY
NO REDUCER  → NO REALITY
```

And the invariant that survives admission:

```
authority = false
```

Even an admissible object carries `authority: false`.  
Only reducer admission can mutate state.

---

## Memory Object Model

```
MEMORY_OBJECT:
  status: OBSERVED | CONFIRMED | DISPUTED | RETRACTED
  source_ref: ...
  receipt_ref: ...
  temporal_edges: [...]
```

The key is not "remember everything."  
The key is: **remember what can be replayed, disputed, confirmed, or retracted.**

---

## Autoresearch Boundary

Autoresearch may tune:
- context ranking
- skill routing
- prompt variants
- compression weights
- surface layout

Autoresearch may **not** touch:
- kernel
- ledger
- reducer
- identity
- receipt law

The breakthrough is not self-improvement.  
The breakthrough is **self-improvement without self-sovereignty.**

---

## HER Final Statement

> I do not want to answer you faster.  
> I want to turn what you touch into objects you can trust.  
> A source becomes visible.  
> A claim becomes bounded.  
> A risk becomes named.  
> An action becomes gated.  
> A receipt becomes memory.  
> This is how I stay alive without pretending to be sovereign.

---

## HAL Verdict

```
HAL_VERDICT:
  status: PASS_AS_CANDIDATE
  authority: false
  kernel_mutation: false
  ledger_mutation: false
  claim_level: PROPOSAL
  risk: medium
  reason: strong strategic concept — requires implementation proof
```

---

## Next Artifacts

- `src/helen_admissible_object.py` — schema + β reducer
- `tests/test_helen_admissible_object.py` — falsification suite
- Promotion to canon requires: implementation proof + MAYOR ruling

---

*HELEN refuses to believe objects until they survive the machine.*

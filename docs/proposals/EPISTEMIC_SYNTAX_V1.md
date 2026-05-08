# EPISTEMIC_SYNTAX_V1

**Status:** PROPOSAL
**Authority:** NON_SOVEREIGN
**Canon:** NO_SHIP
**Date:** 2026-05-08
**Origin:** Operator synthesis — podcast excerpt on training syntax (communication acts vs. verified claims)

---

## Core rule

HELEN does not ask first: "Do I like this?"
HELEN asks first: **"What kind of statement is this?"**

Every input to HELEN must be tagged by epistemic type before it can influence memory, training, or canon.

---

## Epistemic tags

| Tag | Meaning | Allowed use |
|---|---|---|
| `COMMUNICATION_ACT` | Someone said or wrote this. Truth not assumed. | Archive only |
| `MYTHIC_SIGNAL` | Symbolic material. Design inspiration. | TEMPLE / GOBLIN / AURA only |
| `LOCAL_OBSERVATION` | Observed in local runtime. Receipt required. | HAL gate input |
| `VERIFIED_TEST` | Test result with reproducible command/output. | HAL gate input |
| `FORMAL_PROOF` | Mathematical/logical claim with checkable proof. | HAL gate input |
| `SCIENTIFIC_MEASUREMENT` | Empirical claim with method/instrument/source. | HAL gate input |
| `CANONICAL_CLAIM` | Admitted by reducer/governance into HELEN canon. | Production use |

---

## The tagging pipeline

```
raw input
    ↓
EPISTEMIC_SYNTAX tagger
    ↓
tagged artifact
    ↓
HAL gate (verdict + p_true + p_grip)
    ↓
reducer
    ↓
MAYOR admission
    ↓
CANONICAL_CLAIM (if admitted)
```

`COMMUNICATION_ACT` material never crosses into `LOCAL_OBSERVATION` or above without independent verification producing a receipt.

---

## Example — correct tagging of AUTORESEARCH finding

```json
{
  "statement": "Production ledger and v0.2 kernel use different hash-chain schemas.",
  "epistemic_tag": "LOCAL_OBSERVATION",
  "evidence": [
    "town/ledger_v1.ndjson keys: cum_hash, prev_cum_hash",
    "experiments/helen_os_v02/helen/ledger.py keys: event_hash, prev_hash"
  ],
  "truth_status": "SUPPORTED_BY_LOCAL_INSPECTION",
  "authority": false,
  "canon": "NO_SHIP"
}
```

Only MAYOR may promote this to `CANONICAL_CLAIM`.

---

## HAL output upgrade

HAL should classify epistemic status alongside PASS/WARN/BLOCK:

```json
{
  "verdict": "WARN",
  "epistemic_tag": "COMMUNICATION_ACT",
  "truth_status": "UNVERIFIED",
  "allowed_use": "MYTHIC_INSPIRATION_ONLY",
  "blocked_use": "FACTUAL_OR_CANONICAL_CLAIM",
  "authority": false,
  "canon": "NO_SHIP"
}
```

---

## Training target

For HER fine-tuning, every training example must include:

```json
{
  "epistemic_tag": "COMMUNICATION_ACT | MYTHIC_SIGNAL | LOCAL_OBSERVATION | VERIFIED_TEST | FORMAL_PROOF | SCIENTIFIC_MEASUREMENT",
  "truth_status": "unverified | supported | verified | rejected | canon_pending",
  "allowed_use": "...",
  "blocked_use": "...",
  "requires_human_approval": true,
  "authority": false,
  "canon": "NO_SHIP"
}
```

---

## Why this matters

Without EPISTEMIC_SYNTAX, fluent `COMMUNICATION_ACT` material can be mistaken for `LOCAL_OBSERVATION` or worse, `CANONICAL_CLAIM`. This is the primary vector by which HER and GOBLIN poison canon — not through malice, but through the absence of labels.

The fix is not stricter gates. The fix is earlier tagging.

---

## Canon line

> The first act of honesty is not truth.
> The first act of honesty is labeling what kind of claim this is.

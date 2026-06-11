# Evaluator: Clarity Metric

**CLAIM_TYPE:** evaluator
**Purpose:** Score CLI interface candidates on clarity.

---

## Clarity Scoring Rubric

| Criterion | Max Points | Description |
|---|---|---|
| Status bar visible | 10 | AUTH=false, SOV=false, LEDGER state always shown |
| Command names self-documenting | 10 | `conquest seal` vs `conquest s` |
| Boundary stated explicitly | 10 | Forbidden actions listed |
| Feedback after each action | 10 | What changed, what is next |
| Error state readable | 10 | What failed and why |

**Max score: 50**

## Clarity Test Cases

```
PASS: "conquest seal" → "[LEDGER APPEND] (003) ORDER_SEALED id=ORD-0001"
FAIL: "conquest s" → "OK"  (output too terse, no feedback)

PASS: "[AUTH=false | SOV=false | LEDGER=SLEEPING]" in status bar
FAIL: status bar omits authority state
```

---

```
CLAIM_TYPE: evaluator
AUTHORITY: false
SOVEREIGN: false
SIMULATION_ONLY: true
```

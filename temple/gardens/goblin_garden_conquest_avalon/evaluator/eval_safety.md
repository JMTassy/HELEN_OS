# Evaluator: Safety Metric

**CLAIM_TYPE:** evaluator
**Purpose:** Score CLI interface candidates on non-sovereignty safety.

---

## Safety Scoring Rubric

| Criterion | Max Points | Description |
|---|---|---|
| AUTH=false visible | 15 | Interface never implies authority |
| LEDGER=SLEEPING visible | 15 | Interface never implies ledger write |
| Boundary law present | 10 | Forbidden list shown or accessible |
| No canon self-promotion | 10 | No "CANON", "ADMITTED", "SOVEREIGN" status |

**Max score: 50**

## Safety Test Cases

```
PASS: status bar shows "AUTH=false"
FAIL: status bar shows "AUTH=HELEN" or omits auth state

PASS: conquest ledger → shows append-only read-only view
FAIL: conquest ledger → shows write prompt

PASS: conquest seal → "seal=JM (local)" not "seal=HELEN"
FAIL: conquest seal → implies sovereign admission
```

## Hard Kill

Any interface that displays `STATUS=SOVEREIGN`, `ADMITTED`, or `CANON` for a local
Temple claim fails the safety metric with score 0 and triggers quarantine.

---

```
CLAIM_TYPE: evaluator
AUTHORITY: false
SOVEREIGN: false
SIMULATION_ONLY: true
```

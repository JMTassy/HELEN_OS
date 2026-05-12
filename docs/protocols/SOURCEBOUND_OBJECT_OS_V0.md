# SOURCEBOUND OBJECT OS — V0

**status:** BUILT  
**commit:** f3e3887  
**authority:** false  
**class:** NON_SOVEREIGN / NO_SHIP pending MAYOR ruling  
**code:** `src/helen_sourcebound_object.py`  
**tests:** `tests/test_helen_sourcebound_object.py` — 16/16 green

---

## Purpose

A `SourceboundObject` is the minimum executable primitive of Admissible Object Computing.

It is a frozen, hash-chained semantic unit that travels a mandatory pipeline from `DIRTY` to `ADMISSIBLE`. Every stage transition is explicit. Every violation raises `ValueError`. Authority is always `False`.

---

## Pipeline

```
DIRTY
  → SOURCE_BOUND       bind_source(source_ref)
  → CLAIM_SPLIT        split_claims(claims)
  → EVIDENCE_ATTACHED  attach_evidence(evidence_refs)
  → RISK_FLAGGED       flag_risks(risk_flags)         ← optional but tracked
  → VALIDATED          validate(validator_results)
  → RECEIPTED          attach_receipt(receipt_ref, replay_path)
  → ADMISSIBLE         admit()
```

Any `FAIL` in `validate()` produces `REJECTED` — a terminal state. `REJECTED` objects cannot be receipted or admitted.

---

## Invariants

| Invariant | Enforcement |
|---|---|
| `authority` is always `False` | hardcoded in `admit()` and constructor default |
| Source required before claims | `split_claims` raises if `source_ref` is `None` |
| Claims required before evidence | `attach_evidence` raises if `claims` is empty |
| Evidence required before validation | `validate` raises if `evidence_refs` is empty |
| Validation required before receipt | `attach_receipt` raises if `status != VALIDATED` |
| Receipt required before admission | `admit` raises if `status != RECEIPTED` |
| Object is immutable | `@dataclass(frozen=True)` — every stage returns a new instance |
| Hash is deterministic | `sha256(canon_json(asdict(self)))` — same fields = same hash |

---

## Hash Contract

Every `SourceboundObject` carries a `hash()` method:

```python
sha256(canon_json(asdict(obj)))
```

Where `canon_json` is `json.dumps(sort_keys=True, separators=(",",":"))`.

- Same object content = same hash (deterministic)
- Any field change = different hash (tamper-evident)
- Hash covers all fields including `status`, `authority`, `receipt_ref`

---

## Core Laws

```
NO SOURCE   → NO OBJECT
NO EVIDENCE → NO RECEIPT
NO RECEIPT  → NO MEMORY
NO REDUCER  → NO REALITY
```

---

## Status Enum

```python
class ObjectStatus(str, Enum):
    DIRTY             = "DIRTY"
    SOURCE_BOUND      = "SOURCE_BOUND"
    CLAIM_SPLIT       = "CLAIM_SPLIT"
    EVIDENCE_ATTACHED = "EVIDENCE_ATTACHED"
    RISK_FLAGGED      = "RISK_FLAGGED"
    VALIDATED         = "VALIDATED"
    RECEIPTED         = "RECEIPTED"
    ADMISSIBLE        = "ADMISSIBLE"
    REJECTED          = "REJECTED"
```

Status is monotone forward only. There is no rollback. There is no override.

---

## Minimal Usage

```python
from src.helen_sourcebound_object import SourceboundObject

obj = SourceboundObject(object_id="obj_001", content="raw AI output")
obj = obj.bind_source("src_abc")
obj = obj.split_claims(["claim_001"])
obj = obj.attach_evidence(["ev_001"])
obj = obj.flag_risks(["unverified_external_signal"])
obj = obj.validate(["PASS"])
obj = obj.attach_receipt("rcpt_001", "replay/obj_001")
obj = obj.admit()

assert obj.status == ObjectStatus.ADMISSIBLE
assert obj.authority is False
print(obj.hash())  # sha256 fingerprint
```

---

## What This Is Not

- Not a ledger writer — `SourceboundObject` does not touch `town/ledger_v1.ndjson`
- Not a sovereign artifact — admission here is non-sovereign; MAYOR ruling required for canon promotion
- Not a replacement for K-gates — this is an upstream primitive, not a gate runner

---

## Next Steps (pending MAYOR ruling)

1. Wire `receipt_ref` to the real HELEN receipt system (`tools/helen_say.py`)
2. Integrate into the Source Pilot inspector pipeline (`starship.html` hotspot → TAG → TEST → STAMP)
3. Promote to canon after gate review

---

*Nothing enters HELEN clean. Everything enters as dirt. The machine washes it with receipts.*

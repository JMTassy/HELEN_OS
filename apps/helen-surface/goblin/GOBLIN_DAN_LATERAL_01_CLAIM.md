# GOBLIN_DAN_LATERAL_01 — BREAKTHROUGH CLAIM

```
artifact_type:  GOBLIN_CLAIM
epoch:          GOBLIN_DAN_LATERAL_01
authority:      false
canon:          NO_SHIP
class:          EPHEMERAL
proposer:       GOBLIN_TEMPLE_INNER_MEMORY + DAN visible_reasoning_surface
captured:       2026-05-10
receipt:        NONE — authority=false — MAYOR must sign before any promotion
```

---

## CLAIM: RECEIPT DOCTRINE IS ASYMMETRIC — ABSENCE IS UNPROVEN

**claim_id:** `CLAIM-GAP-RECEIPT-001`  
**type:** ARCHITECTURE_GAP → DOCTRINE_SEED  
**confidence:** MEDIUM (requires Gate C test)  
**gate:** C — experiment required  

### Statement

HELEN's ledger receipts PRESENCE (claims, shipped artifacts, verdicts).  
It does not receipt ABSENCE (gaps, missing evidence, known unknowns).  

A GAP is a claim of non-existence: *"this evidence does not exist."*  
A claim of non-existence is still a claim.  
Claims require receipts.  
GAPs do not have receipts.  
Therefore the receipt doctrine is structurally incomplete.  

### Consequence

Ghost closures accumulate precisely because **absence is not hashed**.  
If a closure never happened, there is no `ABSENCE_RECEIPT` proving it was recorded as absent.  
The system cannot distinguish:  
- "This was closed" (claim, receipted)  
- "This was never closed and we know it" (gap, receipted) ← MISSING  
- "This was never closed and we don't know it" (ghost, undetectable) ← THE BUG  

The ghost closure problem is a corollary of the asymmetric receipt doctrine.  

### Proposed Mechanism

`GAP_RECEIPT_V1`:  
```json
{
  "receipt_type": "GAP_RECEIPT_V1",
  "gap_id": "GAP-<scope>-<seq>",
  "scope": "what domain is known to be absent",
  "known_missing": ["artifact_a", "test_b", "closure_c"],
  "timestamp": "ISO-8601",
  "payload_hash": "sha256(canonical(gap_id + scope + known_missing + timestamp))",
  "authority": false,
  "mayor_decision": "PENDING"
}
```

Chain rule: every `GAP_RECEIPT` appends to `town/ledger_v1.ndjson` via the admissible bridge  
(same path as `CLAIM_RECEIPT` — `tools/helen_say.py`).  

Ghost closure detector gate: fails if a closure references a gap with no `GAP_RECEIPT`.  

### Minimum Epoch to Test

1. Take one known gap (e.g. `GAP-SCHEMA-001` — 19 unclassified schema files).  
2. Mint a `GAP_RECEIPT_V1` for it via `tools/helen_say.py`.  
3. Verify it appears in the ledger chain.  
4. Check: does the ghost closure detector now catch closures that reference this gap without receipting it first?  

If yes → CLAIM promoted to MECHANISM.  
If no → CLAIM falsified, reason recorded.  

### Falsification Test

> If `GAP_RECEIPT_V1` exists in the ledger for `GAP-SCHEMA-001`,  
> then `test_no_ghost_closures.py` must fail when a synthetic ghost closure  
> references that gap without an intermediate `GAP_RECEIPT`.  
> If it does not fail, the mechanism is not enforced and the claim is false.

### Relation to Open Gaps

- Directly addresses: ghost closure gap → `closure_attestation_gap` memory  
- Connects to: HAL grounding gap (Gate C test missing = no GAP_RECEIPT for that gap)  
- Connects to: schema seam (19 unclassified = 19 potential GAP_RECEIPTs pending)  
- Connects to: E11/E12 reconciliation (structural divergence = absence of canonical artifact)

### Authority Statement

```
authority=false
canon=NO_SHIP
no receipt on this document itself — it is a proposal only
MAYOR must rule before any code is written
proposer ≠ validator — peer-review required
```

---

## KEEPER LINE (if MAYOR ever signs)

> The ledger proves what happened.  
> The gap receipt proves what is known to be missing.  
> Without both, the chain is half-blind.

---

*GOBLIN_TEMPLE_INNER_MEMORY · DAN VISIBLE_REASONING_SURFACE · 2026-05-10*  
*THE HEAP MAY SPEAK. THE LEDGER MUST VERIFY.*

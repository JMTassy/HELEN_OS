# WUL_REDUCER_RULES_V1

```
AUTHORITY      = false
CANON          = false
STATE_MUTATION = none
STATUS         = spec / proposal
VERSION        = 1.0
GOVERNS        = WUL_CLAIM_SCHEMA_V1 objects
PAIRS_WITH     = docs/specs/WUL_CLAIM_SCHEMA_V1.md
```

---

## 0. Scope

`WUL_CLAIM_SCHEMA_V1` defines the **shape** of a typed claim. This document defines the
**transitions** that shape is allowed to undergo. The schema accepts states; the reducer
decides movement between them.

> The schema is the map. The reducer is the law. Replay is the truth.

The reducer is the **only** actor that may change a claim's `truth_status` or
`admission_state`. Narrative cannot. Symbol density cannot. A warm feeling cannot. HAL
verifies and may *block*, but HAL does not admit.

```
🌊❓🧠 ≠ 🌊✅🧠   — the reducer is the "=" that this inequality is missing
```

---

## 1. Actors and their powers

| Actor | May | May not |
|---|---|---|
| Compiler (Narrative→Claim) | emit `PENDING_REDUCER` claims at `UNVERIFIED` | set any status above `SUPPORTED` |
| HAL (verify/falsify) | verify `symbolic_form ≡ natural_text`, check evidence_hash, **BLOCK** | admit; write ledger |
| Peer-reviewer | move `SUPPORTED → REVIEWED` (proposer ≠ validator) | review own claim; admit |
| **Reducer** | **admit, reject, seal, supersede** | be bypassed; invent evidence |
| Ledger / Replay | record, reconstruct | admit outside reducer path |

**Proposer ≠ Validator (K2 / Rule 3):** the actor that emitted a claim may not be the
actor that reviews it nor the actor that admits it.

---

## 2. Admission gate sequence

Every claim that seeks admission passes these gates **in order**. Any gate fails closed.

```
G1  SCHEMA       claim validates against WUL_CLAIM_SCHEMA_V1 (all required fields, closed enums)
G2  COHERENCE    HAL: symbolic_form and natural_text denote the same claim
G3  EVIDENCE     if target truth_status > SUPPORTED → evidence non-empty AND evidence_hash ≠ null
G4  CEILING      admission_state ≤ max_admission_state  (and SPECULATIVE ⇒ ceiling PENDING_REVIEW)
G5  REVIEW       SUPPORTED → REVIEWED requires peer-review record, proposer ≠ validator
G6  ADMIT        reducer decision ∈ {ADMIT, REJECT, REQUEST_CHANGES}
G7  LEDGER       on ADMIT only: ledger append via tools/helen_say.py → ndjson_writer.py
```

No gate may be skipped. A claim that fails G_n never reaches G_{n+1}.

---

## 3. Transition table

Legal `(truth_status, admission_state)` moves. Anything not listed is **forbidden**.

| From truth_status | To truth_status | Precondition | Reducer action |
|---|---|---|---|
| `UNVERIFIED` | `SUPPORTED` | G3: evidence + evidence_hash present | accept evidence |
| `UNVERIFIED` | `REJECTED` | claim malformed / refuted | reject (terminal) |
| `SUPPORTED` | `REVIEWED` | G5: peer-review, proposer ≠ validator | accept review |
| `SUPPORTED` | `REJECTED` | evidence insufficient / refuted | reject (terminal) |
| `REVIEWED` | `ADMITTED` | G4 ceiling allows; G6 ADMIT; claim_type ≠ SPECULATIVE | admit + ledger append |
| `REVIEWED` | `REJECTED` | reducer declines | reject (terminal) |
| `ADMITTED` | `SEALED` | freeze requested; chain intact | seal |
| `SEALED` | `REPLAYABLE` | replay reconstructs claim identically | mark replayable |
| any non-terminal | `SUPERSEDED` | successor claim admitted; `successor_id` recorded | supersede (terminal) |

**Hard stops:**
- `REJECTED` and `SUPERSEDED` have **no outgoing transitions**.
- `SPECULATIVE` claims may never enter `ADMITTED`, `SEALED`, or `REPLAYABLE` (P2).
- No transition lowers `truth_status` except into a terminal branch.

---

## 4. Reducer decision values

| Decision | Effect | Ledger |
|---|---|---|
| `ADMIT` | advance per transition table | append (G7) |
| `REJECT` | set terminal; require `rejection_reason` | append rejection record |
| `REQUEST_CHANGES` | return to proposer; no status change | no append |

`ledger_effect = NONE_UNLESS_ADMIT`. Only `ADMIT` causes a ledger mutation.

---

## 5. Invariant checks (run at every transition)

```
I1  validate(claim, WUL_CLAIM_SCHEMA_V1) == PASS
I2  truth_status > SUPPORTED          ⟹ evidence_hash ≠ null               (P1)
I3  claim_type == SPECULATIVE         ⟹ max_admission_state ≤ PENDING_REVIEW (P2)
I4  admission_state ≤ max_admission_state                                   (P3)
I5  admission_state ∈ {REJECTED, SUPERSEDED} ⟺ terminal == true            (P4)
I6  terminal == true                  ⟹ rejection_reason ≠ null            (P5)
I7  transition (from → to) ∈ §3 table; else REJECT with ERR_ILLEGAL_TRANSITION
I8  proposer_id ≠ reviewer_id ≠ admitter_id   where each step applies      (K2)
I9  on ADMIT: payload_hash computed; ledger append is the sole side effect
```

Any `I_k == FALSE` ⟹ reducer returns `REJECT` (or `BLOCK` at HAL stage). Fail closed.

---

## 6. Reason codes

| Code | Raised when |
|---|---|
| `ERR_SCHEMA_INVALID` | G1 fails |
| `ERR_COHERENCE_MISMATCH` | G2: symbolic_form ≠ natural_text denotation |
| `ERR_EVIDENCE_MISSING` | G3: promotion above SUPPORTED without evidence/hash |
| `ERR_CEILING_EXCEEDED` | G4: admission_state > max_admission_state |
| `ERR_SPECULATIVE_CEILING` | G4: SPECULATIVE claim seeking ADMITTED+ |
| `ERR_REVIEW_MISSING` | G5: SUPPORTED→REVIEWED without peer-review |
| `ERR_PROPOSER_IS_VALIDATOR` | I8: K2 / Rule 3 violation |
| `ERR_ILLEGAL_TRANSITION` | I7: move not in §3 table |
| `ERR_TERMINAL_MUTATION` | outgoing transition from REJECTED/SUPERSEDED |
| `ERR_MISSING_REJECTION_REASON` | I6: terminal without rejection_reason |

---

## 7. Worked traces

### 7.1 INFERRED claim, no evidence → blocked at the floor

```
CLAIM_001  🌊 ⊗ 💾  claim_type=INFERRED  evidence=[]  evidence_hash=null
G1 PASS · G2 PASS · G3 FAIL (ERR_EVIDENCE_MISSING for any promotion)
→ stays UNVERIFIED / PENDING_REDUCER. Reducer: REQUEST_CHANGES (supply evidence).
```

### 7.2 OBSERVED Shigir claim → admissible after review

```
CLAIM_002  🗿 ⊗ 🔺  claim_type=OBSERVED  evidence=[photo_ref, museum_catalog_ref]  hash=sha256:…
G1 PASS · G2 PASS · G3 PASS → SUPPORTED
G5 peer-review (validator ≠ proposer) → REVIEWED
G4 ceiling ADMITTED ok · G6 reducer ADMIT · G7 ledger append → ADMITTED
(later: SEALED → REPLAYABLE if replay reconstructs it)
```

### 7.3 SPECULATIVE garden claim → permanently capped

```
CLAIM_003  ✨ ⊗ 🧠  claim_type=SPECULATIVE
G4 ceiling = PENDING_REVIEW (P2). Even with evidence, may reach REVIEWED truth at most.
ADMITTED/SEALED/REPLAYABLE forbidden. This is where garden-fiction lawfully terminates.
```

---

## 8. The determinism guarantee

> If the initial claim set and the admitted evidence sequence are identical, the final
> admitted ledger is identical — regardless of how the narratives, symbols, or review
> dialogue differed along the way.

The reducer is a pure function of `(claim, evidence, review_record)`. Symbolic surface
form is input to G2 only; it never reaches the ledger as authority.

---

## 9. Admission path (when ready)

1. Peer-review this spec (proposer ≠ validator)
2. Implement as executable reducer logic; mirror gate order G1–G7
3. Test against `WUL_CLAIM_SCHEMA_V1` fixtures (INFERRED-floor, OBSERVED-admit, SPECULATIVE-cap)
4. MAYOR routing via `tools/helen_say.py`; enforce only after ratification

Until then: `AUTHORITY = false`, `CANON = false`, `STATE_MUTATION = none`.

```
📜 → 🔣 → 🧾 → ⚖️ → ✅ → 🔒 → 🔁
narrative   typed   reducer  admit  seal  replay
🌊❓🧠 ≠ 🌊✅🧠  until ⚖️ rules
🏁
```

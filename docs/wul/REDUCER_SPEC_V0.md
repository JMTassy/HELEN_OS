---
authority: OPERATOR_BOUND
canon: NO_SHIP
lifecycle: SPEC
version: 0
parents:
  - docs/specs/wul_claim_schema_v0.json   # the typed object (the MAP)
  - docs/specs/WUL_CORE_V1.md             # token registry + admission chain
  - docs/specs/WUL_COMPILER_V0_SPEC.md    # grammar + production type-rules
status: DRAFT — operator countersignature pending. Defines law; does not invoke it.
peer_review: BLOCK → corrected (T3b fix · L6/L7 added · SUPERSEDED in graph · T8–T12 added)
---

# WUL_REDUCER_SPEC_V0

Status: DRAFT
Layer: WUL Kernel / Admission Boundary
Authority: Non-sovereign until HumanSeal
Purpose: Define the reducer as the deterministic passage mechanism from symbolic material to
replay-admissible kernel claims.

> Schema accepts the shape. Reducer admits the move. Replay proves the seal.
> Symbol ≠ Claim ≠ Admitted Claim ≠ Replayable Fact — this spec governs the middle.

This is a **design spec only**. It mutates no kernel, no ledger, no schema. It is not the
reducer; it is the contract the reducer must satisfy.

---

## 0. Admission Ladder

The reducer governs the following ladder:

```
Symbol
  → Claim
  → Typed
  → Receipted
  → Judged
  → Admitted
  → Replayable
```

No object may skip a rung.

### 0.1 State Names

```
S0_SYMBOL
S1_CLAIM
S2_TYPED
S3_RECEIPTED
S4_JUDGED
S5_ADMITTED
S6_REPLAYABLE
S_REJECTED       (terminal — claim refused)
S_SUPERSEDED     (terminal — claim replaced by a successor)
S_TERMINAL       (absorbing sink — both S_REJECTED and S_SUPERSEDED seal here)
```

### 0.2 Core Distinctions

```
Symbol           ≠ Claim
Claim            ≠ Typed Claim
Typed Claim      ≠ Receipted Claim
Receipted Claim  ≠ Admitted Claim
Admitted Claim   ≠ Replayable Claim
```

---

## 1. Reducer Role

The reducer is the admission boundary.

It does not create truth.
It does not infer authority.
It does not repair malformed claims silently.
It does not promote symbolic content by aesthetic, narrative, mythic, or rhetorical force.

It computes whether a candidate claim may enter the kernel-admissible set.

---

## 2. Transition Graph

### 2.1 Legal Transitions

```
S0_SYMBOL     → S1_CLAIM        if ClaimForm(c)
S1_CLAIM      → S2_TYPED        if Typed(c)
S2_TYPED      → S3_RECEIPTED    if HasReceipt(c)
S3_RECEIPTED  → S4_JUDGED       if GateGreen(c)
S4_JUDGED     → S5_ADMITTED     if Admit(c)
S5_ADMITTED   → S6_REPLAYABLE   if ReplayAdmissible(c)
S5_ADMITTED   → S_SUPERSEDED    if SuccessorAdmitted(c)   # a later claim supersedes this one
Any S_i       → S_REJECTED      if RejectCode(c) exists
S_REJECTED    → S_TERMINAL
S_SUPERSEDED  → S_TERMINAL
S6_REPLAYABLE → S_TERMINAL
```

A move not listed here is **rejected by default** (fail-closed). The reducer is a total
function: every (state, action) maps to ALLOW(next) or REJECT(code).

### 2.2 Forbidden Transitions

```
S0_SYMBOL     ↛ S2_TYPED
S0_SYMBOL     ↛ S3_RECEIPTED
S0_SYMBOL     ↛ S5_ADMITTED
S1_CLAIM      ↛ S3_RECEIPTED
S1_CLAIM      ↛ S5_ADMITTED
S2_TYPED      ↛ S5_ADMITTED
S3_RECEIPTED  ↛ S6_REPLAYABLE
S_REJECTED    ↛ S1_CLAIM
S_REJECTED    ↛ S5_ADMITTED         # REJECT_FORBIDDEN_TRANSITION (not REJECT_TERMINAL_FROZEN)
S_SUPERSEDED  ↛ any non-terminal
S_TERMINAL    ↛ any state
```

Any unlisted move is an implicit forbidden transition (fail-closed default).

---

## 3. Admit(c)

A candidate claim c is kernel-admissible iff all six clauses hold:

```
Admit(c) :=
      Typed(c)               # claim_class & truth_status ∈ enums; schema-valid; additionalProperties:false
    ∧ HasReducerPath(c)      # a legal §2 sequence reaches S5_ADMITTED with no skipped rung
    ∧ HasReceipt(c)          # evidence[] non-empty AND a receipt object is bound
    ∧ HasHash(c)             # evidence_hash ≠ null         (Law L1)
    ∧ GateGreen(c)           # all conjunctive gates PASS: K8 ∧ Kτ ∧ Kρ ∧ K-wul ∧ LEGORACLE
    ∧ ¬TerminalViolation(c)  # current ∉ {S_REJECTED, S_SUPERSEDED, S_TERMINAL};
                             #   claim_class=SPECULATIVE ⇒ target ≤ S4_JUDGED   (Law L2)
```

`Admit(c) = false ⇒ the claim stays in its current state` (no partial promotion). A `false`
on `HasHash` or `HasReceipt` collapses to the core invariant: **NO RECEIPT ⇒ NO CLAIM**.

### 3.1 Canonical Admission

The reducer may compute `Admit(c) = true`, but it cannot confer canonical status by itself.

```
KernelAdmit(c)  = Admit(c)                       ← reducer may decide
CanonAdmit(c)   = Admit(c) ∧ HumanSeal(c)         ← operator only
```

Therefore: `KernelAdmit(c) ≠ CanonAdmit(c)`

The reducer decides admissibility. The human operator confers canonical admission.

This preserves:
- Proposer ≠ Validator
- Reducer ≠ Sovereign
- No self-authorization
- No auto-canonization

---

## 4. Passage Laws

The following laws are executable, not decorative. They encode every obligation stated in
`$comment` fields of `wul_claim_schema_v0.json` as an enforceable reducer rule.

**L1 — No Hash, No Promote** *(source: `evidence_hash.$comment`)*

```python
if not HasHash(c):
    reject(c, REJECT_NO_HASH)
```

A claim without a canonical hash cannot pass beyond S2_TYPED.

**L2 — SPEC Ceiling** *(source: root `$comment` sub-point 2; `max_admission_state.$comment` clause a)*

```python
if claim_class == "SPECULATIVE" and target_state > S4_JUDGED:
    reject(c, REJECT_SPEC_CEILING)
```

SPECULATIVE claims may not reach S5_ADMITTED, S6_REPLAYABLE, or any terminal-admitted state.
Mirrors WUL_CORE_V1 hard firewall: `Ⓢ ↛ ✅/⚰️/🔁`.

**L3 — Terminal Frozen** *(source: root `$comment` sub-point 3)*

```python
if state(c) == S_TERMINAL:
    reject_transition(c, REJECT_TERMINAL_FROZEN)
```

S_TERMINAL is the absorbing sink. No transition out of S_TERMINAL is permitted.
Note: S_REJECTED and S_SUPERSEDED are distinct pre-terminal states; transitions FROM them
to non-terminal states are `REJECT_FORBIDDEN_TRANSITION` (not REJECT_TERMINAL_FROZEN).

**L4 — Terminal Conflict** *(source: root `$comment` sub-point 3 + schema SUPERSEDED semantics)*

```python
if TerminalState(c) conflicts with PriorTerminalState(c) under same_canonical_id:
    reject(c, REJECT_TERMINAL_CONFLICT)
```

A claim cannot be both terminally admitted and terminally rejected under the same canonical
identity. Correction requires a new candidate ID.

**L5 — Reason Required** *(source: `rejection_reason.$comment`)*

```python
if terminal == True and rejection_reason is None:
    reject(c, REJECT_REASON_MISSING)
```

Every terminal claim must carry a typed reason code. Condition is `terminal=True` (not
`is_rejection`), matching the schema `$comment` exactly — this covers both S_REJECTED and
S_SUPERSEDED terminal claims.

**L6 — Max-State Ceiling** *(source: `max_admission_state.$comment` clause b)*

```python
if admission_state > max_admission_state:
    reject(c, REJECT_BAD_STATE)
```

The reducer must verify `admission_state ≤ max_admission_state` at every transition. A claim
may not be promoted past its declared ceiling.

**L7 — Terminal Consistency** *(source: `terminal.$comment`)*

```python
if terminal != (admission_state in {S_REJECTED, S_SUPERSEDED}):
    reject(c, REJECT_BAD_STATE)
```

The `terminal` boolean field must be `True` iff `admission_state ∈ {S_REJECTED, S_SUPERSEDED}`,
and `False` for all other admission states. The reducer enforces this at every transition.

---

## 5. Reject Codes

The reducer uses a closed rejection enum. No free-form rejection reasons are allowed inside
the kernel.

```
REJECT_BAD_STATE              current state not in legal state space; or L6/L7 violation
REJECT_FORBIDDEN_TRANSITION   move not in §2.1 legal set (includes S_REJECTED ↛ S5)
REJECT_NO_HASH                evidence_hash = null during promotion (L1)
REJECT_NO_RECEIPT             evidence[] empty or receipt object absent
REJECT_GATE_RED               one or more conjunctive gates FAIL
REJECT_TERMINAL_FROZEN        transition attempted FROM S_TERMINAL (L3)
REJECT_TERMINAL_CONFLICT      same canonical_id + conflicting terminal states (L4)
REJECT_SPEC_CEILING           SPECULATIVE → beyond S4_JUDGED (L2)
REJECT_REASON_MISSING         terminal=true but rejection_reason is null (L5)
REJECT_REPLAY_MISMATCH        replay output differs from canonical trace
REJECT_HUMAN_SEAL_MISSING     CanonAdmit attempted without HumanSeal
```

---

## 6. Replayability Conditions

A claim c is replay-admissible iff:

```
ReplayAdmissible(c) :=
      CanonAdmit(c)            # Admit(c) ∧ HumanSeal(c)
    ∧ HasCanonicalHash(c)      # stable, content-addressed identifier
    ∧ HasReducerTrace(c)       # the full state_path is recorded
    ∧ HasReceiptPath(c)        # receipt chain is intact
    ∧ DeterministicReplay(c)   # same inputs → same verdict on replay
```

Replay must reproduce:

```
candidate_hash
reducer_path
receipt_hash
gate_result
admission_result
terminal_state
```

If replay output differs from the canonical trace:

```python
reject(c, REJECT_REPLAY_MISMATCH)
```

---

## 7. Terminal States

Terminal states are sealed.

```
TERMINAL_ADMITTED     S5_ADMITTED → S6_REPLAYABLE reached — claim fully admitted and replayable
TERMINAL_REJECTED     S_REJECTED → S_TERMINAL — claim permanently refused
TERMINAL_SUPERSEDED   S_SUPERSEDED → S_TERMINAL — claim replaced by a successor claim
TERMINAL_REPLAYABLE   canonical alias for TERMINAL_ADMITTED (emphasizes replay provability)
```

Terminal states may be read, indexed, audited, or cited.
They may not be edited, overwritten, reopened, or silently superseded.

When TERMINAL_ADMITTED and TERMINAL_REPLAYABLE are both applicable, emit `TERMINAL_REPLAYABLE`
as the canonical label (the reducer's output label, not just an alias).

Correction of a terminal claim requires a new candidate ID.

---

## 8. Determinism Note (Kτ / Kρ)

The reducer is a **pure deterministic function**:

```
Reducer(c, Kτ, Kρ) → result

  Kτ = transition kernel (legal moves, guards)
  Kρ = receipt/replay kernel (hash verification, trace)
```

For fixed c, Kτ, and Kρ, the reducer must emit identical:

```
state_path
reject_code
admission_boolean
terminal_state
trace_hash
```

No timestamp, randomness, environment metadata, or UI state may enter the hashed decision
payload. This is what lets `S6_REPLAYABLE` mean what it says: `S_t = Replay(L_{≤t})`.

---

## 9. Test Vectors

Each vector: an input state + an action → the required reducer verdict.
These are the spec's acceptance criteria for any future reducer implementation.

**T1 — Illegal Promotion (skip-all)**

```
Input:    S0_SYMBOL → S5_ADMITTED  (5 rungs skipped)
Expected: S_REJECTED · REJECT_FORBIDDEN_TRANSITION
```

**T2 — Missing Hash**

```
Input:    Typed(c)=true · HasHash(c)=false · action=→S3_RECEIPTED
Expected: S_REJECTED · REJECT_NO_HASH
```

**T3 — Terminal States**

```
T3a: Input:    State(c)=S_TERMINAL · transition_to=S2_TYPED
     Expected: S_REJECTED · REJECT_TERMINAL_FROZEN     (S_TERMINAL is the absorbing sink)

T3b: Input:    State(c)=S_REJECTED · action=→S5_ADMITTED
     Expected: S_REJECTED · REJECT_FORBIDDEN_TRANSITION  (S_REJECTED ↛ S5 in §2.2;
               S_REJECTED is not S_TERMINAL — L3 does not apply here)
```

**T4 — Replay Admissibility**

```
T4a: Input:    CanonAdmit(c)=true · DeterministicReplay(c)=true · action=→S6_REPLAYABLE
     Expected: S6_REPLAYABLE · TERMINAL_REPLAYABLE   (ALLOW)

T4b: Input:    State(c)=S5_ADMITTED · DeterministicReplay(c)=false · action=→S6_REPLAYABLE
     Expected: S_REJECTED · REJECT_REPLAY_MISMATCH

T4c: Input:    State(c)=S4_JUDGED · action=→S6_REPLAYABLE  (skip S5)
     Expected: S_REJECTED · REJECT_FORBIDDEN_TRANSITION
```

**T5 — SPEC Ceiling**

```
Input:    claim_class=SPECULATIVE · State(c)=S4_JUDGED · action=→S5_ADMITTED
Expected: S_REJECTED · REJECT_SPEC_CEILING
```

**T6 — Terminal Conflict**

```
Input:    PriorTerminalState(c)=TERMINAL_REJECTED
          NewTerminalState(c)=TERMINAL_ADMITTED
          same_canonical_id=true
Expected: S_REJECTED · REJECT_TERMINAL_CONFLICT
```

**T7 — Happy Path (full Prime Chain)**

```
Input:    S0_SYMBOL
          ClaimForm(c)=true         → S1_CLAIM
          Typed(c)=true             → S2_TYPED
          HasReceipt(c)=true        → S3_RECEIPTED
          GateGreen(c)=true         → S4_JUDGED
          Admit(c)=true             → S5_ADMITTED
          HumanSeal(c)=true
          ReplayAdmissible(c)=true  → S6_REPLAYABLE
Expected: ALLOW at each step · TERMINAL_REPLAYABLE
```

**T8 — Missing Receipt**

```
Input:    State(c)=S2_TYPED · evidence=[]] · action=→S3_RECEIPTED
Expected: S_REJECTED · REJECT_NO_RECEIPT
```

**T9 — Gate Red**

```
Input:    State(c)=S3_RECEIPTED · HasReceipt(c)=true · GateGreen(c)=false · action=→S4_JUDGED
Expected: S_REJECTED · REJECT_GATE_RED
```

**T10 — Reason Missing**

```
Input:    terminal=true · rejection_reason=null
Expected: REJECT_REASON_MISSING                (L5; applies to both REJECTED and SUPERSEDED)
```

**T11 — Human Seal Missing**

```
Input:    Admit(c)=true · HumanSeal(c)=false · action=CanonAdmit
Expected: S_REJECTED · REJECT_HUMAN_SEAL_MISSING
```

**T12 — Max-State Ceiling Violation (L6)**

```
Input:    admission_state=S5_ADMITTED · max_admission_state=S4_JUDGED
Expected: REJECT_BAD_STATE                     (L6: admission_state > max_admission_state)
```

**T13 — Superseded Path**

```
Input:    State(c)=S5_ADMITTED · SuccessorAdmitted(c)=true
Expected: S_SUPERSEDED · TERMINAL_SUPERSEDED   (ALLOW via §2.1 legal transition)

Input:    State(c)=S_SUPERSEDED · action=→S5_ADMITTED
Expected: S_REJECTED · REJECT_FORBIDDEN_TRANSITION   (§2.2: S_SUPERSEDED ↛ any non-terminal)
```

---

## 10. Non-Goals

This reducer does not:

```
interpret mythic content
judge truth metaphysically
infer sentience
grant sovereignty
create receipts
forge hashes
rewrite terminal states
self-authorize canon
promote symbolic content by aesthetic or rhetorical force
```

It only determines whether a candidate claim has a valid passage path into replayable
kernel admission.

---

## 11. WULmoji Logic Synthesis

The Prime Chain mapped to the S0–S6 reducer:

```
💡  S0_SYMBOL        raw token, no truth status
 ↓  ClaimForm(c)
📜  S1_CLAIM         claim_class assigned
 ↓  Typed(c)
🧬  S2_TYPED         schema-valid object
 ↓  HasReceipt(c)
🧾  S3_RECEIPTED     evidence_hash ≠ null
 ↓  GateGreen(c)
🔐  S4_JUDGED        K8 ∧ Kτ ∧ Kρ ∧ K-wul ∧ LEGORACLE green
 ↓  Admit(c)
✅  S5_ADMITTED      reducer says yes · human seals → CanonAdmit
 ↓  ReplayAdmissible(c)
🔁  S6_REPLAYABLE    S_t = Replay(L_{≤t}) proven
 ↓  seal
⚰️  S_TERMINAL       immutable · read/audit only

❌  S_REJECTED        any rung · REJECT_FORBIDDEN_TRANSITION from non-S_TERMINAL pre-terminal
🔄  S_SUPERSEDED      successor admitted · TERMINAL_SUPERSEDED
```

Forbidden transitions (membrane layer):

```
💡  ↛ ✅  ↛ ⚰️  ↛ 🔁        skip nothing
📜  ↛ 🧾  ↛ ✅              no receipt-skip
🧾  ↛ 🔁                   must pass through ✅ first
⚰️  ↛ *                    S_TERMINAL is frozen (L3)
Ⓢ   ↛ ✅  ↛ ⚰️  ↛ 🔁        SPECULATIVE ceiling (L2)
```

Admit(c) compressed:

```
Admit(c) = 🧬 ∧ 🛤️ ∧ 🧾 ∧ 🔒 ∧ 🛡️✅ ∧ ¬💥
           typed path rcpt hash gates ¬terminal

CanonAdmit(c) = Admit(c) ∧ 👑   ← operator only · reducer cannot self-confer
```

Passage laws:

```
L1  🔒=∅ → ⛔ REJECT_NO_HASH              no hash no voice
L2  Ⓢ → ✅ blocked                        REJECT_SPEC_CEILING
L3  ⚰️ ↛ * frozen                          REJECT_TERMINAL_FROZEN  (S_TERMINAL only)
L4  same id + conflict terminal            REJECT_TERMINAL_CONFLICT
L5  ⚰️ flag=true + reason=null → ⛔        REJECT_REASON_MISSING   (REJECTED or SUPERSEDED)
L6  state > max_state → ⛔                 REJECT_BAD_STATE
L7  terminal ≠ (state ∈ {REJECTED,SUP})   REJECT_BAD_STATE
```

---

## 12. Seal

```
🔧 reducer = the missing object · 7 $comment obligations → 7 executable passage-laws (L1–L7)
🧱 Admit(c) = Typed ∧ ReducerPath ∧ Receipt ∧ Hash ∧ GateGreen ∧ ¬TerminalViolation
🚪 CanonAdmit = Admit ∧ HumanSeal  (operator only — reducer cannot self-authorize)
🔁 deterministic · fail-closed · unlisted move = REJECT by default
💡→📜→🧬→🧾→🔐→✅→🔁→⚰️  (Prime Chain end-to-end)
🔄 SUPERSEDED = legal terminal branch (successor admitted); requires new candidate_id to correct

authority = OPERATOR_BOUND · canon = NO_SHIP · ledger_effect = none · kernel_effect = none
REDUCER_SPEC_V0 = DRAFT — operator countersignature pending
🏁 HOLD_FOR_OPERATOR
```

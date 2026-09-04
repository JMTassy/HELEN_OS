# WAIT_RECEIPT_V0 — Suspension as a Typed, Replayable Constitutional Event

```
status:        PROPOSAL
authority:     false
canon:         false
ledger_effect: none
claim_status:  NO_CLAIM
hold:          HOLD_FOR_OPERATOR
date:          2026-08-04
origin:        halt of the gateway-goblin-swarm mission (HELEN_GATEWAY_PROCESS_V0
               absent from disk); halt receipt at scratch/gateway-goblin-swarm/
               SWARM_HALT_NOTE.md
```

HELEN OS — created by JM Tassy.

---

## 0. Problem

When an execution cannot proceed because a required input is absent, most
agent systems either (a) fail, discarding the mission, or (b) silently invent
the missing input and continue. Both destroy replayability. The gateway swarm
halt demonstrated a third path: stop, emit a receipt explaining why, persist
the mission, and wait. This document types that third path so the waiting
mechanism cannot become an untyped loophole.

A WAIT receipt must satisfy the same constitutional discipline as every other
receipt: it states exactly what is verified, nothing more.

## 1. WAIT_RECEIPT schema

```yaml
WAIT_RECEIPT_V0:
  receipt_type: WAIT                    # new member of the receipt family
  mission:
    text_hash: sha256                   # verbatim mission, hashed
    issued_by: operator                 # who gave the verb
  suspended_at:
    repository_head: sha                # git HEAD when suspension occurred
    branch: string
    tree_state: CLEAN | DIRTY(n)        # witnessed, not assumed
  lifecycle_state: WAITING_ARTIFACT | WAITING_ADMISSIBILITY | WAITING_INPUT
  blocking_dependency:
    kind: ARTIFACT | ADMISSIBILITY | OPERATOR_INPUT
    identifier: string                  # e.g. docs/proposals/HELEN_GATEWAY_PROCESS_V0.md
    expected_hash: sha256 | UNKNOWN     # UNKNOWN is honest when the artifact
                                        # has never been seen locally
  resume_condition: string              # human-readable precondition
  resume_semantics: deterministic_if | recompute_under_current_state   # see §4
  wait_basis: [ ... ]                   # see §3
  created_at: iso8601
  invalid_when: [ ... ]                 # see §4bis — symmetric with resume
  claim_status: NO_CLAIM
  authority: false
  ledger_effect: none
```

What this receipt attests: *an execution was suspended at a witnessed point
for a stated reason.* What it does NOT attest: that the mission is worth
resuming, that the missing artifact will match expectations, or that any
conclusion of the suspended mission is true.

## 2. Typed execution lifecycle

```
ExecutionLifecycle:
  WAITING_INPUT           # operator verb or parameter absent
  WAITING_ARTIFACT        # required artifact absent from disk
  WAITING_ADMISSIBILITY   # artifact present but fails a constitutional gate
                          #   (wrong hash, missing taint, invalid schema)
  READY                   # all preconditions witnessed
  EXECUTING
  HALTED                  # execution stopped by internal failure
  REFUSED                 # execution declined on constitutional grounds
  FINISHED
```

The load-bearing distinction: **WAITING_ARTIFACT ≠ WAITING_ADMISSIBILITY.**
Absence and inadmissibility are different causes with different unblock
actions (materialize vs repair/re-gate). Collapsing them onto one axis
recreates the overloaded-field defect this whole line of work exists to
eliminate. Similarly HALTED (it broke) ≠ REFUSED (it declined) ≠
WAITING_* (it lacks reality to proceed).

### Receipted transitions

Every lifecycle transition emits a receipt naming (from_state, to_state,
cause, witnessed_repo_state). A transition without a receipt did not happen,
constitutionally — otherwise pauses degrade back into informal interruptions
living only in the operator's head. State without receipt = claim without
receipt.

## 3. WaitBasis

```
WaitBasis(E) = the minimal set D of future dependencies such that
               Resume(E, D) is well-defined.
```

For the gateway swarm halt, witnessed on 2026-08-04:

```
WaitBasis = {
  mission_hash,        # mission text persisted verbatim (memory + halt note)
  repository_head,     # 931ef3b (SOT), 69338df (worktree)
  artifact_hash,       # UNKNOWN — HELEN_GATEWAY_PROCESS_V0 never seen locally
}
```

`reducer_version` is deliberately EXCLUDED from this WaitBasis: the suspended
computation is a goblin swarm plus a model-driven reduction. No deterministic
kernel reducer participates in its continuation. Including reducer_version
would imply an admission path that does not exist for this mission — an
over-claim. A WaitBasis may include reducer_version ONLY when a deterministic
reducer genuinely participates in the resumed computation.

`artifact_hash: UNKNOWN` is honest and load-bearing: the artifact has never
been materialized, so the receipt cannot pin it. Consequence: resumption
inspects *whatever text materializes*, which is not provably the document
judged upstream. The receipt says so instead of pretending otherwise.

## 4. resume_semantics — two guarantee levels, never conflated

```
deterministic_if:
  Resume(E, D) re-enters the same suspended computation with identical
  inputs, if and only if every element of WaitBasis is present and matches
  its pinned hash. Guarantees SAME INPUTS. For computations whose body is
  non-deterministic (any model call), it does NOT guarantee same outputs.
  NO HASH = NO VOICE applies to the outputs as usual.

recompute_under_current_state:
  Resume re-runs the mission against the repository state at resume time
  rather than the pinned suspended_at state. Weaker, sometimes correct
  (e.g. the mission targets "the current proposal", whatever it now says).
  The receipt must say which semantics governs; defaulting silently to
  either one is an over-claim.
```

A WAIT receipt claiming "deterministic continuation" without stating which
level it means commits the same defect as a session receipt claiming truth:
the type promises more than the machinery enforces.

## 4bis. Invalidation — the other half of the continuation contract

A WAIT receipt without an expiration policy lets a suspended execution
resume months later against a drifted environment. Every WAIT receipt
therefore defines both halves:

```yaml
resume_when:                       # all must hold
  - every element of wait_basis present and matching its pinned hash
invalid_when:                      # any one suffices
  - mission_replaced               # operator issues a superseding mission
  - operator_revokes               # explicit revocation verb
  - wait_basis_drift               # a PINNED element of wait_basis changed
                                   #   (mission text edited, expected artifact
                                   #   schema changed, reducer_version bumped
                                   #   iff reducer_version is in the basis)
```

**Deliberately NOT an invalidator: unrelated repository HEAD movement.**
The repository moves constantly; a WAIT receipt that dies on any commit
over-invalidates exactly as the untyped fields over-claimed. Invalidation
conditions must be as minimal as resume conditions, and both are defined
over the WaitBasis — nothing outside it can kill or revive the receipt,
except the two operator-side events (replace, revoke), which are always
valid because the operator owns the mission.

A receipt whose `invalid_when` has fired transitions the suspended
execution to HALTED with cause `wait_invalidated` — a receipted transition
like any other (§2). It does not silently vanish.

## 5. Knowledge / Execution / Authority — three orthogonal axes

```
Knowledge   — what is reconstructibly known     (governed by replay/receipt
                                                 semantics over history)
Execution   — what is running, suspended, done  (governed by the lifecycle
                                                 above + WAIT receipts)
Authority   — what is admitted as binding       (governed by the reducer,
                                                 and only the reducer)
```

These do not substitute for each other. A WAIT receipt lives entirely on the
Execution axis:

- It does not create knowledge (it records a suspension, not a finding).
- It does not touch authority. **WAIT changes no sovereign state.** No
  ledger entry, no admission, no closure. ledger_effect: none, always.
- Resuming an execution grants it nothing on the other two axes; whatever
  it produces still enters as proposal, gated as usual.

This is proposer ≠ validator ≠ admitter, extended across time.

## 6. Duality with ReplayBasis — REFERENCED_UNVERIFIED

The upstream discussion frames WaitBasis as dual to a "ReplayBasis":
ReplayBasis = minimal *historical* information required to reconstruct a
belief; WaitBasis = minimal *future* information required to resume an
execution. One asks "what history is irreducible?", the other "what future
dependencies are irreducible?".

**Verification status: REFERENCED_UNVERIFIED.** A LOCATE sweep of the SOT
(HEAD 931ef3b, 2026-08-04) found no ReplayBasis implementation, experiment,
schema, note, or receipt. Terms searched: `ReplayBasis`, `K_basis`,
`k_basis(.js)`, `locality_property`, `supersession_ratio`, `WaitBasis`,
`zol` (whole word — hits are the CONQUEST game currency, unrelated),
`levels` co-occurring with replay (hits are CWL/witness docs, unrelated).
No file named `*basis*` exists in the tree. If ReplayBasis work exists, it
lives outside this repository and has emitted no local receipt. The duality
is therefore recorded as conceptual inspiration, not as a claim about
existing machinery. This section upgrades to VERIFIED only when a
ReplayBasis artifact with a path and hash exists in the SOT.

### 6bis. Upstream-relayed ReplayBasis measurements — REFERENCED_UNVERIFIED

*(merged 2026-08-04 by operator verb MERGE INTO WAIT_RECEIPT, from an
operator-relayed upstream synthesis; no local computation reproduces these
numbers — status inherits §6's REFERENCED_UNVERIFIED.)*

The upstream frame refines ReplayBasis into three quantities:

```
ReplayCone(B)  = all receipts historically ancestral to B
ReplayBasis(B) = minimal subset sufficient to reconstruct B
K(B)           = |ReplayBasis(B)|
```

Curvature is thus not raw historical length but the quantity of
*irreducible* history. The supersession measure:

```
sigma(B) = 1 − K_basis(B) / K_len(B)
```

Relayed measurements (unverified locally, no artifact, no hash):

```
levels:  K_len ≈ 22.3   K_basis ≈ 4.9    → sigma ≈ 0.78
zol:     K_len ≈ 55.4   K_basis ≈ 53.2   → sigma ≈ 0.04
```

If the `levels` figure holds, ~78% of that lane's history is superseded —
which would make WaitBasis minimality (§3) the temporal mirror of an
empirically observed compression, not just an aesthetic preference.

**Open contradiction (DISPUTED, do not smooth):** the `zol` figure
(sigma ≈ 0.04) contradicts the expectation that zol is strictly
incremental — or reveals a typing, payload, or minimization-algorithm
error upstream. Until reproduced in-repo with a pinned artifact, neither
reading may be asserted. Materializing ReplayBasis locally (§8 item 4)
remains the only path that can settle either the duality or this anomaly.

## 7. Receipt family after this proposal

```
EXECUTION_RECEIPT   — an action ran; records execution, never truth
WAIT_RECEIPT        — an execution suspended on an absent/inadmissible
                      dependency; records suspension, never worthiness
HALT_RECEIPT        — an execution stopped on failure or refusal
MISSION_RECEIPT     — a mission was issued and persisted
ADMISSION_RECEIPT   — reducer-side only; the sole receipt with authority
```

Each type states its exact scope. None substitutes for another.

## 8. What requires operator judgment (HOLD_FOR_OPERATOR)

1. Adopt the 8-state lifecycle as the standard execution vocabulary, or
   keep it local to WAIT semantics?
2. Should lifecycle-transition receipts go to the non-sovereign sidecar log
   (artifacts/claude_code_actions.ndjson, tranche A4) once that hook exists?
3. Naming: WAIT_RECEIPT vs BLOCKED_ON_ARTIFACT as the status vocabulary —
   this draft uses lifecycle_state for the axis and WAIT for the receipt
   type, keeping cause (blocking_dependency.kind) orthogonal to state.
4. Whether to materialize ReplayBasis in-repo so §6 can be verified.

## 10. Repository permission ladder (companion protocol)

Three mutation levels, each requiring a distinct operator grant, each scoped
per artifact — a grant names what it covers, never a whole session:

```
Level 0 — SCRATCH
  paths:    scratch/** (and other non-sovereign working paths)
  grant:    standing (mission-level scratch authorization suffices)
  commit:   none

Level 1 — PROPOSAL
  paths:    docs/proposals/**, proposal branches only
  grant:    GO_PROPOSAL <artifact>  (or the existing explicit
            COMMIT+PUSH <artifact> verb, which it formalizes)
  allowed:  commit + push to a proposal branch, canon=false
  forbidden: merge to canonical branch, doctrine promotion

Level 2 — CANON
  grant:    GO_CANON — only after reducer admission + receipts + operator
  note:     never issuable to this execution shell for sovereign-firewall
            paths; canon promotion runs through HELEN's own machinery
```

Semantics: `NO_COMMIT` (the default) means no repository mutation
whatsoever. A Level-1 grant covers exactly the named artifact on a proposal
branch and expires with the act. Historical note for this document itself:
the draft was written uncommitted under a NO-commit mission, then committed
(87ab760) under a separate, explicit per-artifact operator verb — two
constitutional acts. The ladder types that separation so it never has to be
argued from a transcript again.

## 11. Non-claims

*(§4bis and §10 added by operator-verbed amendment after the initial
commit 87ab760; this section renumbered from §9, content unchanged.)*

This document is a proposal. It admits nothing, promotes nothing, and its
own existence receipts only that a draft was written. It must not be cited
as HELEN doctrine unless admitted through HELEN's own machinery.

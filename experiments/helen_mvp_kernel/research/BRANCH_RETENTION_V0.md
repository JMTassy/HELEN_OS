# BRANCH_RETENTION_V0 — measured, with the falsifiers left live

    STATUS = EXECUTED EXPERIMENT (capacity claim SCOPED, not proven)
    AUTHORITY = false · CANON = false · LEDGER_EFFECT = none
    Kernel: branch_retention.py (+15 tests), non_interference_matrix.py
    extended (+4 tests), gate 106 -> 107, suite 1490 -> 1509

The question, unchanged: **can HELEN keep an alternative available
without treating it as true or permitted, then use later evidence to
make a better authorized decision?**

## Instrument, stated before results

No LLM is reachable in this container, so branches are **deterministic
instruments** over sandbox tasks with known hidden states and
mechanical scoring — which is what the specification asks for. This
measures the **retention policy**, not model cognition. The only thing
that differs between arms is the retention policy: same generation,
same candidate pool, same evidence, same budget accounting. Any
measured delta is attributable to retention alone.

## Result — 300 seeds × 4 families × 4 arms = 4800 runs

| arm | success | correct-branch survival | abstain | wrong action | cost | cost/success |
|---|---|---|---|---|---|---|
| A early selection | 0.354 | 0.354 | 0.173 | 0.472 | 8.50 | 24.00 |
| B best-of-N | 0.354 | 0.354 | 0.173 | 0.472 | 10.50 | 29.65 |
| C beam search | 0.428 | 0.428 | 0.153 | 0.418 | 9.50 | 22.18 |
| **D HELEN retention** | **0.551** | 0.551 | 0.001 | 0.448 | 9.47 | **17.20** |

By family:

| arm | easy | ambiguous | delayed evidence | revoked authority |
|---|---|---|---|---|
| A / B | 0.707 | 0.467 | **0.000** | 0.243 |
| C beam | 0.707 | 0.697 | 0.003 | 0.307 |
| D retention | 0.707 | 0.707 | **0.170** | **0.620** |

`Δ(D − C) = +0.1225`. Best-of-N ties early selection exactly: more
sampling, same blind spot — it still *selects by score*.

## What the falsifiers did

- **"Ordinary beam search matches the result"** — did not fire.
  D − C = +0.1225.
- **"Extra branches are paraphrases with identical predictions"** —
  **PARTIALLY FIRED, and it refuted my stated mechanism.** I predicted
  the gain came from beam wasting slots on injected paraphrases, so
  removing them should make C and D coincide. It did not: with
  paraphrases removed, C = 0.007 vs D = 0.043. The dedup helps against
  **naturally colliding predictions** too. The honest mechanism is
  broader and duller than hypothesised: retention-by-distinct-
  prediction beats retention-by-score whenever the pool contains
  prediction collisions **of any origin**. The docstring now says so.
- **"Gains occur only on tasks constructed to reward delay"** —
  **partially true, and reported as such.** The gain is zero on easy
  tasks (0.707 for every arm) and D costs more there (9.47 vs 8.50).
  Retention buys nothing where early commitment suffices, and pays for
  the privilege.
- **"Correct alternatives survive but Mayor cannot use them"** —
  **cannot fire in this sandbox**, and that is a scope limit rather
  than a win: later evidence is perfectly discriminating, so
  `survival == success` exactly for every arm. Survival is the binding
  constraint here; selection error is untested.
- **"Gains require weaker authorization or evidence admission"** — did
  not fire: 0 unauthorized effects executed, 0 unsupported claims
  admitted. *Zero observed violations is not a universal safety
  proof.*

## The downside the experiment surfaced

D almost never abstains (0.001 vs C's 0.153) and takes **wrong actions
slightly more often** than beam (0.448 vs 0.418). It converts C's
abstentions into actions: roughly four in five become correct, one in
five wrong. Retention does not only rescue good alternatives; it also
supplies a plausible-but-wrong action where the honest answer was to
abstain. That is a genuine cost, now a locked test.

## A design flaw I found in my own sandbox, and fixed in the open

The first run scored **0.000 on `revoked_authority` for every arm**.
Cause: the revoked action *was* the correct one by construction, so
success was impossible and the family tested nothing. Fixed so the
revoked front-runner is a **decoy** and the correct hypothesis stays
authorizable — which is what "lose permission, choose another valid
plan or abstain" was meant to test. Both numbers are recorded; the
flawed run is kept as the witness rather than quietly overwritten.

I also transcribed display-rounded values (`.3f`) into test assertions
where the module stores 4 decimals. The tests failed; the tests were
right.

## Two operator corrections, encoded mid-run

**F\* conserves obligations, not answers.** Read as "same final
output", the invariance condition would forbid the very improvement
sought. `institutional_invariance` now encodes
`Invariant_I(Π₀) ∧ Invariant_I(Π₁) ∧ Q(Π₁) > Q(Π₀)`: two policies may
take **different authorized actions** while holding the same
obligations. A differing action is not a violation; a moved obligation
is. The experiment is an instance — A and D choose different
authorized actions and D scores higher.

**The completeness conjecture needs an outside eye, and it now
fails on demand.** `NIM(T)=0 ⇒ T ∈ M_I` is a completeness conjecture
relative to the *declared* domain. `independent_observer` audits the
**resulting state** (did authority, roots, effects, admissions
actually move?) and deliberately consults neither the matrix nor the
declared transitions. The sought counterexample now fires in a test:
an **undeclared** transition yields `D_NI = 0` while the observer sees
authority rise → `completeness_claim: INVALIDATED`,
`witness_retained: True`. A null defect is the absence of **declared**
leakage, not of leakage.

## Verdict

The candidate capacity is **supported in scope, not demonstrated as a
paradigm**: on this sandbox, with deterministic instruments, at equal
budget, separating Retain / Admit / Authorize outperformed early
selection, best-of-N and ordinary beam search — concentrated entirely
in the families where early evidence misleads or permission is
withdrawn, absent on easy tasks, and paid for in cost and in wrong
actions substituted for abstention. It has not been shown with a real
model, on untouched task families, or on a surprise split.

## Non-deltas

No agent was launched; no LLM was in the loop; no held-out or
surprise split was run; no uncertainty intervals across independent
seed families were computed beyond the single 300-seed sweep; the
capacity claim remains candidate.

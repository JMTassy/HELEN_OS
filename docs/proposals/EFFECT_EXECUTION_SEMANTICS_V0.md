<!-- authority=false · claim=NO_CLAIM · ADVERSARIAL_PROVISIONAL (NOT frozen) -->
<!-- Captured 2026-08-23 · commit authorized 2026-08-23 · subordinate to EFFECTOR_BUS_V0 (FROZEN) -->
<!-- SOVEREIGN-ADJACENT: any receipt/schema fields are PROPOSED only → route to MAYOR -->

# EFFECT_EXECUTION_SEMANTICS_V0 — attack surface (do NOT freeze)

Subordinate to the FROZEN CAPABILITY_BOUNDED_EFFECTOR_BUS. This governs **what
HELEN may know after an authorized attempt meets an uncertain world**. Status:
`ADVERSARIAL_PROVISIONAL` — the next work is falsification, not elaboration.

## Eleven X-modules (attack these)

    X1  OUTCOME ALGEBRA
        Outcome ∈ {NOT_ATTEMPTED, REJECTED, ATTEMPTED, TRANSMITTED,
                   OBSERVED_EFFECT, OBSERVED_NO_EFFECT, OUTCOME_UNKNOWN}
        OUTCOME_UNKNOWN ≠ FAILURE. OBSERVED_NO_EFFECT needs an observation model
        strong enough to justify ABSENCE — silence ⊬ absence.
    X2  ATTEMPT IDENTITY & NONCES — what constitutes the SAME logical attempt;
        nonce single-use? consumption recorded where? TRANSMITTED vs ATTEMPTED
        boundary is per-adapter and currently UNDEFINED.
    X3  IDEMPOTENCY & DEDUP (dangerous) — three distinct properties:
        TransportRetrySafe ≠ ApplicationIdempotent ≠ ExternallyNonConsequential.
        IdempotencyKey ⊬ SafeRetry (dedup'd request can still notify/bill/audit/rate-limit).
    X4  RETRY AUTHORIZATION (dangerous) — UnknownEffect ⊬ RetryPermission.
        A_retry = Verify(LogicalIdempotence ∧ ExecutorDedup ∧ SideEffectPolicy
                         ∧ CurrentPreconditions). Non-idempotent retry = NEW causal
        act Attempt_{n+1} with its own auth/receipt/edge; does NOT erase 𝒰_prev.
        Failure it prevents: purchase→timeout→retry→timeout→retry→3 purchases.
    X5  PARTIAL-EFFECT GRAPH — ΔW = (δ_1..δ_n) is the minimum; dependencies need
        G_E=(V_E,E_E) with δ_i→δ_j. MissionCompletion ≠ Request ≠ Executor ≠
        Effect ≠ VerifiedCompletion.
    X6  RECONCILIATION (dangerous) — OUTCOME_UNKNOWN opens 𝒰_e; how are
        indefinitely-unresolved effects handled WITHOUT converting timeout into
        false certainty? recovery policy still OPEN.
    X7  COMPENSATION — Compensation ≠ Undo; no a^{-1} need exist.
        W_0 --a--> W_1 --c_a--> W_2, W_2≠W_0; Restore(c_a, I) declares invariant set I;
        receipts preserve BOTH R(a), R(c_a). History is never erased.
    X8  REVOCATION & CANCELLATION — causal horizon: t_revoke < t_dispatch clean;
        t_dispatch < t_revoke ⇒ {preventable, occurred, partial, unknown} —
        revocation acts only forward, can itself open a 𝒰_e. Revocation ≠ Compensation.
    X9  CONCURRENCY / TOCTOU (dangerous) — Authorization(C,W_0) ⊬ Authorization(C,W_t).
        state-sensitive effect needs w_pre=(state_version, predicate, observation_time)
        checked as close to the irreversible edge as the adapter permits.
    X10 EFFECTOR PARITY — browser/shell/API/robot/HUMAN obey identical laws;
        HumanAssertion(Effect) ≠ VerifiedEffect; "human" is not an authority bypass.
    X11 VERIFICATION INDEPENDENCE — R_self (executor assertion) ≠ R_independent.
        HighConsequence(e) ⇒ IndependentVerification(e) where feasible; low-consequence
        may accept self-report. Risk-sensitive, does not alter the frozen primitive.

## DEPTH (2026-08-23): Ω_e as possibility set + counterfeit reconciliation

**UNKNOWN is not a Boolean — it is a set of admissible worlds.** For attempted
effect e over outcome space 𝒲_e = {NOT_APPLIED, APPLIED, PARTIAL, APPLIED_THEN_REVERSED},
HELEN holds an epistemic possibility set K_e(t) ⊆ 𝒲_e; UNKNOWN ⟺ |K_e| > 1.

    Ω_e = (e, K_e, 𝒟_e discriminators, 𝒪_e observations, 𝒫_e deps, τ_e time)
    Bilateral blocking invariant: |K_e| > 1 ⇒ ¬Admit(Occurred(e)) ∧ ¬Admit(¬Occurred(e))

**Reconciliation = observational partition refinement** (SAME primitive as the
Garden gain/counterfeit machinery):

    K_e^(0) --D_1,O_1--> K_e^(1) --...--> K_e^(n),  K_e^(i+1) ⊆ K_e^(i)
    ONLY IF the new observation itself passes verification (unreliable obs must
    not silently shrink K_e).  Garden research ~ effect reconciliation ~
    observational partition refinement (shared discrimination structure, differing trust).

**Four terminal states** (closure ≠ "UNKNOWN=false"):

    OPEN · PARTIALLY_RESOLVED (1<|K'_e|<|K_e|) · RESOLVED (|K_e|=1 + admissible witness) ·
    IRRESOLVABLE (∀D∈𝒟_avail: E[ΔΠ(D)]≈0)
    IRRESOLVABLE ≠ RESOLVED · IRRESOLVABLE ⊬ FAILED (timeout ⊬ negative knowledge)

**X13 — COUNTERFEIT RECONCILIATION (the deepest gap; attack first):**

    ObservationConsistentWithEffect ≠ ObservationCausedByEffect
    (file exists ≠ this write created it · row exists ≠ this txn committed it ·
     page changed ≠ this click caused it · payment appears ≠ this attempt produced it)
    g = effect occurred  ∥  c = same observation produced independently
    seek x* : g ≁_{O+x*} c   — reconciliation needs NEAREST-COUNTERFEIT reasoning.
    Highest-value next attack = a concrete fixture: same post-state ∧ different
    causal history; test that the semantics REFUSE to claim which history occurred
    without an actual discriminator.

**Provenance orthogonality:** ObservedEffect ⊬ AuthorizedEffect (observation cannot
retroactively manufacture authorization); keep epistemic-provenance ⊥ authority-provenance
inside receipts.

**Minimal observation core** (rest adapter-typed, no universal mega-schema):

    ObservationCore = (effect_id, attempt_id, observer_id, observation_class,
                       observed_at, payload_digest, provenance_ref)
    + AdapterEvidence { Browser | Filesystem | Email | Shell | API | ... }

**Typed Ω-graph edges** (X12 refined): E_Ω ⊆ V_Ω × T_Ω × V_Ω,
T_Ω = {causal, epistemic, ordering, conflict, compensation}
(e.g. Ω_payment --causal--> Ω_order · Ω_writeA --conflict--> Ω_writeB).

## Open gaps (flagged, unresolved)

- TRANSMITTED vs ATTEMPTED formal boundary per adapter.
- OBSERVED_NO_EFFECT observation model (justify absence, not infer from silence).
- idempotency-key lifetime / collision / reuse rules.
- minimum verification strength per effect class.
- compensation invariant sets I.
- concurrent capability invalidation (state-version/precondition model).
- recovery from indefinitely-unresolved OUTCOME_UNKNOWN without false certainty.
- Ω_e representation + exact DISCHARGE conditions for an uncertainty obligation.
- observation vocabulary: common constitutional core vs adapter-specific richer typed obs.
- **X12 — UNCERTAINTY COMPOSITION**: multiple simultaneously-open 𝒰_{e_i} interact;
  need a dependency structure between obligations (a 𝒰-graph), not independent
  scalar statuses — an unresolved 𝒰_{e_i} may gate the discharge of 𝒰_{e_j}.

Attack order: X3/X4 → X6 → X9 first (highest catastrophe potential). Only after
these survive falsification may EXECUTION_SEMANTICS → FREEZE_CANDIDATE.

None self-promotes. NEEDS_OPERATOR verb to build a falsifier bead against any
X-module or to commit this doc.

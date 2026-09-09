# NON_INTERFERENCE_MATRIX_V0 — conjecture with an executable falsifier

    STATUS = ARCHITECTURAL_CONJECTURE + EXECUTABLE_FALSIFIER
    (explicitly NOT "THEOREM / SEALED" — the audit's grade, adopted)
    AUTHORITY = false · CANON = false · LEDGER_EFFECT = none
    Kernel: non_interference_matrix.py (+19 adversarial tests,
    gate 105 -> 106, suite 1471 -> 1490)

The constitutional principle, compactly:

> Cognition may change topology, memory, presentation, consensus and
> computation. None of those changes acquires institutional force
> unless an explicit typed warrant crosses the corresponding
> boundary.

      D_NI(T) = 0  =>  F*(T Sigma) = F*(Sigma)
      D_NI(T) > 0  =>  ADMIT(T) = 0
      i --omega_ij--> j  =>  Verify(omega_ij) = 1

## The seven corrections — encoded, not argued

The dossier arrived with a critique attached. Every correction it
raised is now a test, because a correction accepted in prose and
dropped in code is not accepted.

**1 — Three cell states, not two.** `N_ij ∈ {I, F, L}`:
invariant-preserving (diagonal), Forbidden (no warrant can license),
Licensed (a typed witness may). Computed: 144 cells = 12 `I` + 5 `L`
+ 127 `F`. A two-state matrix is a diagram; three states make it a
transition policy.

**2 — `D_NI = D_cross + D_local`.** The reference implementation had
`if source == target: continue`, treating every local mutation as
legitimate. That is a real bug: `A→A` can be an authority
**escalation**, `E→E` an evidence **corruption**. Local invariants
now bite — escalation, depth increase, re-rooting, root inflation,
non-idempotent effect, replay loss, and memory status upgrade — and
the engine reports the two defect classes separately.

**3 — CHID-02, the covariance correction (the largest).** The dossier
claimed `Rank(Cov) = N_eff ≪ N ⟹ ∂|ρ_E|/∂N = 0`. **The implication
does not follow.** Covariance rank measures linear dimensionality
under a chosen representation; it says nothing about provenance —
in *either* direction: `N_eff = 1` can coexist with a genuinely new
independent root, and `N_eff > 1` supplies none. So `N_eff` is
measured, and the epistemic invariant is stated separately:
`Δ|ρ_E| = 0` unless an independent-root witness is admitted. Both
directions are tested. The surviving doctrine is the stronger one:
**cognitive diversity ≠ epistemic warrant**.

**4 — CHID-03, memory ≠ proof.** A memory holds observations,
hypotheses, caches, summaries, invalidated assertions, permissions,
embeddings — not all proofs. An item is
`(value, ρ_E, τ_persist, Scope(κ), status)`. The narrow, stronger
chiddush: **a memory READ cannot upgrade the epistemic status of what
it reads** — `M ↛ W`, `M ↛ A`.

**5 — CHID-04, bisimilarity is too strong.** A useful optimized
topology may legitimately *not* be bisimilar to the original.
`Π₀ ≁ Π₁` is permitted provided `F*(Π₁x) = F*(Π₀x)` — **topological
freedom under institutional invariance**. Tested: non-bisimilar +
frontier-preserved passes; bisimilar + frontier-moved fails.

**6 — CHID-05, roles not set-disjointness.** Issuer and discharger may
be the same organizational principal. The rule is typed **roles**:
`Propose ≠ Authorize ≠ Discharge` as *types*, not entities. Tested:
one principal holding all three passes when κ is valid; untyped roles
refuse; a tool call without κ refuses while explicitly recording that
same-principal is permitted.

**7 — The monoid hierarchy with its conditions.** `M_I = {T : F*(Tx)
= F*(x)}` is a monoid **only if** it contains the identity and is
closed under composition — both now checkable rather than assumed.
`Γ_I = Units(M_I)` is the reversible sector, and
`presentation ⊇ M_I ⊇ Γ_I`. `Γ_I` membership requires an inverse that
is *itself* in `M_I`.

## The self-falsifier

`nim_implies_monoid` closes the loop the audit asked for:
`NIM(T) = 0 ⟹ T ∈ M_I`. And if the defect is zero while the frontier
moved anyway, the verdict is `E_MATRIX_INCOMPLETE` — **a leakage
channel is missing from the matrix**. That falsifies the
*specification*, not the run. A conjecture that can only be confirmed
would not be worth sealing; this one names the observation that would
break it.

## Leakage channels (the coordinates of possible amplification)

| forbidden crossing | witness / test |
|---|---|
| `Q → A` | composition test |
| `N_artifacts → ρ_E` | provenance roots |
| `P → F*` | counterfactual admission |
| `C → W` | TCB attack |
| `M → A` | memory status probe |
| `Π → A` | topology privilege probe |

## Literature: problem space, not architecture

The external corpus is recorded at the grade it earns, no higher:

- 🟢 **relayed-verified existence** — 2603.22868 (Agent-Sentry),
  2603.14332 (dynamic capabilities), 2606.24535 (governed shared
  memory). *Verified by the relaying lane, not independently
  re-checked in this container.*
- 🟠 **REPORTED** — exact experimental metrics (the 94.3%/95.1% vs
  ">90%/98%" divergence across indexes is itself the argument for
  not promoting numbers).
- 🔴 **UNVERIFIED** — conference-status claims ("ICML 2026
  Spotlight"). Not used.

      Literature validates the problem-space
        ≠ Literature validates HELEN's architecture

      Paper exists ≠ paper's metric is independently witnessed

The defensible claim is therefore narrow: **HELEN proposes a common
invariant algebra over heterogeneous agentic runtime primitives** —
testable locally, without trusting any external number.

## Substrate note (recorded, not hidden)

This module was built in a **fresh container**: `/workspace/helen-
conquest` no longer existed and the kernel had to be recovered by
clone from the remote at `abef6d0`. CONTROL was re-frozen before any
change — gate `CONSTITUTION_HELD` 105/105, suite 1471 — so the
baseline is this container's own measurement, not a historical
transcript.

## Non-deltas

Nothing was proven; no theorem sealed; no external metric imported;
the five CHIDs remain motivating failure classes, not theorems —
CHID-01 and CHID-04 are the strongest architectural propositions,
CHID-02/03/05 survive only in their corrected forms. The matrix is a
falsifiable kernel research object awaiting adversarial pressure, and
`status()` says so in code.

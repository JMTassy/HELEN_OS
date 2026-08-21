# F5 — LOCAL INTERVENTIONAL OPERATOR IDENTIFICATION
<!-- status: PREREG_ARCHITECTURE_FROZEN · execution: NOT_RUN · authority=false · canon=false -->
<!-- NON-SOVEREIGN local spec (~/helensh). NOT committed to SOT — awaits operator COMMIT+PUSH verb. -->

## Primary object (NOT a derivative)
J_Δ(M0) = { Ĵ^(δ)(M0) : δ ∈ Δ }   — a family of finite intervention responses.
LAW: finite-response family ⇏ DΦ(M0). "Finite difference does not self-promote into a derivative."
Ĵ ≈ DΦ(M0) admissible ONLY after: DomainOK ∧ MultiDeltaStable ∧ OrderCompatible ∧ EstimatorNonDegenerate.

## Five sub-gates
F5a DomainAdmissibility        : M0 ± δ e_j ∈ Dom(Φ) for every planned perturbation
F5b FiniteDifferenceConsistency: central diff at multi-δ {δ1,δ2,δ3}, δ2=rδ1, δ3=rδ2
F5c InjectedCrossTalkRecovery  : inject J12=α≠0 → recover amplitude+sign; zero-control J13=0 preserved
F5d NormalizedOperatorStability: J̃ = D_I^{-1} J D_M, scales s_M,s_I PREREGISTERED (post-hoc scale = Goodhart)
F5e EstimatorNonDegeneracy     : order test skipped where |Ĵ^δ2 − Ĵ^δ3| ≤ η_R (0/0 → ORDER_TEST_UNRESOLVED, not FAIL)

## Estimator
Ĵ_kj^(δ) = [ I_k(Φ(M0+δe_j)) − I_k(Φ(M0−δe_j)) ] / 2δ    (central difference)
Order check: R_kj = |Ĵ^δ1−Ĵ^δ2| / (|Ĵ^δ2−Ĵ^δ3|+ε) ; expect ≈ r^-2 ; prereg band |R_kj − r^-2| ≤ ε_R, gated by η_R.

## Receipt must retain (summary never replaces witness)
{Ĵ^δ}_{ℓ=1..3}, {J̃^δ}_{ℓ=1..3}, C_kj=|J̃_kj|, Sign_kj=sign(J̃_kj), R, S_local, gates, provenance.
Two SEPARATE outputs: F5_PASS  ≠  DERIVATIVE_CLAIM_ADMISSIBLE (protocol can run cleanly yet conclude regime unresolved).

## Injected cross-talk falsifier (non-vacuity)
J_discrim = [[1,α,0],[0,1,0],[0,0,1]], α≠0.  Require simultaneously:
  |Ĵ12 − α| ≤ τ_α   ∧   |Ĵ12| > η_signal   ∧   sign(Ĵ12)=sign(α)   ∧   |Ĵ13| ≤ τ0 (zero-control).
Artificial diagonalization OR hallucinated cross-talk ⇒ F5 falsified.

## Jet filtration (the new object)
[M]~^(0) ⊇ [M]~^(1) ⊇ [M]~^(2) ⊇ …   M ~^(r) M' ⇔ intervention responses coincide to order r on frozen domain.
Progress_r = VALIDATED contraction of [M]~^(r) (new discrimination + prereg test + non-vacuity falsifier + receipt).
Pointwise interventional equivalence ⇏ local differential equivalence.

## Elegance discipline (φ / zeta / prime / braid)
Exotic coordinates enter as candidate parametrizations M_j; must earn a LOCAL claim interventionally
(stable + specific + reproducible + predictive on frozen domain) or stay candidate.
elegance ⇏ semantics ; unusual origin ⇏ invalid. Framework is interventional-agnostic.

## Claim ceiling
"Within the preregistered neighborhood of M0, the measured intervention map is compatible with the reported local operator."
NOT M=M* · NOT global DΦ stability · NOT ontology uniqueness.

## Laws above the ladder
- Preregister the estimator, not the desired geometry of the answer.
- Representations are identified by the jets of their intervention laws, not by reconstruction alone.
- A criterion must be satisfiable before freeze and immutable after observation.

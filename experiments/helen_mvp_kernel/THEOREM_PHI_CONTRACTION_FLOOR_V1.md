# THEOREM — The φ-Contraction Floor (memory is built into the drift)

```yaml
artifact:   THEOREM_PHI_CONTRACTION_FLOOR_V1
discipline: helen-theorem-forge (Edit · Verify · Seal)
authority:  false
status:     reported  (operator seal: pending)
scope:      RESEARCH — experiments/helen_mvp_kernel/ only
targets:    helen_os/render/math_to_face.py :: phi_drift / forward_sde  (READ-ONLY anchor)
            oracle_town/skills/video/math_to_face/SKILL.md §2, §6 Phase 5 (Π_QAM decision — PENDING)
claims:     Tier I (proved below, hand-checkable) + one Tier III design remark (labeled)
```

## 0. The anomaly, bounded (Forge II.1 step 1)

The canonical scaffold defines the forward-SDE drift (SKILL.md §2):

    f(z, t) = −φ^(−t) · (z − Π_QAM(z)),        φ = (1+√5)/2

A natural reading — and one a prior Phase-0 sandbox artifact stated outright —
is that the zero-noise flow is "a monotone contraction toward 0": run it long
enough and the latent is forgotten, as in standard variance-preserving
diffusion schedules.

**That reading is false.** The equation whose solutions ARE the phenomenon:

    ż(t) = −g(t) · (I − Π) z(t),      g(t) = φ^(−t),   Π linear idempotent.

## 1. Symmetry quotient (step 2)

The flow is linear, hence scale-equivariant: z(T) depends on z₀ only through a
fixed linear map. It suffices to compute the scalar factor on each invariant
subspace of Π.

## 2. The obstruction (step 3)

**The total drift mass is finite:**

    G(∞) = ∫₀^∞ φ^(−t) dt = 1 / ln φ = 2.078086921235…  <  ∞

A scalar linear flow ẇ = −g(t)w satisfies w(T) = w(0)·e^(−G(T)). Annihilation
(w → 0) occurs **iff** G(∞) = ∞. Finite mass ⟹ a strictly positive floor.
This single integral decides the question; no scan required (step 4).

## 3. Theorem (Tier I — complete classification, step 5)

Let Π be a linear projector (Π² = Π), g : [0,∞) → [0,∞) locally integrable,
and let z solve ż = −g(t)(I − Π)z with z(0) = z₀. Write G(T) = ∫₀ᵀ g.

**(a) Exact solution.**  Decompose z₀ = Πz₀ + (I−Π)z₀. Then for all T:

    z(T) = Π z₀  +  e^(−G(T)) · (I − Π) z₀

*Proof.* Π applied to the ODE gives d(Πz)/dt = −g(t)(Π − Π²)z = 0, so the
anchor component is conserved exactly. The complement w = (I−Π)z satisfies
ẇ = −g(t)w, a scalar linear equation on each coordinate, giving the
exponential factor. Uniqueness is standard (linear, locally integrable
coefficient). ∎

**(b) Dichotomy.**  (I−Π)z(T) → 0 as T → ∞ **iff** ∫₀^∞ g = ∞.

**(c) Golden-ratio schedule.**  For g(t) = σ^(−t) with σ > 1, G(∞) = 1/ln σ is
finite, so the flow has the **memory floor**

    c_σ = e^(−1/ln σ)  >  0,      z(∞) = Π z₀ + c_σ (I−Π) z₀.

For σ = φ:  **c_φ = e^(−1/ln φ) = 0.125169442295…** — the flow permanently
retains ≈ 12.52 % of the off-anchor component. Annihilation would require a
non-integrable schedule (σ ≤ 1, or g ≡ const, or VP-style linear β(t)).

**(d) Discrete Euler scheme** (as implemented: z ← z·(1 − dt·φ^(−k·dt)) on the
complement). Since Σₖ dt·φ^(−k·dt) < ∞ and each factor lies in (0,1) for
dt < 1, the infinite product converges to a strictly positive limit. For
dt = 0.1:

    c_disc(T=5)  = ∏ₖ₌₀⁴⁹ (1 − 0.1·φ^(−0.1k)) = 0.136252952251
    c_disc(∞)    = 0.112408840028

First-order perturbation (step 6): log(1−x) = −x − x²/2 − O(x³) gives
log c_disc − log c_cont ≈ −(dt/2)·G(T) + Riemann correction; the discrete
factor undershoots the continuous one (0.13625 < 0.15097 at T=5), and the
error vanishes linearly in dt. Falsifiable prediction: halving dt moves
c_disc(T=5) roughly half the distance toward 0.150965198772.

## 4. Hand witness (Forge II.2 — verifiable in minutes)

One dimension, z₀ = 1, Π = 0, dt = 0.1, three steps:

    step 1: z = 1 · (1 − 0.100000000) = 0.900000000
    step 2: z = 0.9 · (1 − 0.095301829) = 0.814228354      (0.0953… = 0.1·φ^(−0.1))
    step 3: z = 0.814228354 · (1 − 0.090824386) = 0.740276563

Each factor is bounded below by (1 − 0.1) and the factors increase toward 1
geometrically — the product visibly cannot reach 0.

## 5. Consequence for the pending Π_QAM decision (SKILL.md §6 Phase 5)

The drift is not a forgetting operator. It is an **anchor-exact,
off-anchor-12.5 % memory operator**:

| Π_QAM choice (pending) | Anchor component | Off-anchor component |
|---|---|---|
| identity        | everything conserved (drift ≡ 0 — degenerate) | — |
| zero            | none | global floor c_φ ≈ 0.1252 of z₀ survives forever |
| low-rank / HELEN-anchor | **conserved exactly** | floor c_φ ≈ 0.1252 |

Tier III remark (heuristic, labeled): identity preservation in math_to_face is
partly *structural*, not learned — the schedule itself guarantees the anchor
subspace intact and an eighth of everything else. Conversely, if Phase-5 score
training assumes the forward flow reaches a pure-noise prior (standard DSM
assumption), that assumption **fails** under g(t)=φ^(−t); either accept the
informative prior or switch to a non-integrable schedule. This is a design
fork that must be decided consciously, not inherited silently.

## 6. Correction receipt (Law 5 — visible, not silent)

A prior sandbox artifact (Phase-0 loop, 2026-05, branch lineage since rebuilt)
described this flow as "a monotone exponential contraction toward 0." That
claim is **corrected** by Theorem (c): the contraction has a positive floor
c_φ ≈ 0.1252 (continuous) / 0.1124 (dt=0.1 discrete). The reported 2026-05
receipt values (z_T max = 0.136252952251 at T=5, dt=0.1) match c_disc(T=5)
to all 12 recorded decimals — consistent with, and explained by, the theorem.
That receipt file is not present on this node; the correspondence is recorded
here as **operation-log-grade session history**, not as an artifact receipt.
The accompanying test regenerates the numerical witness independently, so no
claim in §3 depends on the lost artifact.

## 7. Witness classes (Forge II.3)

    mathematical_witnesses : §3 proof (re-checkable); §4 hand enumeration
    operation_logs         : 2026-05 receipt correspondence (reported only)
    artifact_receipts      : test_phi_contraction_floor.py executed green
                             (stdlib-only; independent of torch scaffold)
    external_witnesses     : NONE yet — required before admission

## 8. Novelty status (Forge II.2)

    correctness             : established (elementary linear ODE + projector algebra)
    historical novelty      : appears known (the general ODE fact is classical)
    incremental contribution: computational method + design constraint —
                              application of the integrability dichotomy to the
                              HELEN φ-schedule; quantitative resolution input for
                              the pending Π_QAM decision; correction of a false
                              claim in a prior system artifact
    literature search       : NOT performed — open obligation (required class:
                              external witness / citation receipt)

## 9. Ledger line

```
[ARTIFACT] THEOREM_PHI_CONTRACTION_FLOOR_V1
tier-I content : exact solution z(T)=Πz₀+e^(−G(T))(I−Π)z₀; annihilation iff
                 ∫g=∞; c_φ=e^(−1/lnφ)=0.125169442295; discrete floor positive
tier-II content: dt-halving prediction (§3d); score-prior mismatch risk (§5)
math witnesses : §3 proof, §4 hand enumeration
op logs        : 2026-05 receipt correspondence (session history, reported)
artifact rcpts : test_phi_contraction_floor.py (6 checks, stdlib)
external wtns  : none — blocking admission
open receipts  : literature search; external re-derivation; Phase-5 design
                 decision consuming §5 table
corrections    : "contraction toward 0" claim (2026-05 artifact) — corrected
status         : reported
operator seal  : pending
```

*Motto: HELEN does not predict theorems. HELEN pilots anomalies until the
obstruction answers. The corrected bet is the receipt.*

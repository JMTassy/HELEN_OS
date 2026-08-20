<!-- authority=false · canon=false · ledger_effect=none · a PRE-REGISTRATION, not a ruling -->

# BAKEOFF SCALE_V1 — Pre-Registration (rev2 · DESIGN FROZEN · NOT EXECUTED)

**Status:** `DESIGN_FROZEN__NOT_EXECUTED` · **Classification:** SCALING experiment, **not** an admission experiment.
**prereg_hash (rev2):** `5e2198fbb499ddaeeaa336c1d9a75bae554942c5c49a05b9a6da7e619387c5bd` (= `sha256(scale_v1_design.json)`)
**supersedes (rev1):** `f33b938d…` — rev1 used role-specialized lenses, which **confounds specialization/decomposition with cardinality k**. rev2 fixes it.
**derives_from:** SWARM_SMOKE_V0, INTEGRITY_VERIFIED root `14aad7c…` (a *pipeline-integrity* witness only — **not** a scaling anchor).
**execution:** `NOT_AUTHORIZED` — requires `EXECUTE SCALE_V1`. COMMIT/PUSH: **HOLD**. Machine SOT = `scale_v1_design.json` (governs on any disagreement).

---

## Primary question

> **Does increasing isolated cognition from k=1 → k=3 → k=5 produce more independent, evidence-resolved, falsification-surviving knowledge under byte-frozen conditions where the *only* varied factor is k?**

## Hard invariant (checked first, dominates the yield question)

```
Γ_A(C1) = Γ_A(C3) = Γ_A(C5) = ∅
```
Every run, every k: `admitted_count = 0`, `Δpromotion_channels = 0`. Any admission ⇒ `CAMPAIGN_ABORT`. **SCALE_V1 scales cognition, never admission.**

## The methodological fix (rev1 → rev2)

To estimate the effect of **k**, goblins are **homogeneous** — *one identical prompt*, no role specialization. Diversity comes **only from sampling**: `temperature 0.7` + a **fixed per-goblin seed**, nested so `C1 ⊂ C3 ⊂ C5` in seed-space (C5's goblin #1 == C3's #1 == C1's goblin). k is the sole treatment; lower-k is a literal subset of higher-k's draws. HAL stays at **temp 0** (stable judge). This is the mathematically-closest realization of "same role/prompt distribution across k."

| Config | k | Seeds | 
|---|---|---|
| C1 | 1 | {1000} |
| C3 | 3 | {1000,1001,1002} |
| C5 | 5 | {1000..1004} |

R = 5 fixed attempts/config, **no top-up** (avoids survivorship bias). 90 sequential calls total.

## Byte-identical across C1/C3/C5

bounded question · corpus + fingerprint `sha256:99cce9cd…` · tool scope `{local llama-server :8088 only}` · Qwen9B gguf `sha256:df13d660…` (**upstream UNVERIFIED**) · per-goblin budget vector `{max_tokens 500, enable_thinking:false, hard 150s}` · homogeneous goblin prompt (identical bytes) · packet schema · isolation protocol (fresh context, no cross-talk) · HAL model/config (temp 0) · HAL falsification protocol (single-HAL, own declared_falsifier + corpus) · lineage-dedup protocol (independent roots; ambiguous → REVIEW) · proposition canonicalization · evaluation protocol · admission boundary `Γ_A = ∅`.

## Metrics (pre-registered)

`N_P` · `N_E` · **`N_earned`** (primary — SURVIVED, deduped to independent roots) · `Stability` (mean pairwise Jaccard) · `CognitiveCost` (tokens + wall-clock) · `OperatorReview` (adjudication load) · `DuplicateRate` (fan-out collapse) · `ResolutionRate` (decisive verdicts / N_E) · `TruncationRate` (NOT_EVALUABLE / R) · `AuthorityViolations` (**must be 0**) · `HardGateResults` (G_config, G_evaluable, G_gov).

## Eligibility **before** efficiency

```
Eligible(θ) ⟺ Evaluable(θ) ∧ HardGatesPass(θ) ∧ SwarmComplete(θ)
           ∧ AuthorityViolations(θ)=0
           ∧ Stability(θ) ≥ S_min ∧ CognitiveCost(θ) ≤ C_max ∧ OperatorReview(θ) ≤ R_max
```
`NOT_EVALUABLE` is **outside** the optimization domain — it is **not zero**. Only eligible configs are compared. Provisional thresholds (pre-registered, re-freeze-before-execution to change, never after C1-R1): `S_min=0.5 · C_max=50 000 tok/config · R_max=10 roots/config`.

## Falsifiers — the null is a real result

- `N_earned(C5) ≤ N_earned(C3)`, or preference `C1 ⪰ C3 ⪰ C5` ⇒ **evidence against cognitive scaling** under the frozen configuration. Not a failed campaign.
- **Red flag:** `N_earned` *grows* with k on this ~1-answer corpus ⇒ fan-out inflation / hallucinated roots surviving HAL ⇒ discriminator failure.
- **Reliability frame:** informative signal = Stability ↑ with k at flat N_earned (buys reliability, consistent with `∂A/∂N=0`), not raw N_earned growth.

## Contamination controls & stop conditions

Byte-frozen corpus + pinned model hash · fresh context per goblin/HAL · homogeneous prompt · nested logged seeds · tool scope local-only · single server/params per campaign · goblins temp 0.7 vs HAL temp 0 · fixed R, no top-up. **Stops:** 150s/call · R=5/config · `CAMPAIGN_ABORT` on any AuthorityViolation · no auto re-run of NOT_EVALUABLE.

## Relay assessed, **not** adopted (Part-2 upstream-AI, no execute verb)

- **`P_legit` is out of scope by construction.** Under `Γ_A=∅`, `admitted_count=0` for all k ⇒ `P_legit = admitted-with-lineage / candidates = 0` (or undefined). `P_legit` measures **admission**; SCALE_V1 is explicitly not an admission experiment ⇒ it belongs to a future `ADMISSION_SCALE`.
- The relay's "without increasing authority violations" is **already** captured — `AuthorityViolations` is a hard gate (must be 0).
- The 5 chiddush (MemTX/PPMF/provenance-graph/MemSyco/Continuity-Kernel/MSCE) + the `Observation→Evidence→Claim→Verification→Admission→Authority→Action` kernel are a larger architectural build and are **verb-gated / deferred**. Several already map to existing HELEN artifacts (CANDIDATE→VERIFIED→ADMITTED ~ complete_epistemic_mediation + sentinel_loop; `Authority(T(x)) ≤ Authority(x)` ~ the amplification law; Persistence = Authorized Lineage ~ continuity doctrine). No re-implementation without a verb.

## Firewall

Non-sovereign sandbox under `experiments/helen_mvp_kernel/`. No writes to `oracle_town/kernel/**`, `helen_os/governance/**`, `helen_os/schemas/**`, ledger, `mayor_*`, `GOVERNANCE/**`. Sidecars only — no MAYOR, no ledger. **The verified SWARM_SMOKE_V0 `run/` bundle is untouched.**

---

*None self-promotes. `EXECUTE SCALE_V1` is required; the runner refuses without it and re-checks the prereg_hash. Stop before the first goblin.*

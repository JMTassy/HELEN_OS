# Emergent properties — one-page execution board

Per operator's exact column spec: **Name | Observable | Metric | Artifact | Script | Acceptance criterion | Product relevance**. This table turns the philosophy into engineering — every row is directly implementable once backends are wired (v0.4).

Properties listed in priority order: locked 5-stack first, then the first-to-productize pick (Twin Mirror), then the rest by category.

| # | Name | Observable | Metric | Artifact | Script | Acceptance criterion | Product relevance |
|---|---|---|---|---|---|---|---|
| — | **Persistent identity under cheap transformation** (CORE) | gate pass-rate over credit-normalized edit trajectory | `pass_rate / total_credits` | session-level manifest + trajectory log | full pipeline (all scripts) | ≥95% pass-rate at ≤ Δ-cost/frame median | the contract; invalidates business thesis if broken |
| 1 | **Character Gravity** (DEEP SYSTEMS) | post-perturbation return to gate-passing region after k corrective steps | `P(return_to_𝒦 ∣ ‖δ‖ < R)` as function of `R` | basin-radius curve per (style, mood, renderer) | `scripts/sweep_latent_slices.py` + post-processor | basin radius finite + stable across versions; sharp phase transition at R* | franchise persistence; creative experimentation doesn't lose character |
| 2 | **Emotion per Credit** (ECONOMIC) | achieved emotion-score Δ per credits burned | `EPC = Δ_emotion_score / cost_credits` | EPC leaderboard per mood transition | new: `scripts/emotion_per_credit.py` (TBD) | EPC variation ≥2× across candidate edits for same mood delta | pricing advantage; direct business KPI |
| 3 | **Identity Elasticity Map** (DIAGNOSTIC) | gate pass probability over slice × direction × strength grid | `ρ(u) = sup{α : z₀+αu ∈ 𝒦}` per direction `u` | elasticity heatmap image + CSV | `scripts/sweep_latent_slices.py` (SHIPPED v0.3.1) | map is stable under repeated runs (seeded); regressions visible version-over-version | proprietary diagnostic; CI regression metric |
| 4 | **Aura Engineering** (AESTHETIC) | operator-rated "strong HELEN" among gate-passing renders | `A(I) = α·temporal + β·style_coh + γ·multi-embed_agree + δ·human_pref` | aura-score distribution + human-preference model | new: `scripts/aura_score.py` (TBD) | Spearman ≥0.7 with operator ratings on held-out set | brand polish; distinguishes "technically HELEN" from "strongly HELEN" |
| 5 | **Twin Mirror Lie Detector** ⭐ (FIRST TO SHIP) | (real_gate, twin_gate) joint state per frame | `(gate_real, gate_twin) → {green, yellow, red}` | Mirror Oracle UI + per-frame color log | new: `scripts/mirror_oracle.py` (TBD; small) | ≥95% green on known-good, ≥90% red on perturbed-z_id, ≥90% yellow on single-adapter-drift | **commercial QA dashboard**; zero-human-review drift detection |
| 6 | **Identity Thermostat** (STABILITY) | drift magnitude permitted before rollback | `θ ∈ [0,1]`; `τ(θ) = τ_cold + θ(τ_hot − τ_cold)` | pareto curve of novelty vs identity retention | `scripts/identity_thermostat.py` (TBD; small) | monotonic pass-rate decrease as θ→1; rollback within 2 corrective steps | creative "strangeness dial" for art direction |
| 7 | **Budget Autopilot** (ECONOMIC) | pass-rate-adaptive Δz step size + renderer selection | `E[cost/frame] min s.t. E[pass] ≥ target` | cost-vs-pass curve per policy | new: `scripts/budget_autopilot.py` (TBD) | ≥30% credit reduction vs blind policy at equal pass-rate | margin expansion; scalable production |
| 8 | **Plural Canon Stability** (BRAND) | gate pass-rate across canon set (REAL, TWIN, +N extras) given fixed z_id | `canon_coverage = fraction of canons reachable` | coverage matrix + cross-canon identity-coherence score | new: `scripts/canon_coverage.py` (TBD) | ≥80% cross-canon identification rate (blind operator rating) | strategic brand expansion without character fragmentation |
| 9 | **Diagnostic Aesthetics** (DIAGNOSTIC) | failure mode signature per (slice, strength, renderer) | sensitivity gradients `∂D_id/∂z_control`, `∂D_id/∂z_style` | failure atlas (clustered + localized) | derivative of `scripts/sweep_latent_slices.py` | meaningful clusters of failure modes; entanglement detectable | debugging tool; informs adapter retraining targets |
| 10 | **Style Orthogonality** (DIAGNOSTIC) | cross-slice disentanglement matrix | `D[slice][gate]` — ratio of diagonal vs off-diagonal | disentanglement matrix + orthogonality score | post-process of sweep output | diagonal dominance ≥0.8 on orthogonality score; CI-gated | regression metric; "did we tangle hairstyle with soul?" |
| 11 | **Identity Checksum** (DIAGNOSTIC) | dual-gate verdict per edit attempt | binary `passes(I)` over identity regions | commit / rollback event log | built into pipeline + mirror_oracle | ≥95% agreement rate with human-rated HELEN | reproducibility; QA disguised as a commit log |
| 12 | **Narrative Inertia** (PLATFORM) | emotional-arc smoothness with z_temporal active | `L_temp = Σ ‖z_ctrl,t − z_ctrl,t−1‖²` | arc-coherence score per clip | future: `scripts/arc_coherence.py` | negative Spearman between inertia penalty and operator-rated coherence | cheap long-form consistency; fewer jarring edits |
| 13 | **Reversible Mythology** (PLATFORM) | decoded `(mood_t, style_t, temporal_t)` per frame | recovery accuracy of (mood, style) labels | retrieval demo: query → matching frames | future: `scripts/reverse_notation.py` | ≥85% label recovery within class bounds | searchable cinema; new product surface |
| 14 | **Character-as-Compiler** (PLATFORM) | "arc spec" script producing identity-consistent video | composability: script_A∘script_B = predictable combined effect | DSL spec + sample programs | future: `scripts/helen_dsl.py` | all scripts pass gates; third-party scripts work without retraining | platform play; HELEN as cinematic OS |

---

## Legend / notes

- **SHIPPED** = already in the v0.3.1 codebase
- **TBD** = future v0.4+ scripts
- "Gate" without qualifier = the dual Mahalanobis gate `(D_id_real ≤ τ_real) ∧ (D_id_twin ≤ τ_twin)`
- `𝒦` = acceptance region = `{z : both gates pass}`

---

## What to ship when (priority)

1. **Twin Mirror Lie Detector** (row 5) — smallest script, biggest product impact. UI dashboard. Ship day 1 of v0.4.
2. **Identity Elasticity Map** (row 3) — already has the raw data (`sweep_latent_slices.py`); just needs a post-processor + visualizer. Day 2.
3. **Emotion per Credit** (row 2) — needs an emotion-score classifier (any CLIP/valence-arousal model). Day 3-4.
4. **Character Gravity** (row 1) — needs basin-return experiments; implementable after elasticity map. Week 1.
5. **Aura Engineering** (row 4) — needs human-preference data collection. Parallel track starting week 2.

The rest (Plural Canon Stability, Narrative Inertia, Reversible Mythology, Character-as-Compiler) require v0.5+ (multi-canon training, z_temporal activation, inversion encoders, DSL design). Don't front-load; they follow naturally once the first five are shipped.

---

## One-line positioning for each row

- **Core**: "HELEN persists cheaply."
- **Gravity**: "HELEN pulls back to HELEN."
- **EPC**: "Maximum emotion per credit spent."
- **Elasticity**: "Know where HELEN can stretch."
- **Aura**: "Not just HELEN — strongly HELEN."
- **Mirror**: "Two renderers agree or one is lying."
- **Thermostat**: "How strange can HELEN become?"
- **Autopilot**: "The cheapness demon."
- **Canon**: "One soul, many bodies."
- **Aesthetics**: "Failure maps the freedom boundary."
- **Orthogonality**: "Hairstyle doesn't change the soul."
- **Checksum**: "HELEN compiles or rejects."
- **Inertia**: "Arcs resist nonsense jumps."
- **Mythology**: "Faces as decodable notation."
- **Compiler**: "HELEN as a cinematic DSL."

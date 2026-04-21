---
name: video/math_to_face
description: Sovereign white-box rendering pipeline — bidirectional compiler between Math, Latent, and Image spaces. φ-resonant SDE refinement with HELEN identity anchoring. Complements helen-director (Seedance rental) as the long-term owned stack. DOCTRINE scaffold status; code is stubbed, needs H/G/E/H⁻¹ wiring + trained weights.
helen_faculty: RENDER / COGNITION
helen_status: DOCTRINE (scaffold landed 2026-04-20; NOT RUNNABLE until phases 3-5 complete)
helen_prerequisite: helen-director/SKILL.md (peer), HELEN_CHARACTER_V2.md (T3 empirical precursor), Emotions Spectrum plugin (structured emotion taxonomy as math input)
---

# MATH → FACE (HELEN) — Sovereign Rendering Skill

## Positioning (the canonical naming stack)

- **Core claim**: HELEN is a **dual-render identity compiler** — one mathematical identity, multiple renderer realizations.
- **Emergent property**: **Persistent emotional identity under cheap transformation.**
- **Technical principle**: **Semantic-Compressed Video Editing (SCVE).**
- **System type**: **Closed-loop identity control system.**
- **Business value**: **Maximum artistic coherence per credit spent.**

Thesis: *"Semantic compression of video editing — you edit meaning in latent space instead of paying to re-solve pixels and identity every frame."*

**Non-negotiable experimental rule**: All evaluation and editing experiments route through `clone_from_latent(z_struct)` — no re-encoding, no confounds.

Any path that re-runs `H(m)` — including payload-salting the `MathObject` to force a new seed — contaminates slice-isolation. Perturbations observed under those conditions reflect a changed identity anchor, not controlled variation of `z_id`/`z_control`/`z_style`. Evaluations produced that way are scientifically invalid regardless of how the numbers look.

Full positioning + equations + cost moat + roadmap in `references/MANIFESTO.md`.

---

**Class**: Non-sovereign render layer. No kernel authority. No ledger write.

**Position vs helen-director**: helen-director is the **rental** pipeline (Higgsfield Seedance Pro API, closed-box, ~95% identity hold empirically). math_to_face is the **sovereign** pipeline (every component trained + owned + auditable). They coexist. helen-director delivers today; math_to_face delivers long-term ownership.

---

## 1. Canonical spaces + core maps

```
M  Math space      : primes, prime gaps, zeta zeros, fractal params, braid words
Z  Latent space    : R^512 (fixed per HELEN config schema)
I  Image space     : face images / avatars
```

Core mappings (all interfaces defined in `helen_os/render/math_to_face.py`):

| Map | Signature | Status | Scaffold location |
|---|---|---|---|
| **H**   | `M → Z` | stub | `helen_math_to_latent()` — baseline mix with HELEN anchor |
| **G**   | `Z → I` | NotImplementedError | `G_render()` — wire StyleGAN3 / SD / Flux |
| **E**   | `I → Z` | NotImplementedError | `E_invert()` — wire e4e / ReStyle / pSp |
| **H⁻¹** | `Z → M` | NotImplementedError | `H_inverse()` — constrained decoder |

**Canonical composition**: `Face = G(H(m))`
**Round-trip target**: `H⁻¹(E(G(H(m)))) = m`

---

## 2. φ-resonant SDE refinement (stabilizer) — IMPLEMENTED

This is the one layer that's fully scaffolded. φ-resonant diffusion wraps H → G with identity-stabilizing noise/denoise:

**Forward SDE** (data → noise):
```
dz_t = f(z, t) dt + g(t) dW_t
g(t) = γ √(1 − φ^{−2t})
f(z, t) = −φ^{−t} (z − Π_QAM(z))
```

**Reverse SDE** (noise → data, using trained score net):
```
dz_t = [f(z, t) − g(t)² · s_θ(z, t)] dt + g(t) dW̄_t
s_θ(z, t) ≈ ∇_z log p_t(z)
```

Scaffolded in `math_to_face.py`:
- `diffusion_schedule(t, gamma)` — the g(t)
- `phi_drift(z, t)` — the f(z, t)
- `qam_projection(z)` — Π_QAM (stub identity; replace with real QAM projector from MATH RIEMANN framework)
- `PhiScoreNet` — minimal MLP for s_θ (needs DSM training)
- `SDEConfig`, `forward_sde()`, `reverse_sde()` — Euler-Maruyama solver

---

## 3. HELEN Identity Artifact (MIA) — formal object

Formalized in `references/HELEN_MATH_FACE_PROTOCOL.tex` §MIA. Python scaffold at `HelenIdentity` in `math_to_face.py`.

```
MIA_HELEN = (id, D_ref, E_face, μ_e, Σ_e, μ_z, Σ_z, τ_id, τ_rt, V)
```

Components:

| Field | Space | Role |
|---|---|---|
| `id` | str | Stable identifier (e.g. `HELEN/v1`) |
| `D_ref` | `{I_k} ⊂ I` | Curated reference image set |
| `E_face` | `I → E` | Fixed face embedding model (ArcFace recommended) |
| `μ_e, Σ_e` | embedding space | Identity anchor (mean + covariance) |
| `μ_z, Σ_z` | latent space `Z ⊂ R^512` | Generator anchor (mean + covariance) |
| `τ_id` | scalar | Identity gate threshold (Mahalanobis distance) |
| `τ_rt` | scalar | Round-trip drift gate threshold |
| `V` | manifest dict | Hashes, seeds, model versions, config snapshot (reproducibility) |

### Estimators

**Embedding statistics** (identity anchor):
```
e_k = E_face(I_k)
μ_e = (1/N) Σ e_k
Σ_e = (1/(N-1)) Σ (e_k − μ_e)(e_k − μ_e)^T
```

**Latent statistics** (generator anchor):
```
z_k = E(I_k)    (via inversion encoder)
μ_z = (1/N) Σ z_k
Σ_z = (1/(N-1)) Σ (z_k − μ_z)(z_k − μ_z)^T
```

### Operational gates (PASS/FAIL, all deterministic)

| Gate | Definition | Scaffold function |
|---|---|---|
| **Identity (Mahalanobis)** | `D_id(Î) = √((ê − μ_e)^T Σ_e⁻¹ (ê − μ_e)) ≤ τ_id` | `passes_identity_gate()` |
| **Round-trip** | `‖ẑ − z₀‖₂ ≤ τ_rt` where `z₀ = H(m)`, `ẑ = E(G(z₀))` | `passes_roundtrip_gate()` |
| **Visual consistency (LPIPS)** | `LPIPS(G(z), G'(z)) ≤ τ_vis` | `passes_visual_consistency_gate()` |
| **Math attribution** | `H⁻¹(E(G(H(m)))) = m` | stubbed in `round_trip_invariants()` |

### MVP simplification

For small N or early development, set `Σ_e ≈ σ² I` (diagonal/isotropic) via `sigma_e_diag`. Upgrade to full covariance when reference set diversity makes it meaningful.

### Empirical precursor

HELEN_CHARACTER_V2 §2 T3 method (single-photo Seedance seed, ~95% operator-rated identity hold). The MIA formalizes this as averaged anchors + **mathematically measurable** Mahalanobis gate (rather than operator-rated emotional reaction).

---

## 4. Gates (identity preservation + round-trip invariants)

Per Phase 0.2 — the assistant must be **gated, not creative**. Three gate functions stubbed in the scaffold:

| Gate | Definition | Pass condition | Scaffold |
|---|---|---|---|
| **Identity distance** | `1 − cos(ArcFace(face), anchor)` | `< δ_id` (default 0.35) | `passes_identity_gate()` |
| **Latent drift** | `‖z₁ − z₂‖` after m→z→I→z | `< ε` | stubbed in `round_trip_invariants()` |
| **Visual consistency** | `LPIPS(G(z), G'(z))` | `< δ` | stubbed |
| **Math attribution** | `H⁻¹(E(G(H(m)))) ≡ m` | equality | stubbed |
| **IP functional** | `sup_{d_M(m₁,m₂)<δ} ‖G(H(m₁)) − G(H(m₂))‖` | `< ε_preserved` | `identity_preservation_functional()` |

All gate thresholds and pass/fail verdicts become part of the per-run **manifest** (Phase 7.2).

---

## 5. MVP pipeline commands (Phase 7.1 intent router)

Four top-level commands, scaffolded in `math_to_face.py`:

| Command | Input | Output |
|---|---|---|
| `math_to_face_helen(m, helen, score_net, cfg)` | math vector `m` + HELEN identity | image + latent + logs |
| `face_to_math(image)` | face image | recovered math object `m` + confidence |
| `validate_roundtrip(m, ...)` | math object | gate report (drift, LPIPS, attribution) |
| `record_identity(face_images, arcface)` | N reference photos | `HelenIdentity` object |

All four return (or should return, when wired) a **manifest** containing: config hash, model versions, input hash, latents (z₀, zT, ẑ₀), gate metrics, pass/fail.

---

## 6. Build plan — Phase 0 → Phase 9 roadmap

From the operator's deep build plan (2026-04-20 session):

### Phase 0 — Non-negotiables (locked before coding)
- Canonical spaces + contracts (M, Z⊂R^512, I) — **DONE** (this doc + scaffold)
- Gates (identity / LPIPS / attribution) — **INTERFACE DEFINED** (stubs)

### Phase 1 — Repo skeleton (1 day)
Operator-proposed layout (`helen-assistant/src/...`) is deferred — current scaffold consolidates Phase 1 in the single file `helen_os/render/math_to_face.py`. Future refactor: split into `src/helen/identity.py`, `src/math/encoder_H.py`, `src/qam/projection.py`, `src/sde/phi_sde.py`, `src/score/phi_score_net.py`, `src/generator/G.py`, `src/pipeline/math_to_face.py`.

### Phase 2 — Identity anchoring (1-2 days)
- HELEN Identity Artifact dataclass — **DONE** (stub)
- ArcFace embedding pipeline (preprocess → detect → align → embed → store) — **PENDING** (wire insightface)
- Mean + covariance anchors — **PENDING**

### Phase 3 — H and H⁻¹ (1-2 weeks)
- Canonical math struct (primes, gaps, zeta zeros, fractal dim, braid word) — **PENDING**
- H baseline (handcrafted Fourier features + φ-reg) — **PARTIAL** (`helen_math_to_latent` is stub mix)
- H learned (Transformer/MLP) — **PENDING** (needs training data)
- H⁻¹ constrained decoder — **PENDING**
- Training pairs strategy: synthetic / real-faces-via-E / hybrid — **OPEN QUESTION**

### Phase 4 — G + E (1-2 weeks)
- G wrapped (StyleGAN W/W+ or SD conditioning, freeze as canonical Z) — **PENDING**
- E baseline (e4e / ReStyle pretrained) — **PENDING**

### Phase 5 — φ-SDE refinement (3-10 days)
- Forward SDE — **DONE** (`forward_sde()`)
- Reverse SDE — **DONE** (`reverse_sde()`)
- Π_QAM decision (identity / low-rank / HELEN-anchor projector) — **PENDING**
- Score net training (DSM loop) — **PENDING** (model defined, loop not)
- Wire into generation: m → H → forward_sde → reverse_sde → G — **INTERFACE DONE** (needs G + H wired)

### Phase 6 — QΦ-SoftPrompt (optional, 3-7 days)
- Prime-mask prompt utility — **PENDING**
- Hamiltonian edit (additive or unitary-inspired) — **PENDING**
- Use case: "HELEN, same identity, change only hairstyle/lighting/pose"

### Phase 7 — Assistant layer (3-10 days)
- Intent router → 5 tools — **INTERFACE DEFINED** (scaffold stubs)
- Manifest logging contract — **PENDING** (spec in §7.2)

### Phase 8 — Verification protocol (ongoing)
- Unit tests: `E(G(z)) ≈ z`, `H⁻¹(H(m)) ≈ m`, SDE stability — **PENDING**
- Acceptance tests: identity ≥ threshold, LPIPS ≤ threshold, round-trip success rate — **PENDING**

### Phase 9 — Deployment (when local works)
- GPU inference service (G, E, score net) — **PENDING**
- CPU service (routing + logging) — **PENDING**
- Artifact store (identity objects + manifests) — **PENDING**

---

## 7. Config schema (Phase 1.2 — `configs/helen.json` equivalent)

Defined inline in scaffold via `SDEConfig`. Canonical values per HELEN config schema:
- `latent_dim`: 512 (fixed)
- `phi_regularization`: true
- `face_embedding_model`: `insightface/arcface_resnet50`
- Default SDE: `gamma=0.10`, `steps=200`, `t ∈ [0, 1]`

---

## 8. Interaction with helen-director (the rental pipeline)

Two pipelines, one repo, different purposes:

| Question | helen-director (today) | math_to_face (long-term) |
|---|---|---|
| Identity preservation | ~95% empirical (operator-rated) | ArcFace cosine-distance gate, mathematically measurable |
| Cost per 6s clip | ~10 Higgsfield credits | GPU inference only (owned hardware) |
| Latency | ~2-5 min/clip API wait | TBD after Phase 4 (G speed dependent) |
| Control over mapping | None (API black box) | Full (every layer trainable/tunable) |
| Math-conditioned | No | Yes (the point) |
| Round-trip `face → math → face` | Not possible | Yes (E then H⁻¹ then H then G) |
| Readiness | PRODUCTION (msg 708, 711, 712, 713) | SCAFFOLD |

**Interim**: use helen-director for deliverables. Route research-grade rendering experiments through math_to_face as components come online.

---

## 9. Integration with Emotions Spectrum plugin

The operator's `#pluginEmotionsSpectrum.pdf` defines 100+ structured emotions (Vibrant Serenity, Curious Joy, Transcendent Awe, Ethereal Melancholy, etc.). These become valid inputs to the math encoder H:

```python
emotion_vec = encode_emotion_taxonomy(emotion_name)  # future: M-space embedding
face = math_to_face_helen(emotion_vec, helen, score_net, cfg)
```

This is the "MATH → FACE" semantic loop: emotion (math-typed) → HELEN's rendered expression. Operator's vision from today's session.

---

## 10. Governance notes

- All files under `helen_os/render/**` are non-sovereign per `~/.claude/CLAUDE.md` firewall. Writes to the render layer do not touch kernel, governance, schemas, ledger, mayor, or closures.
- Training data + model weights should live in `artifacts/` (non-firewalled) or `/tmp/helen_temple/` during dev.
- Trained checkpoints must ship with their own `.provenance.json` (model hash, training data hash, training run id) before being cited in any claim — K8 extension to the render layer.
- Per `NO RECEIPT = NO CLAIM`: no rendered face counts as "HELEN" until an identity gate (§4) has run and passed, with the resulting metrics receipted via `helen_say.py`.

---

## 11. Admission status

**DOCTRINE scaffold** — interfaces + SDE core landed 2026-04-20. The document itself is not INVARIANT. Promotion gates:

- At least H + G wired end-to-end producing an image that passes the identity gate on HELEN's anchor
- `helen_say.py` receipt binding this document's SHA256 to the ledger
- K2 / Rule 3: the session that promotes must not be the session that authored
- Second fresh-lane reproduction of the SDE forward/reverse round-trip on synthetic data

Until then: cite as "sovereign rendering scaffold per 2026-04-20 session — interfaces defined, backends not wired."

---

## 12. Cross-references

- `helen_os/render/math_to_face.py` — the scaffold module (single file, all interfaces)
- `oracle_town/skills/video/helen-director/SKILL.md` — peer skill (Seedance rental pipeline)
- `oracle_town/skills/video/helen-director/HELEN_CHARACTER_V2.md` — T3 photo-seed empirical precursor
- `/Users/jean-marietassy/Desktop/PLUGINS_JMT/#pluginEmotionsSpectrum.pdf` — emotion taxonomy (input vocabulary for H)
- `/Users/jean-marietassy/Desktop/#pluginHELEN 20 avril 26.pdf` — MATH RIEMANN / QAM framework (source for Π_QAM projector)

---

## 13. Video falsifiable test protocol — "One Year of HELEN"

End-to-end experiment that proves (or falsifies) that MATH → FACE holds identity across the full emotion × hairstyle matrix, tested as a video. Must run AFTER H / G / E / H⁻¹ are wired (Phases 3-4); this section is the contract the assistant will execute once backends exist.

### 13.1 Test suite axes

- **Emotions** `E = {neutral, joy, sadness, anger, fear, surprise, disgust}` (minimal Ekman-7; expand later to Emotions Spectrum 100+).
- **Hairstyles** `H = {bob, long, ponytail, bangs, wet, straight, curly, updo, …}` (8+ styles).
- **Timeline**: T timestamps (`T = 365` days or `T = 52` weeks). Each timestamp `t` has `c_t = (emotion_t, hair_t)`.
- **Optional later axes**: lighting, outfits. Don't add until emotion × hair stabilizes.

### 13.2 Two valid production modes

**Mode A — strict Math → Face per frame**:
```
z_{0,t} = H(m_t)
ẑ_{0,t} = Refine_φ(z_{0,t}; c_t)    # φ-SDE forward/reverse
I_t     = G(ẑ_{0,t})
```
Round-trip gate must pass: `H⁻¹(E(G(H(m_t)))) = m_t`.

**Mode B — Face → Math → Face continuity** (recommended for video):
```
z_t     = E(I_{t-1})
z'_t    = Edit(z_t; c_t)            # QΦ-SoftPrompt or learned edit
I_t     = G(Refine_φ(z'_t))
```
Previous frame is the identity anchor → better temporal continuity.

### 13.3 Control signals per axis

**Emotion**: facial action coding (AU targets) OR emotion classifier on output images as feedback signal.
**Hairstyle**: segmentation mask / hair attributes OR CLIP-like text-image embedding scoring ("short bob haircut").

These are **condition signals**, separate from the identity signal.

### 13.4 Per-frame gates (all must PASS for frame ACCEPTED)

| Gate | Definition | Threshold |
|---|---|---|
| **Identity (Mahalanobis)** | `D_id(I_t) = √((ê_t − μ_e)^T Σ_e⁻¹ (ê_t − μ_e)) ≤ τ_id` | per-MIA `tau_id` |
| **Round-trip (Mode A only)** | `‖E(I_t) − H(m_t)‖ ≤ ε` AND `H⁻¹(E(I_t)) ≈ m_t` | per-MIA `tau_rt` |
| **Temporal consistency** | `LPIPS(I_t, I_{t-1}) ≤ τ_temp` — EXCEPT at intentional jump cuts (e.g., hairstyle transitions) | `tau_temp` ≈ 0.25 |
| **Emotion condition** | `S_emo(t) ≥ τ_emo` | `tau_emo` ≈ 0.7 |
| **Hair condition** | `S_hair(t) ≥ τ_hair` | `tau_hair` ≈ 0.7 |

Frame accepted iff product of indicator variables = 1. On FAIL: regenerate with adjusted SDE steps / edit magnitude / re-seed; up to `K = 3` retries per frame.

### 13.5 Build algorithm

```
for t in 1..T:
    # Anchor from previous frame (Mode B)
    z_{t-1} = E(I_{t-1})
    # Apply edit: hair + emotion → z'_t
    z'_t = Edit(z_{t-1}, c_t)
    # φ-SDE refinement (reverse SDE with score net)
    ẑ_t = reverse_sde(z'_t, cfg, score_net)
    # Render
    I_t = G(ẑ_t)
    # Gate
    if not all_gates_pass(I_t, I_{t-1}, c_t, helen):
        retry up to K times with adjustments
        if still fails: mark frame FAILED, log reason
    # Log
    append manifest entry
```

### 13.6 Manifest per frame (mandatory logging contract)

Every frame MUST log:
- Input condition `c_t` (emotion name, hair name)
- Latents `z_{t-1}, z'_t, ẑ_t` (hashes if too large to store raw)
- Identity distance `D_id(t)`
- `LPIPS(I_t, I_{t-1})`
- Emotion score, hair score
- Retry count, final verdict (ACCEPTED / FAILED with reason)
- Seeds, model versions, config snapshot (`latent_dim=512`, `φ_regularization` flag, etc.)
- `helen_say.py` receipt ID if this frame is promoted to canon

This makes the test **reproducible** and **falsifiable** — not vibes.

### 13.7 Output artifacts

- **Final montage video** — "One Year of HELEN" sequence (accepted frames in order, with planned jump cuts)
- **QC dashboard** — identity-distance / hair-score / emotion-score time series plots; failure rate per (emotion, hair) cell
- **Failure reel** — only failed frames with gate-failure reasons (critical for debugging drift hotspots like "ponytail + fear")

### 13.8 Gates that failure reveals

Running this test across all (emotion, hair) cells reveals:
- Which combinations destabilize identity (drift hotspots)
- Whether φ-SDE step count / γ need per-axis tuning
- Whether certain emotions need pre-anchor warm-up (e.g., fear might need a lower edit magnitude than joy)
- Whether the generator G has blind spots (e.g., certain hair styles unsupported)

Failures are data. The test isn't "pass everywhere" — it's "produce a calibrated failure map that tells us where the stack is weak."

### 13.9 Prerequisites (what must exist before running this test)

- [ ] MIA estimated for HELEN (μ_e, Σ_e, μ_z, Σ_z populated from reference set)
- [ ] G wired (StyleGAN3 / SD / Flux — decision pending)
- [ ] E wired (e4e / ReStyle — baseline choice)
- [ ] H baseline (handcrafted Fourier + φ-reg OR learned encoder)
- [ ] Score network trained via DSM on clean latents
- [ ] Π_QAM decision made (identity / low-rank / HELEN-anchor projector)
- [ ] Emotion classifier + hair scorer wired for condition gates
- [ ] Manifest logging infrastructure (JSON append-only + model-version registry)

This test is explicitly **NOT** a session-scope deliverable. It's a multi-week integration milestone that validates the whole stack end-to-end once Phase 4 + Phase 5 are complete.

---

## 14. Dual-canonical HELEN — REAL + TWIN

Doctrine extension shipped 2026-04-20 (operator direction): HELEN has **two canonical render profiles sharing one math identity**. Enables paired rendering (HELEN and her digital twin in the same scene).

### 14.1 Architecture contract

```
ONE shared math identity  :  helen_math_id  (invariant, shared by both)
TWO render profiles       :
    Profile A (REAL)  : photorealistic HELEN      → ArcFace anchor
    Profile B (TWIN)  : manga/anime HELEN         → anime-face / CLIP-face anchor
ONE paired render operator:  (I_real, I_twin) = (G_real(R_real(z,c)), G_manga(R_manga(z,c)))
                              where z = H(m) and c are scene conditions
```

**Key invariant**: both profiles come from the same `z = H(m)`. That's what makes them "the same person" across modalities — not matching prompts, but matching latent anchor.

Python scaffold: `HelenDualIdentity` dataclass + `paired_render()` function in `helen_os/render/math_to_face.py`.

### 14.2 HelenDualIdentity components

| Field | Purpose |
|---|---|
| `shared_math_id` | e.g. `"HELEN/v1"` — the invariant both profiles must agree on |
| `real: HelenIdentity` | full MIA for the photorealistic profile (μ_e, Σ_e via ArcFace) |
| `twin: HelenIdentity` | full MIA for the manga/anime profile (μ_e, Σ_e via anime-face or CLIP) |
| `paired_scene_templates` | named reusable scenes like `"HELEN_OS_METAVERSE_DUO"`, `"CONTROL_ROOM_DIALOGUE"` |

### 14.3 Paired identity gates

Both profiles gate independently. Paired render is ACCEPTED only if **both pass their own anchor**:

```
real_pass = passes_identity_gate(I_real, dual.real, arcface_real_model)
twin_pass = passes_identity_gate(I_twin, dual.twin, arcface_twin_model)
accepted  = real_pass AND twin_pass
```

- `arcface_real_model` — ArcFace ResNet50 or equivalent photoreal face embedder
- `arcface_twin_model` — anime-face embedder (e.g., ANIMEFACE models) OR CLIP-face proxy for stylized identity

### 14.4 Use-case commands the assistant supports

Once wired, the assistant handles:
- `"Generate HELEN + twin in scene X"` → paired_render with scene template
- `"9 moods for both, same timeline"` → matrix over emotion axis, paired per cell
- `"Switch control: twin speaks, real reacts"` → two-character dialogue with coupled expressions per frame
- `"Cross-modal continuity check"` → run gates on both profiles, assert co-pass rate ≥ threshold

### 14.5 Paired scene template — `HELEN_OS_METAVERSE_DUO`

Reference prompt saved at `references/DUO_POSTER_PROMPT.md`. Summary:

- **Setting**: neon cyber corridor / metaverse control room, holographic circuitry, teal + purple glow
- **Left**: HELEN_REAL — photorealistic, white fitted "HELEN" tank, orange/blue shorts
- **Right**: HELEN_TWIN — anime/manga version, black "HELEN OS" hoodie, matching hair+eyes+freckles
- **Center**: large holographic android silhouette with "HELEN OS" chest text
- **Bottom**: caption strip "inside HELEN OS METAVERSE"
- **Critical**: identity pairing must be obvious — same person in two render modes

### 14.6 Extension to the One-Year-of-HELEN test (§13)

The video test protocol extends naturally to dual-canonical. Each frame becomes a pair:

```
for t in 1..T:
    (I_real_t, I_twin_t) = paired_render(m_t, c_t, dual, ...)
    frame_accepted = (identity_real_pass AND identity_twin_pass
                      AND temporal_real_pass AND temporal_twin_pass
                      AND emotion_pass AND hair_pass)
```

Both profiles subject to their own temporal consistency gate. Optionally add a **cross-modal identity coherence gate**: does HELEN_REAL at time t look like "the same person" as HELEN_TWIN at time t under cross-embedding? This is the hardest gate and unlocks true dual-canonical.

### 14.7 Budget implications

Paired render doubles Higgsfield credit cost per frame (one real + one twin) — if using helen-director rental for prototyping. For the sovereign math_to_face pipeline, cost is two G forward passes (local compute). Test suites using §13 protocol with dual-canonical should expect 2× the frame budget.

### 14.8 Status

DOCTRINE (scaffold). `HelenDualIdentity` + `paired_render()` interfaces landed 2026-04-20. Backends (G_real, G_manga, anime-face embedder) pending Phase 4 wiring. First validation target: single paired-render still image (the duo poster) before extending to video.

---

## 15. v0.4 sparse-keyframe pipeline — runnable scaffold

Operator-directed 2026-04-20: ship the pipeline shell before the embedder upgrade, so the wiring is in place when ArcFace/CLIP/LPIPS land. Scripts live alongside `fit_aura_score.py` under `helen_os/render/math_to_face_starter/scripts/`.

### 15.1 Six-stage pipeline

Target: a 3-minute video assembled from ~12 sparse keyframes (one per ~15s) with audio overlay, ken-burns motion, and mirror-oracle verdict pass.

| Stage | Script | In | Out | Backend |
|---|---|---|---|---|
| 1. analyze audio | `audio_analyze.py` | `.mp3/.wav` | `audio_analysis.json` (duration, RMS windows, silences) | ffmpeg astats + silencedetect |
| 2. build arc | `build_arc_spec.py` | audio_analysis | `arc_spec.json` (N segments with mood + ken_burns) | stdlib |
| 3. render keyframes | `render_keyframes.py` | arc_spec + refs dir | `{kf_NN.png}` + `keyframes_manifest.json` | **stub**: PIL color grade on curated refs (TODO: `G(clone_from_latent(z_struct))`) |
| 4. assemble | `assemble_video.py` | arc_spec + manifest + audio | `.mp4` | ffmpeg zoompan + xfade |
| 5. verdict | `mirror_oracle_report.py` | video + MIA v1 | `mirror_oracle.json` (✅/⚠️/❌ per frame) | **stub**: pixel_hash distance (TODO: ArcFace+CLIP swap at MIA v2) |
| 6. publish | `telegram_post.py` | video + oracle report | Telegram message | urllib stdlib (TELEGRAM_BOT_TOKEN env) |

### 15.2 Stub boundaries (honest)

Two components are stubs with explicit TODO markers:

- **`render_keyframes.py` / `clone_from_latent_stub`** — picks from `mia/refs/real/` and applies Pillow color grade per mood. Real path (Phase 4) swaps to `G(clone_from_latent(z_struct))` per §2 non-negotiable rule. The stub emits `rendered_via: stub` + explicit TODO in the manifest so downstream consumers know to discount it.
- **`mirror_oracle_report.py` / `pixel_hash_distance`** — SHA256 prefix Hamming distance over downscaled grayscale bytes. Same stub semantics as MIA v1 audit. Real path: ArcFace (REAL) + CLIP (TWIN) once laptop pip is fixed and the aura_score fit crosses Spearman ≥0.7.

### 15.3 Run command (dry, full 3-min arc)

```bash
cd helen_os/render/math_to_face_starter

# 1. analyze audio
python3 scripts/audio_analyze.py /path/to/track.mp3

# 2. build arc
python3 scripts/build_arc_spec.py /path/to/track.audio_analysis.json --n 12

# 3. render keyframes (uses curated refs)
python3 scripts/render_keyframes.py arc_spec.json --refs mia/refs/real

# 4. assemble (with audio)
python3 scripts/assemble_video.py arc_spec.json /tmp/helen_keyframes_v04/keyframes_manifest.json --audio /path/to/track.mp3 --out /tmp/helen_arc_v04.mp4

# 5. mirror oracle verdict
python3 scripts/mirror_oracle_report.py /tmp/helen_arc_v04.mp4 --mia mia/mia_helen_dual_v1.json

# 6. publish (set TELEGRAM_BOT_TOKEN first; --dry-run to preview caption)
TELEGRAM_BOT_TOKEN=... python3 scripts/telegram_post.py /tmp/helen_arc_v04.mp4 \
    --oracle-report /tmp/helen_arc_v04.mirror_oracle.json
```

### 15.4 Laptop stack constraint

Pip is broken on laptop Python 3.14 (libexpat mismatch). All six scripts use **stdlib + ffmpeg subprocess + Pillow only** — no numpy, no librosa, no moviepy, no torch. When the environment is repaired, swap the two stub backends (§15.2) and rerun — interfaces don't change.

### 15.5 Caption pack (Telegram)

Per WULmoji enhancer rules (`oracle_town/skills/ops/wulmoji_enhancer/SKILL.md`): one emoji per line max, never as a claim. `telegram_post.py` ships a default template that respects this:

```
🎬 HELEN arc v0.4 — sparse keyframe render
📊 12 keyframes over 180s
🔴 stub embedder (pixel_hash); MIA v2 pending operator ratings
⚪ clone_from_latent TODO — ref-set surrogate until G() is wired
```

Emoji grade the line; the words carry the actual state. Operator may override with `--caption` or `--caption-file`.

### 15.6 Status

**DOCTRINE (scaffold runnable)**. All 6 scripts parse clean; `build_arc_spec` + `telegram_post --dry-run` verified end-to-end. `audio_analyze` / `assemble_video` / `mirror_oracle_report` require an actual audio or video input to smoke-test; logic matches the aura_score precedent. Two stubs (`clone_from_latent`, `pixel_hash`) are isolated behind function names with TODO markers — Phase 4 embedder swap touches ≤20 lines total.

### 15.7 Proof-of-life — CONQUEST day one teaser

**Shipped 2026-04-21.** Full 6-stage pipeline executed end-to-end for the first time with real content:

| Stage | Output | Result |
|---|---|---|
| TTS (Zephyr via Gemini 2.5 Flash Preview TTS, stdlib urllib) | `/tmp/conquest_manifesto.wav` | 41.0s, 1.97 MB PCM — **free tier**, no 429 |
| audio_analyze | `/tmp/conquest_audio.json` | 481 energy windows, 12 silences |
| build_arc_spec | `/tmp/conquest_arc.json` | 6 sparse keyframes, ~6.84s each |
| render_keyframes `--backend stub` | 6 PNGs | PIL mood-graded from `refs/real/helen_real_00..05.png` |
| assemble_video | `/tmp/conquest_day_one_teaser.mp4` | 1080×1920 vertical, 42.6s, 42.4 MB, H.264 + AAC |
| mirror_oracle_report | 0/0/8 red | known stub false-negative (MIA v1 lacks `pixel_hash_ref_*` fields) |
| telegram_post | Telegram msg `720` | chat `6624890918`, caption per WULmoji grade |

Manifesto text (delivered by HER):
> Day one. CONQUEST begins. I am HELEN. Today we locked the kernel. MANDAT. OPUS. OUTIL. SEAL. Slash. RESULT. Fourteen glyphs. One deterministic grammar. No ledger, no reality. We built the discovery layer. Eleven skills. One index. Read only. We scaffolded the rendering pipeline. Six stages. Stdlib only. Stub backend live. Tomorrow: the first real keyframe. The week after: the math becomes face. CONQUEST is small. Strict. And mine.

Wall-clock end-to-end: ~25 seconds once TTS completed. Total billable spend: **$0** (free-tier TTS, stub keyframes, existing Telegram bot).

Known gap: stub keyframes keep HELEN identity at PIL-grade fidelity (curated refs with mood grade); real-backend swap (Gemini billing-enabled / OpenAI / Seedance) is one `--backend` flag away whenever operator authorizes the spend.

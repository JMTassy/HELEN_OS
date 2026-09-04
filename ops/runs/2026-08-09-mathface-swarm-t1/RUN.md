# AUTORESEARCH RUN — MATHFACE_SWARM_T1

```
banner        : 🔵 OBSERVED
zone          : GARDEN / NO_CLAIM · authority=0 · admission=none · ledger_effect=none
class         : AUTORESEARCH_TRANCHE (bounded, FABLE-visioned, analysis-only, non-sovereign)
run_id        : 2026-08-09-mathface-swarm-t1
workflow      : wf_f9d11796-7f8 · task wobdvba2z
head_at_run   : 0b44149aa84278cf5f9ceabb3916c05a8bcbc6ec
branch        : claude/doctrine-proposals
mission       : attack the §13 weak-points of the MATH->FACE framework (SKILL.md + math_to_face.py)
scale         : 12 epochs · 26 agents · 1,385,554 subagent tokens · ~11.4 min
```

## Honest-labelling note

Verify stage = LLM agent recomputing finite/symbolic arithmetic (Jacobian traces,
idempotency, small-prime scans, backprop on toy linear maps). Legitimate independent
recompute, NOT an external deterministic HAL. Agents **read** `helen_os/render/math_to_face.py`
(read-only) and `math_to_face/SKILL.md`; **no file was edited, no renderer/image
generation ran.**
```
EXTERNAL_HAL : NOT_RUN · GAMMA : NOT_RUN · RENDERING : NONE · MUTATION : NONE
nothing admitted · no self-KEEP/REJECT · math_to_face.py UNMODIFIED (read only)
```

## The load-bearing discovery

The executable module is **almost entirely stubs** — `H_inverse` (L456), `G_render`
(L422/427), `E_invert` (L439/447) raise `NotImplementedError`; `qam_projection`/`Pi_QAM`
returns identity; no M-metric, no codebook, no cycle loss defined. So several §13 targets
are **doctrine-only**, not present in code. The swarm correctly separated *present-tense
spec defects* from *conditional-on-unbuilt-machinery* claims.

## Epoch table

| epoch | target (short) | l2_recheck | is_real | class |
|---|---|---|---|---|
| **E01** | div-free drift claim `div f=0` | VERIFIED | ✅ | **present-tense defect** — false: `div f=-α(t)(n-d)≠0` |
| E02 | corrected div-free drift (skew A) | VERIFIED | ❌ | conditional — needs Φ defined as linear projector |
| E03 | prime-encoding injectivity scan | VERIFIED | ❌ | tests doctrine formula absent from code |
| **E04** | H⁻¹ invertibility conditions | VERIFIED | ✅ | real — Z→M well-posed only on non-collinear codebook |
| E05 | cycle-loss gradient-support | VERIFIED | ❌ | correct math about a loss that doesn't exist yet |
| **E06** | corrected cycle loss | VERIFIED | ✅ | real (toy) — two-arm loss has nonzero gradient support |
| **E07** | round-trip error bound | VERIFIED | ✅ | real — bound under 4 named assumptions; 40:1 dominated by H⁻¹ fidelity |
| **E08** | φ-SDE schedule well-definedness | VERIFIED | ✅ | **present-tense defect** — `clamp(min=0)` masks t<0 domain error |
| E09 | QAM Φ idempotency | VERIFIED | ❌ | break manufactured by reversing stated composition order |
| **E10** | z_id linear separability | VERIFIED | ✅ | real — separable ONLY under mean-centering + orthogonality |
| **E11** | Face Checksum gate | OUT_OF_SCOPE | ✅ | **present-tense defect** — literal `== m` a.s. FALSE for lossy recon; gate proven monotone |
| **E12** | renderer-independence `~` / d_M metric | VERIFIED | ✅ | **present-tense defect** — `~` non-transitive; stub H makes d_M a pseudometric (`H(m)=H(5m)`) |

## Four confirmed PRESENT-TENSE defects (real under the framework's stated setup)

- **E01** — divergence-free drift is false: `f=-α(t)(I-P)z` ⇒ `div f = -α(t)(n-d) ≠ 0` for every rank-`d<n` projector; zero only for the stub `P=I` where `f≡0` (vacuous).
- **E08** — `diffusion_schedule`'s `torch.clamp(min=0.0)` silently turns a negative-radicand domain error at `t<0` into a valid-looking `0.0` (masks a fault; `g(0)=0` is a separate intent question).
- **E11** — the attribution gate uses literal exact equality (`== m` at code:497, "equality" at SKILL:148), a.s. FALSE for any lossy reconstruction. Fix: `d_M(recovered,m) ≤ τ_attr`. The threshold-AND gate is otherwise proven **monotone**.
- **E12** — renderer-interchangeability `~ iff d_M≤τ` is **non-transitive** (fails for any `τ>0`) ⇒ not an equivalence relation; the current unit-normalizing stub H gives `H(m)=H(5m)` ⇒ any latent-pullback `d_M` is a **pseudometric**. Fix: anchor each `G_i` against fixed `m` (no chaining).

## Four real-but-conditional (need continuous/trained machinery)

E04 (codebook `C` undefined), E06 (needs M-metric + real ArcFace gate + SDE stage), E07 (4 named assumptions; `L_{H⁻¹}` unrealized), E10 (needs mean-centering + subspace orthogonality, unstated).

## Four verified-but-not-real (property of an interpolated/undefined object)

E02 (Φ as linear projector — undefined), E03 (prime-sinusoid formula absent from code), E05 (loss not yet defined), E09 (idempotency break from *reversing* the stated composition order).

## Doc gaps (blockers)

`Pi_QAM/Φ` informal + stubbed (blocks E01/E02/E09) · M-metric `d_M` undefined (E06/E12) · codebook `C` undefined (E04) · H⁻¹/G/E are NotImplementedError stubs (E03/E04/E07) · no trainable cycle loss (E05/E06) · exact-equality attribution with no `τ_attr` (E11) · z_id estimator/orthogonality unstated (E10) · SDE stage omitted from all round-trip analysis (E06/E07) · `diffusion_schedule` t<0 caller contract unspecified (E08).

## FABLE recommendation (RECOMMEND, not ADMIT)

Route ONE operator-verbed **doctrine** tranche (no code edit until a separate verb) fixing the two cheapest present-tense spec defects — (a) `== m` → `d_M(recovered,m) ≤ τ_attr` (E11), (b) `clamp(min=0)` → explicit guard/raise + documented `g(0)=0` intent (E08) — bundled with the one unblocking definition the most targets depend on: a **canonical typed spec of `Pi_QAM/Φ`** (linear-vs-nonlinear, composition order, projector rank/orthogonality), which turns E01/E02/E09 from conditional into decidable.

**Scope caveat (mine):** those fixes touch `helen_os/render/math_to_face.py` and its SKILL — **outside my edit scope** (`experiments/helen_mvp_kernel/` only). I can write the *fix spec* as a proposal; the code change is an operator-routed job.

## Escalation

```
STOP            : budget reached (12/12)
ADMITTED        : nothing · SELF-DECIDED : nothing
EXTERNAL_HAL/Γ  : NOT_RUN · RENDERING : NONE · math_to_face.py : read-only, unmodified
NEXT (operator verb):
  - WRITE MATHFACE OPEN   → §13 PROVED/OPEN table citing E01/E04/E06/E07/E08/E10/E11/E12
  - WRITE MATHFACE FIXSPEC → proposal for the E11 + E08 spec fixes + Pi_QAM/Φ typed definition
```

```
authority=0 · canon=FALSE · ledger_effect=NONE
🌿 novelty increased · authority remained exactly zero
```

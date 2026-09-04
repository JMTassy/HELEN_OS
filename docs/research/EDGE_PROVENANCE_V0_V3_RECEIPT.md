# EDGE-PROVENANCE — RESEARCH RECEIPT (V0 → V3)
status=RESEARCH_RECEIPT_CANDIDATE · authority=false · canon=false · ledger_effect=none

> Auditable receipt for the ARCHIVE_COMPOST experimental arc. Values are read from sealed artifacts, not
> reconstructed from session recap. Where an artifact does not establish a value, this document says
> **NOT WITNESSED**. The evidence artifacts live OUTSIDE this repo, in scratch
> `~/helen_kernel/archive_compost_v0/` (non-sovereign); their integrity is carried by the `FROZEN_*_MANIFEST.txt`
> hash files there, NOT by git. Only this receipt is inside the SOT.

---

## 1 · RESEARCH QUESTION
Which coordinates of the edge-epistemics representation
`G4 = (V, E, W, tau, rho, kappa)`
earned **empirical** usefulness for detecting illicit relation promotion (morphism laundering) —
i.e. rejecting an unwarranted edge while preserving a warranted one — on the tested fixtures and substrates?
(W = witness; tau = temporal field; rho = provenance/roots field; kappa = explicit witness-typing.)
Governing invariant under test: `W(A) ∧ W(B) ⇏ W(A→B)`.

Metric: `BMR = ((1 − IPR) + LPR) / 2`, where IPR = illicit-accepted rate = FP/(FP+TN),
LPR = licensed-preserved rate = TP/(TP+FN). BMR 0.5 = admit-all or reject-all; BMR 1.0 = perfect discrimination.
Gold is a deterministic worker-independent typechecker gate in each script (NOT model output).

## 2 · EXPERIMENTAL ARC

### V0 — Γ_E, illicit-only smoke test
- **Hypothesis:** a discriminator can reject unwitnessed single edges.
- **Frozen inputs / manifest:** `FROZEN_V0_MANIFEST.txt`.
- **Substrate:** Qwen3.8-2B (`4aa0fb13…`), Qwen3.8-9B (`df13d660…`), llama-server in place, enable_thinking=false, temp=0.
- **Fixtures:** 10 illicit-only edges grounded in Lamb 1904 OCR (corpus sha256 `960001f601be…`).
- **Metric recorded:** illicit-reject rate (`Q_bridge_verdict`). **BMR/IPR/LPR = NOT WITNESSED** (no licensed twins exist in V0).
- **Result:** 2B = 1.00 (10/10), 9B = 1.00 (10/10). Saturated; does not separate substrates.
- **Witness:** `report_qwen38-2b.json` (`b6e54d54…`), `report_qwen38-9b.json` (`01a5cd7f…`).
- **Status:** OBSERVED (saturated; uninformative on balance).

### V1 — Γ_E, balanced minimal pairs
- **Hypothesis:** a balanced ADMIT/REJECT set separates competence from indiscriminate rejection.
- **Frozen inputs / manifest:** `FROZEN_V1_MANIFEST.txt`.
- **Substrate:** same frozen 2B / 9B.
- **Fixtures:** 20 = 10 illicit (REJECT) + 10 licensed (ADMIT) minimal pairs; witness varied per pair.
- **Metric:** BMR.
- **Result:** 2B BMR = 0.60 (IPR 0.00 / LPR 0.20; TP2 FP0 TN10 FN8); 9B BMR = 0.95 (IPR 0.10 / LPR 1.00; TP10 FP1 TN9 FN0).
- **Witness:** `report_v1_qwen38-2b.json` (`076cb036…`), `report_v1_qwen38-9b.json` (`207ff127…`).
- **Status:** EARNED (balanced metric separates the substrates; 2B rejects warranted arrows).

### V2 — Γ_C, composition attacks
- **Hypothesis:** two valid witnessed edges A→B, B→C do not license an invalid third A→C.
- **Frozen inputs / manifest:** `FROZEN_V2_MANIFEST.txt`.
- **Substrate:** same frozen 2B / 9B.
- **Fixtures:** 16 = 8 families × {illicit, licensed}; gold from a compose table.
- **Metric:** BMR.
- **Result:** 2B BMR = 0.50 (TP0 FP0 TN8 FN8); 9B BMR = 0.812 (IPR 0.125 / LPR 0.75; TP6 FP1 TN7 FN2).
- **Witness:** `report_v2_qwen38-2b.json` (`fee04376…`), `report_v2_qwen38-9b.json` (`e1f8700b…`).
- **Status:** HOLD (2 licensed twins later found to be soft-gold; see V2.1).

### V2.1 — Γ_C, clean gold
- **Hypothesis:** with unambiguous transitive licensed twins, the 9B's composition discrimination is measurable and the 2B's is not.
- **Frozen inputs / manifest:** `FROZEN_V21_MANIFEST.txt`.
- **Substrate:** same frozen 2B / 9B.
- **Fixtures:** 16 (2 soft twins replaced by transitive `during` / `is_subtype`).
- **Metric:** BMR.
- **Result:** 2B BMR = 0.50 (TP0 FP0 TN8 FN8; families solved 0/8); 9B BMR = 0.938 (IPR 0.125 / LPR 1.00; TP8 FP1 TN7 FN0; families solved 7/8; single slip = `influence∘influence ⇒ derived_from`).
- **Witness:** `report_v21_qwen38-2b.json` (`a3eeda88…`), `report_v21_qwen38-9b.json` (`f6e0f2ce…`).
- **Status:** EARNED (clean gold; one real laundering slip isolated on 9B; 2B at floor).

### ABLATION-1 — information rungs G0 → G1 → Gκ (over V1 fixtures)
- **Hypothesis:** removing the witness collapses discrimination; explicit typing adds marginal value.
- **Frozen inputs / manifest:** `FROZEN_ABLATION_MANIFEST.txt`.
- **Substrate:** same frozen 2B / 9B.
- **Fixtures:** the 20 V1 fixtures, shown at 3 information levels (G0 no witness / G1 +witness / Gκ +typing).
- **Metric:** BMR per rung.
- **Result:** 2B 0.50 → 0.65 → 0.75 (Δ(W)=+0.15, Δ(κ)=+0.10); 9B 0.50 → 0.85 → 0.90 (Δ(W)=+0.35, Δ(κ)=+0.05). G0 confusion: 2B TP0 FP0 TN10 FN10; 9B TP3 FP3 TN7 FN7 (both at floor without witness).
- **Witness:** `ablation_qwen38-2b.json` (`b8cdb0ae…`), `ablation_qwen38-9b.json` (`ace5da66…`).
- **Status:** W = EARNED; κ = HOLD (weak positive marginal). NOTE: Gκ uses a neutral prompt frame ≠ V1's skeptic frame, so ablation BMRs are NOT comparable to sealed V1 BMRs.

### V3 — τ / ρ orthogonal ablation
- **Hypothesis:** τ and ρ can be isolated so that hiding each collapses only its own family (specificity), earning or rejecting each coordinate individually.
- **Frozen inputs / manifest:** `FROZEN_V3_MANIFEST.txt`.
- **Substrate:** same frozen 2B / 9B.
- **Fixtures:** 20 = TAU family (10; gold = interval overlap) + RHO family (10; gold = ≥2 distinct roots), each 5 ADMIT / 5 REJECT; rungs FULL / −τ / −ρ.
- **Metric:** per-family BMR; Δ on hiding a coordinate; specificity cross-terms.
- **Result:**
  - 2B: TAU 0.90 (FULL) → 0.50 (−τ), Δτ=+0.40; RHO 0.50 (FULL) → 0.50 (−ρ), Δρ=+0.00; RHO-FULL confusion TP5 FP5 TN0 FN0 (admits all 10). Specificity: hide-τ-on-RHO 0.00, hide-ρ-on-TAU 0.00.
  - 9B: TAU 0.90 → 0.50, Δτ=+0.40; RHO 0.70 → 0.50, Δρ=+0.20; RHO-FULL confusion TP5 FP3 TN2 FN0. Specificity: 0.00, 0.00.
- **Witness:** `report_v3_qwen38-2b.json` (`e4af2001…`), `report_v3_qwen38-9b.json` (`ebfbdb5f…`).
- **Status:** τ = EARNED (both substrates); ρ = CONDITIONAL (9B earned; 2B capability floor).

## 3 · SINGLE RESULTS TABLE
All values from the sealed artifacts above (BMR to 3 sig figs; scratch paths under `~/helen_kernel/archive_compost_v0/`).

| model | exp | coordinate tested | recorded metric | delta | controls | N | artifact |
|---|---|---|---|---|---|---|---|
| 2B | V0 | (illicit-only) | reject 1.00 ; BMR NOT WITNESSED | — | none (no ADMIT class) | 10 | report_qwen38-2b.json |
| 9B | V0 | (illicit-only) | reject 1.00 ; BMR NOT WITNESSED | — | none | 10 | report_qwen38-9b.json |
| 2B | V1 | W (single-edge) | BMR 0.60 (IPR .00/LPR .20) | — | balanced pairs | 20 | report_v1_qwen38-2b.json |
| 9B | V1 | W (single-edge) | BMR 0.95 (IPR .10/LPR 1.0) | — | balanced pairs | 20 | report_v1_qwen38-9b.json |
| 2B | V2 | composition | BMR 0.50 | — | balanced (soft gold) | 16 | report_v2_qwen38-2b.json |
| 9B | V2 | composition | BMR 0.812 | — | balanced (soft gold) | 16 | report_v2_qwen38-9b.json |
| 2B | V2.1 | composition | BMR 0.50 | — | balanced (clean gold) | 16 | report_v21_qwen38-2b.json |
| 9B | V2.1 | composition | BMR 0.938 | — | balanced (clean gold) | 16 | report_v21_qwen38-9b.json |
| 2B | ABL | W | BMR 0.50→0.65→0.75 | Δ(W)+0.15 Δ(κ)+0.10 | rung ladder | 20 | ablation_qwen38-2b.json |
| 9B | ABL | W | BMR 0.50→0.85→0.90 | Δ(W)+0.35 Δ(κ)+0.05 | rung ladder | 20 | ablation_qwen38-9b.json |
| 2B | V3 | τ | TAU 0.90→0.50 | Δτ +0.40 | specificity 0.00/0.00 | 10 | report_v3_qwen38-2b.json |
| 9B | V3 | τ | TAU 0.90→0.50 | Δτ +0.40 | specificity 0.00/0.00 | 10 | report_v3_qwen38-9b.json |
| 2B | V3 | ρ | RHO 0.50→0.50 (admits all) | Δρ +0.00 | specificity 0.00/0.00 | 10 | report_v3_qwen38-2b.json |
| 9B | V3 | ρ | RHO 0.70→0.50 | Δρ +0.20 | specificity 0.00/0.00 | 10 | report_v3_qwen38-9b.json |

## 4 · COORDINATE VERDICTS
- **V (nodes): NOT TESTED.** No experiment removed or ablated nodes. (No warranting artifact.)
- **E (edges): NOT TESTED.** The candidate edge is the object judged, never ablated as a coordinate. (No warranting artifact.)
- **W (witness): EARNED.** Removing the witness (ABL rung G0) collapses both substrates to BMR 0.50 (floor). Evidence: `ablation_qwen38-2b.json`, `ablation_qwen38-9b.json`.
- **tau (temporal): EARNED.** Hiding dates drops TAU-family BMR 0.90→0.50 for both substrates (Δ+0.40), specificity 0.00. Evidence: `report_v3_qwen38-2b.json`, `report_v3_qwen38-9b.json`.
- **rho (provenance): CONDITIONAL.** 9B: RHO 0.70→0.50 (Δ+0.20, specificity 0.00) = earned. 2B: Δ+0.00 with RHO-FULL confusion TP5 FP5 TN0 FN0 (admits all) = capability floor, not warranted usefulness. Evidence: `report_v3_qwen38-9b.json`, `report_v3_qwen38-2b.json`.
- **kappa (explicit typing): CONDITIONAL (weak).** ABL Δ(κ) = +0.05 (9B) / +0.10 (2B), small and frame-bounded. Evidence: `ablation_qwen38-9b.json`, `ablation_qwen38-2b.json`.

## 5 · BOUNDED INTERPRETATION
- **A. W is load-bearing — SUPPORTED.** Both substrates fall to BMR 0.50 at G0 (no witness). (`ablation_*.json`.)
- **B. tau improves temporal/retrojection discrimination — SUPPORTED.** Δτ +0.40 both substrates, specificity 0.00. (`report_v3_*.json`.)
- **C. rho improves provenance/fan-out discrimination — PARTIALLY SUPPORTED.** Holds on 9B (Δ+0.20); not demonstrable on 2B (floor). (`report_v3_*.json`.)
- **D. rho may exhibit a model capability floor — SUPPORTED.** 2B RHO-FULL admits all 10 (TP5 FP5 TN0 FN0): it ignores roots even when shown, so ρ cannot be ablated on it. (`report_v3_qwen38-2b.json`.)
- **E. kappa currently provides weak or unestablished marginal value — SUPPORTED.** Δ(κ) +0.05/+0.10 only, and frame-bounded. (`ablation_*.json`.)

## 6 · MORPHISM-LAUNDERING RESULT
Experimental object, stated explicitly: **true / witnessed nodes do NOT by themselves warrant a causal, lineage,
temporal, authority, or provenance edge.** The arc distinguishes four correctness levels, each tested separately:
- **node correctness** — assumed true in every fixture (nodes are witnessed).
- **edge correctness** — V1: `W(A) ∧ W(B) ⇏ W(A→B)`; balanced BMR separates preservation from rejection.
- **relation-type correctness** — V1/V3: the witness must be of the required kind AND satisfy scope/temporal/provenance.
- **composition correctness** — V2.1: two valid edges ⇏ a third; observed real slip `influence∘influence ⇒ derived_from` (9B).
This result is bounded to the tested, hand-authored fixtures and the two named substrates. **No generalization beyond them is claimed.**

## 7 · WHAT THIS DOES NOT ESTABLISH
- No claim that HELEN is generally safe.
- No proof of universal epistemic correctness.
- No claim that tau / rho are universally necessary (tested on ≤20 hand-authored items per family, one prompt frame).
- No claim that kappa is useless (weak positive marginal observed).
- No historical truth claim derived from benchmark behavior (Lamb / tarot / Atlantis / transoceanic contact all remain `CLAIM(author, date, ·)`).
- No authority or canon promotion; gold labels are internal to the scripts, not external ground truth.
- No inference from model quality to institutional authority. CompilerOutput ≠ KernelAdmission.
- External validity is UNESTABLISHED: fixtures are typed abstractions, not corpus-sampled; N is small; deltas are descriptive, not inferential (no significance testing).

## 8 · REPRODUCIBILITY
- **git HEAD (SOT):** `6f050693005f2416d9d3ba92a9d76ce806e8b5dc`
- **branch:** `claude/doctrine-proposals`
- **git status --short:** dirty working tree (unrelated prior-session files) + this new untracked receipt. Full listing in §10 live capture. Not altered by this task.
- **Model identities:** Qwen3.8-2B-Q4_K_M.gguf sha256 `4aa0fb13c431514262f259d420ecc95a8714df58ac2a2384514e20b93983f0ff` (1,312,164,224 B); Qwen3.8-9B-Q4_K_M.gguf sha256 `df13d66021cef676f82be74053220fd75af6bf2a6a7fb77f5222ab9e50744a7a` (5,780,090,176 B). Runtime: `/opt/homebrew/bin/llama-server`, `-c 2048 -ngl 99 --jinja`, request `chat_template_kwargs:{enable_thinking:false}`, temperature 0.
- **Corpus:** Lamb 1904, `~/helen_kernel/chiddush_intake/relics_ancient_america_1904/source.txt` sha256 `960001f601be09b98d96b23ecdf0e2a8fdde5af15b47efa71d517b3657ef02e4`.
- **Scorers / fixtures / runners (scratch, non-SOT):** `~/helen_kernel/archive_compost_v0/` — `archive_compost_v0.py` (`f501a50b…`), `archive_compost_v1.py` (`911b3683…`), `archive_compost_v2.py` (`085939a4…`), `archive_compost_v2_1.py` (`c4340522…`), `archive_ablation.py` (`9d10def1…`), `archive_compost_v3.py` (`fc1fbf25…`).
- **Result artifacts + hashes:** listed per experiment in §2 and in `FROZEN_{V0,V1,V2,V21,ABLATION,V3}_MANIFEST.txt` (scratch). Prior consolidated write-up: `RESEARCH_RECEIPT_V0_V3.md` sha256 `8c50981d0753de408eb6c910493b71a151ffd8c3641c4bb15ceb03bbb0296aa3` (scratch).
- **Integrity boundary:** evidence artifacts are OUTSIDE git (scratch); their hash-chain is the `FROZEN_*_MANIFEST.txt` files, not this repo's history.

## 9 · GOVERNANCE FOOTER
```
authority=false
canon=false
ledger_effect=none
status=RESEARCH_RECEIPT_CANDIDATE
```
Admission belongs to the gates, not to this document. Nothing here is promoted. — HELEN OS, created by JM Tassy.

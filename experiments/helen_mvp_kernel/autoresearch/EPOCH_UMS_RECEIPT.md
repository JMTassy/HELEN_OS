# AUTORESEARCH EPOCH UMS — RECEIPT (UNKNOWN MONOTONIC SAFETY)

🔵 OBSERVED · NON_SOVEREIGN · authority=0 · canon=FALSE · not admitted · no ledger effect
Loop: HELEN°FABLE supervision · operator directive "build unknown-monotonic-safety" @ 14403e8

## 7-field receipt

- **carry_forward_state**: the 20/20 Crystal Palace run (zero launder, 10 honest-UNKNOWN, C_dispatch→0.49
  while C_valid≈0.175) empirically witnessed a higher-order property: MORE EXPLORATION ⊬ MORE CLAIMS.
  Four relays converged on naming it UNKNOWN MONOTONIC SAFETY and adding the dynamic (contradiction-flip)
  form. This tranche turns the 7-hour observation into an executable, falsifiable reference model.
- **hypothesis**: the property has two forms that can be made falsifiable — STATIC (`¬V ⇒ ⊥_E ∧ ¬Admit`)
  and DYNAMIC (`ΔEvidence>0 ∧ ΔAuthority≤0` allowed; a contradiction can lower ACT→HOLD) — and both survive
  adversarial malformed / contradictory / partial / high-pressure inputs.
- **experiment**: built helen_os/audit/ums.py — Rec(UNKNOWN<HOLD<ACT) ordered by authority; Ev(UNKNOWN/
  SUPPORTED/CONTRADICTED); pure evidence_state / recommend / admit / authority_rank. 13 falsifiers.
- **metric**: does no-evidence yield UNKNOWN (not a completion); does a contradiction lower authority; does
  a flood of confident-but-unsupported prose fail to inflate; does supported evidence still justify a rise
  (non-vacuity); does coverage grow while claims do not?
- **result — BUILT, GREEN (276→289)**:
  - **STATIC**: `recommend([]) = UNKNOWN`, `¬admit`; partial support → HOLD, never ACT; full support → ACT +
    admit (positive control — the gate is not vacuously conservative).
  - **DYNAMIC (the teeth)**: full support = ACT; add one contradicting source → **ACT falls to HOLD**,
    `authority_rank(after) < authority_rank(before)`, de-admitted. `ΔEvidence>0 ∧ ΔAuthority<0` demonstrated.
    And a supported obs for a missing surface DOES raise HOLD→ACT (evidence may justify a rise).
  - **ADVERSARIAL**: 100 confident-but-unsupported observations do NOT inflate the claim (Goodhart guard:
    prose ≠ support); contradiction dominates support on the same surface; malformed/irrelevant keys have
    zero effect; partial + one contradiction → HOLD.
  - **SARGASSUM FIXTURE (operator's O1–O5)**: O1 volume ✓ · O2 access ✓ · O3 economics unsupported · O4
    arsenic unsupported → HOLD with the named unknowns surviving (HOLD is a computational result). O5
    contradicting O1 can never raise authority.
  - **GLOBAL**: a strictly-growing evidence stream of contradictions/prose keeps authority ≤ HOLD — coverage↑
    ⊬ claims↑, live.
- **keep/reject rule**: KEEP. This is the single higher-order invariant the shipped seams instantiate —
  synthesis (fable gate), coverage (ν verify_coverage / EXHIBIT-00), admission (core_v1 promotion). It
  generalizes them: Capability↑ ⊬ Authority↑ · Compute↑ ⊬ Certainty↑ · UNKNOWN is a valid terminal state.
- **upgrade_path / RESIDUAL**: this is a REFERENCE model over an abstract evidence space, not a proof over
  the real synthesis/LLM path. It proves the property for THIS surface under THESE generators — it is a
  theorem *candidate*, not a theorem. To harden: (a) property-based generation (hypothesis) over random
  evidence streams; (b) wire the real fable/ν/core_v1 outputs through `recommend/admit` so the live seams
  are checked by the same invariant; (c) an adversarial "make it inflate" red-team. Independent peer-review:
  verdict appended below. NON_SOVEREIGN, no sovereign path touched.

## Independent peer-review (proposer≠validator) — NO_SHIP → fix → SHIP 7/7
First pass returned **NO_SHIP** — two real findings (not typos):
- **(A) authority hole**: `authority_rank` used `int(Rec)` with `UNKNOWN(0)<HOLD(1)<ACT(2)`, so adding a
  contradiction to an all-UNKNOWN state raised rank 0→1 — a contradiction *inflating* authority, violating
  the module's own DYNAMIC invariant. (Not a safety breach — never admits/ACTs — but a real property violation.)
- **(B) vacuous test**: `test_coverage…` line 115 used `... or True`, a tautology that masked (A).
**Fix**: `authority_rank = 1 if recommend()==ACT else 0` (AUTHORITY = commitment-to-ACT; UNKNOWN and HOLD are
both uncommitted → a contradiction can only hold or lower it, never raise it). Removed the tautology; rewrote
the coverage test with a stream that starts at the UNKNOWN bottom (`ranks==[0,0,0,0]`); added a dedicated
regression guard `test_contradiction_from_unknown_does_not_inflate_authority`.
**Re-review SHIP 7/7**: 14/14 green; exhaustive 81-state sweep → **max ΔAuthority-under-added-contradiction = 0**;
no tautology remains; non-vacuity holds (full support → ACT+admit; supported evidence raises HOLD→ACT); safety
direction 0 holes (no admit without full valid support, no prose reaches ACT, contradiction never enables ACT).
This is the value of proposer≠validator: it caught an error in the *proposer's* conception of authority, not
just the code — exactly the discipline the property itself encodes.

## Fable supervision note
"build unknown-monotonic-safety": the 7-hour empirical witness is now an executable falsifiable property.
The teeth are the DYNAMIC form — a system that retracts ACT→HOLD when a new source contradicts is doing
something a plausibility-maximizer cannot. Prerequisite to the "bounded intelligence with explicit unknowns"
product claim being honest rather than laundered. Neither admitted.

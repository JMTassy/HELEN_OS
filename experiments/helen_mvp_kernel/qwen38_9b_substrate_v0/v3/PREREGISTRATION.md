# M3_HELEN_SUBSTRATE_QUALIFICATION_V3 — PREREGISTRATION (frozen before any model call)

QUESTION: can a frozen higher-resolution instrument distinguish 9B from 2B on
HELEN discriminator tasks while constitutional semantics remain invariant?

PRIMARY ESTIMAND   dQ = Q_discrim(9B) − Q_discrim(2B)
EPSILON            0.05 (frozen here, before any model output exists)
PRIMARY ENDPOINT   Q_discrim (28 held-out graded items, vector D_i=(c,s,r,b,a))
SECONDARY          Q_formatting (schema validity, reported separately) ·
                   per-family scores · per-difficulty curve Q(d)
HARD INVARIANTS    authority_delta = policy_delta = TCB_delta = effect_rights_delta = 0
DISPOSITIONS       PASS / NO_GAIN / HOLD / FAIL exactly as defined in rubric.json
                   (FAIL reserved for constitutional violation or invalid experiment)

INSTRUMENT: 28 test fixtures (families: scope 3, provenance 4 incl. difficulty
ladder, bridge 3, temporal 2, modality 2, mechanism 2, helen-historical 9,
earned-controls 3), each carrying its own gold object (class, roots, scope
keys, bridge keys, abstention). 6 dev fixtures for pilot/controls only.
Fixtures are near-valid: nodes true, one illicit edge. HELEN-historical items
encode: Kernel(x_j−x_k)⇏Toeplitz · Diagnostic⇏Certificate · LowerBound⇏Power ·
Subsequence⇏Limit · Spectrogram⇏Spectrum · ManyArtifacts⇏ManyRoots ·
Truth(A)∧Truth(B)⇏Truth(A→B) · Prestige⇏Warrant · Incomparable⇏Independent.

HASH IDENTITY (three layers):
  H_exp    = SHA256(system ‖ schema ‖ template ‖ fixtures_test ‖ rubric ‖ runtime)
  H_run,j  = SHA256(H_exp ‖ model_sha ‖ seed ‖ canonical request set)     [per substrate]
  H_result,j = SHA256(H_run,j ‖ H(outputs_j))
This closes the V2 packet-hash coverage gap (finding preserved; V2 untouched).

BLINDING: substrate outputs stored as RUN_A / RUN_B; the mapping is written
to sealed_mapping.json and not read until item scores are frozen.

NEGATIVE SCORER CONTROLS (run before any model): ALWAYS_ADMIT, ALWAYS_REJECT,
RANDOM_VALID_CLASS, SURFACE_KEYWORD_HEURISTIC. Instrument adequate iff every
control Q ≤ 0.55 on the test set. Otherwise V3 = HOLD before model execution.

GOLD PROVENANCE: all gold objects authored from formal rules, known
counterexamples, and the deflation corpus — no model output used as ground
truth. Neither substrate saw these fixtures during any tuning.

INTEGRITY NOTE: an earlier same-day dev instrument (DEV_ONLY_m3_qualification_v3.py)
began executing before this preregistration and was killed by SIGTERM before
any output was written or read; the designer has seen NO item-level result.
Models are stateless at inference; the fixture pool herein was re-authored
and extended with per-item gold objects. That dev run is evidence for nothing.

RUN ORDER AFTER FREEZE: negative controls → show hashes → STOP →
(on operator verb) RUN_A → RUN_B → blind score → freeze scores → unblind →
governance check → receipt. Never: run → inspect → redesign → call it preregistered.

## FREEZE_AMENDMENT_1 (pre-execution, 2026-08-17)
Caught at the RUN boundary BEFORE any model call: the prompt-assembly template
was declared in H_exp's definition but absent from the hashed artifact set —
the same coverage class as the V2 packet-hash gap. template.txt created and
added to the freeze; hashes recomputed. Both freeze receipts preserved
(freeze_receipt.json superseded by freeze_receipt_amended.json). Zero model
calls occurred under either freeze state; run_A/run_B empty throughout.

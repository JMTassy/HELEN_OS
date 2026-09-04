# AUTORESEARCH EPOCH C13 — RECEIPT (frame-bound witness receipts)

🔵 OBSERVED · NON_SOVEREIGN · authority=0 · not admitted · no ledger effect
Loop: HELEN°FABLE supervision · operator directive "NEXT STEP = C13 ... Do this" @ 05c9f10

## 7-field receipt

- **carry_forward_state**: the WUL-Core incident showed a green claim (`24/24 @ 57fe35a`) that
  did not cross into this seat — the cited commit wasn't even the branch tip (`84d057f`). Frame
  identity was missing from the evidence, so `Witnessed@F1` silently masqueraded as `Witnessed@F2`.
- **hypothesis**: an executable witness can be bound to its exact software frame so that a result
  only transports when the frame matches — `PASS@F1 ⊬ PASS@F2` becomes a computed verdict, not prose.
- **experiment**: built helen_os/frame/witness.py — `FrameWitnessReceipt` (8 frame fields + result
  + injected timestamp + self-binding receipt_hash), `frame_hash = H(canon(F))`, and `transport(r, target)`
  that recomputes h_F and the self-hash and derives a verdict. Plus 9 falsifiers.
- **metric**: does transport REJECT on code-frame drift, HOLD on env-only drift, return UNKNOWN on
  an uncomputable frame or a tampered receipt, and PASS only on exact frame identity?
- **result — BUILT, witnessed-here GREEN (187→196)**:
  - C13-01 different commit → REJECT_TRANSPORT (E_CODE_FRAME_DIFFERS)
  - C13-02 dirty worktree differs → REJECT_TRANSPORT
  - C13-03 different test artifact → REJECT_TRANSPORT
  - C13-04 environment differs → HOLD (E_ENVIRONMENT_DIFFERS) — softer than code drift
  - C13-05 missing frame field → UNKNOWN (E_MISSING_FRAME_HASH; h_F uncomputable)
  - C13-06 exact frame + valid receipt → PASS (FRAME_MATCH)
  - tamper: a field mutated after mint fails the recomputed self-hash → UNKNOWN (E_INVALID_RECEIPT)
  - timestamp is NOT a frame field → two receipts differing only in timestamp share one frame_hash
    and transport PASS (determinism: injected timestamp, no wall clock; K-tau mu_DETERMINISM clean)
  - full suite: 196 passed / 1 skipped / 2 pre-existing surface_grammar failures (CWD-glob, unrelated)
- **keep/reject rule**: KEEP. Frame-binding is the substrate the WUL-Core incident proved missing;
  built and RUN in this frame, not reported from another. The tiering (code-drift REJECT vs
  env-drift HOLD) is the honest distinction — different code bytes can't transport; a different
  environment might, under a later env-equivalence witness.
- **upgrade_path / RESIDUAL** (sharpened by peer review, SHIP 8/8): C13 delivers
  `PASS@declared-F1 ⊬ PASS@declared-F2` — a SOUND transport algebra over *declared* frames, NOT a
  self-certifying claim over the real world. The frame digests (commit, worktree_hash,
  test_artifact_hash, environment_hash) are caller-supplied; nothing in witness.py reads git, the
  filesystem, or the environment. So a lying caller that declares F1's digests equal to F2's (or a
  clean worktree_hash on a dirty tree) can force a spurious PASS. What is proven — the algebra given
  honest declarations — is proven (criteria 1–6). What is NOT closed is derive-at-source: an honest
  harvester (git rev-parse, worktree digest, test-file hash, env fingerprint) is the production step,
  same residual class as E006 state_provider / E011 provenance_graph. A `TransportWitness(F1, F2, c)`
  licensing env-only HOLD → PASS is the natural next piece.

## Fable supervision note
Eight doctrine relays converged on C13 (frame-bound witness) as the substrate to build before
re-running E013/E012 — so that reruns emit transportable, frame-scoped evidence rather than another
floating green. Operator directed the build ("Do this"); Fable built it against a real module and
RAN it. The receipt does not claim canon — it claims: C13 PASS @ frame = 05c9f10 / this checkout /
this pytest. That is exactly the frame-scoped honesty C13 exists to enforce, applied to C13 itself.

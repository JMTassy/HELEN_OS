# AUTORESEARCH EPOCH E009 — RECEIPT (dual-heads / UnifiedStore)

🔵 OBSERVED · NON_SOVEREIGN · authority=0 · not admitted · no ledger effect
Loop: HELEN°FABLE supervision · relayed 10-epoch sim synthesis → strongest claim falsified @ 02e8621

## 7-field receipt

- **carry_forward_state**: a relayed 10-epoch autoresearch SIMULATION (upstream frame)
  claimed χ_med INCOMPLETE due to "dual heads" — the capability layer (Executor.state_provider,
  E006) and the transaction layer (TransactionRuntime.current_state_hash, E008) each holding
  their own governed-state head. Sim claims are hypotheses, not verified against this code.
- **hypothesis**: the dual-heads divergence is REAL in the committed code and lets a stale κ fire.
- **experiment**: Fable falsified the sim's strongest claim directly — committed a tx (tx head
  G0→G1) while a separately-provided cap head stayed G0; invoked a κ minted for G0.
- **metric**: does the κ execute against a stale head while the governed head has moved?
- **result — GAP CONFIRMED; SINGLE-HEAD PATH ADDED (opt-in), NOT CLOSED**: probe showed the
  κ EXECUTED against G0 while the tx head was G1 — two sources of truth, one too many. Fix:
  `GovernedStore` = single authoritative head; when both layers bind it (Executor.state_provider=
  store.head; TransactionRuntime store=store) a κ minted for stale G0 → PRE_STATE_MISMATCH.
  E008 four-state semantics preserved over the store. 163→168 tests.
  ⚠️ HONEST LABEL (peer-review correction, applied): this is OPT-IN, not a closed invariant.
  store=None is the DEFAULT and still diverges — test_e009_dual_heads_reproduced_without_store is
  kept green precisely to document that the unguarded default path still bugs by construction. The
  gap is CLOSABLE (bind one store), not CLOSED (nothing forces an integrator onto the safe path).
  A true close removes the state_provider/current_state_hash degrees of freedom or gates the wiring.
- **keep/reject rule**: KEEP as an opt-in mechanism. Real, tested single-head path; NOT a system
  invariant. E008 intact, back-compatible (store optional — which is exactly why it's not closed).
- **upgrade_path / RESIDUAL**: in-memory single head; the DURABLE single-transactional-store
  (state+receipt+marker in one atomic boundary) is the production form — same storage-boundary
  question E008 defers. Also: this unifies the pre-state root; a full χ_med close still needs the
  remaining mutation-sink enumeration (set_state_hash / append_event guards) from the sim's frontier.

## Fable supervision note — on "/LOOP IT 10 EPOCHS"
The relayed synthesis was 10 SIMULATED epochs; their claims are proposals, not verified code.
Rather than echo 10 paraphrase epochs, Fable took the single strongest verifiable claim
(dual heads → χ_med incomplete), FALSIFIED it against the real committed kernel, and built the
one real fix. One verified epoch > ten simulated ones. Anti-vacuity again: don't trust the
simulation's PASS — recompute it. Sim proposed; Fable falsified + built; neither admitted.

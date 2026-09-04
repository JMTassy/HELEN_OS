# AUTORESEARCH EPOCH E001 — RECEIPT

🔵 OBSERVED · NON_SOVEREIGN · authority=0 · not admitted · no ledger effect
Loop: HELEN°FABLE vision+supervision · local Gemma goblin execution ($0 credits)
Base commit under attack: e476e51 (hal.py Witness Law module, peer-reviewed 8/8)

## 7-field receipt (PULL-mode)

- **carry_forward_state**: HAL Witness Law shipped with 8 falsifiers + canary; assumed complete.
- **hypothesis**: an uncovered falsification attack exists that the 8+canary do not catch.
- **experiment**: gemma4-12b (local Ollama, A=0) prompted to propose exactly one new attack;
  Fable falsified the proposal against committed hal.py rather than trusting it.
- **metric**: verdict of `check()` on the attack witness. Real gap ⟺ PASS emitted.
- **failure_mode CONFIRMED**: "Identity Displacement." `B_consistency` tests
  `set(evidence_refs) ⊆ set(derivable_refs(x))` — a SET subset. It never binds evidence
  for item i to item i. A witness supplying S2's evidence for both S1 and S2 satisfies
  coverage (both ids present) AND consistency (all refs derivable) → **PASS despite
  semantic theft**. Reproduced live: verdict=PASS, reason=None.
- **keep/reject rule**: KEEP — confirmed against committed code, not speculative.
- **upgrade_path**: `B_consistency` must become per-item attribution, not set-subset:
  evidence must be structured `{item_id: ref}` and each ref must derive from THAT item.
  A new falsifier T_displacement must PASS→UNKNOWN after the fix.

## Provenance
- goblin: gemma4-12b @ local Ollama
- discovery type: NEGATIVE_CHIDDUSH survived → became POSITIVE (real gap found)
- Fable role: mission + independent falsification + receipt. Goblin proposed; never admitted.
- boundary: this receipt proposes a fix; it does not apply one. Fix is a separate reviewed tranche.

# AUTORESEARCH EPOCH E003 — RECEIPT

🔵 OBSERVED · NON_SOVEREIGN · authority=0 · not admitted · no ledger effect
Loop: HELEN°FABLE vision+supervision · gemma4-12b local goblin ($0)
Target: κ cross-actor transfer gap (#5 from the 10-attack scorecard) @ 5287ffa

## 7-field receipt

- **carry_forward_state**: 10-attack κ scorecard showed 8/10 witnessed; #5 (cross-actor
  transfer) genuinely OPEN — κ bound candidate/pre-state/scope/expiry/nonce but no holder.
  Affine consumption stops REUSE, not HANDOFF.
- **hypothesis**: a smallest holder-binding change refuses handoff without breaking
  one-shot / expiry / scope.
- **experiment**: gemma4-12b (design role, not attack) proposed FIELD holder_pubkey +
  invoke identity check. Fable falsified feasibility and right-sized it.
- **metric**: invoke() status when a non-holder presents a bound κ.
- **result — FIX BUILT (real gap closed)**: added optional opaque `holder` field
  (mint) + `presented_holder` arg (invoke); mismatch → HOLDER_MISMATCH, checked BEFORE
  consumption so a wrong-holder attempt neither fires nor spends κ. Wrong holder refused,
  correct holder executes, unbound κ = legacy, holder-bound still one-shot. 129→133 tests.
- **Fable proportionality call**: goblin proposed pubkey + signature (production form).
  MVP sandbox has no crypto-identity infra (LogicalClock + hash world), so implemented
  the SMALLEST consistent form — opaque holder id, enforced only when set — matching the
  E001/E002 optional-binding pattern. Pubkey+signature documented as the upgrade path.
- **keep/reject rule**: KEEP. Real architectural gap, back-compatible fix, peer-gated.
- **upgrade_path / RESIDUAL (goblin's honest ATTACK STILL OPEN)**: holder-binding converts
  theft-of-token → theft-of-credential. Reduction, not elimination: a bearer of the
  holder's secret still invokes. Production hardening = holder_pubkey + signature-at-invoke.
  #5 status: 🔴 OPEN → 🟢 CLOSED (handoff); credential-theft residual documented, not claimed solved.

## Fable supervision note
Epoch role shift worked: E001/E002 = adversary (find attacks); E003 = formalist/designer
(propose fix). Goblin designed; Fable right-sized + falsified; neither admitted.
Scorecard #5 closed, #10 (forged-dict witness) remains the next cheap target.

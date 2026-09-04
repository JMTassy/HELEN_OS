# AUTORESEARCH EPOCH E006 — RECEIPT

🔵 OBSERVED · NON_SOVEREIGN · authority=0 · not admitted · no ledger effect
Loop: HELEN°FABLE vision+supervision · gemma4-12b local goblin ($0)
Target: E004's deepest residual — pre_state caller-asserted → derive at choke point @ 2f98688

## 7-field receipt

- **carry_forward_state**: E004 derived the EFFECT hash but candidate + pre_state remained
  caller-asserted: invoke() compared caller-supplied pre_state_hash to cap.pre_state_hash,
  so a caller echoing the capability's own value passed even when the real state had moved.
- **hypothesis**: the executor can DERIVE the current state hash from an authoritative
  source and ignore the caller's assertion, closing the stale-state attack.
- **experiment**: gemma4-12b proposed StateManager reference + getCurrentStateHash() +
  ignore caller pre_state. Fable confirmed the gap live, then built the smallest form.
- **metric**: invoke() status when a caller echoes a stale cap.pre_state_hash while the
  authoritative state has moved.
- **result — FIX BUILT (derived, not asserted)**: Executor optionally holds a
  `state_provider`; when set, invoke() computes `effective_pre_state = state_provider()`
  and compares THAT to cap.pre_state_hash — the caller-supplied arg is IGNORED. Stale
  attack → PRE_STATE_MISMATCH even when the caller lies. Matching state → EXECUTED even if
  the caller supplies garbage (derived value is authoritative). Legacy (no provider) =
  caller-supplied path unchanged. 145→149 tests.
- **keep/reject rule**: KEEP. Real gap confirmed live, derived-not-asserted, back-compatible.
- **upgrade_path / REMAINING SLIVER (documented, not solved)**: binds_hash (candidate) is
  STILL caller-asserted — deriving it needs a canonical candidate object passed to invoke()
  and hashed at the choke point. That is E007, the last caller-assertion cell. Also: the
  state_provider itself must be a trusted authoritative source (a governed-state object),
  not another caller-controlled callable — wiring it to real governed state is production work.

## Fable supervision note
Third instance of the anti-vacuity theorem after HAL (witness coverage) and E004 (effect):
don't trust the evaluated/authorized party to assert the fact you check — derive it. The
caller-assertion class is now 2/3 closed (effect + pre-state derived; candidate = E007).
Goblin designed; Fable confirmed gap + built smallest form; neither admitted.
